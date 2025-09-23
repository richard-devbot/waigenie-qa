from fastapi import APIRouter
from app.services.browser_config_service import browser_config_service

router = APIRouter()

@router.get("/available")
async def get_available_browsers():
    """
    Get list of available browsers on the system.
    
    Returns:
        Dict: Information about installed browsers
    """
    try:
        browsers_info = browser_config_service.get_installed_browsers_with_versions()
        return {
            "status": "success",
            "browsers": browsers_info,
            "default_resolution": browser_config_service.get_default_resolution()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/resolutions")
async def get_supported_resolutions():
    """
    Get list of supported browser resolutions.
    
    Returns:
        Dict: Supported resolutions
    """
    # Common resolutions for browser automation
    resolutions = [
        {"width": 1920, "height": 1080, "name": "1080p (HD)"},
        {"width": 1366, "height": 768, "name": "1366x768 (Common Laptop)"},
        {"width": 1440, "height": 900, "name": "1440x900 (WXGA+)"},
        {"width": 1536, "height": 864, "name": "1536x864 (HD+)"},
        {"width": 1280, "height": 720, "name": "720p (HD)"},
        {"width": 1600, "height": 900, "name": "1600x900 (HD+)"},
        {"width": 2560, "height": 1440, "name": "1440p (QHD)"},
        {"width": 3840, "height": 2160, "name": "4K (UHD)"}
    ]
    
    return {
        "status": "success",
        "resolutions": resolutions
    }

@router.get("/config-options")
async def get_browser_config_options():
    """
    Get available browser configuration options.
    
    Returns:
        Dict: Browser configuration options
    """
    # Supported browsers for CDP connection
    cdp_browsers = [
        {"value": "chrome", "label": "Google Chrome"},
        {"value": "edge", "label": "Microsoft Edge"},
        {"value": "chromium", "label": "Chromium"}
    ]
    
    return {
        "status": "success",
        "cdp_browsers": cdp_browsers
    }