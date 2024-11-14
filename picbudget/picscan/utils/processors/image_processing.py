import cv2
import numpy as np
from functools import lru_cache
from typing import Tuple, List, Optional
import threading
from concurrent.futures import ThreadPoolExecutor


class ImageProcessor:
    # Class-level constants for better performance
    MORPH_KERNEL = np.ones((5, 5), np.uint8)
    GAUSSIAN_KERNEL = (5, 5)
    ADAPTIVE_BLOCK_SIZE = 11
    ADAPTIVE_C = 2

    def __init__(self, image: np.ndarray, max_workers: int = 4):
        """
        Initialize image processor with optional parallel processing.

        Args:
            image: Input image as numpy array
            max_workers: Maximum number of parallel workers for processing
        """
        self.image = image
        self.max_workers = max_workers
        self._lock = threading.Lock()
        self._cache = {}
        self._preprocessed_image = None

    @lru_cache(maxsize=32)
    def _get_cached_operation(
        self, operation_name: str, image_hash: int
    ) -> Optional[np.ndarray]:
        """Cache results of expensive operations."""
        return self._cache.get((operation_name, image_hash))

    def _set_cached_operation(
        self, operation_name: str, image_hash: int, result: np.ndarray
    ) -> None:
        """Store operation result in cache."""
        with self._lock:
            self._cache[(operation_name, image_hash)] = result

    def _preprocess_image(self) -> np.ndarray:
        """
        Preprocess image with parallel processing where possible.
        """
        # Create processing pipeline
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Stage 1: Initial processing
            resized_future = executor.submit(self._resize_image, self.image.copy())
            image, aspect_ratio = resized_future.result()

            # Stage 2: Parallel processing
            grabcut_future = executor.submit(self._apply_grab_cut, image)
            morph_future = executor.submit(
                self._apply_morphology, grabcut_future.result()
            )

            # Stage 3: Sequential processing (dependent operations)
            processed = self._process_sequential(morph_future.result(), aspect_ratio)

            return processed

    def _process_sequential(self, image: np.ndarray, aspect_ratio: float) -> np.ndarray:
        """Process operations that must be done sequentially."""
        image = self._convert_to_gray(image)
        image = self._apply_canny_edge_detection(image)
        image = self._cut_image_to_contours(self.image, image, aspect_ratio)
        image = self._apply_denoising_alternative(image)
        return self._binarize_image(image)

    @staticmethod
    def _resize_image(
        image: np.ndarray, target_width: int = 300
    ) -> Tuple[np.ndarray, float]:
        """Resize image maintaining aspect ratio."""
        aspect_ratio = target_width / image.shape[1]
        dim = (target_width, int(image.shape[0] * aspect_ratio))
        return cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR), aspect_ratio

    def _apply_grab_cut(self, image: np.ndarray) -> np.ndarray:
        """Apply GrabCut algorithm with optimized parameters."""
        height, width = image.shape[:2]
        # Optimize rectangle calculation
        rect_coords = np.array(
            [
                int(width * 0.1),
                int(height * 0.1),
                int(width * 0.8),
                int(height * 0.8),
            ]
        )

        # Pre-allocate arrays
        mask = np.zeros(image.shape[:2], np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        cv2.grabCut(
            image, mask, rect_coords, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT
        )

        # Optimize mask creation
        mask = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
        return image * mask[:, :, np.newaxis]

    def _apply_morphology(self, image: np.ndarray) -> np.ndarray:
        """Apply morphological operations with pre-defined kernel."""
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, self.MORPH_KERNEL, iterations=2)

    @staticmethod
    def _convert_to_gray(image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale."""
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def _apply_canny_edge_detection(image: np.ndarray) -> np.ndarray:
        """Apply Canny edge detection with optimal thresholds."""
        return cv2.Canny(image, 100, 200)

    def _cut_image_to_contours(
        self, original: np.ndarray, image: np.ndarray, aspect_ratio: float
    ) -> np.ndarray:
        """Find and process image contours efficiently."""
        contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return original

        # Get largest contour directly
        largest_contour = max(contours, key=cv2.contourArea)
        receipt_contour = self._approximate_contour(largest_contour)

        if len(receipt_contour) == 4:
            return self._warp_perspective(
                original, self._contour_to_rectangle(receipt_contour, aspect_ratio)
            )
        return original

    @staticmethod
    def _approximate_contour(contour: np.ndarray) -> np.ndarray:
        """Approximate contour with optimal epsilon."""
        peri = cv2.arcLength(contour, True)
        return cv2.approxPolyDP(contour, 0.032 * peri, True)

    @staticmethod
    def _contour_to_rectangle(contour: np.ndarray, resize_ratio: float) -> np.ndarray:
        """Convert contour to rectangle coordinates efficiently."""
        pts = contour.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")

        # Optimize point selection
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)

        rect[0] = pts[np.argmin(s)]  # Top-left
        rect[2] = pts[np.argmax(s)]  # Bottom-right
        rect[1] = pts[np.argmin(diff)]  # Top-right
        rect[3] = pts[np.argmax(diff)]  # Bottom-left

        return rect / resize_ratio

    def _warp_perspective(
        self, image: np.ndarray, rect: np.ndarray, padding: int = 50
    ) -> np.ndarray:
        """Apply perspective transformation with optimized calculations."""
        # Calculate width and height efficiently
        width = np.maximum(
            np.linalg.norm(rect[2] - rect[3]),  # Bottom edge
            np.linalg.norm(rect[1] - rect[0]),  # Top edge
        )
        height = np.maximum(
            np.linalg.norm(rect[1] - rect[2]),  # Right edge
            np.linalg.norm(rect[0] - rect[3]),  # Left edge
        )

        # Create destination points
        max_width = int(width) + 2 * padding
        max_height = int(height) + 2 * padding

        dst = np.array(
            [
                [padding, padding],
                [max_width - padding - 1, padding],
                [max_width - padding - 1, max_height - padding - 1],
                [padding, max_height - padding - 1],
            ],
            dtype="float32",
        )

        # Apply perspective transform
        M = cv2.getPerspectiveTransform(rect, dst)
        return cv2.warpPerspective(image, M, (max_width, max_height))

    def _apply_denoising_alternative(self, image: np.ndarray) -> np.ndarray:
        """Apply Gaussian blur with pre-defined kernel."""
        return cv2.GaussianBlur(image, self.GAUSSIAN_KERNEL, 0)

    def _binarize_image(self, image: np.ndarray) -> np.ndarray:
        """Binarize image with adaptive thresholding."""
        if len(image.shape) == 3:
            image = self._convert_to_gray(image)

        return cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            self.ADAPTIVE_BLOCK_SIZE,
            self.ADAPTIVE_C,
        )

    def get_image(self) -> np.ndarray:
        """Get original image."""
        return self.image

    def preprocess_image(self) -> np.ndarray:
        """Get preprocessed image with caching."""
        if self._preprocessed_image is None:
            self._preprocessed_image = self._preprocess_image()
        return self._preprocessed_image
