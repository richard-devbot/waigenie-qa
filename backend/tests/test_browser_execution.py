import asyncio
import sys
import platform
import os
from app.agents.browser_execution_agent import TrackingBrowserAgent
from app.utils.model_factory import get_llm_instance
from app.utils.browser_manager import BrowserManager

# Set event loop policy for Windows
if platform.system() == "Windows":
    if sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    else:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def test_browser_execution():
    """Test browser execution with a simple task."""
    # Set API key for testing (you'll need to set this in your environment)
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDCzrl0SUX6Iy2hFl7YcBIkueLQI4vcVts"  # Replace with actual key
    
    browser_manager = BrowserManager()
    agent_session = None
    
    try:
        # Get LLM instance for browser-use (not for agno)
        llm = get_llm_instance("Google", "gemini-2.0-flash", for_agno=False)
        
        if not llm:
            print("Failed to initialize LLM. Please check your API keys.")
            return
    except Exception as e:
        print(f"Error initializing LLM: {str(e)}")
        return
    
    # Create a simple test task
    test_task = """
    Scenario: Search on Google
        Given I am on the Google homepage
        When I type "SDET-GENIE" into the search box
        And I click the search button
        Then I should see search results for "SDET-GENIE"
    """
    
    try:
        print("Creating agent session...")
        agent_session = await browser_manager.get_or_create_agent_session(
            session_id="test_session",
            profile_id="test_profile",
            headless=True
        )
        print("Agent session created.")

        # Create browser agent with the created session
        browser_agent = TrackingBrowserAgent(
            task=test_task,
            llm=llm,
            browser_session=agent_session,
            highlight_elements=True,
            use_vision=True
        )
    
        print("Starting browser execution test...")
        # Run the agent
        result = await browser_agent.run(max_steps=10)
        print("Browser execution completed successfully!")
        
        # Get tracked interactions
        interactions = browser_agent.get_tracked_interactions()
        print(f"Total interactions: {interactions['total_interactions']}")
        print(f"Action types: {interactions['action_types']}")
        print(f"Unique elements: {interactions['unique_elements']}")
        
        return result
    except Exception as e:
        print(f"Error during browser execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if agent_session:
            print("Cleaning up agent session...")
            await browser_manager.cleanup_agent("test_session")
        print("Shutting down browser...")
        await browser_manager.shutdown_browser()

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_browser_execution())
    if result:
        print("Test completed successfully!")
    else:
        print("Test failed!")