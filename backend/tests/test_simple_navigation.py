#!/usr/bin/env python3
"""
Simple test script to verify browser navigation fixes and execute Gherkin scenarios in parallel.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.browser.browser_manager import BrowserManager
from app.browser.agent_browser_session import AgentBrowserSession
from app.services.browser_execution_service import BrowserExecutionService

# Sample Gherkin scenarios for testing
SAMPLE_SCENARIOS = [
    '''Feature: Google Search
    Scenario: Search for browser-use documentation
        Given I am on "https://www.google.com"
        When I type "browser-use documentation" into the search box
        And I click the search button
        Then I should see search results related to browser-use''',
    
    '''Feature: GitHub Navigation
    Scenario: Navigate to browser-use repository
        Given I am on "https://github.com"
        When I type "browser-use" into the search box
        And I click the search button
        Then I should see repositories related to browser-use''',
    
    '''Feature: Wikipedia Search
    Scenario: Search for artificial intelligence
        Given I am on "https://www.wikipedia.org"
        When I type "artificial intelligence" into the search box
        And I click the search button
        Then I should see the article about artificial intelligence'''
]

async def test_parallel_gherkin_execution():
    """Test parallel execution of Gherkin scenarios."""
    print("🚀 Testing parallel Gherkin scenario execution...")
    
    # Initialize the browser execution service
    execution_service = BrowserExecutionService()
    
    try:
        # Execute scenarios in parallel
        print(f"Executing {len(SAMPLE_SCENARIOS)} scenarios in parallel...")
        results = await execution_service.execute_parallel_browser_tests(
            test_scripts=SAMPLE_SCENARIOS,
            provider="Google",
            model="gemini-2.0-flash"
        )
        
        # Display results
        print("\n📊 Execution Results:")
        print("====================")
        
        if results["status"] == "completed":
            parallel_results = results["results"]
            print(f"✅ Completed: {parallel_results['completed_agents']}/{parallel_results['agent_count']} agents")
            print(f"❌ Failed: {parallel_results['failed_agents']}/{parallel_results['agent_count']} agents")
            
            # Display individual agent results
            for agent_result in parallel_results["agent_results"]:
                print(f"\nAgent {agent_result['agent_id'] + 1}:")
                print(f"  Status: {agent_result['status']}")
                if agent_result['status'] == 'completed':
                    print(f"  Execution Time: {agent_result['execution_time']:.2f}s")
                    print(f"  Interactions: {agent_result['interactions_count']}")
                else:
                    print(f"  Error: {agent_result['error']}")
            
            print("\n✅ Parallel execution test completed successfully!")
            return True
        else:
            print(f"❌ Execution failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n🏁 Test completed!")

async def test_simple_navigation():
    """Test simple browser navigation to verify the fix."""
    print("🚀 Testing simple browser navigation...")
    
    # Initialize the browser manager
    browser_manager = BrowserManager()
    
    try:
        # Launch browser
        print("Launching browser...")
        await browser_manager.launch_browser(headless=False)
        print("Browser launched successfully!")
        
        # Wait a bit for browser to initialize
        await asyncio.sleep(3)
        
        # Register an agent
        print("Registering agent...")
        agent_session = await browser_manager.register_agent("test_agent")
        print("Agent registered successfully!")
        
        # Wait a bit for agent to initialize
        await asyncio.sleep(2)
        
        # Try to navigate to a simple URL
        print("Navigating to Google...")
        target_id = await agent_session.navigate_to_url("https://www.google.com")
        print(f"Navigation successful! Target ID: {target_id}")
        
        # Wait a bit to see the page
        await asyncio.sleep(5)
        
        # Clean up
        print("Cleaning up...")
        await browser_manager.unregister_agent("test_agent")
        print("✅ Simple navigation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during navigation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n🏁 Test completed!")

if __name__ == "__main__":
    # Run the parallel Gherkin execution test
    result = asyncio.run(test_parallel_gherkin_execution())
    sys.exit(0 if result else 1)