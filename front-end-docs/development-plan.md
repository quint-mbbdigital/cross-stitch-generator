# Plan: Web Frontend Development for Cross-Stitch Generator

## Current State Assessment ✅

**The Foundation**: Excellent backend infrastructure ready for web deployment

- ✅ **CLI Functionality**: Full cross-stitch generation pipeline working perfectly
- ✅ **Test Coverage**: 92/94 tests passing (97.9% success rate)
- ✅ **Core Logic**: 4,800+ lines of clean, modular Python code
- ✅ **DMC Integration**: Color matching and Excel output with thread codes
- ✅ **Texture Detection**: Background analysis with user warnings
- ❌ **Missing**: Web interface to make this accessible to crafters

**Goal**: Transform the CLI tool into a "Modern Atelier" web application using the specified stack.

## The Plan: Modern Atelier Web Interface

### Phase 1: FastAPI Foundation & Deployment Setup
**Goal**: Create web API layer and establish Replit deployment

**Tasks**:
1. **Create FastAPI Application Structure**
   - `web/main.py` - FastAPI app entry point
   - `web/routes/` - API endpoints for pattern generation
   - `web/templates/` - Jinja2 HTML templates
   - `web/static/` - CSS, JavaScript, and asset files
   - `requirements-web.txt` - Web-specific dependencies

2. **Core API Endpoints with Concurrency Architecture**
   - `POST /upload` - Handle image upload and validation with `BytesIO` streams
   - `POST /analyze` - **NEW**: Quick texture detection before heavy processing
   - `POST /generate` - Process image with `BackgroundTasks` for CPU-bound operations
   - `GET /status/{job_id}` - **NEW**: Check generation progress
   - `GET /download/{pattern_id}` - Serve generated Excel files
   - `GET /preview/{pattern_id}` - Return optimized pattern visualization data
   - `GET /` - Main application interface

3. **Pydantic Models & Validation**
   - `PatternConfig` model with strict typing for all parameters
   - Pre-flight validation with immediate 422 feedback
   - Image dimension analysis before triggering heavy processing

4. **Replit Deployment Setup**
   - `.replit` configuration file
   - `replit.nix` for environment setup
   - GitHub sync configuration
   - `TemporaryDirectory` context managers for ephemeral file handling

**Critical Implementation Notes**:
- **Non-Blocking I/O**: Use `run_in_threadpool` for existing CLI logic to prevent event loop blocking
- **Memory Management**: Pre-processing resize step if images exceed 2000px to prevent OOM on Replit
- **Stateless Design**: Refactor core engine to accept `BytesIO` streams instead of file paths

**Test Strategy**: API endpoint testing, file upload validation, integration with existing core logic

### Phase 2: Modern Atelier UI Implementation
**Goal**: Implement the split-pane "Modern Atelier" interface

**Tasks**:
1. **Base Template Structure** (`templates/base.html`)
   - CDN links: HTMX, Alpine.js, Tailwind CSS, DaisyUI, Inter font
   - Split-pane layout: 320px sidebar + fluid canvas
   - Responsive design breakpoints

2. **Control Rail (Sidebar)** (`templates/components/sidebar.html`)
   - Parameter controls: sliders, toggles, dropdowns
   - File upload dropzone with drag/drop
   - Generate button with loading states
   - Configuration persistence using Alpine.js

3. **Canvas Viewport** (`templates/components/canvas.html`)
   - Three states: Empty (invitation), Processing, Review
   - HTML5 Canvas for pattern visualization
   - Zoom/pan controls for large patterns
   - Toggle between "Virtual Stitch" and "Symbol Map" views

4. **Visual Identity System**
   - Color palette: Cold utility colors (zinc, slate, indigo)
   - Typography: Inter font with proper hierarchy
   - Iconography: Lucide icons (stroke-based, 1.5px)

**Test Strategy**: UI component testing, responsive design validation, interaction flows

### Phase 3: Interactive Pattern Visualization
**Goal**: Canvas-based pattern rendering with advanced interactions

**Tasks**:
1. **Optimized Canvas Rendering Engine** (`static/js/canvas-renderer.js`)
   - **Data Serialization**: Use indexed color arrays instead of massive JSON objects
   - **Compact Format**: `Uint8ClampedArray` or flat arrays for 200x200+ patterns (40,000+ cells)
   - **Color Palette Map**: Colors indexed to palette to minimize memory overhead
   - Grid-based pattern display with efficient cell rendering
   - Symbol overlay system with lazy loading

2. **Advanced Interactions**
   - Zoom controls (mouse wheel, touch pinch)
   - Pan navigation (click/drag, touch scroll)
   - Cell inspection (hover tooltip with DMC info)
   - View mode toggle (colors vs symbols)

3. **Pattern Legend Panel**
   - Floating/sliding drawer from right side
   - Thread information: DMC codes, names, stitch counts
   - Color swatches and usage statistics
   - Export options integration

4. **State Management Architecture**
   - **Separation of Concerns**: Canvas data in global `PatternStore` object
   - **Alpine.js Scope**: UI visibility and overlay controls only
   - **Performance**: Prevent DOM thrashing on large pattern updates

**Critical Implementation Notes**:
- **Memory Optimization**: Send compact JSON where colors are indexed to palette map
- **Rendering Performance**: Single HTML5 Canvas with indexed color iteration
- **State Isolation**: Canvas rendering logic separate from Alpine.js reactive data

**Test Strategy**: Canvas performance testing, interaction responsiveness, mobile touch testing

### Phase 4: Progressive Enhancement & HTMX Integration
**Goal**: Single-page app feel without JavaScript complexity

**Tasks**:
1. **HTMX-Powered Interactions with OOB Updates**
   - Form submissions without page reload
   - **Out-of-Band Updates**: Use `hx-swap-oob` for simultaneous UI updates
   - Real-time progress indicators with `hx-indicator` CSS transitions
   - **Locality of Behavior**: Update thread legend + stitch count + canvas simultaneously
   - Error handling with user-friendly messages

2. **Alpine.js State Management (UI-Only Scope)**
   - **1:1 State Mapping**: Alpine.js sidebar ↔ FastAPI Pydantic models
   - Configuration parameter management
   - UI state persistence (sidebar collapse, zoom level)
   - Form validation and user feedback
   - Mobile responsive behavior (drawer toggles)

3. **Performance Optimizations**
   - Lazy loading for large patterns
   - Background image processing with progress feedback
   - Caching strategy for generated patterns
   - Progressive image enhancement
   - **Atelier Loading States**: Blur-in/opacity-fade transitions

**Critical Implementation Notes**:
- **OOB Strategy**: When pattern generates, update sidebar legend + header counts + canvas content in single response
- **Progressive Enhancement**: `hx-indicator` triggers CSS transitions for professional loading states
- **State Boundaries**: Alpine.js handles UI visibility, not pattern data storage

**Test Strategy**: Load testing, real-time interaction testing, error scenario handling

### Phase 5: Production Polish & Integration
**Goal**: Production-ready deployment with full feature integration

**Tasks**:
1. **Error Handling & User Experience**
   - Comprehensive error messages for failed uploads
   - Texture detection warnings in UI (integrated from `/analyze` endpoint)
   - Processing timeout handling
   - Graceful degradation for unsupported browsers

2. **Advanced Features Integration**
   - DMC-only color mode toggle
   - Batch processing for multiple resolutions
   - Pattern comparison views
   - Social sharing capabilities

3. **Production Deployment & Resource Management**
   - **Memory Management**: Strict RAM limits for Replit Free/Lower tiers
   - **Pre-processing Pipeline**: Automatic image resize if exceeds 2000px
   - **File Cleanup**: `TemporaryDirectory` context managers for Excel exports
   - **OOM Prevention**: Resource monitoring and graceful degradation
   - Production Replit configuration
   - GitHub Actions for automated deployment
   - Basic analytics and error tracking

**Critical Implementation Notes**:
- **Replit Resource Limits**: 4K image processing may trigger OOM killer
- **Disk Management**: Prevent legacy `.xlsx` files from filling ephemeral storage
- **Graceful Degradation**: Fallback to lower resolutions when memory constrained
- **User Feedback**: Clear messaging when images are auto-resized for memory management

**Test Strategy**: End-to-end testing, production deployment validation, user acceptance testing, resource limit testing

## Implementation Details

### Technology Stack Architecture
```
Frontend: Tailwind CSS + DaisyUI + HTMX + Alpine.js + HTML5 Canvas
Backend: FastAPI + Jinja2 Templates
Deployment: Replit + GitHub Integration
Existing Logic: Preserved Python core (src/cross_stitch/)
```

### Critical Architecture Decisions (Technical Peer Review Integration)

**1. Concurrency & Non-Blocking I/O**
- **Problem**: CLI logic is CPU-bound; running in standard FastAPI routes blocks event loop
- **Solution**: Use `BackgroundTasks` or `run_in_threadpool` for all image processing
- **Replit Optimization**: Avoid heavy task queues like Celery; FastAPI native solutions only

**2. Stateless Design for Ephemeral Environment**
- **Problem**: CLI assumes local file persistence; Replit environment is ephemeral
- **Solution**: Refactor core engine to accept `BytesIO` streams instead of file paths
- **Benefits**: Prevents "File Not Found" errors, eliminates unnecessary disk I/O

**3. Canvas Performance Optimization**
- **Problem**: 200x200 patterns = 40,000 JSON objects causing DOM thrashing
- **Solution**: Use indexed color arrays + `Uint8ClampedArray` for compact serialization
- **Architecture**: Separate `PatternStore` for canvas data, Alpine.js for UI visibility only

**4. HTMX Out-of-Band Updates**
- **Strategy**: Single response updates sidebar legend + stitch count + canvas simultaneously
- **Implementation**: `hx-swap-oob` for professional "Atelier" user experience
- **Performance**: Minimizes DOM manipulations for complex state changes

**5. Replit Resource Management**
- **Memory Limits**: Free/Lower tiers have strict RAM constraints
- **Auto-Scaling**: Pre-processing resize step if images exceed 2000px
- **Cleanup Strategy**: `TemporaryDirectory` context managers prevent disk overflow

### Key Files to Create
```
web/
├── main.py                     # FastAPI application with BackgroundTasks
├── models/
│   ├── __init__.py
│   ├── requests.py             # Pydantic models (PatternConfig, UploadRequest)
│   └── responses.py            # Response models (PatternData, AnalysisResult)
├── routes/
│   ├── __init__.py
│   ├── api.py                  # Core API endpoints (analyze, generate, status)
│   └── frontend.py             # Template serving
├── utils/
│   ├── __init__.py
│   ├── async_processing.py     # run_in_threadpool wrappers
│   └── memory_management.py    # TemporaryDirectory, image resize
├── templates/
│   ├── base.html               # Base template with CDN links
│   ├── index.html              # Main application interface
│   └── components/
│       ├── sidebar.html        # Control rail component
│       ├── canvas.html         # Visualization viewport
│       └── modals.html         # Export and error dialogs
├── static/
│   ├── css/
│   │   └── custom.css          # Custom styles beyond Tailwind
│   ├── js/
│   │   ├── pattern-store.js    # Separate canvas data management
│   │   ├── canvas-renderer.js  # Optimized pattern visualization
│   │   ├── interactions.js     # UI interactions with OOB updates
│   │   └── upload-handler.js   # File upload logic
│   └── icons/
└── requirements-web.txt        # Web dependencies (FastAPI, Pydantic, etc.)

.replit                         # Replit configuration
replit.nix                      # Environment setup
```

### UI Component Specifications

**Split-Pane Layout**:
- Sidebar: `w-80` (320px), `bg-zinc-50`, `border-r border-zinc-200`
- Canvas: `flex-1`, `bg-white` with optional dot grid pattern
- Mobile: Sidebar becomes slide-over sheet

**Generate Button**:
- `bg-indigo-600 text-white rounded-md shadow-sm`
- States: Default, Loading (spinner), Disabled
- Sticky footer in sidebar or navbar placement

**File Upload Dropzone**:
- `border-dashed border-2 border-zinc-300 rounded-xl`
- Drag-over: `border-indigo-500 bg-indigo-50/20`
- Center-positioned with clear affordance

### Integration Strategy
- **Preserve Existing Logic**: Web layer wraps existing `src/cross_stitch/` modules
- **API Design**: RESTful endpoints that mirror CLI functionality
- **File Handling**: Temporary file storage with cleanup
- **Error Propagation**: Convert Python exceptions to user-friendly messages

## Success Criteria
1. ✅ Modern, professional web interface matching "Atelier" aesthetic
2. ✅ Full feature parity with CLI (all configuration options available)
3. ✅ Real-time pattern generation with progress feedback
4. ✅ Interactive pattern visualization (zoom, pan, mode toggle)
5. ✅ Mobile-responsive design with touch-friendly interactions
6. ✅ Deployed on Replit with GitHub integration
7. ✅ DMC color information displayed in UI and exports
8. ✅ Texture detection warnings integrated into workflow

## Deployment Strategy
**GitHub → Replit Flow**:
1. Push web frontend code to existing GitHub repository
2. Import repository into Replit using "Import from GitHub"
3. Configure `.replit` for FastAPI startup
4. Set up automatic sync for continuous deployment
5. Configure domain and SSL for production access

## Technical Peer Review Integration Summary

**Key Improvements Integrated**:

1. **API Architecture**: Added `/analyze` endpoint for pre-processing texture detection
2. **Concurrency Model**: `BackgroundTasks` and `run_in_threadpool` for CPU-bound operations
3. **Data Models**: Pydantic `PatternConfig` with strict validation and immediate 422 feedback
4. **Canvas Optimization**: Indexed color arrays + `Uint8ClampedArray` for 200x200+ patterns
5. **HTMX Strategy**: Out-of-Band updates for simultaneous UI state changes
6. **Memory Management**: Pre-processing resize, `TemporaryDirectory` cleanup, OOM prevention
7. **State Architecture**: Separate canvas data storage from Alpine.js UI management

**Executive Implementation Note**: Prioritize **non-blocking I/O** for image processing core. Maintain **1:1 state mapping** between Alpine.js sidebar and FastAPI Pydantic models. Optimize for **rendering performance** with indexed color arrays for high-density patterns (200x200+) without UI lag.

## Risk Mitigation
- **Incremental Development**: Build API layer first, then UI components
- **Preserve Core Logic**: Zero modifications to existing `src/cross_stitch/` code
- **Fallback Strategy**: CLI remains fully functional if web layer fails
- **Performance**: Canvas optimization for large pattern rendering with memory constraints
- **Browser Compatibility**: Progressive enhancement with graceful degradation
- **Resource Management**: Automatic scaling for Replit environment limits