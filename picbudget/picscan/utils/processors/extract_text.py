from paddleocr import PaddleOCR
import re
from typing import List, Tuple
from functools import lru_cache


class TextExtractor:
    # Compile regex patterns once during class initialization
    DATE_PATTERN = re.compile(r"\b\d{2}[./-]\d{2}[./-]\d{2,4}\b")
    RP_PATTERN = re.compile(r"\brp[.\s]?", re.IGNORECASE)
    SPECIAL_CHARS_PATTERN = re.compile(r"[^\w\s.,]")
    SINGLE_LETTER_PATTERN = re.compile(r"\b[a-zA-Z]\b")
    PUNCTUATION_PATTERN = re.compile(
        r"(?<!\d)[.,](?!\d)|(?<!\b[a-zA-Z])[.,](?!\b[a-zA-Z])"
    )
    SINGLE_DIGIT_PATTERN = re.compile(r"\b\d\b")
    EMPTY_LINE_PATTERN = re.compile(r"^\s*$\n", re.MULTILINE)
    WHITESPACE_PATTERN = re.compile(r"\s+")

    def __init__(self, image: str):
        """Initialize OCR with optimized settings."""
        self.image = image
        self.ocr = PaddleOCR(
            use_angle_cls=False,
            lang="id",
            use_gpu=False,
            show_log=False,
            enable_mkldnn=True,  # Enable Intel MKL-DNN acceleration
            cpu_threads=4,  # Adjust based on your CPU
        )
        self.extracted_text = self.extract_text(image)

    @staticmethod
    @lru_cache(maxsize=128)
    def _preprocess_text(line: str) -> str:
        """Preprocess text with cached results for repeated patterns."""
        dates = TextExtractor.DATE_PATTERN.findall(line)

        # Chain replacements for better performance
        line = TextExtractor.RP_PATTERN.sub("", line).lower().strip()

        line = TextExtractor.SPECIAL_CHARS_PATTERN.sub("", line)

        # Add dates back if found
        if dates:
            line = f"{line} {' '.join(dates)}"

        # Apply remaining patterns in a single pass
        line = TextExtractor.SINGLE_LETTER_PATTERN.sub(" ", line).strip()
        line = TextExtractor.PUNCTUATION_PATTERN.sub("", line)
        line = TextExtractor.SINGLE_DIGIT_PATTERN.sub("", line)
        line = TextExtractor.EMPTY_LINE_PATTERN.sub("", line)
        line = TextExtractor.WHITESPACE_PATTERN.sub(" ", line).strip()

        return line

    @staticmethod
    def _is_inline(
        box1: List[Tuple[float, float]],
        box2: List[Tuple[float, float]],
        tolerance: int = 15,
    ) -> bool:
        """Check if two boxes are inline using vectorized operations."""
        return (
            abs(box1[0][1] - box2[0][1]) <= tolerance
            and abs(box1[2][1] - box2[2][1]) <= tolerance
        )

    def _group_inline(self, ocr_result: List[Tuple], tolerance: int = 15) -> List[str]:
        """Group inline text more efficiently."""
        if not ocr_result:
            return []

        grouped_result = []
        current_group = []

        # Use enumerate for better performance than index lookups
        for i, current in enumerate(ocr_result[:-1]):
            current_group.append(current[1][0])

            if not self._is_inline(current[0], ocr_result[i + 1][0], tolerance):
                grouped_result.append(" ".join(current_group).lower())
                current_group = []

        # Add the last group
        if ocr_result:
            current_group.append(ocr_result[-1][1][0])
            grouped_result.append(" ".join(current_group).lower())

        return grouped_result

    def extract_text(self, image: str) -> str:
        """Extract text with improved error handling and performance."""
        try:
            result = self.ocr.ocr(image, cls=False)
            if not result or not result[0]:
                print("OCR did not return any results.")
                return ""

            # Process results in a more streamlined way
            grouped_text = self._group_inline(result[0])
            cleaned_lines = [
                self._preprocess_text(line) for line in grouped_text if line.strip()
            ]

            return "\n".join(cleaned_lines)

        except Exception as e:
            print(f"Error during text extraction: {str(e)}")
            return ""
