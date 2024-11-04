import spacy
import re
from datetime import datetime


class ReceiptProcessor:
    def __init__(self, model_path):
        # Load the trained model from disk
        self.nlp = spacy.load(model_path)

    def process_text_line_by_line(self, text):
        """
        Process the given text line by line and extract named entities using spaCy.

        Args:
            text (str): The input text to be processed.

        Returns:
            list: A list of named entity tuples for each line in the text.
                  Each tuple contains the named entity text and its label.
        """
        lines = text.splitlines()
        results = []
        for line in lines:
            doc = self.nlp(line)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            results.append(entities)
        return results

    def filter_item_prices(self, entities):
        """
        Filters out item prices from a list of entities.

        Args:
            entities (list): A list of tuples containing entities and their labels.

        Returns:
            list: A filtered list of tuples containing only the item prices.

        """
        filtered_entities = []
        for entity, label in entities:
            if label == "ITEM_PRICE":
                # Check if the entity is a number and ends with '00' or '000'
                if re.match(r"^\d+(00|000)$", entity):
                    filtered_entities.append((entity, label))
            else:
                filtered_entities.append((entity, label))
        return filtered_entities

    def filter_item_names(self, entities):
        """
        Filters out unwanted item names from the given list of entities.

        Args:
            entities (list): A list of tuples containing entity-label pairs.

        Returns:
            list: A filtered list of tuples containing entity-label pairs, excluding unwanted item names.

        """
        filtered_entities = []
        exclude_keywords = {
            "total",
            "cash",
            "bayar",
            "kembali",
            "terima",
            "kasih",
            "jual",
            "harga",
            "beli",
            "uang",
            "kembalian",
            "tunai",
            "pulsa",
            "saldo",
            "voucher",
            "pembayaran",
            "pembelian",
            "belanja",
            "change",
        }
        quantity_pattern = re.compile(r"^\d+x$", re.IGNORECASE)
        for entity, label in entities:
            if label == "ITEM_NAME":
                if not any(
                    keyword in entity.lower() for keyword in exclude_keywords
                ) and not quantity_pattern.match(entity):
                    filtered_entities.append((entity, label))
            else:
                filtered_entities.append((entity, label))
        return filtered_entities

    def get_total_entities(self, text):
        """
        Retrieves the total number of entities from the given text.

        Args:
            text (str): The input text.

        Returns:
            int: The total number of entities found in the text.
        """
        tokens = text.split(" ")
        total = 0
        is_total = False
        for line in tokens:
            if "total" in line:
                is_total = True
            if is_total:
                try:
                    total = int(line)
                    break
                except Exception as e:
                    print(e)
                    continue
        return total

    def get_date_entities(self, text):
        """
        Extracts the date entities from the given text.

        Args:
            text (str): The input text.

        Returns:
            str: The extracted date entity.

        """
        tokens = text.split(" ")
        date = None
        for line in tokens:
            dates = re.findall(r"\b\d{2}[./-]\d{2}[./-]\d{2,4}\b", line)
            if dates:
                date = dates[0]
                break
        if date is None:
            date = datetime.now().strftime("%d/%m/%Y")
        return date

    def find_item_name_price_pattern(self, filtered_line_ner_results):
        """
        Finds and returns a list of items with their corresponding prices from the given filtered line NER results.

        Args:
            filtered_line_ner_results (list): A list of filtered line NER results, where each result is a list of (entity, label) tuples.

        Returns:
            list: A list of dictionaries, where each dictionary represents an item with its name and price. The dictionary has the following structure:
                {
                    "item": str,  # The name of the item
                    "price": int  # The price of the item
                }
        """
        items = []
        for i in range(len(filtered_line_ner_results)):
            filtered_entities = filtered_line_ner_results[i]
            item_name = None
            item_price = None
            for entity, label in filtered_entities:
                if label == "ITEM_NAME":
                    item_name = entity
                elif label == "ITEM_PRICE":
                    item_price = entity
            if item_name and item_price:
                items.append({"item": item_name, "price": int(item_price)})
            elif (
                item_name and not item_price and i + 1 < len(filtered_line_ner_results)
            ):
                next_line_entities = filtered_line_ner_results[i + 1]
                for entity, label in next_line_entities:
                    if label == "ITEM_PRICE":
                        item_price = entity
                        items.append({"item": item_name, "price": int(item_price)})
                        break
        return items

    def process_receipt(self, text):
        """
        Process the receipt text and extract relevant information such as total, date, address, and items.

        Args:
            text (str): The receipt text to be processed.

        Returns:
            dict: A dictionary containing the extracted information from the receipt.
                The dictionary has the following keys:
                - "total": The total amount on the receipt.
                - "date": The date mentioned on the receipt.
                - "address": The address mentioned on the receipt.
                - "items": A list of items and their corresponding prices mentioned on the receipt.
        """
        line_ner_results = self.process_text_line_by_line(text)
        inline_text = text.split("\n")

        for i in range(len(line_ner_results)):
            filtered_entities = self.filter_item_prices(line_ner_results[i])
            filtered_entities = self.filter_item_names(filtered_entities)
            line_ner_results[i] = filtered_entities

        total = self.get_total_entities(" ".join(inline_text))
        date = self.get_date_entities(" ".join(inline_text))

        try:
            address = [
                address
                for address in line_ner_results
                if any("ADDRESS" in label for _, label in address)
            ]
            address = address[0][0][0]
        except Exception as e:
            print(e)
            address = None

        items = self.find_item_name_price_pattern(line_ner_results)

        result = {"total": total, "date": date, "address": address, "items": items}
        return result
