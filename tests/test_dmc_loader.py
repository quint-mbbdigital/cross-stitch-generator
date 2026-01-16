"""Tests for DMC color database loader."""

import pytest

from src.cross_stitch.data.dmc_loader import load_dmc_palette
from src.cross_stitch.models.color_palette import Color


class TestDMCLoader:
    """Test DMC color palette loading functionality."""

    def test_load_dmc_palette_returns_dict_of_colors(self, tmp_path):
        """Test that load_dmc_palette returns dictionary mapping DMC codes to Color objects."""
        # Create a temporary CSV file with sample DMC colors
        csv_content = """dmc_code,name,r,g,b,hex_code
310,Black,0,0,0,000000
BLANC,White,255,255,255,FFFFFF
666,Bright Red,227,29,66,E31D42"""

        csv_file = tmp_path / "test_dmc_colors.csv"
        csv_file.write_text(csv_content)

        # Load the palette
        palette = load_dmc_palette(str(csv_file))

        # Should return a dictionary
        assert isinstance(palette, dict)
        assert len(palette) == 3

        # All values should be Color objects
        assert all(isinstance(color, Color) for color in palette.values())

        # Check specific colors exist as keys
        assert "310" in palette
        assert "BLANC" in palette
        assert "666" in palette

    def test_loaded_colors_use_existing_color_model_properly(self, tmp_path):
        """Test that loaded colors populate Color model fields correctly."""
        csv_content = """dmc_code,name,r,g,b,hex_code
702,Kelly Green,71,167,47,47A72F
3371,Black Brown,27,20,16,1B1410"""

        csv_file = tmp_path / "test_dmc_colors.csv"
        csv_file.write_text(csv_content)

        palette = load_dmc_palette(str(csv_file))

        # Check Kelly Green
        kelly_green = palette["702"]
        assert kelly_green.r == 71
        assert kelly_green.g == 167
        assert kelly_green.b == 47
        assert kelly_green.name == "Kelly Green"
        assert kelly_green.thread_code == "702"
        assert kelly_green.hex_code == "#47a72f"  # Property should work
        assert kelly_green.rgb_tuple == (71, 167, 47)  # Property should work

        # Check Black Brown
        black_brown = palette["3371"]
        assert black_brown.r == 27
        assert black_brown.g == 20
        assert black_brown.b == 16
        assert black_brown.name == "Black Brown"
        assert black_brown.thread_code == "3371"

    def test_known_dmc_codes_have_correct_colors(self, tmp_path):
        """Test that specific known DMC codes load with correct RGB values."""
        csv_content = """dmc_code,name,r,g,b,hex_code
310,Black,0,0,0,000000
BLANC,White,255,255,255,FFFFFF"""

        csv_file = tmp_path / "test_dmc_colors.csv"
        csv_file.write_text(csv_content)

        palette = load_dmc_palette(str(csv_file))

        # Test DMC 310 (Black)
        black = palette["310"]
        assert black.rgb_tuple == (0, 0, 0)
        assert black.name == "Black"
        assert black.thread_code == "310"

        # Test DMC BLANC (White)
        white = palette["BLANC"]
        assert white.rgb_tuple == (255, 255, 255)
        assert white.name == "White"
        assert white.thread_code == "BLANC"

    def test_all_rgb_values_are_valid_range(self, tmp_path):
        """Test that all loaded colors have RGB values in valid 0-255 range."""
        csv_content = """dmc_code,name,r,g,b,hex_code
310,Black,0,0,0,000000
BLANC,White,255,255,255,FFFFFF
702,Kelly Green,71,167,47,47A72F
3371,Black Brown,27,20,16,1B1410
666,Bright Red,227,29,66,E31D42"""

        csv_file = tmp_path / "test_dmc_colors.csv"
        csv_file.write_text(csv_content)

        palette = load_dmc_palette(str(csv_file))

        # Check every color has valid RGB range
        for dmc_code, color in palette.items():
            assert 0 <= color.r <= 255, (
                f"DMC {dmc_code} has invalid red value: {color.r}"
            )
            assert 0 <= color.g <= 255, (
                f"DMC {dmc_code} has invalid green value: {color.g}"
            )
            assert 0 <= color.b <= 255, (
                f"DMC {dmc_code} has invalid blue value: {color.b}"
            )

    def test_missing_csv_file_handled_gracefully(self):
        """Test that missing CSV file is handled gracefully without crashing."""
        non_existent_path = "/path/that/does/not/exist.csv"

        # Should not raise an exception
        palette = load_dmc_palette(non_existent_path)

        # Should return empty dictionary
        assert isinstance(palette, dict)
        assert len(palette) == 0

    def test_default_path_behavior(self):
        """Test behavior when no CSV path is provided (uses default)."""
        # Should not crash when called without parameters
        palette = load_dmc_palette()

        # Should return a dictionary (empty if default file doesn't exist)
        assert isinstance(palette, dict)

    def test_invalid_csv_format_raises_error(self, tmp_path):
        """Test that invalid CSV format raises appropriate error."""
        # Missing required columns
        csv_content = """code,color,red,green,blue
310,Black,0,0,0"""

        csv_file = tmp_path / "bad_dmc_colors.csv"
        csv_file.write_text(csv_content)

        with pytest.raises(ValueError, match="Invalid DMC CSV format"):
            load_dmc_palette(str(csv_file))

    def test_invalid_rgb_values_raise_error(self, tmp_path):
        """Test that RGB values outside 0-255 range raise errors."""
        # RGB value > 255
        csv_content = """dmc_code,name,r,g,b,hex_code
310,Black,0,0,0,000000
BAD,Invalid Color,300,0,0,FF0000"""

        csv_file = tmp_path / "invalid_dmc_colors.csv"
        csv_file.write_text(csv_content)

        with pytest.raises(ValueError, match="RGB values must be between 0 and 255"):
            load_dmc_palette(str(csv_file))

    def test_duplicate_dmc_codes_handled_gracefully(self, tmp_path):
        """Test that duplicate DMC codes are handled gracefully."""
        csv_content = """dmc_code,name,r,g,b,hex_code
310,Black,0,0,0,000000
310,Also Black,10,10,10,0A0A0A
BLANC,White,255,255,255,FFFFFF"""

        csv_file = tmp_path / "duplicate_dmc_colors.csv"
        csv_file.write_text(csv_content)

        palette = load_dmc_palette(str(csv_file))

        # Should handle duplicates (implementation choice: use first occurrence)
        assert len(palette) == 2  # Only unique codes
        assert "310" in palette
        assert "BLANC" in palette

    def test_empty_csv_returns_empty_palette(self, tmp_path):
        """Test that empty CSV file returns empty palette."""
        csv_content = """dmc_code,name,r,g,b,hex_code"""  # Headers only, no data

        csv_file = tmp_path / "empty_dmc_colors.csv"
        csv_file.write_text(csv_content)

        palette = load_dmc_palette(str(csv_file))

        assert isinstance(palette, dict)
        assert len(palette) == 0

    def test_color_distance_calculation_works_with_dmc_colors(self, tmp_path):
        """Test that loaded DMC colors work with existing Color.distance_to() method."""
        csv_content = """dmc_code,name,r,g,b,hex_code
310,Black,0,0,0,000000
BLANC,White,255,255,255,FFFFFF"""

        csv_file = tmp_path / "test_dmc_colors.csv"
        csv_file.write_text(csv_content)

        palette = load_dmc_palette(str(csv_file))

        black = palette["310"]
        white = palette["BLANC"]

        # Should be able to calculate distance (existing Color method)
        distance = black.distance_to(white)
        expected_distance = (
            255**2 + 255**2 + 255**2
        ) ** 0.5  # Distance from black to white
        assert abs(distance - expected_distance) < 0.001
