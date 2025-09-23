from fastapi import APIRouter, Depends, HTTPException
from app.config.settings import settings
import os

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/env")
async def get_env_vars():
    """Get environment variables for debugging purposes"""
    return {
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY[:5] + "..." if settings.GOOGLE_API_KEY else None,
        "OPENAI_API_KEY": settings.OPENAI_API_KEY[:5] + "..." if settings.OPENAI_API_KEY else None,
        "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY[:5] + "..." if settings.ANTHROPIC_API_KEY else None,
        "GROQ_API_KEY": settings.GROQ_API_KEY[:5] + "..." if settings.GROQ_API_KEY else None,
        "ENV_GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY", "")[:5] + "..." if os.environ.get("GOOGLE_API_KEY") else None
    }