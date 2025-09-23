import asyncio
import sys
import platform
from typing import Any, Optional, Callable, Dict, List
from collections.abc import Awaitable
from app.agents.base_agent import BaseAgent
from browser_use import Agent as BrowserAgent
from browser_use.browser.events import ClickElementEvent, TypeTextEvent
from browser_use import BrowserProfile
from browser_use.dom.views import EnhancedDOMTreeNode
from pathlib import Path
import os
import subprocess
import tempfile
import time
import json
import datetime

# Import the prompt utilities to load instructions from markdown
from app.prompts.prompt_utils import load_agent_instructions
# Import the element tracker for element details extraction
from app.utils.element_tracker import ElementTracker
# Import global helper functions from element_extractor for better code reuse
from app.utils.element_extractor import extract_all_element_details, get_element_statistics

# Set event loop policy for Windows as early as possible
if platform.system() == "Windows":
    if sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    else:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class TrackingBrowserAgent(BrowserAgent):
    """Browser agent that tracks element interactions for script generation."""
    
    def __init__(self, task: str, llm: Any, **kwargs):
        # Extract our custom parameters before passing to parent
        self.generate_gif = kwargs.pop('generate_gif', False)
        self.highlight_elements = kwargs.pop('highlight_elements', True)
        self.record_video_dir = kwargs.pop('record_video_dir', None)
        self.record_har_path = kwargs.pop('record_har_path', None)
        self.traces_dir = kwargs.pop('traces_dir', None)
        headless = kwargs.pop('headless', True)  # Force headless mode
        window_size = kwargs.pop('window_size', None)
        self.use_vision = kwargs.pop('use_vision', True)
        self.record_har_content = kwargs.pop('record_har_content', 'embed')
        self.record_har_mode = kwargs.pop('record_har_mode', 'full')
        self.max_history_items = kwargs.pop('max_history_items', None)
        self.save_conversation_path = kwargs.pop('save_conversation_path', None)
        # Extract browser configuration parameters
        self.browser_name = kwargs.pop('browser_name', 'chrome')
        self.browser_executable_path = kwargs.pop('browser_executable_path', None)
        self.browser_resolution = kwargs.pop('browser_resolution', None)
        self.keep_alive = kwargs.pop('keep_alive', False)
        
        # Create element tracker instance for this agent
        self.element_tracker = ElementTracker()
        
        # Set event loop policy for Windows to avoid subprocess issues (redundant but safe)
        if platform.system() == "Windows":
            if sys.version_info >= (3, 8):
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            else:
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # Set up browser profile with enhanced features and recording parameters
        if 'browser' not in kwargs and 'browser_session' not in kwargs:
            # Handle Windows-specific browser configuration to avoid subprocess issues
            browser_kwargs = {
                "headless": headless,
                "window_size": window_size,
                "record_video_dir": self.record_video_dir,
                "record_har_path": self.record_har_path,
                "traces_dir": self.traces_dir,
                "record_har_content": self.record_har_content,
                "record_har_mode": self.record_har_mode
            }
            
            # Remove None values
            browser_kwargs = {k: v for k, v in browser_kwargs.items() if v is not None}
            
            # Apply browser resolution if provided
            if self.browser_resolution:
                try:
                    width, height = self.browser_resolution
                    browser_kwargs["window_size"] = {"width": width, "height": height}
                except (TypeError, ValueError):
                    pass  # Invalid resolution format, ignore
            
            # Special handling for Windows to avoid subprocess issues
            if platform.system() == "Windows":
                # For Windows, we'll launch Chrome manually with remote debugging and connect to it
                cdp_url = self._launch_chrome_with_remote_debugging()
                if cdp_url:
                    # Connect to remote browser instead of launching local one
                    browser_kwargs["cdp_url"] = cdp_url
                    browser_kwargs["is_local"] = False
                    # Remove headless parameter as we're connecting to existing browser
                    browser_kwargs.pop("headless", None)
                else:
                    # Fallback to local browser launch with additional Windows-specific flags
                    browser_kwargs["headless"] = True
                    browser_kwargs["disable_backgrounding_observable"] = True
                    browser_kwargs["disable_renderer_backgrounding"] = True
                    browser_kwargs["disable_background_timer_throttling"] = True
                    # Add additional Windows-specific flags
                    browser_kwargs["args"] = [
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-extensions",
                        "--disable-background-timer-throttling",
                        "--disable-renderer-backgrounding",
                        "--disable-backgrounding-observable",
                        "--disable-features=VizDisplayCompositor",
                        "--disable-web-security",
                        "--allow-running-insecure-content",
                        "--disable-features=IsolateOrigins,site-per-process",
                        "--disable-ipc-flooding-protection",
                        "--disable-background-networking",
                        "--disable-default-apps",
                        "--disable-breakpad"
                    ]
                    browser_kwargs["keep_alive"] = False
                    browser_kwargs["chromium_sandbox"] = False
                    browser_kwargs["is_local"] = True
            
            # Add browser executable path if specified
            if self.browser_executable_path:
                browser_kwargs["executable_path"] = self.browser_executable_path
            elif self.browser_name:
                # Import browser config service to detect browser paths
                from app.services.browser_config_service import browser_config_service
                installed_browsers = browser_config_service.detect_installed_browsers()
                if self.browser_name.lower() in installed_browsers:
                    browser_kwargs["executable_path"] = installed_browsers[self.browser_name.lower()]
            
            # Add keep_alive parameter for shared browser sessions
            if self.keep_alive:
                browser_kwargs["keep_alive"] = True
            
            browser_profile = BrowserProfile(**browser_kwargs)
            kwargs['browser_profile'] = browser_profile
        
        # Pass the browser-use specific parameters directly to the Agent
        # Use a string path for generate_gif to control where browser-use creates the GIF
        # If we want to generate our own GIF in a specific location, we'll handle that separately
        if self.generate_gif and self.record_video_dir:
            kwargs['generate_gif'] = str(Path(self.record_video_dir) / "execution.gif")
        else:
            kwargs['generate_gif'] = self.generate_gif
        kwargs['highlight_elements'] = self.highlight_elements
        kwargs['use_vision'] = self.use_vision
        kwargs['max_history_items'] = self.max_history_items
        kwargs['save_conversation_path'] = self.save_conversation_path
        
        # Load browser execution instructions from markdown file
        browser_instructions = load_agent_instructions("browser_execution")
        
        # Generate enhanced task prompt using the browser execution instructions
        execution_context = {
            "current_url": "about:blank",
            "visited_urls": [],
            "session_data": {}
        }
        
        # Format the task with the instructions and context
        enhanced_task = f"{browser_instructions}\n\n**Given Gherkin Scenario:**\n\n```gherkin\n{task}\n```"
        
        super().__init__(task=enhanced_task, llm=llm, **kwargs)
        self.on_step_end_callback = None
        self._interactions_cleared = False
        self._event_handlers_registered = False
        self.interactions: List[Dict[str, Any]] = []
        # Store Chrome process for cleanup on Windows
        self._chrome_process = None
    
    def _launch_chrome_with_remote_debugging(self) -> Optional[str]:
        """Launch Chrome with remote debugging enabled and return the CDP URL."""
        try:
            # Import browser config service
            from app.services.browser_config_service import browser_config_service
            
            # Get browser executable path
            executable_path = self.browser_executable_path
            if not executable_path:
                installed_browsers = browser_config_service.detect_installed_browsers()
                executable_path = installed_browsers.get(self.browser_name.lower(), 
                                                       "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
            
            if not os.path.exists(executable_path):
                # Try alternative paths
                chrome_paths = [
                    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                    os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
                ]
                for path in chrome_paths:
                    if os.path.exists(path):
                        executable_path = path
                        break
                else:
                    print("Chrome not found at expected locations")
                    return None
            
            # Create a temporary user data directory
            temp_dir = tempfile.mkdtemp(prefix="browser_use_chrome_")
            
            # Find a free port for remote debugging
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', 0))
                port = s.getsockname()[1]
            
            # Launch Chrome with remote debugging
            chrome_args = [
                executable_path,
                f"--remote-debugging-port={port}",
                f"--user-data-dir={temp_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-observable",
                "--disable-ipc-flooding-protection"
            ]
            
            # Apply window size if specified
            if self.browser_resolution:
                try:
                    width, height = self.browser_resolution
                    chrome_args.extend([
                        f"--window-size={width},{height}",
                        "--disable-web-security"
                    ])
                except (TypeError, ValueError):
                    pass  # Invalid resolution format, ignore
            
            print(f"Launching {self.browser_name} with remote debugging on port {port}")
            process = subprocess.Popen(chrome_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._chrome_process = process
            
            # Wait for Chrome to start and get the CDP URL
            cdp_url = f"http://127.0.0.1:{port}"
            
            # Wait a moment for Chrome to start
            time.sleep(2)
            
            # Verify Chrome is running
            if process.poll() is not None:
                print("Chrome process terminated unexpectedly")
                return None
                
            print(f"{self.browser_name} launched successfully with CDP URL: {cdp_url}")
            return cdp_url
            
        except Exception as e:
            print(f"Failed to launch {self.browser_name} with remote debugging: {e}")
            return None
    
    def __del__(self):
        """Cleanup Chrome process if it was launched."""
        if hasattr(self, '_chrome_process') and self._chrome_process:
            try:
                self._chrome_process.terminate()
                self._chrome_process.wait(timeout=5)
            except:
                try:
                    self._chrome_process.kill()
                except:
                    pass
    
    async def run(
        self,
        max_steps: int = 100,
        on_step_start: Callable[['BrowserAgent'], Awaitable[None]] | None = None,
        on_step_end: Callable[['BrowserAgent'], Awaitable[None]] | None = None,
    ):
        """Run the agent and track interactions."""
        # Clear previous interactions only if this is a fresh run
        if not self._interactions_cleared:
            self.clear_interactions()
            self._interactions_cleared = True
        
        # Ensure event handlers are registered before running
        self._ensure_event_handlers_registered()
        
        # Override the on_step_end callback to add our tracking
        async def wrapped_on_step_end(agent):
            # Call the original on_step_end if it exists
            if on_step_end:
                await on_step_end(agent)
            
            # Call our custom callback if it exists
            if self.on_step_end_callback:
                if asyncio.iscoroutinefunction(self.on_step_end_callback):
                    await self.on_step_end_callback(agent)
                else:
                    self.on_step_end_callback(agent)
        
        # Run the parent agent with our wrapped callback
        try:
            result = await super().run(max_steps, on_step_start, wrapped_on_step_end)
            
            # Capture final screenshot after execution using browser-use's native method
            try:
                # Use browser-use's built-in take_screenshot method if available
                if hasattr(self, 'browser_session') and self.browser_session:
                    await self.browser_session.take_screenshot()
            except Exception as e:
                print(f"Error capturing final screenshot: {e}")
            
            return result
        except Exception as e:
            # Re-raise the exception to be handled by the caller
            raise
        finally:
            # Cleanup resources
            await self._cleanup_resources()
    
    async def _cleanup_resources(self):
        """Clean up resources after execution."""
        try:
            # Cleanup Chrome process if it was launched
            if hasattr(self, '_chrome_process') and self._chrome_process:
                try:
                    self._chrome_process.terminate()
                    await asyncio.sleep(0.1)  # Small delay
                    if self._chrome_process.poll() is None:  # Still running
                        self._chrome_process.kill()
                except Exception as e:
                    print(f"Error cleaning up Chrome process: {e}")
                finally:
                    self._chrome_process = None
            
            # Clean up browser session if it exists
            if hasattr(self, 'browser_session') and self.browser_session:
                try:
                    # Only stop if it's not a shared session
                    if not getattr(self, 'keep_alive', False):
                        await self.browser_session.stop()
                except Exception as e:
                    print(f"Error stopping browser session: {e}")
        except Exception as e:
            print(f"Error during resource cleanup: {e}")
    
    def _ensure_event_handlers_registered(self):
        """Ensure event handlers are registered when browser is available."""
        # Only register once and only if browser is available
        if self._event_handlers_registered:
            return
            
        if not hasattr(self, 'browser_session') or not self.browser_session:
            print("Warning: Browser session not available for event handler registration")
            return  # Browser not initialized yet, will try again later
            
        # Register click event handler
        self.browser_session.event_bus.on(ClickElementEvent, self._handle_click_event)
        
        # Register type text event handler
        self.browser_session.event_bus.on(TypeTextEvent, self._handle_type_text_event)
        
        self._event_handlers_registered = True
        print("Event handlers registered successfully")
    
    def _handle_click_event(self, event: ClickElementEvent):
        """Handle click events and track them."""
        try:
            print(f"Handling click event: {event}")  # Debug print
            self.track_click(event)
        except Exception as e:
            print(f"Error tracking click event: {e}")
    
    def _handle_type_text_event(self, event: TypeTextEvent):
        """Handle type text events and track them."""
        try:
            print(f"Handling type text event: {event}")  # Debug print
            self.track_type_text(event)
        except Exception as e:
            print(f"Error tracking type text event: {e}")
    
    def update_context(self, context: Dict[str, Any]):
        """Update the execution context."""
        self.element_tracker.update_context(context)
    
    def extract_element_details(self, node: EnhancedDOMTreeNode) -> Dict[str, Any]:
        """Extract comprehensive element details using the element tracker."""
        return self.element_tracker.extract_element_details(node)
    
    def track_click(self, event: ClickElementEvent) -> None:
        """Track a click event."""
        # Use the element tracker to track the click
        self.element_tracker.track_click(event)
        # Get the tracked interaction and add it to our interactions list
        interactions = self.element_tracker.get_interactions()
        if interactions:
            self.interactions.append(interactions[-1])  # Add the latest interaction
        print(f"Total interactions after click: {len(self.interactions)}")
    
    def track_type_text(self, event: TypeTextEvent) -> None:
        """Track a type text event."""
        # Use the element tracker to track the type text
        self.element_tracker.track_type_text(event)
        # Get the tracked interaction and add it to our interactions list
        interactions = self.element_tracker.get_interactions()
        if interactions:
            self.interactions.append(interactions[-1])  # Add the latest interaction
        print(f"Total interactions after type text: {len(self.interactions)}")
    
    def get_tracked_interactions(self):
        """Get all tracked element interactions using global helper functions for better reliability."""
        # Ensure handlers are registered
        self._ensure_event_handlers_registered()
        
        # Prepare interaction data for element extractor
        interaction_data = {
            "element_interactions": {
                "total_interactions": len(self.interactions),
                "action_types": list(set(i["action_type"] for i in self.interactions)),
                "unique_elements": len(set(
                    i["element_details"].get("element_index", 0) 
                    for i in self.interactions 
                    if i["element_details"].get("element_index") is not None
                )),
                "automation_data": self.element_tracker.get_automation_script_data() if hasattr(self.element_tracker, 'get_automation_script_data') else {}
            }
        }
        
        # Use global helper functions to extract comprehensive element details
        # This leverages the element_extractor utilities instead of duplicating logic
        try:
            element_details = extract_all_element_details(interaction_data)
        except Exception as e:
            print(f"Error extracting element details using global helper function: {e}")
            element_details = {}
        
        # Get additional statistics using global helper function
        try:
            stats = get_element_statistics(element_details) if element_details else {}
        except Exception as e:
            print(f"Error getting element statistics using global helper function: {e}")
            stats = {}
        
        # Get screenshot paths if available from browser-use's native recording
        screenshot_paths = []
        if self.record_video_dir:
            screenshots_dir = Path(self.record_video_dir) / 'screenshots'
            if screenshots_dir.exists():
                screenshot_paths = [str(f) for f in screenshots_dir.glob('*.png')]
        
        # Return the interaction data directly from the agent's interactions list for compatibility with tests
        return {
            "total_interactions": len(self.interactions),
            "action_types": list(set(i["action_type"] for i in self.interactions)),
            "interactions": self.interactions.copy(),
            "unique_elements": len(set(
                i["element_details"].get("element_index", 0) 
                for i in self.interactions 
                if i["element_details"].get("element_index") is not None
            )),
            "automation_data": self.element_tracker.get_automation_script_data() if hasattr(self.element_tracker, 'get_automation_script_data') else {},
            "element_details": element_details,
            "statistics": stats,
            "screenshot_paths": screenshot_paths
        }
    
    def clear_interactions(self) -> None:
        """Clear all tracked interactions."""
        self.interactions = []
        # Also clear the element tracker's interactions
        self.element_tracker.clear_interactions()
    
    def get_element_details(self, element_key: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific element by its key."""
        return self.element_tracker.get_element_details(element_key)
    
    def get_all_elements(self) -> Dict[str, Any]:
        """Get all tracked elements."""
        return self.element_tracker.get_all_elements()
    
    def get_action_sequence(self) -> List[Dict[str, Any]]:
        """Get the sequence of actions performed."""
        return self.element_tracker.get_action_sequence()
    
    def get_framework_selectors(self, framework: str) -> Dict[str, Any]:
        """Get selectors for a specific automation framework."""
        return self.element_tracker.get_framework_selectors(framework)
    
    def export_for_framework(self, framework: str = "selenium") -> Dict[str, Any]:
        """Export interactions formatted for specific automation framework."""
        return self.element_tracker.export_for_framework(framework)


def create_browser_execution_agent(model_provider: str = "Google", model_name: str = "gemini-2.0-flash") -> BaseAgent:
    """
    Create a browser execution agent.
    
    Args:
        model_provider (str): The model provider to use
        model_name (str): The specific model to use
        
    Returns:
        BaseAgent: Configured browser execution agent
    """
    # This function is kept for compatibility but not used in the current implementation
    # The TrackingBrowserAgent class is used directly instead
    pass