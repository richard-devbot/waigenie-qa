#!/usr/bin/env python3
"""
Test script for browser configuration enhancements
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.browser_config_service import BrowserConfigService

def test_browser_config_service():
    """Test the enhanced browser configuration service"""
    print("Testing Browser Configuration Service Enhancements")
    print("=" * 50)
    
    # Initialize the browser config service
    config_service = BrowserConfigService()
    
    # Test 1: Get vision arguments
    print("Test 1: Vision Arguments")
    vision_args = config_service.get_vision_args(vision_enabled=True)
    print(f"Vision args (enabled): {vision_args}")
    
    vision_args = config_service.get_vision_args(vision_enabled=False)
    print(f"Vision args (disabled): {vision_args}")
    print()
    
    # Test 2: Get CDP arguments
    print("Test 2: CDP Arguments")
    cdp_args = config_service.get_cdp_args(cdp_port=9222)
    print(f"CDP args (port 9222): {cdp_args}")
    
    cdp_args = config_service.get_cdp_args(cdp_port=9223)
    print(f"CDP args (port 9223): {cdp_args}")
    print()
    
    # Test 3: Get custom resolution arguments
    print("Test 3: Custom Resolution Arguments")
    resolution_args = config_service.get_custom_resolution_args(1920, 1080)
    print(f"Resolution args (1920x1080): {resolution_args}")
    
    resolution_args = config_service.get_custom_resolution_args(2560, 1440)
    print(f"Resolution args (2560x1440): {resolution_args}")
    print()
    
    # Test 4: Get all browser arguments
    print("Test 4: Combined Browser Arguments")
    all_args = config_service.get_all_browser_args(
        browser_name="chrome",
        vision_enabled=True,
        cdp_port=9222,
        custom_width=1920,
        custom_height=1080
    )
    print(f"All args for Chrome with all features enabled:")
    for arg in all_args:
        print(f"  {arg}")
    print()
    
    # Test 5: Test with different browsers
    print("Test 5: Browser-specific Arguments")
    browsers = ["chrome", "edge", "firefox", "chromium"]
    for browser in browsers:
        args = config_service.get_parallel_execution_args(browser)
        print(f"{browser.capitalize()} parallel execution args count: {len(args)}")
    print()
    
    print("All tests completed successfully!")

if __name__ == "__main__":
    test_browser_config_service()