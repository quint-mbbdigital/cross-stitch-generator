# Cross-Stitch Generator: Web Frontend Development Plan

**Project:** Modern Atelier Web Interface  
**Target Environment:** Replit + GitHub Integration  
**Agent Optimization:** Claude Code / Agentic Workflows  
**Version:** 2.0 (Claude-Native)

---

## How to Use This Document

This plan is structured for **agentic task execution**. Each phase contains:

1. **CONTEXT** — Everything Claude needs to understand the task (no external references required)
2. **TASKS** — Atomic work units with explicit file paths and complete code samples
3. **CHECKPOINT** — Verifiable success criteria before proceeding
4. **HANDOFF** — State summary for the next phase

**Agent Directive:** Execute phases sequentially. Do not proceed to Phase N+1 until Phase N checkpoint passes.

---

## Parallelization Guide

For multi-agent execution, use this dependency graph. Tasks marked `[P]` can run in parallel. Tasks marked `[I]` are integration points requiring prior tasks.

```
PHASE 0: Sequential (setup)
  0.1 → 0.2 → 0.3

PHASE 1: Parallel Foundation
  ┌─────────────────────────────────────────────┐
  │  [P] 1.2 Models    [P] 1.3 Utils            │
  │         │                │                  │
  │         └────────┬───────┘                  │
  │                  │                          │
  │  [P] 1.4 API Routes    [P] 1.5 Frontend     │
  │         │                    │              │
  │         └────────┬───────────┘              │
  │                  ▼                          │
  │         [I] 1.6 main.py (integration)       │
  └─────────────────────────────────────────────┘

PHASE 2: Parallel Templates
  ┌─────────────────────────────────────────────┐
  │  [P] 2.1 base.html (must complete first)    │
  │              │                              │
  │  ┌───────────┼───────────┬────────────┐     │
  │  ▼           ▼           ▼            ▼     │
  │ [P]2.3    [P]2.4      [P]2.5      [P]CSS    │
  │ sidebar   canvas      legend      custom    │
  │  │           │           │            │     │
  │  └───────────┴───────────┴────────────┘     │
  │                  │                          │
  │                  ▼                          │
  │         [I] 2.2 index.html (integration)    │
  └─────────────────────────────────────────────┘

PHASE 3: Parallel JavaScript
  ┌─────────────────────────────────────────────┐
  │  [P] pattern-store.js                       │
  │  [P] upload-handler.js                      │
  │  [P] interactions.js                        │
  │         │                                   │
  │         ▼                                   │
  │  [I] Update base.html with script tags      │
  └─────────────────────────────────────────────┘

PHASE 4: Sequential (polish)
  4.1 → 4.2 → 4.3 → 4.4 → 4.5
```

### Sub-Agent Task Assignments

For Workflow 3 (Parallel Swarm), assign agents as follows:

| Agent ID | Phase 1 Task | Phase 2 Task | Phase 3 Task |
|----------|--------------|--------------|--------------|
| Worker-1 | 1.2 Models | 2.1 base.html | pattern-store.js |
| Worker-2 | 1.3 Utils | 2.3 sidebar | upload-handler.js |
| Worker-3 | 1.4 API Routes | 2.4 canvas | interactions.js |
| Worker-4 | 1.5 Frontend | 2.5 legend | — |
| Integrator | 1.6 main.py | 2.2 index.html | Update base.html |

### Completion Markers

Each sub-agent should create a marker file on completion:

```bash
# Agent creates on success:
echo "COMPLETE $(date -Iseconds)" > .completion/{task-id}.done

# Integrator waits for:
while [ $(ls .completion/*.done 2>/dev/null | wc -l) -lt 4 ]; do
    sleep 2
done
```

---

## Peer Review Integration (v2.1)

The following refinements were integrated based on technical peer review:

| Review Point | Resolution | Location |
|--------------|------------|----------|
| Early texture detection | Added call to existing `TextureDetector` in `process_upload()` | Phase 1.3 |
| Stateless ephemeral workspace | Fully implemented `download_excel` with `BytesIO` + `TemporaryDirectory` | Phase 1.4 |
| Canvas performance (40k+ cells) | Implemented `Uint8ClampedArray` + `ImageData` bulk rendering | Phase 3.1 |
| HTMX OOB for "Magic Moment" | Added `/generate/{job_id}/htmx` endpoint with simultaneous swaps | Phase 4.0 |

---

## Current State

```
Repository: https://github.com/quint-mbbdigital/cross-stitch-generator

Existing Structure:
├── src/cross_stitch/       # Core Python logic (DO NOT MODIFY)
│   ├── core/               # Processing classes
│   ├── models/             # Data models
│   ├── utils/              # Utilities
│   └── cli/                # Command-line interface
├── tests/                  # Test suite (92/94 passing)
├── data/                   # DMC thread database
├── cross_stitch_generator.py  # CLI entry point
├── requirements.txt        # Dependencies
└── CLAUDE.md              # Agent instructions
```

**What Works:** Full CLI pipeline—image upload → color quantization → DMC matching → Excel export  
**What's Missing:** Web interface for non-technical users

---

## Phase 0: Repository Preparation

### CONTEXT

Before adding web infrastructure, ensure the repository is ready for web development and Replit deployment.

### TASKS

#### 0.1 Update `CLAUDE.md` with Web Development Context

**File:** `CLAUDE.md` (append to existing)

```markdown
## Web Development Context

### Stack
- Backend: FastAPI + Jinja2
- Frontend: HTMX + Alpine.js + Tailwind CSS + DaisyUI
- Deployment: Replit (ephemeral filesystem)

### Architecture Principles
- **Non-blocking I/O**: Use `run_in_threadpool` for CPU-bound image processing
- **Stateless Design**: Accept `BytesIO` streams, not file paths
- **Memory Management**: Pre-resize images > 2000px to prevent OOM

### File Conventions
- Web code lives in `web/` directory
- Templates use Jinja2 blocks for layout inheritance
- Static assets served from `web/static/`

### Testing Commands
```bash
# Run all tests
pytest tests/ -v

# Run web-specific tests
pytest tests/test_web/ -v

# Start development server
uvicorn web.main:app --reload --host 0.0.0.0 --port 8000
```

### Critical Constraints
- DO NOT modify `src/cross_stitch/` core logic
- All image processing must be wrapped in `run_in_threadpool`
- Temporary files must use `TemporaryDirectory` context managers
```

#### 0.2 Create Web Requirements File

**File:** `requirements-web.txt`

```
# Web Framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6
jinja2>=3.1.2

# Async Support
aiofiles>=23.2.1

# Existing Dependencies (from requirements.txt)
-r requirements.txt
```

#### 0.3 Create Replit Configuration

**File:** `.replit`

```toml
run = "uvicorn web.main:app --host 0.0.0.0 --port 8000"
entrypoint = "web/main.py"

[env]
PYTHONPATH = "${REPL_HOME}"

[nix]
channel = "stable-24_05"

[deployment]
run = ["uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "8000"]

[[ports]]
localPort = 8000
externalPort = 80
```

**File:** `replit.nix`

```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
  ];
}
```

### CHECKPOINT

```bash
# Verify files exist
ls -la CLAUDE.md requirements-web.txt .replit replit.nix

# Verify requirements parse correctly
pip install --dry-run -r requirements-web.txt
```

**Pass Criteria:** All files exist, no pip resolution errors.

### HANDOFF

Repository is configured for web development. Replit can import and run the project.

---

## Phase 1: FastAPI Foundation

### CONTEXT

Create the API layer that wraps existing CLI functionality. The API must be non-blocking and memory-efficient.

**Design Constraint:** The existing `src/cross_stitch/` modules expect file paths. We must adapt to `BytesIO` streams without modifying core logic.

### TASKS

#### 1.1 Create Web Directory Structure

```bash
mkdir -p web/routes web/models web/utils web/templates/components web/static/css web/static/js web/static/icons
mkdir -p .completion  # For sub-agent coordination
touch web/__init__.py web/routes/__init__.py web/models/__init__.py web/utils/__init__.py
```

#### 1.2 Create Pydantic Models `[P]` — *Can run in parallel*

**File:** `web/models/requests.py`

```python
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
```

**File:** `web/models/responses.py`

```python
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
```

#### 1.3 Create Async Processing Utilities `[P]` — *Can run in parallel*

**File:** `web/utils/async_processing.py`

```python
"""Async wrappers for CPU-bound operations."""
import asyncio
from io import BytesIO
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from PIL import Image

# Thread pool for CPU-bound work
_executor = ThreadPoolExecutor(max_workers=2)


async def run_in_threadpool(func, *args, **kwargs):
    """Run a blocking function in a thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, partial(func, *args, **kwargs))


def resize_if_needed(image: Image.Image, max_dimension: int = 2000) -> tuple[Image.Image, Optional[str]]:
    """Resize image if it exceeds max dimension. Returns (image, warning_message)."""
    w, h = image.size
    if max(w, h) <= max_dimension:
        return image, None
    
    scale = max_dimension / max(w, h)
    new_size = (int(w * scale), int(h * scale))
    resized = image.resize(new_size, Image.Resampling.LANCZOS)
    
    warning = f"Image resized from {w}×{h} to {new_size[0]}×{new_size[1]} for memory efficiency"
    return resized, warning


async def process_upload(file_bytes: bytes) -> tuple[Image.Image, AnalysisResult]:
    """Process uploaded file bytes into PIL Image with analysis.
    
    CRITICAL: This function performs early texture detection using existing
    CLI logic to warn users about complex backgrounds BEFORE generation.
    """
    from web.models.responses import AnalysisResult
    
    def _process():
        image = Image.open(BytesIO(file_bytes))
        image, resize_warning = resize_if_needed(image)
        
        # Convert to RGB for analysis
        if image.mode == 'RGBA':
            has_transparency = True
        else:
            has_transparency = False
            
        # Estimate color count (sample for speed)
        sample = image.copy()
        sample.thumbnail((100, 100))
        colors = sample.convert('RGB').getcolors(maxcolors=1000)
        estimated_colors = len(colors) if colors else 1000
        
        # TEXTURE DETECTION: Use existing CLI logic for background analysis
        # This implements the UI-UX "User Warning" requirement
        texture_warning = None
        try:
            from src.cross_stitch.core.texture_detector import TextureDetector
            detector = TextureDetector()
            analysis = detector.analyze(image)
            
            if analysis.has_complex_background:
                texture_warning = (
                    f"Complex background detected ({analysis.texture_score:.0%} texture density). "
                    "Consider using 'Hard' edge mode or pre-processing your image to remove the background."
                )
            elif analysis.has_gradient_background:
                texture_warning = (
                    "Gradient background detected. This may result in many similar thread colors. "
                    "Consider increasing the color cleanup threshold."
                )
        except ImportError:
            # TextureDetector not available - skip warning
            pass
        except Exception as e:
            # Don't fail upload on texture detection errors
            pass
        
        return image, AnalysisResult(
            width=image.size[0],
            height=image.size[1],
            has_transparency=has_transparency,
            estimated_colors=estimated_colors,
            texture_warning=texture_warning,
            resize_warning=resize_warning
        )
    
    return await run_in_threadpool(_process)
```

**File:** `web/utils/memory_management.py`

```python
"""Memory and temporary file management for Replit environment."""
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from pathlib import Path
import shutil


@contextmanager
def ephemeral_workspace():
    """Create a temporary workspace that auto-cleans on exit."""
    with TemporaryDirectory(prefix="cross_stitch_") as tmpdir:
        workspace = Path(tmpdir)
        yield workspace
        # Cleanup is automatic via context manager


def estimate_memory_usage(width: int, height: int, colors: int) -> int:
    """Estimate peak memory usage in MB for pattern generation."""
    # Rough estimate: image data + quantization + output
    pixels = width * height
    image_mb = (pixels * 4) / (1024 * 1024)  # RGBA
    quant_mb = (pixels * colors * 4) / (1024 * 1024)  # Distance matrix
    return int(image_mb + quant_mb + 50)  # 50MB overhead
```

#### 1.4 Create Core API Routes `[P]` — *Can run in parallel*

**File:** `web/routes/api.py`

```python
"""API endpoints for pattern generation."""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse, HTMLResponse
from io import BytesIO
from pathlib import Path
import uuid

from web.models.requests import PatternConfig
from web.models.responses import AnalysisResult, PatternData, ThreadInfo
from web.utils.async_processing import process_upload, run_in_threadpool
from web.utils.memory_management import ephemeral_workspace, estimate_memory_usage

router = APIRouter(prefix="/api", tags=["api"])

# In-memory job storage (ephemeral—Replit restarts clear this)
_jobs: dict[str, dict] = {}


@router.post("/upload", response_model=AnalysisResult)
async def upload_image(file: UploadFile = File(...)):
    """Upload and analyze image before generation."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(413, "Image too large (max 10MB)")
    
    try:
        image, analysis = await process_upload(contents)
        # Store image for later generation
        job_id = str(uuid.uuid4())
        _jobs[job_id] = {"image": image, "analysis": analysis}
        
        return JSONResponse(content={
            **analysis.model_dump(),
            "job_id": job_id
        })
    except Exception as e:
        raise HTTPException(400, f"Invalid image: {str(e)}")


@router.post("/generate/{job_id}")
async def generate_pattern(job_id: str, config: PatternConfig):
    """Generate pattern from previously uploaded image."""
    if job_id not in _jobs:
        raise HTTPException(404, "Upload expired or not found. Please re-upload image.")
    
    job = _jobs[job_id]
    image = job["image"]
    
    # Memory check
    mem_estimate = estimate_memory_usage(config.resolution, config.resolution, config.max_colors)
    if mem_estimate > 500:  # 500MB limit for Replit
        raise HTTPException(413, f"Pattern too complex ({mem_estimate}MB estimated). Reduce resolution or colors.")
    
    try:
        pattern_data = await run_in_threadpool(
            _generate_pattern_sync,
            image,
            config
        )
        return pattern_data
    except Exception as e:
        raise HTTPException(500, f"Generation failed: {str(e)}")


def _generate_pattern_sync(image, config: PatternConfig) -> PatternData:
    """Synchronous pattern generation (runs in thread pool).
    
    This wraps the existing CLI logic without modifying it.
    """
    from PIL import Image
    
    # Import existing modules
    from src.cross_stitch.core.quantizer import ColorQuantizer
    from src.cross_stitch.core.dmc_matcher import DMCMatcher
    from src.cross_stitch.models.config import ProcessingConfig
    
    # Resize to target resolution
    target_size = (config.resolution, config.resolution)
    resample = Image.Resampling.NEAREST if config.edge_mode.value == "hard" else Image.Resampling.LANCZOS
    
    # Preserve aspect ratio
    image.thumbnail(target_size, resample)
    
    # Handle transparency
    if image.mode == 'RGBA' and config.transparency.value == "white_background":
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    else:
        image = image.convert('RGB')
    
    # Quantize colors
    quantizer = ColorQuantizer(method=config.quantization.value)
    quantized = quantizer.quantize(image, config.max_colors)
    
    # Get palette and grid
    palette = quantized.getpalette()[:config.max_colors * 3]
    palette_hex = [f"#{palette[i]:02x}{palette[i+1]:02x}{palette[i+2]:02x}" 
                   for i in range(0, len(palette), 3)]
    
    # Convert to indexed grid
    pixels = list(quantized.getdata())
    
    # DMC matching
    threads = []
    if config.enable_dmc:
        matcher = DMCMatcher()
        color_counts = {}
        for p in pixels:
            color_counts[p] = color_counts.get(p, 0) + 1
        
        total = len(pixels)
        for idx, hex_color in enumerate(palette_hex):
            count = color_counts.get(idx, 0)
            if count > 0:
                dmc = matcher.find_closest(hex_color)
                threads.append(ThreadInfo(
                    dmc_code=dmc.code,
                    name=dmc.name,
                    hex_color=hex_color,
                    stitch_count=count,
                    percentage=round(count / total * 100, 1)
                ))
    
    return PatternData(
        width=image.size[0],
        height=image.size[1],
        palette=palette_hex,
        grid=pixels,
        threads=sorted(threads, key=lambda t: -t.stitch_count),
        total_stitches=len(pixels)
    )


@router.get("/download/{job_id}")
async def download_excel(job_id: str, config: PatternConfig):
    """Generate and download Excel file.
    
    CRITICAL: Uses TemporaryDirectory to prevent disk overflow on Replit.
    All file operations use context managers for guaranteed cleanup.
    """
    if job_id not in _jobs:
        raise HTTPException(404, "Upload expired")
    
    job = _jobs[job_id]
    image = job["image"]
    
    # Generate Excel in ephemeral workspace
    with ephemeral_workspace() as workspace:
        output_path = workspace / "pattern.xlsx"
        
        # Use existing CLI Excel writer via thread pool
        def _generate_excel():
            from src.cross_stitch.core.excel_writer import ExcelWriter
            from src.cross_stitch.core.quantizer import ColorQuantizer
            from src.cross_stitch.core.dmc_matcher import DMCMatcher
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
            
            # Quantize
            quantizer = ColorQuantizer(method=config.quantization.value)
            quantized = quantizer.quantize(work_image, config.max_colors)
            
            # Write Excel using existing CLI logic
            writer = ExcelWriter(
                enable_dmc=config.enable_dmc,
                dmc_only=config.dmc_only
            )
            writer.write(quantized, str(output_path))
            
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
```

#### 1.5 Create Frontend Routes `[P]` — *Can run in parallel*

**File:** `web/routes/frontend.py`

```python
"""Frontend template routes."""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/")
async def index(request: Request):
    """Serve main application interface."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Cross-Stitch Pattern Generator"
    })
```

#### 1.6 Create FastAPI Application Entry Point `[I]` — *Integration: requires 1.2-1.5*

**File:** `web/main.py`

```python
"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from web.routes import api, frontend

app = FastAPI(
    title="Cross-Stitch Generator",
    description="Convert images to cross-stitch patterns",
    version="1.0.0"
)

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include routers
app.include_router(api.router)
app.include_router(frontend.router)


@app.get("/health")
async def health_check():
    """Health check endpoint for Replit."""
    return {"status": "healthy"}
```

### CHECKPOINT

```bash
# Install dependencies
pip install -r requirements-web.txt

# Start server
uvicorn web.main:app --reload &
sleep 3

# Test health endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Test upload endpoint (with test image)
curl -X POST http://localhost:8000/api/upload \
  -F "file=@tests/fixtures/test_image.png" \
  | python -m json.tool
# Expected: JSON with width, height, job_id

# Kill server
pkill -f uvicorn
```

**Pass Criteria:** Health endpoint returns 200, upload returns valid JSON with `job_id`.

### HANDOFF

API layer complete. FastAPI wraps existing CLI logic with non-blocking I/O. Ready for frontend templates.

---

## Phase 2: Modern Atelier UI Templates

### CONTEXT

Implement the "Modern Atelier" interface using server-side templates. The aesthetic is defined by:

- **Chromatic Restraint:** Cold utility colors (zinc, slate, indigo)
- **High Data Density:** Maximum information, minimum clutter
- **Split-Pane Layout:** 320px sidebar (configuration) + fluid canvas (visualization)

**Color Palette:**
| Role | Color | Tailwind Class |
|------|-------|----------------|
| Canvas | `#FFFFFF` | `bg-white` |
| Surface | `#F8FAFC` | `bg-slate-50` |
| Primary Text | `#1E293B` | `text-slate-800` |
| Secondary Text | `#64748B` | `text-slate-500` |
| Accent | `#4F46E5` | `bg-indigo-600` |
| Border | `#E2E8F0` | `border-slate-200` |

**Typography:** Inter font, light headers, regular body, uppercase labels.

### TASKS

#### 2.1 Create Base Template `[P]` — *Must complete before 2.3-2.5*

**File:** `web/templates/base.html`

```html
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Cross-Stitch Generator{% endblock %}</title>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    
    <!-- Tailwind CSS + DaisyUI -->
    <link href="https://cdn.jsdelivr.net/npm/daisyui@4.7.2/dist/full.min.css" rel="stylesheet" type="text/css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'system-ui', 'sans-serif'],
                    },
                },
            },
            daisyui: {
                themes: ["light"],
            },
        }
    </script>
    
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    
    <!-- Alpine.js -->
    <script defer src="https://unpkg.com/alpinejs@3.13.5/dist/cdn.min.js"></script>
    
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@0.312.0/dist/umd/lucide.min.js"></script>
    
    <!-- Custom Styles -->
    <style>
        body { font-family: 'Inter', sans-serif; }
        
        /* Aida cloth grid pattern */
        .canvas-grid {
            background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
            background-size: 20px 20px;
        }
        
        /* Data labels */
        .label-data {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 500;
            color: #64748b;
        }
        
        /* HTMX loading indicator */
        .htmx-indicator {
            opacity: 0;
            transition: opacity 200ms ease-in;
        }
        .htmx-request .htmx-indicator {
            opacity: 1;
        }
        .htmx-request.htmx-indicator {
            opacity: 1;
        }
        
        /* Smooth transitions for panel swaps */
        .pattern-fade-in {
            animation: fadeIn 0.3s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.98); }
            to { opacity: 1; transform: scale(1); }
        }
    </style>
    
    {% block head %}{% endblock %}
</head>
<body class="h-full bg-white font-sans antialiased" x-data="appState()">
    {% block body %}{% endblock %}
    
    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        // Alpine.js application state
        function appState() {
            return {
                // UI State
                sidebarOpen: true,
                viewMode: 'color', // 'color' | 'symbol'
                showLegend: false,
                zoom: 1,
                
                // Configuration State (maps 1:1 to PatternConfig Pydantic model)
                config: {
                    resolution: 100,
                    max_colors: 64,
                    quantization: 'median_cut',
                    edge_mode: 'smooth',
                    transparency: 'white_background',
                    min_color_percent: 1.0,
                    enable_dmc: true,
                    dmc_only: false,
                },
                
                // Application State
                jobId: null,
                hasImage: false,
                isGenerating: false,
                patternData: null,
                
                // Methods
                toggleSidebar() {
                    this.sidebarOpen = !this.sidebarOpen;
                },
                
                setViewMode(mode) {
                    this.viewMode = mode;
                    if (this.patternData) {
                        this.$dispatch('render-pattern', { mode });
                    }
                },
                
                zoomIn() {
                    this.zoom = Math.min(this.zoom * 1.25, 5);
                },
                
                zoomOut() {
                    this.zoom = Math.max(this.zoom / 1.25, 0.25);
                },
                
                resetZoom() {
                    this.zoom = 1;
                },
            };
        }
    </script>
    
    {% block scripts %}{% endblock %}
</body>
</html>
```

#### 2.2 Create Main Index Template `[I]` — *Integration: requires 2.1, 2.3-2.5*

**File:** `web/templates/index.html`

```html
{% extends "base.html" %}

{% block body %}
<div class="h-full flex">
    <!-- Sidebar (Control Rail) -->
    <aside 
        x-show="sidebarOpen"
        x-transition:enter="transition ease-out duration-200"
        x-transition:enter-start="-translate-x-full"
        x-transition:enter-end="translate-x-0"
        class="w-80 flex-shrink-0 bg-slate-50 border-r border-slate-200 flex flex-col h-full overflow-hidden"
    >
        {% include "components/sidebar.html" %}
    </aside>
    
    <!-- Main Canvas -->
    <main class="flex-1 flex flex-col h-full overflow-hidden">
        {% include "components/canvas.html" %}
    </main>
    
    <!-- Legend Drawer -->
    <div 
        x-show="showLegend && patternData"
        x-transition:enter="transition ease-out duration-200"
        x-transition:enter-start="translate-x-full"
        x-transition:enter-end="translate-x-0"
        class="w-80 flex-shrink-0 bg-white border-l border-slate-200 overflow-y-auto"
    >
        {% include "components/legend.html" %}
    </div>
</div>

<!-- Mobile Sidebar Toggle -->
<button 
    @click="toggleSidebar"
    class="lg:hidden fixed bottom-4 left-4 z-50 btn btn-circle btn-primary shadow-lg"
    :class="{ 'hidden': sidebarOpen }"
>
    <i data-lucide="settings" class="w-5 h-5"></i>
</button>
{% endblock %}
```

#### 2.3 Create Sidebar Component `[P]` — *Can run in parallel after 2.1*

**File:** `web/templates/components/sidebar.html`

```html
<!-- Sidebar Header -->
<div class="p-4 border-b border-slate-200">
    <h1 class="text-lg font-light tracking-tight text-slate-800">
        Cross-Stitch Generator
    </h1>
    <p class="text-xs text-slate-500 mt-1">Modern Atelier</p>
</div>

<!-- Sidebar Content (Scrollable) -->
<div class="flex-1 overflow-y-auto p-4 space-y-6" :class="{ 'opacity-50 pointer-events-none': !hasImage }">
    
    <!-- Resolution -->
    <div class="space-y-2">
        <label class="label-data">Pattern Size</label>
        <div class="flex items-center gap-3">
            <input 
                type="range" 
                x-model.number="config.resolution"
                min="25" max="200" step="25"
                class="range range-primary range-sm flex-1"
            >
            <input 
                type="number"
                x-model.number="config.resolution"
                min="25" max="300"
                class="input input-bordered input-sm w-20 text-center"
            >
        </div>
        <p class="text-xs text-slate-400">
            <span x-text="config.resolution"></span> × <span x-text="config.resolution"></span> stitches
        </p>
    </div>
    
    <!-- Max Colors -->
    <div class="space-y-2">
        <label class="label-data">Thread Colors</label>
        <div class="flex items-center gap-3">
            <input 
                type="range" 
                x-model.number="config.max_colors"
                min="8" max="128" step="8"
                class="range range-primary range-sm flex-1"
            >
            <input 
                type="number"
                x-model.number="config.max_colors"
                min="2" max="256"
                class="input input-bordered input-sm w-20 text-center"
            >
        </div>
    </div>
    
    <!-- Edge Mode -->
    <div class="space-y-2">
        <label class="label-data">Edge Handling</label>
        <div class="btn-group w-full">
            <button 
                @click="config.edge_mode = 'smooth'"
                :class="{ 'btn-active': config.edge_mode === 'smooth' }"
                class="btn btn-sm flex-1"
            >
                <i data-lucide="waves" class="w-4 h-4 mr-1"></i>
                Smooth
            </button>
            <button 
                @click="config.edge_mode = 'hard'"
                :class="{ 'btn-active': config.edge_mode === 'hard' }"
                class="btn btn-sm flex-1"
            >
                <i data-lucide="square" class="w-4 h-4 mr-1"></i>
                Hard
            </button>
        </div>
        <p class="text-xs text-slate-400">
            <span x-show="config.edge_mode === 'smooth'">Best for photos and gradients</span>
            <span x-show="config.edge_mode === 'hard'">Best for logos and pixel art</span>
        </p>
    </div>
    
    <!-- Color Quantization -->
    <div class="space-y-2">
        <label class="label-data">Quantization Method</label>
        <select x-model="config.quantization" class="select select-bordered select-sm w-full">
            <option value="median_cut">Median Cut (Fast)</option>
            <option value="kmeans">K-Means (Accurate)</option>
        </select>
    </div>
    
    <!-- DMC Options -->
    <div class="space-y-3">
        <label class="label-data">DMC Thread Matching</label>
        <label class="flex items-center gap-3 cursor-pointer">
            <input 
                type="checkbox" 
                x-model="config.enable_dmc"
                class="checkbox checkbox-primary checkbox-sm"
            >
            <span class="text-sm text-slate-700">Match to DMC colors</span>
        </label>
        <label class="flex items-center gap-3 cursor-pointer" x-show="config.enable_dmc">
            <input 
                type="checkbox" 
                x-model="config.dmc_only"
                class="checkbox checkbox-primary checkbox-sm"
            >
            <span class="text-sm text-slate-700">DMC palette only</span>
        </label>
    </div>
    
    <!-- Noise Threshold -->
    <div class="space-y-2">
        <label class="label-data">Color Cleanup</label>
        <div class="flex items-center gap-3">
            <input 
                type="range" 
                x-model.number="config.min_color_percent"
                min="0" max="5" step="0.5"
                class="range range-sm flex-1"
            >
            <span class="text-sm text-slate-600 w-12 text-right" x-text="config.min_color_percent + '%'"></span>
        </div>
        <p class="text-xs text-slate-400">Remove colors below this threshold</p>
    </div>
</div>

<!-- Sidebar Footer (Generate Button) -->
<div class="p-4 border-t border-slate-200 bg-white">
    <button 
        @click="$dispatch('generate-pattern')"
        :disabled="!hasImage || isGenerating"
        class="btn btn-primary w-full"
        :class="{ 'loading': isGenerating }"
    >
        <template x-if="!isGenerating">
            <span class="flex items-center gap-2">
                <i data-lucide="sparkles" class="w-4 h-4"></i>
                Generate Pattern
            </span>
        </template>
        <template x-if="isGenerating">
            <span>Processing...</span>
        </template>
    </button>
</div>
```

#### 2.4 Create Canvas Component `[P]` — *Can run in parallel after 2.1*

**File:** `web/templates/components/canvas.html`

```html
<!-- Canvas Header -->
<div class="flex items-center justify-between px-4 py-2 border-b border-slate-200 bg-white">
    <!-- View Mode Toggle -->
    <div class="flex items-center gap-2" x-show="patternData">
        <div class="btn-group">
            <button 
                @click="setViewMode('color')"
                :class="{ 'btn-active': viewMode === 'color' }"
                class="btn btn-sm"
            >
                <i data-lucide="palette" class="w-4 h-4 mr-1"></i>
                Colors
            </button>
            <button 
                @click="setViewMode('symbol')"
                :class="{ 'btn-active': viewMode === 'symbol' }"
                class="btn btn-sm"
            >
                <i data-lucide="hash" class="w-4 h-4 mr-1"></i>
                Symbols
            </button>
        </div>
    </div>
    
    <!-- Zoom Controls -->
    <div class="flex items-center gap-1" x-show="patternData">
        <button @click="zoomOut" class="btn btn-ghost btn-sm btn-square">
            <i data-lucide="minus" class="w-4 h-4"></i>
        </button>
        <button @click="resetZoom" class="btn btn-ghost btn-sm px-2">
            <span x-text="Math.round(zoom * 100) + '%'" class="text-xs"></span>
        </button>
        <button @click="zoomIn" class="btn btn-ghost btn-sm btn-square">
            <i data-lucide="plus" class="w-4 h-4"></i>
        </button>
    </div>
    
    <!-- Actions -->
    <div class="flex items-center gap-2">
        <button 
            @click="showLegend = !showLegend"
            x-show="patternData"
            :class="{ 'btn-active': showLegend }"
            class="btn btn-ghost btn-sm"
        >
            <i data-lucide="list" class="w-4 h-4 mr-1"></i>
            Legend
        </button>
        <button 
            x-show="patternData"
            class="btn btn-ghost btn-sm"
            hx-get="/api/download/{jobId}"
            hx-swap="none"
        >
            <i data-lucide="download" class="w-4 h-4 mr-1"></i>
            Export
        </button>
    </div>
</div>

<!-- Canvas Viewport -->
<div class="flex-1 overflow-auto canvas-grid">
    <!-- Empty State (Invitation) -->
    <div 
        x-show="!hasImage && !isGenerating"
        class="h-full flex items-center justify-center p-8"
    >
        <div 
            class="w-full max-w-md aspect-square border-2 border-dashed border-slate-300 rounded-xl flex flex-col items-center justify-center gap-4 transition-colors"
            :class="{ 'border-indigo-500 bg-indigo-50/20': isDragging }"
            x-data="{ isDragging: false }"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleFileDrop($event)"
        >
            <i data-lucide="image-plus" class="w-12 h-12 text-slate-400"></i>
            <div class="text-center">
                <p class="text-slate-600 font-medium">Drop your image here</p>
                <p class="text-sm text-slate-400 mt-1">or click to browse</p>
            </div>
            <input 
                type="file" 
                accept="image/*"
                @change="handleFileSelect($event)"
                class="hidden"
                id="file-input"
            >
            <label for="file-input" class="btn btn-outline btn-sm cursor-pointer">
                <i data-lucide="upload" class="w-4 h-4 mr-2"></i>
                Choose File
            </label>
        </div>
    </div>
    
    <!-- Loading State -->
    <div 
        x-show="isGenerating"
        class="h-full flex items-center justify-center"
    >
        <div class="text-center">
            <span class="loading loading-spinner loading-lg text-primary"></span>
            <p class="mt-4 text-slate-600">Generating your pattern...</p>
        </div>
    </div>
    
    <!-- Pattern Canvas -->
    <div 
        x-show="patternData && !isGenerating"
        class="h-full flex items-center justify-center p-4"
    >
        <canvas 
            id="pattern-canvas"
            class="shadow-lg pattern-fade-in"
            :style="{ transform: `scale(${zoom})`, transformOrigin: 'center' }"
        ></canvas>
    </div>
</div>
```

#### 2.5 Create Legend Component `[P]` — *Can run in parallel after 2.1*

**File:** `web/templates/components/legend.html`

```html
<!-- Legend Header -->
<div class="p-4 border-b border-slate-200 sticky top-0 bg-white z-10">
    <div class="flex items-center justify-between">
        <h2 class="text-sm font-medium text-slate-800">Thread Legend</h2>
        <button @click="showLegend = false" class="btn btn-ghost btn-sm btn-square">
            <i data-lucide="x" class="w-4 h-4"></i>
        </button>
    </div>
    <p class="text-xs text-slate-500 mt-1" x-show="patternData">
        <span x-text="patternData?.threads?.length || 0"></span> colors • 
        <span x-text="patternData?.total_stitches?.toLocaleString() || 0"></span> stitches
    </p>
</div>

<!-- Thread List -->
<div class="p-4 space-y-2" x-show="patternData">
    <template x-for="thread in patternData?.threads || []" :key="thread.dmc_code">
        <div class="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50 transition-colors">
            <!-- Color Swatch -->
            <div 
                class="w-8 h-8 rounded-md shadow-inner flex-shrink-0 border border-slate-200"
                :style="{ backgroundColor: thread.hex_color }"
            ></div>
            
            <!-- Thread Info -->
            <div class="flex-1 min-w-0">
                <div class="flex items-baseline gap-2">
                    <span class="text-sm font-medium text-slate-800" x-text="thread.dmc_code"></span>
                    <span class="text-xs text-slate-500 truncate" x-text="thread.name"></span>
                </div>
                <div class="flex items-center gap-2 mt-0.5">
                    <span class="text-xs text-slate-400" x-text="thread.stitch_count.toLocaleString() + ' stitches'"></span>
                    <span class="text-xs text-slate-300">•</span>
                    <span class="text-xs text-slate-400" x-text="thread.percentage + '%'"></span>
                </div>
            </div>
        </div>
    </template>
</div>

<!-- Empty Legend State -->
<div class="p-8 text-center" x-show="!patternData">
    <i data-lucide="palette" class="w-8 h-8 text-slate-300 mx-auto"></i>
    <p class="text-sm text-slate-400 mt-2">Generate a pattern to see the thread legend</p>
</div>
```

### CHECKPOINT

```bash
# Start server
uvicorn web.main:app --reload &
sleep 3

# Load index page
curl -s http://localhost:8000/ | grep -q "Cross-Stitch Generator"
echo "Index page loads: $?"

# Check all template includes
curl -s http://localhost:8000/ | grep -q "Drop your image here"
echo "Empty state renders: $?"

pkill -f uvicorn
```

**Pass Criteria:** Index page loads with all components rendered, no Jinja2 template errors.

### HANDOFF

Templates complete. UI matches Modern Atelier specification. Ready for interactive JavaScript and HTMX integration.

---

## Phase 3: Interactive Canvas Renderer

### CONTEXT

The pattern canvas must render 40,000+ cells (200×200 patterns) efficiently. We use indexed color arrays and HTML5 Canvas for performance.

**Data Format:**
```javascript
{
  width: 100,
  height: 100,
  palette: ["#ff0000", "#00ff00", ...],  // N colors
  grid: [0, 1, 0, 2, 1, ...],  // width × height palette indices
}
```

### TASKS

#### 3.1 Create Pattern Store (Data Management) `[P]` — *Can run in parallel*

**File:** `web/static/js/pattern-store.js`

```javascript
/**
 * PatternStore: Centralized pattern data management.
 * Separated from Alpine.js to prevent DOM thrashing on large patterns.
 * 
 * CRITICAL: Uses Uint8ClampedArray for the grid to handle 40,000+ cells
 * (200x200 patterns) without UI lag. This is essential for "Modern Atelier" snappiness.
 */
const PatternStore = {
    data: null,
    canvas: null,
    ctx: null,
    cellSize: 4,
    
    // Typed array for high-performance grid access
    gridBuffer: null,
    
    /**
     * Initialize store with canvas element.
     */
    init(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (this.canvas) {
            this.ctx = this.canvas.getContext('2d', { 
                alpha: false,  // Optimization: no transparency needed
                willReadFrequently: false 
            });
        }
    },
    
    /**
     * Load pattern data from API response.
     * Converts grid array to Uint8ClampedArray for performance.
     */
    load(patternData) {
        this.data = patternData;
        
        // Convert grid to typed array for fast iteration
        // This is CRITICAL for 200x200+ patterns (40,000 cells)
        this.gridBuffer = new Uint8ClampedArray(patternData.grid);
        
        this.render('color');
    },
    
    /**
     * Render pattern to canvas using optimized buffer access.
     * @param {'color'|'symbol'} mode - Render mode
     */
    render(mode = 'color') {
        if (!this.data || !this.ctx || !this.gridBuffer) return;
        
        const { width, height, palette } = this.data;
        
        // Calculate optimal cell size
        const maxCanvasSize = Math.min(window.innerWidth - 400, window.innerHeight - 100);
        this.cellSize = Math.max(2, Math.floor(maxCanvasSize / Math.max(width, height)));
        
        // Size canvas
        this.canvas.width = width * this.cellSize;
        this.canvas.height = height * this.cellSize;
        
        // Pre-parse palette colors for performance
        const paletteRGB = palette.map(hex => ({
            r: parseInt(hex.slice(1, 3), 16),
            g: parseInt(hex.slice(3, 5), 16),
            b: parseInt(hex.slice(5, 7), 16),
            hex: hex
        }));
        
        // Use ImageData for bulk pixel manipulation (fastest method)
        if (this.cellSize <= 4) {
            this.renderWithImageData(width, height, paletteRGB);
        } else {
            // For larger cells, use fillRect (allows grid lines)
            this.renderWithFillRect(width, height, paletteRGB, mode);
        }
    },
    
    /**
     * Ultra-fast rendering using ImageData for small cell sizes.
     * Directly manipulates pixel buffer - no fillRect overhead.
     */
    renderWithImageData(width, height, paletteRGB) {
        const imageData = this.ctx.createImageData(this.canvas.width, this.canvas.height);
        const pixels = imageData.data;
        const cellSize = this.cellSize;
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const colorIndex = this.gridBuffer[y * width + x];
                const color = paletteRGB[colorIndex];
                
                // Fill cell in pixel buffer
                for (let cy = 0; cy < cellSize; cy++) {
                    for (let cx = 0; cx < cellSize; cx++) {
                        const px = (x * cellSize + cx);
                        const py = (y * cellSize + cy);
                        const idx = (py * this.canvas.width + px) * 4;
                        
                        pixels[idx] = color.r;
                        pixels[idx + 1] = color.g;
                        pixels[idx + 2] = color.b;
                        pixels[idx + 3] = 255;
                    }
                }
            }
        }
        
        this.ctx.putImageData(imageData, 0, 0);
    },
    
    /**
     * Standard rendering with fillRect for larger cells.
     * Allows grid lines and symbol overlays.
     */
    renderWithFillRect(width, height, paletteRGB, mode) {
        // Clear
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Render cells
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const colorIndex = this.gridBuffer[y * width + x];
                const color = paletteRGB[colorIndex];
                
                const px = x * this.cellSize;
                const py = y * this.cellSize;
                
                // Fill cell
                this.ctx.fillStyle = color.hex;
                this.ctx.fillRect(px, py, this.cellSize, this.cellSize);
                
                // Draw symbol overlay if requested
                if (mode === 'symbol' && this.cellSize >= 8) {
                    this.drawSymbol(px, py, colorIndex, color);
                }
            }
        }
        
        // Draw grid lines if cells are large enough
        if (this.cellSize >= 6) {
            this.drawGrid(width, height);
        }
    },
    
    /**
     * Draw symbol for a cell.
     */
    drawSymbol(px, py, colorIndex, color) {
        const symbols = '○●◊◆□■△▲▽▼☆★♦♠♣♥';
        const symbol = symbols[colorIndex % symbols.length];
        
        // Calculate luminance for contrast
        const luminance = (0.299 * color.r + 0.587 * color.g + 0.114 * color.b) / 255;
        this.ctx.fillStyle = luminance > 0.5 ? '#000000' : '#ffffff';
        
        this.ctx.font = `${this.cellSize * 0.7}px monospace`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(
            symbol,
            px + this.cellSize / 2,
            py + this.cellSize / 2
        );
    },
    
    /**
     * Draw grid lines.
     */
    drawGrid(width, height) {
        this.ctx.strokeStyle = 'rgba(0,0,0,0.1)';
        this.ctx.lineWidth = 0.5;
        
        // Batch path operations for performance
        this.ctx.beginPath();
        for (let x = 0; x <= width; x++) {
            this.ctx.moveTo(x * this.cellSize, 0);
            this.ctx.lineTo(x * this.cellSize, height * this.cellSize);
        }
        for (let y = 0; y <= height; y++) {
            this.ctx.moveTo(0, y * this.cellSize);
            this.ctx.lineTo(width * this.cellSize, y * this.cellSize);
        }
        this.ctx.stroke();
    },
    
    /**
     * Get cell info at coordinates (for hover tooltips).
     */
    getCellAt(canvasX, canvasY) {
        if (!this.data || !this.gridBuffer) return null;
        
        const x = Math.floor(canvasX / this.cellSize);
        const y = Math.floor(canvasY / this.cellSize);
        
        if (x < 0 || x >= this.data.width || y < 0 || y >= this.data.height) {
            return null;
        }
        
        const colorIndex = this.gridBuffer[y * this.data.width + x];
        const thread = this.data.threads.find(t => t.hex_color === this.data.palette[colorIndex]);
        
        return {
            x, y,
            color: this.data.palette[colorIndex],
            thread: thread || null
        };
    }
};
```

#### 3.2 Create Upload Handler `[P]` — *Can run in parallel*

**File:** `web/static/js/upload-handler.js`

```javascript
/**
 * File upload handling with HTMX integration.
 */

// Handle file drop on dropzone
function handleFileDrop(event) {
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        uploadFile(file);
    }
}

// Handle file selection from input
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

// Upload file to server
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Get Alpine.js state
    const appEl = document.querySelector('[x-data]');
    const app = Alpine.$data(appEl);
    
    app.isGenerating = true;
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        const result = await response.json();
        
        // Update state
        app.jobId = result.job_id;
        app.hasImage = true;
        app.isGenerating = false;
        
        // Show any warnings
        if (result.resize_warning) {
            showNotification(result.resize_warning, 'warning');
        }
        if (result.texture_warning) {
            showNotification(result.texture_warning, 'warning');
        }
        
    } catch (error) {
        app.isGenerating = false;
        showNotification(error.message, 'error');
    }
}

// Simple notification helper
function showNotification(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} fixed bottom-4 right-4 w-auto max-w-sm shadow-lg z-50`;
    toast.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="btn btn-ghost btn-sm btn-square">
            <i data-lucide="x" class="w-4 h-4"></i>
        </button>
    `;
    document.body.appendChild(toast);
    lucide.createIcons();
    
    // Auto-remove after 5 seconds
    setTimeout(() => toast.remove(), 5000);
}
```

#### 3.3 Create HTMX Interactions `[P]` — *Can run in parallel*

**File:** `web/static/js/interactions.js`

```javascript
/**
 * HTMX and Alpine.js interaction handlers.
 */

// Listen for generate-pattern event from Alpine.js
document.addEventListener('alpine:init', () => {
    Alpine.data('patternGenerator', () => ({
        async generatePattern() {
            const app = Alpine.$data(document.querySelector('[x-data="appState()"]'));
            
            if (!app.jobId) {
                showNotification('Please upload an image first', 'warning');
                return;
            }
            
            app.isGenerating = true;
            
            try {
                const response = await fetch(`/api/generate/${app.jobId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(app.config)
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Generation failed');
                }
                
                const patternData = await response.json();
                
                // Store pattern data
                app.patternData = patternData;
                
                // Initialize and render canvas
                PatternStore.init('pattern-canvas');
                PatternStore.load(patternData);
                
                app.isGenerating = false;
                
            } catch (error) {
                app.isGenerating = false;
                showNotification(error.message, 'error');
            }
        }
    }));
});

// Listen for custom events
document.addEventListener('generate-pattern', async (event) => {
    const app = Alpine.$data(document.querySelector('[x-data="appState()"]'));
    
    if (!app.jobId) {
        showNotification('Please upload an image first', 'warning');
        return;
    }
    
    app.isGenerating = true;
    
    try {
        const response = await fetch(`/api/generate/${app.jobId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(app.config)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Generation failed');
        }
        
        const patternData = await response.json();
        app.patternData = patternData;
        
        PatternStore.init('pattern-canvas');
        PatternStore.load(patternData);
        
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        app.isGenerating = false;
    }
});

// Listen for render mode changes
document.addEventListener('render-pattern', (event) => {
    if (PatternStore.data) {
        PatternStore.render(event.detail.mode);
    }
});

// Canvas hover for cell info
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('pattern-canvas');
    if (canvas) {
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const cell = PatternStore.getCellAt(x, y);
            if (cell && cell.thread) {
                canvas.title = `${cell.thread.dmc_code}: ${cell.thread.name}`;
            } else {
                canvas.title = '';
            }
        });
    }
});
```

#### 3.4 Update Base Template to Include Scripts `[I]` — *Integration: requires 3.1-3.3*

**Edit:** `web/templates/base.html` — Add before `</body>`:

```html
<!-- Pattern Store and Interactions -->
<script src="/static/js/pattern-store.js"></script>
<script src="/static/js/upload-handler.js"></script>
<script src="/static/js/interactions.js"></script>
```

### CHECKPOINT

```bash
# Start server with all assets
uvicorn web.main:app --reload &
sleep 3

# Verify static files served
curl -s http://localhost:8000/static/js/pattern-store.js | head -5
curl -s http://localhost:8000/static/js/upload-handler.js | head -5
curl -s http://localhost:8000/static/js/interactions.js | head -5

# Manual test: Open browser, upload image, click Generate
echo "Manual test required: http://localhost:8000"

pkill -f uvicorn
```

**Pass Criteria:** Static JS files load, upload triggers analysis response, Generate renders pattern to canvas.

### HANDOFF

Interactive canvas complete. Pattern rendering works with zoom, view mode toggle, and hover inspection. Ready for polish phase.

---

## Phase 4: Production Polish

### CONTEXT

Final polish: error handling, export functionality, mobile responsiveness, and deployment configuration.

### TASKS

#### 4.0 Implement HTMX Out-of-Band Updates `[CRITICAL]`

The "Magic Moment" requires simultaneous updates to canvas, legend, and stitch count. This uses HTMX OOB swaps.

**Update:** `web/routes/api.py` — Add OOB response endpoint

```python
from fastapi.responses import HTMLResponse

@router.post("/generate/{job_id}/htmx")
async def generate_pattern_htmx(job_id: str, config: PatternConfig, request: Request):
    """Generate pattern and return HTMX OOB response for simultaneous UI updates.
    
    This endpoint returns multiple HTML fragments that HTMX swaps simultaneously:
    - Main canvas data (primary target)
    - Legend panel (OOB swap)
    - Stitch count in sidebar (OOB swap)
    
    This creates the "Magic Moment" effect from the UI-UX specification.
    """
    if job_id not in _jobs:
        raise HTTPException(404, "Upload expired")
    
    job = _jobs[job_id]
    image = job["image"]
    
    # Generate pattern (same as JSON endpoint)
    pattern_data = await run_in_threadpool(_generate_pattern_sync, image, config)
    
    # Store for download
    _jobs[job_id]["pattern"] = pattern_data
    
    # Build OOB response with multiple fragments
    # Primary: Canvas data script (injected into #canvas-data)
    # OOB 1: Legend thread list
    # OOB 2: Stitch count badge
    
    threads_html = "".join([
        f'''<div class="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50">
            <div class="w-8 h-8 rounded-md shadow-inner border border-slate-200" 
                 style="background-color: {t.hex_color}"></div>
            <div class="flex-1 min-w-0">
                <div class="flex items-baseline gap-2">
                    <span class="text-sm font-medium text-slate-800">{t.dmc_code}</span>
                    <span class="text-xs text-slate-500 truncate">{t.name}</span>
                </div>
                <div class="text-xs text-slate-400">
                    {t.stitch_count:,} stitches • {t.percentage}%
                </div>
            </div>
        </div>'''
        for t in pattern_data.threads
    ])
    
    html_response = f'''
    <!-- Primary target: Canvas data injection -->
    <script id="pattern-data-script">
        PatternStore.init('pattern-canvas');
        PatternStore.load({pattern_data.model_dump_json()});
        
        // Update Alpine.js state
        const app = Alpine.$data(document.querySelector('[x-data="appState()"]'));
        app.patternData = {pattern_data.model_dump_json()};
        app.isGenerating = false;
    </script>
    
    <!-- OOB: Thread legend -->
    <div id="thread-list" hx-swap-oob="innerHTML">
        {threads_html}
    </div>
    
    <!-- OOB: Stitch count in sidebar -->
    <span id="stitch-count-badge" hx-swap-oob="innerHTML" class="badge badge-primary">
        {pattern_data.total_stitches:,} stitches
    </span>
    
    <!-- OOB: Thread count -->
    <span id="thread-count-badge" hx-swap-oob="innerHTML" class="badge badge-secondary">
        {len(pattern_data.threads)} colors
    </span>
    '''
    
    return HTMLResponse(content=html_response)
```

**Update:** `web/templates/components/sidebar.html` — Add OOB target badges

```html
<!-- Add after Generate button, before closing sidebar footer -->
<div class="flex items-center gap-2 mt-3" x-show="patternData">
    <span id="stitch-count-badge" class="badge badge-primary badge-sm"></span>
    <span id="thread-count-badge" class="badge badge-secondary badge-sm"></span>
</div>
```

**Update:** `web/templates/components/legend.html` — Add OOB target container

```html
<!-- Replace the template x-for with static container -->
<div id="thread-list" class="p-4 space-y-2">
    <!-- Populated via HTMX OOB swap -->
</div>
```

**Update:** Generate button to use HTMX endpoint

```html
<button 
    hx-post="/api/generate/{jobId}/htmx"
    hx-target="#canvas-container"
    hx-vals='js:{...Alpine.$data(document.querySelector("[x-data]")).config}'
    hx-indicator="#generate-spinner"
    :disabled="!hasImage || isGenerating"
    class="btn btn-primary w-full"
>
    <span id="generate-spinner" class="loading loading-spinner htmx-indicator"></span>
    <span>Generate Pattern</span>
</button>
```

#### 4.1 Add Error Boundary Component

**File:** `web/templates/components/error-toast.html`

```html
<!-- Error Toast Container -->
<div 
    id="toast-container" 
    class="fixed bottom-4 right-4 z-50 space-y-2"
    x-data="{ toasts: [] }"
    @show-toast.window="toasts.push($event.detail); setTimeout(() => toasts.shift(), 5000)"
>
    <template x-for="(toast, index) in toasts" :key="index">
        <div 
            class="alert shadow-lg max-w-sm"
            :class="{
                'alert-error': toast.type === 'error',
                'alert-warning': toast.type === 'warning',
                'alert-info': toast.type === 'info',
                'alert-success': toast.type === 'success'
            }"
            x-transition:enter="transition ease-out duration-200"
            x-transition:enter-start="opacity-0 translate-x-full"
            x-transition:enter-end="opacity-100 translate-x-0"
        >
            <span x-text="toast.message"></span>
            <button @click="toasts.splice(index, 1)" class="btn btn-ghost btn-sm btn-square">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        </div>
    </template>
</div>
```

#### 4.2 Add Export Modal

**File:** `web/templates/components/export-modal.html`

```html
<!-- Export Modal -->
<dialog id="export-modal" class="modal" x-data="{ format: 'xlsx' }">
    <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">Export Pattern</h3>
        
        <div class="space-y-3">
            <label class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-slate-50 transition-colors" :class="{ 'border-indigo-500 bg-indigo-50': format === 'xlsx' }">
                <input type="radio" x-model="format" value="xlsx" class="radio radio-primary radio-sm">
                <div>
                    <p class="font-medium text-sm">Excel Spreadsheet (.xlsx)</p>
                    <p class="text-xs text-slate-500">Full pattern with color legend and DMC codes</p>
                </div>
            </label>
            
            <label class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-slate-50 transition-colors" :class="{ 'border-indigo-500 bg-indigo-50': format === 'png' }">
                <input type="radio" x-model="format" value="png" class="radio radio-primary radio-sm">
                <div>
                    <p class="font-medium text-sm">Image Preview (.png)</p>
                    <p class="text-xs text-slate-500">High-resolution pattern image</p>
                </div>
            </label>
            
            <label class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-slate-50 transition-colors" :class="{ 'border-indigo-500 bg-indigo-50': format === 'json' }">
                <input type="radio" x-model="format" value="json" class="radio radio-primary radio-sm">
                <div>
                    <p class="font-medium text-sm">Raw Data (.json)</p>
                    <p class="text-xs text-slate-500">Machine-readable pattern data</p>
                </div>
            </label>
        </div>
        
        <div class="modal-action">
            <form method="dialog">
                <button class="btn btn-ghost">Cancel</button>
            </form>
            <button 
                @click="downloadPattern(format)"
                class="btn btn-primary"
            >
                <i data-lucide="download" class="w-4 h-4 mr-2"></i>
                Download
            </button>
        </div>
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>
```

#### 4.3 Add Mobile Responsive Styles

**Edit:** `web/templates/base.html` — Add to `<style>` block:

```css
/* Mobile Responsive */
@media (max-width: 1024px) {
    .sidebar-mobile {
        position: fixed;
        left: 0;
        top: 0;
        height: 100vh;
        z-index: 40;
        transform: translateX(-100%);
        transition: transform 0.2s ease-out;
    }
    .sidebar-mobile.open {
        transform: translateX(0);
    }
    .sidebar-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.3);
        z-index: 30;
    }
}

/* Touch-friendly controls */
@media (max-width: 768px) {
    .btn {
        min-height: 44px;
    }
    .range {
        height: 44px;
    }
    input[type="number"] {
        min-height: 44px;
    }
}
```

#### 4.4 Add Health Check and Metrics

**Edit:** `web/main.py` — Add after health endpoint:

```python
from datetime import datetime

_start_time = datetime.now()
_request_count = 0


@app.middleware("http")
async def count_requests(request, call_next):
    global _request_count
    _request_count += 1
    response = await call_next(request)
    return response


@app.get("/metrics")
async def metrics():
    """Basic metrics for monitoring."""
    uptime = (datetime.now() - _start_time).total_seconds()
    return {
        "uptime_seconds": uptime,
        "requests_total": _request_count,
        "active_jobs": len(_jobs) if '_jobs' in dir() else 0
    }
```

#### 4.5 Create GitHub Actions Workflow

**File:** `.github/workflows/deploy.yml`

```yaml
name: Deploy to Replit

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-web.txt
          pip install pytest pytest-asyncio httpx
          
      - name: Run tests
        run: pytest tests/ -v
        
      - name: Test web server starts
        run: |
          uvicorn web.main:app --host 0.0.0.0 --port 8000 &
          sleep 5
          curl -f http://localhost:8000/health
          pkill -f uvicorn

  notify:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deployment ready
        run: echo "Tests passed. Pull changes in Replit to deploy."
```

### CHECKPOINT

```bash
# Run full test suite
pytest tests/ -v

# Start server
uvicorn web.main:app --reload &
sleep 3

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/metrics

# Test full flow (manual)
echo "Manual test: Upload → Configure → Generate → Export"
echo "http://localhost:8000"

pkill -f uvicorn
```

**Pass Criteria:** All tests pass, health and metrics endpoints respond, full user flow works.

### HANDOFF

Production-ready. Deploy by importing GitHub repo into Replit.

---

## Deployment Checklist

```
□ All phases complete
□ pytest passes (92+/94 tests)
□ Web server starts without errors
□ Upload → Generate → Export flow works
□ Mobile responsive
□ GitHub repo up to date
□ Replit import configured
□ Health check responds
```

## File Reference

```
cross-stitch-generator/
├── .github/workflows/deploy.yml     # CI/CD
├── .replit                          # Replit config
├── replit.nix                       # Nix environment
├── requirements-web.txt             # Web dependencies
├── CLAUDE.md                        # Agent instructions (updated)
├── web/
│   ├── __init__.py
│   ├── main.py                      # FastAPI entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py              # Pydantic request models
│   │   └── responses.py             # Pydantic response models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py                   # API endpoints
│   │   └── frontend.py              # Template routes
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── async_processing.py      # Thread pool wrappers
│   │   └── memory_management.py     # Temp file management
│   ├── templates/
│   │   ├── base.html                # Base layout
│   │   ├── index.html               # Main app
│   │   └── components/
│   │       ├── sidebar.html         # Control rail
│   │       ├── canvas.html          # Visualization
│   │       ├── legend.html          # Thread legend
│   │       ├── error-toast.html     # Notifications
│   │       └── export-modal.html    # Export dialog
│   └── static/
│       ├── css/
│       │   └── custom.css           # Additional styles
│       └── js/
│           ├── pattern-store.js     # Canvas data management
│           ├── upload-handler.js    # File upload
│           └── interactions.js      # HTMX/Alpine integration
└── src/cross_stitch/                # Existing (DO NOT MODIFY)
```

---

*This plan is optimized for agentic execution with Claude Code. Each phase is self-contained with embedded specifications, explicit file paths, and verifiable checkpoints.*
