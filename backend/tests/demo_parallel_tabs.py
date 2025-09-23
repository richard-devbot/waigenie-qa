"""Demo script to test parallel browser execution with tab management."""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.services.browser_execution_service import BrowserExecutionService

browser_execution_service = BrowserExecutionService()

async def demo_parallel_tabs():
    """Demo parallel execution with tab management."""
    print("🚀 Starting Parallel Browser Execution with Tab Management Demo")
    print()

    # Define test scenarios
    test_scripts = [
        """Scenario: Search for Python documentation
    Given I am on "https://www.google.com"
    When I type "Python documentation" into the search box
    And I click the search button
    Then I should see search results related to Python documentation""",
        
        """Scenario: Search for GitHub
    Given I am on "https://www.google.com"
    When I type "GitHub" into the search box
    And I click the search button
    Then I should see search results related to GitHub""",
        
        """Scenario: Search for Stack Overflow
    Given I am on "https://www.google.com"
    When I type "Stack Overflow" into the search box
    And I click the search button
    Then I should see search results related to Stack Overflow"""
    ]

    try:
        print("📋 Running 3 scenarios in parallel with tab management...")
        print()
        
        # Execute parallel browser tests with tab management
        result = await browser_execution_service.execute_parallel_browser_tests(
            test_scripts=test_scripts,
            provider="Google",
            model="gemini-2.0-flash"
        )
        
        print("✅ Demo completed successfully!")
        print()
        
        # Print summary
        if result["status"] == "completed":
            results_data = result["results"]
            print(f"📊 Execution Summary:")
            print(f"   • Total Agents: {results_data['agent_count']}")
            print(f"   • Completed: {results_data['completed_agents']}")
            print(f"   • Failed: {results_data['failed_agents']}")
            print(f"   • Session ID: {results_data['session_id']}")
            
            # Print individual agent results
            print()
            print("📋 Individual Agent Results:")
            for agent_result in results_data["agent_results"]:
                status_icon = "✅" if agent_result["status"] == "completed" else "❌"
                print(f"   {status_icon} Agent {agent_result['agent_id'] + 1}: {agent_result['status']}")
                if agent_result["status"] == "completed":
                    print(f"      • Execution Time: {agent_result['execution_time']:.2f}s")
                    print(f"      • Interactions: {agent_result['interactions_count']}")
                else:
                    print(f"      • Error: {agent_result['error']}")
        else:
            print("❌ Demo failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print("❌ Demo failed with error:", str(e))
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_parallel_tabs())