"""DMC floss color database loader."""

import csv
import os
from pathlib import Path
from typing import Dict, Optional

from ..models.color_palette import Color


def load_dmc_palette(csv_path: Optional[str] = None) -> Dict[str, Color]:
    """Load DMC floss color palette from CSV file.

    Args:
        csv_path: Path to DMC colors CSV file. If None, uses default data/dmc_colors.csv

    Returns:
        Dictionary mapping DMC codes to Color objects

    Raises:
        ValueError: If CSV format is invalid or RGB values are out of range
    """
    # Use default path if none provided
    if csv_path is None:
        # Default to data/dmc_colors.csv relative to project root
        # Go up from src/cross_stitch/data/ to project root, then to data/
        default_path = Path(__file__).parent.parent.parent.parent / "data" / "dmc_colors.csv"
        csv_path = str(default_path)

    # Return empty dict if file doesn't exist (graceful handling)
    if not os.path.exists(csv_path):
        return {}

    palette = {}
    required_columns = {'dmc_code', 'name', 'r', 'g', 'b', 'hex_code'}

    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Validate CSV format - check required columns exist
            if not required_columns.issubset(set(reader.fieldnames or [])):
                missing = required_columns - set(reader.fieldnames or [])
                raise ValueError(f"Invalid DMC CSV format. Missing columns: {missing}")

            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header line
                try:
                    # Extract values
                    dmc_code = row['dmc_code'].strip()
                    name = row['name'].strip()

                    # Skip empty rows
                    if not dmc_code:
                        continue

                    r = int(row['r'])
                    g = int(row['g'])
                    b = int(row['b'])

                    # Validate RGB values (Color constructor will also validate, but we want specific error message)
                    for component, comp_name in [(r, 'r'), (g, 'g'), (b, 'b')]:
                        if not 0 <= component <= 255:
                            raise ValueError(f"RGB values must be between 0 and 255. Got {comp_name}={component} for DMC {dmc_code}")

                    # Handle duplicates - use first occurrence (skip if already exists)
                    if dmc_code in palette:
                        continue

                    # Create Color object with DMC metadata
                    color = Color(
                        r=r,
                        g=g,
                        b=b,
                        name=name,
                        thread_code=dmc_code
                    )

                    palette[dmc_code] = color

                except (ValueError, KeyError) as e:
                    if "RGB values must be between 0 and 255" in str(e):
                        raise  # Re-raise our specific RGB validation error
                    # For other parsing errors, wrap with context
                    raise ValueError(f"Error parsing row {row_num} for DMC {row.get('dmc_code', 'UNKNOWN')}: {e}")

    except (IOError, OSError) as e:
        # File exists but couldn't be read - return empty dict (graceful handling)
        return {}

    return palette