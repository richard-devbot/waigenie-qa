#!/usr/bin/env python3
"""
Test script to verify the fix for URL extraction in parallel execution.
"""

import re

def test_url_extraction_logic():
    """Test the URL extraction logic that was added to fix the hardcoded URL issue."""
    
    # Test scenarios with proper URLs
    test_scenarios = [
        # Scenario with existing entry point URL
        """@login @smoke @regression
Scenario: Successful login with valid credentials redirects to inventory page
  Given I am on "https://www.saucedemo.com/"
  When the user enters 'standard_user' in the 'Username' field
  Then the user should be redirected to the inventory page 'https://www.saucedemo.com/inventory.html'
  And the inventory page should display a list of available products""",
        
        # Scenario without entry point URL but with URL in Given step
        """@inventory @regression @add_to_cart
Scenario: Add to cart button changes to 'Remove' for Sauce Labs Bolt T-Shirt
  Given I am on https://www.saucedemo.com/inventory.html
  When the user clicks the 'Add to cart' button for 'Sauce Labs Bolt T-Shirt'
  Then the 'Add to cart' button for 'Sauce Labs Bolt T-Shirt' should change to 'Remove'""",
        
        # Scenario without any URL
        """@cart @regression @cart_details
Scenario: Sauce Labs Bolt T-Shirt details are displayed on the cart page
  Given the user is logged in
  When the user clicks the cart icon
  Then the user should be redirected to the cart page
  And a 'Checkout' button should be present on the cart page"""
    ]
    
    print("Testing URL extraction logic:")
    print("=" * 50)
    
    for i, test_script in enumerate(test_scenarios):
        print(f"Test Scenario {i+1}:")
        print("Original:")
        print(test_script)
        print("\nProcessed:")
        
        # Apply the same logic as in the fixed code
        task = test_script
        if task and not re.search(r'I am on "https?://[^"]+"', task):
            # If no entry point URL is found, try to extract one from the task or use a default
            url_match = re.search(r'https?://[^\s"]+', task)
            if url_match:
                url = url_match.group(0)
                task = f"Given I am on \"{url}\"\n{task}"
            else:
                # Only use default if no URL can be extracted
                task = f"Given I am on \"https://example.com\"\n{task}"
        # If the task already contains an entry point URL, make sure it's properly formatted
        elif task and re.search(r'https?://[^\s"]+', task):
            # Extract the first URL found in the task
            url_match = re.search(r'https?://[^\s"]+', task)
            if url_match:
                url = url_match.group(0)
                # Make sure the task starts with the proper Given step
                if not task.strip().startswith("Given I am on"):
                    task = f"Given I am on \"{url}\"\n{task}"
        
        print(task)
        print("-" * 30)

if __name__ == "__main__":
    test_url_extraction_logic()