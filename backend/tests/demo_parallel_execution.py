"""
Demo script to showcase parallel browser execution functionality.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.browser_execution_service import BrowserExecutionService

async def demo_parallel_execution():
    """Demo parallel execution with sample Gherkin scenarios."""
    print("🚀 Starting Parallel Browser Execution Demo")
    
    # Initialize the browser execution service
    service = BrowserExecutionService()
    
    # Sample Gherkin scenarios
    test_scripts = [
        """@demo @parallel
Scenario: Search Google for browser automation
  Given I am on "https://www.google.com"
  When I search for "browser automation testing"
  Then I should see search results related to browser automation""",
        
        """@demo @parallel
Scenario: Visit GitHub and search for repositories
  Given I am on "https://github.com"
  When I search for "browser-use" in the search bar
  Then I should see repositories related to browser-use""",
        
        """@demo @parallel
Scenario: Check Wikipedia for testing information
  Given I am on "https://www.wikipedia.org"
  When I search for "software testing" in the search box
  Then I should be redirected to the software testing page"""
    ]
    
    print(f"📋 Running {len(test_scripts)} scenarios in parallel...")
    
    try:
        # Execute the scenarios in parallel
        result = await service.execute_parallel_browser_tests(
            test_scripts=test_scripts,
            provider="Google",
            model="gemini-2.0-flash",
            browser_name="chrome"
        )
        
        # Display results
        print("\n📊 Execution Results:")
        print(f"Status: {result['status']}")
        
        if result['status'] == 'completed':
            results_data = result['results']
            print(f"Execution Type: {results_data['execution_type']}")
            print(f"Total Agents: {results_data['agent_count']}")
            print(f"Completed Agents: {results_data['completed_agents']}")
            print(f"Failed Agents: {results_data['failed_agents']}")
            
            print("\n🤖 Agent Details:")
            for agent_result in results_data['agent_results']:
                print(f"  Agent {agent_result['agent_id'] + 1}: {agent_result['status']}")
                if agent_result['status'] == 'completed':
                    print(f"    Scenarios: {agent_result['scenarios_count']}")
                    print(f"    Execution Time: {agent_result.get('execution_time', 0):.2f}s")
                    print(f"    Interactions: {agent_result.get('interactions_count', 0)}")
                else:
                    print(f"    Error: {agent_result.get('error', 'Unknown error')}")
            
            print("\n🔗 Combined Interactions:")
            interactions = results_data['combined_interactions']
            print(f"  Total Interactions: {interactions['total_interactions']}")
            print(f"  Unique Elements: {interactions['unique_elements']}")
            print(f"  Action Types: {', '.join(interactions['action_types'])}")
            
            # Execution metrics
            if 'execution_metrics' in interactions:
                metrics = interactions['execution_metrics']
                print(f"\n📈 Execution Metrics:")
                print(f"  Average Execution Time: {metrics.get('average_execution_time', 0):.2f}s")
                print(f"  Interaction Rate: {metrics.get('interaction_rate', 0):.2f} ops/s")
                print(f"  Completed Agents: {metrics.get('completed_agents', 0)}/{metrics.get('total_agents', 0)}")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_parallel_execution())