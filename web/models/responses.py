"""Response models for API endpoints."""
from pydantic import BaseModel
from typing import Optional


class AnalysisResult(BaseModel):
    """Result from image analysis (pre-generation check)."""
    width: int
    height: int
    has_transparency: bool
    estimated_colors: int
    texture_warning: Optional[str] = None
    resize_warning: Optional[str] = None


class ThreadInfo(BaseModel):
    """DMC thread information for legend."""
    dmc_code: str
    name: str
    hex_color: str
    stitch_count: int
    percentage: float


class PatternData(BaseModel):
    """Generated pattern data for frontend rendering."""
    width: int
    height: int
    palette: list[str]  # Hex colors indexed 0..N
    grid: list[int]  # Flat array of palette indices (row-major)
    threads: list[ThreadInfo]
    total_stitches: int