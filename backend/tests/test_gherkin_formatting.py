#!/usr/bin/env python3
"""
Test script to verify Gherkin scenario formatting in the pipeline service.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.pipeline_service import PipelineService

# Sample Gherkin scenarios as they would be returned by the Gherkin service
sample_scenarios = [
    {
        "title": "Search for browser-use documentation",
        "tags": ["@search", "@documentation"],
        "given": "I am on \"https://www.google.com\"",
        "when": "I type \"browser-use documentation\" into the search box",
        "then": "I should see search results related to browser-use",
        "and": ["I click the search button"],
        "but": "",
        "entry_point_url": "https://www.google.com"
    },
    {
        "title": "Navigate to browser-use repository",
        "tags": ["@github", "@repository"],
        "given": "I am on \"https://github.com\"",
        "when": "I type \"browser-use\" into the search box",
        "then": "I should see repositories related to browser-use",
        "and": ["I click the search button"],
        "but": "",
        "entry_point_url": "https://github.com"
    }
]

def test_formatting():
    """Test the formatting of Gherkin scenarios."""
    pipeline_service = PipelineService()
    
    # Test single scenario formatting
    print("Testing single scenario formatting:")
    single_scenario = sample_scenarios[0]
    formatted_single = pipeline_service._format_single_scenario(single_scenario)
    print(formatted_single)
    print()
    
    # Test multiple scenarios formatting
    print("Testing multiple scenarios formatting:")
    formatted_multiple = pipeline_service._format_gherkin_for_execution(sample_scenarios)
    print(formatted_multiple)
    print()
    
    # Test parallel execution formatting
    print("Testing parallel execution formatting:")
    test_scripts = []
    for scenario in sample_scenarios:
        if isinstance(scenario, str):
            test_scripts.append(scenario)
        else:
            # Format dict scenario as string
            formatted_scenario = pipeline_service._format_single_scenario(scenario)
            test_scripts.append(formatted_scenario)
    
    for i, script in enumerate(test_scripts):
        print(f"Scenario {i+1}:")
        print(script)
        print()

if __name__ == "__main__":
    test_formatting()