"""
LeadSync Agent — FastAPI Application

Main entry point. Configures CORS, routes, lifespan events,
and serves the React frontend as static files.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import get_settings
from app.routes.chat import router as chat_router
from app.routes.sessions import router as sessions_router
from app.services.mongodb import ping_mongo, close_mongo_client

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-30s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    settings = get_settings()
    logger.info(f"🚀 Starting {settings.APP_NAME}")

    # Test MongoDB connection
    mongo_ok = await ping_mongo()
    if mongo_ok:
        logger.info("✅ MongoDB connected")
    else:
        logger.warning("⚠️  MongoDB not reachable — some features may not work")

    yield

    # Shutdown
    await close_mongo_client()
    logger.info("👋 Shutdown complete")


# ── App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="LeadSync Agent API",
    description=(
        "AI-powered visiting card digitization and voice-note-linked contact management. "
        "Orchestrated by a single LangGraph agent with human-in-the-loop confirmation."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ───────────────────────────────────────────────────────
app.include_router(chat_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")


# ── Health Check ─────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    mongo_ok = await ping_mongo()
    return {
        "status": "healthy" if mongo_ok else "degraded",
        "service": "LeadSync Agent",
        "mongodb": "connected" if mongo_ok else "disconnected",
    }


# ── Serve React Frontend ────────────────────────────────────────────
# In production, the built React app is served as static files.
# The frontend build output should be at ../frontend/dist/

FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIR.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="static")

    # Catch-all: serve index.html for client-side routing
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the React SPA for any non-API route."""
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "message": "LeadSync Agent API",
            "docs": "/docs",
            "note": "Frontend not built yet. Run 'npm run build' in frontend/",
        }
