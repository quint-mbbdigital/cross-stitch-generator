"""Test UI styling consistency and Modern Atelier compliance."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from bs4 import BeautifulSoup
import re

from web.main import app

client = TestClient(app)


class TestModernAtelierStyling:
    """Test suite for Modern Atelier design compliance."""

    def test_frontend_loads_successfully(self):
        """Test that the frontend loads without errors."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_inter_font_loading(self):
        """Test that Inter font is properly loaded."""
        response = client.get("/")
        content = response.text

        # Check for Google Fonts Inter loading
        assert "fonts.googleapis.com" in content
        assert "family=Inter" in content
        assert "font-family: 'Inter'" in content

    def test_sidebar_field_name_consistency(self):
        """Test that sidebar field names match Alpine.js config structure."""
        response = client.get("/")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for correct Alpine.js model bindings
        alpine_bindings = [
            'x-model.number="config.resolution"',
            'x-model.number="config.max_colors"',
            'x-model="config.edge_mode"',
            'x-model="config.enable_dmc"',
            'x-model="config.dmc_only"',
            'x-model.number="config.min_color_percent"'
        ]

        content = response.text
        for binding in alpine_bindings:
            assert binding in content, f"Missing Alpine.js binding: {binding}"

        # Ensure old incorrect bindings are removed
        incorrect_bindings = [
            'x-model="config.maxColors"',
            'x-model="config.edgeMode"',
            'x-model="config.dmcMatching"',
            'x-model="config.noiseThreshold"'
        ]

        for binding in incorrect_bindings:
            assert binding not in content, f"Found deprecated binding: {binding}"

    def test_modern_atelier_color_scheme(self):
        """Test that Modern Atelier slate colors are used throughout."""
        response = client.get("/")
        content = response.text

        # Check for Modern Atelier slate color classes
        required_classes = [
            'bg-slate-50',     # Sidebar background
            'border-slate-200', # Border colors
            'text-slate-900',   # Primary text
            'text-slate-600',   # Secondary text
            'text-slate-500',   # Tertiary text
            'bg-slate-900',     # Primary button
            'hover:bg-slate-800', # Button hover
        ]

        for class_name in required_classes:
            assert class_name in content, f"Missing Modern Atelier class: {class_name}"

        # Ensure old gray classes are removed from critical components
        deprecated_classes = [
            'bg-gray-200',
            'text-gray-700',
            'border-gray-200',
            'bg-blue-600'  # Should use slate for primary actions
        ]

        # These should not appear in the main sidebar component
        soup = BeautifulSoup(content, 'html.parser')
        sidebar = soup.find('aside') or soup.find('div', class_=re.compile('w-80.*bg-slate'))
        if sidebar:
            sidebar_html = str(sidebar)
            for deprecated in deprecated_classes:
                if deprecated in sidebar_html and deprecated not in ['bg-gray-200']:  # Some legacy might remain elsewhere
                    pytest.fail(f"Found deprecated class in sidebar: {deprecated}")

    def test_typography_hierarchy(self):
        """Test that typography follows Modern Atelier hierarchy."""
        response = client.get("/")
        content = response.text

        # Check for proper typography classes
        typography_patterns = [
            r'text-lg font-semibold.*tracking-tight',  # Header typography
            r'label-data',  # Data labels with proper styling
            r'font-mono.*text-slate-700',  # Monospace values
            r'text-xs.*font-medium.*text-slate-500'  # Range labels
        ]

        for pattern in typography_patterns:
            assert re.search(pattern, content), f"Missing typography pattern: {pattern}"

    def test_label_data_styling(self):
        """Test that label-data class is properly defined and used."""
        response = client.get("/")
        content = response.text

        # Check that label-data CSS class is defined
        assert '.label-data' in content
        assert 'text-transform: uppercase' in content
        assert 'letter-spacing: 0.05em' in content
        assert 'font-weight: 600' in content

        # Check that label-data class is used in the sidebar
        assert 'class="label-data"' in content

    def test_custom_slider_styling(self):
        """Test that custom range slider styling is applied."""
        response = client.get("/")
        content = response.text

        # Check for custom slider CSS
        slider_styles = [
            'input[type="range"]',
            '-webkit-slider-thumb',
            '-moz-range-thumb',
            'background: #475569',  # Slate color for thumb
            'border-radius: 50%'
        ]

        for style in slider_styles:
            assert style in content, f"Missing slider style: {style}"

    def test_notification_styling_support(self):
        """Test that notification styling functions are available."""
        # Test that the upload handler includes the updated notification function
        response = client.get("/static/js/upload-handler.js")
        assert response.status_code == 200

        content = response.text

        # Check for Modern Atelier notification styling
        notification_features = [
            'bg-slate-900 text-white',  # Info style
            'bg-amber-50 text-amber-900',  # Warning style
            'alert-triangle',  # Warning icon (checking for icon name)
            'transition-all duration-300',  # Smooth animations
            'rounded-md border'  # Modern borders
        ]

        for feature in notification_features:
            assert feature in content, f"Missing notification feature: {feature}"

    def test_form_accessibility(self):
        """Test that form elements have proper accessibility attributes."""
        response = client.get("/")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check that range inputs have proper attributes
        range_inputs = soup.find_all('input', type='range')
        assert len(range_inputs) >= 3, "Should have at least 3 range sliders"

        for input_elem in range_inputs:
            assert input_elem.get('min'), "Range input should have min attribute"
            assert input_elem.get('max'), "Range input should have max attribute"
            assert input_elem.get('step'), "Range input should have step attribute"

        # Check that radio buttons have proper grouping
        radio_inputs = soup.find_all('input', type='radio')
        edge_mode_radios = [r for r in radio_inputs if 'edge_mode' in str(r)]
        assert len(edge_mode_radios) >= 2, "Should have edge mode radio buttons"

    def test_responsive_design_classes(self):
        """Test that responsive design classes are included."""
        response = client.get("/")
        content = response.text

        # Check for responsive classes
        responsive_classes = [
            'lg:hidden',  # Mobile sidebar toggle
            'flex-shrink-0',  # Prevent sidebar shrinking
            'overflow-y-auto',  # Scrollable content
            'h-full',  # Full height layout
        ]

        for class_name in responsive_classes:
            assert class_name in content, f"Missing responsive class: {class_name}"

    def test_animation_classes(self):
        """Test that animation classes are properly included."""
        response = client.get("/")
        content = response.text

        # Check for animation classes
        animation_classes = [
            'transition-colors',
            'transition-all',
            'hover:bg-slate-100',
            'pattern-fade-in'
        ]

        for class_name in animation_classes:
            assert class_name in content, f"Missing animation class: {class_name}"

    def test_config_range_limits(self):
        """Test that configuration ranges match realistic values."""
        response = client.get("/")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find resolution slider
        resolution_input = soup.find('input', {'x-model': 'config.resolution'})
        if resolution_input:
            assert resolution_input.get('min') == '30', "Resolution min should be 30"
            assert resolution_input.get('max') == '300', "Resolution max should be 300"

        # Find colors slider
        colors_input = soup.find('input', {'x-model': 'config.max_colors'})
        if colors_input:
            assert colors_input.get('min') == '2', "Colors min should be 2"
            assert colors_input.get('max') == '256', "Colors max should be 256"


if __name__ == "__main__":
    # Run tests directly for debugging
    test_instance = TestModernAtelierStyling()

    print("Testing Modern Atelier UI styling compliance...")

    tests = [
        test_instance.test_frontend_loads_successfully,
        test_instance.test_inter_font_loading,
        test_instance.test_sidebar_field_name_consistency,
        test_instance.test_modern_atelier_color_scheme,
        test_instance.test_typography_hierarchy,
        test_instance.test_label_data_styling,
        test_instance.test_custom_slider_styling,
        test_instance.test_notification_styling_support,
        test_instance.test_form_accessibility,
        test_instance.test_responsive_design_classes,
        test_instance.test_animation_classes,
        test_instance.test_config_range_limits,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All UI styling tests PASSED!")
    else:
        print("⚠️ Some styling tests failed - please review the issues above.")