# Parallel Browser Execution

This document explains how to use the parallel browser execution feature in the SDET-GENIE application.

## Overview

The parallel browser execution feature allows running multiple Gherkin scenarios simultaneously using separate browser instances. This significantly reduces the total execution time and provides better isolation between test scenarios.

## How It Works

1. When multiple Gherkin scenarios are generated, the pipeline automatically detects this and uses parallel execution
2. Each scenario is assigned to a separate browser agent with its own browser instance
3. All agents run concurrently, executing their scenarios independently
4. Results from all agents are collected and combined for reporting

## Backend Implementation

### BrowserExecutionService

The `BrowserExecutionService` contains the `execute_parallel_browser_tests` method which handles the parallel execution:

```python
async def execute_parallel_browser_tests(
    self,
    test_scripts: List[str],
    provider: str = "Google",
    model: str = "gemini-2.0-flash",
    browser_name: str = "chrome",
    browser_executable_path: str = None,
    browser_resolution: tuple = None
) -> Dict[str, Any]:
```

### TrackingBrowserAgent

The `TrackingBrowserAgent` has been enhanced to support:
- Unique agent IDs for parallel execution identification
- Tab management capabilities
- Improved resource cleanup

### PipelineService

The `PipelineService` automatically detects when to use parallel execution:
- If there's more than one Gherkin scenario, parallel execution is used
- Otherwise, single execution is used

## Frontend Visualization

### PipelineVisualizer

The `PipelineVisualizer` component displays parallel execution results with:
- Summary of all agents
- Individual agent results with execution time and interaction metrics
- Combined interaction data
- Framework exports

### ParallelExecutionVisualizer

The `ParallelExecutionVisualizer` provides detailed visualization of parallel execution with:
- Agent-specific results
- Interaction metrics
- Element library
- Framework exports
- Performance metrics

## Configuration

### Browser Configuration

The `BrowserConfigService` provides optimized browser arguments for parallel execution:
- Disabled backgrounding features to prevent throttling
- Security settings adjusted for testing environments
- Resource optimization flags

### MCP Service

The `MCPService` limits concurrent jobs to prevent resource exhaustion:
- Maximum of 5 concurrent jobs by default
- Automatic queuing when limit is reached

## Usage

### Automatic Detection

The system automatically uses parallel execution when multiple Gherkin scenarios are present:
1. User story is enhanced
2. Manual test cases are generated
3. Multiple Gherkin scenarios are created
4. Pipeline detects multiple scenarios and uses parallel execution

### Manual Usage

You can also manually trigger parallel execution by providing multiple test scripts to the `execute_parallel_browser_tests` method.

## Benefits

1. **Reduced Execution Time**: Multiple scenarios run simultaneously
2. **Better Isolation**: Each agent has its own browser instance
3. **Improved Reliability**: Failures in one agent don't affect others
4. **Resource Utilization**: Better use of system resources
5. **Scalability**: Can handle large numbers of scenarios efficiently

## Limitations

1. **Resource Usage**: More browser instances consume more system resources
2. **Browser Compatibility**: Some browsers may have limitations with parallel execution
3. **Network Constraints**: Multiple agents may compete for network resources

## Troubleshooting

### Resource Exhaustion

If you encounter resource exhaustion:
1. Reduce the maximum concurrent jobs in `MCPService`
2. Use headless mode for browsers
3. Increase system resources

### Browser Issues

If browsers fail to launch:
1. Check browser installation paths
2. Verify browser versions are compatible
3. Ensure sufficient system resources

### Timeout Issues

If execution times out:
1. Increase the timeout in `PipelineService`
2. Check for infinite loops in test scenarios
3. Verify network connectivity