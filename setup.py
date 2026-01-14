"""Setup configuration for Cross-Stitch Pattern Generator."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements from requirements.txt
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []

if requirements_path.exists():
    with requirements_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                # Extract just the package name and version
                package = line.split('#')[0].strip()
                if package:
                    requirements.append(package)

setup(
    name="cross-stitch-generator",
    version="0.1.0",
    description="Generate cross-stitch patterns from images as Excel files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cross-Stitch Generator",
    python_requires=">=3.11",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cross-stitch=cross_stitch.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Artistic Software",
    ],
    keywords="cross-stitch, pattern, embroidery, excel, image-processing",
    project_urls={
        "Source": "https://github.com/user/cross-stitch-generator",
        "Bug Reports": "https://github.com/user/cross-stitch-generator/issues",
    },
)