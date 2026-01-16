"""Main orchestration class for cross-stitch pattern generation."""

from typing import Union, Dict, Any, Optional, Callable
from pathlib import Path
import logging

from ..models import GeneratorConfig, PatternSet, CrossStitchPattern
from ..utils import (
    validate_config, validate_image_file, validate_resolution_for_image,
    PatternGenerationError, ImageProcessingError, ColorQuantizationError,
    ExcelGenerationError
)
from .image_processor import ImageProcessor
from .color_manager import ColorManager
from .excel_generator import ExcelGenerator
from .texture_detector import TextureDetector, TextureWarning


# Set up logging
logger = logging.getLogger(__name__)


class PatternGenerator:
    """Main class for generating cross-stitch patterns from images."""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """
        Initialize PatternGenerator with configuration.

        Args:
            config: Generator configuration. If None, default config is used.
        """
        self.config = config or GeneratorConfig()

        # Validate configuration
        validate_config(self.config)

        # Initialize component classes
        self.image_processor = ImageProcessor(self.config)
        self.color_manager = ColorManager(self.config)
        self.excel_generator = ExcelGenerator(self.config)

        # Progress tracking
        self.progress_callback: Optional[Callable[[str, float], None]] = None

    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """
        Set callback function for progress reporting.

        Args:
            callback: Function that takes (message: str, progress: float) where
                     progress is between 0.0 and 1.0
        """
        self.progress_callback = callback

    def generate_patterns(self, image_path: Union[str, Path],
                          output_path: Union[str, Path]) -> PatternSet:
        """
        Generate complete cross-stitch pattern set from image.

        Args:
            image_path: Path to source image file
            output_path: Path where to save Excel file

        Returns:
            PatternSet containing all generated patterns

        Raises:
            PatternGenerationError: If pattern generation fails
        """
        try:
            self._report_progress("Starting pattern generation...", 0.0)

            # Convert paths
            image_path = Path(image_path)
            output_path = Path(output_path)

            # Validate inputs
            self._validate_inputs(image_path)
            self._report_progress("Input validation complete", 0.1)

            # Load and process image
            processed_image = self._load_and_process_image(image_path)
            self._report_progress("Image loaded and processed", 0.2)

            # Generate patterns for all resolutions
            patterns = self._generate_all_patterns(processed_image, str(image_path))
            self._report_progress("All patterns generated", 0.8)

            # Create pattern set
            pattern_set = PatternSet(
                patterns=patterns,
                source_image_path=image_path,
                metadata=self._generate_metadata(processed_image)
            )

            # Generate Excel file
            self._generate_excel_output(pattern_set, output_path)
            self._report_progress("Excel file generated", 0.9)

            self._report_progress("Pattern generation complete!", 1.0)

            return pattern_set

        except Exception as e:
            error_msg = f"Pattern generation failed: {e}"
            logger.error(error_msg, exc_info=True)

            if isinstance(e, (ImageProcessingError, ColorQuantizationError, ExcelGenerationError)):
                raise PatternGenerationError(
                    error_msg,
                    stage="generation",
                    cause=e
                )
            else:
                raise PatternGenerationError(
                    error_msg,
                    stage="unknown",
                    cause=e
                )

    def generate_single_pattern(self, image_path: Union[str, Path],
                                resolution: tuple[int, int]) -> CrossStitchPattern:
        """
        Generate a single cross-stitch pattern at specified resolution.

        Args:
            image_path: Path to source image file
            resolution: Target resolution (width, height)

        Returns:
            Single CrossStitchPattern object

        Raises:
            PatternGenerationError: If pattern generation fails
        """
        try:
            image_path = Path(image_path)
            resolution_name = self.config.get_resolution_name(*resolution)

            self._report_progress(f"Generating pattern for {resolution_name}...", 0.0)

            # Validate inputs
            validate_image_file(image_path)
            validate_resolution_for_image(image_path, resolution)

            # Load and process image
            processed_image = self._load_and_process_image(image_path)
            self._report_progress("Image processed", 0.3)

            # Resize to target resolution
            resized = self.image_processor._resize_image(processed_image, resolution)
            self._report_progress("Image resized", 0.5)

            # Quantize colors
            palette, color_indices = self.color_manager.quantize_image(resized)
            self._report_progress("Colors quantized", 0.8)

            # Create pattern object
            pattern = CrossStitchPattern(
                width=resolution[0],
                height=resolution[1],
                colors=color_indices,
                palette=palette,
                resolution_name=resolution_name
            )

            self._report_progress("Pattern generation complete", 1.0)

            return pattern

        except Exception as e:
            raise PatternGenerationError(
                f"Single pattern generation failed: {e}",
                resolution=f"{resolution[0]}x{resolution[1]}",
                stage="single_generation",
                cause=e
            )

    def _validate_inputs(self, image_path: Path) -> None:
        """Validate input parameters."""
        try:
            # Validate image file
            validate_image_file(image_path)

            # Validate resolutions for this image
            for resolution in self.config.resolutions:
                validate_resolution_for_image(image_path, resolution)

        except Exception as e:
            raise PatternGenerationError(
                f"Input validation failed: {e}",
                stage="validation",
                cause=e
            )

    def _load_and_process_image(self, image_path: Path):
        """Load and process image for pattern generation."""
        try:
            return self.image_processor.load_and_process_image(image_path)

        except ImageProcessingError as e:
            raise PatternGenerationError(
                f"Image processing failed: {e}",
                stage="image_processing",
                cause=e
            )

    def _generate_all_patterns(self, image, image_path: str) -> Dict[str, CrossStitchPattern]:
        """Generate patterns for all configured resolutions."""
        patterns = {}

        try:
            # Resize image to all target resolutions
            resized_images = self.image_processor.resize_to_resolutions(image, image_path)

            total_resolutions = len(resized_images)
            for i, (resolution, resized_image) in enumerate(resized_images):
                resolution_name = self.config.get_resolution_name(*resolution)

                try:
                    # Report progress for this resolution
                    progress = 0.2 + (0.6 * i / total_resolutions)
                    self._report_progress(f"Processing {resolution_name}...", progress)

                    # Quantize colors for this resolution
                    palette, color_indices = self.color_manager.quantize_image(resized_image)

                    # Create pattern object
                    pattern = CrossStitchPattern(
                        width=resolution[0],
                        height=resolution[1],
                        colors=color_indices,
                        palette=palette,
                        resolution_name=resolution_name
                    )

                    patterns[resolution_name] = pattern

                except Exception as e:
                    raise PatternGenerationError(
                        f"Failed to generate pattern for {resolution_name}: {e}",
                        resolution=resolution_name,
                        stage="pattern_creation",
                        cause=e
                    )

            return patterns

        except Exception as e:
            if isinstance(e, PatternGenerationError):
                raise
            raise PatternGenerationError(
                f"Pattern generation failed: {e}",
                stage="pattern_generation",
                cause=e
            )

    def _generate_excel_output(self, pattern_set: PatternSet, output_path: Path) -> None:
        """Generate Excel file from pattern set."""
        try:
            self.excel_generator.generate_excel_file(pattern_set, output_path)

        except ExcelGenerationError as e:
            raise PatternGenerationError(
                f"Excel generation failed: {e}",
                stage="excel_generation",
                cause=e
            )

    def _generate_metadata(self, processed_image) -> Dict[str, Any]:
        """Generate metadata about the processing."""
        return {
            'config': {
                'resolutions': self.config.resolutions,
                'max_colors': self.config.max_colors,
                'quantization_method': self.config.quantization_method,
                'preserve_aspect_ratio': self.config.preserve_aspect_ratio,
                'handle_transparency': self.config.handle_transparency
            },
            'processing_info': {
                'original_size': (processed_image.width, processed_image.height),
                'original_mode': processed_image.mode
            }
        }

    def _report_progress(self, message: str, progress: float) -> None:
        """Report progress if callback is set."""
        if self.progress_callback:
            try:
                self.progress_callback(message, progress)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    def get_processing_info(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about what processing would be performed without actually doing it.

        Args:
            image_path: Path to source image

        Returns:
            Dictionary with processing information
        """
        try:
            image_path = Path(image_path)

            # Load image info without full processing
            from ..utils import get_image_info
            image_info = get_image_info(image_path)

            # Calculate target sizes for each resolution
            target_info = {}
            for resolution in self.config.resolutions:
                resolution_name = self.config.get_resolution_name(*resolution)
                target_info[resolution_name] = {
                    'target_size': resolution,
                    'scale_factor_x': resolution[0] / image_info['width'],
                    'scale_factor_y': resolution[1] / image_info['height']
                }

            # Add texture analysis if enabled
            texture_info = {}
            if self.config.check_for_texture:
                texture_result = self.analyze_image_texture(image_path)
                texture_info = {
                    'enabled': True,
                    'has_problematic_texture': texture_result.has_problematic_texture,
                    'warning_message': texture_result.warning_message,
                    'confidence_score': texture_result.confidence_score
                }
            else:
                texture_info = {'enabled': False}

            return {
                'source_image': {
                    'path': str(image_path),
                    'size': (image_info['width'], image_info['height']),
                    'mode': image_info['mode'],
                    'format': image_info['format'],
                    'file_size': image_info['file_size'],
                    'has_transparency': image_info['has_transparency']
                },
                'target_resolutions': target_info,
                'config': {
                    'max_colors': self.config.max_colors,
                    'quantization_method': self.config.quantization_method,
                    'transparency_handling': self.config.handle_transparency,
                    'preserve_aspect_ratio': self.config.preserve_aspect_ratio
                },
                'texture_analysis': texture_info
            }

        except Exception as e:
            raise PatternGenerationError(
                f"Failed to get processing info: {e}",
                stage="info_gathering",
                cause=e
            )

    def estimate_processing_time(self, image_path: Union[str, Path]) -> Dict[str, float]:
        """
        Estimate processing time for the image (rough estimates).

        Args:
            image_path: Path to source image

        Returns:
            Dictionary with time estimates in seconds
        """
        try:
            from ..utils import get_image_info
            image_info = get_image_info(image_path)

            # Base estimates (very rough)
            base_load_time = 0.5
            base_resize_time = 0.1 * len(self.config.resolutions)

            # Scale based on image size (pixels)
            total_pixels = image_info['width'] * image_info['height']
            pixel_factor = total_pixels / (1024 * 768)  # Relative to ~800K pixels

            # Scale based on number of target colors
            color_factor = self.config.max_colors / 64

            estimates = {
                'image_loading': base_load_time * pixel_factor,
                'image_resizing': base_resize_time * pixel_factor,
                'color_quantization': 1.0 * pixel_factor * color_factor * len(self.config.resolutions),
                'excel_generation': 0.5 * len(self.config.resolutions),
                'total': 0
            }

            estimates['total'] = sum(estimates.values())

            return estimates

        except Exception:
            # Return default estimates if calculation fails
            return {
                'image_loading': 1.0,
                'image_resizing': 1.0,
                'color_quantization': 5.0,
                'excel_generation': 2.0,
                'total': 9.0
            }

    def analyze_image_texture(self, image_path: Union[str, Path]) -> TextureWarning:
        """
        Analyze image for problematic texture patterns.

        Args:
            image_path: Path to source image

        Returns:
            TextureWarning object with analysis results
        """
        try:
            from ..utils import load_image

            # Load the image
            image = load_image(image_path)

            # Create texture detector and analyze
            detector = TextureDetector()
            result = detector.analyze_texture(image)

            return result

        except Exception as e:
            # Return safe default if analysis fails
            logger.warning(f"Texture analysis failed: {e}")
            return TextureWarning(
                has_problematic_texture=False,
                warning_message="",
                confidence_score=0.0,
                detection_details={'error': str(e)}
            )