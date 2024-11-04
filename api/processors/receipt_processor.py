import re
from datetime import datetime
from keras_preprocessing.sequence import pad_sequences
from keras.models import load_model
import pickle
import numpy as np


class ReceiptProcessor:
    def __init__(self, model_path):
        # Load the trained model
        self.model = load_model(model_path + "picbudget_model.h5")

        # Load the tokenizers
        with open(model_path + "tokenizer.pickle", "rb") as handle:
            self.tokenizer = pickle.load(handle)

        with open(model_path + "label_tokenizer.pickle", "rb") as handle:
            self.label_tokenizer = pickle.load(handle)

        # Create a mapping from index to label
        self.index_to_label = {v: k for k, v in self.label_tokenizer.word_index.items()}
        self.index_to_label[0] = "O"  # Assuming 'O' is for non-entity tokens

        # Compile regex patterns once
        self.date_pattern = re.compile(
            r"\b(\d{1,2}[-/\s]\d{1,2}[-/\s]\d{2,4}|\d{4}[-/\s]\d{1,2}[-/\s]\d{1,2}|\d{1,2}\s+\w+\s+\d{4})\b"
        )
        self.qty_pattern = re.compile(r"^\d+X$")
        self.formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d %B %Y",
            "%m-%d-%Y",
            "%d %b %Y",
            "%Y.%m.%d",
            "%d-%m-%Y",
            "%m/%d/%Y",
            "%d %b %Y",
            "%Y.%m.%d",
            "%d-%m-%y",
            "%d/%m/%y",
            "%d.%m.%y",
        ]

    def get_total_entities(self, text):
        tokens = text.split(" ")
        total = 0
        is_total = False
        for token in tokens:
            if "TOTAL" in token:
                is_total = True
            if is_total:
                try:
                    total = int(token)
                    break
                except ValueError:
                    continue
        return total

    def correct_price_label(self, word, label):
        if "PRICE" in label:
            if not word.endswith("00"):
                return "O"
            try:
                float(word)
            except ValueError:
                return "O"
        return label

    def correct_item_name_label(self, word, label):
        if "ITEM_NAME" in label:
            if word in [
                "PCS",
                "TOTAL",
                "PPN",
                "KEMBALI",
                "NO",
                "KM",
                "PEMBAYARAN",
                "HARGA",
            ]:
                return "O"
            try:
                float(word)
                if not word.endswith("00"):
                    return "O"
                else:
                    return "PRICE"
            except ValueError:
                if word[0].isdigit():
                    return "O"
        return label

    def correct_qty_label(self, word, label):
        if re.match(self.qty_pattern, word):
            return "O"
        return label

    def correct_labels(self, line, labels):
        for j, (word, label) in enumerate(zip(line, labels)):
            label = self.correct_price_label(word, label)
            label = self.correct_item_name_label(word, label)
            label = self.correct_qty_label(word, label)
            labels[j] = label
        return labels

    def correct_address_labels(self, line, labels):
        if "ITEM_NAME" in labels and any(
            word in ["JL", "JALAN", "J1"] for word in line
        ):
            labels = ["ADDRESS"] * len(line)
        if "ADDRESS" in labels and any(word in ["KEC", "KAB"] for word in line):
            labels = ["O"] * len(line)
        if "ITEM_NAME" in labels and any(word in ["KEC", "KAB"] for word in line):
            labels = ["O"] * len(line)
        if "ADDRESS" in labels:
            labels = ["ADDRESS"] * len(line)
        return labels

    def correct_date_labels(self, line, labels):
        if "DATE" in labels:
            labels = ["DATE"] * len(line)
        return labels

    def extract_date(self, line):
        match = self.date_pattern.search(" ".join(line))
        if match:
            date_str = match.group(0)
            for date_format in self.formats:
                try:
                    date_obj = datetime.strptime(date_str, date_format)
                    if (
                        date_format in ["%d-%m-%y", "%d/%m/%y", "%d.%m.%y"]
                        and date_obj.year < 100
                    ):
                        current_year = datetime.now().year
                        current_century = current_year // 100 * 100
                        date_obj = date_obj.replace(
                            year=current_century + date_obj.year
                        )
                    return date_obj.strftime("%d/%m/%Y")
                except ValueError:
                    continue
        return datetime.now().strftime("%d/%m/%Y")

    def extract_items(self, text_lines, label_lines, i, items):
        line = text_lines[i].split()
        labels = label_lines[i]
        item_name = " ".join(
            word for word, label in zip(line, labels) if label == "ITEM_NAME"
        )
        prices = []

        # Extract prices from the current line
        for word, label in zip(line, labels):
            if label == "PRICE":
                try:
                    prices.append(int(word))
                except ValueError:
                    continue

        price = prices[-1] if prices else None

        # If no price found in the current line, check the next immediate line
        if price is None and i + 1 < len(text_lines):
            next_line = text_lines[i + 1].split()
            next_labels = label_lines[i + 1]
            next_prices = []

            for word, label in zip(next_line, next_labels):
                if label == "PRICE":
                    try:
                        next_prices.append(int(word))
                    except ValueError:
                        continue

            price = next_prices[-1] if next_prices else None

        # Only append if both item_name and price are found
        if item_name and price is not None:
            items.append({"item": item_name, "price": int(price)})

    def should_skip_line(self, labels):
        return labels.count("O") > len(labels) / 2

    def correct_item_name_labels(self, labels):
        if "ITEM_NAME" in labels and "PRICE" in labels:
            labels = ["ITEM_NAME" if label == "O" else label for label in labels]
        return labels

    def extract_address(self, line_words, labels, current_address):
        if not current_address and "ADDRESS" in labels:
            return " ".join(line_words)
        return current_address

    def process_receipt(self, new_text):
        new_text = new_text.upper()
        # Clean and prepare text
        new_text_cleaned = new_text.replace("\n", " ")
        new_sequences = self.tokenizer.texts_to_sequences([new_text_cleaned])
        padded_new_sequences = pad_sequences(new_sequences, maxlen=150, padding="post")

        # Predict labels
        new_predictions = self.model.predict(padded_new_sequences)

        # Convert predictions to label indices
        predicted_labels_indices = np.argmax(new_predictions, axis=-1)

        # Map predicted indices to labels
        predicted_labels = [
            [self.index_to_label.get(label, "O") for label in sentence]
            for sentence in predicted_labels_indices
        ]

        # Combine text lines with their labels
        new_text_lines = new_text.strip().split("\n")
        token_index = 0

        text_line = []
        label_line = []

        for line in new_text_lines:
            line_tokens = line.split()
            line_labels = predicted_labels[0][
                token_index : token_index + len(line_tokens)
            ]
            token_index += len(line_tokens)
            text_line.append(line)
            label_line.append(line_labels)

        total = self.get_total_entities(new_text_cleaned)
        address = None
        date = None
        items = []

        clean_text_line = []
        clean_label_line = []
        for i, (line, labels) in enumerate(zip(text_line, label_line)):
            line_words = line.split()
            labels = self.correct_labels(line_words, labels)
            labels = self.correct_address_labels(line_words, labels)
            labels = self.correct_date_labels(line_words, labels)

            if self.should_skip_line(labels):
                continue

            labels = self.correct_item_name_labels(labels)
            clean_label_line.append(labels)
            clean_text_line.append(line)

            address = self.extract_address(line_words, labels, address)
            date = date or self.extract_date(line_words)

        for i, (line, labels) in enumerate(zip(clean_text_line, clean_label_line)):
            if "ITEM_NAME" in labels:
                self.extract_items(clean_text_line, clean_label_line, i, items)

        return {"total": total, "date": date, "address": address, "items": items}
