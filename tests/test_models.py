"""Tests for cross-stitch data models."""

import pytest
import numpy as np
from pathlib import Path

from src.cross_stitch.models import (
    Color, ColorPalette, GeneratorConfig,
    CrossStitchPattern, PatternSet
)


class TestColor:
    """Test Color model."""

    def test_color_creation(self):
        """Test basic color creation."""
        color = Color(r=255, g=128, b=64)
        assert color.r == 255
        assert color.g == 128
        assert color.b == 64
        assert color.name is None
        assert color.thread_code is None

    def test_color_with_metadata(self):
        """Test color creation with metadata."""
        color = Color(r=100, g=150, b=200, name="Sky Blue", thread_code="DMC-518")
        assert color.name == "Sky Blue"
        assert color.thread_code == "DMC-518"

    def test_hex_code_property(self):
        """Test hex code generation."""
        color = Color(r=255, g=0, b=128)
        assert color.hex_code == "#ff0080"

        color = Color(r=0, g=0, b=0)
        assert color.hex_code == "#000000"

        color = Color(r=255, g=255, b=255)
        assert color.hex_code == "#ffffff"

    def test_rgb_tuple_property(self):
        """Test RGB tuple property."""
        color = Color(r=123, g=45, b=67)
        assert color.rgb_tuple == (123, 45, 67)

    def test_color_validation(self):
        """Test color value validation."""
        # Valid colors should work
        Color(r=0, g=0, b=0)
        Color(r=255, g=255, b=255)
        Color(r=128, g=64, b=192)

        # Invalid colors should raise ValueError
        with pytest.raises(ValueError, match="Color component r must be 0-255"):
            Color(r=-1, g=0, b=0)

        with pytest.raises(ValueError, match="Color component g must be 0-255"):
            Color(r=0, g=256, b=0)

        with pytest.raises(ValueError, match="Color component b must be 0-255"):
            Color(r=0, g=0, b=300)

    def test_from_hex(self):
        """Test creating color from hex string."""
        # Test with # prefix
        color = Color.from_hex("#ff8040")
        assert color.r == 255
        assert color.g == 128
        assert color.b == 64

        # Test without # prefix
        color = Color.from_hex("80ff40")
        assert color.r == 128
        assert color.g == 255
        assert color.b == 64

        # Test with metadata
        color = Color.from_hex("#ffffff", name="White", thread_code="DMC-B5200")
        assert color.rgb_tuple == (255, 255, 255)
        assert color.name == "White"
        assert color.thread_code == "DMC-B5200"

        # Test invalid hex codes
        with pytest.raises(ValueError, match="Invalid hex color code"):
            Color.from_hex("#gggggg")

        with pytest.raises(ValueError, match="Invalid hex color code"):
            Color.from_hex("12345")

    def test_from_rgb(self):
        """Test creating color from RGB tuple."""
        color = Color.from_rgb((200, 100, 50))
        assert color.r == 200
        assert color.g == 100
        assert color.b == 50

        # Test with metadata
        color = Color.from_rgb((0, 0, 0), name="Black")
        assert color.rgb_tuple == (0, 0, 0)
        assert color.name == "Black"

    def test_distance_to(self):
        """Test color distance calculation."""
        red = Color(r=255, g=0, b=0)
        green = Color(r=0, g=255, b=0)
        blue = Color(r=0, g=0, b=255)

        # Distance from red to green
        distance = red.distance_to(green)
        expected = ((255-0)**2 + (0-255)**2 + (0-0)**2) ** 0.5
        assert abs(distance - expected) < 0.001

        # Distance to itself should be 0
        assert red.distance_to(red) == 0

        # Distance should be symmetric
        assert abs(red.distance_to(blue) - blue.distance_to(red)) < 0.001

    def test_color_string_representation(self):
        """Test color string representation."""
        color = Color(r=255, g=128, b=64)
        assert str(color) == "#ff8040"

        color_with_name = Color(r=255, g=0, b=0, name="Red")
        assert str(color_with_name) == "Red (#ff0000)"


class TestColorPalette:
    """Test ColorPalette model."""

    def test_palette_creation(self, sample_colors):
        """Test basic palette creation."""
        palette = ColorPalette(colors=sample_colors[:3])
        assert len(palette) == 3
        assert palette.max_colors == 256
        assert palette.quantization_method == "median_cut"

    def test_palette_validation(self, sample_colors):
        """Test palette validation."""
        # Too many colors should raise error
        too_many_colors = sample_colors * 100  # 500 colors
        with pytest.raises(ValueError, match="Too many colors"):
            ColorPalette(colors=too_many_colors, max_colors=256)

    def test_add_color(self, sample_colors):
        """Test adding colors to palette."""
        palette = ColorPalette(colors=[])

        # Add first color
        index = palette.add_color(sample_colors[0])
        assert index == 0
        assert len(palette) == 1

        # Add different color
        index = palette.add_color(sample_colors[1])
        assert index == 1
        assert len(palette) == 2

        # Add same color again (should return existing index)
        index = palette.add_color(sample_colors[0])
        assert index == 0
        assert len(palette) == 2

    def test_add_color_full_palette(self, sample_colors):
        """Test adding color to full palette."""
        # Create palette at max capacity
        palette = ColorPalette(colors=sample_colors, max_colors=5)

        # Adding another color should fail
        new_color = Color(r=128, g=128, b=128)
        with pytest.raises(ValueError, match="Cannot add color: palette full"):
            palette.add_color(new_color)

    def test_get_color_by_index(self, sample_palette):
        """Test getting color by index."""
        color = sample_palette.get_color_by_index(0)
        assert color == sample_palette.colors[0]

        # Invalid index should raise error
        with pytest.raises(IndexError, match="Color index .* out of range"):
            sample_palette.get_color_by_index(100)

    def test_find_closest_color(self, sample_colors):
        """Test finding closest color in palette."""
        palette = ColorPalette(colors=sample_colors[:3])  # Red, Green, Blue

        # Find closest to orange (should be red)
        orange = Color(r=255, g=128, b=0)
        closest, index = palette.find_closest_color(orange)
        assert index == 0  # Red is at index 0
        assert closest.r == 255 and closest.g == 0 and closest.b == 0

        # Test empty palette
        empty_palette = ColorPalette(colors=[])
        with pytest.raises(ValueError, match="Palette is empty"):
            empty_palette.find_closest_color(orange)

    def test_palette_iteration(self, sample_palette):
        """Test palette iteration and indexing."""
        # Test iteration
        colors = [color for color in sample_palette]
        assert len(colors) == len(sample_palette.colors)

        # Test indexing
        assert sample_palette[0] == sample_palette.colors[0]
        assert sample_palette[1] == sample_palette.colors[1]

    def test_to_rgb_array(self, sample_palette):
        """Test converting palette to RGB array."""
        rgb_array = sample_palette.to_rgb_array()
        assert len(rgb_array) == len(sample_palette)
        assert rgb_array[0] == (255, 0, 0)  # Red
        assert rgb_array[1] == (0, 255, 0)  # Green


class TestGeneratorConfig:
    """Test GeneratorConfig model."""

    def test_default_config(self):
        """Test default configuration."""
        config = GeneratorConfig()
        assert config.resolutions == [(50, 50), (100, 100), (150, 150)]
        assert config.max_colors == 256
        assert config.quantization_method == "median_cut"
        assert config.preserve_aspect_ratio is True
        assert config.handle_transparency == "white_background"
        assert config.excel_cell_size == 20.0
        assert config.include_color_legend is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = GeneratorConfig(
            resolutions=[(25, 25), (200, 200)],
            max_colors=128,
            quantization_method="kmeans",
            preserve_aspect_ratio=False
        )
        assert config.resolutions == [(25, 25), (200, 200)]
        assert config.max_colors == 128
        assert config.quantization_method == "kmeans"
        assert config.preserve_aspect_ratio is False

    def test_config_validation(self):
        """Test configuration validation."""
        config = GeneratorConfig()
        config.validate()  # Should not raise

        # Test invalid resolutions
        config.resolutions = []
        with pytest.raises(ValueError, match="At least one resolution must be specified"):
            config.validate()

        config.resolutions = [(-1, 50)]
        with pytest.raises(ValueError, match="Invalid resolution"):
            config.validate()

        config.resolutions = [(1001, 50)]
        with pytest.raises(ValueError, match="Resolution too large"):
            config.validate()

        # Test invalid max_colors
        config.resolutions = [(50, 50)]
        config.max_colors = 0
        with pytest.raises(ValueError, match="max_colors must be between 1 and"):
            config.validate()

        # Test invalid quantization method
        config.max_colors = 256
        config.quantization_method = "invalid"
        with pytest.raises(ValueError, match="Unknown quantization method"):
            config.validate()

    def test_get_resolution_name(self):
        """Test resolution name generation."""
        config = GeneratorConfig()
        assert config.get_resolution_name(50, 75) == "50x75"
        assert config.get_resolution_name(100, 100) == "100x100"

    def test_get_output_filename(self):
        """Test output filename generation."""
        config = GeneratorConfig()
        filename = config.get_output_filename("/path/to/image.jpg")
        assert filename == "image_cross_stitch.xlsx"

        filename = config.get_output_filename("test.png")
        assert filename == "test_cross_stitch.xlsx"


class TestCrossStitchPattern:
    """Test CrossStitchPattern model."""

    def test_pattern_creation(self, sample_pattern):
        """Test basic pattern creation."""
        assert sample_pattern.width == 10
        assert sample_pattern.height == 10
        assert sample_pattern.colors.shape == (10, 10)
        assert sample_pattern.resolution_name == "10x10"

    def test_pattern_validation(self, sample_palette):
        """Test pattern validation."""
        # Valid pattern
        colors = np.array([[0, 1], [2, 3]])
        pattern = CrossStitchPattern(
            width=2, height=2, colors=colors,
            palette=sample_palette, resolution_name="2x2"
        )

        # Invalid dimensions
        with pytest.raises(ValueError, match="Invalid dimensions"):
            CrossStitchPattern(
                width=0, height=10, colors=colors,
                palette=sample_palette, resolution_name="test"
            )

        # Mismatched color array shape
        colors_wrong_shape = np.array([[0, 1, 2]])  # 1x3 instead of 2x2
        with pytest.raises(ValueError, match="Color array shape.*doesn't match dimensions"):
            CrossStitchPattern(
                width=2, height=2, colors=colors_wrong_shape,
                palette=sample_palette, resolution_name="test"
            )

        # Invalid color indices
        colors_invalid = np.array([[0, 99]])  # Index 99 doesn't exist in palette
        with pytest.raises(ValueError, match="Color indices must be between 0 and"):
            CrossStitchPattern(
                width=1, height=1, colors=colors_invalid,
                palette=sample_palette, resolution_name="test"
            )

    def test_pattern_properties(self, sample_pattern):
        """Test pattern properties."""
        assert sample_pattern.total_stitches == 100
        assert sample_pattern.unique_colors_used <= 5  # At most 5 different colors

    def test_get_color_at(self, sample_pattern):
        """Test getting color at specific coordinates."""
        color_index = sample_pattern.get_color_at(0, 0)
        assert 0 <= color_index < len(sample_pattern.palette)

        stitch_color = sample_pattern.get_stitch_color(0, 0)
        assert stitch_color == sample_pattern.palette[color_index]

        # Test out of bounds
        with pytest.raises(IndexError, match="Coordinates.*out of bounds"):
            sample_pattern.get_color_at(20, 5)

    def test_color_usage_stats(self, sample_pattern):
        """Test color usage statistics."""
        stats = sample_pattern.get_color_usage_stats()
        assert isinstance(stats, dict)
        assert sum(stats.values()) == sample_pattern.total_stitches

    def test_pattern_area(self, sample_pattern):
        """Test getting pattern area."""
        area = sample_pattern.get_pattern_area(2, 3, 6, 8)
        assert area.shape == (5, 4)  # 8-3 = 5 rows, 6-2 = 4 columns

    def test_to_dict(self, sample_pattern):
        """Test pattern dictionary conversion."""
        pattern_dict = sample_pattern.to_dict()
        assert pattern_dict['width'] == 10
        assert pattern_dict['height'] == 10
        assert pattern_dict['total_stitches'] == 100
        assert 'unique_colors_used' in pattern_dict
        assert 'color_usage' in pattern_dict


class TestPatternSet:
    """Test PatternSet model."""

    def test_pattern_set_creation(self, sample_pattern, sample_image_rgb):
        """Test basic pattern set creation."""
        patterns = {"10x10": sample_pattern}
        pattern_set = PatternSet(
            patterns=patterns,
            source_image_path=sample_image_rgb,
            metadata={"test": True}
        )

        assert pattern_set.pattern_count == 1
        assert sample_image_rgb in pattern_set.source_image_path.parents or \
               pattern_set.source_image_path == sample_image_rgb

    def test_pattern_set_validation(self, sample_image_rgb):
        """Test pattern set validation."""
        # Empty patterns should fail
        with pytest.raises(ValueError, match="PatternSet must contain at least one pattern"):
            PatternSet(patterns={}, source_image_path=sample_image_rgb, metadata={})

        # Non-existent source path should fail
        fake_path = Path("/nonexistent/image.jpg")
        patterns = {"test": sample_pattern}
        with pytest.raises(ValueError, match="Source image path does not exist"):
            PatternSet(patterns=patterns, source_image_path=fake_path, metadata={})

    def test_get_pattern(self, sample_pattern, sample_image_rgb):
        """Test getting pattern by name."""
        patterns = {"10x10": sample_pattern}
        pattern_set = PatternSet(
            patterns=patterns,
            source_image_path=sample_image_rgb,
            metadata={}
        )

        retrieved_pattern = pattern_set.get_pattern("10x10")
        assert retrieved_pattern == sample_pattern

        # Non-existent pattern should raise KeyError
        with pytest.raises(KeyError, match="Pattern 'nonexistent' not found"):
            pattern_set.get_pattern("nonexistent")

    def test_get_pattern_by_size(self, sample_pattern, sample_image_rgb):
        """Test getting pattern by exact dimensions."""
        patterns = {"10x10": sample_pattern}
        pattern_set = PatternSet(
            patterns=patterns,
            source_image_path=sample_image_rgb,
            metadata={}
        )

        found_pattern = pattern_set.get_pattern_by_size(10, 10)
        assert found_pattern == sample_pattern

        not_found = pattern_set.get_pattern_by_size(20, 20)
        assert not_found is None

    def test_pattern_set_properties(self, sample_pattern, sample_image_rgb):
        """Test pattern set properties."""
        patterns = {"10x10": sample_pattern, "test": sample_pattern}
        pattern_set = PatternSet(
            patterns=patterns,
            source_image_path=sample_image_rgb,
            metadata={}
        )

        assert pattern_set.pattern_count == 2
        assert "10x10" in pattern_set.resolution_names
        assert "test" in pattern_set.resolution_names

    def test_get_summary(self, sample_pattern, sample_image_rgb):
        """Test getting pattern set summary."""
        patterns = {"10x10": sample_pattern}
        pattern_set = PatternSet(
            patterns=patterns,
            source_image_path=sample_image_rgb,
            metadata={"generator": "test"}
        )

        summary = pattern_set.get_summary()
        assert 'source_image' in summary
        assert 'pattern_count' in summary
        assert summary['pattern_count'] == 1
        assert 'patterns' in summary
        assert '10x10' in summary['patterns']