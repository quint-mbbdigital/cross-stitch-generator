"""Color and palette models for cross-stitch patterns."""

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class Color:
    """RGB color with optional metadata."""

    r: int
    g: int
    b: int
    name: Optional[str] = None
    thread_code: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate color values."""
        for component, name in [(self.r, "r"), (self.g, "g"), (self.b, "b")]:
            if not 0 <= component <= 255:
                raise ValueError(
                    f"Color component {name} must be 0-255, got {component}"
                )

    @property
    def hex_code(self) -> str:
        """Get hexadecimal color code."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @property
    def rgb_tuple(self) -> Tuple[int, int, int]:
        """Get RGB tuple."""
        return (self.r, self.g, self.b)

    @classmethod
    def from_hex(
        cls,
        hex_code: str,
        name: Optional[str] = None,
        thread_code: Optional[str] = None,
    ) -> "Color":
        """Create Color from hexadecimal string."""
        # Remove '#' if present
        hex_code = hex_code.lstrip("#")

        if len(hex_code) != 6:
            raise ValueError(f"Invalid hex color code: {hex_code}")

        try:
            r = int(hex_code[0:2], 16)
            g = int(hex_code[2:4], 16)
            b = int(hex_code[4:6], 16)
        except ValueError:
            raise ValueError(f"Invalid hex color code: {hex_code}")

        return cls(r=r, g=g, b=b, name=name, thread_code=thread_code)

    @classmethod
    def from_rgb(
        cls,
        rgb: Tuple[int, int, int],
        name: Optional[str] = None,
        thread_code: Optional[str] = None,
    ) -> "Color":
        """Create Color from RGB tuple."""
        return cls(r=rgb[0], g=rgb[1], b=rgb[2], name=name, thread_code=thread_code)

    def distance_to(self, other: "Color") -> float:
        """Calculate Euclidean distance to another color."""
        return (
            (self.r - other.r) ** 2 + (self.g - other.g) ** 2 + (self.b - other.b) ** 2
        ) ** 0.5

    def __str__(self) -> str:
        """String representation."""
        if self.name:
            return f"{self.name} ({self.hex_code})"
        return self.hex_code


@dataclass
class ColorPalette:
    """Collection of colors used in a cross-stitch pattern."""

    colors: List[Color]
    max_colors: int = 256
    quantization_method: str = "median_cut"

    def __post_init__(self) -> None:
        """Validate palette."""
        if len(self.colors) > self.max_colors:
            raise ValueError(f"Too many colors: {len(self.colors)} > {self.max_colors}")

    def add_color(self, color: Color) -> int:
        """Add a color to the palette and return its index."""
        if len(self.colors) >= self.max_colors:
            raise ValueError(
                f"Cannot add color: palette full ({self.max_colors} colors)"
            )

        # Check if color already exists
        for i, existing_color in enumerate(self.colors):
            if existing_color.rgb_tuple == color.rgb_tuple:
                return i

        # Add new color
        self.colors.append(color)
        return len(self.colors) - 1

    def get_color_by_index(self, index: int) -> Color:
        """Get color by index."""
        if not 0 <= index < len(self.colors):
            raise IndexError(f"Color index {index} out of range")
        return self.colors[index]

    def find_closest_color(self, target_color: Color) -> Tuple[Color, int]:
        """Find the closest color in the palette."""
        if not self.colors:
            raise ValueError("Palette is empty")

        closest_color = self.colors[0]
        closest_index = 0
        min_distance = target_color.distance_to(closest_color)

        for i, color in enumerate(self.colors[1:], 1):
            distance = target_color.distance_to(color)
            if distance < min_distance:
                min_distance = distance
                closest_color = color
                closest_index = i

        return closest_color, closest_index

    def get_color_counts(self) -> int:
        """Get the number of colors in the palette."""
        return len(self.colors)

    def to_rgb_array(self) -> List[Tuple[int, int, int]]:
        """Convert palette to list of RGB tuples."""
        return [color.rgb_tuple for color in self.colors]

    def __len__(self) -> int:
        """Number of colors in palette."""
        return len(self.colors)

    def __getitem__(self, index: int) -> Color:
        """Get color by index."""
        return self.colors[index]

    def __iter__(self):
        """Iterate over colors."""
        return iter(self.colors)
