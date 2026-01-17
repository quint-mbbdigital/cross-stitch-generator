"""Test image processing functionality with real image files."""

import pytest
from io import BytesIO
from pathlib import Path
import asyncio

from web.utils.async_processing import process_upload, resize_if_needed
from web.models.responses import AnalysisResult


# Test image path
TEST_IMAGE_PATH = Path(__file__).parent.parent.parent / "mbb_digital.jpg"


class TestImageProcessing:
    """Test image processing functions with real image."""

    def test_image_file_exists(self):
        """Verify test image file exists."""
        assert TEST_IMAGE_PATH.exists(), f"Test image not found: {TEST_IMAGE_PATH}"
        assert TEST_IMAGE_PATH.stat().st_size > 0, "Test image file is empty"

    def test_image_loading_direct(self):
        """Test basic PIL image loading without async wrapper."""
        from PIL import Image

        with open(TEST_IMAGE_PATH, 'rb') as f:
            image_bytes = f.read()

        # Test direct PIL loading
        image = Image.open(BytesIO(image_bytes))
        assert image.size[0] > 0, "Image width should be positive"
        assert image.size[1] > 0, "Image height should be positive"
        print(f"Image loaded successfully: {image.size} pixels, mode: {image.mode}")

    def test_resize_if_needed_function(self):
        """Test the resize function without numpy dependencies."""
        from PIL import Image

        with open(TEST_IMAGE_PATH, 'rb') as f:
            image_bytes = f.read()

        image = Image.open(BytesIO(image_bytes))
        original_size = image.size

        # Test resize with normal image (should not resize)
        resized, warning = resize_if_needed(image, max_dimension=2000)
        assert resized.size == original_size, "Normal sized image should not be resized"
        assert warning is None, "No warning should be generated for normal image"

        # Test resize with small max dimension (should resize)
        resized, warning = resize_if_needed(image, max_dimension=100)
        assert max(resized.size) <= 100, "Image should be resized to fit max dimension"
        assert warning is not None, "Warning should be generated when resizing"
        print(f"Resize test passed: {original_size} -> {resized.size}")

    @pytest.mark.asyncio
    async def test_process_upload_without_texture_detector(self):
        """Test process_upload function, skipping texture detection to isolate numpy error."""

        with open(TEST_IMAGE_PATH, 'rb') as f:
            image_bytes = f.read()

        try:
            image, analysis = await process_upload(image_bytes)

            # Verify image processing worked
            assert image.size[0] > 0, "Processed image should have positive width"
            assert image.size[1] > 0, "Processed image should have positive height"

            # Verify analysis result
            assert isinstance(analysis, AnalysisResult), "Should return AnalysisResult object"
            assert analysis.width > 0, "Analysis width should be positive"
            assert analysis.height > 0, "Analysis height should be positive"
            assert analysis.estimated_colors > 0, "Should estimate some colors"

            print(f"Upload processing successful:")
            print(f"  Image: {image.size}")
            print(f"  Analysis: {analysis}")

        except Exception as e:
            print(f"Error in process_upload: {e}")
            # Let's see if it's specifically a numpy error
            if "numpy.dtype size changed" in str(e):
                print("FOUND: numpy compatibility error in process_upload")
                print("This is likely in scikit-learn or another compiled package")
            raise

    def test_color_estimation_manual(self):
        """Test color estimation manually to isolate numpy issues."""
        from PIL import Image

        with open(TEST_IMAGE_PATH, 'rb') as f:
            image_bytes = f.read()

        image = Image.open(BytesIO(image_bytes))

        # Manual color estimation without scikit-learn
        sample = image.copy()
        sample.thumbnail((100, 100))

        # Convert to RGB for analysis
        if sample.mode != 'RGB':
            sample = sample.convert('RGB')

        # Get colors manually
        colors = sample.getcolors(maxcolors=1000)
        estimated_colors = len(colors) if colors else 1000

        print(f"Manual color estimation: {estimated_colors} colors")
        assert estimated_colors > 0, "Should find some colors"
        return estimated_colors


@pytest.mark.asyncio
async def test_pattern_generation_minimal():
    """Test minimal pattern generation to identify numpy error location."""
    from web.routes.api import _generate_pattern_sync
    from web.models.requests import PatternConfig
    from PIL import Image

    # Load test image
    with open(TEST_IMAGE_PATH, 'rb') as f:
        image_bytes = f.read()

    image = Image.open(BytesIO(image_bytes))

    # Create minimal config
    config = PatternConfig(
        resolution=50,  # Small to avoid memory issues
        max_colors=16,  # Few colors to test basic functionality
        quantization="median_cut",  # Avoid k-means (uses sklearn)
        edge_mode="smooth",
        enable_dmc=False  # Disable DMC to isolate core functionality
    )

    try:
        # Test pattern generation
        pattern_data = await asyncio.get_event_loop().run_in_executor(
            None, _generate_pattern_sync, image, config
        )

        print(f"Pattern generation successful:")
        print(f"  Size: {pattern_data.width}x{pattern_data.height}")
        print(f"  Palette: {len(pattern_data.palette)} colors")
        print(f"  Grid: {len(pattern_data.grid)} cells")

        assert pattern_data.width > 0
        assert pattern_data.height > 0
        assert len(pattern_data.palette) > 0
        assert len(pattern_data.grid) > 0

    except Exception as e:
        print(f"Error in pattern generation: {e}")
        if "numpy.dtype size changed" in str(e):
            print("FOUND: numpy compatibility error in pattern generation")
            print("This is likely in the ColorQuantizer or related imports")
        raise


if __name__ == "__main__":
    # Run basic tests directly for debugging
    test_instance = TestImageProcessing()

    print("Testing basic image loading...")
    test_instance.test_image_file_exists()
    test_instance.test_image_loading_direct()

    print("\nTesting resize function...")
    test_instance.test_resize_if_needed_function()

    print("\nTesting color estimation...")
    test_instance.test_color_estimation_manual()

    print("\nTesting async upload processing...")
    asyncio.run(test_instance.test_process_upload_without_texture_detector())

    print("\nTesting pattern generation...")
    asyncio.run(test_pattern_generation_minimal())

    print("\nAll tests completed!")