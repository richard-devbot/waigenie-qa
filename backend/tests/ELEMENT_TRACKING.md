# Element Tracking in SDET-Genie

This document explains how element tracking works in the SDET-Genie application.

## Overview

Element tracking is a core feature that captures detailed information about user interactions during browser automation execution. This includes:

1. Click events
2. Type text events
3. Element details (selectors, attributes, positions, etc.)
4. Action sequences

## Implementation

### Browser Execution Agent

The [TrackingBrowserAgent](file:///e:/Appdata/program%20files/python/projects/full-stack-sdet/backend/app/agents/browser_execution_agent.py#L33-L719) class in [backend/app/agents/browser_execution_agent.py](file:///e:/Appdata/program%20files/python/projects/full-stack-sdet/backend/app/agents/browser_execution_agent.py) is responsible for tracking element interactions.

Key methods:
- `track_click()`: Tracks click events
- `track_type_text()`: Tracks text input events
- `extract_element_details()`: Extracts comprehensive element details
- `get_tracked_interactions()`: Returns all tracked interactions

### Element Extractor

The [element_extractor.py](file:///e:/Appdata/program%20files/python/projects/full-stack-sdet/backend/app/utils/element_extractor.py) module in [backend/app/utils/element_extractor.py](file:///e:/Appdata/program%20files/python/projects/full-stack-sdet/backend/app/utils/element_extractor.py) provides utility functions for extracting element details:

- `extract_element_attributes()`: Extracts element attributes from interaction data
- `extract_all_element_details()`: Extracts comprehensive element details

### Browser Execution Service

The [browser_execution_service.py](file:///e:/Appdata/program%20files/python/projects/full-stack-sdet/backend/app/services/browser_execution_service.py) in [backend/app/services/browser_execution_service.py](file:///e:/Appdata/program%20files/python/projects/full-stack-sdet/backend/app/services/browser_execution_service.py) formats the tracked interactions for frontend consumption.

### Frontend Display

The [ParallelExecutionVisualizer.tsx](file:///e:/Appdata/program%20files/python/projects/full-stack-sdet/frontend/components/pipeline/ParallelExecutionVisualizer.tsx) component in [frontend/components/pipeline/ParallelExecutionVisualizer.tsx](file:///e:/Appdata/program%20files/python/projects/full-stack-sdet/frontend/components/pipeline/ParallelExecutionVisualizer.tsx) displays the tracked interactions in a user-friendly interface.

## Data Flow

1. Browser agent executes actions (click, type, etc.)
2. Event handlers capture interactions and extract element details
3. Interaction data is stored in the agent's interactions list
4. After execution, `get_tracked_interactions()` returns formatted data
5. Browser execution service formats data for frontend
6. Frontend displays interaction details in the visualization

## Tracked Information

For each interaction, the following information is captured:

### Element Details
- Tag name
- Selectors (ID, CSS, XPath, etc.)
- Attributes
- Position (x, y, width, height)
- Accessibility information
- Meaningful text content
- Framework-specific selectors

### Action Metadata
- Action type (click, type_text)
- Timestamp
- Action-specific data (button for clicks, text for typing)

### Aggregated Data
- Total interactions count
- Unique elements count
- Action types list
- Element library
- Action sequence

## Testing

Unit tests in [backend/tests/test_element_tracking.py](file:///e:/Appdata/program%20files/python/projects/full-stack-sdet/backend/tests/test_element_tracking.py) verify all aspects of the element tracking functionality.