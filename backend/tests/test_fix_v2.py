#!/usr/bin/env python3
"""
Test script to verify the improved URL extraction logic.
"""

import re

def test_improved_url_extraction_logic():
    """Test the improved URL extraction logic."""
    
    # Test scenarios with proper URLs
    test_scenarios = [
        # Scenario with existing entry point URL (should not be modified)
        """@login @smoke @regression
Scenario: Successful login with valid credentials redirects to inventory page
  Given I am on "https://www.saucedemo.com/"
  When the user enters 'standard_user' in the 'Username' field
  Then the user should be redirected to the inventory page 'https://www.saucedemo.com/inventory.html'
  And the inventory page should display a list of available products""",
        
        # Scenario without entry point URL but with URL in Given step (should add proper Given I am on)
        """@inventory @regression @add_to_cart
Scenario: Add to cart button changes to 'Remove' for Sauce Labs Bolt T-Shirt
  Given I am on https://www.saucedemo.com/inventory.html
  When the user clicks the 'Add to cart' button for 'Sauce Labs Bolt T-Shirt'
  Then the 'Add to cart' button for 'Sauce Labs Bolt T-Shirt' should change to 'Remove'""",
        
        # Scenario without any URL (should add default)
        """@cart @regression @cart_details
Scenario: Sauce Labs Bolt T-Shirt details are displayed on the cart page
  Given the user is logged in
  When the user clicks the cart icon
  Then the user should be redirected to the cart page
  And a 'Checkout' button should be present on the cart page"""
    ]
    
    print("Testing improved URL extraction logic:")
    print("=" * 50)
    
    for i, test_script in enumerate(test_scenarios):
        print(f"Test Scenario {i+1}:")
        print("Original:")
        print(test_script)
        print("\nProcessed:")
        
        # Apply the improved logic
        task = test_script
        # Check if the task already has a properly formatted entry point URL at the beginning
        if task and not re.search(r'^\s*Given\s+I\s+am\s+on\s+"https?://[^"]+"', task, re.MULTILINE):
            # If no entry point URL is found at the beginning, try to extract one from the task or use a default
            url_match = re.search(r'https?://[^\s"]+', task)
            if url_match:
                url = url_match.group(0)
                task = f"Given I am on \"{url}\"\n{task}"
            else:
                # Only use default if no URL can be extracted
                task = f"Given I am on \"https://example.com\"\n{task}"
        
        print(task)
        print("-" * 30)

if __name__ == "__main__":
    test_improved_url_extraction_logic()