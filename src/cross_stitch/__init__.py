"""Cross-Stitch Pattern Generator

A Python application that converts image files into Excel-based cross-stitch patterns
with multiple resolution tabs.
"""

from .core import PatternGenerator
from .models import GeneratorConfig

__version__ = "0.1.0"
__all__ = ["PatternGenerator", "GeneratorConfig"]
