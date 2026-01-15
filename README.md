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

## Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

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

### Common Issues

1. **"Image file too large"**: Reduce image size or use a smaller resolution
2. **"Too many colors"**: Increase `--max-colors` or use more aggressive quantization
3. **"Resolution too large for image"**: Use smaller target resolutions for small images
4. **Excel file won't open**: Ensure sufficient disk space and write permissions

### Performance Tips

- Use JPEG format for photographs (smaller file size)
- Use PNG format for graphics with few colors
- Start with lower resolutions for large images
- Reduce `--max-colors` for faster processing

## License

This project is provided as-is for educational and personal use.

## Contributing

This is a standalone implementation. For issues or suggestions, please review the code and adapt as needed for your use case.