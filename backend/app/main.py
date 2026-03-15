import asyncio
import logging
import os
import sys
import platform
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1 import api_router
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Set event loop policy for Windows to avoid subprocess issues (centralised here only)
if platform.system() == "Windows":
    if sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    else:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def _get_allowed_origins() -> list[str]:
    """Read allowed CORS origins from ALLOWED_ORIGINS env var (comma-separated).
    Falls back to localhost dev origins only — never a wildcard with credentials.
    """
    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    if env_origins.strip():
        return [o.strip() for o in env_origins.split(",") if o.strip()]
    return [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SDET-GENIE backend...")
    yield
    logger.info("Shutting down SDET-GENIE backend...")

def create_app() -> FastAPI:
    app = FastAPI(
        title="SDET-GENIE API",
        description="AI-powered QA automation framework API",
        version="1.0.0",
        lifespan=lifespan
    )

    allowed_origins = _get_allowed_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        return {"message": "Welcome to SDET-GENIE API", "version": "1.0.0"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "SDET-GENIE"}
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )