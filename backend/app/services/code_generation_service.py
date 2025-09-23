from typing import Dict, Any, Optional, List
from app.agents.code_generation_agent import create_code_generation_agent
import json
import re

class CodeGenerationService:
    """Service for generating test automation code from Gherkin scenarios and execution history."""
    
    def __init__(self):
        """Initialize the CodeGenerationService."""
        pass
    
    def generate_automation_code(
        self,
        gherkin_steps: str,
        history_data: Dict[str, Any],
        framework: str,
        provider: str = "Google",
        model: str = "gemini-2.0-flash"
    ) -> Dict[str, Any]:
        """
        Generate automation code for a specific framework based on Gherkin scenarios and execution history.
        
        Args:
            gherkin_steps (str): The Gherkin scenarios to generate code for
            history_data (Dict[str, Any]): The execution history data with element tracking
            framework (str): The target framework for code generation
            provider (str): The model provider to use
            model (str): The specific model to use
            
        Returns:
            Dict[str, Any]: Generated automation code and metadata
        """
        # Validate inputs
        if not gherkin_steps:
            raise ValueError("Gherkin steps are required")
        
        if not history_data:
            raise ValueError("Execution history data is required")
            
        if not framework:
            raise ValueError("Framework is required")
        
        # Create the agent
        agent = create_code_generation_agent(model_provider=provider, model_name=model)
        
        # Prepare the input for the agent
        # Extract feature name from Gherkin (optional, for context)
        feature_match = None
        if gherkin_steps:
            feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
        feature_name = feature_match.group(1).strip() if feature_match else "Automated Test"

        # Get URLs visited
        urls = history_data.get('urls', [])
        # Extract URL from the first visited URL if available, otherwise use a more meaningful default
        base_url = self._extract_meaningful_url_from_history(history_data, urls)

        # Use enhanced element tracking data if available
        if 'element_interactions' in history_data:
            # Enhanced tracking data
            element_data = history_data['element_interactions']
            automation_data = history_data.get('automation_script_data', {})
            
            # Get framework-specific exports
            framework_export = {}
            if 'framework_exports' in history_data:
                framework_key = framework.lower().replace(' ', '_').replace('+', '_').replace('/', '_').replace('(', '').replace(')', '')
                if framework_key in history_data['framework_exports']:
                    framework_export = history_data['framework_exports'][framework_key]
                elif 'selenium' in framework_key and 'selenium' in history_data['framework_exports']:
                    framework_export = history_data['framework_exports']['selenium']
                elif 'playwright' in framework_key and 'playwright' in history_data['framework_exports']:
                    framework_export = history_data['framework_exports']['playwright']
                elif 'cypress' in framework_key and 'cypress' in history_data['framework_exports']:
                    framework_export = history_data['framework_exports']['cypress']
            
            input_text = f"""
            Generate comprehensive {framework} code using enhanced element tracking data:

            Gherkin Steps:
            ```gherkin
            {gherkin_steps}
            ```

            Enhanced Element Tracking Data:
            - Base URL: {base_url}
            - Total Elements Interacted: {element_data.get('unique_elements', 0)}
            - Action Types: {element_data.get('action_types', [])}
            - Element Library: {json.dumps(automation_data.get('element_library', {}), indent=2)}
            - Action Sequence: {json.dumps(automation_data.get('action_sequence', []), indent=2)}
            - {framework} Framework Export: {json.dumps(framework_export, indent=2)}
            
            IMPORTANT: Use the provided element selectors and interaction details to generate robust, production-ready test code.
            Prioritize data-testid, ID, and name attributes over XPath when available.
            """
        else:
            # Fallback to legacy extraction for backward compatibility
            from app.utils.element_extractor import extract_selectors_from_history, analyze_actions
            selectors = extract_selectors_from_history(history_data)
            actions = analyze_actions(history_data)
            
            input_text = f"""
            Generate {framework} code based on the following:

            Gherkin Steps:
            ```gherkin
            {gherkin_steps}
            ```

            Agent Execution Details:
            - Base URL: {base_url}
            - Element Selectors: {json.dumps(selectors, indent=2)}
            - Actions Performed: {json.dumps(actions, indent=2)}
            - Extracted Content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
            """

        # Run the agent
        response = agent.run(input_text)
        
        # Extract code from the response
        code = self._extract_code_from_response(response)
        
        return {
            "data": {
                "code": code,
                "framework": framework
            },
            "metadata": {
                "gherkin_steps": gherkin_steps,
                "provider": provider,
                "model": model,
                "status": "success"
            },
            "raw_response": str(response)
        }
    
    def _extract_meaningful_url_from_history(self, history_data: Dict[str, Any], urls: List[str]) -> str:
        """
        Extract a meaningful URL from history data.
        
        Args:
            history_data (Dict[str, Any]): The history data
            urls (List[str]): List of URLs from history
            
        Returns:
            str: A meaningful base URL
        """
        # First try to get URL from the history data
        if urls:
            base_url = urls[0]
            # Validate it's a proper URL
            if base_url.startswith(('http://', 'https://')):
                return base_url
        
        # Try to extract from element interactions or other data
        if 'element_interactions' in history_data:
            element_data = history_data['element_interactions']
            if 'automation_data' in element_data:
                automation_data = element_data['automation_data']
                if 'element_library' in automation_data:
                    # Look for URLs in element attributes
                    for element in automation_data['element_library'].values():
                        if 'attributes' in element:
                            attrs = element['attributes']
                            # Check for href attributes that might contain URLs
                            if 'href' in attrs and attrs['href'].startswith(('http://', 'https://')):
                                return attrs['href']
        
        # Default fallback
        return "https://example.com"
    
    def _extract_code_from_response(self, response: str) -> str:
        """
        Extract code from the agent's response.
        
        Args:
            response (str): The raw response from the agent
            
        Returns:
            str: Extracted code content
        """
        # If response is an object with content attribute, get the content
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        # Look for content between triple backticks
        code_block_pattern = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)
        match = code_block_pattern.search(response_text)

        if match:
            return match.group(1).strip()
        return response_text.strip()

# Create a singleton instance
code_generation_service = CodeGenerationService()
