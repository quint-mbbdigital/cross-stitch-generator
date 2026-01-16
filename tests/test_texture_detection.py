"""Tests for texture detection to warn about problematic background patterns."""

import pytest
import numpy as np
from PIL import Image
from pathlib import Path
import sys
from unittest.mock import patch
from io import StringIO

from src.cross_stitch.models.config import GeneratorConfig
from src.cross_stitch.core.pattern_generator import PatternGenerator
from src.cross_stitch.core.texture_detector import TextureDetector, TextureWarning
from src.cross_stitch.cli.main import main


class TestTextureDetectionFixtures:
    """Test fixtures for different image types."""

    def create_solid_color_image(self) -> Image.Image:
        """Create a solid color image with no texture."""
        image_array = np.full((100, 100, 3), [128, 128, 128], dtype=np.uint8)  # Solid gray
        return Image.fromarray(image_array, mode='RGB')

    def create_simple_gradient_image(self) -> Image.Image:
        """Create a natural gradient image (should not trigger texture warning)."""
        image_array = np.zeros((100, 100, 3), dtype=np.uint8)

        # Create smooth gradient from blue to red
        for y in range(100):
            for x in range(100):
                # Horizontal gradient
                r = int(255 * (x / 100))
                g = 0
                b = int(255 * ((100 - x) / 100))
                image_array[y, x] = [r, g, b]

        return Image.fromarray(image_array, mode='RGB')

    def create_fabric_texture_image(self) -> Image.Image:
        """Create an image with fabric-like cross-hatch texture."""
        # Base cream fabric color
        base_color = np.array([245, 240, 230], dtype=np.uint8)
        image_array = np.full((100, 100, 3), base_color, dtype=np.uint8)

        # Add cross-hatch texture pattern (simulating fabric weave)
        for y in range(100):
            for x in range(100):
                # Create subtle variation based on position
                variation = 0

                # Horizontal threads every 4 pixels
                if y % 4 < 2:
                    variation += 8
                else:
                    variation -= 4

                # Vertical threads every 4 pixels
                if x % 4 < 2:
                    variation += 6
                else:
                    variation -= 3

                # Add some noise
                variation += np.random.randint(-3, 4)

                # Apply variation to all color channels
                new_color = np.clip(base_color + variation, 0, 255)
                image_array[y, x] = new_color

        return Image.fromarray(image_array, mode='RGB')

    def create_halftone_pattern_image(self) -> Image.Image:
        """Create an image with halftone dot pattern (problematic texture)."""
        image_array = np.full((100, 100, 3), [200, 200, 200], dtype=np.uint8)  # Light gray base

        # Add halftone dots pattern
        for y in range(0, 100, 8):
            for x in range(0, 100, 8):
                # Create dots in a grid pattern
                center_y, center_x = y + 4, x + 4
                for dy in range(-3, 4):
                    for dx in range(-3, 4):
                        if 0 <= center_y + dy < 100 and 0 <= center_x + dx < 100:
                            distance = np.sqrt(dy*dy + dx*dx)
                            if distance <= 2.5:  # Create circular dots
                                # Make dots darker
                                image_array[center_y + dy, center_x + dx] = [160, 160, 160]

        return Image.fromarray(image_array, mode='RGB')


class TestTextureDetector:
    """Test the TextureDetector class functionality."""

    def test_texture_detector_exists(self):
        """Test that TextureDetector class can be instantiated."""
        detector = TextureDetector()
        assert detector is not None

    def test_solid_color_image_no_texture_warning(self, tmp_path):
        """Test that solid color images don't trigger texture warnings."""
        fixtures = TestTextureDetectionFixtures()
        solid_image = fixtures.create_solid_color_image()

        detector = TextureDetector()
        result = detector.analyze_texture(solid_image)

        assert isinstance(result, TextureWarning)
        assert result.has_problematic_texture == False
        assert result.warning_message == ""
        assert result.confidence_score < 0.3  # Low confidence of texture

    def test_fabric_texture_triggers_warning(self, tmp_path):
        """Test that fabric texture patterns trigger appropriate warnings."""
        fixtures = TestTextureDetectionFixtures()
        fabric_image = fixtures.create_fabric_texture_image()

        detector = TextureDetector()
        result = detector.analyze_texture(fabric_image)

        assert isinstance(result, TextureWarning)
        assert result.has_problematic_texture == True
        assert "texture" in result.warning_message.lower() or "background" in result.warning_message.lower()
        assert result.confidence_score > 0.6  # High confidence of problematic texture

    def test_gradient_image_no_texture_warning(self, tmp_path):
        """Test that natural gradients don't trigger texture warnings."""
        fixtures = TestTextureDetectionFixtures()
        gradient_image = fixtures.create_simple_gradient_image()

        detector = TextureDetector()
        result = detector.analyze_texture(gradient_image)

        assert isinstance(result, TextureWarning)
        assert result.has_problematic_texture == False

    def test_texture_warning_includes_helpful_suggestions(self, tmp_path):
        """Test that texture warnings include helpful suggestions."""
        fixtures = TestTextureDetectionFixtures()
        fabric_image = fixtures.create_fabric_texture_image()

        detector = TextureDetector()
        result = detector.analyze_texture(fabric_image)

        assert result.has_problematic_texture == True

        # Should include helpful suggestions
        message_lower = result.warning_message.lower()
        assert any(keyword in message_lower for keyword in [
            "preprocess", "blur", "fewer colors", "max-colors",
            "smooth", "filter", "reduce"
        ])


class TestTextureWarningModel:
    """Test the TextureWarning model."""

    def test_texture_warning_model_creation(self):
        """Test that TextureWarning model can be created."""
        warning = TextureWarning(
            has_problematic_texture=True,
            warning_message="Test warning",
            confidence_score=0.8,
            detection_details={
                'color_variance': 0.7,
                'clustered_colors': 0.9,
                'high_frequency': 0.6
            }
        )

        assert warning.has_problematic_texture is True
        assert warning.warning_message == "Test warning"
        assert warning.confidence_score == 0.8
        assert 'color_variance' in warning.detection_details


class TestPatternGeneratorTextureIntegration:
    """Test integration of texture detection with pattern generation."""

    def test_pattern_generator_checks_texture_before_processing(self, tmp_path):
        """Test that PatternGenerator includes texture checking."""
        fixtures = TestTextureDetectionFixtures()
        fabric_image = fixtures.create_fabric_texture_image()

        # Save test image
        image_path = tmp_path / "fabric_texture.png"
        fabric_image.save(image_path)

        config = GeneratorConfig(
            resolutions=[(20, 20)],
            max_colors=16,
            check_for_texture=True  # New config option
        )

        generator = PatternGenerator(config)

        # Should have method to get texture analysis
        texture_result = generator.analyze_image_texture(image_path)

        assert isinstance(texture_result, TextureWarning)
        if texture_result.has_problematic_texture:
            assert texture_result.warning_message != ""

    def test_texture_warning_displayed_in_info_command(self, tmp_path):
        """Test that info command shows texture warnings."""
        fixtures = TestTextureDetectionFixtures()
        fabric_image = fixtures.create_fabric_texture_image()

        # Save test image
        image_path = tmp_path / "fabric_info_test.png"
        fabric_image.save(image_path)

        config = GeneratorConfig(check_for_texture=True)
        generator = PatternGenerator(config)

        # Get processing info should include texture analysis
        info = generator.get_processing_info(image_path)

        assert 'texture_analysis' in info
        texture_info = info['texture_analysis']
        assert 'has_problematic_texture' in texture_info
        assert 'warning_message' in texture_info

    def test_texture_checking_can_be_disabled(self, tmp_path):
        """Test that texture checking can be disabled via config."""
        fixtures = TestTextureDetectionFixtures()
        fabric_image = fixtures.create_fabric_texture_image()

        image_path = tmp_path / "no_texture_check.png"
        fabric_image.save(image_path)

        config = GeneratorConfig(check_for_texture=False)
        generator = PatternGenerator(config)

        # Should not perform texture analysis when disabled
        info = generator.get_processing_info(image_path)

        # Texture analysis should be skipped
        if 'texture_analysis' in info:
            assert info['texture_analysis'].get('enabled', True) is False

    def test_cli_integration_texture_warning_displayed(self, tmp_path):
        """Test CLI integration: texture warnings appear in stderr but processing continues."""
        fixtures = TestTextureDetectionFixtures()
        fabric_image = fixtures.create_fabric_texture_image()

        # Save textured test image
        image_path = tmp_path / "textured_fabric.png"
        fabric_image.save(image_path)

        output_path = tmp_path / "test_cli_texture_output.xlsx"

        # Set up CLI arguments to generate patterns from textured image
        test_argv = [
            'cross_stitch_generator.py',
            '--quiet',  # Suppress progress output to focus on warnings
            'generate',
            str(image_path),
            str(output_path),
            '--resolutions', '20x20',
            '--max-colors', '16'
        ]

        # Capture stderr to check for texture warnings
        captured_stderr = StringIO()
        captured_stdout = StringIO()

        with patch.object(sys, 'argv', test_argv), \
             patch('sys.stderr', captured_stderr), \
             patch('sys.stdout', captured_stdout):

            exit_code = main()

        # Processing should complete successfully (warning doesn't block)
        assert exit_code == 0
        assert output_path.exists(), "Output file should be created despite texture warning"

        # Verify texture warning appears in stderr
        stderr_output = captured_stderr.getvalue()
        assert "WARNING:" in stderr_output, f"Expected WARNING in stderr, got: {stderr_output}"
        assert "texture" in stderr_output.lower() or "background" in stderr_output.lower(), \
               f"Expected texture/background warning in stderr, got: {stderr_output}"

        # Verify helpful suggestion is included
        assert any(keyword in stderr_output.lower() for keyword in [
            "preprocess", "blur", "max-colors", "smooth", "background"
        ]), f"Expected helpful suggestions in warning, got: {stderr_output}"

        # Verify processing continuation message appears
        assert "continue" in stderr_output.lower(), \
               f"Expected 'continue' message in stderr, got: {stderr_output}"