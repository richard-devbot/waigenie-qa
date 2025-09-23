import traceback
from typing import Dict, Any, Optional
import uuid
import asyncio
import logging
import platform
import sys
from app.services.story_service import StoryService
from app.services.test_case_service import TestCaseService
from app.services.gherkin_service import GherkinService
from app.services.browser_execution_service import BrowserExecutionService
from app.services.code_generation_service import CodeGenerationService
from app.utils.task_manager import TaskManager
from app.services.mcp_service import mcp_service

# Set event loop policy for Windows as early as possible
if platform.system() == "Windows":
    if sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    else:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineService:
    """Service for orchestrating the end-to-end pipeline process."""
    
    def __init__(self):
        self.story_service = StoryService()
        self.test_case_service = TestCaseService()
        self.gherkin_service = GherkinService()
        self.browser_execution_service = BrowserExecutionService()
        self.code_generation_service = CodeGenerationService()
        self.task_manager = TaskManager()
    
    async def start_pipeline(
        self, 
        raw_story: str, 
        framework: str, 
        context: Optional[str] = None,
        provider: str = "Google",
        model: str = "gemini-2.0-flash",
        browser_name: str = "chrome",
        browser_executable_path: str = None,
        browser_resolution: tuple = None,
        vision_enabled: bool = True,
        cdp_port: int = None
    ) -> str:
        """Start the end-to-end pipeline process."""
        task_id = str(uuid.uuid4())
        
        # Initialize task in task manager with proper structure
        self.task_manager.set_task_status(
            task_id, 
            "ENHANCING_STORY", 
            {
                "status": "RUNNING",
                "current_stage": "ENHANCING_STORY",
                "message": "Enhancing user story...",
                "results": {}
            }
        )
        
        # Run the pipeline in background
        asyncio.create_task(
            self._run_pipeline(task_id, raw_story, framework, context, provider, model, browser_name, browser_executable_path, browser_resolution, vision_enabled, cdp_port)
        )
        
        return task_id
    
    async def _run_pipeline(
        self,
        task_id: str,
        raw_story: str,
        framework: str,
        context: Optional[str] = None,
        provider: str = "Google",
        model: str = "gemini-2.0-flash",
        browser_name: str = "chrome",
        browser_executable_path: str = None,
        browser_resolution: tuple = None,
        vision_enabled: bool = True,
        cdp_port: int = None
    ):
        """Run the complete pipeline process."""
        results = {}
        
        try:
            # Stage 1: Enhance User Story
            logger.info(f"Task {task_id}: Stage 1 - Enhancing user story")
            self._update_task_status(task_id, "ENHANCING_STORY", "Enhancing user story with AI...", results)
            
            enhanced_story_response = await self.story_service.enhance_user_story(raw_story, provider, model, context)
            enhanced_story_data = enhanced_story_response.get("data", {})
            enhanced_story_text = enhanced_story_data.get("enhanced_story", str(enhanced_story_response))
            results['enhanced_story'] = enhanced_story_response
            
            logger.info(f"Task {task_id}: Stage 1 completed successfully")
            self._update_task_with_results(task_id, "ENHANCING_STORY", "User story enhanced successfully!", results, enhanced_story_response)
            
            # Stage 2: Generate Manual Test Cases
            logger.info(f"Task {task_id}: Stage 2 - Generating manual test cases")
            self._update_task_status(task_id, "GENERATING_TESTS", "Generating manual test cases...", results)
            
            manual_tests_response = self.test_case_service.generate_test_cases(enhanced_story_text, context, provider, model)
            manual_tests_data = manual_tests_response.get("data", {})
            manual_tests_list = manual_tests_data.get("test_cases", [])
            results['manual_tests'] = manual_tests_response
            
            logger.info(f"Task {task_id}: Stage 2 completed successfully")
            self._update_task_with_results(task_id, "GENERATING_TESTS", "Manual test cases generated successfully!", results, manual_tests_response)
            
            # Stage 3: Generate Gherkin Scenarios
            logger.info(f"Task {task_id}: Stage 3 - Generating Gherkin scenarios")
            self._update_task_status(task_id, "GENERATING_GHERKIN", "Generating Gherkin scenarios...", results)
            
            gherkin_response = self.gherkin_service.generate_gherkin_scenarios(manual_tests_list, context, provider, model)
            gherkin_data = gherkin_response.get("data", {})
            gherkin_scenarios = gherkin_data.get("scenarios", [])
            gherkin_string = self._format_gherkin_for_execution(gherkin_scenarios)
            
            # Log the Gherkin string for debugging
            logger.info(f"Gherkin string being passed to browser execution: {gherkin_string}")
            
            results['gherkin_scenarios'] = gherkin_response
            
            logger.info(f"Task {task_id}: Stage 3 completed successfully")
            # Update task with results immediately after completion
            self._update_task_with_results(task_id, "GENERATING_GHERKIN", "Gherkin scenarios generated successfully!", results, gherkin_response)
            
            # Stage 4: Execute Browser Automation
            logger.info(f"Task {task_id}: Stage 4 - Executing browser automation")
            self._update_task_status(task_id, "EXECUTING_BROWSER", "Executing browser automation...", results)
            
            # Check if we should use parallel execution for multiple scenarios
            # use_parallel_execution = len(gherkin_scenarios) > 1
            
            # Always use parallel execution for all scenarios
            logger.info(f"Task {task_id}: Using parallel execution for {len(gherkin_scenarios)} scenarios")
            
            # Convert scenarios to individual test scripts
            test_scripts = []
            for scenario in gherkin_scenarios:
                if isinstance(scenario, str):
                    test_scripts.append(scenario)
                else:
                    # Format dict scenario as string
                    formatted_scenario = self._format_single_scenario(scenario)
                    test_scripts.append(formatted_scenario)
            
            # Submit parallel browser execution task to MCP service
            browser_payload = {
                "test_scripts": test_scripts,
                "provider": provider,
                "model": model,
                "browser_name": browser_name,
                "browser_executable_path": browser_executable_path,
                "browser_resolution": browser_resolution,
                "vision_enabled": vision_enabled,
                "cdp_port": cdp_port
            }
            
            browser_task_id = await mcp_service.submit_mcp_job("browser_use_parallel_execution", browser_payload)
            
            # # // Remove single execution fallback
            # // else:
            # //     # Use single execution for single scenario
            # //     logger.info(f"Task {task_id}: Using single execution for 1 scenario")
            # //     
            # //     # Submit browser execution task to MCP service
            # //     browser_payload = {
            # //         "test_script": gherkin_string,
            # //         "provider": provider,
            # //         "model": model,
            # //         "browser_name": browser_name,
            # //         "browser_executable_path": browser_executable_path,
            # //         "browser_resolution": browser_resolution
            # //     }
            # //     
            # //     browser_task_id = await mcp_service.submit_mcp_job("browser_use_execution", browser_payload)
            
            # Poll for completion
            execution_result = None
            max_wait_time = 600  # Increase timeout to 10 minutes for complex scenarios
            wait_interval = 2    # 2 seconds between checks
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                status = await mcp_service.get_job_status(browser_task_id)
                if status["status"] in ["completed", "failed"]:
                    if status["status"] == "completed":
                        execution_result = status["result"]
                        break
                    else:
                        raise Exception(f"Browser execution failed: {status['error']}")
                await asyncio.sleep(wait_interval)
                elapsed_time += wait_interval
            
            # Check if we timed out
            if execution_result is None:
                # Try to cancel the job if it exists
                try:
                    # In a real implementation, we would have a cancel method
                    # For now, we'll just log that we're timing out
                    logger.warning(f"Browser execution timed out after {max_wait_time} seconds, attempting to clean up...")
                except Exception as cleanup_e:
                    logger.error(f"Error during timeout cleanup: {cleanup_e}")
                raise Exception(f"Browser execution timed out after {max_wait_time} seconds")
            
            results['browser_execution'] = execution_result
            history_data = execution_result.get("results", {})
            
            logger.info(f"Task {task_id}: Stage 4 completed successfully")
            self._update_task_with_results(task_id, "EXECUTING_BROWSER", "Browser automation executed successfully!", results, execution_result)
            
            # Stage 5: Generate Code
            logger.info(f"Task {task_id}: Stage 5 - Generating automation code")
            
            # Simplify history_data to avoid recursive references that cause AGNO agent to fail
            simplified_history_data = self._simplify_history_data(history_data)
            
            code_response = self.code_generation_service.generate_automation_code(
                gherkin_steps=gherkin_string,
                history_data=simplified_history_data,
                framework=framework,
                provider=provider,
                model=model
            )
            
            code_data = code_response.get("data", {})
            generated_code = code_data.get("code", "")
            results['generated_code'] = code_response
            
            logger.info(f"Task {task_id}: Pipeline completed successfully")
            
            # Final completion update with structured data for frontend
            self.task_manager.set_task_status(
                task_id,
                "COMPLETED",
                {
                    "status": "COMPLETED",
                    "current_stage": "COMPLETED",
                    "message": "Pipeline completed successfully!",
                    "results": results,
                    # Flatten results for easier frontend access with proper structure
                    "enhanced_story": {
                        "content": enhanced_story_text,
                        "parsed": enhanced_story_data.get("parsed_story", {})
                    },
                    "test_cases": {
                        "test_cases": manual_tests_list
                    },
                    "gherkin_scenarios": {
                        "scenarios": gherkin_scenarios
                    },
                    "browser_execution": {
                        "results": execution_result.get("results", {}),
                        "raw_response": execution_result.get("raw_response", ""),
                        "test_scripts": execution_result.get("test_scripts", [])
                    },
                    "generated_code": {
                        "code": generated_code,
                        "framework": code_data.get("framework", framework)
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Pipeline failed with error: {str(e)}")
            logger.error(traceback.format_exc())
            
            self.task_manager.set_task_status(
                task_id,
                "FAILED",
                {
                    "status": "FAILED",
                    "current_stage": "FAILED",
                    "message": f"Pipeline failed: {str(e)}",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "results": results  # Include partial results
                }
            )

    def _update_task_status(self, task_id: str, stage: str, message: str, results: dict):
        """Helper method to update task status consistently."""
        self.task_manager.set_task_status(
            task_id,
            stage,
            {
                "status": "RUNNING",
                "current_stage": stage,
                "message": message,
                "results": results.copy()  # Create a copy to avoid reference issues
            }
        )

    def _update_task_with_results(self, task_id: str, stage: str, message: str, all_results: dict, stage_result: dict):
        """Helper method to update task status with stage results."""
        # Create a copy of results to avoid reference issues
        results_copy = all_results.copy()
        
        self.task_manager.set_task_status(
            task_id,
            stage,
            {
                "status": "RUNNING",
                "current_stage": stage,
                "message": message,
                "results": results_copy,
                "stage_result": stage_result
            }
        )

    def _format_gherkin_for_execution(self, gherkin_scenarios: list) -> str:
        """Convert Gherkin scenarios to formatted string."""
        import re
        formatted_scenarios = []
        
        for scenario in gherkin_scenarios:
            # Check if the scenario is already a properly formatted string
            if isinstance(scenario, str):
                # If it's already a string, use it as is
                formatted_scenarios.append(scenario)
            else:
                # If it's a dict, format it as proper Gherkin text
                # Start with tags if present
                scenario_lines = []
                
                # Add tags if present
                if 'tags' in scenario and scenario['tags']:
                    tags = ' '.join(scenario['tags']) if isinstance(scenario['tags'], list) else str(scenario['tags'])
                    scenario_lines.append(tags)
                
                # Add scenario title
                scenario_lines.append(f"Scenario: {scenario.get('title', 'Untitled Scenario')}")
                
                # Add Given step with entry point URL check
                if 'given' in scenario and scenario['given']:
                    given_text = scenario['given']
                    # Check if we need to add an entry point URL
                    has_entry_url = False
                    
                    if isinstance(given_text, str):
                        has_entry_url = given_text.startswith("I am on ") or re.search(r'I am on "https?://[^"]+"', given_text)
                        if not has_entry_url:
                            # Add entry point URL as first Given step only if it's not already present
                            # and if we can extract a meaningful URL from the scenario
                            url = self._extract_meaningful_url(scenario)
                            if url:
                                scenario_lines.append(f"  Given I am on \"{url}\"")
                        scenario_lines.append(f"  Given {given_text}")
                    elif isinstance(given_text, list) and given_text:
                        first_given = given_text[0]
                        has_entry_url = first_given.startswith("I am on ") or re.search(r'I am on "https?://[^"]+"', first_given)
                        if not has_entry_url:
                            # Add entry point URL as first Given step only if it's not already present
                            # and if we can extract a meaningful URL from the scenario
                            url = self._extract_meaningful_url(scenario)
                            if url:
                                scenario_lines.append(f"  Given I am on \"{url}\"")
                        
                        for step in given_text:
                            scenario_lines.append(f"  Given {step}")
                else:
                    # If no Given steps exist, add a default one with entry point URL
                    url = self._extract_meaningful_url(scenario)
                    if url:
                        scenario_lines.append(f"  Given I am on \"{url}\"")
                    else:
                        # Only add default URL if we can't extract a meaningful one
                        scenario_lines.append(f"  Given I am on \"https://example.com\"")
                
                # Add When step
                if 'when' in scenario and scenario['when']:
                    scenario_lines.append(f"  When {scenario['when']}")
                
                # Add Then step
                if 'then' in scenario and scenario['then']:
                    scenario_lines.append(f"  Then {scenario['then']}")
                
                # Add And steps if present
                if 'and' in scenario and scenario['and']:
                    and_steps = scenario['and'] if isinstance(scenario['and'], list) else [str(scenario['and'])]
                    for and_step in and_steps:
                        scenario_lines.append(f"  And {and_step}")
                
                # Add But step if present
                if 'but' in scenario and scenario['but']:
                    scenario_lines.append(f"  But {scenario['but']}")
                
                formatted_scenarios.append('\n'.join(scenario_lines))
        
        result = "\n\n".join(formatted_scenarios)
        logger.info(f"Formatted Gherkin scenarios for execution:\n{result}")
        return result
    
    def _extract_meaningful_url(self, scenario: dict) -> Optional[str]:
        """
        Extract a meaningful URL from the scenario instead of using hardcoded defaults.
        
        Args:
            scenario (dict): The scenario dictionary
            
        Returns:
            Optional[str]: A meaningful URL if found, None otherwise
        """
        # Try to extract URL from entry_point_url field
        if 'entry_point_url' in scenario and scenario['entry_point_url']:
            url = scenario['entry_point_url']
            if isinstance(url, str) and (url.startswith('http://') or url.startswith('https://')):
                return url
        
        # Try to extract URL from the given step
        if 'given' in scenario and scenario['given']:
            given_text = scenario['given']
            if isinstance(given_text, str):
                # Look for URL patterns in the given text
                import re
                url_match = re.search(r'https?://[^\s"]+', given_text)
                if url_match:
                    return url_match.group(0)
            elif isinstance(given_text, list) and given_text:
                # Check first item in list for URL
                first_given = given_text[0]
                if isinstance(first_given, str):
                    import re
                    url_match = re.search(r'https?://[^\s"]+', first_given)
                    if url_match:
                        return url_match.group(0)
        
        # Try to extract from feature or title context
        if 'feature' in scenario and scenario['feature']:
            feature = scenario['feature']
            if isinstance(feature, str):
                # Look for common application names that might indicate a URL pattern
                feature_lower = feature.lower()
                if 'ecommerce' in feature_lower or 'shop' in feature_lower:
                    return "https://example-shop.com"
                elif 'bank' in feature_lower or 'finance' in feature_lower:
                    return "https://example-bank.com"
                elif 'social' in feature_lower or 'media' in feature_lower:
                    return "https://example-social.com"
        
        # No meaningful URL found
        return None
    
    def _format_single_scenario(self, scenario: dict) -> str:
        """Format a single scenario dict as Gherkin text."""
        import re
        scenario_lines = []
        
        # Add tags if present
        if 'tags' in scenario and scenario['tags']:
            tags = ' '.join(scenario['tags']) if isinstance(scenario['tags'], list) else str(scenario['tags'])
            scenario_lines.append(tags)
        
        # Add scenario title
        scenario_lines.append(f"Scenario: {scenario.get('title', 'Untitled Scenario')}")
        
        # Add Given step with entry point URL check
        if 'given' in scenario and scenario['given']:
            given_text = scenario['given']
            # Check if we need to add an entry point URL
            has_entry_url = False
            
            if isinstance(given_text, str):
                has_entry_url = given_text.startswith("I am on ") or re.search(r'I am on "https?://[^"]+"', given_text)
                if not has_entry_url:
                    # Add entry point URL as first Given step only if it's not already present
                    # and if we can extract a meaningful URL from the scenario
                    url = self._extract_meaningful_url(scenario)
                    if url:
                        scenario_lines.append(f"  Given I am on \"{url}\"")
                scenario_lines.append(f"  Given {given_text}")
            elif isinstance(given_text, list) and given_text:
                first_given = given_text[0]
                has_entry_url = first_given.startswith("I am on ") or re.search(r'I am on "https?://[^"]+"', first_given)
                if not has_entry_url:
                    # Add entry point URL as first Given step only if it's not already present
                    # and if we can extract a meaningful URL from the scenario
                    url = self._extract_meaningful_url(scenario)
                    if url:
                        scenario_lines.append(f"  Given I am on \"{url}\"")
                
                for step in given_text:
                    scenario_lines.append(f"  Given {step}")
        else:
            # If no Given steps exist, add a default one with entry point URL
            url = self._extract_meaningful_url(scenario)
            if url:
                scenario_lines.append(f"  Given I am on \"{url}\"")
            else:
                # Only add default URL if we can't extract a meaningful one
                scenario_lines.append(f"  Given I am on \"https://example.com\"")
        
        # Add When step
        if 'when' in scenario and scenario['when']:
            scenario_lines.append(f"  When {scenario['when']}")
        
        # Add Then step
        if 'then' in scenario and scenario['then']:
            scenario_lines.append(f"  Then {scenario['then']}")
        
        # Add And steps if present
        if 'and' in scenario and scenario['and']:
            and_steps = scenario['and'] if isinstance(scenario['and'], list) else [str(scenario['and'])]
            for and_step in and_steps:
                scenario_lines.append(f"  And {and_step}")
        
        # Add But step if present
        if 'but' in scenario and scenario['but']:
            scenario_lines.append(f"  But {scenario['but']}")
        
        return '\n'.join(scenario_lines)
    
    def _simplify_history_data(self, history_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simplify history data to avoid recursive references that cause AGNO agent to fail.
        
        Args:
            history_data (Dict[str, Any]): The original history data
            
        Returns:
            Dict[str, Any]: Simplified history data safe for JSON serialization
        """
        if not history_data:
            return {}
        
        # Create a simplified copy with only the essential data needed for code generation
        simplified = {}
        
        # Copy simple fields directly
        simple_fields = [
            'urls', 'action_names', 'element_xpaths', 'errors', 'execution_date',
            'gif_path', 'total_duration', 'number_of_steps', 'final_result',
            'is_done', 'is_successful'
        ]
        
        for field in simple_fields:
            if field in history_data:
                try:
                    # Try to serialize to JSON to check for circular references
                    import json
                    json.dumps(history_data[field])
                    simplified[field] = history_data[field]
                except (TypeError, ValueError):
                    # If serialization fails, convert to string representation
                    simplified[field] = str(history_data[field])
        
        # Handle element interactions data specifically
        if 'element_interactions' in history_data:
            element_interactions = history_data['element_interactions']
            if isinstance(element_interactions, dict):
                simplified['element_interactions'] = {
                    'total_interactions': element_interactions.get('total_interactions', 0),
                    'action_types': element_interactions.get('action_types', []),
                    'unique_elements': element_interactions.get('unique_elements', 0)
                }
                
                # Safely copy automation data if present
                if 'automation_data' in element_interactions and isinstance(element_interactions['automation_data'], dict):
                    automation_data = element_interactions['automation_data']
                    simplified['automation_script_data'] = {
                        'element_library': self._safe_copy_dict(automation_data.get('element_library', {})),
                        'action_sequence': self._safe_copy_list(automation_data.get('action_sequence', [])),
                        'framework_selectors': self._safe_copy_dict(automation_data.get('framework_selectors', {}))
                    }
        
        # Handle framework exports specifically
        if 'framework_exports' in history_data:
            framework_exports = history_data['framework_exports']
            if isinstance(framework_exports, dict):
                simplified['framework_exports'] = {}
                for framework_name, export_data in framework_exports.items():
                    if isinstance(export_data, dict):
                        # Only copy the essential parts to avoid deep nesting
                        simplified['framework_exports'][framework_name] = {
                            'framework': export_data.get('framework', framework_name),
                            'test_steps': self._safe_copy_list(export_data.get('test_steps', [])),
                            'page_objects': self._safe_copy_dict(export_data.get('page_objects', {}))
                        }
        
        # Handle extracted content
        if 'extracted_content' in history_data:
            try:
                import json
                json.dumps(history_data['extracted_content'])
                simplified['extracted_content'] = history_data['extracted_content']
            except (TypeError, ValueError):
                # If serialization fails, create a simplified version
                if isinstance(history_data['extracted_content'], list):
                    simplified['extracted_content'] = [str(item) for item in history_data['extracted_content']]
                else:
                    simplified['extracted_content'] = str(history_data['extracted_content'])
        
        return simplified
    
    def _safe_copy_dict(self, data: Any) -> Dict:
        """
        Safely copy a dictionary, handling potential circular references.
        
        Args:
            data: The data to copy
            
        Returns:
            Dict: A safely copied dictionary
        """
        if not isinstance(data, dict):
            return {}
        
        result = {}
        for key, value in data.items():
            try:
                # Try to serialize the key and value to check for circular references
                import json
                json.dumps(key)
                json.dumps(value)
                result[key] = value
            except (TypeError, ValueError):
                # If serialization fails, convert to string representation
                result[str(key)] = str(value)
        return result
    
    def _safe_copy_list(self, data: Any) -> list:
        """
        Safely copy a list, handling potential circular references.
        
        Args:
            data: The data to copy
            
        Returns:
            list: A safely copied list
        """
        if not isinstance(data, list):
            return []
        
        result = []
        for item in data:
            try:
                # Try to serialize the item to check for circular references
                import json
                json.dumps(item)
                result.append(item)
            except (TypeError, ValueError):
                # If serialization fails, convert to string representation
                result.append(str(item))
        return result

    def get_pipeline_status(self, task_id: str) -> Dict[str, Any]:
        """Get the current status of a pipeline task."""
        return self.task_manager.get_task_status(task_id)

# Create a singleton instance
pipeline_service = PipelineService()