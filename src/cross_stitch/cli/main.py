"""Command-line interface for cross-stitch pattern generator."""

import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
import logging

from ..models import GeneratorConfig
from ..core import PatternGenerator
from ..utils import (
    CrossStitchError, ValidationError, ImageProcessingError,
    ColorQuantizationError, ExcelGenerationError, PatternGenerationError
)


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(levelname)s: %(message)s' if not verbose else '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def parse_resolutions(resolution_str: str) -> List[Tuple[int, int]]:
    """
    Parse resolution string into list of tuples.

    Args:
        resolution_str: String like "50x50,100x100,150x150"

    Returns:
        List of (width, height) tuples

    Raises:
        ValueError: If resolution format is invalid
    """
    resolutions = []

    for res in resolution_str.split(','):
        res = res.strip()
        if 'x' not in res:
            raise ValueError(f"Invalid resolution format: {res}. Use 'WIDTHxHEIGHT'")

        try:
            width_str, height_str = res.split('x')
            width = int(width_str)
            height = int(height_str)

            if width <= 0 or height <= 0:
                raise ValueError(f"Resolution dimensions must be positive: {res}")

            resolutions.append((width, height))

        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"Invalid resolution format: {res}. Use numbers only.")
            raise

    return resolutions


def progress_callback(message: str, progress: float) -> None:
    """Progress callback for pattern generation."""
    # Create simple progress bar
    bar_length = 30
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)

    # Format progress message
    percent = progress * 100
    print(f'\r{message} [{bar}] {percent:5.1f}%', end='', flush=True)

    if progress >= 1.0:
        print()  # New line when complete


def create_config_from_args(args) -> GeneratorConfig:
    """Create GeneratorConfig from command-line arguments."""
    config = GeneratorConfig()

    # Override default settings with command-line arguments
    if args.resolutions:
        config.resolutions = parse_resolutions(args.resolutions)

    if args.max_colors:
        config.max_colors = args.max_colors

    if args.quantization:
        config.quantization_method = args.quantization

    if args.transparency:
        config.handle_transparency = args.transparency

    if args.no_aspect_ratio:
        config.preserve_aspect_ratio = False

    if args.cell_size:
        config.excel_cell_size = args.cell_size

    if args.no_legend:
        config.include_color_legend = False

    if args.legend_name:
        config.legend_sheet_name = args.legend_name

    return config


def info_command(args) -> int:
    """Handle the info subcommand."""
    try:
        config = create_config_from_args(args)
        generator = PatternGenerator(config)

        print(f"Analyzing image: {args.image}")
        info = generator.get_processing_info(args.image)

        # Print source image information
        source = info['source_image']
        print(f"\nSource Image:")
        print(f"  Size: {source['size'][0]}x{source['size'][1]} pixels")
        print(f"  Mode: {source['mode']}")
        print(f"  Format: {source['format']}")
        print(f"  File Size: {source['file_size'] / 1024:.1f} KB")
        print(f"  Has Transparency: {source['has_transparency']}")

        # Print target resolutions
        print(f"\nTarget Resolutions:")
        for name, target in info['target_resolutions'].items():
            size = target['target_size']
            scale_x = target['scale_factor_x']
            scale_y = target['scale_factor_y']
            print(f"  {name}: {size[0]}x{size[1]} (scale: {scale_x:.2f}x, {scale_y:.2f}x)")

        # Print configuration
        config_info = info['config']
        print(f"\nConfiguration:")
        print(f"  Max Colors: {config_info['max_colors']}")
        print(f"  Quantization: {config_info['quantization_method']}")
        print(f"  Transparency: {config_info['transparency_handling']}")
        print(f"  Preserve Aspect: {config_info['preserve_aspect_ratio']}")

        # Print time estimates
        if args.estimate_time:
            estimates = generator.estimate_processing_time(args.image)
            print(f"\nEstimated Processing Time:")
            print(f"  Image Loading: {estimates['image_loading']:.1f}s")
            print(f"  Image Resizing: {estimates['image_resizing']:.1f}s")
            print(f"  Color Quantization: {estimates['color_quantization']:.1f}s")
            print(f"  Excel Generation: {estimates['excel_generation']:.1f}s")
            print(f"  Total: {estimates['total']:.1f}s")

        return 0

    except Exception as e:
        print(f"Error getting image info: {e}")
        return 1


def generate_command(args) -> int:
    """Handle the generate subcommand."""
    try:
        # Create configuration from arguments
        config = create_config_from_args(args)

        # Create generator
        generator = PatternGenerator(config)

        # Set up progress reporting if not quiet
        if not args.quiet:
            generator.set_progress_callback(progress_callback)

        print(f"Generating cross-stitch patterns from: {args.image}")
        if not args.quiet:
            print(f"Output file: {args.output}")

        # Generate patterns
        pattern_set = generator.generate_patterns(args.image, args.output)

        # Print summary
        if not args.quiet:
            print(f"\nGeneration Complete!")
            print(f"Patterns generated: {pattern_set.pattern_count}")
            for name, pattern in pattern_set.patterns.items():
                print(f"  {name}: {pattern.width}x{pattern.height} stitches, {pattern.unique_colors_used} colors")

            total_colors = pattern_set.get_total_unique_colors()
            print(f"Total unique colors across all patterns: {total_colors}")

        return 0

    except CrossStitchError as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate cross-stitch patterns from images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate patterns with default settings
  cross-stitch generate input.jpg output.xlsx

  # Custom resolutions and colors
  cross-stitch generate input.png output.xlsx --resolutions "30x30,60x60,120x120" --max-colors 128

  # Get image information before generating
  cross-stitch info input.jpg --estimate-time

  # Generate with custom transparency handling
  cross-stitch generate input.png output.xlsx --transparency white_background --verbose

Supported image formats: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP
        """
    )

    # Global options
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress progress output')

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate cross-stitch patterns')
    gen_parser.add_argument('image', help='Input image file path')
    gen_parser.add_argument('output', help='Output Excel file path')

    gen_parser.add_argument('--resolutions', '-r', type=str,
                            help='Target resolutions (e.g., "50x50,100x100,150x150")')
    gen_parser.add_argument('--max-colors', '-c', type=int,
                            help='Maximum number of colors (default: 256)')
    gen_parser.add_argument('--quantization', '-q', choices=['median_cut', 'kmeans'],
                            help='Color quantization method (default: median_cut)')
    gen_parser.add_argument('--transparency', '-t',
                            choices=['white_background', 'remove', 'preserve'],
                            help='Transparency handling (default: white_background)')
    gen_parser.add_argument('--no-aspect-ratio', action='store_true',
                            help='Do not preserve aspect ratio when resizing')
    gen_parser.add_argument('--cell-size', type=float,
                            help='Excel cell size in points (default: 20.0)')
    gen_parser.add_argument('--no-legend', action='store_true',
                            help='Do not include color legend sheet')
    gen_parser.add_argument('--legend-name', type=str,
                            help='Name for color legend sheet (default: "Color Legend")')

    # Info command
    info_parser = subparsers.add_parser('info', help='Get information about an image')
    info_parser.add_argument('image', help='Input image file path')
    info_parser.add_argument('--estimate-time', action='store_true',
                             help='Include processing time estimates')

    # Add the same configuration options to info command (for analysis)
    info_parser.add_argument('--resolutions', '-r', type=str,
                             help='Target resolutions for analysis')
    info_parser.add_argument('--max-colors', '-c', type=int,
                             help='Maximum number of colors for analysis')
    info_parser.add_argument('--quantization', choices=['median_cut', 'kmeans'],
                             help='Color quantization method for analysis')
    info_parser.add_argument('--transparency', choices=['white_background', 'remove', 'preserve'],
                             help='Transparency handling for analysis')
    info_parser.add_argument('--no-aspect-ratio', action='store_true',
                             help='Do not preserve aspect ratio for analysis')

    return parser


def main() -> int:
    """Main entry point for CLI."""
    parser = create_parser()

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)

    # Handle commands
    if args.command == 'generate':
        return generate_command(args)
    elif args.command == 'info':
        return info_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())