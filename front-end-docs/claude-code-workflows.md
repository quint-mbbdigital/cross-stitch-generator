# Claude Code Workflows for Cross-Stitch Web Development

This document provides three workflow patterns for executing the development plan with Claude Code, ranging from simple sequential execution to advanced parallel sub-agent orchestration.

---

## Workflow 1: Sequential Execution (Solo Agent)

**Best for:** Learning the codebase, careful iteration, limited compute.

### Setup

```bash
cd ~/projects/cross-stitch-generator
claude
```

### Execution Pattern

Paste each phase as a single prompt. Wait for checkpoint confirmation before proceeding.

```
Phase 0: Execute all tasks in Phase 0 of the development plan 
(cross-stitch-web-development-plan.md). Create all files as specified. 
Run the checkpoint commands and report pass/fail status.
```

After checkpoint passes:

```
Phase 1: Execute all tasks in Phase 1. Create the FastAPI foundation 
with all models, routes, and utilities. Run checkpoint commands.
```

Continue through Phase 4.

### Session Management

For long sessions, use checkpoints to save state:

```bash
# Before ending session
git add -A && git commit -m "Checkpoint: Phase N complete"

# Resume later
claude
> "Continue from Phase N+1. The repository has Phase N complete and committed."
```

---

## Workflow 2: Task-Based Execution (Sub-Agent Spawning)

**Best for:** Medium parallelism, maintaining oversight, interactive development.

### Setup

```bash
cd ~/projects/cross-stitch-generator
claude
```

### Execution Pattern

Use Claude Code's `/task` command to spawn focused sub-agents for independent work units.

#### Phase 1 Example (3 parallel sub-agents)

```
I'm executing Phase 1 of the web development plan. Spawn three sub-agents:

/task "Create Pydantic models in web/models/requests.py and web/models/responses.py 
exactly as specified in the development plan Phase 1.2"

/task "Create async utilities in web/utils/async_processing.py and 
web/utils/memory_management.py exactly as specified in Phase 1.3"

/task "Create route files web/routes/api.py and web/routes/frontend.py 
exactly as specified in Phase 1.4 and 1.5"
```

After sub-agents complete, the main agent integrates:

```
Sub-agents have completed their tasks. Now:
1. Create web/main.py to wire everything together (Phase 1.6)
2. Run the Phase 1 checkpoint commands
3. Report any integration issues
```

#### Phase 2 Example (4 parallel sub-agents)

```
Spawn four sub-agents for Phase 2 templates:

/task "Create web/templates/base.html with all CDN links, Tailwind config, 
and Alpine.js appState() function as specified in Phase 2.1"

/task "Create web/templates/components/sidebar.html with all parameter 
controls exactly as specified in Phase 2.3"

/task "Create web/templates/components/canvas.html with empty state, 
loading state, and pattern canvas as specified in Phase 2.4"

/task "Create web/templates/components/legend.html with thread list 
display as specified in Phase 2.5"
```

Integration:

```
Sub-agents complete. Now create web/templates/index.html that includes 
all components (Phase 2.2) and run the Phase 2 checkpoint.
```

---

## Workflow 3: Parallel Agent Swarm (Maximum Parallelism)

**Best for:** Fast execution, CI/CD pipelines, experienced users.

This workflow uses Claude Code's headless mode to run multiple independent agents simultaneously, with a coordinator agent managing state.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      COORDINATOR AGENT                          │
│  - Reads development plan                                       │
│  - Spawns worker agents                                         │
│  - Monitors completion                                          │
│  - Runs integration & checkpoints                               │
└─────────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
    │ Worker  │   │ Worker  │   │ Worker  │   │ Worker  │
    │ Agent 1 │   │ Agent 2 │   │ Agent 3 │   │ Agent 4 │
    │ Models  │   │ Utils   │   │ Routes  │   │Templates│
    └─────────┘   └─────────┘   └─────────┘   └─────────┘
```

### Setup: Create Orchestration Script

**File:** `scripts/parallel-build.sh`

```bash
#!/bin/bash
# Parallel agent orchestration for cross-stitch web development
# Usage: ./scripts/parallel-build.sh [phase]

set -e
PROJECT_ROOT=$(pwd)
LOG_DIR="$PROJECT_ROOT/.build-logs"
mkdir -p "$LOG_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[ORCHESTRATOR]${NC} $1"; }
warn() { echo -e "${YELLOW}[ORCHESTRATOR]${NC} $1"; }
error() { echo -e "${RED}[ORCHESTRATOR]${NC} $1"; }

# Phase 1: Parallel Foundation Build
phase1_parallel() {
    log "Starting Phase 1: FastAPI Foundation (4 parallel agents)"
    
    # Agent 1: Pydantic Models
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/models/ with requests.py and responses.py
    
    Create these files with EXACT content from the development plan Phase 1.2:
    - web/models/__init__.py (empty)
    - web/models/requests.py (PatternConfig, enums)
    - web/models/responses.py (AnalysisResult, ThreadInfo, PatternData)
    
    After creating files, output: AGENT1_COMPLETE
    " > "$LOG_DIR/agent1.log" 2>&1 &
    PID1=$!
    
    # Agent 2: Async Utilities
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/utils/ with async processing utilities
    
    Create these files with EXACT content from the development plan Phase 1.3:
    - web/utils/__init__.py (empty)
    - web/utils/async_processing.py (run_in_threadpool, process_upload)
    - web/utils/memory_management.py (ephemeral_workspace, estimate_memory)
    
    After creating files, output: AGENT2_COMPLETE
    " > "$LOG_DIR/agent2.log" 2>&1 &
    PID2=$!
    
    # Agent 3: API Routes
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/routes/api.py with all API endpoints
    
    Create these files with EXACT content from the development plan Phase 1.4:
    - web/routes/__init__.py (empty)
    - web/routes/api.py (upload, generate, download endpoints)
    
    After creating files, output: AGENT3_COMPLETE
    " > "$LOG_DIR/agent3.log" 2>&1 &
    PID3=$!
    
    # Agent 4: Frontend Routes
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/routes/frontend.py with template serving
    
    Create this file with EXACT content from the development plan Phase 1.5:
    - web/routes/frontend.py (index route with Jinja2)
    
    After creating file, output: AGENT4_COMPLETE
    " > "$LOG_DIR/agent4.log" 2>&1 &
    PID4=$!
    
    # Wait for all agents
    log "Waiting for agents: $PID1 $PID2 $PID3 $PID4"
    wait $PID1 $PID2 $PID3 $PID4
    
    # Check completion
    for i in 1 2 3 4; do
        if grep -q "AGENT${i}_COMPLETE" "$LOG_DIR/agent${i}.log"; then
            log "Agent $i completed successfully"
        else
            error "Agent $i may have failed. Check $LOG_DIR/agent${i}.log"
        fi
    done
    
    # Integration agent
    log "Running integration agent for web/main.py"
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/main.py that wires together all components
    
    The following files should already exist:
    - web/models/requests.py
    - web/models/responses.py
    - web/utils/async_processing.py
    - web/utils/memory_management.py
    - web/routes/api.py
    - web/routes/frontend.py
    
    Create web/main.py with EXACT content from development plan Phase 1.6.
    Then run the Phase 1 checkpoint commands and report results.
    "
}

# Phase 2: Parallel Template Build
phase2_parallel() {
    log "Starting Phase 2: Templates (5 parallel agents)"
    
    # Agent 1: Base Template
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/templates/base.html
    
    Create with EXACT content from development plan Phase 2.1.
    Include all CDN links, Tailwind config, Alpine.js appState().
    
    After creating file, output: AGENT1_COMPLETE
    " > "$LOG_DIR/phase2_agent1.log" 2>&1 &
    PID1=$!
    
    # Agent 2: Sidebar
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/templates/components/sidebar.html
    
    Create with EXACT content from development plan Phase 2.3.
    All sliders, toggles, DMC options, Generate button.
    
    After creating file, output: AGENT2_COMPLETE
    " > "$LOG_DIR/phase2_agent2.log" 2>&1 &
    PID2=$!
    
    # Agent 3: Canvas
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/templates/components/canvas.html
    
    Create with EXACT content from development plan Phase 2.4.
    Empty state dropzone, loading spinner, pattern canvas.
    
    After creating file, output: AGENT3_COMPLETE
    " > "$LOG_DIR/phase2_agent3.log" 2>&1 &
    PID3=$!
    
    # Agent 4: Legend
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/templates/components/legend.html
    
    Create with EXACT content from development plan Phase 2.5.
    Thread list with swatches, DMC codes, stitch counts.
    
    After creating file, output: AGENT4_COMPLETE
    " > "$LOG_DIR/phase2_agent4.log" 2>&1 &
    PID4=$!
    
    # Agent 5: Static CSS
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/static/css/custom.css
    
    Create custom CSS for Aida cloth grid pattern, mobile responsive 
    styles, and touch-friendly controls as mentioned in the plan.
    
    After creating file, output: AGENT5_COMPLETE
    " > "$LOG_DIR/phase2_agent5.log" 2>&1 &
    PID5=$!
    
    wait $PID1 $PID2 $PID3 $PID4 $PID5
    
    # Integration
    log "Running integration agent for index.html"
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/templates/index.html
    
    Create with EXACT content from development plan Phase 2.2.
    Include all components via Jinja2 include.
    Run Phase 2 checkpoint and report.
    "
}

# Phase 3: Parallel JavaScript Build
phase3_parallel() {
    log "Starting Phase 3: JavaScript (3 parallel agents)"
    
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/static/js/pattern-store.js
    EXACT content from Phase 3.1.
    After creating, output: AGENT1_COMPLETE
    " > "$LOG_DIR/phase3_agent1.log" 2>&1 &
    PID1=$!
    
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/static/js/upload-handler.js
    EXACT content from Phase 3.2.
    After creating, output: AGENT2_COMPLETE
    " > "$LOG_DIR/phase3_agent2.log" 2>&1 &
    PID2=$!
    
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Create web/static/js/interactions.js
    EXACT content from Phase 3.3.
    After creating, output: AGENT3_COMPLETE
    " > "$LOG_DIR/phase3_agent3.log" 2>&1 &
    PID3=$!
    
    wait $PID1 $PID2 $PID3
    
    # Integration: Update base.html
    log "Running integration agent to update base.html with script includes"
    claude --print "
    Working directory: $PROJECT_ROOT
    Task: Update web/templates/base.html to include the JavaScript files.
    Add script tags before </body> as specified in Phase 3.4.
    Run Phase 3 checkpoint and report.
    "
}

# Main execution
case "${1:-all}" in
    phase1) phase1_parallel ;;
    phase2) phase2_parallel ;;
    phase3) phase3_parallel ;;
    all)
        phase1_parallel
        phase2_parallel
        phase3_parallel
        log "All phases complete. Run Phase 4 manually for polish."
        ;;
    *)
        echo "Usage: $0 [phase1|phase2|phase3|all]"
        exit 1
        ;;
esac
```

### Alternative: Pure Claude Code Sub-Agent Approach

If you prefer staying entirely within Claude Code's interactive mode, use this coordinator prompt:

```
You are the COORDINATOR AGENT for building the cross-stitch web frontend.

Your job is to:
1. Read the development plan
2. Spawn sub-agents for parallelizable work using /task
3. Wait for completion signals
4. Run integration and checkpoints
5. Proceed to next phase only after checkpoint passes

PHASE 1 EXECUTION:

Spawn these sub-agents simultaneously:

/task "WORKER-MODELS: Create web/models/requests.py and web/models/responses.py 
with exact content from Phase 1.2 of the development plan. When complete, 
create a file .completion/models-done with content 'COMPLETE'."

/task "WORKER-UTILS: Create web/utils/async_processing.py and 
web/utils/memory_management.py with exact content from Phase 1.3. 
When complete, create .completion/utils-done with 'COMPLETE'."

/task "WORKER-ROUTES: Create web/routes/api.py and web/routes/frontend.py 
with exact content from Phase 1.4-1.5. 
When complete, create .completion/routes-done with 'COMPLETE'."

After spawning, poll for completion files, then integrate with web/main.py.
```

### Monitoring Parallel Execution

While agents run, monitor progress:

```bash
# Watch log directory
watch -n 2 'ls -la .build-logs/ && tail -5 .build-logs/*.log'

# Check for completion markers
watch -n 2 'grep -l COMPLETE .build-logs/*.log | wc -l'

# Monitor file creation
watch -n 2 'find web/ -type f -newer .build-logs/start-marker 2>/dev/null'
```

---

## Workflow 4: CI/CD Pipeline Integration

**Best for:** Automated builds, PR validation, deployment pipelines.

### GitHub Actions with Parallel Agents

**File:** `.github/workflows/claude-build.yml`

```yaml
name: Claude Code Build

on:
  workflow_dispatch:
    inputs:
      phase:
        description: 'Phase to build (1-4 or all)'
        required: true
        default: 'all'

jobs:
  # Parallel foundation jobs
  models:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Models
        run: |
          claude --print "Create web/models/ as specified in Phase 1.2" \
            > models-output.txt
      - uses: actions/upload-artifact@v4
        with:
          name: models
          path: web/models/

  utils:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Utils
        run: |
          claude --print "Create web/utils/ as specified in Phase 1.3" \
            > utils-output.txt
      - uses: actions/upload-artifact@v4
        with:
          name: utils
          path: web/utils/

  routes:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Routes
        run: |
          claude --print "Create web/routes/ as specified in Phase 1.4-1.5" \
            > routes-output.txt
      - uses: actions/upload-artifact@v4
        with:
          name: routes
          path: web/routes/

  # Integration job - depends on parallel jobs
  integrate:
    needs: [models, utils, routes]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
      - name: Integrate
        run: |
          # Move artifacts into place
          mv models/* web/models/
          mv utils/* web/utils/
          mv routes/* web/routes/
          
          # Run integration agent
          claude --print "Create web/main.py and run Phase 1 checkpoint"
      - name: Test
        run: |
          pip install -r requirements-web.txt
          uvicorn web.main:app &
          sleep 5
          curl -f http://localhost:8000/health
```

---

## Quick Reference: Which Workflow When?

| Scenario | Recommended Workflow |
|----------|---------------------|
| Learning/exploring | Workflow 1 (Sequential) |
| Interactive development | Workflow 2 (Task-based) |
| Fast full build | Workflow 3 (Parallel swarm) |
| CI/CD automation | Workflow 4 (GitHub Actions) |
| Debugging issues | Workflow 1 with verbose |
| Demo/presentation | Workflow 2 for visibility |

---

## Tips for Sub-Agent Success

1. **Be explicit about file paths** — Sub-agents don't share context. Always specify absolute paths.

2. **Use completion markers** — Have agents create sentinel files so the coordinator knows they're done.

3. **Isolate dependencies** — Don't have Agent A create files that Agent B needs to import. Handle imports in integration.

4. **Log everything** — Redirect output to log files for debugging.

5. **Checkpoint before integration** — Verify each sub-agent's output before wiring together.

6. **Handle failures gracefully** — Check for completion markers and re-run failed agents.

```bash
# Example: Re-run failed agent
if ! grep -q "COMPLETE" .build-logs/agent2.log; then
    warn "Agent 2 failed, retrying..."
    claude --print "..." > .build-logs/agent2.log 2>&1
fi
```
