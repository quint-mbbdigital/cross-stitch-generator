"""Tests for edge-mode functionality."""

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


class TestEdgeModeCLIFlags:
    """Test edge-mode command-line flags and options."""

    def test_edge_mode_flag_accepts_smooth_value(self):
        """Test that --edge-mode accepts 'smooth' value."""
        parser = create_parser()

        # Should NOT raise SystemExit for valid value
        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--edge-mode', 'smooth'])
        assert args.edge_mode == 'smooth'

    def test_edge_mode_flag_accepts_hard_value(self):
        """Test that --edge-mode accepts 'hard' value."""
        parser = create_parser()

        # Should NOT raise SystemExit for valid value
        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--edge-mode', 'hard'])
        assert args.edge_mode == 'hard'

    def test_edge_mode_flag_rejects_invalid_value(self):
        """Test that --edge-mode rejects invalid values."""
        parser = create_parser()

        # Should raise SystemExit for invalid value
        with pytest.raises(SystemExit):
            parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--edge-mode', 'invalid'])

    def test_edge_mode_defaults_to_smooth_when_not_provided(self):
        """Test that edge-mode defaults to 'smooth' when flag not provided."""
        parser = create_parser()

        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx'])
        # Should have default value of 'smooth'
        assert args.edge_mode == 'smooth'

    def test_edge_mode_available_in_info_command(self):
        """Test that --edge-mode is available in info command for analysis."""
        parser = create_parser()

        args = parser.parse_args(['info', 'input.jpg', '--edge-mode', 'hard'])
        assert args.edge_mode == 'hard'


class TestEdgeModeConfiguration:
    """Test edge-mode configuration integration."""

    def test_edge_mode_smooth_sets_config_option(self):
        """Test that --edge-mode smooth properly sets configuration."""
        args = Namespace(
            edge_mode='smooth'
        )

        config = create_config_from_args(args)

        # Should have edge_mode set to smooth
        assert hasattr(config, 'edge_mode')
        assert config.edge_mode == 'smooth'

    def test_edge_mode_hard_sets_config_option(self):
        """Test that --edge-mode hard properly sets configuration."""
        args = Namespace(
            edge_mode='hard'
        )

        config = create_config_from_args(args)

        # Should have edge_mode set to hard
        assert hasattr(config, 'edge_mode')
        assert config.edge_mode == 'hard'

    def test_edge_mode_default_in_generator_config(self):
        """Test that GeneratorConfig has edge_mode with default 'smooth'."""
        config = GeneratorConfig()

        # Should have edge_mode attribute with default value
        assert hasattr(config, 'edge_mode')
        assert config.edge_mode == 'smooth'

    def test_config_validation_accepts_valid_edge_modes(self):
        """Test that config validation accepts valid edge-mode values."""
        config = GeneratorConfig(edge_mode='smooth')
        config.validate()  # Should not raise

        config = GeneratorConfig(edge_mode='hard')
        config.validate()  # Should not raise

    def test_config_validation_rejects_invalid_edge_mode(self):
        """Test that config validation rejects invalid edge-mode values."""
        config = GeneratorConfig(edge_mode='invalid')

        with pytest.raises(ValueError, match="Invalid edge_mode"):
            config.validate()


class TestEdgeModeImageProcessing:
    """Test edge-mode image processing behavior."""

    def create_simple_two_color_image(self):
        """Create a simple 2-color test image with hard edges."""
        # Create 6x6 image: left half blue (0,0,255), right half red (255,0,0)
        image_array = np.zeros((6, 6, 3), dtype=np.uint8)
        image_array[:, :3] = [0, 0, 255]    # Left half blue
        image_array[:, 3:] = [255, 0, 0]    # Right half red
        return Image.fromarray(image_array, mode='RGB')

    def test_smooth_mode_creates_interpolated_colors(self, tmp_path):
        """Test that smooth mode creates interpolated transition colors."""
        # Create simple 2-color image
        test_image = self.create_simple_two_color_image()
        test_image_path = tmp_path / "two_color_test.png"
        test_image.save(test_image_path)

        config = GeneratorConfig(
            resolutions=[(5, 5)],  # Minimum valid resolution
            max_colors=10,
            edge_mode='smooth'
        )

        generator = PatternGenerator(config)
        pattern_set = generator.generate_patterns(test_image_path, tmp_path / "smooth_test.xlsx")

        pattern = pattern_set.get_pattern("5x5")
        # Smooth mode should create MORE than 2 colors due to interpolation
        assert pattern.unique_colors_used > 2

    def test_hard_mode_preserves_original_colors(self, tmp_path):
        """Test that hard mode preserves exactly the original colors."""
        # Create simple 2-color image
        test_image = self.create_simple_two_color_image()
        test_image_path = tmp_path / "two_color_test.png"
        test_image.save(test_image_path)

        config = GeneratorConfig(
            resolutions=[(5, 5)],  # Minimum valid resolution
            max_colors=10,
            edge_mode='hard'
        )

        generator = PatternGenerator(config)
        pattern_set = generator.generate_patterns(test_image_path, tmp_path / "hard_test.xlsx")

        pattern = pattern_set.get_pattern("5x5")
        # Hard mode should preserve exactly 2 colors (no interpolated colors)
        assert pattern.unique_colors_used == 2

    def test_hard_mode_uses_nearest_neighbor_resampling(self, tmp_path):
        """Test that hard mode uses PIL.Image.NEAREST resampling method."""
        test_image = self.create_simple_two_color_image()
        test_image_path = tmp_path / "resampling_test.png"
        test_image.save(test_image_path)

        config = GeneratorConfig(
            resolutions=[(5, 5)],
            edge_mode='hard'
        )

        # Mock PIL Image.resize to verify NEAREST is used
        with patch.object(Image.Image, 'resize') as mock_resize:
            mock_resize.return_value = test_image.resize((5, 5), Image.NEAREST)

            generator = PatternGenerator(config)
            generator.generate_patterns(test_image_path, tmp_path / "mock_test.xlsx")

            # Verify resize was called with NEAREST resampling
            mock_resize.assert_called()
            call_args = mock_resize.call_args
            assert call_args[0][0] == (5, 5)  # Target size
            assert call_args[1]['resample'] == Image.NEAREST  # Should use NEAREST

    def test_smooth_mode_uses_lanczos_resampling(self, tmp_path):
        """Test that smooth mode uses PIL.Image.LANCZOS resampling method."""
        test_image = self.create_simple_two_color_image()
        test_image_path = tmp_path / "resampling_test.png"
        test_image.save(test_image_path)

        config = GeneratorConfig(
            resolutions=[(5, 5)],
            edge_mode='smooth'
        )

        # Mock PIL Image.resize to verify LANCZOS is used
        with patch.object(Image.Image, 'resize') as mock_resize:
            mock_resize.return_value = test_image.resize((5, 5), Image.LANCZOS)

            generator = PatternGenerator(config)
            generator.generate_patterns(test_image_path, tmp_path / "mock_test.xlsx")

            # Verify resize was called with LANCZOS resampling
            mock_resize.assert_called()
            call_args = mock_resize.call_args
            assert call_args[0][0] == (5, 5)  # Target size
            assert call_args[1]['resample'] == Image.LANCZOS  # Should use LANCZOS


class TestEdgeModeIntegration:
    """Test edge-mode end-to-end integration."""

    def test_edge_mode_hard_cli_integration(self, tmp_path, tiny_image):
        """Test complete CLI integration with --edge-mode hard."""
        output_file = tmp_path / "edge_mode_hard_test.xlsx"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--edge-mode', 'hard',
            '--resolutions', '8x8'
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            # Should complete successfully
            assert exit_code == 0
            assert output_file.exists()

    def test_edge_mode_smooth_cli_integration(self, tmp_path, tiny_image):
        """Test complete CLI integration with --edge-mode smooth."""
        output_file = tmp_path / "edge_mode_smooth_test.xlsx"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--edge-mode', 'smooth',
            '--resolutions', '8x8'
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            # Should complete successfully
            assert exit_code == 0
            assert output_file.exists()

    def test_edge_mode_default_cli_integration(self, tmp_path, tiny_image):
        """Test CLI integration with default edge-mode (should be smooth)."""
        output_file = tmp_path / "edge_mode_default_test.xlsx"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--resolutions', '8x8'
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            # Should complete successfully with default smooth mode
            assert exit_code == 0
            assert output_file.exists()

    def test_info_command_with_edge_mode(self, tiny_image):
        """Test that info command works with edge-mode flag."""
        test_argv = [
            'cross_stitch_generator.py',
            'info',
            str(tiny_image),
            '--edge-mode', 'hard'
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            # Should complete successfully
            assert exit_code == 0


class TestEdgeModeErrorHandling:
    """Test edge-mode error handling and validation."""

    def test_invalid_edge_mode_cli_error(self):
        """Test that invalid --edge-mode value produces clear error."""
        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            'input.jpg',
            'output.xlsx',
            '--edge-mode', 'invalid_value'
        ]

        with patch.object(sys, 'argv', test_argv):
            # Should exit with error for invalid edge mode
            with pytest.raises(SystemExit):
                main()

    def test_edge_mode_help_shows_options(self, capsys):
        """Test that help output shows edge-mode options."""
        test_argv = ['cross_stitch_generator.py', 'generate', '--help']

        with patch.object(sys, 'argv', test_argv):
            with pytest.raises(SystemExit):  # --help causes SystemExit
                main()

        captured = capsys.readouterr()
        help_output = captured.out

        # Should contain edge-mode in help
        assert '--edge-mode' in help_output
        assert 'smooth' in help_output
        assert 'hard' in help_output