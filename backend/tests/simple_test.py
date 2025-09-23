#!/usr/bin/env python3
"""
Simple test script to verify formatting of actual Gherkin scenarios without dependencies.
"""

import re
from typing import Dict, List, Optional

# Simplified version of the formatting functions from pipeline_service.py
def _extract_meaningful_url(scenario: dict) -> Optional[str]:
    """
    Extract a meaningful URL from the scenario instead of using hardcoded defaults.
    
    Args:
        scenario (dict): The scenario dictionary
        
    Returns:
        Optional[str]: A meaningful URL if found, None otherwise
    """
    # Try to extract URL from entry_point_url field
    if 'entry_point_url' in scenario and scenario['entry_point_url']:
        url = scenario['entry_point_url']
        if isinstance(url, str) and (url.startswith('http://') or url.startswith('https://')):
            return url
    
    # Try to extract URL from the given step
    if 'given' in scenario and scenario['given']:
        given_text = scenario['given']
        if isinstance(given_text, str):
            # Look for URL patterns in the given text
            url_match = re.search(r'https?://[^\s"]+', given_text)
            if url_match:
                return url_match.group(0)
        elif isinstance(given_text, list) and given_text:
            # Check first item in list for URL
            first_given = given_text[0]
            if isinstance(first_given, str):
                url_match = re.search(r'https?://[^\s"]+', first_given)
                if url_match:
                    return url_match.group(0)
    
    # Try to extract from feature or title context
    if 'feature' in scenario and scenario['feature']:
        feature = scenario['feature']
        if isinstance(feature, str):
            # Look for common application names that might indicate a URL pattern
            feature_lower = feature.lower()
            if 'ecommerce' in feature_lower or 'shop' in feature_lower:
                return "https://example-shop.com"
            elif 'bank' in feature_lower or 'finance' in feature_lower:
                return "https://example-bank.com"
            elif 'social' in feature_lower or 'media' in feature_lower:
                return "https://example-social.com"
    
    # No meaningful URL found
    return None

def _format_single_scenario(scenario: dict) -> str:
    """Format a single scenario dict as Gherkin text."""
    scenario_lines = []
    
    # Add tags if present
    if 'tags' in scenario and scenario['tags']:
        tags = ' '.join(scenario['tags']) if isinstance(scenario['tags'], list) else str(scenario['tags'])
        scenario_lines.append(tags)
    
    # Add scenario title
    scenario_lines.append(f"Scenario: {scenario.get('title', 'Untitled Scenario')}")
    
    # Add Given step with entry point URL check
    if 'given' in scenario and scenario['given']:
        given_text = scenario['given']
        # Check if we need to add an entry point URL
        has_entry_url = False
        
        if isinstance(given_text, str):
            has_entry_url = given_text.startswith("I am on ") or re.search(r'I am on "https?://[^"]+"', given_text)
            if not has_entry_url:
                # Add entry point URL as first Given step only if it's not already present
                # and if we can extract a meaningful URL from the scenario
                url = _extract_meaningful_url(scenario)
                if url:
                    scenario_lines.append(f"  Given I am on \"{url}\"")
            scenario_lines.append(f"  Given {given_text}")
        elif isinstance(given_text, list) and given_text:
            first_given = given_text[0]
            has_entry_url = first_given.startswith("I am on ") or re.search(r'I am on "https?://[^"]+"', first_given)
            if not has_entry_url:
                # Add entry point URL as first Given step only if it's not already present
                # and if we can extract a meaningful URL from the scenario
                url = _extract_meaningful_url(scenario)
                if url:
                    scenario_lines.append(f"  Given I am on \"{url}\"")
            
            for step in given_text:
                scenario_lines.append(f"  Given {step}")
    else:
        # If no Given steps exist, add a default one with entry point URL
        url = _extract_meaningful_url(scenario)
        if url:
            scenario_lines.append(f"  Given I am on \"{url}\"")
        else:
            # Only add default URL if we can't extract a meaningful one
            scenario_lines.append(f"  Given I am on \"https://example.com\"")
    
    # Add When step
    if 'when' in scenario and scenario['when']:
        scenario_lines.append(f"  When {scenario['when']}")
    
    # Add Then step
    if 'then' in scenario and scenario['then']:
        scenario_lines.append(f"  Then {scenario['then']}")
    
    # Add And steps if present
    if 'and' in scenario and scenario['and']:
        and_steps = scenario['and'] if isinstance(scenario['and'], list) else [str(scenario['and'])]
        for and_step in and_steps:
            scenario_lines.append(f"  And {and_step}")
    
    # Add But step if present
    if 'but' in scenario and scenario['but']:
        scenario_lines.append(f"  But {scenario['but']}")
    
    return '\n'.join(scenario_lines)

# Actual Gherkin scenarios as they would be returned by the Gherkin service
actual_scenarios = [
    {
        "title": "Successful login with valid credentials redirects to inventory page",
        "tags": ["@login", "@smoke", "@regression"],
        "feature": "User Login and Inventory Access",
        "given": "I am on https://www.saucedemo.com/",
        "when": "the user enters 'standard_user' in the 'Username' field",
        "then": "the user should be redirected to the inventory page 'https://www.saucedemo.com/inventory.html'",
        "and": ["the inventory page should display a list of available products"],
        "but": "",
        "entry_point_url": "https://www.saucedemo.com/"
    },
    {
        "title": "Add to cart button changes to 'Remove' for Sauce Labs Bolt T-Shirt",
        "tags": ["@inventory", "@regression", "@add_to_cart"],
        "feature": "Add and Remove Items from Cart",
        "given": "I am on https://www.saucedemo.com/inventory.html",
        "when": "the user clicks the 'Add to cart' button for 'Sauce Labs Bolt T-Shirt'",
        "then": "the 'Add to cart' button for 'Sauce Labs Bolt T-Shirt' should change to 'Remove'",
        "and": [],
        "but": "",
        "entry_point_url": "https://www.saucedemo.com/inventory.html"
    },
    {
        "title": "Cart icon displays '1' after adding Sauce Labs Bolt T-Shirt to cart",
        "tags": ["@inventory", "@regression", "@cart_badge"],
        "feature": "Add and Remove Items from Cart",
        "given": "I am on https://www.saucedemo.com/inventory.html",
        "when": "I inspect the cart icon",
        "then": "the cart icon should display a badge with '1'",
        "and": ["the 'Sauce Labs Bolt T-Shirt' is added to the cart"],
        "but": "",
        "entry_point_url": "https://www.saucedemo.com/inventory.html"
    },
    {
        "title": "Sauce Labs Bolt T-Shirt details are displayed on the cart page",
        "tags": ["@cart", "@regression", "@cart_details"],
        "feature": "Cart Page Functionality",
        "given": "I am on https://www.saucedemo.com/inventory.html",
        "when": "the user clicks the cart icon",
        "then": "the user should be redirected to the cart page 'https://www.saucedemo.com/cart.html'",
        "and": ["a 'Checkout' button should be present on the cart page"],
        "but": "",
        "entry_point_url": "https://www.saucedemo.com/inventory.html"
    },
    {
        "title": "'Remove' button changes to 'Add to cart' and cart badge disappears after removing item",
        "tags": ["@inventory", "@regression", "@remove_from_cart"],
        "feature": "Add and Remove Items from Cart",
        "given": "I am on https://www.saucedemo.com/inventory.html",
        "when": "the user clicks the 'Remove' button for 'Sauce Labs Bolt T-Shirt'",
        "then": "the 'Remove' button for 'Sauce Labs Bolt T-Shirt' should change to 'Add to cart'",
        "and": ["the cart icon badge should no longer be displayed"],
        "but": "",
        "entry_point_url": "https://www.saucedemo.com/inventory.html"
    }
]

def test_actual_scenario_formatting():
    """Test the formatting of actual Gherkin scenarios."""
    
    print("Testing actual scenario formatting:")
    print("=" * 50)
    
    # Test single scenario formatting
    for i, scenario in enumerate(actual_scenarios):
        print(f"Scenario {i+1}:")
        formatted_scenario = _format_single_scenario(scenario)
        print(formatted_scenario)
        print("-" * 30)
    
    print("\nTesting parallel execution formatting:")
    print("=" * 50)
    
    # Test parallel execution formatting
    test_scripts = []
    for scenario in actual_scenarios:
        if isinstance(scenario, str):
            test_scripts.append(scenario)
        else:
            # Format dict scenario as string
            formatted_scenario = _format_single_scenario(scenario)
            test_scripts.append(formatted_scenario)
    
    for i, script in enumerate(test_scripts):
        print(f"Test Script {i+1}:")
        print(script)
        print("-" * 30)

if __name__ == "__main__":
    test_actual_scenario_formatting()