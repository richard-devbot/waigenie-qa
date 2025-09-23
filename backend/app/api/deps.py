from fastapi import Depends, HTTPException, status
from typing import Generator
import os
from app.config.settings import settings

def get_settings():
    return settings

def verify_api_key(provider: str) -> Generator[None, None, None]:
    """
    Dependency to verify API key is set for the specified provider
    """
    api_key_map = {
        "Google": settings.GOOGLE_API_KEY,
        "OpenAI": settings.OPENAI_API_KEY,
        "Anthropic": settings.ANTHROPIC_API_KEY,
        "Groq": settings.GROQ_API_KEY
    }
    
    api_key = api_key_map.get(provider)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key for {provider} not configured"
        )
    
    # Additional validation could be added here
    yield