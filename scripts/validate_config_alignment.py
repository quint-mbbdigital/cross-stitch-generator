#!/usr/bin/env python3
"""Development utility to validate frontend/backend config alignment.

Run this script during development to quickly check for configuration
mismatches between the Alpine.js frontend and Pydantic backend.
"""

import re
import sys
from pathlib import Path
from typing import Dict, Set, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from web.models.requests import PatternConfig, QuantizationMethod, EdgeMode, TransparencyMode


class ConfigValidator:
    """Validates frontend/backend configuration alignment."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.frontend_template_path = project_root / "web/templates/base.html"
        self.sidebar_template_path = project_root / "web/templates/components/sidebar.html"

    def validate_all(self) -> bool:
        """Run all validation checks. Returns True if all checks pass."""
        print("🔍 Validating frontend/backend configuration alignment...\n")

        self._validate_template_files_exist()
        self._validate_field_names()
        self._validate_enum_values()
        self._validate_default_values()
        self._validate_frontend_cleaning_function()

        self._print_results()
        return len(self.errors) == 0

    def _validate_template_files_exist(self):
        """Check that required template files exist."""
        if not self.frontend_template_path.exists():
            self.errors.append(f"Frontend template not found: {self.frontend_template_path}")
        if not self.sidebar_template_path.exists():
            self.errors.append(f"Sidebar template not found: {self.sidebar_template_path}")

    def _validate_field_names(self):
        """Validate that frontend config fields match backend model."""
        print("📋 Checking field name alignment...")

        backend_fields = set(PatternConfig.model_fields.keys())
        frontend_fields = self._extract_frontend_config_fields()

        if not frontend_fields:
            self.errors.append("Could not extract frontend config fields from templates")
            return

        missing_from_frontend = backend_fields - frontend_fields
        extra_in_frontend = frontend_fields - backend_fields

        if missing_from_frontend:
            self.errors.append(f"Backend fields missing from frontend: {missing_from_frontend}")

        if extra_in_frontend:
            self.warnings.append(f"Extra frontend fields (should be filtered): {extra_in_frontend}")

        print(f"   ✅ Backend fields: {sorted(backend_fields)}")
        print(f"   ✅ Frontend fields: {sorted(frontend_fields)}")

    def _validate_enum_values(self):
        """Validate that enum values match between frontend and backend."""
        print("\n🔧 Checking enum value alignment...")

        # Quantization methods
        frontend_quantization = self._extract_frontend_enum_values("quantization")
        backend_quantization = {e.value for e in QuantizationMethod}

        if frontend_quantization != backend_quantization:
            self.errors.append(
                f"Quantization enum mismatch:\n"
                f"  Frontend: {frontend_quantization}\n"
                f"  Backend: {backend_quantization}"
            )
        else:
            print(f"   ✅ Quantization values match: {backend_quantization}")

        # Edge modes
        frontend_edge_mode = self._extract_frontend_enum_values("edge_mode")
        backend_edge_mode = {e.value for e in EdgeMode}

        if frontend_edge_mode != backend_edge_mode:
            self.errors.append(
                f"Edge mode enum mismatch:\n"
                f"  Frontend: {frontend_edge_mode}\n"
                f"  Backend: {backend_edge_mode}"
            )
        else:
            print(f"   ✅ Edge mode values match: {backend_edge_mode}")

        # Transparency modes (check if any exist in frontend)
        frontend_transparency = self._extract_frontend_enum_values("transparency")
        backend_transparency = {e.value for e in TransparencyMode}

        if frontend_transparency and frontend_transparency != backend_transparency:
            self.errors.append(
                f"Transparency enum mismatch:\n"
                f"  Frontend: {frontend_transparency}\n"
                f"  Backend: {backend_transparency}"
            )
        elif frontend_transparency:
            print(f"   ✅ Transparency values match: {backend_transparency}")
        else:
            print(f"   ⚠️ No transparency radio buttons found in frontend")

    def _validate_default_values(self):
        """Validate that default values match."""
        print("\n📊 Checking default value alignment...")

        default_config = PatternConfig()
        frontend_defaults = self._extract_frontend_default_values()

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
                if frontend_value != backend_value:
                    self.errors.append(
                        f"Default value mismatch for {field}:\n"
                        f"  Frontend: {frontend_value} (type: {type(frontend_value)})\n"
                        f"  Backend: {backend_value} (type: {type(backend_value)})"
                    )
                else:
                    print(f"   ✅ {field}: {backend_value}")
            else:
                self.warnings.append(f"Could not extract frontend default for: {field}")

    def _validate_frontend_cleaning_function(self):
        """Check that frontend has a config cleaning function."""
        print("\n🧹 Checking frontend config cleaning...")

        base_content = self.frontend_template_path.read_text()

        if "getCleanConfig" not in base_content:
            self.errors.append("getCleanConfig function not found in frontend")
        else:
            print("   ✅ getCleanConfig function exists")

        # Check that it filters to the right fields
        backend_fields = set(PatternConfig.model_fields.keys())
        clean_config_match = re.search(r'getCleanConfig\(\)\s*{([^}]+)}', base_content, re.DOTALL)

        if clean_config_match:
            clean_config_text = clean_config_match.group(1)
            cleaned_fields = set(re.findall(r'(\w+):', clean_config_text))

            if cleaned_fields != backend_fields:
                self.errors.append(
                    f"getCleanConfig doesn't return exactly the backend fields:\n"
                    f"  Cleaned: {cleaned_fields}\n"
                    f"  Expected: {backend_fields}"
                )
            else:
                print(f"   ✅ getCleanConfig returns correct fields: {sorted(backend_fields)}")

    def _extract_frontend_config_fields(self) -> Set[str]:
        """Extract config field names from frontend templates."""
        try:
            base_content = self.frontend_template_path.read_text()
            config_match = re.search(r'config:\s*{([^}]+)}', base_content, re.DOTALL)

            if config_match:
                config_text = config_match.group(1)
                field_pattern = r'(\w+):\s*[^,\n}]+'
                return set(re.findall(field_pattern, config_text))
        except Exception as e:
            self.errors.append(f"Error extracting frontend fields: {str(e)}")

        return set()

    def _extract_frontend_enum_values(self, field_name: str) -> Set[str]:
        """Extract enum values from frontend radio buttons."""
        try:
            sidebar_content = self.sidebar_template_path.read_text()
            pattern = rf'x-model="config\.{field_name}"\s+value="([^"]+)"'
            return set(re.findall(pattern, sidebar_content))
        except Exception as e:
            self.warnings.append(f"Error extracting {field_name} enum values: {str(e)}")
            return set()

    def _extract_frontend_default_values(self) -> Dict[str, Any]:
        """Extract default values from frontend config object."""
        try:
            base_content = self.frontend_template_path.read_text()
            config_match = re.search(r'config:\s*({[^}]+})', base_content, re.DOTALL)

            if not config_match:
                return {}

            config_text = config_match.group(1)
            defaults = {}

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

                    if field in ['resolution', 'max_colors']:
                        defaults[field] = int(value)
                    elif field == 'min_color_percent':
                        defaults[field] = float(value)
                    elif field in ['enable_dmc', 'dmc_only']:
                        defaults[field] = value.lower() == 'true'
                    else:
                        defaults[field] = value

            return defaults
        except Exception as e:
            self.warnings.append(f"Error extracting frontend defaults: {str(e)}")
            return {}

    def _print_results(self):
        """Print validation results."""
        print("\n" + "="*60)

        if self.errors:
            print("❌ VALIDATION FAILED")
            print(f"\n🚨 {len(self.errors)} Error(s):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        else:
            print("✅ VALIDATION PASSED")

        if self.warnings:
            print(f"\n⚠️ {len(self.warnings)} Warning(s):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")

        print("\n" + "="*60)


def main():
    """Main entry point."""
    validator = ConfigValidator()
    success = validator.validate_all()

    if success:
        print("🎉 All configuration alignment checks passed!")
        sys.exit(0)
    else:
        print("💥 Configuration alignment validation failed!")
        print("\nPlease fix the errors above and run this script again.")
        sys.exit(1)


if __name__ == "__main__":
    main()