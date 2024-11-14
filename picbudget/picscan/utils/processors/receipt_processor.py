import re
from datetime import datetime
from functools import lru_cache
from typing import List, Dict, Optional, Tuple
import numpy as np
from keras.utils import pad_sequences


class ReceiptProcessor:
    # Class-level constants
    SKIP_ITEMS = frozenset(
        [
            "PCS",
            "TOTAL",
            "PPN",
            "KEMBALI",
            "NO",
            "KM",
            "PEMBAYARAN",
            "HARGA",
            "LAYANAN",
            "KONSUMEN",
        ]
    )
    ADDRESS_INDICATORS = frozenset(["JL", "JALAN", "J1"])
    SKIP_ADDRESS = frozenset(["KEC", "KAB"])

    def __init__(self, model, tokenizer, label_tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.label_tokenizer = label_tokenizer
        self.index_to_label = {v: k for k, v in label_tokenizer.word_index.items()}
        self.index_to_label[0] = "O"

        # Compile regex patterns once
        self._compile_regex_patterns()
        self._initialize_date_formats()

    def _compile_regex_patterns(self) -> None:
        """Compile all regex patterns once during initialization."""
        self.date_pattern = re.compile(
            r"\b(\d{1,2}[-/\s]\d{1,2}[-/\s]\d{2,4}|\d{4}[-/\s]\d{1,2}[-/\s]\d{1,2}|\d{1,2}\s+\w+\s+\d{4})\b"
        )
        self.qty_pattern = re.compile(r"^\d+X$")
        self.total_pattern = re.compile(r"\d+")
        self.price_pattern = re.compile(r"^\d+00$")

    def _initialize_date_formats(self) -> None:
        """Initialize date formats."""
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

    @lru_cache(maxsize=128)
    def _is_valid_price(self, word: str) -> bool:
        """Check if a word is a valid price with caching."""
        if not word.endswith("00"):
            return False
        try:
            float(word)
            return True
        except ValueError:
            return False

    @staticmethod
    @lru_cache(maxsize=256)
    def _clean_text(text: str) -> str:
        """Clean text with caching."""
        return text.upper().replace("\n", " ")

    def get_total_entities(self, text: str) -> int:
        """Extract total amount from text more efficiently."""
        words = text.split()
        total_idx = -1

        # Find the last occurrence of "TOTAL"
        for i, word in enumerate(words):
            if "TOTAL" in word:
                total_idx = i

        if total_idx != -1:
            # Look for numbers after "TOTAL"
            for word in words[total_idx + 1 :]:
                match = self.total_pattern.search(word)
                if match:
                    try:
                        return int(match.group())
                    except ValueError:
                        continue
        return 0

    def correct_labels(self, words: List[str], labels: List[str]) -> List[str]:
        """Correct labels more efficiently."""
        corrected = labels.copy()

        for i, (word, label) in enumerate(zip(words, labels)):
            if label == "PRICE" and not self._is_valid_price(word):
                corrected[i] = "O"
            elif label == "ITEM_NAME":
                if word in self.SKIP_ITEMS or word[0].isdigit():
                    corrected[i] = "O"
                elif self._is_valid_price(word):
                    corrected[i] = "PRICE"
            elif self.qty_pattern.match(word):
                corrected[i] = "O"

        return corrected

    def correct_address_labels(self, words: List[str], labels: List[str]) -> List[str]:
        """Correct address labels more efficiently."""
        if "ITEM_NAME" in labels and any(
            word in self.ADDRESS_INDICATORS for word in words
        ):
            return ["ADDRESS"] * len(words)
        if ("ADDRESS" in labels or "ITEM_NAME" in labels) and any(
            word in self.SKIP_ADDRESS for word in words
        ):
            return ["O"] * len(words)
        if "ADDRESS" in labels:
            return ["ADDRESS"] * len(words)
        return labels

    @lru_cache(maxsize=64)
    def extract_date(self, text: str) -> str:
        """Extract date with caching."""
        match = self.date_pattern.search(text)
        if match:
            date_str = match.group(0)
            for date_format in self.formats:
                try:
                    date_obj = datetime.strptime(date_str, date_format)
                    if (
                        date_format in ["%d-%m-%y", "%d/%m/%y", "%d.%m.%y"]
                        and date_obj.year < 100
                    ):
                        current_century = datetime.now().year // 100 * 100
                        date_obj = date_obj.replace(
                            year=current_century + date_obj.year
                        )
                    # Return date in datetime format
                    return date_obj
                except ValueError:
                    continue
        return datetime.now()

    def extract_items(
        self, text_lines: List[str], label_lines: List[List[str]], current_idx: int
    ) -> Optional[Dict[str, any]]:
        """Extract items more efficiently."""
        line = text_lines[current_idx].split()
        labels = label_lines[current_idx]

        item_name = " ".join(
            word for word, label in zip(line, labels) if label == "ITEM_NAME"
        )

        if not item_name:
            return None

        # Find price in current and next line
        price = None
        for i in range(2):  # Check current and next line
            if current_idx + i >= len(text_lines):
                break

            check_line = text_lines[current_idx + i].split()
            check_labels = label_lines[current_idx + i]

            prices = [
                int(word)
                for word, label in zip(check_line, check_labels)
                if label == "PRICE" and self._is_valid_price(word)
            ]

            if prices:
                price = prices[-1]
                break

        if price is not None:
            return {"item_name": item_name, "item_price": price}
        return None

    def process_receipt(self, text: str) -> Dict[str, any]:
        """Process receipt more efficiently."""
        # Clean and prepare text
        clean_text = self._clean_text(text)
        sequences = pad_sequences(
            self.tokenizer.texts_to_sequences([clean_text]), maxlen=150, padding="post"
        )

        # Predict labels
        predictions = self.model.predict(sequences, verbose=0)
        predicted_indices = np.argmax(predictions, axis=-1)[0]

        # Process text lines
        text_lines = text.strip().split("\n")
        token_index = 0
        processed_lines = []

        for line in text_lines:
            tokens = line.split()
            if not tokens:
                continue

            labels = [
                self.index_to_label.get(idx, "O")
                for idx in predicted_indices[token_index : token_index + len(tokens)]
            ]
            token_index += len(tokens)
            processed_lines.append((line, tokens, labels))

        # Extract information
        items = []
        address = None
        date = None

        for i, (line, tokens, labels) in enumerate(processed_lines):
            # Apply corrections
            labels = self.correct_labels(tokens, labels)
            labels = self.correct_address_labels(tokens, labels)

            if "ITEM_NAME" in labels:
                item = self.extract_items(
                    [p[0] for p in processed_lines], [p[2] for p in processed_lines], i
                )
                if item:
                    items.append(item)

            if not address and "ADDRESS" in labels:
                address = line

            if not date:
                date = self.extract_date(line)

        return {
            "total": self.get_total_entities(clean_text),
            "date": date,
            "address": address,
            "items": items,
        }
