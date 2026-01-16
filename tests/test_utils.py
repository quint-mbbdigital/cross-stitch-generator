"""Tests for cross-stitch utility functions."""

import pytest
from PIL import Image
import os

from src.cross_stitch.utils import (
    load_image,
    save_file,
    validate_output_path,
    get_image_info,
    validate_image_file,
    validate_config,
    validate_resolution_for_image,
    ValidationError,
    ImageProcessingError,
    FileOperationError,
)
from src.cross_stitch.models import GeneratorConfig


class TestFileUtils:
    """Test file utility functions."""

    def test_load_image_success(self, sample_image_rgb):
        """Test successful image loading."""
        image = load_image(sample_image_rgb)
        assert isinstance(image, Image.Image)
        assert image.size == (100, 100)
        assert image.mode in ["RGB", "RGBA"]

    def test_load_image_rgba(self, sample_image_rgba):
        """Test loading RGBA image."""
        image = load_image(sample_image_rgba)
        assert isinstance(image, Image.Image)
        assert image.size == (50, 50)
        assert image.mode == "RGBA"

    def test_load_image_grayscale(self, sample_image_grayscale):
        """Test loading grayscale image."""
        image = load_image(sample_image_grayscale)
        assert isinstance(image, Image.Image)
        assert image.size == (75, 75)
        assert image.mode == "L"

    def test_load_image_nonexistent(self, nonexistent_image_path):
        """Test loading non-existent image."""
        with pytest.raises(FileOperationError, match="Image file does not exist"):
            load_image(nonexistent_image_path)

    def test_load_image_invalid(self, temp_dir):
        """Test loading invalid image file."""
        # Create a file with .png extension but invalid content
        invalid_path = temp_dir / "corrupted.png"
        invalid_path.write_bytes(b"This is not a PNG file")

        with pytest.raises(ImageProcessingError, match="Cannot identify image file"):
            load_image(invalid_path)

    def test_load_image_unsupported_format(self, temp_dir):
        """Test loading unsupported file format."""
        unsupported_file = temp_dir / "test.xyz"
        unsupported_file.write_text("fake image data")

        with pytest.raises(ImageProcessingError, match="Unsupported image format"):
            load_image(unsupported_file)

    def test_validate_output_path_success(self, temp_dir):
        """Test successful output path validation."""
        output_path = temp_dir / "output.xlsx"
        validated_path = validate_output_path(output_path)

        assert validated_path.suffix == ".xlsx"
        assert validated_path.parent.exists()

    def test_validate_output_path_add_extension(self, temp_dir):
        """Test adding .xlsx extension automatically."""
        output_path = temp_dir / "output"
        validated_path = validate_output_path(output_path)

        assert validated_path.suffix == ".xlsx"
        assert str(validated_path).endswith("output.xlsx")

    def test_validate_output_path_create_directory(self, temp_dir):
        """Test creating parent directory."""
        output_path = temp_dir / "new_dir" / "output.xlsx"
        validated_path = validate_output_path(output_path)

        assert validated_path.parent.exists()
        assert validated_path.suffix == ".xlsx"

    def test_validate_output_path_not_writable(self, temp_dir):
        """Test handling non-writable directory."""
        if os.name == "posix":  # Unix-like systems
            # Create directory and remove write permission
            read_only_dir = temp_dir / "readonly"
            read_only_dir.mkdir()
            read_only_dir.chmod(0o444)  # Read-only

            output_path = read_only_dir / "output.xlsx"
            with pytest.raises(FileOperationError, match="not writable"):
                validate_output_path(output_path)

            # Clean up (restore permissions)
            read_only_dir.chmod(0o755)

    def test_save_file_success(self, temp_dir):
        """Test successful file saving."""
        test_data = b"Hello, world!"
        output_path = temp_dir / "test.xlsx"

        saved_path = save_file(test_data, output_path)
        assert saved_path.exists()
        assert saved_path.read_bytes() == test_data

    def test_save_file_with_backup(self, temp_dir):
        """Test file saving with backup of existing file."""
        output_path = temp_dir / "existing.xlsx"
        original_data = b"Original data"
        new_data = b"New data"

        # Create existing file
        output_path.write_bytes(original_data)

        # Save new data (should create backup)
        saved_path = save_file(new_data, output_path, backup_existing=True)

        assert saved_path.exists()
        assert saved_path.read_bytes() == new_data
        # Backup should be cleaned up after successful save

    def test_get_image_info_success(self, sample_image_rgb):
        """Test getting image information."""
        info = get_image_info(sample_image_rgb)

        assert info["width"] == 100
        assert info["height"] == 100
        assert info["mode"] in ["RGB", "RGBA"]
        assert info["format"] is not None
        assert info["file_size"] > 0
        assert isinstance(info["has_transparency"], bool)

    def test_get_image_info_rgba(self, sample_image_rgba):
        """Test getting info for RGBA image."""
        info = get_image_info(sample_image_rgba)

        assert info["has_transparency"] is True
        assert info["mode"] == "RGBA"

    def test_get_image_info_nonexistent(self, nonexistent_image_path):
        """Test getting info for non-existent image."""
        with pytest.raises(FileOperationError, match="Image file does not exist"):
            get_image_info(nonexistent_image_path)


class TestValidation:
    """Test validation functions."""

    def test_validate_image_file_success(self, sample_image_rgb):
        """Test successful image file validation."""
        validate_image_file(sample_image_rgb)  # Should not raise

    def test_validate_image_file_nonexistent(self, nonexistent_image_path):
        """Test validating non-existent image file."""
        with pytest.raises(ValidationError, match="Image file does not exist"):
            validate_image_file(nonexistent_image_path)

    def test_validate_image_file_not_file(self, temp_dir):
        """Test validating directory instead of file."""
        with pytest.raises(ValidationError, match="Path is not a file"):
            validate_image_file(temp_dir)

    def test_validate_image_file_unsupported_format(self, invalid_image_path):
        """Test validating unsupported file format."""
        with pytest.raises(ValidationError, match="Unsupported image format"):
            validate_image_file(invalid_image_path)

    def test_validate_image_file_too_large(self, temp_dir):
        """Test validating very large image file."""
        # Create a fake large file
        large_file = temp_dir / "large.png"
        # Write 150MB of data (over the 100MB limit)
        large_data = b"x" * (150 * 1024 * 1024)
        large_file.write_bytes(large_data)

        with pytest.raises(ValidationError, match="Image file too large"):
            validate_image_file(large_file)

    def test_validate_image_file_too_small(self, temp_dir):
        """Test validating image that's too small."""
        # Create a very small image (3x3, below minimum of 5x5)
        small_image = Image.new("RGB", (3, 3), color=(255, 0, 0))
        small_path = temp_dir / "small.png"
        small_image.save(small_path)

        with pytest.raises(ValidationError, match="Image too small"):
            validate_image_file(small_path)

    def test_validate_config_success(self, sample_config):
        """Test successful config validation."""
        validate_config(sample_config)  # Should not raise

    def test_validate_config_empty_resolutions(self):
        """Test validating config with empty resolutions."""
        config = GeneratorConfig(resolutions=[])
        with pytest.raises(
            ValidationError, match="At least one resolution must be specified"
        ):
            validate_config(config)

    def test_validate_config_invalid_resolution(self):
        """Test validating config with invalid resolution."""
        config = GeneratorConfig(resolutions=[(0, 50)])
        with pytest.raises(ValidationError, match="Invalid resolution"):
            validate_config(config)

    def test_validate_config_duplicate_resolutions(self):
        """Test validating config with duplicate resolutions."""
        config = GeneratorConfig(resolutions=[(50, 50), (100, 100), (50, 50)])
        with pytest.raises(ValidationError, match="Duplicate resolution"):
            validate_config(config)

    def test_validate_config_resolution_too_large(self):
        """Test validating config with resolution too large."""
        config = GeneratorConfig(resolutions=[(1001, 500)])
        with pytest.raises(ValidationError, match="Resolution too large"):
            validate_config(config)

    def test_validate_config_invalid_quantization(self):
        """Test validating config with invalid quantization method."""
        config = GeneratorConfig(quantization_method="invalid_method")
        with pytest.raises(ValidationError, match="Unknown quantization method"):
            validate_config(config)

    def test_validate_config_invalid_transparency(self):
        """Test validating config with invalid transparency handling."""
        config = GeneratorConfig(handle_transparency="invalid_method")
        with pytest.raises(ValidationError, match="Invalid transparency handling"):
            validate_config(config)

    def test_validate_config_invalid_cell_size(self):
        """Test validating config with invalid cell size."""
        config = GeneratorConfig(excel_cell_size=0)
        with pytest.raises(ValidationError, match="excel_cell_size must be positive"):
            validate_config(config)

        config = GeneratorConfig(excel_cell_size=150)
        with pytest.raises(ValidationError, match="Excel cell size too large"):
            validate_config(config)

    def test_validate_config_invalid_sheet_name(self):
        """Test validating config with invalid sheet name."""
        # Empty sheet name
        config = GeneratorConfig(legend_sheet_name="")
        with pytest.raises(ValidationError, match="Legend sheet name cannot be empty"):
            validate_config(config)

        # Too long sheet name
        config = GeneratorConfig(legend_sheet_name="a" * 40)
        with pytest.raises(ValidationError, match="Legend sheet name too long"):
            validate_config(config)

        # Invalid characters
        config = GeneratorConfig(legend_sheet_name="Sheet[1]")
        with pytest.raises(
            ValidationError, match="Legend sheet name contains invalid characters"
        ):
            validate_config(config)

    def test_validate_config_invalid_filename_template(self):
        """Test validating config with invalid filename template."""
        config = GeneratorConfig(output_filename_template="no_placeholder.xlsx")
        with pytest.raises(
            ValidationError, match="Output filename template must contain"
        ):
            validate_config(config)

    def test_validate_resolution_for_image_success(self, sample_image_rgb):
        """Test successful resolution validation for image."""
        validate_resolution_for_image(sample_image_rgb, (50, 50))  # Should not raise

    def test_validate_resolution_for_image_too_large(self, tiny_image):
        """Test resolution too large for image."""
        # 5x5 image, requesting 100x100 resolution (20x scale)
        with pytest.raises(ValidationError, match="Target resolution.*is too large"):
            validate_resolution_for_image(tiny_image, (100, 100))

    def test_validate_resolution_for_image_too_small(self, large_image):
        """Test resolution too small for image."""
        # 500x500 image, requesting 1x1 resolution (very small scale)
        with pytest.raises(ValidationError, match="Target resolution.*is too small"):
            validate_resolution_for_image(large_image, (1, 1))


class TestExceptions:
    """Test custom exception classes."""

    def test_cross_stitch_error_basic(self):
        """Test basic CrossStitchError."""
        from src.cross_stitch.utils.exceptions import CrossStitchError

        error = CrossStitchError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.cause is None

    def test_cross_stitch_error_with_cause(self):
        """Test CrossStitchError with cause."""
        from src.cross_stitch.utils.exceptions import CrossStitchError

        original_error = ValueError("Original error")
        error = CrossStitchError("Wrapper error", cause=original_error)

        assert "Wrapper error" in str(error)
        assert "Original error" in str(error)
        assert error.cause == original_error

    def test_validation_error_with_field(self):
        """Test ValidationError with field information."""
        error = ValidationError("Invalid value", field="test_field", value="bad_value")

        error_str = str(error)
        assert "test_field" in error_str
        assert "Invalid value" in error_str
        assert "bad_value" in error_str

    def test_image_processing_error_details(self):
        """Test ImageProcessingError with details."""
        error = ImageProcessingError(
            "Processing failed", image_path="/path/to/image.jpg", operation="resize"
        )

        error_str = str(error)
        assert "Processing failed" in error_str
        assert "/path/to/image.jpg" in error_str
        assert "resize" in error_str

    def test_file_operation_error_details(self):
        """Test FileOperationError with details."""
        error = FileOperationError(
            "Cannot save file", file_path="/path/to/output.xlsx", operation="save"
        )

        error_str = str(error)
        assert "Cannot save file" in error_str
        assert "/path/to/output.xlsx" in error_str
        assert "save" in error_str


class TestUtilityHelpers:
    """Test utility helper functions from conftest."""

    def test_assert_valid_color(self, sample_colors):
        """Test color validation helper."""
        from tests.conftest import assert_valid_color

        # Valid color should pass
        assert_valid_color(sample_colors[0])

        # This test would fail during Color creation due to validation,
        # so we just test that the helper works with valid colors
        for color in sample_colors:
            assert_valid_color(color)

    def test_assert_valid_palette(self, sample_palette):
        """Test palette validation helper."""
        from tests.conftest import assert_valid_palette

        assert_valid_palette(sample_palette)

    def test_assert_valid_pattern(self, sample_pattern):
        """Test pattern validation helper."""
        from tests.conftest import assert_valid_pattern

        assert_valid_pattern(sample_pattern)

    def test_create_test_image(self):
        """Test test image creation helper."""
        from tests.conftest import create_test_image

        # Create RGB image
        image = create_test_image(50, 30, "RGB")
        assert image.size == (50, 30)
        assert image.mode == "RGB"

        # Create RGBA image
        image = create_test_image(25, 25, "RGBA")
        assert image.size == (25, 25)
        assert image.mode == "RGBA"

        # Create grayscale image
        image = create_test_image(40, 60, "L")
        assert image.size == (40, 60)
        assert image.mode == "L"

        # Invalid mode should raise error
        with pytest.raises(ValueError, match="Unsupported mode"):
            create_test_image(10, 10, "INVALID")
