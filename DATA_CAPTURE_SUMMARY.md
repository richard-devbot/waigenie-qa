# Data Capture and Frontend Display Summary

## Overview
This document summarizes what data we are capturing during parallel browser execution and how it's displayed in the frontend.

## Data Captured Per Agent

### 1. Element Interactions & Tracking
- **Element Details**: Comprehensive element attributes including:
  - Tag name, ID, class, name, type, placeholder, value, role, aria-label
  - Position and bounds (x, y, width, height)
  - Accessibility information (role, name, description)
  - Computed styles and client rectangles
  - Meaningful text content
  - Built-in XPath from browser-use
  - Custom selectors for multiple frameworks (CSS, XPath, Playwright, Cypress, Selenium)

- **Interaction Tracking**: 
  - Click events with element details
  - Type text events with element details
  - Timestamps for each interaction
  - Action metadata (button type, text content, etc.)

### 2. Visual Artifacts
- **GIFs**: Execution recordings saved to `./recordings/videos/{session_id}/agent_{agent_id}/execution.gif`
- **Screenshots**: Step-by-step screenshots saved to `./recordings/debug.traces/{session_id}/agent_{agent_id}/screenshots/step_{number}.png`
- **Network Traces**: HAR files saved to `./recordings/network.traces/{session_id}/agent_{agent_id}.har`
- **Debug Traces**: Debug information saved to `./recordings/debug.traces/{session_id}/agent_{agent_id}/`

### 3. Execution Metrics
- **Performance Data**:
  - Execution time per agent
  - Total interactions count
  - Scenarios count
  - Interaction rate (interactions per second)
  - Average execution time across agents

- **Agent Status**:
  - Completion status (completed/failed)
  - Error messages for failed agents
  - Success/failure indicators

### 4. Framework Data
- **Element Library**: Comprehensive element database with all interacted elements
- **Action Sequence**: Chronological list of all actions performed
- **Framework Selectors**: Multiple selector types for each element
- **Automation Data**: Structured data for script generation

## Frontend Display Structure

### Main Tabs
1. **Agents Tab**: Individual agent execution results
2. **Interactions Tab**: Combined element interactions across all agents
3. **Metrics Tab**: Performance metrics and execution statistics
4. **Frameworks Tab**: Framework information (currently browser-use only)
5. **Artifacts Tab**: Visual artifacts with sub-tabs

### Artifacts Sub-Tabs
1. **GIFs**: Execution recordings for each agent
2. **Screenshots**: Step-by-step screenshots for each agent
3. **Network**: HAR files for network analysis
4. **Debug**: Debug traces and information
5. **Directories**: File system paths and structure

## API Endpoints for Artifacts

### Screenshots
```
GET /api/v1/artifacts/{session_id}/debug.traces/agent_{agent_id}/screenshots/{filename}
```

### GIFs
```
GET /api/v1/artifacts/{session_id}/videos/agent_{agent_id}/execution.gif
```

### Network Traces
```
GET /api/v1/artifacts/{session_id}/network.traces/agent_{agent_id}.har
```

### Debug Traces
```
GET /api/v1/artifacts/{session_id}/debug.traces/agent_{agent_id}/{filename}
```

## Key Features

### Element Interaction Display
- Expandable element details with comprehensive information
- Visual representation of element positions and bounds
- Multiple selector types for each element
- Interaction count tracking
- Meaningful text extraction

### Artifact Management
- Visual previews for images (GIFs, screenshots)
- Download functionality for all artifacts
- Error handling for missing files
- Organized by agent and type

### Performance Metrics
- Real-time execution statistics
- Comparative analysis across agents
- Success/failure tracking
- Interaction rate calculations

## Data Structure

### Agent Result Structure
```json
{
  "agent_id": 0,
  "status": "completed",
  "details": "Execution completed successfully",
  "execution_time": 15.5,
  "interactions_count": 8,
  "artifacts": {
    "agent_id": 0,
    "session_id": "parallel_execution_20241201_120000",
    "video_dir": "./recordings/videos/parallel_execution_20241201_120000/agent_0",
    "traces_dir": "./recordings/debug.traces/parallel_execution_20241201_120000/agent_0",
    "har_path": "./recordings/network.traces/parallel_execution_20241201_120000/agent_0.har",
    "gif_path": "./recordings/videos/parallel_execution_20241201_120000/agent_0/execution.gif",
    "screenshot_paths": [
      "./recordings/debug.traces/parallel_execution_20241201_120000/agent_0/screenshots/step_1.png",
      "./recordings/debug.traces/parallel_execution_20241201_120000/agent_0/screenshots/step_2.png"
    ],
    "screenshots_count": 2
  }
}
```

### Element Interaction Structure
```json
{
  "total_interactions": 24,
  "unique_elements": 8,
  "action_types": ["click", "type_text"],
  "automation_data": {
    "element_library": {
      "element_123": {
        "tag_name": "button",
        "selectors": {
          "css_id": "#submit-btn",
          "xpath_id": "//button[@id='submit-btn']",
          "playwright_testid": "[data-testid='submit-button']"
        },
        "attributes": {
          "id": "submit-btn",
          "class": "btn btn-primary",
          "type": "submit"
        },
        "position": {
          "x": 100,
          "y": 200,
          "width": 120,
          "height": 40
        },
        "meaningful_text": "Submit Form",
        "interactions_count": 1
      }
    },
    "action_sequence": [
      {
        "step_number": 1,
        "action_type": "click",
        "element_reference": "element_123",
        "agent_id": 0,
        "timestamp": 1701432000.123
      }
    ]
  }
}
```

## Recent Improvements

### Screenshot Capture
- ✅ Added proper ScreenshotService initialization
- ✅ Fixed screenshot capture mechanism
- ✅ Added fallback screenshot saving
- ✅ Integrated with browser-use SDK

### Frontend Enhancements
- ✅ Added dedicated screenshots tab
- ✅ Enhanced artifact preview functionality
- ✅ Improved error handling for missing files
- ✅ Added download functionality
- ✅ Organized artifacts by type and agent

### Data Structure
- ✅ Comprehensive element tracking
- ✅ Multiple selector generation
- ✅ Performance metrics collection
- ✅ Artifact path management
- ✅ API endpoint structure

## Next Steps

### Pending Improvements
- [ ] Fix network trace (HAR) capture mechanism
- [ ] Fix debug trace capture mechanism
- [ ] Add more comprehensive network request tracking
- [ ] Implement real-time artifact updates
- [ ] Add artifact compression and optimization

### Future Enhancements
- [ ] Add video playback controls
- [ ] Implement screenshot comparison
- [ ] Add network request analysis
- [ ] Create artifact export functionality
- [ ] Add performance profiling
