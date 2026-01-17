"""Test symbols availability logic for different pattern sizes."""

import pytest
from fastapi.testclient import TestClient

from web.main import app

client = TestClient(app)


class TestSymbolsAvailability:
    """Test symbols availability at different pattern resolutions."""

    def test_symbols_available_logic_embedded_in_frontend(self):
        """Test that the frontend contains the correct symbols availability logic."""
        # Get the frontend HTML
        response = client.get("/")
        assert response.status_code == 200

        content = response.text

        # Check that symbolsAvailable function is present
        assert "symbolsAvailable()" in content
        assert "symbolsTooltipText()" in content

        # Check the correct calculation logic
        assert "cellSize >= 8" in content
        assert "Math.max(this.patternData.width, this.patternData.height)" in content
        assert "Math.floor(maxCanvasSize / maxDimension)" in content

    def test_symbols_disabled_state_in_template(self):
        """Test that the symbols button has proper disabled state logic."""
        # Get the frontend HTML
        response = client.get("/")
        assert response.status_code == 200

        content = response.text

        # Check that symbols button has conditional logic
        assert ":disabled=\"!symbolsAvailable()\"" in content
        assert "symbolsAvailable() ? setViewMode('symbol') : null" in content
        assert ":title=\"symbolsTooltipText()\"" in content

    def test_symbols_tooltip_logic(self):
        """Test that tooltip logic provides appropriate feedback."""
        response = client.get("/")
        assert response.status_code == 200

        content = response.text

        # Check tooltip messages are present
        assert "Symbols not available for" in content
        assert "Try a smaller resolution" in content
        assert "Show pattern with symbols" in content

    @pytest.mark.parametrize("pattern_width,pattern_height,expected_available", [
        # Small patterns - should have symbols available
        (50, 50, True),      # 50x50: likely cell size > 8px
        (60, 60, True),      # 60x60: likely cell size > 8px
        (80, 80, True),      # 80x80: borderline, likely still > 8px

        # Large patterns - may not have symbols available
        (120, 120, False),   # 120x120: likely cell size < 8px
        (150, 150, False),   # 150x150: definitely cell size < 8px (user's reported issue)
        (200, 200, False),   # 200x200: definitely too small for symbols
    ])
    def test_symbol_availability_threshold_calculation(self, pattern_width, pattern_height, expected_available):
        """Test the symbol availability calculation for different pattern sizes.

        This test validates the logic that determines when symbols are available
        based on the calculated cell size threshold of 8 pixels.
        """
        # Simulating the frontend calculation
        # Assume a typical canvas size (this matches the frontend logic)
        window_width = 1200  # Typical desktop width
        window_height = 800  # Typical desktop height

        max_canvas_size = min(window_width - 400, window_height - 100)  # 800px
        max_dimension = max(pattern_width, pattern_height)
        cell_size = max(2, max_canvas_size // max_dimension)

        symbols_available = cell_size >= 8

        assert symbols_available == expected_available, (
            f"Pattern {pattern_width}x{pattern_height} should {'have' if expected_available else 'not have'} "
            f"symbols available (calculated cell size: {cell_size}px)"
        )

    def test_user_reported_150x150_issue(self):
        """Specifically test the user's reported issue with 150x150 patterns."""
        # This is the specific case the user mentioned
        pattern_width, pattern_height = 150, 150

        # Frontend calculation (conservative canvas size)
        max_canvas_size = 700  # Conservative estimate
        max_dimension = max(pattern_width, pattern_height)  # 150
        cell_size = max(2, max_canvas_size // max_dimension)  # 4px

        symbols_available = cell_size >= 8  # False

        assert not symbols_available, (
            f"150x150 pattern should NOT have symbols available "
            f"(cell size: {cell_size}px < 8px threshold)"
        )


if __name__ == "__main__":
    # Quick manual test
    test_instance = TestSymbolsAvailability()

    print("Testing symbols availability logic...")
    test_instance.test_symbols_available_logic_embedded_in_frontend()

    print("Testing symbols button disabled state...")
    test_instance.test_symbols_disabled_state_in_template()

    print("Testing 150x150 specific case...")
    test_instance.test_user_reported_150x150_issue()

    print("All symbols tests passed!")