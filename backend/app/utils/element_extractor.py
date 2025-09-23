from typing import Dict, Any, List, Optional
import json

def extract_selectors_from_history(history_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract element selectors from execution history data.
    
    Args:
        history_data (Dict[str, Any]): The execution history data
        
    Returns:
        Dict[str, str]: A dictionary of element selectors
    """
    selectors = {}
    
    # Extract from extracted_content if available
    if 'extracted_content' in history_data:
        for item in history_data['extracted_content']:
            if isinstance(item, dict) and 'selector' in item and 'value' in item:
                selectors[item['selector']] = item['value']
    
    # Extract from action events if available
    if 'actions' in history_data:
        for action in history_data['actions']:
            if isinstance(action, dict):
                # Extract from click events
                if action.get('type') == 'click_element' and 'xpath' in action:
                    selectors[action['xpath']] = f"Click element {action.get('element_id', 'unknown')}"
                
                # Extract from type events
                if action.get('type') == 'type_text' and 'xpath' in action:
                    selectors[action['xpath']] = f"Type text: {action.get('text', '')}"
    
    return selectors

def analyze_actions(history_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analyze actions from execution history data.
    
    Args:
        history_data (Dict[str, Any]): The execution history data
        
    Returns:
        List[Dict[str, Any]]: A list of analyzed actions
    """
    actions = []
    
    # Extract from actions if available
    if 'actions' in history_data:
        for action in history_data['actions']:
            if isinstance(action, dict):
                actions.append({
                    'type': action.get('type', 'unknown'),
                    'description': action.get('description', ''),
                    'timestamp': action.get('timestamp', ''),
                    'element': action.get('element_id', 'unknown') if action.get('type') == 'click_element' else None,
                    'text': action.get('text', '') if action.get('type') == 'type_text' else None
                })
    
    return actions

def extract_element_attributes(interaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract comprehensive element attributes from interaction data for every agent execution on each tab.
    
    Args:
        interaction_data (Dict[str, Any]): The interaction data from tracked interactions
        
    Returns:
        Dict[str, Any]: A dictionary of comprehensive element attributes
    """
    element_attributes = {}
    
    # Extract from automation data if available
    if 'automation_data' in interaction_data:
        automation_data = interaction_data['automation_data']
        
        # Extract from element library
        if 'element_library' in automation_data:
            for element_key, element_data in automation_data['element_library'].items():
                element_attributes[element_key] = {
                    'tag_name': element_data.get('tag_name', ''),
                    'selectors': element_data.get('selectors', {}),
                    'attributes': element_data.get('attributes', {}),
                    'position': element_data.get('position', {}),
                    'accessibility': element_data.get('accessibility', {}),
                    'meaningful_text': element_data.get('meaningful_text', ''),
                    'interactions_count': element_data.get('interactions_count', 0)
                }
        
        # Extract from action sequence
        if 'action_sequence' in automation_data:
            for action in automation_data['action_sequence']:
                element_context = action.get('element_context', {})
                if element_context:
                    element_ref = action.get('element_reference', '')
                    if element_ref and element_ref not in element_attributes:
                        element_attributes[element_ref] = {
                            'tag_name': element_context.get('tag_name', ''),
                            'selectors': action.get('selectors', {}),
                            'attributes': element_context.get('attributes', {}),
                            'meaningful_text': element_context.get('meaningful_text', ''),
                            'is_visible': element_context.get('is_visible', True)
                        }
    
    # Extract from framework selectors
    if 'framework_selectors' in interaction_data:
        framework_selectors = interaction_data['framework_selectors']
        for selector_type, selectors in framework_selectors.items():
            for element_key, selector_value in selectors.items():
                if element_key in element_attributes:
                    if 'framework_selectors' not in element_attributes[element_key]:
                        element_attributes[element_key]['framework_selectors'] = {}
                    element_attributes[element_key]['framework_selectors'][selector_type] = selector_value
                else:
                    element_attributes[element_key] = {
                        'framework_selectors': {selector_type: selector_value}
                    }
    
    return element_attributes

def extract_all_element_details(history_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract all element details from execution history for comprehensive analysis.
    
    Args:
        history_data (Dict[str, Any]): The execution history data
        
    Returns:
        Dict[str, Any]: A dictionary of all element details
    """
    all_details = {
        'element_attributes': {},
        'interaction_summary': {},
        'framework_selectors': {}
    }
    
    # Extract element attributes from tracked interactions
    if 'element_interactions' in history_data:
        element_interactions = history_data['element_interactions']
        all_details['element_attributes'] = extract_element_attributes(element_interactions)
        
        # Add interaction summary
        all_details['interaction_summary'] = {
            'total_interactions': element_interactions.get('total_interactions', 0),
            'action_types': element_interactions.get('action_types', []),
            'unique_elements': element_interactions.get('unique_elements', 0)
        }
    
    # Extract framework selectors if available
    if 'framework_exports' in history_data:
        framework_exports = history_data['framework_exports']
        for framework, export_data in framework_exports.items():
            if 'page_objects' in export_data:
                all_details['framework_selectors'][framework] = export_data['page_objects']
    
    return all_details

def export_element_details_to_json(element_details: Dict[str, Any], file_path: Optional[str] = None) -> str:
    """
    Export element details to JSON format.
    
    Args:
        element_details (Dict[str, Any]): The element details to export
        file_path (Optional[str]): Optional file path to save JSON. If None, returns JSON string.
        
    Returns:
        str: JSON string representation of element details
    """
    # Convert to JSON string
    json_str = json.dumps(element_details, indent=2, default=str)
    
    # Save to file if path provided
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        except Exception as e:
            print(f"Error writing JSON file: {e}")
    
    return json_str

def get_element_statistics(element_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get statistics about element interactions.
    
    Args:
        element_details (Dict[str, Any]): The element details
        
    Returns:
        Dict[str, Any]: Statistics about element interactions
    """
    stats = {
        'total_elements': 0,
        'most_interacted_element': None,
        'interaction_distribution': {},
        'selector_coverage': {},
        'framework_coverage': {}
    }
    
    if 'element_attributes' in element_details:
        elements = element_details['element_attributes']
        stats['total_elements'] = len(elements)
        
        # Find most interacted element
        max_interactions = 0
        for element_key, element_data in elements.items():
            interactions_count = element_data.get('interactions_count', 0)
            if interactions_count > max_interactions:
                max_interactions = interactions_count
                stats['most_interacted_element'] = {
                    'element_key': element_key,
                    'interactions_count': interactions_count,
                    'tag_name': element_data.get('tag_name', '')
                }
        
        # Interaction distribution
        interaction_counts = [element_data.get('interactions_count', 0) for element_data in elements.values()]
        if interaction_counts:
            stats['interaction_distribution'] = {
                'min': min(interaction_counts),
                'max': max(interaction_counts),
                'avg': sum(interaction_counts) / len(interaction_counts)
            }
        
        # Selector coverage
        selector_types = set()
        for element_data in elements.values():
            if 'selectors' in element_data:
                selector_types.update(element_data['selectors'].keys())
        stats['selector_coverage'] = list(selector_types)
        
        # Framework coverage
        framework_types = set()
        for element_data in elements.values():
            if 'framework_selectors' in element_data:
                framework_types.update(element_data['framework_selectors'].keys())
        stats['framework_coverage'] = list(framework_types)
    
    return stats

def merge_element_details(details_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple element details dictionaries into one comprehensive dictionary.
    
    Args:
        details_list (List[Dict[str, Any]]): List of element details dictionaries
        
    Returns:
        Dict[str, Any]: Merged element details
    """
    merged = {
        'element_attributes': {},
        'interaction_summary': {
            'total_interactions': 0,
            'action_types': set(),
            'unique_elements': 0
        },
        'framework_selectors': {}
    }
    
    for details in details_list:
        # Merge element attributes
        if 'element_attributes' in details:
            merged['element_attributes'].update(details['element_attributes'])
        
        # Merge interaction summary
        if 'interaction_summary' in details:
            summary = details['interaction_summary']
            merged['interaction_summary']['total_interactions'] += summary.get('total_interactions', 0)
            merged['interaction_summary']['action_types'].update(summary.get('action_types', []))
            merged['interaction_summary']['unique_elements'] += summary.get('unique_elements', 0)
    
        # Merge framework selectors
        if 'framework_selectors' in details:
            for framework, selectors in details['framework_selectors'].items():
                if framework not in merged['framework_selectors']:
                    merged['framework_selectors'][framework] = {}
                merged['framework_selectors'][framework].update(selectors)
    
    # Convert action_types set back to list
    merged['interaction_summary']['action_types'] = list(merged['interaction_summary']['action_types'])
    
    return merged

def filter_elements_by_tag(elements: Dict[str, Any], tag_name: str) -> Dict[str, Any]:
    """
    Filter elements by tag name.
    
    Args:
        elements (Dict[str, Any]): Dictionary of elements
        tag_name (str): Tag name to filter by
        
    Returns:
        Dict[str, Any]: Filtered elements
    """
    return {k: v for k, v in elements.items() if v.get('tag_name', '').lower() == tag_name.lower()}

def filter_elements_by_interaction_count(elements: Dict[str, Any], min_count: int = 1) -> Dict[str, Any]:
    """
    Filter elements by minimum interaction count.
    
    Args:
        elements (Dict[str, Any]): Dictionary of elements
        min_count (int): Minimum interaction count
        
    Returns:
        Dict[str, Any]: Filtered elements
    """
    return {k: v for k, v in elements.items() if v.get('interactions_count', 0) >= min_count}

def format_for_frontend(element_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format element details specifically for frontend consumption.
    
    Args:
        element_details (Dict[str, Any]): Element details to format
        
    Returns:
        Dict[str, Any]: Formatted data for frontend
    """
    formatted = {
        "element_interactions": {
            "total_interactions": element_details.get("interaction_summary", {}).get("total_interactions", 0),
            "unique_elements": element_details.get("interaction_summary", {}).get("unique_elements", 0),
            "action_types": element_details.get("interaction_summary", {}).get("action_types", []),
            "automation_data": {
                "element_library": element_details.get("element_attributes", {}),
                "action_sequence": [],  # This would need to be populated separately
                "framework_selectors": element_details.get("framework_selectors", {})
            }
        }
    }
    
    # Add statistics if available
    try:
        stats = get_element_statistics(element_details)
        formatted["element_statistics"] = stats
    except Exception as e:
        print(f"Error getting element statistics: {e}")
    
    return formatted