"""Image processing functionality for cross-stitch pattern generation."""

from typing import List, Tuple, Union
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

from ..models import GeneratorConfig
from ..utils import load_image, validate_image_file, ImageProcessingError


class ImageProcessor:
    """Handles image loading, processing, and resizing for cross-stitch patterns."""

    def __init__(self, config: GeneratorConfig):
        """
        Initialize ImageProcessor with configuration.

        Args:
            config: Generator configuration object
        """
        self.config = config

    def load_and_process_image(self, image_path: Union[str, Path]) -> Image.Image:
        """
        Load and process an image for pattern generation.

        Args:
            image_path: Path to the image file

        Returns:
            Processed PIL Image object

        Raises:
            ImageProcessingError: If image processing fails
        """
        try:
            # Validate the image file
            validate_image_file(image_path)

            # Load the image
            image = load_image(image_path)

            # Process the image according to configuration
            processed_image = self._process_image(image, str(image_path))

            return processed_image

        except Exception as e:
            if isinstance(e, ImageProcessingError):
                raise
            raise ImageProcessingError(
                f"Failed to load and process image: {e}",
                image_path=str(image_path),
                operation="load_and_process",
                cause=e
            )

    def resize_to_resolutions(self, image: Image.Image,
                              source_path: str) -> List[Tuple[Tuple[int, int], Image.Image]]:
        """
        Resize image to all configured resolutions.

        Args:
            image: Source PIL Image object
            source_path: Path to source image (for error messages)

        Returns:
            List of tuples: (resolution, resized_image)

        Raises:
            ImageProcessingError: If resizing fails
        """
        resized_images = []

        try:
            for resolution in self.config.resolutions:
                try:
                    resized = self._resize_image(image, resolution)
                    resized_images.append((resolution, resized))
                except Exception as e:
                    raise ImageProcessingError(
                        f"Failed to resize to {resolution[0]}x{resolution[1]}: {e}",
                        image_path=source_path,
                        operation="resize",
                        cause=e
                    )

            return resized_images

        except Exception as e:
            if isinstance(e, ImageProcessingError):
                raise
            raise ImageProcessingError(
                f"Failed to resize image to target resolutions: {e}",
                image_path=source_path,
                operation="resize_to_resolutions",
                cause=e
            )

    def _process_image(self, image: Image.Image, image_path: str) -> Image.Image:
        """
        Apply initial processing to the loaded image.

        Args:
            image: Source PIL Image object
            image_path: Path to source image

        Returns:
            Processed PIL Image object
        """
        try:
            # Handle different color modes
            processed = self._normalize_color_mode(image)

            # Handle transparency according to configuration
            processed = self._handle_transparency(processed)

            # Apply orientation correction if needed
            processed = self._correct_orientation(processed)

            return processed

        except Exception as e:
            raise ImageProcessingError(
                f"Image processing failed: {e}",
                image_path=image_path,
                operation="process_image",
                cause=e
            )

    def _normalize_color_mode(self, image: Image.Image) -> Image.Image:
        """Convert image to appropriate color mode for processing."""
        mode = image.mode

        if mode == 'P':  # Palette mode
            # Convert palette images to RGBA to preserve transparency if present
            if 'transparency' in image.info:
                return image.convert('RGBA')
            else:
                return image.convert('RGB')

        elif mode in ['1', 'L']:  # Binary or grayscale
            return image.convert('RGB')

        elif mode == 'LA':  # Grayscale with alpha
            return image.convert('RGBA')

        elif mode in ['RGB', 'RGBA']:
            return image

        else:
            # Convert any other mode to RGB
            return image.convert('RGB')

    def _handle_transparency(self, image: Image.Image) -> Image.Image:
        """Handle transparency according to configuration."""
        if image.mode not in ['RGBA', 'LA']:
            return image

        transparency_method = self.config.handle_transparency

        if transparency_method == "white_background":
            # Create white background and composite
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                return Image.alpha_composite(
                    background.convert('RGBA'), image
                ).convert('RGB')
            else:  # LA mode
                background = Image.new('L', image.size, 255)
                alpha = image.split()[-1]
                gray = image.split()[0]
                # Simple alpha blending with white background
                result = Image.eval(gray, lambda x: int(255 * (1 - alpha.getpixel((0, 0)) / 255.0) + x * (alpha.getpixel((0, 0)) / 255.0)))
                return result.convert('RGB')

        elif transparency_method == "remove":
            # Remove fully transparent pixels (make them white)
            if image.mode == 'RGBA':
                data = np.array(image)
                # Make fully transparent pixels white
                transparent_mask = data[:, :, 3] == 0
                data[transparent_mask] = [255, 255, 255, 255]
                return Image.fromarray(data).convert('RGB')
            else:
                return image.convert('RGB')

        elif transparency_method == "preserve":
            # Keep transparency for later processing
            return image

        else:
            # Default: convert to RGB (removes transparency)
            return image.convert('RGB')

    def _correct_orientation(self, image: Image.Image) -> Image.Image:
        """Correct image orientation based on EXIF data."""
        try:
            # Use PIL's ImageOps.exif_transpose to handle orientation
            return ImageOps.exif_transpose(image)
        except Exception:
            # If EXIF processing fails, return original image
            return image

    def _resize_image(self, image: Image.Image, target_resolution: Tuple[int, int]) -> Image.Image:
        """
        Resize image to target resolution.

        Args:
            image: Source image
            target_resolution: Target (width, height)

        Returns:
            Resized image
        """
        target_width, target_height = target_resolution

        # Choose resampling method based on edge_mode
        if self.config.edge_mode == "hard":
            resample_method = Image.Resampling.NEAREST
        else:  # "smooth" or default
            resample_method = Image.Resampling.LANCZOS

        if self.config.preserve_aspect_ratio:
            # Calculate the scaling factor to fit within target dimensions
            scale_x = target_width / image.width
            scale_y = target_height / image.height
            scale = min(scale_x, scale_y)

            # Calculate new dimensions
            new_width = int(image.width * scale)
            new_height = int(image.height * scale)

            # Resize image
            resized = image.resize((new_width, new_height), resample_method)

            # If the resized image is smaller than target, pad it
            if new_width < target_width or new_height < target_height:
                # Create a new image with target dimensions and white background
                padded = Image.new(resized.mode, target_resolution,
                                   (255, 255, 255) if resized.mode == 'RGB' else
                                   (255, 255, 255, 255))

                # Calculate padding to center the image
                x_offset = (target_width - new_width) // 2
                y_offset = (target_height - new_height) // 2

                # Paste the resized image onto the padded background
                padded.paste(resized, (x_offset, y_offset))
                return padded
            else:
                return resized

        else:
            # Stretch to exact target dimensions
            return image.resize(target_resolution, resample_method)

    def get_image_array(self, image: Image.Image) -> np.ndarray:
        """
        Convert PIL Image to numpy array for processing.

        Args:
            image: PIL Image object

        Returns:
            Numpy array with shape (height, width, channels)
        """
        try:
            # Convert image to numpy array
            array = np.array(image)

            # Ensure we have the right shape
            if len(array.shape) == 2:  # Grayscale
                # Convert to RGB format
                array = np.stack([array, array, array], axis=2)
            elif len(array.shape) == 3 and array.shape[2] == 4:  # RGBA
                # Remove alpha channel if present
                array = array[:, :, :3]

            return array

        except Exception as e:
            raise ImageProcessingError(
                f"Failed to convert image to array: {e}",
                operation="image_to_array",
                cause=e
            )

    def array_to_image(self, array: np.ndarray) -> Image.Image:
        """
        Convert numpy array back to PIL Image.

        Args:
            array: Numpy array with shape (height, width, channels)

        Returns:
            PIL Image object
        """
        try:
            # Ensure array is in the right format
            if array.dtype != np.uint8:
                array = array.astype(np.uint8)

            # Create PIL Image
            if len(array.shape) == 2:
                return Image.fromarray(array, mode='L')
            elif len(array.shape) == 3 and array.shape[2] == 3:
                return Image.fromarray(array, mode='RGB')
            else:
                raise ValueError(f"Unsupported array shape: {array.shape}")

        except Exception as e:
            raise ImageProcessingError(
                f"Failed to convert array to image: {e}",
                operation="array_to_image",
                cause=e
            )

    def get_processing_info(self, original_image: Image.Image,
                            processed_images: List[Tuple[Tuple[int, int], Image.Image]]) -> dict:
        """
        Get information about the processing results.

        Args:
            original_image: Original source image
            processed_images: List of (resolution, processed_image) tuples

        Returns:
            Dictionary with processing information
        """
        info = {
            'original_size': (original_image.width, original_image.height),
            'original_mode': original_image.mode,
            'processed_resolutions': {},
            'transparency_handling': self.config.handle_transparency,
            'aspect_ratio_preserved': self.config.preserve_aspect_ratio
        }

        for resolution, processed_image in processed_images:
            resolution_name = self.config.get_resolution_name(*resolution)
            info['processed_resolutions'][resolution_name] = {
                'target_size': resolution,
                'actual_size': (processed_image.width, processed_image.height),
                'mode': processed_image.mode
            }

        return info