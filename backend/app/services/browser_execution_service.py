"""Service for executing browser automation tests with element tracking and artifact generation."""

import asyncio
import datetime
import logging
import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Set event loop policy for Windows as early as possible
if platform.system() == "Windows":
    if sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    else:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Import the TrackingBrowserAgent from the new implementation
from app.agents.browser_execution_agent import TrackingBrowserAgent
from app.services.mcp_service import mcp_service
from app.browser.browser_manager import BrowserManager
from app.utils.model_factory import get_llm_instance

# Import BrowserUseTools
from app.browser.browser_tools.browser_use_tools import BrowserUseTools

# Explicit imports from browser_use for clarity
from browser_use.browser.session import BrowserSession
from app.browser.agent_browser_profile import AgentBrowserProfile

# Import element tracking utilities for global helper functions
from app.utils.element_tracker import ElementTracker
from app.utils.element_extractor import extract_all_element_details, get_element_statistics, format_for_frontend


class BrowserExecutionService:
    """Service for executing browser automation tests with element tracking and artifact generation."""
    
    def __init__(self):
        """Initialize the BrowserExecutionService."""
        # Set event loop policy for Windows to avoid subprocess issues
        if platform.system() == "Windows":
            if sys.version_info >= (3, 8):
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            else:
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        self.browser_manager = BrowserManager()
        # Initialize BrowserUseTools instance
        self.browser_use_tools = BrowserUseTools()
        # Create a global element tracker instance for service-level operations
        self.global_element_tracker = ElementTracker()
    
    async def execute_browser_test(
        self,
        test_script: str,
        provider: str = "Google",
        model: str = "gemini-2.0-flash"
    ) -> Dict[str, Any]:
        """
        Execute a browser automation test script with full artifact generation.
        
        Args:
            test_script (str): The browser test script to execute
            provider (str): The model provider to use
            model (str): The specific model to use
            
        Returns:
            Dict[str, Any]: Test execution results and element tracking data
        """
        # Validate inputs
        if not test_script:
            raise ValueError("Test script is required")
        
        # Package the task for MCP execution
        payload = {
            "test_script": test_script,
            "provider": provider,
            "model": model
        }
        
        # Submit the job to MCP service
        task_id = await mcp_service.submit_mcp_job("browser_use_execution", payload)
        
        # Poll for completion
        while True:
            status = await mcp_service.get_job_status(task_id)
            if status["status"] in ["completed", "failed"]:
                if status["status"] == "completed":
                    return status["result"]
                else:
                    raise Exception(f"Browser execution failed: {status['error']}")
            await asyncio.sleep(1)

    async def execute_parallel_browser_tests(
        self,
        test_scripts: List[str],
        provider: str = "Google",
        model: str = "gemini-2.0-flash",
        browser_name: str = "chrome",
        browser_executable_path: str = None,
        browser_resolution: tuple = None,
        vision_enabled: bool = True,
        cdp_port: int = None
    ) -> Dict[str, Any]:
        """
        Execute multiple browser automation test scripts in parallel using tab management within a single browser session.
        
        Args:
            test_scripts (List[str]): List of browser test scripts to execute in parallel
            provider (str): The model provider to use
            model (str): The specific model to use
            browser_name (str): The browser to use (chrome, edge, firefox, chromium)
            browser_executable_path (str): Custom browser executable path
            browser_resolution (tuple): Browser window resolution (width, height)
            vision_enabled (bool): Whether vision capabilities are enabled
            cdp_port (int): Custom CDP port for browser connection
            
        Returns:
            Dict[str, Any]: Parallel execution results and element tracking data
        """
        # Validate inputs
        if not test_scripts:
            raise ValueError("Test scripts are required")
        
        # Get the LLM instance
        llm = get_llm_instance(provider, model, for_agno=False)
        
        if not llm:
            raise Exception("Failed to initialize the BrowserAgent model. Please check your API keys and environment setup.")
        
        # Create timestamp for this execution session
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"parallel_execution_{timestamp}"
        
        # Create directories for this session using browser-use's native recording capabilities
        session_recordings_dir = f"./recordings/{session_id}"
        Path(session_recordings_dir).mkdir(parents=True, exist_ok=True)
        
        # Track if we successfully launched the browser
        browser_launched = False
        agents_created = []
        agent_sessions = []
        
        try:
            # Launch the browser first with custom configuration
            try:
                await self.browser_manager.launch_browser(
                    headless=False, 
                    executable_path=browser_executable_path,
                    browser_name=browser_name,
                    vision_enabled=vision_enabled,
                    cdp_port=cdp_port,
                    custom_resolution=browser_resolution
                )
                browser_launched = True
                logger.info(f"Browser launched successfully for session {session_id}")
            except Exception as e:
                logger.error(f"Failed to launch browser: {e}")
                raise RuntimeError(f"Failed to launch browser for parallel execution: {e}") from e
            
            # Wait for browser to be fully initialized
            await asyncio.sleep(2)
            
            # Create browser agents for each test script using tabs within the same browser session
            agents = []
            
            # Register all agents first
            for i, test_script in enumerate(test_scripts):
                try:
                    # Register agent with the browser manager
                    agent_session = await self.browser_manager.register_agent(f"parallel_agent_{i}")
                    agent_sessions.append((i, agent_session))
                    logger.info(f"Registered agent parallel_agent_{i}")
                except Exception as e:
                    logger.error(f"Error registering agent {i+1}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # If we can't register any agents, there's no point in continuing
                    if not agent_sessions:
                        raise RuntimeError(f"Failed to register any agents for parallel execution: {e}") from e
            
            if not agent_sessions:
                raise Exception("Failed to register any agents for parallel execution")
            
            # Create browser agents for each test script
            for i, agent_session in agent_sessions:
                try:
                    test_script = test_scripts[i]
                    
                    # Create agent with the session
                    # Load browser execution instructions from markdown file
                    from app.prompts.prompt_utils import load_agent_instructions
                    browser_instructions = load_agent_instructions("browser_execution")
                    
                    # Format the task with the instructions and context
                    # Ensure the Gherkin scenario has an entry point URL in the first Given step
                    import re
                    task = test_script
                    # Check if the task already has a properly formatted entry point URL at the beginning
                    if task and not re.search(r'^\s*Given\s+I\s+am\s+on\s+"https?://[^\"]+"', task, re.MULTILINE):
                        # If no entry point URL is found at the beginning, try to extract one from the task or use a default
                        url_match = re.search(r'https?://[^\s"]+', task)
                        if url_match:
                            url = url_match.group(0)
                            task = f"Given I am on \"{url}\"\n{task}"
                        else:
                            # Only use default if no URL can be extracted
                            task = f"Given I am on \"https://example.com\"\n{task}"
                    
                    enhanced_task = f"{browser_instructions}\n\n**Given Gherkin Scenario:**\n\n```gherkin\n{task}\n```"
                    
                    # Create unique directories for this agent's artifacts using browser-use's native capabilities
                    agent_recordings_dir = f"{session_recordings_dir}/agent_{i}"
                    agent_video_dir = f"{agent_recordings_dir}/videos"
                    agent_traces_dir = f"{agent_recordings_dir}/traces"
                    agent_har_path = f"{agent_recordings_dir}/network.har"
                    
                    # Ensure agent directories exist
                    Path(agent_recordings_dir).mkdir(parents=True, exist_ok=True)
                    Path(agent_video_dir).mkdir(parents=True, exist_ok=True)
                    Path(agent_traces_dir).mkdir(parents=True, exist_ok=True)
                    
                    agent = TrackingBrowserAgent(
                        task=enhanced_task,  # Use the properly formatted task
                        llm=llm,
                        browser_session=agent_session,
                        generate_gif=True,
                        highlight_elements=True,
                        use_vision=vision_enabled,
                        record_video_dir=agent_video_dir,
                        record_har_path=agent_har_path,
                        traces_dir=agent_traces_dir,
                        agent_id=i,  # Unique agent ID for parallel execution
                    )
                    
                    agents.append((i, agent, test_script))
                    agents_created.append(i)
                    logger.info(f"Created agent parallel_agent_{i}")
                except Exception as e:
                    logger.error(f"Error creating agent {i+1}: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            if not agents:
                raise Exception("Failed to create any browser agents for parallel execution")
            
            # Run all agents in parallel using tabs within the same browser session
            parallel_results = []
            all_tracked_interactions = []
            
            try:
                # Create tasks for all agents
                agent_tasks = []
                for i, agent, test_script in agents:
                    task = asyncio.create_task(
                        self._run_agent_in_tab(agent, i, test_script, f"parallel_agent_{i}", session_id),
                        name=f"parallel_agent_{i}"
                    )
                    agent_tasks.append((i, task, agent))
                
                # Wait for all tasks to complete with a timeout
                task_results = await asyncio.gather(*[task for _, task, _ in agent_tasks], return_exceptions=True)
                
                # Process results
                for (i, _, agent), result in zip(agent_tasks, task_results):
                    if isinstance(result, Exception):
                        logger.error(f"Agent {i+1} failed with error: {str(result)}")
                        parallel_results.append({
                            "agent_id": i,
                            "status": "failed",
                            "error": str(result),
                            "test_script": agents[i][2] if i < len(agents) else ""
                        })
                    else:
                        parallel_results.append({
                            "agent_id": i,
                            "status": "completed",
                            "result": result,
                            "test_script": agents[i][2] if i < len(agents) else ""
                        })
                    
                    # Get tracked interactions if available using the improved method
                    if hasattr(agent, 'get_tracked_interactions'):
                        try:
                            tracked_interactions = agent.get_tracked_interactions()
                            all_tracked_interactions.append({
                                "agent_id": i,
                                "interactions": tracked_interactions
                            })
                        except Exception as e:
                            logger.error(f"Error getting tracked interactions for agent {i}: {str(e)}")
                            
            finally:
                # Clean up the browser manager and shared browser session
                try:
                    # Clean up each agent session individually
                    for i, _ in agent_sessions:
                        try:
                            await self.browser_manager.unregister_agent(f"parallel_agent_{i}")
                            logger.info(f"Unregistered agent parallel_agent_{i}")
                        except Exception as e:
                            logger.error(f"Error unregistering agent {i}: {e}")
                except Exception as e:
                    logger.error(f"Error stopping shared browser session: {e}")
        
        except Exception as e:
            logger.error(f"Error in parallel execution: {str(e)}")
            import traceback
            traceback.print_exc()
            # Make sure we clean up even if there was an error
            try:
                # Clean up any agents that were created
                for i in agents_created:
                    try:
                        await self.browser_manager.unregister_agent(f"parallel_agent_{i}")
                        logger.info(f"Unregistered agent parallel_agent_{i} during cleanup")
                    except Exception as cleanup_e:
                        logger.error(f"Error during agent cleanup for agent {i}: {cleanup_e}")
                
                # Shutdown the browser if it was launched
                if browser_launched:
                    try:
                        await self.browser_manager.shutdown_browser()
                        logger.info("Browser shutdown completed")
                    except Exception as shutdown_e:
                        logger.error(f"Error during browser shutdown: {shutdown_e}")
            except Exception as final_cleanup_e:
                logger.error(f"Error during final cleanup: {final_cleanup_e}")
            raise e
        finally:
            # Ensure browser is always shut down
            try:
                if browser_launched:
                    await self.browser_manager.shutdown_browser()
                    logger.info("Browser shutdown completed in finally block")
            except Exception as e:
                logger.error(f"Error during final browser shutdown: {e}")
        
        # Compile comprehensive results using global helper functions
        session_data = {
            "execution_type": "parallel",
            "agent_count": len(agents),
            "completed_agents": len([r for r in parallel_results if r["status"] == "completed"]),
            "failed_agents": len([r for r in parallel_results if r["status"] == "failed"]),
            "results": parallel_results,
            "tracked_interactions": all_tracked_interactions,
            "session_id": session_id,
            "execution_date": datetime.datetime.now().isoformat()
        }
        
        # Format results for frontend consumption using global helper functions
        formatted_results = self._format_parallel_results_for_frontend_with_helpers(session_data)
        
        return {
            "status": "completed",
            "results": formatted_results,
            "raw_response": str(parallel_results),
            "test_scripts": test_scripts
        }
    
    async def _run_agent_in_tab(self, agent, agent_id: int, test_script: str, agent_name: str, session_id: str):
        """Run a single agent in a separate tab and return the results."""
        start_time = asyncio.get_event_loop().time()  # Track start time
        try:
            print(f"Executing parallel agent {agent_id+1} in tab")
            
            # The BrowserManager now handles the CDP connection and tab management,
            # so we can directly run the agent.
            
            # Execute and collect results
            history = await agent.run(max_steps=50)
            
            end_time = asyncio.get_event_loop().time()  # Track end time
            execution_time = end_time - start_time  # Calculate execution time
            
            # Get interaction count using the agent's improved built-in method
            tracked_interactions = agent.get_tracked_interactions()
            interactions_count = tracked_interactions.get("total_interactions", 0)
            
            # Get the actual paths from the agent if available
            gif_path = None
            if hasattr(agent, 'record_video_dir') and agent.record_video_dir:
                gif_path = f"{agent.record_video_dir}/execution.gif"
                # Check if the GIF was actually created
                if not os.path.exists(gif_path):
                    gif_path = None
            
            # Get screenshot paths from agent using browser-use's native recording
            screenshot_paths = []
            try:
                # Get screenshot paths from the agent's tracked interactions
                tracked_interactions = agent.get_tracked_interactions()
                screenshot_paths = tracked_interactions.get("screenshot_paths", [])
                
                # Also take a final screenshot if none exist using browser-use's native method
                if not screenshot_paths and hasattr(agent, 'browser_session') and agent.browser_session:
                    try:
                        # Use browser-use's built-in take_screenshot method
                        screenshot_b64 = await agent.browser_session.take_screenshot()
                        if screenshot_b64:
                            # Save to the recordings directory
                            if hasattr(agent, 'record_video_dir') and agent.record_video_dir:
                                screenshots_dir = Path(agent.record_video_dir) / 'screenshots'
                                screenshots_dir.mkdir(parents=True, exist_ok=True)
                                screenshot_filename = f'final_screenshot_agent_{agent_id}.png'
                                screenshot_path = screenshots_dir / screenshot_filename
                                
                                # Decode base64 and save to disk
                                import base64
                                screenshot_data = base64.b64decode(screenshot_b64)
                                
                                with open(screenshot_path, 'wb') as f:
                                    f.write(screenshot_data)
                                screenshot_paths.append(str(screenshot_path))
                    except Exception as e:
                        logger.error(f"Error taking final screenshot for agent {agent_id}: {e}")
            except Exception as e:
                logger.error(f"Error getting screenshot paths for agent {agent_id}: {e}")
            
            # Get artifact paths from browser-use's native recording capabilities
            video_dir = getattr(agent, 'record_video_dir', None)
            traces_dir = getattr(agent, 'traces_dir', None)
            har_path = getattr(agent, 'record_har_path', None)
            
            result = {
                "status": "completed",
                "details": "Execution completed successfully",
                "test_script": test_script,
                "execution_time": execution_time,  # Add execution time
                "interactions_count": interactions_count,  # Add interactions count
                # Add artifact paths for frontend display using browser-use's native capabilities
                "artifacts": {
                    "agent_id": agent_id,
                    "session_id": session_id,
                    "video_dir": video_dir,
                    "traces_dir": traces_dir,
                    "har_path": har_path,
                    "gif_path": gif_path,
                    "screenshot_paths": screenshot_paths,  # Actual screenshot paths
                    "screenshots_count": len(screenshot_paths)  # Count of screenshots
                }
            }
            
            return result
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            execution_time = end_time - start_time
            print(f"Error executing agent {agent_id+1}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e

    async def _run_agent(self, agent, agent_id: int, test_script: str, scenarios: List[str]):
        """Run a single agent and return the results."""
        start_time = asyncio.get_event_loop().time()  # Track start time
        try:
            print(f"Executing parallel agent {agent_id+1}")
            
            # Execute and collect results
            history = await agent.run(max_steps=50)
            
            end_time = asyncio.get_event_loop().time()  # Track end time
            execution_time = end_time - start_time  # Calculate execution time
            
            # Get interaction count using the agent's improved built-in method
            tracked_interactions = agent.get_tracked_interactions()
            interactions_count = tracked_interactions.get("total_interactions", 0)
            
            result = {
                "status": "completed",
                "details": "Execution completed successfully",
                "test_script": test_script,
                "scenarios_count": len(scenarios),
                "execution_time": execution_time,  # Add execution time
                "interactions_count": interactions_count  # Add interactions count
            }
            
            return result
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            execution_time = end_time - start_time
            print(f"Error executing agent {agent_id+1}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e

    def _format_parallel_results_for_frontend_with_helpers(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format parallel execution results specifically for frontend consumption using global helper functions.
        This approach reduces code duplication by leveraging element_extractor utilities.
        
        Args:
            session_data (Dict[str, Any]): Raw session data from parallel execution
            
        Returns:
            Dict[str, Any]: Formatted results for frontend
        """
        # Extract key information for frontend tabs
        formatted = {
            "execution_type": session_data.get("execution_type", "parallel"),
            "agent_count": session_data.get("agent_count", 0),
            "completed_agents": session_data.get("completed_agents", 0),
            "failed_agents": session_data.get("failed_agents", 0),
            "is_successful": session_data.get("completed_agents", 0) > 0,
            "execution_date": session_data.get("execution_date", datetime.datetime.now().isoformat()),
            "session_id": session_data.get("session_id", ""),
            "agent_results": [],
            "combined_interactions": {
                "total_interactions": 0,
                "action_types": [],
                "unique_elements": 0,
                "automation_data": {
                    "element_library": {},
                    "action_sequence": [],
                    "framework_selectors": {}
                },
                "element_details": {}  # Add element details
            }
        }
        
        # Process individual agent results
        all_action_types = set()
        total_interactions = 0
        unique_elements = 0
        
        for result in session_data.get("results", []):
            agent_result = {
                "agent_id": result.get("agent_id", 0),
                "status": result.get("status", "unknown"),
                "error": result.get("error", None),
                "details": result.get("result", {}).get("details", ""),
                "scenarios_count": result.get("result", {}).get("scenarios_count", 0),
                "execution_time": result.get("result", {}).get("execution_time", 0),  # Add execution time
                "interactions_count": result.get("result", {}).get("interactions_count", 0),  # Add interactions count
                # Add artifact information
                "artifacts": result.get("result", {}).get("artifacts", {})
            }
            formatted["agent_results"].append(agent_result)
            
            # Collect error information if any
            if result.get("status") == "failed":
                formatted["is_successful"] = False
        
        # Process tracked interactions from all agents using global helper functions
        combined_element_library = {}
        combined_action_sequence = []
        combined_framework_selectors = {}
        combined_element_details = {}  # Add element details collection
        
        # Prepare list of element details for merging
        element_details_list = []
        
        for interaction_data in session_data.get("tracked_interactions", []):
            agent_id = interaction_data.get("agent_id", 0)
            interactions = interaction_data.get("interactions", {})
            
            # Update metrics
            total_interactions += interactions.get("total_interactions", 0)
            unique_elements += interactions.get("unique_elements", 0)
            all_action_types.update(interactions.get("action_types", []))
            
            # Combine element library
            automation_data = interactions.get("automation_data", {})
            element_library = automation_data.get("element_library", {})
            for element_key, element_data in element_library.items():
                # Prefix element key with agent ID to avoid conflicts
                prefixed_key = f"agent_{agent_id}_{element_key}"
                combined_element_library[prefixed_key] = element_data
            
            # Combine action sequence
            action_sequence = automation_data.get("action_sequence", [])
            for action in action_sequence:
                # Add agent ID to action for tracking
                action_with_agent = action.copy()
                action_with_agent["agent_id"] = agent_id
                combined_action_sequence.append(action_with_agent)
            
            # Combine framework selectors
            framework_selectors = automation_data.get("framework_selectors", {})
            for selector_type, selectors in framework_selectors.items():
                if selector_type not in combined_framework_selectors:
                    combined_framework_selectors[selector_type] = {}
                for element_key, selector_value in selectors.items():
                    # Prefix element key with agent ID to avoid conflicts
                    prefixed_key = f"agent_{agent_id}_{element_key}"
                    combined_framework_selectors[selector_type][prefixed_key] = selector_value
            
            # Use global helper function to extract comprehensive element details
            # This leverages the element_extractor utilities instead of duplicating logic
            try:
                element_details = extract_all_element_details(interactions)
                if element_details:
                    # Prefix keys with agent ID to avoid conflicts
                    for key, value in element_details.items():
                        prefixed_key = f"agent_{agent_id}_{key}"
                        combined_element_details[prefixed_key] = value
                    # Add to list for merging
                    element_details_list.append(element_details)
            except Exception as e:
                logger.error(f"Error extracting element details for agent {agent_id}: {str(e)}")
        
        # Update combined interactions
        formatted["combined_interactions"] = {
            "total_interactions": total_interactions,
            "action_types": list(all_action_types),
            "unique_elements": unique_elements,
            "automation_data": {
                "element_library": combined_element_library,
                "action_sequence": combined_action_sequence,
                "framework_selectors": combined_framework_selectors
            },
            "element_details": combined_element_details,  # Include element details
            "execution_metrics": {  # Add execution metrics using helper functions
                "total_agents": session_data.get("agent_count", 0),
                "completed_agents": session_data.get("completed_agents", 0),
                "failed_agents": session_data.get("failed_agents", 0),
                "average_execution_time": self._calculate_average_execution_time(session_data.get("results", [])),
                "total_interactions": total_interactions,
                "interaction_rate": self._calculate_interaction_rate(session_data.get("results", []), total_interactions)
            }
        }
        
        # Add framework exports using the element tracker's built-in functionality
        # This eliminates code duplication by leveraging existing functionality
        try:
            # Use the global element tracker to generate framework exports
            # As per project requirements, we're simplifying this to only include browser-use framework
            formatted["framework_exports"] = {
                "browser_use": {
                    "framework": "browser_use",
                    "description": "Using browser-use framework for automation",
                    "note": "Playwright, Selenium, and Cypress code generation has been disabled as per project requirements"
                }
            }
        except Exception as e:
            logger.error(f"Error generating framework exports: {str(e)}")
            # Fallback to simple structure
            formatted["framework_exports"] = {
                "browser_use": {
                    "framework": "browser_use",
                    "description": "Using browser-use framework for automation",
                    "note": "Playwright, Selenium, and Cypress code generation has been disabled as per project requirements"
                }
            }
        
        return formatted
    
    def _format_results_for_frontend(self, session_data: Dict[str, Any], tracked_interactions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format results specifically for frontend consumption in the pipeline visualization.
        Uses element_extractor utilities to reduce code duplication.
        
        Args:
            session_data (Dict[str, Any]): Raw session data
            tracked_interactions (Dict[str, Any]): Element tracking data
            
        Returns:
            Dict[str, Any]: Formatted results for frontend
        """
        # Extract key information for frontend tabs
        formatted = {
            # Summary tab data
            "is_successful": session_data.get("is_successful", False),
            "final_result": session_data.get("final_result", ""),
            "total_duration": session_data.get("total_duration", 0),
            "action_names": session_data.get("action_names", []),
            
            # Actions tab data
            "detailed_actions": session_data.get("detailed_actions", []),
            
            # Use the new formatting function from element_extractor
        }
        
        # Format element interactions using the new utility function
        try:
            if tracked_interactions:
                # Create a structure compatible with the format_for_frontend function
                element_details_structure = {
                    "interaction_summary": {
                        "total_interactions": tracked_interactions.get("total_interactions", 0),
                        "unique_elements": tracked_interactions.get("unique_elements", 0),
                        "action_types": tracked_interactions.get("action_types", [])
                    },
                    "element_attributes": tracked_interactions.get("automation_data", {}).get("element_library", {}),
                    "framework_selectors": tracked_interactions.get("automation_data", {}).get("framework_selectors", {})
                }
                
                formatted_element_data = format_for_frontend(element_details_structure)
                formatted.update(formatted_element_data)
            else:
                # Fallback to original implementation
                formatted["element_interactions"] = {
                    "total_interactions": 0,
                    "unique_elements": 0,
                    "action_types": [],
                    "automation_data": {
                        "element_library": {},
                        "action_sequence": [],
                        "framework_selectors": {}
                    }
                }
        except Exception as e:
            logger.error(f"Error formatting element interactions: {str(e)}")
            # Fallback to original implementation
            formatted["element_interactions"] = {
                "total_interactions": tracked_interactions.get("total_interactions", 0) if tracked_interactions else 0,
                "unique_elements": tracked_interactions.get("unique_elements", 0) if tracked_interactions else 0,
                "action_types": tracked_interactions.get("action_types", []) if tracked_interactions else [],
                "automation_data": tracked_interactions.get("automation_data", {}) if tracked_interactions else {}
            }
        
        # Add debug tab data
        formatted.update({
            "screenshots": session_data.get("screenshots", []),
            "gif_path": session_data.get("gif_path"),
            "recording_paths": session_data.get("recording_paths", {}),
            
            # Agent tab data
            "model_outputs": session_data.get("model_outputs", []),
            "urls": session_data.get("urls", []),
            "number_of_steps": session_data.get("number_of_steps", 0),
            "execution_date": session_data.get("execution_date", datetime.datetime.now().isoformat())
        })
        
        # Use element_extractor utilities to get additional statistics
        try:
            if tracked_interactions:
                # Create a structure compatible with get_element_statistics
                element_details_for_stats = {
                    "element_attributes": tracked_interactions.get("automation_data", {}).get("element_library", {})
                }
                element_stats = get_element_statistics(element_details_for_stats)
                formatted["element_statistics"] = element_stats
        except Exception as e:
            logger.error(f"Error getting element statistics: {str(e)}")
        
        return formatted
    
    def _export_for_framework(self, tracked_interactions: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Export tracked interactions for browser-use framework only."""
        # Simplified implementation without code generation
        return {
            "framework": framework,
            "note": "Automation code generation has been disabled as per project requirements",
            "elements_tracked": len(tracked_interactions.get("element_library", {})) if isinstance(tracked_interactions.get("element_library"), dict) else 0
        }
    
    def _convert_action_to_framework(self, action: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Convert a generic action to framework-specific format.
        
        Note: As per project requirements, we're removing code generation.
        """
        # Simplified implementation without code generation
        return {
            "step_number": action["step_number"],
            "description": f"{action['action_type']} on {action['element_context']['tag_name']}",
            "action_type": action["action_type"],
            "element_reference": action["element_reference"]
        }
    
    def _generate_selenium_code(self, action: Dict[str, Any]) -> str:
        """Generate Selenium-specific code for an action.
        
        Note: As per project requirements, we're removing code generation.
        """
        # Return a note instead of actual code
        return "# Selenium code generation disabled as per project requirements"
    
    def _generate_playwright_code(self, action: Dict[str, Any]) -> str:
        """Generate Playwright-specific code for an action.
        
        Note: As per project requirements, we're removing code generation.
        """
        # Return a note instead of actual code
        return "# Playwright code generation disabled as per project requirements"
    
    def _generate_cypress_code(self, action: Dict[str, Any]) -> str:
        """Generate Cypress-specific code for an action.
        
        Note: As per project requirements, we're removing code generation.
        """
        # Return a note instead of actual code
        return "# Cypress code generation disabled as per project requirements"
    
    def _generate_page_object_element(self, element_data: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Generate page object element definition.
        
        Note: As per project requirements, we're removing code generation.
        """
        # Simplified implementation without code generation
        return {
            "tag_name": element_data["tag_name"],
            "selectors": element_data["selectors"],
            "attributes": element_data["attributes"],
            "meaningful_text": element_data.get("meaningful_text", "")
        }
    
    def _compile_session_data(
        self, 
        history, 
        all_actions: List[Dict[str, Any]], 
        element_xpath_map: Dict[str, str],
        all_extracted_content: List[Any], 
        all_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compile comprehensive session data from execution results.
        
        Args:
            history: Browser agent execution history
            all_actions: List of action details
            element_xpath_map: Element XPath mappings
            all_extracted_content: Extracted content list
            all_results: Execution results
            
        Returns:
            Dict[str, Any]: Comprehensive session data
        """
        # If history is None (simulation), create a basic structure
        if history is None:
            # This shouldn't happen with the real implementation, but just in case
            return {
                "urls": [],
                "action_names": [],
                "detailed_actions": [],
                "element_xpaths": {},
                "extracted_content": [],
                "errors": [],
                "execution_date": datetime.datetime.now().isoformat(),
                "screenshots": [],
                "screenshot_paths": [],
                "gif_path": None,
                "total_duration": 0,
                "number_of_steps": 0,
                "model_outputs": [],
                "final_result": "",
                "is_done": False,
                "is_successful": False,
                "recording_paths": {
                    "videos": "./recordings/videos",
                    "network_traces": "./recordings/network.traces",
                    "debug_traces": "./recordings/debug.traces"
                },
                "element_interactions": {
                    "total_interactions": 0,
                    "action_types": [],
                    "unique_elements": 0,
                    "automation_data": {
                        "element_library": {},
                        "action_sequence": [],
                        "framework_selectors": {}
                    }
                },
                "framework_exports": {
                    "selenium": {
                        "framework": "selenium",
                        "test_steps": [],
                        "page_objects": {},
                        "setup_data": {
                            "required_imports": [],
                            "setup_methods": [],
                            "teardown_methods": []
                        }
                    },
                    "playwright": {
                        "framework": "playwright",
                        "test_steps": [],
                        "page_objects": {},
                        "setup_data": {
                            "required_imports": [],
                            "setup_methods": [],
                            "teardown_methods": []
                        }
                    },
                    "cypress": {
                        "framework": "cypress",
                        "test_steps": [],
                        "page_objects": {},
                        "setup_data": {
                            "required_imports": [],
                            "setup_methods": [],
                            "teardown_methods": []
                        }
                    }
                }
            }
        
        # Extract data from the actual history object
        session_data = {
            "urls": history.urls() if hasattr(history, 'urls') else [],
            "action_names": history.action_names() if hasattr(history, 'action_names') else [],
            "detailed_actions": all_actions,
            "element_xpaths": element_xpath_map,
            "extracted_content": all_extracted_content,
            "errors": history.errors() if hasattr(history, 'errors') else [],
            "execution_date": datetime.datetime.now().isoformat(),
            # Enhanced data from browser-use features
            "screenshots": history.screenshots() if hasattr(history, 'screenshots') else [],
            "screenshot_paths": history.screenshot_paths() if hasattr(history, 'screenshot_paths') else [],
            "gif_path": self._find_gif_path(),
            "total_duration": history.total_duration_seconds() if hasattr(history, 'total_duration_seconds') else 0,
            "number_of_steps": history.number_of_steps() if hasattr(history, 'number_of_steps') else 0,
            # Additional browser-use features
            "model_outputs": history.model_outputs() if hasattr(history, 'model_outputs') else [],
            "final_result": history.final_result() if hasattr(history, 'final_result') else "",
            "is_done": history.is_done() if hasattr(history, 'is_done') else False,
            "is_successful": history.is_successful() if hasattr(history, 'is_successful') else False,
            # Recording paths for UI display using browser-use's native capabilities
            "recording_paths": {
                "videos": "./recordings/videos",
                "network_traces": "./recordings/network.traces",
                "debug_traces": "./recordings/debug.traces"
            },
            # Element interaction data will be added by the calling function
            "element_interactions": {
                "total_interactions": 0,
                "action_types": [],
                "unique_elements": 0,
                "automation_data": {
                    "element_library": {},
                    "action_sequence": [],
                    "framework_selectors": {}
                }
            },
            "framework_exports": {
                "browser_use": {
                    "framework": "browser_use",
                    "description": "Using browser-use framework for automation",
                    "note": "Playwright, Selenium, and Cypress code generation has been disabled as per project requirements"
                }
            }
        }
        
        return session_data
    
    def _find_gif_path(self) -> Optional[str]:
        """
        Find the path to the generated GIF file.
        
        Returns:
            Optional[str]: Path to the GIF file, or None if not found
        """
        # In a real implementation, this would search for the actual GIF file
        # For now, we'll return a placeholder
        return "./recordings/videos/execution_20241201_120000_scenario_1/execution.gif"

    def _parse_gherkin_scenarios(self, gherkin_content: str) -> List[str]:
        """
        Parse Gherkin content to extract individual scenarios.
        
        Args:
            gherkin_content: Gherkin scenarios text
            
        Returns:
            List of individual scenario strings
        """
        if not gherkin_content:
            return []
        
        # Log the Gherkin content being parsed
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Parsing Gherkin content: {gherkin_content}")
        
        # Split by "Scenario:" keyword
        scenarios = gherkin_content.split("Scenario:")
        
        # The first part is usually the feature description, so we skip it
        scenarios = scenarios[1:]
        
        # Re-add "Scenario:" to each scenario and strip whitespace
        scenarios = ["Scenario:" + s.strip() for s in scenarios]
        
        # Log the parsed scenarios
        logger.info(f"Parsed scenarios: {scenarios}")
        
        return scenarios
    
    def _calculate_average_execution_time(self, results: List[Dict[str, Any]]) -> float:
        """Calculate the average execution time for completed agents."""
        total_time = 0
        completed_count = 0
        for result in results:
            if result.get("status") == "completed":
                total_time += result.get("result", {}).get("execution_time", 0)
                completed_count += 1
        return total_time / completed_count if completed_count > 0 else 0
    
    def _calculate_interaction_rate(self, results: List[Dict[str, Any]], total_interactions: int) -> float:
        """Calculate the interaction rate (interactions per second)."""
        total_time = sum(r.get("result", {}).get("execution_time", 0) for r in results if r.get("status") == "completed")
        return total_interactions / total_time if total_time > 0 else 0

# Create a module-level instance
browser_execution_service = BrowserExecutionService()
