"""Generate descriptive color names from hex codes for better UX."""

import colorsys
from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSL."""
    r, g, b = r/255.0, g/255.0, b/255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100, l * 100  # Convert to degrees and percentages


def generate_color_name(hex_color: str) -> str:
    """Generate a descriptive color name from hex code.

    Args:
        hex_color: Hex color string like "#3A5FCD"

    Returns:
        Descriptive color name like "Steel Blue" or "Forest Green"
    """
    try:
        r, g, b = hex_to_rgb(hex_color)
        h, s, l = rgb_to_hsl(r, g, b)

        # Handle grayscale colors first
        if s < 10:  # Very low saturation = grayscale
            if l < 15:
                return "Black"
            elif l < 25:
                return "Charcoal"
            elif l < 40:
                return "Dark Gray"
            elif l < 60:
                return "Gray"
            elif l < 80:
                return "Light Gray"
            elif l < 95:
                return "Silver"
            else:
                return "White"

        # Determine base hue name
        hue_name = get_hue_name(h)

        # Determine lightness modifier
        lightness_modifier = get_lightness_modifier(l)

        # Determine saturation modifier
        saturation_modifier = get_saturation_modifier(s, l)

        # Combine modifiers intelligently
        if lightness_modifier and saturation_modifier:
            if saturation_modifier in ["Muted", "Dusty"]:
                return f"{saturation_modifier} {lightness_modifier} {hue_name}".strip()
            else:
                return f"{lightness_modifier} {saturation_modifier} {hue_name}".strip()
        elif lightness_modifier:
            return f"{lightness_modifier} {hue_name}".strip()
        elif saturation_modifier:
            return f"{saturation_modifier} {hue_name}".strip()
        else:
            return hue_name

    except (ValueError, IndexError):
        # Fallback for invalid hex codes
        return "Unknown Color"


def get_hue_name(hue: float) -> str:
    """Get base color name from hue (0-360 degrees)."""
    # Normalize hue to 0-360
    hue = hue % 360

    if hue < 15 or hue >= 345:
        return "Red"
    elif hue < 30:
        return "Orange"
    elif hue < 45:
        return "Gold"
    elif hue < 75:
        return "Yellow"
    elif hue < 105:
        return "Lime"
    elif hue < 135:
        return "Green"
    elif hue < 165:
        return "Emerald"
    elif hue < 195:
        return "Cyan"
    elif hue < 225:
        return "Blue"
    elif hue < 255:
        return "Navy"
    elif hue < 285:
        return "Purple"
    elif hue < 315:
        return "Magenta"
    else:
        return "Rose"


def get_lightness_modifier(lightness: float) -> str:
    """Get lightness modifier from lightness percentage."""
    if lightness < 20:
        return "Very Dark"
    elif lightness < 35:
        return "Dark"
    elif lightness < 45:
        return "Deep"
    elif lightness < 65:
        return ""  # No modifier for medium lightness
    elif lightness < 80:
        return "Light"
    elif lightness < 90:
        return "Very Light"
    else:
        return "Pale"


def get_saturation_modifier(saturation: float, lightness: float) -> str:
    """Get saturation modifier from saturation and lightness percentages."""
    if saturation < 20:
        if lightness > 60:
            return "Dusty"
        else:
            return "Muted"
    elif saturation < 40:
        return "Soft"
    elif saturation > 80:
        if lightness < 40:
            return "Rich"
        else:
            return "Bright"
    else:
        return ""  # No modifier for medium saturation


# Popular cross-stitch color examples for testing
EXAMPLE_COLORS = {
    "#000000": "Black",
    "#FFFFFF": "White",
    "#FF0000": "Bright Red",
    "#800000": "Dark Red",
    "#FFA500": "Orange",
    "#FFD700": "Gold",
    "#FFFF00": "Bright Yellow",
    "#008000": "Green",
    "#0000FF": "Blue",
    "#000080": "Navy",
    "#800080": "Purple",
    "#FFC0CB": "Light Rose",
    "#708090": "Gray",
    "#2F4F4F": "Dark Gray",
    "#4169E1": "Blue",
    "#32CD32": "Lime",
    "#DC143C": "Red",
    "#FF1493": "Bright Magenta",
    "#8B4513": "Dark Gold",
    "#228B22": "Dark Green",
}


if __name__ == "__main__":
    # Test the color name generator
    print("Testing color name generation:")
    for hex_code, expected in EXAMPLE_COLORS.items():
        generated = generate_color_name(hex_code)
        print(f"{hex_code:8} → {generated:20} (expected: {expected})")