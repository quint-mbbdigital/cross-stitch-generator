"""DMC color matching functionality for cross-stitch patterns."""

import math
from typing import Dict, Tuple, Optional

from ..models.color_palette import Color, ColorPalette
from ..data.dmc_loader import load_dmc_palette


class DMCMatcher:
    """Matches colors to closest DMC floss colors."""

    def __init__(self, dmc_database_path: Optional[str] = None):
        """Initialize DMC matcher with color database.

        Args:
            dmc_database_path: Path to custom DMC color database CSV file
        """
        self.dmc_palette = load_dmc_palette(dmc_database_path)

    def is_available(self) -> bool:
        """Check if DMC palette is available."""
        return len(self.dmc_palette) > 0

    def find_closest_dmc(self, rgb: Tuple[int, int, int]) -> Color:
        """Find closest DMC color to given RGB values.

        Args:
            rgb: RGB tuple (r, g, b)

        Returns:
            Color object with DMC thread code and name

        Raises:
            ValueError: If no DMC palette is available
        """
        if not self.is_available():
            raise ValueError("No DMC color palette available")

        r, g, b = rgb
        min_distance = float('inf')
        closest_color = None

        # Find closest color using Euclidean distance in RGB space
        for dmc_code, dmc_color in self.dmc_palette.items():
            # Calculate Euclidean distance
            distance = math.sqrt(
                (r - dmc_color.r) ** 2 +
                (g - dmc_color.g) ** 2 +
                (b - dmc_color.b) ** 2
            )

            if distance < min_distance:
                min_distance = distance
                closest_color = dmc_color

        if closest_color is None:
            raise ValueError("No DMC colors available for matching")

        return closest_color

    def map_palette_to_dmc(self, palette: ColorPalette) -> ColorPalette:
        """Map an existing color palette to nearest DMC colors.

        Args:
            palette: Original color palette

        Returns:
            New palette with DMC-matched colors
        """
        if not self.is_available():
            # Return original palette if no DMC database available
            return palette

        dmc_colors = []

        for color in palette.colors:
            # Find closest DMC color
            closest_dmc = self.find_closest_dmc((color.r, color.g, color.b))

            # Create new color with original RGB but DMC metadata
            # Keep original RGB for visual consistency, add DMC info for reference
            dmc_matched_color = Color(
                r=color.r,
                g=color.g,
                b=color.b,
                name=closest_dmc.name,
                thread_code=closest_dmc.thread_code
            )

            dmc_colors.append(dmc_matched_color)

        # Create new palette with DMC-enhanced colors
        return ColorPalette(
            colors=dmc_colors,
            max_colors=palette.max_colors,
            quantization_method=palette.quantization_method
        )

    def create_dmc_only_palette(self, max_colors: int,
                               most_common_only: Optional[int] = None) -> ColorPalette:
        """Create a palette using only actual DMC colors.

        Args:
            max_colors: Maximum number of colors in palette
            most_common_only: If specified, only use N most common DMC colors

        Returns:
            ColorPalette with only real DMC colors
        """
        if not self.is_available():
            raise ValueError("No DMC color palette available")

        available_colors = list(self.dmc_palette.values())

        # If most_common_only is specified, we'd need usage statistics
        # For now, just use the first N colors from the database
        # In a real implementation, you might sort by actual usage frequency
        if most_common_only is not None:
            available_colors = available_colors[:most_common_only]

        # Limit to max_colors
        selected_colors = available_colors[:max_colors]

        return ColorPalette(
            colors=selected_colors,
            max_colors=max_colors,
            quantization_method="dmc_only"
        )

    def get_palette_info(self) -> Dict[str, int]:
        """Get information about the loaded DMC palette.

        Returns:
            Dictionary with palette statistics
        """
        return {
            'total_colors': len(self.dmc_palette),
            'available': self.is_available()
        }