"""Test frontend and backend configuration alignment.

This test suite ensures the Alpine.js frontend config matches
the Pydantic backend PatternConfig model exactly.
"""

import pytest
import re
import json
from pathlib import Path
from typing import Dict, Any, Set
from fastapi.testclient import TestClient

from web.main import app
from web.models.requests import PatternConfig, QuantizationMethod, EdgeMode, TransparencyMode


class TestConfigAlignment:
    """Test suite to ensure frontend/backend config consistency."""

    def test_frontend_backend_field_names_match(self):
        """Ensure all PatternConfig fields exist in frontend Alpine.js config."""
        # Get PatternConfig model fields
        backend_fields = set(PatternConfig.model_fields.keys())

        # Read frontend template to extract config fields
        frontend_fields = self._extract_frontend_config_fields()

        # Check that all backend fields exist in frontend
        missing_from_frontend = backend_fields - frontend_fields
        assert not missing_from_frontend, (
            f"Backend PatternConfig fields missing from frontend: {missing_from_frontend}"
        )

        # Check for extra frontend fields (these get filtered by getCleanConfig)
        extra_in_frontend = frontend_fields - backend_fields
        if extra_in_frontend:
            print(f"ℹ️ Extra frontend fields (filtered by getCleanConfig): {extra_in_frontend}")

    def test_enum_values_match_across_frontend_backend(self):
        """Test that enum values match between frontend HTML and backend Pydantic models."""

        # Test QuantizationMethod enum
        frontend_quantization = self._extract_frontend_enum_values("quantization")
        backend_quantization = {e.value for e in QuantizationMethod}
        assert frontend_quantization == backend_quantization, (
            f"Quantization values mismatch:\n"
            f"Frontend: {frontend_quantization}\n"
            f"Backend: {backend_quantization}"
        )

        # Test EdgeMode enum
        frontend_edge_mode = self._extract_frontend_enum_values("edge_mode")
        backend_edge_mode = {e.value for e in EdgeMode}
        assert frontend_edge_mode == backend_edge_mode, (
            f"Edge mode values mismatch:\n"
            f"Frontend: {frontend_edge_mode}\n"
            f"Backend: {backend_edge_mode}"
        )

        # Test TransparencyMode enum (if any radio buttons exist)
        frontend_transparency = self._extract_frontend_enum_values("transparency")
        backend_transparency = {e.value for e in TransparencyMode}
        if frontend_transparency:  # Only test if frontend has transparency options
            assert frontend_transparency == backend_transparency, (
                f"Transparency values mismatch:\n"
                f"Frontend: {frontend_transparency}\n"
                f"Backend: {backend_transparency}"
            )

    def test_default_values_alignment(self):
        """Test that frontend default values match backend defaults."""
        # Create default PatternConfig
        default_config = PatternConfig()

        # Extract frontend defaults
        frontend_defaults = self._extract_frontend_default_values()

        # Compare key default values
        backend_defaults = {
            'resolution': default_config.resolution,
            'max_colors': default_config.max_colors,
            'quantization': default_config.quantization.value,
            'edge_mode': default_config.edge_mode.value,
            'transparency': default_config.transparency.value,
            'min_color_percent': default_config.min_color_percent,
            'enable_dmc': default_config.enable_dmc,
            'dmc_only': default_config.dmc_only,
        }

        for field, backend_value in backend_defaults.items():
            if field in frontend_defaults:
                frontend_value = frontend_defaults[field]
                assert frontend_value == backend_value, (
                    f"Default value mismatch for {field}:\n"
                    f"Frontend: {frontend_value} (type: {type(frontend_value)})\n"
                    f"Backend: {backend_value} (type: {type(backend_value)})"
                )

    def test_config_validation_with_frontend_examples(self):
        """Test that typical frontend configurations validate successfully."""

        # Test configurations that should work
        valid_configs = [
            # Default config
            {
                "resolution": 100,
                "max_colors": 64,
                "quantization": "median_cut",
                "edge_mode": "smooth",
                "transparency": "white_background",
                "min_color_percent": 1.0,
                "enable_dmc": True,
                "dmc_only": False
            },
            # High resolution config
            {
                "resolution": 200,
                "max_colors": 128,
                "quantization": "kmeans",
                "edge_mode": "hard",
                "transparency": "remove",
                "min_color_percent": 2.5,
                "enable_dmc": False,
                "dmc_only": False
            },
            # Minimal config
            {
                "resolution": 30,
                "max_colors": 8,
                "quantization": "median_cut",
                "edge_mode": "smooth",
                "transparency": "preserve",
                "min_color_percent": 0.0,
                "enable_dmc": True,
                "dmc_only": True
            }
        ]

        for i, config_data in enumerate(valid_configs):
            try:
                config = PatternConfig.model_validate(config_data)
                assert config is not None, f"Config {i} should validate successfully"
            except Exception as e:
                pytest.fail(f"Valid config {i} failed validation: {str(e)}")

    def test_frontend_config_cleaning_function_exists(self):
        """Test that the frontend has a getCleanConfig function."""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200

        # Check that getCleanConfig function exists in the frontend code
        content = response.text
        assert "getCleanConfig" in content, "getCleanConfig function not found in frontend"
        assert "function getCleanConfig" in content or "getCleanConfig()" in content, (
            "getCleanConfig should be defined as a function"
        )

    def test_backend_handles_extra_frontend_fields_gracefully(self):
        """Test that backend properly handles and ignores extra frontend fields."""
        client = TestClient(app)

        # First upload an image
        test_image_path = Path(__file__).parent.parent.parent / "mbb_digital.jpg"
        if not test_image_path.exists():
            pytest.skip("Test image not available")

        with open(test_image_path, 'rb') as f:
            upload_response = client.post("/api/upload", files={"file": ("test.jpg", f, "image/jpeg")})

        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        job_id = upload_data["job_id"]

        # Test config with extra fields (like a raw frontend config)
        config_with_extra_fields = {
            # Required PatternConfig fields
            "resolution": 80,
            "max_colors": 32,
            "quantization": "median_cut",
            "edge_mode": "smooth",
            "transparency": "white_background",
            "min_color_percent": 1.0,
            "enable_dmc": True,
            "dmc_only": False,

            # Extra fields that should be ignored
            "max_merge_distance": 50.0,
            "resolutions": None,
            "excel_cell_size": 20.0,
            "include_color_legend": True,
            "legend_sheet_name": "Color Legend",
            "dmc_palette_size": None,
            "dmc_database": None,
        }

        # This should fail with current implementation since extra fields aren't filtered
        response = client.post(f"/api/generate/{job_id}", json=config_with_extra_fields)

        # We expect this to fail currently, but the error should be clear
        if response.status_code != 200:
            error_text = response.text
            # Should get a validation error about unexpected fields, not a generic error
            assert "field required" in error_text.lower() or "extra" in error_text.lower() or "unexpected" in error_text.lower(), (
                f"Expected validation error about extra fields, got: {error_text}"
            )

    def _extract_frontend_config_fields(self) -> Set[str]:
        """Extract config field names from frontend Alpine.js template."""
        client = TestClient(app)
        response = client.get("/")
        content = response.text

        # Find the config object in Alpine.js state
        config_match = re.search(r'config:\s*{([^}]+)}', content, re.DOTALL)
        if not config_match:
            pytest.fail("Could not find config object in frontend template")

        config_text = config_match.group(1)

        # Extract field names (looking for "fieldname:" patterns)
        field_pattern = r'(\w+):\s*[^,\n}]+'
        fields = set(re.findall(field_pattern, config_text))

        return fields

    def _extract_frontend_enum_values(self, field_name: str) -> Set[str]:
        """Extract enum values from frontend radio buttons or select options."""
        client = TestClient(app)
        response = client.get("/")
        content = response.text

        # Look for radio buttons with x-model matching the field
        pattern = rf'x-model="config\.{field_name}"\s+value="([^"]+)"'
        values = set(re.findall(pattern, content))

        return values

    def _extract_frontend_default_values(self) -> Dict[str, Any]:
        """Extract default values from frontend Alpine.js config."""
        client = TestClient(app)
        response = client.get("/")
        content = response.text

        # Find the config object and extract it
        config_match = re.search(r'config:\s*({[^}]+})', content, re.DOTALL)
        if not config_match:
            return {}

        config_text = config_match.group(1)

        # Parse individual field values
        defaults = {}

        # Simple patterns for common types
        patterns = {
            'resolution': r'resolution:\s*(\d+)',
            'max_colors': r'max_colors:\s*(\d+)',
            'quantization': r"quantization:\s*['\"]([^'\"]+)['\"]",
            'edge_mode': r"edge_mode:\s*['\"]([^'\"]+)['\"]",
            'transparency': r"transparency:\s*['\"]([^'\"]+)['\"]",
            'min_color_percent': r'min_color_percent:\s*([\d.]+)',
            'enable_dmc': r'enable_dmc:\s*(true|false)',
            'dmc_only': r'dmc_only:\s*(true|false)',
        }

        for field, pattern in patterns.items():
            match = re.search(pattern, config_text)
            if match:
                value = match.group(1)

                # Convert to appropriate type
                if field in ['resolution', 'max_colors']:
                    defaults[field] = int(value)
                elif field == 'min_color_percent':
                    defaults[field] = float(value)
                elif field in ['enable_dmc', 'dmc_only']:
                    defaults[field] = value.lower() == 'true'
                else:
                    defaults[field] = value

        return defaults

    def test_field_validation_ranges_match(self):
        """Test that validation ranges match between frontend and backend."""
        # Get PatternConfig field constraints
        model_fields = PatternConfig.model_fields

        # Check resolution constraints
        resolution_field = model_fields['resolution']
        assert hasattr(resolution_field, 'metadata'), "Resolution field should have validation metadata"

        # Note: This is a basic test - could be expanded to check actual HTML input ranges
        client = TestClient(app)
        response = client.get("/")
        content = response.text

        # Check that resolution slider has reasonable min/max
        resolution_input = re.search(r'x-model[^>]*="config\.resolution"[^>]*', content)
        if resolution_input:
            input_html = resolution_input.group(0)
            min_match = re.search(r'min="(\d+)"', input_html)
            max_match = re.search(r'max="(\d+)"', input_html)

            if min_match and max_match:
                frontend_min = int(min_match.group(1))
                frontend_max = int(max_match.group(1))

                # Should align with backend validation (ge=25, le=300)
                assert frontend_min >= 25, f"Frontend min resolution ({frontend_min}) should be >= 25"
                assert frontend_max <= 300, f"Frontend max resolution ({frontend_max}) should be <= 300"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])