# Cross-Stitch Pattern Generator

A Python application that converts image files into Excel-based cross-stitch patterns with multiple resolution tabs.

## Features

- **Multi-Resolution Support**: Generate patterns at 50x50, 100x100, and 150x150 stitches (configurable)
- **Smart Color Quantization**: Uses median cut or k-means algorithms to reduce colors to manageable palettes
- **Excel Output**: Creates `.xlsx` files where each cell represents one stitch with accurate background colors
- **Square Cells**: Properly sized cells for realistic pattern visualization
- **Color Legend**: Optional color palette summary with usage statistics
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

## Command-Line Options

### Generate Command

- `--resolutions` / `-r`: Target resolutions (e.g., "50x50,100x100,150x150")
- `--max-colors` / `-c`: Maximum number of colors (default: 256)
- `--quantization`: Color quantization method (`median_cut` or `kmeans`)
- `--transparency`: Transparency handling (`white_background`, `remove`, `preserve`)
- `--no-aspect-ratio`: Disable aspect ratio preservation
- `--cell-size`: Excel cell size in points (default: 20.0)
- `--no-legend`: Skip color legend sheet
- `--legend-name`: Custom name for legend sheet

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

## Output Structure

The generated Excel file contains:

1. **Pattern Sheets**: One sheet per resolution with colored cells representing stitches
2. **Color Legend**: Summary of all colors with hex codes, RGB values, and usage statistics
3. **Summary Sheet**: Metadata about the source image and generation settings

### Pattern Sheets
- Each cell represents one stitch
- Cell background color matches the quantized pixel color
- Square cells sized for realistic visualization
- Optional gridlines for easier counting

### Color Legend
- Color swatches with hex codes
- RGB values for color matching
- Usage count and percentage for each color
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