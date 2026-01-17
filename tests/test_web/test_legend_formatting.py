"""Test legend formatting and duplicate color elimination."""

import pytest
from fastapi.testclient import TestClient

from web.main import app

client = TestClient(app)


class TestLegendFormatting:
    """Test that legend shows clean, non-duplicated color information."""

    def test_legend_template_has_conditional_display_logic(self):
        """Test that legend template has logic to avoid duplication."""
        response = client.get("/")
        assert response.status_code == 200

        content = response.text

        # Check for conditional templates to handle DMC vs generic colors
        assert "x-if=\"thread.dmc_code && thread.dmc_code !== ''\""  in content
        assert "x-if=\"!thread.dmc_code || thread.dmc_code === ''\""  in content

        # Ensure we don't have the old duplicative logic
        assert "thread.dmc_code || ('Color '" not in content  # Old problematic pattern

    def test_legend_shows_dmc_code_and_name_when_available(self):
        """Test that when DMC code is available, both code and name are shown."""
        response = client.get("/")
        content = response.text

        # Check for DMC display logic
        assert "x-text=\"thread.dmc_code\"" in content
        assert "x-text=\"thread.name || ''\"" in content

    def test_legend_shows_only_color_n_when_no_dmc(self):
        """Test that when no DMC code, only 'Color N' is shown."""
        response = client.get("/")
        content = response.text

        # Check for generic color display logic
        assert "x-text=\"'Color ' + (index + 1)\"" in content

    def test_legend_structure_contains_thread_info(self):
        """Test that legend has the expected structure for thread information."""
        response = client.get("/")
        content = response.text

        # Check for essential legend elements
        assert "Thread Legend" in content
        assert "patternData?.threads" in content
        assert "thread.hex_color" in content
        assert "thread.stitch_count" in content
        assert "thread.percentage" in content

    def test_legend_empty_state_messaging(self):
        """Test that legend shows helpful message when no pattern data."""
        response = client.get("/")
        content = response.text

        # Check empty state
        assert "Generate a pattern to see the thread legend" in content
        assert "x-show=\"!patternData\"" in content

    def test_legend_summary_information(self):
        """Test that legend header shows summary information."""
        response = client.get("/")
        content = response.text

        # Check summary info in header
        assert "patternData?.threads?.length" in content
        assert "patternData?.total_stitches" in content
        assert "colors •" in content
        assert "stitches" in content

    @pytest.mark.parametrize("expected_element", [
        "Color Swatch",  # Color display
        "w-8 h-8 rounded-md",  # Swatch styling
        "backgroundColor: thread.hex_color",  # Color binding
        "stitches",  # Stitch count label
        "%",  # Percentage display
    ])
    def test_legend_visual_elements(self, expected_element):
        """Test that legend contains expected visual and data elements."""
        response = client.get("/")
        content = response.text

        # Check for essential visual elements
        if "Color Swatch" in expected_element:
            # This is in a comment, check for color swatch div instead
            assert "w-8 h-8 rounded-md" in content
        else:
            assert expected_element in content


if __name__ == "__main__":
    # Quick manual test
    test_instance = TestLegendFormatting()

    print("Testing legend conditional display logic...")
    test_instance.test_legend_template_has_conditional_display_logic()

    print("Testing DMC code display...")
    test_instance.test_legend_shows_dmc_code_and_name_when_available()

    print("Testing generic color display...")
    test_instance.test_legend_shows_only_color_n_when_no_dmc()

    print("Testing legend structure...")
    test_instance.test_legend_structure_contains_thread_info()

    print("All legend formatting tests passed!")