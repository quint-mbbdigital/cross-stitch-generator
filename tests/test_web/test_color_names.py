"""Test descriptive color name generation for legend."""

import pytest
from fastapi.testclient import TestClient

from web.main import app
from web.utils.color_names import generate_color_name, hex_to_rgb, rgb_to_hsl

client = TestClient(app)


class TestColorNames:
    """Test descriptive color name generation for improved legend UX."""

    def test_generate_color_name_basic_colors(self):
        """Test color name generation for basic colors."""
        test_cases = [
            ("#000000", "Black"),
            ("#FFFFFF", "White"),
            ("#FF0000", "Bright Red"),
            ("#00FF00", "Bright Green"),
            ("#0000FF", "Blue"),
            ("#FFFF00", "Bright Yellow"),
        ]

        for hex_code, expected_contains in test_cases:
            result = generate_color_name(hex_code)
            assert expected_contains.lower() in result.lower(), f"Expected '{expected_contains}' in '{result}' for {hex_code}"

    def test_generate_color_name_dark_colors(self):
        """Test color name generation includes darkness modifiers."""
        dark_colors = ["#800000", "#008000", "#000080"]  # Dark red, dark green, dark blue

        for hex_code in dark_colors:
            result = generate_color_name(hex_code)
            assert "Dark" in result or "Deep" in result, f"Expected darkness modifier in '{result}' for {hex_code}"

    def test_generate_color_name_light_colors(self):
        """Test color name generation includes lightness modifiers."""
        light_colors = ["#FFB6C1", "#E0FFFF", "#F0E68C"]  # Light pink, light cyan, light yellow

        for hex_code in light_colors:
            result = generate_color_name(hex_code)
            assert any(modifier in result for modifier in ["Light", "Pale", "Very Light"]), \
                f"Expected lightness modifier in '{result}' for {hex_code}"

    def test_generate_color_name_grayscale(self):
        """Test color name generation for grayscale colors."""
        grayscale_cases = [
            ("#404040", "Gray"),
            ("#808080", "Gray"),
            ("#C0C0C0", ["Silver", "Light Gray"]),
        ]

        for hex_code, expected in grayscale_cases:
            result = generate_color_name(hex_code)
            if isinstance(expected, list):
                assert any(exp.lower() in result.lower() for exp in expected), \
                    f"Expected one of {expected} in '{result}' for {hex_code}"
            else:
                assert expected.lower() in result.lower(), f"Expected '{expected}' in '{result}' for {hex_code}"

    def test_hex_to_rgb_conversion(self):
        """Test hex to RGB conversion utility."""
        test_cases = [
            ("#FF0000", (255, 0, 0)),
            ("#00FF00", (0, 255, 0)),
            ("#0000FF", (0, 0, 255)),
            ("#FFFFFF", (255, 255, 255)),
            ("#000000", (0, 0, 0)),
        ]

        for hex_code, expected_rgb in test_cases:
            result = hex_to_rgb(hex_code)
            assert result == expected_rgb, f"Expected {expected_rgb}, got {result} for {hex_code}"

    def test_rgb_to_hsl_conversion(self):
        """Test RGB to HSL conversion for color analysis."""
        # Test a few key colors
        test_cases = [
            ((255, 0, 0), (0, 100, 50)),      # Red
            ((0, 255, 0), (120, 100, 50)),    # Green
            ((0, 0, 255), (240, 100, 50)),    # Blue
            ((255, 255, 255), (0, 0, 100)),   # White (hue irrelevant)
            ((0, 0, 0), (0, 0, 0)),          # Black (hue irrelevant)
        ]

        for rgb, expected_hsl in test_cases:
            h, s, l = rgb_to_hsl(*rgb)
            expected_h, expected_s, expected_l = expected_hsl

            # For grayscale colors, hue can be any value, so skip hue check
            if expected_s == 0:  # Grayscale
                assert abs(s - expected_s) < 1, f"Saturation mismatch for {rgb}"
                assert abs(l - expected_l) < 1, f"Lightness mismatch for {rgb}"
            else:
                assert abs(h - expected_h) < 5, f"Hue mismatch for {rgb}: expected {expected_h}, got {h}"
                assert abs(s - expected_s) < 5, f"Saturation mismatch for {rgb}"
                assert abs(l - expected_l) < 5, f"Lightness mismatch for {rgb}"

    def test_legend_shows_descriptive_names_in_frontend(self):
        """Test that legend template shows descriptive color names and hex codes."""
        response = client.get("/")
        content = response.text

        # Check that frontend shows the descriptive color name (not generic "Color N")
        assert "thread.name" in content  # Shows the generated color name
        assert "thread.hex_color" in content  # Shows hex code alongside

        # Check conditional logic for DMC vs descriptive names
        assert "thread.dmc_code && thread.dmc_code !== ''" in content
        assert "!thread.dmc_code || thread.dmc_code === ''" in content

    def test_invalid_hex_code_handling(self):
        """Test that invalid hex codes are handled gracefully."""
        invalid_codes = ["#GGGGGG", "#12345", "not-a-color", "#"]

        for invalid_code in invalid_codes:
            result = generate_color_name(invalid_code)
            assert result == "Unknown Color", f"Expected 'Unknown Color' for invalid code '{invalid_code}', got '{result}'"

    @pytest.mark.parametrize("hex_code,expected_descriptive", [
        ("#228B22", "green"),  # Should contain "green"
        ("#DC143C", "red"),    # Should contain "red"
        ("#4169E1", "blue"),   # Should contain "blue"
        ("#FFD700", "yellow"), # Should contain "yellow"
        ("#800080", "purple"), # Should contain "purple" or "magenta"
    ])
    def test_color_name_contains_base_hue(self, hex_code, expected_descriptive):
        """Test that generated names contain the expected base color."""
        result = generate_color_name(hex_code).lower()
        assert expected_descriptive in result, f"Expected '{expected_descriptive}' in '{result}' for {hex_code}"


if __name__ == "__main__":
    # Quick manual test
    test_instance = TestColorNames()

    print("Testing basic color name generation...")
    test_instance.test_generate_color_name_basic_colors()

    print("Testing dark color modifiers...")
    test_instance.test_generate_color_name_dark_colors()

    print("Testing light color modifiers...")
    test_instance.test_generate_color_name_light_colors()

    print("Testing grayscale colors...")
    test_instance.test_generate_color_name_grayscale()

    print("All color name tests passed!")