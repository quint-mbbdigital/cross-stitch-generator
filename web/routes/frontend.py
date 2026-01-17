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