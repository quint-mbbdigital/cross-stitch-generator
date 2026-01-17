"""Request models with strict validation."""
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from enum import Enum


class QuantizationMethod(str, Enum):
    MEDIAN_CUT = "median_cut"
    KMEANS = "kmeans"


class EdgeMode(str, Enum):
    SMOOTH = "smooth"
    HARD = "hard"


class TransparencyMode(str, Enum):
    WHITE_BACKGROUND = "white_background"
    REMOVE = "remove"
    PRESERVE = "preserve"


class PatternConfig(BaseModel):
    """Configuration for pattern generation.

    This model maps 1:1 to the Alpine.js sidebar state.
    """
    resolution: int = Field(default=100, ge=25, le=300, description="Pattern size in stitches")
    max_colors: int = Field(default=64, ge=2, le=256, description="Maximum thread colors")
    quantization: QuantizationMethod = Field(default=QuantizationMethod.MEDIAN_CUT)
    edge_mode: EdgeMode = Field(default=EdgeMode.SMOOTH)
    transparency: TransparencyMode = Field(default=TransparencyMode.WHITE_BACKGROUND)
    min_color_percent: float = Field(default=1.0, ge=0.0, le=10.0, description="Noise threshold")
    enable_dmc: bool = Field(default=True, description="Match to DMC thread colors")
    dmc_only: bool = Field(default=False, description="Restrict to DMC palette only")

    @field_validator('resolution')
    @classmethod
    def resolution_must_be_reasonable(cls, v: int) -> int:
        if v > 200:
            # Warn but allow—will be slow
            pass
        return v