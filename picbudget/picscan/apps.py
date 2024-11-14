from django.apps import AppConfig
import pickle
import pathlib
from keras.models import load_model  # type: ignore
from .utils.processors.receipt_processor import ReceiptProcessor


class PicscanConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "picbudget.picscan"
    TOKENIZER_PATH = (
        pathlib.Path(__file__).parent / "utils" / "models" / "tokenizer.pickle"
    )
    LABEL_TOKENIZER_PATH = (
        pathlib.Path(__file__).parent / "utils" / "models" / "label_tokenizer.pickle"
    )
    MODEL_PATH = pathlib.Path(__file__).parent / "utils" / "models" / "model.keras"

    def ready(self):
        with open(self.TOKENIZER_PATH, "rb") as file:
            self.tokenizer = pickle.load(file)

        with open(self.LABEL_TOKENIZER_PATH, "rb") as file:
            self.label_tokenizer = pickle.load(file)

        self.model = load_model(self.MODEL_PATH)

        self.receipt_processor = ReceiptProcessor(
            model=self.model,
            tokenizer=self.tokenizer,
            label_tokenizer=self.label_tokenizer,
        )
