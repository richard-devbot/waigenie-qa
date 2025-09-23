#!/usr/bin/env python3
"""
Test script to verify formatting of actual Gherkin scenarios.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.pipeline_service import PipelineService

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
    pipeline_service = PipelineService()
    
    print("Testing actual scenario formatting:")
    print("=" * 50)
    
    # Test single scenario formatting
    for i, scenario in enumerate(actual_scenarios):
        print(f"Scenario {i+1}:")
        formatted_scenario = pipeline_service._format_single_scenario(scenario)
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
            formatted_scenario = pipeline_service._format_single_scenario(scenario)
            test_scripts.append(formatted_scenario)
    
    for i, script in enumerate(test_scripts):
        print(f"Test Script {i+1}:")
        print(script)
        print("-" * 30)

if __name__ == "__main__":
    test_actual_scenario_formatting()