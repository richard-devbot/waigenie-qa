#!/usr/bin/env python3
"""
Final test to verify the complete fix works correctly.
"""

import re

def test_complete_fix():
    """Test the complete fix with realistic scenarios."""
    
    # Realistic test scenarios that would come from the Gherkin service
    test_scenarios = [
        # Scenario with existing properly formatted entry point URL
        """@login @smoke @regression
Scenario: Successful login with valid credentials
  Given I am on "https://www.saucedemo.com/"
  When I enter username "standard_user" and password "secret_sauce"
  Then I should be redirected to the inventory page""",
        
        # Scenario with URL in Given step but not properly formatted
        """@inventory @regression
Scenario: Add item to cart
  Given I am on https://www.saucedemo.com/inventory.html
  When I click the "Add to cart" button for "Sauce Labs Backpack"
  Then the cart badge should show "1\"""",
        
        # Scenario without any URL
        """@cart @negative
Scenario: Error message for empty cart
  Given I am on the cart page
  When I click "Checkout"
  Then I should see error message "Cannot checkout with empty cart\"""",
        
        # Scenario with URL in middle of text
        """@checkout @regression
Scenario: Complete checkout process
  Given I am logged in as "standard_user"
  And I am on https://www.saucedemo.com/cart.html
  When I click "Checkout"
  And I fill in checkout information
  Then I should be on https://www.saucedemo.com/checkout-complete.html"""
    ]
    
    print("Testing complete fix with realistic scenarios:")
    print("=" * 60)
    
    for i, test_script in enumerate(test_scenarios, 1):
        print(f"Test Scenario {i}:")
        print("Original:")
        print(test_script)
        print("\nProcessed:")
        
        # Apply the exact same logic as in our fix
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
        print("-" * 40)

if __name__ == "__main__":
    test_complete_fix()