"""Pattern models for cross-stitch generation."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
import numpy as np

from .color_palette import ColorPalette


@dataclass
class CrossStitchPattern:
    """Represents a cross-stitch pattern at a specific resolution."""

    width: int
    height: int
    colors: np.ndarray  # 2D array of color indices into the palette
    palette: ColorPalette
    resolution_name: str

    def __post_init__(self) -> None:
        """Validate pattern data."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"Invalid dimensions: {self.width}x{self.height}")

        if self.colors.shape != (self.height, self.width):
            raise ValueError(
                f"Color array shape {self.colors.shape} doesn't match dimensions "
                f"({self.height}, {self.width})"
            )

        # Check that all color indices are valid
        max_index = len(self.palette) - 1
        if np.any(self.colors > max_index) or np.any(self.colors < 0):
            raise ValueError(f"Color indices must be between 0 and {max_index}")

    @property
    def total_stitches(self) -> int:
        """Total number of stitches in the pattern."""
        return self.width * self.height

    @property
    def unique_colors_used(self) -> int:
        """Number of unique colors actually used in the pattern."""
        return len(np.unique(self.colors))

    def get_color_at(self, x: int, y: int) -> int:
        """Get color index at specific coordinates."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"Coordinates ({x}, {y}) out of bounds")
        return int(self.colors[y, x])

    def get_stitch_color(self, x: int, y: int):
        """Get the actual Color object for a stitch."""
        color_index = self.get_color_at(x, y)
        return self.palette[color_index]

    def get_color_usage_stats(self) -> Dict[int, int]:
        """Get statistics on how many times each color is used."""
        unique, counts = np.unique(self.colors, return_counts=True)
        return dict(zip(unique.astype(int), counts.astype(int)))

    def get_pattern_area(self, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """Get a rectangular area of the pattern."""
        x1, x2 = max(0, min(x1, x2)), min(self.width, max(x1, x2))
        y1, y2 = max(0, min(y1, y2)), min(self.height, max(y1, y2))
        return self.colors[y1:y2, x1:x2]

    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary for serialization."""
        return {
            "width": self.width,
            "height": self.height,
            "resolution_name": self.resolution_name,
            "total_stitches": self.total_stitches,
            "unique_colors_used": self.unique_colors_used,
            "palette_size": len(self.palette),
            "color_usage": self.get_color_usage_stats(),
        }


@dataclass
class PatternSet:
    """Collection of cross-stitch patterns at different resolutions."""

    patterns: Dict[str, CrossStitchPattern]
    source_image_path: Path
    metadata: Dict[str, Any]

    def __post_init__(self) -> None:
        """Validate pattern set."""
        if not self.patterns:
            raise ValueError("PatternSet must contain at least one pattern")

        if not self.source_image_path.exists():
            raise ValueError(
                f"Source image path does not exist: {self.source_image_path}"
            )

    def get_pattern(self, resolution_name: str) -> CrossStitchPattern:
        """Get pattern by resolution name."""
        if resolution_name not in self.patterns:
            available = list(self.patterns.keys())
            raise KeyError(
                f"Pattern '{resolution_name}' not found. Available: {available}"
            )
        return self.patterns[resolution_name]

    def get_pattern_by_size(
        self, width: int, height: int
    ) -> Optional[CrossStitchPattern]:
        """Get pattern by exact dimensions."""
        for pattern in self.patterns.values():
            if pattern.width == width and pattern.height == height:
                return pattern
        return None

    def add_pattern(self, pattern: CrossStitchPattern) -> None:
        """Add a pattern to the set."""
        self.patterns[pattern.resolution_name] = pattern

    @property
    def resolution_names(self) -> list[str]:
        """Get list of all resolution names."""
        return list(self.patterns.keys())

    @property
    def pattern_count(self) -> int:
        """Number of patterns in the set."""
        return len(self.patterns)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary information about all patterns."""
        summary = {
            "source_image": str(self.source_image_path),
            "pattern_count": self.pattern_count,
            "resolutions": self.resolution_names,
            "metadata": self.metadata,
            "patterns": {},
        }

        for name, pattern in self.patterns.items():
            summary["patterns"][name] = pattern.to_dict()

        return summary

    def get_total_unique_colors(self) -> int:
        """Get total number of unique colors used across all patterns."""
        all_colors = set()
        for pattern in self.patterns.values():
            # Add color tuples from each palette
            for color in pattern.palette:
                all_colors.add(color.rgb_tuple)
        return len(all_colors)

    def __iter__(self):
        """Iterate over patterns."""
        return iter(self.patterns.values())

    def __len__(self) -> int:
        """Number of patterns."""
        return len(self.patterns)

    def __getitem__(self, resolution_name: str) -> CrossStitchPattern:
        """Get pattern by resolution name."""
        return self.get_pattern(resolution_name)
