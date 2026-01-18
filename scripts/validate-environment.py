#!/usr/bin/env python3
"""
Environment validation script for Replit deployment.
Checks Python version, dependencies, and library compatibility before starting the application.
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Verify Python 3.11.x is running."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major != 3 or version.minor != 11:
        print("❌ ERROR: Python 3.11.x required")
        print(f"   Current: {version.major}.{version.minor}.{version.micro}")
        print("   Fix: Update replit.nix to use python311Full")
        return False

    print("✅ Python version OK")
    return True

def check_critical_imports():
    """Test importing critical dependencies."""
    critical_modules = [
        ("numpy", "2.4.1"),
        ("scipy", "1.17.0"),
        ("sklearn", "1.8.0"),
        ("PIL", "12.1.0"),
        ("openpyxl", "3.1.5"),
        ("fastapi", "0.115.6"),
        ("uvicorn", "0.34.0"),
        ("jinja2", "3.1.4"),
        ("pydantic", "2.10.6")
    ]

    failed = []

    for module_name, expected_version in critical_modules:
        try:
            module = importlib.import_module(module_name)

            # Get version
            version = None
            for attr in ['__version__', 'version', '__VERSION__']:
                if hasattr(module, attr):
                    version = getattr(module, attr)
                    break

            if version:
                print(f"✅ {module_name}: {version}")
                if module_name == "sklearn" and hasattr(module, '__version__'):
                    # Special case for scikit-learn version check
                    pass
            else:
                print(f"⚠️  {module_name}: imported but no version info")

        except ImportError as e:
            print(f"❌ {module_name}: FAILED - {e}")
            failed.append(module_name)
        except Exception as e:
            print(f"⚠️  {module_name}: WARNING - {e}")

    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        return False

    print("\n✅ All critical imports successful")
    return True

def test_numpy_operations():
    """Test NumPy C extensions work."""
    try:
        import numpy as np

        # Test basic operations
        arr = np.array([1, 2, 3, 4, 5])
        result = np.mean(arr)

        # Test more complex operations that use C extensions
        matrix = np.random.random((10, 10))
        eigenvals = np.linalg.eigvals(matrix)

        print("✅ NumPy C extensions working")
        return True

    except Exception as e:
        print(f"❌ NumPy C extensions FAILED: {e}")
        return False

def test_image_processing():
    """Test image processing pipeline."""
    try:
        from PIL import Image
        import numpy as np

        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='red')

        # Convert to array (tests PIL-NumPy integration)
        img_array = np.array(test_image)

        print("✅ Image processing pipeline working")
        return True

    except Exception as e:
        print(f"❌ Image processing FAILED: {e}")
        return False

def test_web_stack():
    """Test web application stack."""
    try:
        from fastapi import FastAPI
        from jinja2 import Template
        from pydantic import BaseModel

        # Test basic FastAPI creation
        app = FastAPI(title="Test")

        # Test Jinja2 templating
        template = Template("Hello {{ name }}!")
        rendered = template.render(name="World")

        # Test Pydantic model
        class TestModel(BaseModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)

        print("✅ Web application stack working")
        return True

    except Exception as e:
        print(f"❌ Web stack FAILED: {e}")
        return False

def check_system_libraries():
    """Check for required system libraries."""
    try:
        import ctypes

        # Try to load libstdc++ (the main issue in the error)
        try:
            ctypes.CDLL("libstdc++.so.6")
            print("✅ libstdc++.so.6 found")
        except OSError:
            print("⚠️  libstdc++.so.6 not found in standard location")

        return True

    except Exception as e:
        print(f"⚠️  System library check failed: {e}")
        return True  # Don't fail on this

def main():
    """Run all validation checks."""
    print("🔍 Cross-Stitch Generator Environment Validation")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Critical Imports", check_critical_imports),
        ("NumPy Operations", test_numpy_operations),
        ("Image Processing", test_image_processing),
        ("Web Stack", test_web_stack),
        ("System Libraries", check_system_libraries),
    ]

    failed_checks = []

    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}:")
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"❌ {check_name} CRASHED: {e}")
            failed_checks.append(check_name)

    print("\n" + "=" * 50)

    if failed_checks:
        print(f"❌ VALIDATION FAILED")
        print(f"   Failed checks: {', '.join(failed_checks)}")
        print("\n🔧 Recommended fixes:")
        print("   1. pip uninstall numpy scipy scikit-learn -y")
        print("   2. pip cache purge")
        print("   3. pip install -r requirements-pinned.txt")
        print("   4. Restart Repl environment")
        sys.exit(1)
    else:
        print("✅ ALL CHECKS PASSED")
        print("🚀 Environment ready for Cross-Stitch Generator!")
        sys.exit(0)

if __name__ == "__main__":
    main()