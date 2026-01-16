#!/usr/bin/env python3
"""
Cross-Stitch Pattern Generator

A command-line tool for converting images into cross-stitch patterns.
Generates Excel files with multiple resolution tabs where each cell
represents one stitch with background colors matching the image.

Usage:
    python cross_stitch_generator.py generate input.jpg output.xlsx
    python cross_stitch_generator.py info input.jpg

For detailed help:
    python cross_stitch_generator.py --help
"""

import sys
from pathlib import Path

# Add src directory to path so we can import the package
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from cross_stitch.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
