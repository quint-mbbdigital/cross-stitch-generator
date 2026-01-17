"""Memory and temporary file management for Replit environment."""
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from pathlib import Path
import shutil


@contextmanager
def ephemeral_workspace():
    """Create a temporary workspace that auto-cleans on exit."""
    with TemporaryDirectory(prefix="cross_stitch_") as tmpdir:
        workspace = Path(tmpdir)
        yield workspace


def estimate_memory_usage(width: int, height: int, max_colors: int) -> dict:
    """Estimate memory usage for pattern generation."""
    pixels = width * height

    # Base image processing: ~24 bytes per pixel (RGB float64 intermediate)
    image_memory = pixels * 24

    # Pattern storage: 1 byte per pixel for color indices
    pattern_memory = pixels

    # Color palette: ~100 bytes per color (RGB + metadata)
    palette_memory = max_colors * 100

    # Excel generation overhead: ~2x pattern size
    excel_memory = pattern_memory * 2

    total_mb = (image_memory + pattern_memory + palette_memory + excel_memory) / 1_000_000

    return {
        "total_mb": round(total_mb, 1),
        "image_mb": round(image_memory / 1_000_000, 1),
        "pattern_mb": round(pattern_memory / 1_000_000, 1),
        "excel_mb": round(excel_memory / 1_000_000, 1)
    }