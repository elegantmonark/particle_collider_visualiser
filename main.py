"""
Collider Viz - Particle Collision Event Display

FastAPI application serving a 3D particle collision visualizer
with physics-based event generation.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from physics import generate_event, generate_batch, PARTICLES, DETECTOR

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Collider Viz - Particle Collision Event Display",
    description="3D visualization of particle physics collision events.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "collider-viz"}


@app.get("/api/event")
async def get_event(type: str | None = None):
    """Generate a single collision event."""
    try:
        event = generate_event(type)
        return event
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/batch")
async def get_batch(n: int = 20):
    """Generate a batch of collision events."""
    n = min(max(n, 1), 100)
    try:
        events = generate_batch(n)
        return {"events": events, "count": len(events)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/particles")
async def get_particles():
    """Return particle type catalogue."""
    return {"particles": PARTICLES}


@app.get("/api/detector")
async def get_detector():
    """Return detector geometry."""
    return {"detector": DETECTOR}



