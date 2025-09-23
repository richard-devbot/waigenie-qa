#!/usr/bin/env python3
"""
Test script to verify the fixes for parallel browser execution.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

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

async def main():
    """Main function to test parallel browser execution."""
    print("🚀 Testing parallel browser execution fixes...")
    
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

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)