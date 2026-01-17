"""API endpoints for pattern generation."""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from io import BytesIO
from pathlib import Path
import uuid
import logging

from web.models.requests import PatternConfig
from web.models.responses import AnalysisResult, PatternData, ThreadInfo
from web.utils.async_processing import process_upload, run_in_threadpool
from web.utils.memory_management import ephemeral_workspace, estimate_memory_usage

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

# In-memory job storage (ephemeral—Replit restarts clear this)
_jobs: dict[str, dict] = {}


@router.post("/upload", response_model=AnalysisResult)
async def upload_image(file: UploadFile = File(...)):
    """Upload and analyze image before generation."""
    logger.info(f"📤 Upload started - filename: {file.filename}, content_type: {file.content_type}")

    if not file.content_type or not file.content_type.startswith("image/"):
        logger.warning(f"❌ Invalid content type: {file.content_type}")
        raise HTTPException(400, "File must be an image")

    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    logger.info(f"📊 File size: {file_size_mb:.2f}MB")

    if len(contents) > 10 * 1024 * 1024:  # 10MB limit
        logger.warning(f"📁 File too large: {file_size_mb:.2f}MB > 10MB")
        raise HTTPException(413, "Image too large (max 10MB)")

    try:
        logger.info("🔄 Starting image processing...")
        image, analysis = await process_upload(contents)

        # Store image for later generation
        job_id = str(uuid.uuid4())
        _jobs[job_id] = {"image": image, "analysis": analysis}

        logger.info(f"✅ Upload successful - job_id: {job_id}")
        logger.info(f"📏 Image dimensions: {analysis.width}x{analysis.height}")
        logger.info(f"🎨 Estimated colors: {analysis.estimated_colors}")

        if analysis.resize_warning:
            logger.info(f"⚠️ Resize warning: {analysis.resize_warning}")
        if analysis.texture_warning:
            logger.info(f"⚠️ Texture warning: {analysis.texture_warning}")

        return JSONResponse(content={
            **analysis.model_dump(),
            "job_id": job_id
        })
    except Exception as e:
        logger.error(f"❌ Upload processing failed: {str(e)}", exc_info=True)
        raise HTTPException(400, f"Invalid image: {str(e)}")


@router.post("/generate/{job_id}")
async def generate_pattern(job_id: str, config: PatternConfig, request: Request):
    """Generate pattern from previously uploaded image."""
    logger.info(f"🎨 Pattern generation started - job_id: {job_id}")
    logger.info(f"⚙️ Config: {config.resolution}x{config.resolution}, {config.max_colors} colors, {config.quantization.value}")

    if job_id not in _jobs:
        logger.warning(f"❌ Job not found: {job_id}")
        raise HTTPException(404, "Upload expired or not found. Please re-upload image.")

    job = _jobs[job_id]
    image = job["image"]
    logger.info(f"📏 Processing image: {image.size[0]}x{image.size[1]}")

    # Memory check
    mem_estimate = estimate_memory_usage(config.resolution, config.resolution, config.max_colors)
    logger.info(f"🧠 Memory estimate: {mem_estimate['total_mb']}MB")

    if mem_estimate["total_mb"] > 500:  # 500MB limit for Replit
        logger.warning(f"❌ Memory limit exceeded: {mem_estimate['total_mb']}MB > 500MB")
        raise HTTPException(413, f"Pattern too complex ({mem_estimate['total_mb']}MB estimated). Reduce resolution or colors.")

    try:
        logger.info("🔄 Starting pattern generation...")
        pattern_data = await run_in_threadpool(
            _generate_pattern_sync,
            image,
            config
        )
        logger.info(f"✅ Pattern generated successfully - {pattern_data.width}x{pattern_data.height}, {len(pattern_data.palette)} colors")

        # Check if HTMX request (return HTML with OOB updates)
        if "hx-request" in request.headers:
            templates = Jinja2Templates(directory="web/templates")

            # Render legend content for OOB update
            legend_html = templates.get_template("components/legend_content.html").render(
                pattern_data=pattern_data
            )

            # Return HTML response with legend and stats OOB updates
            html_response = f"""
                <div id="pattern-data"
                     hx-swap-oob="true"
                     data-pattern-json='{pattern_data.model_dump_json()}'>
                </div>
                <div id="legend-content" hx-swap-oob="true" data-htmx-updated="true">
                    {legend_html}
                </div>
                <div id="legend-stats-content" hx-swap-oob="true">
                    {len(pattern_data.threads) if pattern_data.threads else 0} colors •
                    {pattern_data.total_stitches:,} stitches
                </div>
            """

            return HTMLResponse(content=html_response)

        # JSON response for non-HTMX requests
        return pattern_data
    except Exception as e:
        logger.error(f"❌ Pattern generation failed: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Generation failed: {str(e)}")


def _generate_pattern_sync(image, config: PatternConfig) -> PatternData:
    """Synchronous pattern generation (runs in thread pool).

    This wraps the existing CLI logic without modifying it.
    """
    from PIL import Image

    # Import existing modules
    from src.cross_stitch.core.color_manager import ColorManager
    from src.cross_stitch.core.dmc_matcher import DMCMatcher
    from src.cross_stitch.models.config import GeneratorConfig

    # Resize to target resolution
    target_size = (config.resolution, config.resolution)
    resample = Image.Resampling.NEAREST if config.edge_mode.value == "hard" else Image.Resampling.LANCZOS

    # Resize to exact target size (allows both enlarging and shrinking)
    image = image.resize(target_size, resample)

    # Handle transparency
    if image.mode == 'RGBA' and config.transparency.value == "white_background":
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    else:
        image = image.convert('RGB')

    # Create GeneratorConfig from PatternConfig
    generator_config = GeneratorConfig(
        resolutions=[(config.resolution, config.resolution)],
        max_colors=config.max_colors,
        quantization_method=config.quantization.value,
        edge_mode=config.edge_mode.value,
        handle_transparency=config.transparency.value,
        min_color_percent=config.min_color_percent,
        enable_dmc=config.enable_dmc,
        dmc_only=config.dmc_only
    )

    # Quantize colors using proper ColorManager API
    color_manager = ColorManager(generator_config)
    palette, color_indices = color_manager.quantize_image(image)

    # Convert palette to hex format
    palette_hex = [color.hex_code for color in palette.colors]

    # Convert color_indices array to flat list for grid
    grid = color_indices.flatten().tolist()

    # DMC matching (already handled by ColorManager if enabled)
    threads = []
    if config.enable_dmc and palette.colors:
        # Count usage for each color in the pattern
        color_counts = {}
        for color_idx in grid:
            color_counts[color_idx] = color_counts.get(color_idx, 0) + 1

        total = len(grid)
        for idx, color in enumerate(palette.colors):
            count = color_counts.get(idx, 0)
            if count > 0:
                # Check if color has DMC info (from ColorManager DMC matching)
                if hasattr(color, 'dmc_code') and color.dmc_code:
                    threads.append(ThreadInfo(
                        dmc_code=color.dmc_code,
                        name=getattr(color, 'dmc_name', f"DMC {color.dmc_code}"),
                        hex_color=color.hex_code,
                        stitch_count=count,
                        percentage=round(count / total * 100, 1)
                    ))
                else:
                    # Fallback: create thread info without DMC code
                    threads.append(ThreadInfo(
                        dmc_code="",
                        name=f"Color {idx + 1}",
                        hex_color=color.hex_code,
                        stitch_count=count,
                        percentage=round(count / total * 100, 1)
                    ))

    return PatternData(
        width=image.size[0],
        height=image.size[1],
        palette=palette_hex,
        grid=grid,
        threads=sorted(threads, key=lambda t: -t.stitch_count),
        total_stitches=len(grid)
    )


@router.get("/download/{job_id}")
async def download_excel(
    job_id: str,
    resolution: int = 50,
    max_colors: int = 16,
    quantization: str = "median_cut",
    edge_mode: str = "smooth",
    transparency: str = "white_background",
    min_color_percent: float = 1.0,
    enable_dmc: bool = False,
    dmc_only: bool = False
):
    """Generate and download Excel file.

    CRITICAL: Uses TemporaryDirectory to prevent disk overflow on Replit.
    All file operations use context managers for guaranteed cleanup.
    """
    # Create PatternConfig from query parameters
    from web.models.requests import PatternConfig, QuantizationMethod, EdgeMode, TransparencyMode

    config = PatternConfig(
        resolution=resolution,
        max_colors=max_colors,
        quantization=QuantizationMethod(quantization),
        edge_mode=EdgeMode(edge_mode),
        transparency=TransparencyMode(transparency),
        min_color_percent=min_color_percent,
        enable_dmc=enable_dmc,
        dmc_only=dmc_only
    )

    if job_id not in _jobs:
        raise HTTPException(404, "Upload expired")

    job = _jobs[job_id]
    image = job["image"]

    # Generate Excel in ephemeral workspace
    with ephemeral_workspace() as workspace:
        output_path = workspace / "pattern.xlsx"

        # Use existing CLI Excel generator via thread pool
        def _generate_excel():
            from src.cross_stitch.core.excel_generator import ExcelGenerator
            from src.cross_stitch.core.color_manager import ColorManager
            from src.cross_stitch.models.config import GeneratorConfig
            from src.cross_stitch.models.pattern import CrossStitchPattern, PatternSet
            from pathlib import Path
            from PIL import Image as PILImage

            # Process image (same as generate endpoint)
            target_size = (config.resolution, config.resolution)
            resample = PILImage.Resampling.NEAREST if config.edge_mode.value == "hard" else PILImage.Resampling.LANCZOS

            work_image = image.copy()
            work_image.thumbnail(target_size, resample)

            if work_image.mode == 'RGBA' and config.transparency.value == "white_background":
                background = PILImage.new('RGB', work_image.size, (255, 255, 255))
                background.paste(work_image, mask=work_image.split()[3])
                work_image = background
            else:
                work_image = work_image.convert('RGB')

            # Create GeneratorConfig from PatternConfig
            generator_config = GeneratorConfig(
                resolutions=[(config.resolution, config.resolution)],
                max_colors=config.max_colors,
                quantization_method=config.quantization.value,
                edge_mode=config.edge_mode.value,
                handle_transparency=config.transparency.value,
                min_color_percent=config.min_color_percent,
                enable_dmc=config.enable_dmc,
                dmc_only=config.dmc_only
            )

            # Quantize using proper ColorManager API
            color_manager = ColorManager(generator_config)
            palette, color_indices = color_manager.quantize_image(work_image)

            # Create CrossStitchPattern object
            resolution_name = f"{config.resolution}x{config.resolution}"
            pattern = CrossStitchPattern(
                width=work_image.size[0],
                height=work_image.size[1],
                colors=color_indices,
                palette=palette,
                resolution_name=resolution_name
            )

            # Create a temporary placeholder image file for PatternSet validation
            temp_image_path = output_path.parent / "temp_uploaded_image.jpg"
            work_image.save(temp_image_path, format='JPEG')

            # Create PatternSet object
            pattern_set = PatternSet(
                patterns={resolution_name: pattern},
                source_image_path=temp_image_path,
                metadata={
                    "original_size": f"{work_image.size[0]}x{work_image.size[1]}",
                    "colors_used": len(palette.colors),
                    "quantization": config.quantization.value,
                    "created_at": "web_interface"
                }
            )

            # Generate Excel using existing CLI logic
            excel_generator = ExcelGenerator(generator_config)
            excel_generator.generate_excel_file(pattern_set, str(output_path))

            return output_path

        await run_in_threadpool(_generate_excel)

        # Read file into memory before workspace cleanup
        with open(output_path, 'rb') as f:
            file_bytes = BytesIO(f.read())

        # Return from memory (workspace auto-cleans on context exit)
        return StreamingResponse(
            file_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=cross_stitch_pattern.xlsx"}
        )