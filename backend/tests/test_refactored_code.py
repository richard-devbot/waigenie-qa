"""
Test script to verify the refactored code works correctly.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.element_tracker import ElementTracker
from app.utils.element_extractor import (
    extract_selectors_from_history, 
    analyze_actions, 
    extract_element_attributes,
    extract_all_element_details,
    get_element_statistics,
    merge_element_details,
    filter_elements_by_tag,
    filter_elements_by_interaction_count,
    format_for_frontend
)

def test_element_tracker_enhancements():
    """Test the new methods added to ElementTracker."""
    print("Testing ElementTracker enhancements...")
    
    # Create an element tracker instance
    tracker = ElementTracker()
    
    # Test that the new methods exist
    assert hasattr(tracker, 'get_element_details'), "get_element_details method missing"
    assert hasattr(tracker, 'get_all_elements'), "get_all_elements method missing"
    assert hasattr(tracker, 'get_action_sequence'), "get_action_sequence method missing"
    assert hasattr(tracker, 'get_framework_selectors'), "get_framework_selectors method missing"
    
    print("✓ ElementTracker enhancements verified")

def test_element_extractor_enhancements():
    """Test the new functions added to element_extractor."""
    print("Testing ElementExtractor enhancements...")
    
    # Test merge_element_details
    details_list = [
        {
            'element_attributes': {
                'element_1': {'tag_name': 'button', 'interactions_count': 2}
            },
            'interaction_summary': {
                'total_interactions': 2,
                'action_types': ['click'],
                'unique_elements': 1
            }
        },
        {
            'element_attributes': {
                'element_2': {'tag_name': 'input', 'interactions_count': 3}
            },
            'interaction_summary': {
                'total_interactions': 3,
                'action_types': ['type_text'],
                'unique_elements': 1
            }
        }
    ]
    
    merged = merge_element_details(details_list)
    assert 'element_attributes' in merged, "merge_element_details failed"
    assert len(merged['element_attributes']) == 2, "merge_element_details didn't merge correctly"
    
    # Test filter_elements_by_tag
    elements = {
        'element_1': {'tag_name': 'button'},
        'element_2': {'tag_name': 'input'},
        'element_3': {'tag_name': 'button'}
    }
    
    filtered = filter_elements_by_tag(elements, 'button')
    assert len(filtered) == 2, "filter_elements_by_tag failed"
    
    # Test filter_elements_by_interaction_count
    elements = {
        'element_1': {'interactions_count': 3},
        'element_2': {'interactions_count': 1},
        'element_3': {'interactions_count': 0}
    }
    
    filtered = filter_elements_by_interaction_count(elements, 2)
    assert len(filtered) == 1, "filter_elements_by_interaction_count failed"
    
    # Test format_for_frontend
    element_details = {
        "interaction_summary": {
            "total_interactions": 5,
            "unique_elements": 3,
            "action_types": ["click", "type_text"]
        },
        "element_attributes": {
            "element_1": {"tag_name": "button", "interactions_count": 2}
        },
        "framework_selectors": {
            "selenium": {"element_1": "#button1"}
        }
    }
    
    formatted = format_for_frontend(element_details)
    assert "element_interactions" in formatted, "format_for_frontend failed"
    
    print("✓ ElementExtractor enhancements verified")

def test_backward_compatibility():
    """Test that existing functionality still works."""
    print("Testing backward compatibility...")
    
    # Test existing element_extractor functions
    history_data = {
        'extracted_content': [
            {'selector': 'xpath1', 'value': 'Click element 1'}
        ],
        'actions': [
            {'type': 'click_element', 'xpath': 'xpath2', 'element_id': 'element2'}
        ]
    }
    
    selectors = extract_selectors_from_history(history_data)
    assert 'xpath1' in selectors, "extract_selectors_from_history failed"
    assert 'xpath2' in selectors, "extract_selectors_from_history failed"
    
    actions = analyze_actions(history_data)
    assert len(actions) == 1, "analyze_actions failed"
    
    print("✓ Backward compatibility verified")

if __name__ == "__main__":
    print("Running refactored code tests...\n")
    
    test_element_tracker_enhancements()
    test_element_extractor_enhancements()
    test_backward_compatibility()
    
    print("\n✓ All tests passed! Refactored code is working correctly.")