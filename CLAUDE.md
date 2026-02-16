# Cross-Stitch Pattern Generator

## Project Overview
A sophisticated dual-mode application that converts images into cross-stitch patterns exported as Excel files. Features both a Python CLI and a modern web interface with comprehensive pattern generation, color quantization, and DMC floss thread color matching for real-world embroidery projects.

## Getting Started for New Team Members

### 30-Minute Setup Checklist

**Prerequisites** (5 minutes):
- [ ] Python 3.11+ installed and working
- [ ] Git access to repository
- [ ] Basic understanding of Python development

**Environment Setup** (10-15 minutes):
- [ ] Clone repository: `git clone <repo-url>`
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate environment: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
- [ ] Install dependencies: `pip install -r requirements.txt -r requirements-web.txt`
- [ ] Validate environment: `python scripts/validate-environment.py` (should show all ✅)

**Functionality Test** (5-10 minutes):
- [ ] CLI test: `python cross_stitch_generator.py info --help`
- [ ] Create test pattern: `python cross_stitch_generator.py generate <small-image> test.xlsx`
- [ ] Web interface test: `uvicorn web.main:app --reload --port 8000` → visit localhost:8000
- [ ] Run test suite: `pytest tests/ -v` (expect ~254/279 to pass)

**Completion criteria**: All checkboxes completed, environment validation passes, both CLI and web interface working

### 2-Hour Full Understanding Path

**Hour 1 - Codebase Navigation**:
1. **Read project structure** (this file, lines 49-99) - understand package organization
2. **Explore core modules** (`src/cross_stitch/core/`) - understand the processing pipeline
3. **Review CLI interface** (`src/cross_stitch/cli/main.py`) - understand user-facing commands
4. **Test web interface** (`web/main.py`, `web/routes/`) - understand API structure

**Hour 2 - Development Environment**:
1. **Run different test categories**:
   ```bash
   pytest tests/test_integration.py -v    # CLI end-to-end tests
   pytest tests/test_models.py -v         # Data model tests
   pytest tests/test_utils.py -v          # Utility function tests
   ```
2. **Try CLI variations**:
   ```bash
   python cross_stitch_generator.py generate sample.jpg test.xlsx --verbose
   python cross_stitch_generator.py generate sample.jpg dmc.xlsx --enable-dmc
   ```
3. **Development workflow practice**:
   ```bash
   python -m ruff check .                 # Code linting
   python -m ruff format .                # Code formatting
   python -m mypy src/                    # Type checking
   ```

### Your First Contribution Walkthrough

**Phase 1 - Understanding** (30 minutes):
1. **Pick a good first task**: Look for tests marked as "known failing" or documentation improvements
2. **Understand the feature**: Read relevant code, understand existing implementation
3. **Review test coverage**: Check what tests exist for the area you're modifying

**Phase 2 - Development** (1-2 hours):
1. **Follow TDD process**: Write failing test first (RED), implement minimal solution (GREEN), refactor (REFACTOR)
2. **Test both interfaces**: Verify changes work in both CLI and web interface (if applicable)
3. **Run full validation**:
   ```bash
   pytest tests/ -v && python -m ruff check . && python -m mypy src/
   ```

**Phase 3 - Integration** (15 minutes):
1. **Manual testing**: Try your change with real images and different settings
2. **Documentation**: Update README.md or CLAUDE.md if you changed user-facing behavior
3. **Commit**: Use conventional commit format (`feat:`, `fix:`, `docs:`, `test:`)

### Code Navigation Guide ("Where to Find X")

| Looking for... | Location | Purpose |
|----------------|----------|---------|
| **Command-line interface** | `src/cross_stitch/cli/main.py` | User commands, argument parsing |
| **Image processing** | `src/cross_stitch/core/image_processor.py` | Load, resize, format handling |
| **Color quantization** | `src/cross_stitch/core/color_manager.py` | Reduce colors to manageable palette |
| **DMC thread matching** | `src/cross_stitch/core/dmc_matcher.py` | Match colors to real thread colors |
| **Excel generation** | `src/cross_stitch/core/excel_generator.py` | Create Excel files with pattern data |
| **Pattern orchestration** | `src/cross_stitch/core/pattern_generator.py` | Main processing pipeline |
| **Data models** | `src/cross_stitch/models/` | Configuration, colors, patterns |
| **Web API** | `web/routes/api.py` | HTTP endpoints for pattern generation |
| **Web frontend** | `web/templates/base.html` + `web/static/js/` | User interface |
| **Test fixtures** | `tests/conftest.py` | Reusable test data and setup |
| **DMC color data** | `data/dmc_colors.csv` | Real-world thread color database |

### Expected Outcomes at Each Step

**After 30 minutes**: Environment working, can generate basic patterns
**After 2 hours**: Understand codebase structure, can run tests and development tools
**After first contribution**: Confident with development workflow, understand testing approach

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

## CRITICAL: TDD Enforcement & Team Development Workflow

### Test-Driven Development Process

**YOU MUST FOLLOW TEST-DRIVEN DEVELOPMENT**:
1. **RED**: Write failing tests FIRST, before any implementation
2. **GREEN**: Write minimal code to make tests pass
3. **REFACTOR**: Clean up code while keeping tests passing
4. **VERIFY**: Run `pytest tests/ -v` after every change

**Never Skip Tests**: If functionality doesn't have tests, create them FIRST. No exceptions.

### Practical TDD Examples

**Example 1: Adding New CLI Option**
```bash
# 1. RED - Write failing test first
# In tests/test_cli.py, add test for new --format option
def test_format_option_validation():
    result = runner.invoke(cli, ['generate', 'test.jpg', 'out.xlsx', '--format', 'invalid'])
    assert result.exit_code != 0
    assert "Invalid format" in result.output

# 2. Run test (should fail)
pytest tests/test_cli.py::test_format_option_validation -v

# 3. GREEN - Implement minimal code to pass
# Add format validation in src/cross_stitch/cli/main.py

# 4. REFACTOR - Clean up implementation
# Extract validation to utils/validation.py if reusable
```

**Example 2: Web API Enhancement**
```bash
# 1. RED - Write failing test first
# In tests/test_web/test_api.py, add test for new endpoint
def test_pattern_metadata_endpoint():
    response = client.get("/api/pattern/123/metadata")
    assert response.status_code == 200
    assert "width" in response.json()

# 2. GREEN - Add minimal endpoint implementation
# 3. REFACTOR - Extract business logic to core modules
```

### Parallel Development Without Conflicts

**Branch Strategy for Multiple Developers**:
```bash
# Feature branch workflow
git checkout -b feature/new-edge-algorithm
# Develop with TDD, commit frequently
git commit -m "feat: add test for new edge detection"
git commit -m "feat: implement basic edge detection algorithm"

# Before merging, update from main
git checkout main
git pull origin main
git checkout feature/new-edge-algorithm
git rebase main  # Or merge main into feature branch
```

**Code Areas by Developer** (minimize conflicts):
- **Core algorithms**: `src/cross_stitch/core/` - coordinate changes
- **CLI interface**: `src/cross_stitch/cli/` - usually safe to modify independently
- **Web interface**: `web/` - can develop in parallel with core changes
- **Tests**: `tests/` - add tests freely, merge conflicts rare
- **Documentation**: Can be updated independently

### Test-Driven Feature Development Walkthrough

**Planning Phase**:
1. **Define feature scope**: What should the feature do?
2. **Identify test categories**: Unit tests, integration tests, CLI tests, web tests
3. **Plan data models**: What new models or changes to existing models?

**Implementation Phase** (TDD cycle):
```bash
# Cycle 1: Data models
# Write failing model tests
pytest tests/test_models.py -k "new_feature" -v
# Implement minimal model
# Refactor and improve

# Cycle 2: Core logic
# Write failing business logic tests
pytest tests/test_core/ -k "new_feature" -v
# Implement minimal business logic
# Refactor for cleanliness

# Cycle 3: CLI integration
# Write failing CLI tests
pytest tests/test_integration.py -k "new_feature" -v
# Add CLI command/option
# Test with real examples

# Cycle 4: Web integration (if applicable)
# Write failing web API tests
pytest tests/test_web/ -k "new_feature" -v
# Add web endpoint
# Test with browser
```

**Verification Phase**:
```bash
# Full test suite
pytest tests/ -v

# Code quality
python -m ruff check . && python -m mypy src/

# Manual testing
python cross_stitch_generator.py generate test.jpg output.xlsx --new-feature
uvicorn web.main:app --reload --port 8000  # Test web interface
```

### Test Coverage Guidelines

**Target Coverage**: Maintain >95% test coverage

**Current Status**: 254/279 tests passing (~91% success rate)
- **Critical path coverage**: 100% (image processing, pattern generation, Excel output)
- **Enhancement feature coverage**: ~85% (edge modes, advanced Excel features)
- **Web interface coverage**: ~88% (API endpoints, UI interactions)

**Coverage by Component**:
- **Core modules** (`src/cross_stitch/core/`): >98% required
- **CLI interface**: >95% required
- **Data models**: >99% required (simple to test, critical for stability)
- **Web interface**: >90% acceptable
- **Utilities**: >95% required

## Approval Gates - STOP Points

**YOU MUST STOP and get explicit user approval after**:
1. Creating test files (before implementation)
2. Implementing each module (after tests pass)
3. Making significant architectural changes
4. Before modifying existing functionality
5. Before committing to git

**Never proceed to the next phase without explicit user approval.**

## Team Workflow & Communication

### Code Review Expectations

**Pre-Review Checklist**:
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Code quality checks pass: `ruff check . && mypy src/`
- [ ] Manual testing completed for both CLI and web interface (if applicable)
- [ ] Documentation updated if user-facing behavior changed
- [ ] Conventional commit messages used

**Review Focus Areas**:
- **Test coverage**: New code should have corresponding tests
- **Code style**: Follows established patterns and type hints
- **Error handling**: Proper use of custom exception hierarchy
- **Performance**: Reasonable efficiency, especially for image processing
- **User experience**: Both CLI and web interface remain intuitive

### Decision-Making Process

**Technical Decisions**:
1. **Individual contributor decisions**: Code style, internal implementation details, test approaches
2. **Team discussion required**: API changes, new dependencies, architectural modifications
3. **User consultation needed**: User interface changes, breaking CLI changes

**Architecture Changes**:
- **Minor refactoring**: Individual contributor decision, review for approval
- **Major refactoring**: Team discussion, impact assessment
- **New dependencies**: Team discussion, security and maintenance assessment
- **Breaking changes**: User consultation, migration path planning

### Issue Escalation Procedures

**Development Blockers**:
1. **Environment issues**: Check with `scripts/validate-environment.py`, consult team if unresolved
2. **Test failures**: Investigate failing tests, distinguish critical vs non-critical (see Known Issues section)
3. **Dependency conflicts**: Document issue, discuss team-wide impact before resolution
4. **Performance problems**: Profile issue, discuss optimization approach before major changes

**Priority Levels**:
- **P0 Critical**: Core functionality broken, blocks user workflow
- **P1 High**: Important features affected, workarounds exist
- **P2 Medium**: Enhancement features affected, basic functionality intact
- **P3 Low**: Minor issues, aesthetic improvements, nice-to-have features

### Contributing Guidelines

**Getting Started**:
1. **Choose appropriate task**: New contributors should start with failing tests or documentation improvements
2. **Understand existing patterns**: Review similar implementations before starting
3. **Small incremental changes**: Prefer multiple small PRs over large feature branches

**Code Standards**:
- **Type hints required**: All function signatures must include type annotations
- **Docstrings required**: All public functions need Google-style docstrings
- **Error handling**: Use custom exceptions from `src/cross_stitch/utils/exceptions.py`
- **Testing**: Follow TDD process, maintain test coverage above 95%

**Documentation Standards**:
- **User-facing changes**: Update README.md with examples and usage
- **Developer-facing changes**: Update CLAUDE.md with workflow or architecture notes
- **API changes**: Update docstrings and type hints
- **Breaking changes**: Document migration path and backwards compatibility approach

**Commit Standards**:
```bash
# Use conventional commits
feat: add support for WebP image format
fix: resolve DMC color matching edge case
docs: improve CLI examples in README
test: add integration tests for transparency handling
refactor: extract color quantization to separate module
```

**Pull Request Guidelines**:
- **Clear title**: Summarize change in <50 characters
- **Detailed description**: Explain motivation, approach, testing completed
- **Test evidence**: Include test results, manual testing notes
- **Breaking changes**: Clearly document any backwards compatibility impact

### Testing Standards for New Features

**Required Test Categories**:
1. **Unit tests**: Test individual functions and classes in isolation
2. **Integration tests**: Test feature end-to-end through CLI interface
3. **Web tests**: Test API endpoints and web interface integration (if applicable)
4. **Error handling tests**: Test failure modes and error conditions

**Test Organization**:
- **Core functionality**: `tests/test_*.py` files for each major module
- **CLI testing**: `tests/test_integration.py` for command-line interface
- **Web testing**: `tests/test_web/` directory for API and UI tests
- **Utility testing**: `tests/test_utils.py` for helper functions

**Test Data Management**:
- **Use fixtures**: Leverage `tests/conftest.py` for reusable test data
- **Small test images**: Use minimal images for fast test execution
- **Realistic scenarios**: Include tests with actual image types users will provide

## Quick Reference for Developers

### Development Task Shortcuts

| Task | Command | Notes |
|------|---------|--------|
| **Full test suite** | `pytest tests/ -v` | Expect ~254/279 passing |
| **Test specific area** | `pytest tests/test_models.py -v` | Unit tests for data models |
| **Test with coverage** | `pytest tests/ -v --cov=src/cross_stitch --cov-report=term-missing` | Coverage report |
| **Code quality check** | `ruff check . && mypy src/` | Lint + type check |
| **Format code** | `ruff format .` | Auto-format all files |
| **Environment validation** | `python scripts/validate-environment.py` | Check setup |
| **Start web dev server** | `uvicorn web.main:app --reload --port 8000` | Auto-reload on changes |
| **CLI help** | `python cross_stitch_generator.py --help` | Command reference |

### Development Environment One-Liners

```bash
# Full environment setup
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt -r requirements-web.txt

# Test-driven development cycle
pytest tests/test_models.py::test_new_feature -v && pytest tests/ -v && ruff check .

# Pre-commit quality check
pytest tests/ -v && ruff check . && ruff format . && mypy src/

# Web development cycle
uvicorn web.main:app --reload --port 8000 & pytest tests/test_web/ -v

# Troubleshoot failing tests
pytest tests/ -v --tb=short -x  # Stop on first failure with short traceback
```

### Code Navigation Shortcuts

| Looking for... | Location | Purpose |
|----------------|----------|---------|
| **Main CLI entry point** | `cross_stitch_generator.py` | User-facing command |
| **Core image processing** | `src/cross_stitch/core/image_processor.py:342` | Image loading and transformation |
| **Pattern generation orchestration** | `src/cross_stitch/core/pattern_generator.py:391` | Main processing pipeline |
| **Excel file creation** | `src/cross_stitch/core/excel_generator.py:368` | Output file generation |
| **DMC color database** | `data/dmc_colors.csv` + `src/cross_stitch/core/dmc_matcher.py` | Thread color matching |
| **Web API endpoints** | `web/routes/api.py` | HTTP API for web interface |
| **Test fixtures** | `tests/conftest.py` | Reusable test data and setup |
| **Configuration models** | `src/cross_stitch/models/config.py` | Application settings |

### Related Documentation

- **[README.md](README.md)**: User-facing installation, usage examples, and troubleshooting guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Production deployment instructions for server environments
- **Environment Validation**: `python scripts/validate-environment.py` - comprehensive setup verification
- **Test Organization**: See `tests/` directory structure for testing different components

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

## Development Environment Setup

### Environment Validation & Setup

**Primary Validation Tool**: Use `scripts/validate-environment.py` for comprehensive environment checking

```bash
# Full environment validation (recommended first step)
python scripts/validate-environment.py

# Expected output: All checks show ✅ green checkmarks
# If any show ❌ red X marks, follow the recommended fixes
```

**What the validation checks**:
- Python 3.11+ version compatibility
- Critical imports (numpy, scipy, pillow, openpyxl, fastapi, etc.)
- NumPy C extensions (performance-critical operations)
- Image processing pipeline (PIL + NumPy integration)
- Web application stack (FastAPI + Jinja2 + Pydantic)
- System libraries (libstdc++ and other native dependencies)

### Virtual Environment Setup (Project-Specific)

**Recommended approach for this project**:
```bash
# Create project-specific virtual environment
python -m venv cross-stitch-env

# Activate (choose your platform)
# Windows:
cross-stitch-env\Scripts\activate
# macOS/Linux:
source cross-stitch-env/bin/activate

# Install core dependencies
pip install -r requirements.txt

# Install web interface dependencies
pip install -r requirements-web.txt

# Install development tools
pip install pytest pytest-cov mypy ruff pre-commit
```

### Environment Validation Checklist

Use this checklist to verify your development environment:

- [ ] **Python Version**: `python --version` shows 3.11+
- [ ] **Virtual Environment**: `which python` shows venv path (not system Python)
- [ ] **Core Dependencies**: `python scripts/validate-environment.py` shows all ✅
- [ ] **CLI Interface**: `python cross_stitch_generator.py --help` works
- [ ] **Web Interface**: `uvicorn web.main:app --reload --port 8000` starts successfully
- [ ] **Tests**: `pytest tests/ -v` runs (expect 254/279 passing)
- [ ] **Code Quality**: `ruff check .` and `mypy src/` run without critical errors

### Platform-Specific Setup Notes

**Windows Development**:
- Install Visual Studio Build Tools for C++ compilation
- Use PowerShell or Command Prompt, not Git Bash for Python commands
- Consider Windows Subsystem for Linux (WSL) for Unix-like environment

**macOS Development**:
- Install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew for system dependencies if needed
- M1/M2 Macs: Some dependencies may need `--no-use-pep517` flag

**Linux Development**:
- Install build tools: `sudo apt-get install build-essential python3.11-dev`
- For RHEL/CentOS: `sudo yum install python3-devel gcc gcc-c++`
- Ensure system Python doesn't interfere with venv

### Development Dependencies Explanation

**Core Runtime** (`requirements.txt`):
- Image processing and pattern generation dependencies
- Required for both CLI and basic functionality

**Web Interface** (`requirements-web.txt`):
- FastAPI web framework and related packages
- Only needed if developing web interface features

**Development Tools** (install separately):
- `pytest`: Test runner and framework
- `pytest-cov`: Test coverage reporting
- `mypy`: Static type checking
- `ruff`: Fast linting and formatting
- `pre-commit`: Git hooks for code quality

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

**⚠️ Known Issues Action Plan**:

**24/279 Tests Failing (91% Success Rate)**:

*Critical vs Enhancement Classification*:
- **0 Critical failures**: Core functionality (image processing, pattern generation, Excel output) fully working
- **24 Enhancement failures**: Advanced features that don't affect basic operation

*Specific Failing Test Categories*:
1. **Edge Mode Processing** (12 tests): Advanced edge handling algorithms
   - **Impact**: Basic edge processing works, advanced smoothing may be suboptimal
   - **Workaround**: Use default edge mode for reliable results
   - **Priority**: Medium (quality improvement, not functionality)

2. **Excel Professional Features** (8 tests): Advanced Excel formatting and styling
   - **Impact**: Basic Excel patterns always work, some advanced formatting may be missing
   - **Workaround**: Generated Excel files are fully functional for cross-stitch use
   - **Priority**: Low (aesthetic improvement)

3. **Web Interface Edge Cases** (4 tests): Specific UI interaction scenarios
   - **Impact**: Core web functionality works, some edge case interactions may behave unexpectedly
   - **Workaround**: Refresh page if UI becomes unresponsive
   - **Priority**: Low (rare scenarios)

*Development Safety*:
- **Safe to ignore during development**: All 24 failing tests are non-critical features
- **Core pipeline integrity**: 100% of critical path tests passing
- **User-facing impact**: Minimal - users can successfully generate patterns

*Timeline & Priority*:
- **High Priority**: 0 critical issues (all resolved)
- **Medium Priority**: Edge mode improvements (planned for future enhancement)
- **Low Priority**: Excel professional formatting and web UI edge cases

**Other Non-Critical Issues**:
- **Pillow deprecation warnings**: Safe to ignore, deprecated 'mode' parameter usage
  - **Fix**: Update to newer Pillow API calls (low priority)
  - **Impact**: None on functionality
- **Web test alignment**: Some tests may need updates after recent UI changes
  - **Fix**: Review and update web-specific test expectations
  - **Impact**: Testing reliability, not user functionality

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