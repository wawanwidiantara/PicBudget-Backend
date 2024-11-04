import numpy as np
import cv2
from rembg import remove
from matplotlib import pyplot as plt


class PageExtractor:
    def __init__(
        self,
        image_path=None,
        image_array=None,
        remove_background="n",
    ):
        self.image = self._load_image(image_path, image_array)
        self.remove_background = remove_background
        self._preprocessed_image = self._preprocess_image()

    def _load_image(self, image_path, image_array):
        if image_path:
            return cv2.imread(image_path)
        elif image_array is not None:
            return image_array
        else:
            raise ValueError("Either image_path or image_array must be provided")

    def _preprocess_image(self):
        image, aspect_ratio = self._resize_image(self.image.copy())
        if self.remove_background == "y":
            image = remove(image)
        else:
            image = self._apply_grab_cut(image)
            image = self._apply_morphology(image)
        image = self._convert_to_gray(image)
        image = self._apply_canny_edge_detection(image)
        image = self._cut_image_to_contours(self.image, image, aspect_ratio)
        image = self._apply_denoising_alternative(image)
        image = self._binarize_image(image)
        return image

    def _resize_image(self, image, ratio=300):
        aspect_ratio = ratio / image.shape[1]
        dim = (int(image.shape[1] * aspect_ratio), int(image.shape[0] * aspect_ratio))
        return cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR), aspect_ratio

    def _apply_grab_cut(self, image):
        height, width = image.shape[:2]
        rectangle = (
            int(width * 0.1),
            int(height * 0.1),
            int(width * 0.8),
            int(height * 0.8),
        )
        mask = np.zeros(image.shape[:2], np.uint8)
        background_model = np.zeros((1, 65), np.float64)
        foreground_model = np.zeros((1, 65), np.float64)
        cv2.grabCut(
            image,
            mask,
            rectangle,
            background_model,
            foreground_model,
            5,
            cv2.GC_INIT_WITH_RECT,
        )
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
        return image * mask2[:, :, np.newaxis]

    def _apply_morphology(self, image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=2)

    def _convert_to_gray(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def _apply_canny_edge_detection(self, image):
        return cv2.Canny(image, 100, 200)

    def _cut_image_to_contours(self, original, image, aspect_ratio):
        contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        largest_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
        receipt_contour = self._get_receipt_contour(largest_contours)
        if len(receipt_contour) > 0:
            return self._warp_perspective(
                original.copy(),
                self._contour_to_rectangle(receipt_contour, aspect_ratio),
            )
        else:
            return original

    def _get_receipt_contour(self, contours):
        for contour in contours:
            approx = self._approximate_contour(contour)
            if len(approx) == 4:
                return approx
        return []

    def _approximate_contour(self, contour):
        peri = cv2.arcLength(contour, True)
        return cv2.approxPolyDP(contour, 0.032 * peri, True)

    def _contour_to_rectangle(self, contour, resize_ratio):
        pts = contour.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect / resize_ratio

    def _warp_perspective(self, image, rect, padding=50):
        (tl, tr, br, bl) = rect
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_width = max(int(width_a), int(width_b)) + 2 * padding
        max_height = max(int(height_a), int(height_b)) + 2 * padding
        dst = np.array(
            [
                [padding, padding],
                [max_width - 1 - padding, padding],
                [max_width - 1 - padding, max_height - 1 - padding],
                [padding, max_height - 1 - padding],
            ],
            dtype="float32",
        )
        M = cv2.getPerspectiveTransform(rect, dst)
        return cv2.warpPerspective(image, M, (max_width, max_height))

    def _apply_denoising(self, image):
        return cv2.fastNlMeansDenoising(image, h=3)

    def _apply_denoising_alternative(self, image):
        return cv2.GaussianBlur(image, (5, 5), 0)

    def _binarize_image(self, image):
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

    def get_image(self):
        return self.image

    def preprocess_image(self):
        return self._preprocessed_image
