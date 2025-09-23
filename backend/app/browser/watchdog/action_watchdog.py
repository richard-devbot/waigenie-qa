import asyncio
from typing import List, Dict, Any
from browser_use.browser.watchdogs.default_action_watchdog import DefaultActionWatchdog
from browser_use.browser.events import (
    ClickElementEvent,
    GetDropdownOptionsEvent,
    GoBackEvent,
    GoForwardEvent,
    RefreshEvent,
    ScrollEvent,
    ScrollToTextEvent,
    SelectDropdownOptionEvent,
    SendKeysEvent,
    TypeTextEvent,
    UploadFileEvent,
    WaitEvent,
)
from browser_use.browser.views import BrowserError, URLNotAllowedError
from browser_use.browser.watchdog_base import BaseWatchdog
from browser_use.dom.service import EnhancedDOMTreeNode
from pydantic import Field

class CustomActionWatchdog(DefaultActionWatchdog):
    # Add the custom field to the model
    allow_parallel_action_types: List[str] = Field(default_factory=lambda: ["extract_structured_data", "extract_content_from_file"])
        
    async def on_ClickElementEvent(self, event: ClickElementEvent) -> None:
        """Handle click request with CDP."""
        try:
            # Check if session is alive before attempting any operations
            if not self.browser_session.agent_focus or not self.browser_session.agent_focus.target_id:
                error_msg = 'Cannot execute click: browser session is corrupted (target_id=None). Session may have crashed.'
                self.logger.error(f'⚠️ {error_msg}')
                raise BrowserError(error_msg)

            # Use the provided node
            element_node = event.node
            index_for_logging = element_node.element_index or 'unknown'
            starting_target_id = self.browser_session.agent_focus.target_id

            # Track initial number of tabs to detect new tab opening
            if hasattr(self.browser_session, "main_browser_session") and self.browser_session.main_browser_session:
                initial_target_ids = await self.browser_session.main_browser_session._cdp_get_all_pages()
            else:
                initial_target_ids = await self.browser_session._cdp_get_all_pages()

            # Check if element is a file input (should not be clicked)
            if self.browser_session.is_file_input(element_node):
                msg = f'Index {index_for_logging} - has an element which opens file upload dialog. To upload files please use a specific function to upload files'
                self.logger.info(msg)
                raise BrowserError(
                    message=msg,
                    long_term_memory=msg,
                )

            # Perform the actual click using internal implementation
            click_metadata = None
            click_metadata = await self._click_element_node_impl(element_node,
                                                                 while_holding_ctrl=event.while_holding_ctrl)
            download_path = None  # moved to downloads_watchdog.py

            # Build success message
            if download_path:
                msg = f'Downloaded file to {download_path}'
                self.logger.info(f'💾 {msg}')
            else:
                msg = f'Clicked button with index {index_for_logging}: {element_node.get_all_children_text(max_depth=2)}'
                self.logger.debug(f'🖱️ {msg}')
            self.logger.debug(f'Element xpath: {element_node.xpath}')

            # Wait a bit for potential new tab to be created
            # This is necessary because tab creation is async and might not be immediate
            await asyncio.sleep(0.5)

            # Clear cached state after click action since DOM might have changed
            self.browser_session.agent_focus = await self.browser_session.get_or_create_cdp_session(
                target_id=starting_target_id, focus=True
            )

            # Check if a new tab was opened
            if hasattr(self.browser_session, "main_browser_session") and self.browser_session.main_browser_session:
                after_target_ids = await self.browser_session.main_browser_session._cdp_get_all_pages()
            else:
                after_target_ids = await self.browser_session._cdp_get_all_pages()
            new_target_ids = {t['targetId'] for t in after_target_ids} - {t['targetId'] for t in initial_target_ids}
            if new_target_ids:
                new_tab_msg = 'New tab opened - switching to it'
                msg += f' - {new_tab_msg}'
                self.logger.info(f'🔗 {new_tab_msg}')
                new_target_id = new_target_ids.pop()
                if not event.while_holding_ctrl:
                    # if while_holding_ctrl=False it means agent was not expecting a new tab to be opened
                    # so we need to switch to the new tab to make the agent aware of the surprise new tab that was opened.
                    # when while_holding_ctrl=True we dont actually want to switch to it,
                    # we should match human expectations of ctrl+click which opens in the background,
                    # so in multi_act it usually already sends [click_element_by_index(123, while_holding_ctrl=True), switch_tab(tab_id=None)] anyway
                    from browser_use.browser.events import SwitchTabEvent

                    await self.browser_session.get_or_create_cdp_session(
                        target_id=new_target_id, focus=True
                    )
                else:
                    await self.browser_session.get_or_create_cdp_session(
                        target_id=new_target_id, focus=False
                    )

            return None
        except Exception as e:
            raise

    def _matches_action_type(self, action_type: str, allowed_pattern: str) -> bool:
        """
        Check if an action type matches an allowed pattern, supporting wildcards.
        
        Args:
            action_type: The actual action type (e.g., "mcp.filesystem.read_file")
            allowed_pattern: The pattern to match (e.g., "mcp.filesystem*")
            
        Returns:
            True if the action type matches the pattern
        """
        if allowed_pattern.endswith('*'):
            # Wildcard matching
            prefix = allowed_pattern[:-1]
            return action_type.startswith(prefix)
        else:
            # Exact matching
            return action_type == allowed_pattern

    def _is_action_parallel_allowed(self, action_name: str) -> bool:
        """
        Check if an action is allowed to be executed in parallel.
        
        Args:
            action_name: The name of the action to check
            
        Returns:
            True if the action can be executed in parallel
        """
        if not action_name:
            return False

        for allowed_pattern in self.allow_parallel_action_types:
            if self._matches_action_type(action_name, allowed_pattern):
                return True

        return False

    def _group_actions_for_parallel_execution(self, actions: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Group consecutive actions that can be executed in parallel.
        
        Args:
            actions: List of actions to group
            
        Returns:
            List of action groups, where each group can be executed in parallel
        """
        if not actions:
            return []

        groups = []
        current_group = [actions[0]]

        for i in range(1, len(actions)):
            current_action = actions[i]
            previous_action = actions[i - 1]
            
            # Get action names
            current_action_name = next(iter(current_action.keys())) if current_action else None
            previous_action_name = next(iter(previous_action.keys())) if previous_action else None

            # Check if both current and previous actions can be executed in parallel
            if (self._is_action_parallel_allowed(current_action_name) and
                    self._is_action_parallel_allowed(previous_action_name)):
                # Add to current group
                current_group.append(current_action)
            else:
                # Start a new group
                groups.append(current_group)
                current_group = [current_action]

        # Add the last group
        groups.append(current_group)

        return groups

    async def execute_actions_in_parallel(self, actions: List[Dict[str, Any]]) -> List[Any]:
        """Execute a group of actions in parallel using asyncio.gather"""

        async def execute_single_parallel_action(action: Dict[str, Any], action_index: int) -> Any:
            """Execute a single action for parallel execution"""
            # Get action info for logging
            action_name = next(iter(action.keys())) if action else 'unknown'
            action_params = action.get(action_name, {})
            
            self.logger.info(f'  🦾 [PARALLEL ACTION {action_index + 1}/{len(actions)}] {action_name}: {action_params}')

            # Execute the action based on its type
            try:
                # First, try to execute using BrowserUseTools if available
                if hasattr(self.browser_session, 'browser_use_tools'):
                    # Check if the action is available in BrowserUseTools
                    tool_actions = getattr(self.browser_session.browser_use_tools, '_registered_actions', {})
                    if action_name in tool_actions:
                        # Execute using BrowserUseTools
                        result = await tool_actions[action_name](action_params)
                        return result
                
                # Fallback to default event-based execution
                # Map action names to event classes
                event_class_map = {
                    "ClickElement": ClickElementEvent,
                    "GetDropdownOptions": GetDropdownOptionsEvent,
                    "GoBack": GoBackEvent,
                    "GoForward": GoForwardEvent,
                    "Refresh": RefreshEvent,
                    "Scroll": ScrollEvent,
                    "ScrollToText": ScrollToTextEvent,
                    "SelectDropdownOption": SelectDropdownOptionEvent,
                    "SendKeys": SendKeysEvent,
                    "TypeText": TypeTextEvent,
                    "UploadFile": UploadFileEvent,
                    "Wait": WaitEvent,
                }
                
                # Create event object
                if action_name in event_class_map:
                    event_class = event_class_map[action_name]
                    # Create event instance with parameters
                    # Handle special case where some events might need the node from selector map
                    if action_name == "ClickElement" and "index" in action_params:
                        # For ClickElement, we need to get the node from the selector map
                        selector_map = await self.browser_session.get_selector_map()
                        if action_params["index"] in selector_map:
                            action_params["node"] = selector_map[action_params["index"]]
                    
                    event_instance = event_class(**action_params) if action_params else event_class()
                    
                    # Get the appropriate method to call based on the action name
                    method_name = f"on_{action_name}Event"
                    if hasattr(self, method_name):
                        method = getattr(self, method_name)
                        # Execute the method with the event
                        result = await method(event_instance)
                        return result
                    else:
                        raise ValueError(f"Method {method_name} not found for action {action_name}")
                else:
                    raise ValueError(f"Unsupported action type: {action_name}")
            except Exception as e:
                self.logger.error(f'❌ Parallel action {action_index + 1} failed: {type(e).__name__}: {e}')
                raise e

        # Create tasks for parallel execution
        tasks = [
            execute_single_parallel_action(action, i)
            for i, action in enumerate(actions)
        ]

        # Execute all tasks in parallel
        parallel_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle any exceptions
        processed_results = []
        for i, result in enumerate(parallel_results):
            if isinstance(result, Exception):
                self.logger.error(f'❌ Parallel action {i + 1} failed: {type(result).__name__}: {result}')
                # Instead of raising, we'll return the error as part of results
                processed_results.append(result)
            else:
                processed_results.append(result)

        return processed_results