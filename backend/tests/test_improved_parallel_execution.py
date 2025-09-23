#!/usr/bin/env python3
"""
Improved test script for parallel Gherkin scenario execution with performance optimizations.
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

# Sample Gherkin scenarios for testing - simplified for better performance
SIMPLIFIED_SCENARIOS = [
    '''Feature: Google Search
    Scenario: Search for browser-use
        Given I am on "https://www.google.com"
        When I type "browser-use" into the search box
        And I click the search button
        Then I should see search results''',
    
    '''Feature: GitHub Search
    Scenario: Search for browser-use on GitHub
        Given I am on "https://github.com"
        When I type "browser-use" into the search box
        And I click the search button
        Then I should see repositories''',
    
    '''Feature: Wikipedia Search
    Scenario: Search for artificial intelligence
        Given I am on "https://www.wikipedia.org"
        When I type "artificial intelligence" into the search box
        And I click the search button
        Then I should see the article'''
]

async def test_improved_parallel_execution():
    """Test improved parallel execution with better performance."""
    print("🚀 Testing improved parallel Gherkin scenario execution...")
    
    # Initialize the browser execution service
    execution_service = BrowserExecutionService()
    
    try:
        # Execute scenarios in parallel
        print(f"Executing {len(SIMPLIFIED_SCENARIOS)} scenarios in parallel...")
        results = await execution_service.execute_parallel_browser_tests(
            test_scripts=SIMPLIFIED_SCENARIOS,
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

async def test_sequential_execution():
    """Test sequential execution for comparison."""
    print("🚀 Testing sequential Gherkin scenario execution...")
    
    # Initialize the browser execution service
    execution_service = BrowserExecutionService()
    
    try:
        results = []
        for i, scenario in enumerate(SIMPLIFIED_SCENARIOS):
            print(f"Executing scenario {i+1}/{len(SIMPLIFIED_SCENARIOS)}...")
            result = await execution_service.execute_browser_test_direct(
                test_script=scenario,
                provider="Google",
                model="gemini-2.0-flash"
            )
            results.append(result)
            print(f"✅ Completed scenario {i+1}")
        
        print("\n✅ Sequential execution test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during sequential execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n🏁 Sequential test completed!")

if __name__ == "__main__":
    print("Choose execution mode:")
    print("1. Parallel execution (default)")
    print("2. Sequential execution")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        result = asyncio.run(test_sequential_execution())
    else:
        result = asyncio.run(test_improved_parallel_execution())
    
    sys.exit(0 if result else 1)