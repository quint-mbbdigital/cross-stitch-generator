"""Pytest configuration and fixtures for cross-stitch generator tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import numpy as np

from src.cross_stitch.models import GeneratorConfig, Color, ColorPalette, CrossStitchPattern


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    return GeneratorConfig(
        resolutions=[(50, 50), (100, 100)],
        max_colors=64,
        quantization_method="median_cut",
        preserve_aspect_ratio=True,
        handle_transparency="white_background",
        excel_cell_size=20.0,
        include_color_legend=True
    )


@pytest.fixture
def sample_colors():
    """Create sample colors for testing."""
    return [
        Color(r=255, g=0, b=0),    # Red
        Color(r=0, g=255, b=0),    # Green
        Color(r=0, g=0, b=255),    # Blue
        Color(r=255, g=255, b=0),  # Yellow
        Color(r=255, g=255, b=255) # White
    ]


@pytest.fixture
def sample_palette(sample_colors):
    """Create a sample color palette for testing."""
    return ColorPalette(
        colors=sample_colors,
        max_colors=256,
        quantization_method="median_cut"
    )


@pytest.fixture
def sample_pattern(sample_palette):
    """Create a sample cross-stitch pattern for testing."""
    # Create a simple 10x10 pattern with alternating colors
    colors = np.array([[i % 5 for i in range(10)] for _ in range(10)])

    return CrossStitchPattern(
        width=10,
        height=10,
        colors=colors,
        palette=sample_palette,
        resolution_name="10x10"
    )


@pytest.fixture
def sample_image_rgb(temp_dir):
    """Create a sample RGB image for testing."""
    # Create a simple 100x100 RGB image with a gradient
    width, height = 100, 100
    image_array = np.zeros((height, width, 3), dtype=np.uint8)

    # Create a gradient pattern
    for y in range(height):
        for x in range(width):
            image_array[y, x] = [
                int(255 * x / width),      # Red gradient horizontal
                int(255 * y / height),     # Green gradient vertical
                128                        # Constant blue
            ]

    image = Image.fromarray(image_array, mode='RGB')
    image_path = temp_dir / "sample_rgb.png"
    image.save(image_path)

    return image_path


@pytest.fixture
def sample_image_rgba(temp_dir):
    """Create a sample RGBA image with transparency for testing."""
    # Create a simple 50x50 RGBA image
    width, height = 50, 50
    image_array = np.zeros((height, width, 4), dtype=np.uint8)

    # Create a pattern with transparency
    for y in range(height):
        for x in range(width):
            if (x + y) % 2 == 0:  # Checkerboard pattern
                image_array[y, x] = [255, 0, 0, 255]  # Red, opaque
            else:
                image_array[y, x] = [0, 255, 0, 128]  # Green, semi-transparent

    image = Image.fromarray(image_array, mode='RGBA')
    image_path = temp_dir / "sample_rgba.png"
    image.save(image_path)

    return image_path


@pytest.fixture
def sample_image_grayscale(temp_dir):
    """Create a sample grayscale image for testing."""
    # Create a simple 75x75 grayscale image
    width, height = 75, 75
    image_array = np.zeros((height, width), dtype=np.uint8)

    # Create a circular gradient
    center_x, center_y = width // 2, height // 2
    max_distance = min(width, height) // 2

    for y in range(height):
        for x in range(width):
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            intensity = max(0, int(255 * (1 - distance / max_distance)))
            image_array[y, x] = intensity

    image = Image.fromarray(image_array, mode='L')
    image_path = temp_dir / "sample_grayscale.png"
    image.save(image_path)

    return image_path


@pytest.fixture
def invalid_image_path(temp_dir):
    """Create an invalid image file for testing error cases."""
    invalid_path = temp_dir / "invalid.txt"
    invalid_path.write_text("This is not an image file")
    return invalid_path


@pytest.fixture
def nonexistent_image_path(temp_dir):
    """Return a path to a non-existent image file."""
    return temp_dir / "nonexistent.png"


@pytest.fixture
def sample_excel_output(temp_dir):
    """Return a path for Excel output testing."""
    return temp_dir / "test_output.xlsx"


@pytest.fixture
def large_image(temp_dir):
    """Create a larger image for performance testing."""
    # Create a 500x500 image with multiple colors
    width, height = 500, 500
    image_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)

    image = Image.fromarray(image_array, mode='RGB')
    image_path = temp_dir / "large_image.png"
    image.save(image_path)

    return image_path


@pytest.fixture
def tiny_image(temp_dir):
    """Create a very small image for edge case testing."""
    # Create a 5x5 image
    width, height = 5, 5
    image_array = np.array([
        [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [255, 0, 255]],
        [[0, 255, 0], [0, 0, 255], [255, 255, 0], [255, 0, 255], [255, 0, 0]],
        [[0, 0, 255], [255, 255, 0], [255, 0, 255], [255, 0, 0], [0, 255, 0]],
        [[255, 255, 0], [255, 0, 255], [255, 0, 0], [0, 255, 0], [0, 0, 255]],
        [[255, 0, 255], [255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]]
    ], dtype=np.uint8)

    image = Image.fromarray(image_array, mode='RGB')
    image_path = temp_dir / "tiny_image.png"
    image.save(image_path)

    return image_path


class MockProgressCallback:
    """Mock progress callback for testing."""

    def __init__(self):
        self.calls = []

    def __call__(self, message: str, progress: float):
        self.calls.append((message, progress))

    @property
    def last_message(self):
        return self.calls[-1][0] if self.calls else None

    @property
    def last_progress(self):
        return self.calls[-1][1] if self.calls else None

    @property
    def final_progress(self):
        """Return the highest progress value recorded."""
        return max(call[1] for call in self.calls) if self.calls else 0.0


@pytest.fixture
def mock_progress_callback():
    """Create a mock progress callback for testing."""
    return MockProgressCallback()


# Utility functions for tests

def assert_valid_color(color):
    """Assert that a color object is valid."""
    assert isinstance(color, Color)
    assert 0 <= color.r <= 255
    assert 0 <= color.g <= 255
    assert 0 <= color.b <= 255
    assert isinstance(color.hex_code, str)
    assert len(color.hex_code) == 7
    assert color.hex_code.startswith('#')


def assert_valid_palette(palette):
    """Assert that a color palette is valid."""
    assert isinstance(palette, ColorPalette)
    assert len(palette.colors) > 0
    assert len(palette.colors) <= palette.max_colors

    for color in palette.colors:
        assert_valid_color(color)


def assert_valid_pattern(pattern):
    """Assert that a cross-stitch pattern is valid."""
    assert isinstance(pattern, CrossStitchPattern)
    assert pattern.width > 0
    assert pattern.height > 0
    assert pattern.colors.shape == (pattern.height, pattern.width)
    assert_valid_palette(pattern.palette)

    # Check that all color indices are valid
    max_index = len(pattern.palette) - 1
    assert np.all(pattern.colors >= 0)
    assert np.all(pattern.colors <= max_index)


def create_test_image(width: int, height: int, mode: str = 'RGB') -> Image.Image:
    """Create a test image with specific dimensions and mode."""
    if mode == 'RGB':
        channels = 3
    elif mode == 'RGBA':
        channels = 4
    elif mode == 'L':
        return Image.new('L', (width, height), color=128)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    # Create random image data
    image_array = np.random.randint(0, 256, (height, width, channels), dtype=np.uint8)

    if mode == 'RGBA':
        # Make some pixels transparent for testing
        image_array[:, :, 3] = np.random.choice([0, 255], size=(height, width))

    return Image.fromarray(image_array, mode=mode)