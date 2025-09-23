#!/usr/bin/env python3
"""
Demo script showcasing the upgraded parallel browser execution service with enhanced features
from the friend's implementation.
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
    """Main function to demonstrate parallel browser execution."""
    print("🚀 Starting upgraded parallel browser execution demo...")
    
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
            
            # Display combined interactions
            combined_interactions = parallel_results["combined_interactions"]
            print(f"\n📈 Combined Interactions:")
            print(f"  Total Interactions: {combined_interactions['total_interactions']}")
            print(f"  Unique Elements: {combined_interactions['unique_elements']}")
            print(f"  Action Types: {', '.join(combined_interactions['action_types'])}")
            
            # Display execution metrics
            metrics = combined_interactions["execution_metrics"]
            print(f"\n⏱️  Execution Metrics:")
            print(f"  Total Agents: {metrics['total_agents']}")
            print(f"  Completed Agents: {metrics['completed_agents']}")
            print(f"  Failed Agents: {metrics['failed_agents']}")
            print(f"  Average Execution Time: {metrics['average_execution_time']:.2f}s")
            print(f"  Total Interactions: {metrics['total_interactions']}")
            print(f"  Interaction Rate: {metrics['interaction_rate']:.2f} interactions/second")
            
            # Display framework exports
            framework_exports = parallel_results["framework_exports"]
            print(f"\n📦 Framework Exports:")
            for framework, data in framework_exports.items():
                print(f"  {framework.capitalize()}: {len(data['test_steps'])} test steps, {len(data['page_objects'])} page objects")
        else:
            print(f"❌ Execution failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🏁 Demo completed!")

if __name__ == "__main__":
    asyncio.run(main())