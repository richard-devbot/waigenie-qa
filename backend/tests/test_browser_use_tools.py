#!/usr/bin/env python3
"""
Test script to verify the BrowserUseTools integration.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.browser.browser_tools.browser_use_tools import BrowserUseTools
from app.browser.agent_browser_session import AgentBrowserSession

async def test_browser_use_tools():
    """Test the BrowserUseTools integration."""
    print("🚀 Testing BrowserUseTools integration...")
    
    # Create an instance of BrowserUseTools
    tools = BrowserUseTools()
    
    # Check if tools are registered
    # Access the registry actions correctly
    registered_actions = {}
    if hasattr(tools, 'registry') and hasattr(tools.registry, 'registry') and hasattr(tools.registry.registry, 'actions'):
        registered_actions = tools.registry.registry.actions
    print(f"Registered actions: {list(registered_actions.keys())}")
    
    # Check if specific actions from browser-use-tools.py are available
    expected_actions = ['hover_element', 'extract_structured_data', 'take_screenshot']
    available_actions = [action for action in expected_actions if action in registered_actions]
    
    print(f"Available custom actions: {available_actions}")
    
    if len(available_actions) > 0:
        print("✅ BrowserUseTools integration successful!")
        return True
    else:
        print("❌ BrowserUseTools integration failed!")
        return False

async def test_agent_browser_session():
    """Test the AgentBrowserSession with BrowserUseTools."""
    print("\n🚀 Testing AgentBrowserSession with BrowserUseTools...")
    
    try:
        # Create an instance of AgentBrowserSession
        session = AgentBrowserSession()
        
        # Check if BrowserUseTools is available
        if hasattr(session, 'browser_use_tools'):
            print("✅ BrowserUseTools instance found in AgentBrowserSession!")
            
            # Check registered actions
            registered_actions = {}
            if (hasattr(session.browser_use_tools, 'registry') and 
                hasattr(session.browser_use_tools.registry, 'registry') and 
                hasattr(session.browser_use_tools.registry.registry, 'actions')):
                registered_actions = session.browser_use_tools.registry.registry.actions
            print(f"Registered actions in session: {list(registered_actions.keys())}")
            
            return True
        else:
            print("❌ BrowserUseTools instance not found in AgentBrowserSession!")
            return False
    except Exception as e:
        print(f"❌ Error creating AgentBrowserSession: {e}")
        return False

async def main():
    """Main test function."""
    print("🧪 Running BrowserUseTools integration tests...\n")
    
    # Test BrowserUseTools
    tools_success = await test_browser_use_tools()
    
    # Test AgentBrowserSession
    session_success = await test_agent_browser_session()
    
    if tools_success and session_success:
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n💥 Some tests failed!")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)