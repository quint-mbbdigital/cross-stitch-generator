"""Test view mode preservation during pattern regeneration."""

import pytest
from fastapi.testclient import TestClient

from web.main import app

client = TestClient(app)


class TestViewModePreservation:
    """Test that view modes (symbols/colors) are preserved during regeneration."""

    def test_regeneration_preserves_view_mode_logic_in_frontend(self):
        """Test that the frontend has logic to preserve view mode after regeneration."""
        # Get the frontend HTML
        response = client.get("/")
        assert response.status_code == 200

        content = response.text

        # Check that after setting patternData, we dispatch render-pattern with current viewMode
        assert "this.$dispatch('render-pattern', { mode: this.viewMode })" in content

        # Verify this happens after pattern data is set in regeneratePattern
        pattern_data_index = content.find("this.patternData = patternData;")
        render_dispatch_index = content.find("this.$dispatch('render-pattern', { mode: this.viewMode })")

        assert pattern_data_index != -1, "Pattern data assignment not found"
        assert render_dispatch_index != -1, "Render pattern dispatch not found"
        assert render_dispatch_index > pattern_data_index, "Render dispatch should come after pattern data assignment"

    def test_setViewMode_function_dispatches_render_pattern(self):
        """Test that setViewMode function properly dispatches render-pattern events."""
        response = client.get("/")
        content = response.text

        # Check setViewMode function exists and dispatches render-pattern
        assert "setViewMode(mode)" in content
        assert "this.viewMode = mode;" in content
        assert "this.$dispatch('render-pattern', { mode });" in content

    def test_symbols_button_calls_setViewMode_when_available(self):
        """Test that symbols button calls setViewMode when symbols are available."""
        response = client.get("/")
        content = response.text

        # Check that symbols button calls setViewMode when available
        assert "symbolsAvailable() ? setViewMode('symbol') : null" in content

    def test_colors_button_calls_setViewMode(self):
        """Test that colors button always calls setViewMode."""
        response = client.get("/")
        content = response.text

        # Check that colors button calls setViewMode
        assert "setViewMode('stitch')" in content

    def test_view_mode_state_management(self):
        """Test that viewMode state is properly managed in Alpine.js."""
        response = client.get("/")
        content = response.text

        # Check that viewMode is initialized
        assert "viewMode: 'stitch'" in content  # Default to stitch (colors)

        # Check that viewMode affects button styling
        assert "viewMode === 'stitch'" in content
        assert "viewMode === 'symbol'" in content

    def test_regeneration_comment_explains_preservation(self):
        """Test that code has helpful comment explaining view mode preservation."""
        response = client.get("/")
        content = response.text

        # Check for explanatory comment
        assert "// Preserve current view mode (symbols/colors) after regeneration" in content

    def test_magic_moment_and_render_pattern_both_dispatched(self):
        """Test that both magic-moment and render-pattern events are dispatched during regeneration."""
        response = client.get("/")
        content = response.text

        # Both events should be dispatched in regeneratePattern
        assert "this.$dispatch('magic-moment', { data: patternData });" in content
        assert "this.$dispatch('render-pattern', { mode: this.viewMode });" in content

        # Verify they're in the same function
        regenerate_start = content.find("async regeneratePattern()")
        next_function_start = content.find("init()", regenerate_start)

        magic_moment_index = content.find("this.$dispatch('magic-moment'", regenerate_start)
        render_pattern_index = content.find("this.$dispatch('render-pattern'", regenerate_start)

        assert regenerate_start < magic_moment_index < next_function_start
        assert regenerate_start < render_pattern_index < next_function_start


if __name__ == "__main__":
    # Quick manual test
    test_instance = TestViewModePreservation()

    print("Testing view mode preservation logic...")
    test_instance.test_regeneration_preserves_view_mode_logic_in_frontend()

    print("Testing setViewMode function...")
    test_instance.test_setViewMode_function_dispatches_render_pattern()

    print("Testing button interactions...")
    test_instance.test_symbols_button_calls_setViewMode_when_available()
    test_instance.test_colors_button_calls_setViewMode()

    print("Testing state management...")
    test_instance.test_view_mode_state_management()

    print("All view mode preservation tests passed!")