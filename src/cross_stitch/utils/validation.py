"""Input validation utilities for cross-stitch pattern generation."""

import os
from pathlib import Path
from typing import Union, List, Tuple


from ..models import GeneratorConfig
from .exceptions import ValidationError, ImageProcessingError
from .file_utils import SUPPORTED_IMAGE_FORMATS, get_image_info


def validate_image_file(image_path: Union[str, Path]) -> None:
    """
    Validate an image file for cross-stitch pattern generation.

    Args:
        image_path: Path to the image file to validate

    Raises:
        ValidationError: If validation fails
    """
    try:
        path = Path(image_path)

        # Check if file exists
        if not path.exists():
            raise ValidationError(
                "Image file does not exist",
                field="image_path",
                value=str(path)
            )

        # Check if it's a file (not directory)
        if not path.is_file():
            raise ValidationError(
                "Path is not a file",
                field="image_path",
                value=str(path)
            )

        # Check file extension
        if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
            supported = ", ".join(sorted(SUPPORTED_IMAGE_FORMATS))
            raise ValidationError(
                f"Unsupported image format '{path.suffix}'. Supported: {supported}",
                field="image_format",
                value=path.suffix
            )

        # Check file size (not too large)
        file_size = path.stat().st_size
        max_size_mb = 100  # 100MB limit
        max_size_bytes = max_size_mb * 1024 * 1024

        if file_size > max_size_bytes:
            size_mb = file_size / (1024 * 1024)
            raise ValidationError(
                f"Image file too large: {size_mb:.1f}MB (max {max_size_mb}MB)",
                field="file_size",
                value=f"{size_mb:.1f}MB"
            )

        # Check if file is readable
        if not os.access(path, os.R_OK):
            raise ValidationError(
                "Image file is not readable",
                field="file_permissions",
                value=str(path)
            )

        # Get image information and validate
        try:
            info = get_image_info(path)
        except ImageProcessingError as e:
            raise ValidationError(
                f"Cannot read image file: {e.message}",
                field="image_content",
                value=str(path)
            )

        # Check image dimensions
        width, height = info['width'], info['height']

        if width <= 0 or height <= 0:
            raise ValidationError(
                f"Invalid image dimensions: {width}x{height}",
                field="image_dimensions",
                value=f"{width}x{height}"
            )

        # Check minimum dimensions
        min_size = 5
        if width < min_size or height < min_size:
            raise ValidationError(
                f"Image too small: {width}x{height} (minimum {min_size}x{min_size})",
                field="image_dimensions",
                value=f"{width}x{height}"
            )

        # Check maximum dimensions
        max_size = 5000
        if width > max_size or height > max_size:
            raise ValidationError(
                f"Image too large: {width}x{height} (maximum {max_size}x{max_size})",
                field="image_dimensions",
                value=f"{width}x{height}"
            )

        # Check color mode
        mode = info['mode']
        supported_modes = {'RGB', 'RGBA', 'L', 'LA', 'P'}
        if mode not in supported_modes:
            raise ValidationError(
                f"Unsupported color mode: {mode}. Supported: {', '.join(supported_modes)}",
                field="color_mode",
                value=mode
            )

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(
            f"Image validation failed: {e}",
            field="image_file",
            value=str(image_path)
        )


def validate_config(config: GeneratorConfig) -> None:
    """
    Validate a generator configuration object.

    Args:
        config: Configuration to validate

    Raises:
        ValidationError: If validation fails
    """
    try:
        # Use the built-in validation from the config object
        config.validate()

    except ValueError as e:
        # Convert ValueError to ValidationError with more context
        message = str(e)

        # Try to extract field name from error message
        field = None
        if "resolution" in message.lower():
            field = "resolutions"
        elif "max_colors" in message.lower():
            field = "max_colors"
        elif "quantization" in message.lower():
            field = "quantization_method"
        elif "transparency" in message.lower():
            field = "handle_transparency"
        elif "cell_size" in message.lower():
            field = "excel_cell_size"

        raise ValidationError(message, field=field)

    # Additional validation beyond what's in the config object
    _validate_resolutions(config.resolutions)
    _validate_quantization_method(config.quantization_method)
    _validate_transparency_handling(config.handle_transparency)
    _validate_excel_settings(config)


def _validate_resolutions(resolutions: List[Tuple[int, int]]) -> None:
    """Validate resolution list."""
    if not resolutions:
        raise ValidationError("At least one resolution must be specified", field="resolutions")

    seen_resolutions = set()
    for width, height in resolutions:
        # Check for duplicates
        resolution_tuple = (width, height)
        if resolution_tuple in seen_resolutions:
            raise ValidationError(
                f"Duplicate resolution: {width}x{height}",
                field="resolutions",
                value=f"{width}x{height}"
            )
        seen_resolutions.add(resolution_tuple)

        # Check individual dimensions
        if width <= 0 or height <= 0:
            raise ValidationError(
                f"Invalid resolution dimensions: {width}x{height}",
                field="resolutions",
                value=f"{width}x{height}"
            )

        # Check reasonable limits
        if width > 1000 or height > 1000:
            raise ValidationError(
                f"Resolution too large: {width}x{height} (max 1000x1000)",
                field="resolutions",
                value=f"{width}x{height}"
            )

        # Check minimum size
        min_size = 5
        if width < min_size or height < min_size:
            raise ValidationError(
                f"Resolution too small: {width}x{height} (min {min_size}x{min_size})",
                field="resolutions",
                value=f"{width}x{height}"
            )


def _validate_quantization_method(method: str) -> None:
    """Validate color quantization method."""
    valid_methods = {"median_cut", "kmeans"}
    if method not in valid_methods:
        raise ValidationError(
            f"Invalid quantization method: {method}. Valid methods: {', '.join(valid_methods)}",
            field="quantization_method",
            value=method
        )


def _validate_transparency_handling(handling: str) -> None:
    """Validate transparency handling method."""
    valid_methods = {"white_background", "remove", "preserve"}
    if handling not in valid_methods:
        raise ValidationError(
            f"Invalid transparency handling: {handling}. Valid methods: {', '.join(valid_methods)}",
            field="handle_transparency",
            value=handling
        )


def _validate_excel_settings(config: GeneratorConfig) -> None:
    """Validate Excel-specific settings."""
    # Validate cell size
    if config.excel_cell_size <= 0:
        raise ValidationError(
            "Excel cell size must be positive",
            field="excel_cell_size",
            value=str(config.excel_cell_size)
        )

    if config.excel_cell_size > 100:
        raise ValidationError(
            f"Excel cell size too large: {config.excel_cell_size} (max 100 points)",
            field="excel_cell_size",
            value=str(config.excel_cell_size)
        )

    # Validate legend sheet name
    if not config.legend_sheet_name or not config.legend_sheet_name.strip():
        raise ValidationError(
            "Legend sheet name cannot be empty",
            field="legend_sheet_name",
            value=config.legend_sheet_name
        )

    # Check Excel sheet name limits (Excel has a 31 character limit)
    if len(config.legend_sheet_name) > 31:
        raise ValidationError(
            f"Legend sheet name too long: {len(config.legend_sheet_name)} chars (max 31)",
            field="legend_sheet_name",
            value=config.legend_sheet_name
        )

    # Check for invalid characters in sheet name
    invalid_chars = {'\\', '/', '*', '?', ':', '[', ']'}
    if any(char in config.legend_sheet_name for char in invalid_chars):
        raise ValidationError(
            f"Legend sheet name contains invalid characters: {', '.join(invalid_chars)}",
            field="legend_sheet_name",
            value=config.legend_sheet_name
        )

    # Validate filename template
    if not config.output_filename_template or '{base_name}' not in config.output_filename_template:
        raise ValidationError(
            "Output filename template must contain '{base_name}' placeholder",
            field="output_filename_template",
            value=config.output_filename_template
        )


def validate_resolution_for_image(image_path: Union[str, Path],
                                  resolution: Tuple[int, int]) -> None:
    """
    Validate that a resolution is reasonable for a given image.

    Args:
        image_path: Path to the image file
        resolution: Target resolution (width, height)

    Raises:
        ValidationError: If resolution is inappropriate for the image
    """
    try:
        info = get_image_info(image_path)
        image_width, image_height = info['width'], info['height']
        target_width, target_height = resolution

        # Check if target resolution is much larger than source
        scale_factor_x = target_width / image_width
        scale_factor_y = target_height / image_height
        max_scale = max(scale_factor_x, scale_factor_y)

        if max_scale > 10:
            raise ValidationError(
                f"Target resolution {target_width}x{target_height} is too large for "
                f"source image {image_width}x{image_height} (scale factor: {max_scale:.1f}x, max: 10x)",
                field="resolution_scale",
                value=f"{target_width}x{target_height}"
            )

        # Check if target resolution is extremely small compared to source
        min_scale = min(scale_factor_x, scale_factor_y)
        if min_scale < 0.01:
            raise ValidationError(
                f"Target resolution {target_width}x{target_height} is too small for "
                f"source image {image_width}x{image_height} (scale factor: {min_scale:.3f}x, min: 0.01x)",
                field="resolution_scale",
                value=f"{target_width}x{target_height}"
            )

    except ImageProcessingError as e:
        raise ValidationError(
            f"Cannot validate resolution for image: {e.message}",
            field="image_file",
            value=str(image_path)
        )