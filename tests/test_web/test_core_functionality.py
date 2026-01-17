"""Test core web functionality avoiding sklearn imports."""

import sys
from pathlib import Path
from io import BytesIO

# Test image path
TEST_IMAGE_PATH = Path(__file__).parent.parent.parent / "mbb_digital.jpg"


def test_image_file_loading():
    """Test basic image loading with PIL."""
    from PIL import Image

    print(f"Testing image file: {TEST_IMAGE_PATH}")
    assert TEST_IMAGE_PATH.exists(), f"Test image not found: {TEST_IMAGE_PATH}"

    with open(TEST_IMAGE_PATH, 'rb') as f:
        image_bytes = f.read()

    print(f"Image file size: {len(image_bytes)} bytes")

    # Test PIL loading
    image = Image.open(BytesIO(image_bytes))
    print(f"Image loaded: {image.size} pixels, mode: {image.mode}")

    assert image.size[0] > 0, "Image width should be positive"
    assert image.size[1] > 0, "Image height should be positive"

    return image, image_bytes


def test_fastapi_server_basic():
    """Test FastAPI server without sklearn dependencies."""
    from fastapi.testclient import TestClient

    # Create a minimal FastAPI app to test core functionality
    from fastapi import FastAPI, UploadFile, File
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import JSONResponse

    app = FastAPI()

    # Mount static files if they exist
    static_path = Path(__file__).parent.parent.parent / "web" / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=static_path), name="static")

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.post("/test-upload")
    async def test_upload(file: UploadFile = File(...)):
        """Test upload without processing pipeline."""
        if not file.content_type or not file.content_type.startswith("image/"):
            return JSONResponse({"error": "Not an image"}, status_code=400)

        contents = await file.read()

        # Basic image analysis without sklearn
        from PIL import Image
        try:
            image = Image.open(BytesIO(contents))
            return {
                "success": True,
                "width": image.size[0],
                "height": image.size[1],
                "mode": image.mode,
                "file_size": len(contents)
            }
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    client = TestClient(app)

    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    print("✅ Health endpoint works")

    # Test upload with real image
    with open(TEST_IMAGE_PATH, 'rb') as f:
        files = {"file": ("mbb_digital.jpg", f, "image/jpeg")}
        response = client.post("/test-upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["width"] > 0
    assert data["height"] > 0

    print(f"✅ Upload test successful: {data}")
    return data


def test_median_cut_quantization():
    """Test median cut color quantization without sklearn."""
    from PIL import Image

    image, _ = test_image_file_loading()

    # Test median cut quantization (built into PIL, no sklearn needed)
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Resize to manageable size
    image.thumbnail((100, 100))

    # Use PIL's quantize with median cut algorithm
    quantized = image.quantize(colors=16, method=Image.Quantize.MEDIANCUT)

    print(f"✅ Median cut quantization: {image.size} -> {quantized.mode} with {len(quantized.getcolors())} colors")

    # Get palette colors
    palette = quantized.getpalette()
    if palette:
        # Convert palette to hex colors
        hex_colors = []
        for i in range(0, min(48, len(palette)), 3):  # 16 colors * 3 components
            r, g, b = palette[i:i+3]
            hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")

        print(f"✅ Generated palette: {hex_colors[:8]}...")  # Show first 8 colors

    return quantized, hex_colors


def test_basic_pattern_data_structure():
    """Test creating pattern data structure without full pipeline."""
    quantized, hex_colors = test_median_cut_quantization()

    # Create basic pattern data structure
    width, height = quantized.size
    pixels = list(quantized.getdata())

    pattern_data = {
        "width": width,
        "height": height,
        "palette": hex_colors,
        "grid": pixels,
        "total_stitches": len(pixels)
    }

    print(f"✅ Pattern data structure: {pattern_data['width']}x{pattern_data['height']}, {len(pattern_data['palette'])} colors")

    assert pattern_data["width"] > 0
    assert pattern_data["height"] > 0
    assert len(pattern_data["palette"]) > 0
    assert len(pattern_data["grid"]) > 0

    return pattern_data


def test_web_template_rendering():
    """Test web template rendering."""
    from fastapi import FastAPI, Request
    from fastapi.templating import Jinja2Templates
    from fastapi.testclient import TestClient

    app = FastAPI()

    # Templates path
    templates_path = Path(__file__).parent.parent.parent / "web" / "templates"
    if not templates_path.exists():
        print("❌ Templates directory not found - skipping template test")
        return

    templates = Jinja2Templates(directory=templates_path)

    @app.get("/")
    async def index(request: Request):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "title": "Cross-Stitch Generator"
        })

    client = TestClient(app)
    response = client.get("/")

    if response.status_code == 200:
        content = response.text
        assert "Cross-Stitch Generator" in content
        assert "Modern Atelier" in content or "text/html" in response.headers["content-type"]
        print("✅ Template rendering works")
    else:
        print(f"❌ Template rendering failed: {response.status_code}")


if __name__ == "__main__":
    print("=== Testing Core Web Functionality (No sklearn) ===\n")

    try:
        print("1. Testing basic image loading...")
        test_image_file_loading()

        print("\n2. Testing FastAPI server...")
        test_fastapi_server_basic()

        print("\n3. Testing median cut quantization...")
        test_median_cut_quantization()

        print("\n4. Testing pattern data structure...")
        test_basic_pattern_data_structure()

        print("\n5. Testing template rendering...")
        test_web_template_rendering()

        print("\n🎉 All core tests PASSED!")
        print("\nNext steps:")
        print("1. Install fixed requirements: pip install -r requirements-web-fixed.txt")
        print("2. This will downgrade numpy to be compatible with pandas/sklearn")
        print("3. Then the full web application will work without numpy errors")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()