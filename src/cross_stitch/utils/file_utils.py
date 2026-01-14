"""File I/O utilities for cross-stitch pattern generation."""

import os
from pathlib import Path
from typing import Union
from PIL import Image, UnidentifiedImageError

from .exceptions import FileOperationError, ImageProcessingError


# Supported image formats
SUPPORTED_IMAGE_FORMATS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp'
}

# Excel file extension
EXCEL_EXTENSION = '.xlsx'


def validate_output_path(output_path: Union[str, Path]) -> Path:
    """
    Validate and prepare output file path.

    Args:
        output_path: Path where the Excel file will be saved

    Returns:
        Validated Path object

    Raises:
        FileOperationError: If path validation fails
    """
    try:
        path = Path(output_path)

        # Ensure it has .xlsx extension
        if path.suffix.lower() != EXCEL_EXTENSION:
            path = path.with_suffix(EXCEL_EXTENSION)

        # Check if parent directory exists, create if needed
        parent_dir = path.parent
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise FileOperationError(
                    f"Cannot create output directory: {e}",
                    file_path=str(parent_dir),
                    operation="create_directory",
                    cause=e
                )

        # Check if parent directory is writable
        if not os.access(parent_dir, os.W_OK):
            raise FileOperationError(
                "Output directory is not writable",
                file_path=str(parent_dir),
                operation="check_permissions"
            )

        # Check if file exists and is writable (if it exists)
        if path.exists() and not os.access(path, os.W_OK):
            raise FileOperationError(
                "Output file exists but is not writable",
                file_path=str(path),
                operation="check_permissions"
            )

        return path

    except Exception as e:
        if isinstance(e, FileOperationError):
            raise
        raise FileOperationError(
            f"Invalid output path: {e}",
            file_path=str(output_path),
            operation="validate_path",
            cause=e
        )


def load_image(image_path: Union[str, Path]) -> Image.Image:
    """
    Load and validate an image file.

    Args:
        image_path: Path to the image file

    Returns:
        PIL Image object

    Raises:
        ImageProcessingError: If image loading fails
        FileOperationError: If file access fails
    """
    try:
        path = Path(image_path)

        # Check if file exists
        if not path.exists():
            raise FileOperationError(
                "Image file does not exist",
                file_path=str(path),
                operation="load_image"
            )

        # Check if file is readable
        if not os.access(path, os.R_OK):
            raise FileOperationError(
                "Image file is not readable",
                file_path=str(path),
                operation="load_image"
            )

        # Check file extension
        if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
            supported = ", ".join(sorted(SUPPORTED_IMAGE_FORMATS))
            raise ImageProcessingError(
                f"Unsupported image format '{path.suffix}'. Supported formats: {supported}",
                image_path=str(path),
                operation="validate_format"
            )

        # Load the image
        try:
            image = Image.open(path)
            # Verify the image by loading it completely
            image.load()
            return image

        except UnidentifiedImageError as e:
            raise ImageProcessingError(
                "Cannot identify image file - file may be corrupted or in unsupported format",
                image_path=str(path),
                operation="load_image",
                cause=e
            )

        except OSError as e:
            raise ImageProcessingError(
                f"Cannot open image file: {e}",
                image_path=str(path),
                operation="load_image",
                cause=e
            )

    except Exception as e:
        if isinstance(e, (ImageProcessingError, FileOperationError)):
            raise
        raise ImageProcessingError(
            f"Unexpected error loading image: {e}",
            image_path=str(image_path),
            operation="load_image",
            cause=e
        )


def save_file(data: bytes, output_path: Union[str, Path],
              backup_existing: bool = True) -> Path:
    """
    Save binary data to file with optional backup of existing file.

    Args:
        data: Binary data to save
        output_path: Path where to save the file
        backup_existing: Whether to backup existing file

    Returns:
        Path object of saved file

    Raises:
        FileOperationError: If saving fails
    """
    try:
        path = validate_output_path(output_path)

        # Create backup if file exists and backup is requested
        backup_path = None
        if backup_existing and path.exists():
            backup_path = path.with_suffix(f'{path.suffix}.backup')
            try:
                backup_path.write_bytes(path.read_bytes())
            except OSError as e:
                raise FileOperationError(
                    f"Cannot create backup file: {e}",
                    file_path=str(backup_path),
                    operation="create_backup",
                    cause=e
                )

        # Save the data
        try:
            path.write_bytes(data)
        except OSError as e:
            # If backup was created, try to restore it
            if backup_path and backup_path.exists():
                try:
                    path.write_bytes(backup_path.read_bytes())
                    backup_path.unlink()  # Remove backup after restoration
                except OSError:
                    pass  # Restoration failed, but original error is more important

            raise FileOperationError(
                f"Cannot save file: {e}",
                file_path=str(path),
                operation="save_file",
                cause=e
            )

        # Clean up backup if save was successful
        if backup_path and backup_path.exists():
            try:
                backup_path.unlink()
            except OSError:
                # Backup cleanup failed, but save was successful
                pass

        return path

    except Exception as e:
        if isinstance(e, FileOperationError):
            raise
        raise FileOperationError(
            f"Unexpected error saving file: {e}",
            file_path=str(output_path),
            operation="save_file",
            cause=e
        )


def get_image_info(image_path: Union[str, Path]) -> dict:
    """
    Get basic information about an image file without fully loading it.

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary with image information

    Raises:
        ImageProcessingError: If reading image info fails
    """
    try:
        path = Path(image_path)

        if not path.exists():
            raise FileOperationError(
                "Image file does not exist",
                file_path=str(path),
                operation="get_image_info"
            )

        with Image.open(path) as image:
            info = {
                'width': image.width,
                'height': image.height,
                'mode': image.mode,
                'format': image.format,
                'file_size': path.stat().st_size,
                'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
            }

        return info

    except Exception as e:
        if isinstance(e, (ImageProcessingError, FileOperationError)):
            raise
        raise ImageProcessingError(
            f"Cannot get image info: {e}",
            image_path=str(image_path),
            operation="get_image_info",
            cause=e
        )


def ensure_directory(directory_path: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory

    Returns:
        Path object of the directory

    Raises:
        FileOperationError: If directory creation fails
    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    except OSError as e:
        raise FileOperationError(
            f"Cannot create directory: {e}",
            file_path=str(directory_path),
            operation="create_directory",
            cause=e
        )