from paddleocr import PaddleOCR
import re


class TextExtractor:
    def __init__(self, image):
        self.image = image
        self.ocr = PaddleOCR(use_angle_cls=False, lang="id", use_gpu=False)
        self.extracted_text = self.extract_text(image)

    def extract_text(self, image):
        result = self.ocr.ocr(image, cls=False)

        if not result or not result[0]:
            print("OCR did not return any results.")
            return ""

        clean_result = [line for line in result[0]]
        grouped_text = self._group_inline(clean_result)
        cleaned_lines = [self._preprocess_text(line) for line in grouped_text]
        cleaned_lines = [line.strip() for line in cleaned_lines if line.strip()]
        extracted_text = "\n".join(cleaned_lines).lower()

        return extracted_text

    def _preprocess_text(self, line):
        dates = re.findall(r"\b\d{2}[./-]\d{2}[./-]\d{2,4}\b", line)
        line = re.sub(r"\brp[.\s]?", "", line, flags=re.IGNORECASE)
        line = re.sub(r"[^\w\s.,]", "", line)
        for date in dates:
            line += f" {date}"
        line = re.sub(r"\b[a-zA-Z]\b", " ", line)
        line = re.sub(r"(?<!\d)[.,](?!\d)|(?<!\b[a-zA-Z])[.,](?!\b[a-zA-Z])", "", line)
        line = re.sub(r"\b\d\b", "", line)
        line = re.sub(r"^\s*$\n", "", line, flags=re.MULTILINE)
        line = re.sub(r"\s+", " ", line).strip()
        return line

    def _group_inline(self, ocr_result, tolerance=15):
        grouped_result = []
        temp = ocr_result[0]
        for i in range(1, len(ocr_result)):
            if not self._is_inline(ocr_result[i - 1][0], ocr_result[i][0], tolerance):
                joined_text = " ".join(
                    [
                        line[1][0]
                        for line in ocr_result[
                            ocr_result.index(temp) : ocr_result.index(ocr_result[i])
                        ]
                    ]
                )
                grouped_result.append(joined_text.lower())
                temp = ocr_result[i]
        return grouped_result

    def _is_inline(self, box1, box2, tolerance):
        top_aligned = abs(box1[0][1] - box2[0][1]) <= tolerance
        bottom_aligned = abs(box1[2][1] - box2[2][1]) <= tolerance
        return top_aligned and bottom_aligned
