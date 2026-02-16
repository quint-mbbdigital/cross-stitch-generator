# Cross-Stitch Pattern Generator

## Project Overview
A sophisticated dual-mode application that converts images into cross-stitch patterns exported as Excel files. Features both a Python CLI and a modern web interface with comprehensive pattern generation, color quantization, and DMC floss thread color matching for real-world embroidery projects.

## Quick Reference Commands

**Core Operations**:
- **Generate Pattern**: `python cross_stitch_generator.py generate input.jpg output.xlsx`
- **Get Image Info**: `python cross_stitch_generator.py info input.jpg`
- **Help**: `python cross_stitch_generator.py --help`

**Development Commands**:
- **Test**: `python -m pytest tests/ -v`
- **Test with Coverage**: `python -m pytest tests/ -v --cov=src/cross_stitch --cov-report=term-missing`
- **Lint**: `python -m ruff check .`
- **Format**: `python -m ruff format .`
- **Type Check**: `python -m mypy src/`
- **Install Dependencies**: `pip install -r requirements.txt`

**Test Specific Modules**:
- `python -m pytest tests/test_integration.py -v`
- `python -m pytest tests/test_models.py -v`
- `python -m pytest tests/test_utils.py -v`

## CRITICAL: TDD Enforcement

**YOU MUST FOLLOW TEST-DRIVEN DEVELOPMENT**:
1. **RED**: Write failing tests FIRST, before any implementation
2. **GREEN**: Write minimal code to make tests pass
3. **REFACTOR**: Clean up code while keeping tests passing
4. **VERIFY**: Run `pytest tests/ -v` after every change

**Never Skip Tests**: If functionality doesn't have tests, create them FIRST. No exceptions.

**Test Coverage**: Maintain >95% test coverage. Current: 254/279 tests passing (~91%)

## Approval Gates - STOP Points

**YOU MUST STOP and get explicit user approval after**:
1. Creating test files (before implementation)
2. Implementing each module (after tests pass)
3. Making significant architectural changes
4. Before modifying existing functionality
5. Before committing to git

**Never proceed to the next phase without explicit user approval.**

## Current Project Structure

```
cross-stitch-generator/
├── src/cross_stitch/           # Main package (CLI backend)
│   ├── cli/
│   │   └── main.py             # Command-line interface (163 lines)
│   ├── core/                   # Core processing modules
│   │   ├── color_manager.py    # Color quantization with DMC support
│   │   ├── dmc_matcher.py      # DMC thread color matching
│   │   ├── excel_generator.py  # Excel file generation (368 lines)
│   │   ├── image_processor.py  # Image loading/processing (342 lines)
│   │   └── pattern_generator.py # Main orchestration (391 lines)
│   ├── models/                 # Data models
│   │   ├── config.py           # GeneratorConfig dataclass
│   │   ├── color_palette.py    # Color/ColorPalette models (140 lines)
│   │   └── pattern.py          # Pattern/PatternSet models (160 lines)
│   └── utils/                  # Utilities
│       ├── exceptions.py       # Custom exceptions (162 lines)
│       ├── file_utils.py       # File/image utilities
│       └── validation.py       # Input validation (331 lines)
├── web/                        # Web interface
│   ├── routes/
│   │   ├── api.py              # FastAPI backend routes
│   │   └── web.py              # Web page routes
│   ├── models/
│   │   └── requests.py         # Pydantic request models
│   ├── static/js/              # Frontend JavaScript
│   │   ├── display-effects.js  # Animation and effects system
│   │   ├── interactions.js     # UI interaction handling
│   │   ├── pattern-store.js    # Canvas rendering and storage
│   │   └── upload-handler.js   # File upload management
│   ├── templates/              # Jinja2 templates
│   │   ├── base.html           # Main application template
│   │   └── components/         # Reusable UI components
│   └── main.py                 # FastAPI application entry point
├── tests/                      # Test suite (279 tests total)
│   ├── conftest.py             # Test fixtures
│   ├── test_integration.py     # CLI integration tests
│   ├── test_models.py          # Model unit tests
│   ├── test_utils.py           # Utility tests
│   ├── test_dmc_*.py           # DMC functionality tests
│   ├── test_edge_mode.py       # Edge processing tests
│   └── test_web/               # Web interface tests
├── data/
│   └── dmc_colors.csv          # DMC thread color database
├── cross_stitch_generator.py   # CLI entry point
├── requirements.txt            # Core dependencies
├── requirements-web.txt        # Web dependencies
└── CLAUDE.md                   # This file
```

## Code Style Guidelines

**Python Version**: 3.11+

**Type Hints**: Required for all function signatures
```python
def process_image(image_path: str, config: GeneratorConfig) -> PatternSet:
    """Process image with proper typing."""
```

**Docstrings**: Required for all public functions (Google style)
```python
def quantize_colors(image: Image, max_colors: int) -> ColorPalette:
    """Quantize image colors to specified palette size.

    Args:
        image: PIL Image to quantize
        max_colors: Maximum colors in resulting palette

    Returns:
        ColorPalette with quantized colors

    Raises:
        ColorQuantizationError: If quantization fails
    """
```

**Function Length**: Keep functions under 50 lines. Break complex logic into smaller functions.

**Error Handling**: Use custom exception hierarchy from `utils.exceptions`

**Imports**: Group imports (stdlib, third-party, local) with blank lines between groups

## Current Functionality Status

**✅ Core Features (CLI + Web)**:
- Image loading (PNG, JPG, GIF, BMP, TIFF, WEBP)
- Color quantization (median cut and k-means algorithms)
- Pattern generation at multiple resolutions
- Excel file generation with colored cells and DMC codes
- Color legend and summary sheets
- **DMC floss thread color matching** - Full database with 500+ colors
- CLI with progress reporting
- Modern web interface with real-time preview
- Comprehensive error handling with graceful fallbacks
- Transparency handling (white background, remove, preserve)
- Edge mode processing (smooth/hard)

**✅ Web Interface Features**:
- Real-time pattern preview with canvas rendering
- Advanced animation system with accessibility support
- Drag-and-drop file upload
- Interactive color/symbol view modes
- DMC thread shopping list generation
- Responsive design with mobile support

**⚠️ Known Issues**:
- Some edge mode and Excel professional improvement tests failing (24/279 tests)
- Pillow deprecation warnings for 'mode' parameter
- Web-specific tests may need alignment after recent changes

**🔒 Recent Stability Fixes**:
- Fixed silent exception handling in DMC initialization
- Added graceful fallback for missing DMC database
- Improved error logging and debugging capabilities

## Dependencies

**Core (CLI)**:
- `pillow==12.1.0` - Image processing
- `openpyxl==3.1.5` - Excel generation
- `numpy==2.4.1` - Array operations
- `scikit-learn==1.8.0` - K-means clustering

**Web Interface**:
- `fastapi` - Modern Python web framework
- `jinja2` - Template engine
- `python-multipart` - File upload support
- `uvicorn` - ASGI server

**Frontend Stack**:
- **HTMX** - Dynamic HTML without JavaScript complexity
- **Alpine.js** - Reactive components and state management
- **Tailwind CSS** - Utility-first CSS framework
- **DaisyUI** - Component library for Tailwind

**Development**:
- `pytest==9.0.2` - Testing framework
- `mypy==1.19.1` - Type checking
- `ruff==0.14.11` - Linting and formatting

## CLI Usage Examples

```bash
# Basic pattern generation
python cross_stitch_generator.py generate photo.jpg pattern.xlsx

# Custom resolutions and color limits
python cross_stitch_generator.py generate photo.jpg pattern.xlsx \
  --resolutions "30x30,60x60,120x120" --max-colors 64

# Handle transparency
python cross_stitch_generator.py generate transparent.png pattern.xlsx \
  --transparency white_background

# Get image analysis before generating
python cross_stitch_generator.py info photo.jpg --estimate-time

# Verbose output for debugging
python cross_stitch_generator.py generate photo.jpg pattern.xlsx --verbose

# Enable DMC color matching
python cross_stitch_generator.py generate photo.jpg pattern.xlsx --enable-dmc

# DMC-only palette (restrict to available DMC colors)
python cross_stitch_generator.py generate photo.jpg pattern.xlsx --dmc-only
```

## Web Interface Usage

The web interface provides a modern, interactive experience for pattern generation:

**Development Server:**
```bash
# Start the web application
uvicorn web.main:app --reload --host 0.0.0.0 --port 8000
```

**Web Features:**
- **Drag & Drop Upload**: Direct image upload with preview
- **Real-time Configuration**: Interactive sliders and controls
- **Canvas Preview**: Live pattern rendering with color/symbol modes
- **DMC Integration**: Automatic thread color matching with shopping lists
- **Animation System**: Smooth transitions with accessibility support
- **Download Options**: Excel files with professional formatting

**Architecture Notes:**
- **FastAPI Backend**: RESTful API with async support
- **Alpine.js Frontend**: Reactive components without build complexity
- **HTMX Integration**: Dynamic updates without full page reloads
- **Effect System**: Centralized animation management with presets

## Testing Requirements

**Test Categories**:
1. **Unit Tests**: Individual functions and classes
2. **Integration Tests**: Full pipeline workflows
3. **CLI Tests**: Command-line interface behavior
4. **File I/O Tests**: Image loading, Excel generation

**Test Fixtures**: Use fixtures in `conftest.py` for:
- Sample images (RGB, RGBA, grayscale)
- Test configurations
- Temporary directories

**Test Data**: Create realistic test scenarios with actual image patterns

## Git Workflow

**Commit Standards**: Use conventional commits
- `feat:` - New features
- `fix:` - Bug fixes
- `test:` - Adding or fixing tests
- `docs:` - Documentation updates
- `refactor:` - Code refactoring

**Branch Strategy**: Work on `main` branch for now (single developer)

**Commit Frequency**: Commit after each passing test suite, not before

## Recent Major Improvements

The project has evolved significantly from a CLI-only tool to a sophisticated dual-mode application:

**Phase 1 - Critical Stability Fixes:**
- Fixed silent exception handling in DMC initialization (was masking errors)
- Added graceful fallback for missing DMC database configuration
- Improved error logging and debugging capabilities

**Phase 2 - Complexity Reduction:**
- Streamlined display effects system (44% code reduction)
- Aligned frontend/backend parameter consistency (removed 7 unused fields)
- Simplified UI by removing unused configuration sections

**Phase 3 - Web Interface Enhancement:**
- Comprehensive display effects system with animation presets
- Advanced canvas rendering with pre-sizing to prevent visual "pop"
- Effect-aware pattern rendering with accessibility support
- Clean git history with logical commit organization

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