import secrets
from fastapi import Header, HTTPException, status
from app.config.settings import settings


def get_settings():
    return settings


async def verify_api_key(x_api_key: str = Header(default="")) -> None:
    """
    FastAPI dependency to verify the X-API-Key request header.
    When settings.API_KEY_REQUIRED is False (default for dev), the check is skipped.
    Uses secrets.compare_digest to prevent timing-based attacks.
    """
    if not settings.API_KEY_REQUIRED:
        return
    if not secrets.compare_digest(x_api_key, settings.SECRET_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
