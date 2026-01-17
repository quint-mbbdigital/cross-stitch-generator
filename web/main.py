"""FastAPI application entry point."""
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime

from web.routes import api, frontend

# Configure logging with emojis for better readability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Cross-Stitch Generator",
    description="Convert images to cross-stitch patterns",
    version="1.0.0"
)

# Application metrics
_start_time = datetime.now()
_request_count = 0


@app.middleware("http")
async def count_requests(request, call_next):
    global _request_count
    _request_count += 1
    response = await call_next(request)
    return response

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


@app.get("/metrics")
async def metrics():
    """Basic metrics for monitoring."""
    uptime = (datetime.now() - _start_time).total_seconds()
    return {
        "uptime_seconds": uptime,
        "requests_total": _request_count,
        "active_jobs": len(api._jobs) if hasattr(api, '_jobs') else 0
    }