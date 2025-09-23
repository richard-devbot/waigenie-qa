#!/usr/bin/env python3
"""
Unit tests for element tracking functionality in the browser execution agent.
"""

import unittest
from unittest.mock import Mock, patch
from app.agents.browser_execution_agent import TrackingBrowserAgent
from app.utils.element_extractor import extract_element_attributes, extract_all_element_details

class TestElementTracking(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock LLM
        self.mock_llm = Mock()
        self.mock_llm.provider = "test"
        self.mock_llm.model = "test-model"
        self.mock_llm.ainvoke = Mock()
        
        # Create mock DOM node
        self.mock_node = Mock()
        self.mock_node.element_index = 1
        self.mock_node.node_id = 123
        self.mock_node.backend_node_id = 456
        self.mock_node.node_name = "input"
        self.mock_node.node_type = "ELEMENT_NODE"
        self.mock_node.attributes = {
            "id": "test-input",
            "class": "form-control",
            "type": "text",
            "placeholder": "Enter text"
        }
        self.mock_node.is_visible = True
        self.mock_node.is_scrollable = False
        self.mock_node.frame_id = None
        self.mock_node.session_id = "test-session"
        
        # Mock absolute position
        mock_position = Mock()
        mock_position.x = 100.0
        mock_position.y = 200.0
        mock_position.width = 300.0
        mock_position.height = 40.0
        self.mock_node.absolute_position = mock_position
        
        # Mock snapshot node
        mock_snapshot = Mock()
        mock_snapshot.is_clickable = True
        mock_snapshot.cursor_style = "text"
        self.mock_node.snapshot_node = mock_snapshot
        
        # Mock accessibility node
        mock_ax_node = Mock()
        mock_ax_node.role = "textbox"
        mock_ax_node.name = "Test Input"
        mock_ax_node.description = ""
        mock_ax_node.ignored = False
        mock_ax_node.properties = []
        self.mock_node.ax_node = mock_ax_node
        
        # Mock methods
        self.mock_node.get_meaningful_text_for_llm = Mock(return_value="Test Input Field")
        self.mock_node.xpath = "//input[@id='test-input']"
    
    def test_extract_element_details(self):
        """Test that element details are extracted correctly."""
        # Create a TrackingBrowserAgent instance
        agent = TrackingBrowserAgent(
            task="Test task",
            llm=self.mock_llm
        )
        
        # Extract element details
        details = agent.extract_element_details(self.mock_node)
        
        # Verify basic properties
        self.assertEqual(details["element_index"], 1)
        self.assertEqual(details["node_id"], 123)
        self.assertEqual(details["backend_node_id"], 456)
        self.assertEqual(details["tag_name"], "input")
        self.assertEqual(details["node_type"], "ELEMENT_NODE")
        
        # Verify attributes
        self.assertIn("id", details["attributes"])
        self.assertEqual(details["attributes"]["id"], "test-input")
        
        # Verify position
        self.assertIn("absolute_position", details)
        self.assertEqual(details["absolute_position"]["x"], 100.0)
        self.assertEqual(details["absolute_position"]["y"], 200.0)
        
        # Verify meaningful text
        self.assertEqual(details["meaningful_text"], "Test Input Field")
        
        # Verify built-in xpath
        self.assertEqual(details["built_in_xpath"], "//input[@id='test-input']")
        
        # Verify selectors are generated
        self.assertIn("selectors", details)
        selectors = details["selectors"]
        self.assertIn("id", selectors)
        self.assertEqual(selectors["id"], "#test-input")
    
    def test_track_click_event(self):
        """Test that click events are tracked correctly."""
        # Create a TrackingBrowserAgent instance
        agent = TrackingBrowserAgent(
            task="Test task",
            llm=self.mock_llm
        )
        
        # Create a mock click event
        mock_event = Mock()
        mock_event.node = self.mock_node
        mock_event.button = "left"
        mock_event.while_holding_ctrl = False
        
        # Track the click event
        agent.track_click(mock_event)
        
        # Verify interaction was recorded
        self.assertEqual(len(agent.interactions), 1)
        
        interaction = agent.interactions[0]
        self.assertEqual(interaction["action_type"], "click")
        self.assertIn("element_details", interaction)
        self.assertEqual(interaction["element_details"]["element_index"], 1)
        
        # Verify metadata
        metadata = interaction["metadata"]
        self.assertEqual(metadata["button"], "left")
        self.assertEqual(metadata["ctrl_held"], False)
    
    def test_track_type_text_event(self):
        """Test that type text events are tracked correctly."""
        # Create a TrackingBrowserAgent instance
        agent = TrackingBrowserAgent(
            task="Test task",
            llm=self.mock_llm
        )
        
        # Create a mock type text event
        mock_event = Mock()
        mock_event.node = self.mock_node
        mock_event.text = "test text"
        mock_event.clear_existing = True
        
        # Track the type text event
        agent.track_type_text(mock_event)
        
        # Verify interaction was recorded
        self.assertEqual(len(agent.interactions), 1)
        
        interaction = agent.interactions[0]
        self.assertEqual(interaction["action_type"], "type_text")
        self.assertIn("element_details", interaction)
        self.assertEqual(interaction["element_details"]["element_index"], 1)
        
        # Verify metadata
        metadata = interaction["metadata"]
        self.assertEqual(metadata["text"], "test text")
        self.assertEqual(metadata["clear_existing"], True)
    
    def test_get_tracked_interactions(self):
        """Test that tracked interactions are returned correctly."""
        # Create a TrackingBrowserAgent instance
        agent = TrackingBrowserAgent(
            task="Test task",
            llm=self.mock_llm
        )
        
        # Add some mock interactions
        agent.interactions = [
            {
                "action_type": "click",
                "timestamp": 1234567890.123,
                "element_details": {
                    "element_index": 1,
                    "tag_name": "input",
                    "meaningful_text": "Test Input"
                },
                "metadata": {
                    "button": "left",
                    "ctrl_held": False
                }
            },
            {
                "action_type": "type_text",
                "timestamp": 1234567891.456,
                "element_details": {
                    "element_index": 1,
                    "tag_name": "input",
                    "meaningful_text": "Test Input"
                },
                "metadata": {
                    "text": "test value",
                    "clear_existing": True
                }
            }
        ]
        
        # Get tracked interactions
        tracked = agent.get_tracked_interactions()
        
        # Verify structure
        self.assertIn("total_interactions", tracked)
        self.assertIn("action_types", tracked)
        self.assertIn("interactions", tracked)
        self.assertIn("unique_elements", tracked)
        self.assertIn("automation_data", tracked)
        self.assertIn("element_details", tracked)
        
        # Verify values
        self.assertEqual(tracked["total_interactions"], 2)
        self.assertEqual(set(tracked["action_types"]), {"click", "type_text"})
        self.assertEqual(tracked["unique_elements"], 1)
        self.assertEqual(len(tracked["interactions"]), 2)
    
    def test_element_extractor_integration(self):
        """Test integration with element extractor functions."""
        # Create mock interaction data
        mock_interaction_data = {
            "element_interactions": {
                "total_interactions": 2,
                "action_types": ["click", "type_text"],
                "unique_elements": 1,
                "automation_data": {
                    "element_library": {
                        "element_1": {
                            "tag_name": "input",
                            "selectors": {"id": "#test-input"},
                            "attributes": {"id": "test-input"},
                            "meaningful_text": "Test Input"
                        }
                    },
                    "action_sequence": [
                        {
                            "step_number": 1,
                            "action_type": "type_text",
                            "element_reference": "element_1",
                            "selectors": {"id": "#test-input"},
                            "metadata": {"text": "test"},
                            "element_context": {"tag_name": "input"}
                        }
                    ],
                    "framework_selectors": {}
                }
            }
        }
        
        # Test extract_element_attributes
        element_attributes = extract_element_attributes(mock_interaction_data)
        self.assertIsInstance(element_attributes, dict)
        
        # Test extract_all_element_details
        all_details = extract_all_element_details(mock_interaction_data)
        self.assertIn("element_attributes", all_details)
        self.assertIn("interaction_summary", all_details)
        self.assertIn("framework_selectors", all_details)

if __name__ == "__main__":
    unittest.main()
"""
Test file for element tracking functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.utils.element_tracker import ElementTracker
from app.utils.element_extractor import extract_all_element_details, get_element_statistics

def test_element_tracker():
    """Test the ElementTracker functionality"""
    # Create an element tracker instance
    tracker = ElementTracker()
    
    # Check that it was created successfully
    assert tracker is not None
    print("ElementTracker created successfully")
    
    # Check that it has the required methods
    assert hasattr(tracker, 'extract_element_details')
    assert hasattr(tracker, 'track_click')
    assert hasattr(tracker, 'track_type_text')
    assert hasattr(tracker, 'get_interactions')
    assert hasattr(tracker, 'clear_interactions')
    assert hasattr(tracker, 'export_to_json')
    assert hasattr(tracker, 'get_interactions_summary')
    assert hasattr(tracker, 'export_for_framework')
    print("All required methods present")
    
    # Test element details extraction method exists
    assert callable(tracker.extract_element_details)
    print("extract_element_details method is callable")
    
    # Test selector generation method exists
    assert hasattr(tracker, '_generate_production_selectors')
    print("_generate_production_selectors method is present")
    
    # Test framework selector generation method exists
    assert hasattr(tracker, '_generate_framework_selectors')
    print("_generate_framework_selectors method is present")
    
    print("All tests passed!")

def test_element_extractor():
    """Test the element extractor functionality"""
    # Create sample data to test with
    sample_data = {
        "element_interactions": {
            "total_interactions": 0,
            "action_types": [],
            "unique_elements": 0,
            "automation_data": {}
        }
    }
    
    # Test extract_all_element_details
    details = extract_all_element_details(sample_data)
    assert isinstance(details, dict)
    print("extract_all_element_details works correctly")
    
    # Test get_element_statistics
    stats = get_element_statistics(details)
    assert isinstance(stats, dict)
    print("get_element_statistics works correctly")
    
    print("Element extractor tests passed!")

if __name__ == "__main__":
    print("Testing Element Tracking Implementation...")
    test_element_tracker()
    test_element_extractor()
    print("All tests completed successfully!")