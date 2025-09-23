#!/usr/bin/env python3
"""Test script to verify browser connection fixes."""

import asyncio
import sys
import os
import logging

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_browser_connection():
    """Test browser connection with improved error handling."""
    try:
        from app.browser.browser_manager import BrowserManager
        from app.services.browser_config_service import browser_config_service
        
        logger.info("Starting browser connection test...")
        
        # Create browser manager instance
        browser_manager = BrowserManager()
        
        # Detect installed browsers
        installed_browsers = browser_config_service.detect_installed_browsers()
        logger.info(f"Installed browsers: {installed_browsers}")
        
        if not installed_browsers:
            logger.error("No browsers found!")
            return False
            
        # Get the first available browser
        browser_name = list(installed_browsers.keys())[0]
        browser_path = installed_browsers[browser_name]
        logger.info(f"Using browser: {browser_name} at {browser_path}")
        
        # Try to launch browser with improved connection handling
        logger.info("Launching browser...")
        await browser_manager.launch_browser(
            headless=False,
            executable_path=browser_path,
            browser_name=browser_name,
            vision_enabled=True
        )
        
        logger.info("Browser launched successfully!")
        
        # Try to register an agent
        logger.info("Registering agent...")
        agent_session = await browser_manager.register_agent("test_agent_1")
        logger.info("Agent registered successfully!")
        
        # Clean up
        logger.info("Cleaning up...")
        await browser_manager.unregister_agent("test_agent_1")
        await browser_manager.shutdown_browser()
        
        logger.info("Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_browser_connection())
    if success:
        print("Browser connection test PASSED")
        sys.exit(0)
    else:
        print("Browser connection test FAILED")
        sys.exit(1)