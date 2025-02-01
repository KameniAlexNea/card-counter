from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np
import numpy.typing as npt
from loguru import logger
from PIL import Image


@dataclass
class ProcessedImage:
    image: npt.NDArray
    angle: Optional[float] = None
    enhancement_applied: bool = False
    preprocessing_history: Optional[list[str]] = None

    def __post_init__(self):
        """Initialize preprocessing history if not provided."""
        if self.preprocessing_history is None:
            self.preprocessing_history = []
        if isinstance(self.image, Image.Image):
            self.image = np.array(self.image.convert("RGB"))


class ImagePreprocessor:
    @staticmethod
    def denoise(image: npt.NDArray) -> ProcessedImage:
        try:
            if len(image.shape) == 3:
                denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
            else:
                denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)

            return ProcessedImage(image=denoised, preprocessing_history=["denoise"])
        except Exception as e:
            logger.error(f"Error during denoising: {str(e)}")
            raise ValueError(f"Failed to denoise image: {str(e)}")

    @staticmethod
    def deskew(image: npt.NDArray) -> ProcessedImage:
        """Correct image skew by detecting and rotating to align text.

        Uses contour detection to find the dominant text angle and corrects it.

        Args:
            image: Input image as numpy array

        Returns:
            ProcessedImage: Deskewed image with rotation angle

        Raises:
            ValueError: If angle detection fails
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Detect edges
            edges = cv2.Canny(gray, 50, 200, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)

            if lines is None:
                logger.warning("No lines detected for deskewing")
                return ProcessedImage(image=image, angle=0)

            # Calculate dominant angle
            angles = []
            for _, theta in lines[0]:
                angle = theta * 180 / np.pi
                if angle < 45:
                    angles.append(angle)
                elif angle > 135:
                    angles.append(angle - 180)

            if not angles:
                return ProcessedImage(image=image, angle=0)

            median_angle = np.median(angles)

            # Rotate image
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
            )

            return ProcessedImage(
                image=rotated, angle=median_angle, preprocessing_history=["deskew"]
            )
        except Exception as e:
            logger.error(f"Error during deskewing: {str(e)}")
            raise ValueError(f"Failed to deskew image: {str(e)}")


@dataclass()
class PreprocessingConfig:
    """Configuration for image preprocessing steps."""

    denoise: bool = True
    deskew: bool = True
    contrast_enhancement: bool = True
    threshold: Optional[float] = None
    resize_factor: Optional[float] = None


class ImageHandler:
    _supported_formats = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

    def __init__(self):
        self.preprocessor = ImagePreprocessor()

    def preprocess_image(
        self, image: npt.NDArray, config: PreprocessingConfig
    ) -> ProcessedImage:
        try:
            result = ProcessedImage(image=image)

            if config.denoise:
                denoised = self.preprocessor.denoise(result.image)
                result.image = denoised.image
                result.preprocessing_history.extend(denoised.preprocessing_history)

            if config.deskew:
                deskewed = self.preprocessor.deskew(result.image)
                result.image = deskewed.image
                result.angle = deskewed.angle
                result.preprocessing_history.extend(deskewed.preprocessing_history)

            return result

        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            raise ValueError(f"Image preprocessing failed: {str(e)}")
