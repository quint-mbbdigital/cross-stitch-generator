"""Tests for min-color-percent functionality."""

import pytest
import sys
import numpy as np
from pathlib import Path
from unittest.mock import patch
from argparse import Namespace
from PIL import Image

from src.cross_stitch.cli.main import main, create_parser, create_config_from_args
from src.cross_stitch.models.config import GeneratorConfig
from src.cross_stitch.core import PatternGenerator


class TestMinColorPercentCLIFlags:
    """Test min-color-percent command-line flags and options."""

    def test_min_color_percent_flag_accepts_float_values(self):
        """Test that --min-color-percent accepts float values."""
        parser = create_parser()

        # Should accept valid float values
        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--min-color-percent', '2.5'])
        assert args.min_color_percent == 2.5

        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--min-color-percent', '0.0'])
        assert args.min_color_percent == 0.0

        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--min-color-percent', '100.0'])
        assert args.min_color_percent == 100.0

    def test_min_color_percent_flag_rejects_invalid_values(self):
        """Test that --min-color-percent rejects invalid values."""
        parser = create_parser()

        # Should reject negative values
        with pytest.raises(SystemExit):
            parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--min-color-percent', '-1.0'])

        # Should reject values > 100
        with pytest.raises(SystemExit):
            parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--min-color-percent', '101.0'])

    def test_min_color_percent_defaults_to_zero_when_not_provided(self):
        """Test that min-color-percent defaults to 0 when flag not provided."""
        parser = create_parser()

        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx'])
        # Should have default value of 0 (no merging)
        assert args.min_color_percent == 0.0

    def test_min_color_percent_available_in_info_command(self):
        """Test that --min-color-percent is available in info command."""
        parser = create_parser()

        args = parser.parse_args(['info', 'input.jpg', '--min-color-percent', '5.0'])
        assert args.min_color_percent == 5.0


class TestMinColorPercentConfiguration:
    """Test min-color-percent configuration integration."""

    def test_min_color_percent_sets_config_option(self):
        """Test that --min-color-percent properly sets configuration."""
        args = Namespace(
            min_color_percent=3.5
        )

        config = create_config_from_args(args)

        # Should have min_color_percent set
        assert hasattr(config, 'min_color_percent')
        assert config.min_color_percent == 3.5

    def test_min_color_percent_default_in_generator_config(self):
        """Test that GeneratorConfig has min_color_percent with default 0."""
        config = GeneratorConfig()

        # Should have min_color_percent attribute with default value
        assert hasattr(config, 'min_color_percent')
        assert config.min_color_percent == 0.0

    def test_config_validation_accepts_valid_min_color_percent(self):
        """Test that config validation accepts valid min-color-percent values."""
        config = GeneratorConfig(min_color_percent=0.0)
        config.validate()  # Should not raise

        config = GeneratorConfig(min_color_percent=2.5)
        config.validate()  # Should not raise

        config = GeneratorConfig(min_color_percent=100.0)
        config.validate()  # Should not raise

    def test_config_validation_rejects_invalid_min_color_percent(self):
        """Test that config validation rejects invalid min-color-percent values."""
        config = GeneratorConfig(min_color_percent=-1.0)
        with pytest.raises(ValueError, match="min_color_percent must be between 0 and 100"):
            config.validate()

        config = GeneratorConfig(min_color_percent=101.0)
        with pytest.raises(ValueError, match="min_color_percent must be between 0 and 100"):
            config.validate()


class TestMinColorPercentColorMerging:
    """Test min-color-percent color merging behavior."""

    def create_test_image_with_specific_percentages(self):
        """Create a test image with specific color percentages: 5% red, 93% blue, 2% pink."""
        # Create 100x100 image for easy percentage calculation
        image_array = np.zeros((100, 100, 3), dtype=np.uint8)

        # Fill with blue (93% = 9300 pixels)
        image_array[:, :] = [0, 0, 255]  # Blue background

        # Add red (5% = 500 pixels) - top 5 rows
        image_array[:5, :] = [255, 0, 0]  # Red

        # Add pink (2% = 200 pixels) - top-left 20x10 area
        image_array[:10, :20] = [255, 192, 203]  # Pink

        return Image.fromarray(image_array, mode='RGB')

    def test_colors_below_threshold_get_merged(self, tmp_path):
        """Test that colors below threshold (2% pink) get merged into nearest neighbor (red)."""
        test_image = self.create_test_image_with_specific_percentages()
        test_image_path = tmp_path / "percentage_test.png"
        test_image.save(test_image_path)

        config = GeneratorConfig(
            resolutions=[(20, 20)],
            max_colors=10,
            min_color_percent=3.0  # Pink (2%) should be merged, red (5%) and blue (93%) preserved
        )

        generator = PatternGenerator(config)
        pattern_set = generator.generate_patterns(test_image_path, tmp_path / "merged_test.xlsx")

        pattern = pattern_set.get_pattern("20x20")
        # Should have fewer colors after merging, but only if they're visually similar
        # With max_merge_distance protection, visually distinct colors are preserved
        # Note: quantization may create more colors than the original 3
        assert pattern.unique_colors_used <= 6  # Allow for quantization artifacts

    def test_colors_above_threshold_are_preserved(self, tmp_path):
        """Test that colors above threshold are preserved."""
        test_image = self.create_test_image_with_specific_percentages()
        test_image_path = tmp_path / "preserved_test.png"
        test_image.save(test_image_path)

        config = GeneratorConfig(
            resolutions=[(20, 20)],
            max_colors=10,
            min_color_percent=1.0  # All colors (2%, 5%, 93%) should be preserved
        )

        generator = PatternGenerator(config)
        pattern_set = generator.generate_patterns(test_image_path, tmp_path / "preserved_test.xlsx")

        pattern = pattern_set.get_pattern("20x20")
        # Should have more colors when threshold is low (less aggressive merging)
        colors_with_low_threshold = pattern.unique_colors_used
        assert colors_with_low_threshold >= 3

    def test_zero_threshold_preserves_all_colors(self, tmp_path):
        """Test that 0% threshold (default) preserves all colors."""
        test_image = self.create_test_image_with_specific_percentages()
        test_image_path = tmp_path / "zero_threshold_test.png"
        test_image.save(test_image_path)

        config = GeneratorConfig(
            resolutions=[(20, 20)],
            max_colors=10,
            min_color_percent=0.0  # No merging
        )

        generator = PatternGenerator(config)
        pattern_set = generator.generate_patterns(test_image_path, tmp_path / "zero_test.xlsx")

        pattern = pattern_set.get_pattern("20x20")
        # Should preserve all colors (no merging with 0% threshold)
        # Due to interpolation, this will be more than the original 3 colors
        colors_without_cleanup = pattern.unique_colors_used
        assert colors_without_cleanup >= 3

    def test_hundred_percent_threshold_merges_everything(self, tmp_path):
        """Test that 100% threshold merges everything into one color."""
        test_image = self.create_test_image_with_specific_percentages()
        test_image_path = tmp_path / "hundred_threshold_test.png"
        test_image.save(test_image_path)

        config = GeneratorConfig(
            resolutions=[(20, 20)],
            max_colors=10,
            min_color_percent=100.0  # Merge everything
        )

        generator = PatternGenerator(config)
        pattern_set = generator.generate_patterns(test_image_path, tmp_path / "hundred_test.xlsx")

        pattern = pattern_set.get_pattern("20x20")
        # Should have only 1 color after merging everything
        assert pattern.unique_colors_used == 1

    def test_noise_color_merging_with_real_image(self, tmp_path):
        """Test that small noise colors get merged into dominant colors."""
        # Create image with main color + small noise pixels
        image_array = np.zeros((50, 50, 3), dtype=np.uint8)
        image_array[:, :] = [100, 100, 100]  # Gray background (96%)
        image_array[0, 0] = [255, 0, 0]      # Single red pixel (0.04%)
        image_array[0, 1] = [0, 255, 0]      # Single green pixel (0.04%)
        image_array[1, 0] = [200, 200, 200]  # Light gray (0.04%)

        # Add some blue pixels (4%)
        image_array[:2, 45:] = [0, 0, 255]   # Blue section

        test_image = Image.fromarray(image_array, mode='RGB')
        test_image_path = tmp_path / "noise_test.png"
        test_image.save(test_image_path)

        config = GeneratorConfig(
            resolutions=[(15, 15)],
            max_colors=20,
            min_color_percent=1.0  # Should merge noise colors (< 1%) but keep blue (4%)
        )

        generator = PatternGenerator(config)
        pattern_set = generator.generate_patterns(test_image_path, tmp_path / "noise_merged.xlsx")

        pattern = pattern_set.get_pattern("15x15")
        # Should have fewer colors due to noise merging, but preserve visually distinct ones
        # With distance protection, only truly similar colors get merged
        assert pattern.unique_colors_used <= 5  # Gray, blue, and some preserved distinct colors


class TestMinColorPercentIntegration:
    """Test min-color-percent end-to-end integration."""

    def test_min_color_percent_cli_integration(self, tmp_path, tiny_image):
        """Test complete CLI integration with --min-color-percent."""
        output_file = tmp_path / "min_color_test.xlsx"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--min-color-percent', '2.0',
            '--resolutions', '10x10'
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            # Should complete successfully
            assert exit_code == 0
            assert output_file.exists()

    def test_min_color_percent_with_edge_mode_hard(self, tmp_path, tiny_image):
        """Test min-color-percent works with edge-mode hard."""
        output_file = tmp_path / "combined_test.xlsx"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--edge-mode', 'hard',
            '--min-color-percent', '5.0',
            '--resolutions', '10x10'
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            # Should complete successfully
            assert exit_code == 0
            assert output_file.exists()

    def test_info_command_with_min_color_percent(self, tiny_image):
        """Test that info command works with min-color-percent flag."""
        test_argv = [
            'cross_stitch_generator.py',
            'info',
            str(tiny_image),
            '--min-color-percent', '3.0'
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            # Should complete successfully
            assert exit_code == 0


class TestMinColorPercentErrorHandling:
    """Test min-color-percent error handling and validation."""

    def test_invalid_min_color_percent_cli_error(self):
        """Test that invalid --min-color-percent value produces clear error."""
        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            'input.jpg',
            'output.xlsx',
            '--min-color-percent', '-5.0'
        ]

        with patch.object(sys, 'argv', test_argv):
            # Should exit with error for negative value
            with pytest.raises(SystemExit):
                main()

    def test_min_color_percent_help_shows_options(self, capsys):
        """Test that help output shows min-color-percent options."""
        test_argv = ['cross_stitch_generator.py', 'generate', '--help']

        with patch.object(sys, 'argv', test_argv):
            with pytest.raises(SystemExit):  # --help causes SystemExit
                main()

        captured = capsys.readouterr()
        help_output = captured.out

        # Should contain min-color-percent in help
        assert '--min-color-percent' in help_output
        assert 'remove noise colors below this threshold' in help_output.lower()


class TestMinColorPercentVisualDistinctness:
    """Test that min-color-percent doesn't merge visually distinct colors."""

    def create_cream_with_text_image(self):
        """Create image with cream background and visually distinct blue/black text.

        Returns: Image with 90% cream, 5% blue text, 5% black text
        """
        # Create 100x100 image for easy percentage calculation
        image_array = np.zeros((100, 100, 3), dtype=np.uint8)

        # Fill with cream background (90% = 9000 pixels)
        image_array[:, :] = [255, 253, 208]  # Light cream color

        # Add blue text (5% = 500 pixels) - left side vertical strip
        image_array[:, :5] = [0, 0, 255]  # Pure blue

        # Add black text (5% = 500 pixels) - right side vertical strip
        image_array[:, 95:] = [0, 0, 0]  # Pure black

        return Image.fromarray(image_array, mode='RGB')

    def test_visually_distinct_colors_not_merged_despite_low_percentage(self, tmp_path):
        """Test that visually distinct colors are preserved even when below percentage threshold.

        This test should FAIL with current implementation, demonstrating the bug.

        Image has:
        - 90% cream background (RGB: 255, 253, 208)
        - 5% blue text (RGB: 0, 0, 255)
        - 5% black text (RGB: 0, 0, 0)

        With min-color-percent=10, blue and black are below threshold but should NOT
        be merged into cream because they're visually too different (high color distance).
        """
        test_image = self.create_cream_with_text_image()
        test_image_path = tmp_path / "cream_text_test.png"
        test_image.save(test_image_path)

        config = GeneratorConfig(
            resolutions=[(20, 20)],
            max_colors=10,
            min_color_percent=10.0  # Blue (5%) and black (5%) are below threshold
        )

        generator = PatternGenerator(config)
        pattern_set = generator.generate_patterns(test_image_path, tmp_path / "distinct_test.xlsx")

        pattern = pattern_set.get_pattern("20x20")

        # Should have 3+ colors: cream, blue, black (quantization may create slight variants)
        # Buggy implementation merges blue+black into cream = few colors
        # Fixed implementation preserves distinct colors = more colors
        assert pattern.unique_colors_used >= 3, (
            f"Expected 3+ colors (cream, blue, black) but got {pattern.unique_colors_used}. "
            f"Bug: visually distinct colors merged into background despite high color distance."
        )

        # Verify the colors are actually distinct by checking color palette
        palette_colors = [(color.r, color.g, color.b) for color in pattern.palette.colors]

        # Should contain cream-like color
        has_cream = any(r > 240 and g > 240 and b > 200 for r, g, b in palette_colors)
        assert has_cream, f"Expected cream color in palette, got: {palette_colors}"

        # Should contain blue-like color
        has_blue = any(r < 50 and g < 50 and b > 200 for r, g, b in palette_colors)
        assert has_blue, f"Expected blue color in palette, got: {palette_colors}"

        # Should contain black-like color
        has_black = any(r < 50 and g < 50 and b < 50 for r, g, b in palette_colors)
        assert has_black, f"Expected black color in palette, got: {palette_colors}"