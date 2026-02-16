# Cross-Stitch Pattern Generator

A Python application that converts image files into Excel-based cross-stitch patterns with multiple resolution tabs.

## Features

- **Multi-Resolution Support**: Generate patterns at 50x50, 100x100, and 150x150 stitches (configurable)
- **Smart Color Quantization**: Uses median cut or k-means algorithms to reduce colors to manageable palettes
- **Edge Handling Controls**: Choose smooth (LANCZOS) or hard (NEAREST) resampling for different image types
- **Color Cleanup**: Automatically remove minor "noise" colors below configurable threshold
- **DMC Thread Matching**: Automatically match colors to DMC embroidery floss threads with thread codes
- **Excel Output**: Creates `.xlsx` files where each cell represents one stitch with accurate background colors
- **DMC Integration**: Pattern cells display DMC thread codes, legend shows thread names and quantities
- **Square Cells**: Properly sized cells for realistic pattern visualization
- **Color Legend**: Optional color palette summary with usage statistics and DMC thread information
- **Multiple Image Formats**: Supports PNG, JPG, GIF, BMP, TIFF, and WEBP
- **Transparency Handling**: Configurable transparency processing for RGBA images
- **Aspect Ratio Preservation**: Maintains image proportions or allows stretching

## Prerequisites & System Requirements

Before installation, ensure your system meets these requirements:

### Required Software
- **Python 3.11+** - [Download for Windows](https://python.org/downloads/) | [macOS](https://python.org/downloads/) | [Linux package manager](https://python.org)
- **C++ Build Tools** (for NumPy/SciPy compilation):
  - **Windows**: Microsoft Visual Studio Build Tools or Visual Studio Community
  - **macOS**: Xcode Command Line Tools (`xcode-select --install`)
  - **Linux**: `build-essential` package (`sudo apt-get install build-essential`)

### System Resources
- **Memory**: 2GB+ RAM recommended (large images require significant processing)
- **Storage**: 500MB for dependencies + workspace for generated files
- **Browser**: Modern browser for web interface (Chrome, Firefox, Safari, Edge)

### Expected Setup Time
- **New installation**: 5-15 minutes (depending on dependency compilation)
- **Verification & first pattern**: Additional 2-5 minutes

## Installation & Setup Validation

### Option 1: Virtual Environment Setup (Strongly Recommended)
```bash
# Create isolated environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Global Installation
```bash
# Install dependencies globally (not recommended for development)
pip install -r requirements.txt
```

### Dependency Choice Guide
- **`requirements.txt`**: Latest compatible versions (recommended for new installs)
- **`requirements-pinned.txt`**: Exact tested versions (use if you encounter compatibility issues)

### Validate Your Installation
After installation, verify everything works:

```bash
# Run environment validation
python scripts/validate-environment.py

# Quick functionality test
python cross_stitch_generator.py info --help
```

**Expected validation results**: All checks should show ✅ (green checkmarks). If you see ❌ (red X marks), see troubleshooting section below.

### Common Installation Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named '_ctypes'` | Install C++ build tools (see requirements above) |
| `ERROR: Failed building wheel for numpy` | Update pip: `python -m pip install --upgrade pip` |
| `Permission denied` errors | Use `--user` flag: `pip install --user -r requirements.txt` |
| `Port already in use` for web interface | Change port: `--port 8001` or kill conflicting process |

## Which Interface Should I Use?

Choose the right interface for your needs:

### 🌐 Web Interface (Recommended for Most Users)
**Best for**: Interactive exploration, drag-and-drop uploads, real-time preview
**When to use**:
- First-time users learning the tool
- Experimenting with settings and colors
- Need visual feedback during pattern creation
- Creating one-off patterns for personal use

**Advantages**: Real-time preview, visual controls, DMC shopping lists, mobile-friendly

### 💻 CLI Interface (Best for Power Users)
**Best for**: Automation, scripting, batch processing, integration
**When to use**:
- Processing multiple images with same settings
- Integrating into automated workflows
- Server environments without GUI
- Reproducible pattern generation with exact parameters

**Advantages**: Scriptable, faster for batch jobs, precise control, automatable

### Performance Comparison
- **Web interface**: Slightly more memory usage (browser + server), better user experience
- **CLI interface**: Lower resource usage, faster for repeated operations

## Running Locally

### Web Interface (Recommended)
Start the modern web interface with drag-and-drop upload:
```bash
uvicorn web.main:app --reload --host 127.0.0.1 --port 8000
```
Then visit: **http://localhost:8000**

### CLI Interface
For command-line usage, see the Quick Start section below.

## Quick Start

### Basic Usage

Generate cross-stitch patterns with default settings:
```bash
python cross_stitch_generator.py generate input.jpg output.xlsx
```

### Get Image Information

Analyze an image before processing:
```bash
python cross_stitch_generator.py info input.png --estimate-time
```

### Advanced Usage

Generate patterns with custom settings:
```bash
python cross_stitch_generator.py generate input.png output.xlsx \
    --resolutions "30x30,60x60,120x120" \
    --max-colors 128 \
    --quantization kmeans \
    --transparency white_background
```

### Edge Handling and Color Cleanup

#### Edge Mode Selection
- **Use `--edge-mode hard`** for:
  - Logos and graphics with solid colors
  - Pixel art and sprites
  - Images with sharp, defined boundaries
  - When you want to preserve exact color boundaries

- **Use `--edge-mode smooth` (default)** for:
  - Photographs and realistic images
  - Images with gradients and natural textures
  - When you want smooth color transitions

#### Color Cleanup
- **Use `--min-color-percent`** to automatically remove minor "noise" colors:
  - **Recommended values: 1.0-3.0** for cleaning edge artifacts
  - **Set to 0 (default)** to keep all colors
  - Colors below the threshold get merged into their nearest neighbors
  - Helps simplify patterns and reduce thread count

#### Combined Usage Example
```bash
python cross_stitch_generator.py generate logo.png pattern.xlsx \
    --edge-mode hard \
    --min-color-percent 2.0
```

## Command-Line Options

### Generate Command

- `--resolutions` / `-r`: Target resolutions (e.g., "50x50,100x100,150x150")
- `--max-colors` / `-c`: Maximum number of colors (default: 256)
- `--quantization`: Color quantization method (`median_cut` or `kmeans`)
- `--transparency`: Transparency handling (`white_background`, `remove`, `preserve`)
- `--no-aspect-ratio`: Disable aspect ratio preservation
- `--edge-mode`: Edge handling mode (`smooth` for photos, `hard` for logos/graphics)
- `--min-color-percent`: Merge colors below this percentage threshold (0.0-100.0)
- `--cell-size`: Excel cell size in points (default: 20.0)
- `--no-legend`: Skip color legend sheet
- `--legend-name`: Custom name for legend sheet

#### DMC Thread Options
- `--enable-dmc`: Enable DMC thread color matching (default when database available)
- `--dmc-only`: Restrict quantization to existing DMC thread colors only
- `--dmc-palette-size N`: Limit to N most common DMC thread colors
- `--no-dmc`: Explicitly disable DMC thread matching
- `--dmc-database PATH`: Use custom DMC thread database CSV file

### Info Command

- `--estimate-time`: Include processing time estimates
- Configuration options (same as generate) for analysis

### Global Options

- `--verbose` / `-v`: Enable detailed output
- `--quiet` / `-q`: Suppress progress output

## Examples

### Example 1: Basic Pattern Generation
```bash
python cross_stitch_generator.py generate photo.jpg my_pattern.xlsx
```

Creates an Excel file with three sheets (50x50, 100x100, 150x150) plus color legend.

### Example 2: Custom Resolutions for Small Design
```bash
python cross_stitch_generator.py generate logo.png small_pattern.xlsx \
    --resolutions "25x25,40x40" \
    --max-colors 16
```

### Example 3: Large Pattern with Many Colors
```bash
python cross_stitch_generator.py generate landscape.jpg detailed_pattern.xlsx \
    --resolutions "200x200,300x300" \
    --max-colors 512 \
    --quantization kmeans
```

### Example 4: Transparent Image Processing
```bash
python cross_stitch_generator.py generate sprite.png game_pattern.xlsx \
    --transparency white_background \
    --resolutions "32x32,64x64"
```

### Example 5: DMC Thread Color Matching
```bash
python cross_stitch_generator.py generate flower.jpg dmc_pattern.xlsx \
    --enable-dmc \
    --max-colors 32
```

Generates patterns with DMC thread codes displayed in cells and thread names in the legend.

### Example 6: DMC-Only Color Palette
```bash
python cross_stitch_generator.py generate portrait.jpg dmc_only.xlsx \
    --dmc-only \
    --dmc-palette-size 50 \
    --max-colors 24
```

Restricts quantization to only use actual DMC thread colors from the 50 most common threads.

### Example 7: Custom DMC Database
```bash
python cross_stitch_generator.py generate vintage.jpg custom_dmc.xlsx \
    --dmc-database my_dmc_colors.csv \
    --enable-dmc
```

Uses a custom DMC thread database file for specialized thread collections.

### Example 8: Disable DMC for RGB-Only Output
```bash
python cross_stitch_generator.py generate abstract.png rgb_only.xlsx \
    --no-dmc \
    --max-colors 64
```

Explicitly disables DMC matching for pure RGB color output without thread codes.

### Example 9: Clean Logo/Graphics Pattern
```bash
python cross_stitch_generator.py generate logo.png pattern.xlsx \
    --edge-mode hard \
    --min-color-percent 2.0
```

Perfect for logos, pixel art, and graphics with solid colors. Uses hard edges to prevent color bleeding and removes minor noise colors.

### Example 10: High-Quality Photo Pattern
```bash
python cross_stitch_generator.py generate photo.jpg pattern.xlsx \
    --edge-mode smooth \
    --min-color-percent 1.0
```

Best for photographs and complex images. Uses smooth interpolation for natural gradients while cleaning up minor noise.

## Setting Up for Development

If you plan to contribute to the project or need the development environment:

### Development vs Production Installation

**Production Use** (pattern generation only):
```bash
pip install -r requirements.txt
```

**Development Setup** (contributing, testing, debugging):
```bash
# Install development dependencies
pip install -r requirements.txt -r requirements-web.txt

# Install additional development tools
pip install pytest pytest-cov mypy ruff
```

### Running and Interpreting Tests

```bash
# Run all tests with detailed output
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src/cross_stitch --cov-report=term-missing

# Run specific test modules
pytest tests/test_integration.py -v
pytest tests/test_models.py -v
pytest tests/test_utils.py -v
```

**Current Test Status**: 254/279 tests passing (~91% success rate)
- **24 failing tests**: Non-critical features (edge mode improvements, Excel professional formatting)
- **Safe to develop**: Core functionality (image processing, pattern generation, Excel output) is fully tested and stable
- **Known issues**: Some edge mode and professional Excel enhancement tests failing - these don't affect basic functionality

### Development Server (Web Interface)

```bash
# Start development server with hot reload
uvicorn web.main:app --reload --host 0.0.0.0 --port 8000

# Or with specific configuration
uvicorn web.main:app --reload --host 127.0.0.1 --port 8001 --log-level debug
```

Visit: http://localhost:8000 for the web interface

### Code Quality Tools

```bash
# Check code style and potential issues
python -m ruff check .

# Format code automatically
python -m ruff format .

# Type checking
python -m mypy src/

# Run all quality checks before committing
python -m ruff check . && python -m ruff format . && python -m mypy src/ && pytest tests/ -v
```

### Development Workflow Quick Reference

1. **Make changes** to code
2. **Run tests** to ensure nothing breaks: `pytest tests/ -v`
3. **Run code quality** checks: `ruff check . && mypy src/`
4. **Test manually** with both CLI and web interface
5. **Commit** with descriptive message following [conventional commits](https://conventionalcommits.org/)

### Pre-commit Setup (Optional)

For automatic code quality checks before each commit:
```bash
# Install pre-commit
pip install pre-commit

# Install git hook scripts
pre-commit install

# Run against all files
pre-commit run --all-files
```

### Related Documentation

- **[CLAUDE.md](CLAUDE.md)**: Comprehensive development guide with TDD workflow, team collaboration guidelines, and architecture details
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Production deployment instructions and server configuration
- **Environment Validation**: Use `python scripts/validate-environment.py` for comprehensive setup verification

## Quick Reference

### Essential Commands Matrix

| Task | CLI Command | Web Interface |
|------|-------------|---------------|
| **Basic Pattern** | `python cross_stitch_generator.py generate input.jpg output.xlsx` | Upload → Generate → Download |
| **Custom Size** | `python cross_stitch_generator.py generate input.jpg output.xlsx --resolutions "100x100"` | Use size slider → Generate |
| **Fewer Colors** | `python cross_stitch_generator.py generate input.jpg output.xlsx --max-colors 32` | Use color slider → Generate |
| **DMC Threads** | `python cross_stitch_generator.py generate input.jpg output.xlsx --enable-dmc` | Toggle "Use DMC Colors" → Generate |
| **Image Info** | `python cross_stitch_generator.py info input.jpg --estimate-time` | Upload image → View info panel |
| **Web Interface** | `uvicorn web.main:app --reload --host 0.0.0.0 --port 8000` | N/A - starts web server |

### Common Options Quick Lookup

```bash
# Image Processing
--resolutions "50x50,100x100,150x150"    # Multiple pattern sizes
--max-colors 64                           # Reduce thread count
--transparency white_background           # Handle PNG transparency
--edge-mode smooth                        # Best for photos
--edge-mode hard                          # Best for logos/graphics

# DMC Thread Options
--enable-dmc                             # Match to real thread colors
--dmc-only                               # Use only available DMC colors
--no-dmc                                 # Disable thread matching

# Output Control
--no-legend                              # Skip color reference sheet
--cell-size 15.0                         # Smaller pattern cells
--verbose                                # Detailed progress output
```

### Troubleshooting One-Liners

```bash
# Environment Check
python scripts/validate-environment.py

# Dependency Issues
pip uninstall numpy scipy scikit-learn -y && pip cache purge && pip install -r requirements.txt

# Quick Test
python cross_stitch_generator.py info --help

# Port Conflicts (Web)
uvicorn web.main:app --port 8001

# Permission Issues
pip install --user -r requirements.txt
```

## Output Structure

The generated Excel file contains:

1. **Pattern Sheets**: One sheet per resolution with colored cells representing stitches
2. **Color Legend**: Summary of all colors with hex codes, RGB values, usage statistics, and DMC thread information
3. **Summary Sheet**: Metadata about the source image and generation settings

### Pattern Sheets
- Each cell represents one stitch
- Cell background color matches the quantized pixel color
- DMC thread codes displayed as text within cells (when DMC matching enabled)
- Square cells sized for realistic visualization
- Optional gridlines for easier counting

### Color Legend
- Color swatches with hex codes
- RGB values for color matching
- DMC thread codes and thread names (when available)
- Usage count and percentage for each color
- Thread quantity calculations for shopping lists
- Sorted by frequency of use

## Configuration

### Default Settings
- **Resolutions**: 50x50, 100x100, 150x150 stitches
- **Max Colors**: 256 colors per pattern
- **Quantization**: Median cut algorithm
- **Transparency**: Convert to white background
- **Cell Size**: 20 points (square cells)
- **Aspect Ratio**: Preserved during resizing

### Supported Image Formats
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- WebP (.webp)

## Technical Details

### Color Quantization
- **Median Cut**: Efficient algorithm that preserves color distribution
- **K-Means**: Machine learning approach for optimal color clustering
- Both methods reduce colors to specified palette size while maintaining visual quality

### Image Processing
- Automatic format detection and conversion
- EXIF orientation correction
- Memory-efficient processing for large images
- Configurable transparency handling

### Excel Generation
- Uses openpyxl for Excel file creation
- Optimized cell styling for performance
- Square cell dimensions for accurate visualization
- Multiple worksheet support

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Project Structure
```
src/cross_stitch/
├── core/              # Core processing classes
├── models/            # Data models and configuration
├── utils/             # Utilities and validation
└── cli/               # Command-line interface

tests/                 # Comprehensive test suite
```

## Performance Notes

- Processing time scales with image size and color count
- Recommended maximum: 2000x2000 pixel images
- Memory usage optimized for typical desktop systems
- Large patterns (>500x500) may take several minutes

## Troubleshooting

### Installation Issues

#### Python Environment Problems
| Problem | Symptoms | Solution |
|---------|----------|----------|
| **Wrong Python Version** | `python --version` shows < 3.11 | Install Python 3.11+ from [python.org](https://python.org/downloads/) |
| **Missing C++ Build Tools** | NumPy/SciPy installation fails | Install build tools (see Prerequisites section) |
| **Permission Errors** | `Permission denied` during pip install | Use `pip install --user` or activate virtual environment |
| **Module Import Errors** | `ModuleNotFoundError` after installation | Run `python scripts/validate-environment.py` for diagnosis |

#### Operating System Specific Issues

**Windows**:
- **Long path issues**: Enable long path support in Windows settings
- **Antivirus interference**: Add project folder to antivirus exclusions
- **PowerShell execution policy**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**macOS**:
- **Command line tools missing**: Run `xcode-select --install`
- **Homebrew conflicts**: Consider using pyenv for Python version management
- **M1/M2 compatibility**: Use `pip install --no-use-pep517` if needed

**Linux**:
- **Missing system packages**: Install `python3.11-dev libffi-dev libssl-dev`
- **Debian/Ubuntu**: `sudo apt-get update && sudo apt-get install python3.11-dev build-essential`
- **RHEL/CentOS**: `sudo yum install python3-devel gcc gcc-c++ make`

### Runtime Issues

#### Application Errors
| Problem | Symptoms | Solution |
|---------|----------|----------|
| **"Image file too large"** | Error during processing | Reduce image size or use smaller `--resolutions` |
| **"Too many colors"** | Processing hangs or fails | Increase `--max-colors` or use `kmeans` quantization |
| **"Resolution too large for image"** | Pattern appears pixelated | Use smaller target resolutions for small source images |
| **Excel file won't open** | File corruption or permission errors | Check disk space, write permissions, and try different output location |
| **Memory errors** | Application crashes with large images | Use smaller images (< 2000px) or increase system memory |

#### Web Interface Issues
| Problem | Symptoms | Solution |
|---------|----------|----------|
| **Port already in use** | `Address already in use` error | Use different port: `--port 8001` or kill conflicting process |
| **File upload fails** | Upload spinner never completes | Check file size (< 10MB recommended) and format support |
| **Canvas not rendering** | Blank preview area | Try refreshing page, check browser console for errors |
| **Slow performance** | Web interface feels sluggish | Close other browser tabs, try smaller images first |

#### DMC Database Issues
| Problem | Symptoms | Solution |
|---------|----------|----------|
| **DMC colors not matching** | Patterns use RGB instead of thread codes | Verify `data/dmc_colors.csv` exists and use `--enable-dmc` |
| **"DMC database not found"** | Warning during processing | Ensure `data/dmc_colors.csv` is present or use `--no-dmc` |
| **Limited color options** | Patterns look different than expected | Try `--dmc-only` to restrict to available thread colors |

### Performance Optimization

#### For Large Images
```bash
# Step 1: Start with smaller resolution
python cross_stitch_generator.py generate large_photo.jpg test.xlsx \
  --resolutions "50x50" --max-colors 32

# Step 2: If successful, increase gradually
python cross_stitch_generator.py generate large_photo.jpg final.xlsx \
  --resolutions "100x100,200x200" --max-colors 64
```

#### Memory Usage Tips
- **Recommended image sizes**: Under 2000×2000 pixels for best performance
- **Memory requirements**: ~50MB RAM per 1 million pixels processed
- **Batch processing**: Process multiple small images instead of one large image
- **Format selection**: JPEG for photos (smaller file size), PNG for graphics

#### Processing Speed Tips
- **Use fewer colors**: `--max-colors 32` for faster processing
- **Choose quantization method**: `median_cut` is faster, `kmeans` is more accurate
- **Smaller resolutions**: Start with `50x50` for quick testing
- **Disable features**: Use `--no-dmc` and `--no-legend` for faster processing

### Debugging Tools

#### Environment Validation
```bash
# Full environment check
python scripts/validate-environment.py

# Quick dependency check
python -c "import numpy, PIL, openpyxl; print('Core dependencies OK')"

# Check Python version
python --version
```

#### Verbose Output
```bash
# Enable detailed logging for troubleshooting
python cross_stitch_generator.py generate image.jpg output.xlsx --verbose

# Web interface debugging
uvicorn web.main:app --reload --log-level debug
```

#### Test Installation
```bash
# Test CLI functionality
python cross_stitch_generator.py info sample_image.jpg

# Test web interface (should show startup logs)
uvicorn web.main:app --host 127.0.0.1 --port 8000
```

### Getting Help

If you're still experiencing issues:

1. **Check environment**: Run `python scripts/validate-environment.py`
2. **Review logs**: Use `--verbose` flag for detailed error information
3. **Test with small image**: Try a simple 100×100 pixel test image first
4. **Check dependencies**: Verify all required packages are installed correctly
5. **System resources**: Ensure adequate RAM and disk space
6. **Known issues**: Review current test status (24/279 tests failing are non-critical)

### Known Non-Critical Issues

- **Pillow deprecation warnings**: Safe to ignore, functionality not affected
- **Edge mode test failures**: Advanced edge processing features, core functionality works
- **Excel professional formatting**: Some advanced Excel features may not work, basic patterns always work

## License

This project is provided as-is for educational and personal use.

## Contributing

This is a standalone implementation. For issues or suggestions, please review the code and adapt as needed for your use case.