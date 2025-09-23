"""Test script to verify CDP connection is working properly."""

import asyncio
from browser_use import BrowserProfile, BrowserSession

async def test_cdp_connection():
    """Test CDP connection."""
    print("🚀 Testing CDP Connection")
    print()
    
    try:
        # Create browser profile
        browser_profile = BrowserProfile(
            headless=False,
            window_size={"width": 1280, "height": 720}
        )
        
        # Create browser session
        browser_session = BrowserSession(browser_profile=browser_profile)
        
        # Start the browser session
        print("Starting browser session...")
        await browser_session.start()
        print("Browser session started successfully!")
        
        # Wait a moment for the browser to fully initialize
        await asyncio.sleep(3)
        
        # Check CDP connection
        print("Checking CDP connection...")
        if (hasattr(browser_session, '_cdp_client_root') and 
            browser_session._cdp_client_root and
            hasattr(browser_session._cdp_client_root, 'is_connected') and
            browser_session._cdp_client_root.is_connected()):
            print("✅ CDP client is connected!")
            
            # Test the connection with a simple command
            try:
                targets = await browser_session._cdp_client_root.send.Target.getTargets()
                if targets and 'targetInfos' in targets:
                    print("✅ CDP connection test successful!")
                    print(f"   Found {len(targets['targetInfos'])} targets")
                    for i, target in enumerate(targets['targetInfos'][:3]):  # Show first 3 targets
                        print(f"   Target {i+1}: {target['url']}")
                else:
                    print("❌ CDP connection test failed - invalid response")
            except Exception as test_e:
                print(f"❌ CDP connection test failed: {test_e}")
        else:
            print("❌ CDP client is not connected!")
            print(f"   _cdp_client_root: {hasattr(browser_session, '_cdp_client_root')}")
            if hasattr(browser_session, '_cdp_client_root'):
                print(f"   _cdp_client_root value: {browser_session._cdp_client_root}")
                if browser_session._cdp_client_root:
                    print(f"   is_connected: {hasattr(browser_session._cdp_client_root, 'is_connected')}")
                    if hasattr(browser_session._cdp_client_root, 'is_connected'):
                        print(f"   is_connected value: {browser_session._cdp_client_root.is_connected()}")
        
        # Clean up
        print("Cleaning up...")
        await browser_session.stop()
        print("✅ Cleanup completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_cdp_connection())