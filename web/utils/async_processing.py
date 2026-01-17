"""Async wrappers for CPU-bound operations."""
import asyncio
from io import BytesIO
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from PIL import Image

# Thread pool for CPU-bound work
_executor = ThreadPoolExecutor(max_workers=2)


async def run_in_threadpool(func, *args, **kwargs):
    """Execute CPU-bound function in thread pool."""
    loop = asyncio.get_event_loop()
    if kwargs:
        func = partial(func, **kwargs)
    return await loop.run_in_executor(_executor, func, *args)


def resize_if_needed(image: Image.Image, max_dimension: int = 2000) -> tuple[Image.Image, Optional[str]]:
    """Sync helper: Resize PIL Image if dimension exceeds max_dimension."""
    max_size = max(image.size)

    if max_size <= max_dimension:
        return image, None

    # Calculate new size maintaining aspect ratio
    scale = max_dimension / max_size
    new_width = int(image.size[0] * scale)
    new_height = int(image.size[1] * scale)

    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    warning = f"Image resized from {image.size} to {resized.size} due to size limits"

    return resized, warning


async def resize_image_bytes(image_bytes: bytes, max_pixels: int = 1_000_000) -> tuple[bytes, bool]:
    """Resize image bytes if too large, return (bytes, was_resized)."""
    def _resize():
        image = Image.open(BytesIO(image_bytes))
        total_pixels = image.size[0] * image.size[1]

        if total_pixels <= max_pixels:
            return image_bytes, False

        # Calculate new size maintaining aspect ratio
        scale = (max_pixels / total_pixels) ** 0.5
        new_width = int(image.size[0] * scale)
        new_height = int(image.size[1] * scale)

        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        output = BytesIO()
        format = image.format if image.format else 'PNG'
        resized.save(output, format=format, optimize=True)
        return output.getvalue(), True

    return await run_in_threadpool(_resize)


async def process_upload(image_bytes: bytes):
    """Process uploaded image with texture detection."""
    from web.models.responses import AnalysisResult
    from src.cross_stitch.core.texture_detector import TextureDetector

    def _process():
        # Load and analyze image
        image = Image.open(BytesIO(image_bytes))

        # Basic analysis
        has_transparency = image.mode in ('RGBA', 'LA') or 'transparency' in image.info

        # Estimate colors (rough approximation)
        if image.mode == 'P':
            estimated_colors = len(image.getcolors() or [])
        else:
            # Sample and count unique colors in a representative area
            sample_size = min(100, image.width // 4, image.height // 4)
            if sample_size > 10:
                # Get center region
                cx, cy = image.width // 2, image.height // 2
                box = (
                    cx - sample_size // 2,
                    cy - sample_size // 2,
                    cx + sample_size // 2,
                    cy + sample_size // 2
                )
                sample = image.crop(box)
                colors = sample.getcolors(maxcolors=256)
                estimated_colors = len(colors) if colors else 256
            else:
                estimated_colors = 64  # Default estimate

        # No longer showing resize warnings - all images get resized to pattern resolution anyway
        resize_warning = None

        # CRITICAL: Texture detection using existing CLI logic
        texture_warning = None
        try:
            detector = TextureDetector()
            cli_warning = detector.analyze_texture(image)

            if cli_warning.has_problematic_texture:
                from web.models.responses import WebTextureWarning
                texture_warning = WebTextureWarning(
                    detected=True,
                    message=cli_warning.warning_message,
                    confidence=cli_warning.confidence_score
                )
        except Exception:
            # Don't fail upload on texture detection errors
            pass

        return image, AnalysisResult(
            width=image.size[0],
            height=image.size[1],
            has_transparency=has_transparency,
            estimated_colors=estimated_colors,
            texture_warning=texture_warning,
            resize_warning=resize_warning
        )

    return await run_in_threadpool(_process)