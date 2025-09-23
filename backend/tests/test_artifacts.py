#!/usr/bin/env python3
"""Test script to verify artifact generation and display in parallel browser execution."""

import asyncio
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app.services.browser_execution_service import browser_execution_service

async def test_parallel_execution_with_artifacts():
    """Test parallel browser execution with artifact generation."""
    
    # Sample Gherkin scenarios for testing
    test_scenarios = [
        """Scenario: Search for Python documentation
    Given I am on "https://www.python.org"
    When I search for "documentation"
    Then I should see search results""",
        
        """Scenario: Check Python downloads page
    Given I am on "https://www.python.org/downloads/"
    When I look at the download options
    Then I should see the latest Python version"""
    ]
    
    try:
        print("Starting parallel browser execution test with artifact generation...")
        
        # Execute parallel browser tests with artifact generation
        result = await browser_execution_service.execute_parallel_browser_tests(
            test_scripts=test_scenarios,
            provider="Google",
            model="gemini-2.0-flash",
            browser_name="chrome",
            vision_enabled=True
        )
        
        print("Parallel execution completed successfully!")
        print(f"Session ID: {result.get('results', {}).get('session_id', 'N/A')}")
        print(f"Agent count: {result.get('results', {}).get('agent_count', 0)}")
        print(f"Completed agents: {result.get('results', {}).get('completed_agents', 0)}")
        
        # Check artifact information in results
        agent_results = result.get('results', {}).get('agent_results', [])
        for i, agent_result in enumerate(agent_results):
            print(f"\nAgent {i+1} artifacts:")
            artifacts = agent_result.get('artifacts', {})
            print(f"  GIF path: {artifacts.get('gif_path', 'N/A')}")
            print(f"  Video directory: {artifacts.get('video_dir', 'N/A')}")
            print(f"  Traces directory: {artifacts.get('traces_dir', 'N/A')}")
            print(f"  HAR path: {artifacts.get('har_path', 'N/A')}")
            
            # Check if GIF file exists
            gif_path = artifacts.get('gif_path')
            if gif_path and os.path.exists(gif_path):
                print(f"  GIF file exists: YES")
            elif gif_path:
                print(f"  GIF file exists: NO (expected path: {gif_path})")
            else:
                print(f"  GIF file exists: N/A")
        
        return result
        
    except Exception as e:
        print(f"Error during parallel execution: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_parallel_execution_with_artifacts())
    
    if result:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed!")
        sys.exit(1)