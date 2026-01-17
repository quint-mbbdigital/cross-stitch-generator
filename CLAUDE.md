# Cross-Stitch Pattern Generator

## Project Overview
A Python CLI application that converts images into cross-stitch patterns exported as Excel files. Currently generates patterns at multiple resolutions with color quantization, but lacks DMC floss thread color matching - the key feature needed for real-world embroidery use.

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

**Test Coverage**: Maintain >95% test coverage. Current: 92/94 tests passing (97.9%)

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
├── src/cross_stitch/           # Main package
│   ├── cli/
│   │   └── main.py             # Command-line interface (163 lines)
│   ├── core/                   # Core processing modules
│   │   ├── color_manager.py    # Color quantization (410 lines)
│   │   ├── excel_generator.py  # Excel file generation (368 lines)
│   │   ├── image_processor.py  # Image loading/processing (342 lines)
│   │   └── pattern_generator.py # Main orchestration (391 lines)
│   ├── models/                 # Data models
│   │   ├── config.py           # GeneratorConfig dataclass (63 lines)
│   │   ├── color_palette.py    # Color/ColorPalette models (140 lines)
│   │   └── pattern.py          # Pattern/PatternSet models (160 lines)
│   └── utils/                  # Utilities
│       ├── exceptions.py       # Custom exceptions (162 lines)
│       ├── file_utils.py       # File/image utilities
│       └── validation.py       # Input validation (331 lines)
├── tests/                      # Test suite (94 tests, 92 passing)
│   ├── conftest.py             # Test fixtures
│   ├── test_integration.py     # Integration tests (374 lines)
│   ├── test_models.py          # Model unit tests (430+ lines)
│   └── test_utils.py           # Utility tests (400+ lines)
├── cross_stitch_generator.py   # CLI entry point
├── requirements.txt            # Dependencies
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

**✅ Working Features**:
- Image loading (PNG, JPG, GIF, BMP, TIFF, WEBP)
- Color quantization (median cut and k-means algorithms)
- Pattern generation at multiple resolutions
- Excel file generation with colored cells
- Color legend and summary sheets
- CLI with progress reporting
- Comprehensive error handling
- Transparency handling (white background, remove, preserve)

**⚠️ Known Issues**:
- K-means quantization fails on some grayscale images (2 test failures)
- Pillow deprecation warnings for 'mode' parameter

**❌ Missing Critical Feature**:
- **DMC floss thread color matching** - Currently generates arbitrary RGB colors
- Need DMC color database and matching algorithm
- Excel output should show DMC thread codes in cells

## Dependencies

**Core**:
- `pillow==12.1.0` - Image processing
- `openpyxl==3.1.5` - Excel generation
- `numpy==2.4.1` - Array operations
- `scikit-learn==1.8.0` - K-means clustering

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
```

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

## Current Priority: DMC Color Matching

The codebase is solid but missing the key feature for real-world use. Next phase should add:
1. DMC floss color database (`data/dmc_colors.csv`)
2. Color matching algorithm (`src/cross_stitch/core/dmc_matcher.py`)
3. Excel output enhancement (show DMC codes in cells)
4. CLI flags for DMC options

**Critical**: Implement with TDD - write tests for DMC functionality BEFORE implementation.

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