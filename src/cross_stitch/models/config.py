"""Configuration models for cross-stitch pattern generation."""

import os
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class GeneratorConfig:
    """Configuration options for pattern generation."""

    # Resolution settings
    resolutions: List[Tuple[int, int]] = field(
        default_factory=lambda: [(50, 50), (100, 100), (150, 150)]
    )

    # Color management
    max_colors: int = 256
    quantization_method: str = "median_cut"  # "median_cut", "kmeans"

    # Image processing
    preserve_aspect_ratio: bool = True
    handle_transparency: str = (
        "white_background"  # "white_background", "remove", "preserve"
    )
    edge_mode: str = "smooth"  # "smooth", "hard"
    min_color_percent: float = 0.0  # Merge colors below this percentage threshold
    max_merge_distance: float = 50.0  # Maximum RGB color distance for merging colors

    # Excel formatting
    excel_cell_size: float = 20.0  # points (width and height)
    include_color_legend: bool = True
    legend_sheet_name: str = "Color Legend"

    # Analysis settings
    check_for_texture: bool = True  # Check for problematic background textures

    # Output settings
    output_filename_template: str = "{base_name}_cross_stitch.xlsx"

    # DMC color matching settings
    enable_dmc: bool = True  # Enable DMC color matching by default when available
    dmc_only: bool = False  # Restrict quantization to existing DMC colors only
    dmc_palette_size: Optional[int] = None  # Limit to N most common DMC colors
    no_dmc: bool = False  # Explicitly disable DMC matching
    dmc_database: Optional[str] = None  # Path to custom DMC color database

    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.resolutions:
            raise ValueError("At least one resolution must be specified")

        for width, height in self.resolutions:
            if width <= 0 or height <= 0:
                raise ValueError(f"Invalid resolution: {width}x{height}")
            if width > 1000 or height > 1000:
                raise ValueError(
                    f"Resolution too large: {width}x{height} (max 1000x1000)"
                )

        if self.max_colors <= 0 or self.max_colors > 16777216:  # 2^24
            raise ValueError(
                f"max_colors must be between 1 and 16777216, got {self.max_colors}"
            )

        if self.quantization_method not in ["median_cut", "kmeans"]:
            raise ValueError(f"Unknown quantization method: {self.quantization_method}")

        if self.handle_transparency not in ["white_background", "remove", "preserve"]:
            raise ValueError(
                f"Invalid transparency handling: {self.handle_transparency}"
            )

        if self.edge_mode not in ["smooth", "hard"]:
            raise ValueError(f"Invalid edge_mode: {self.edge_mode}")

        if not (0.0 <= self.min_color_percent <= 100.0):
            raise ValueError(
                f"min_color_percent must be between 0 and 100, got {self.min_color_percent}"
            )

        if self.max_merge_distance <= 0:
            raise ValueError(
                f"max_merge_distance must be positive, got {self.max_merge_distance}"
            )

        if self.excel_cell_size <= 0:
            raise ValueError(
                f"excel_cell_size must be positive, got {self.excel_cell_size}"
            )

        # DMC validation
        if self.dmc_palette_size is not None and self.dmc_palette_size <= 0:
            raise ValueError(
                f"dmc_palette_size must be positive, got {self.dmc_palette_size}"
            )

        if self.dmc_database is not None:
            if not os.path.exists(self.dmc_database):
                raise ValueError(
                    f"DMC database file does not exist: {self.dmc_database}"
                )

    def get_resolution_name(self, width: int, height: int) -> str:
        """Generate a readable name for a resolution."""
        return f"{width}x{height}"

    def get_output_filename(self, input_path: str) -> str:
        """Generate output filename based on input path."""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        return self.output_filename_template.format(base_name=base_name)
