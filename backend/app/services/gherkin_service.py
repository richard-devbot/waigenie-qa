from typing import List, Dict, Any, Optional
from app.agents.gherkin_agent import create_gherkin_agent
import json
import re

class GherkinService:
    """Service for generating Gherkin scenarios from user stories or requirements."""
    
    def __init__(self):
        """Initialize the GherkinService."""
        pass
    
    def generate_gherkin_scenarios(
        self,
        manual_test_cases: List[Dict[str, Any]],
        context: Optional[str] = None,
        provider: str = "Google",
        model: str = "gemini-2.0-flash"
    ) -> Dict[str, Any]:
        """
        Generate Gherkin scenarios from manual test cases.
        
        Args:
            manual_test_cases (List[Dict[str, Any]]): The manual test cases to convert to Gherkin scenarios
            context (str, optional): Additional context for scenario generation
            provider (str): The model provider to use
            model (str): The specific model to use
            
        Returns:
            Dict[str, Any]: Generated Gherkin scenarios and metadata
        """
        # Validate inputs
        if not manual_test_cases:
            raise ValueError("Manual test cases are required")
        
        # Create the agent
        agent = create_gherkin_agent(model_provider=provider, model_name=model)
        
        # Convert manual test cases to a string format for the agent
        test_cases_str = json.dumps(manual_test_cases, indent=2)
        
        # Prepare the input for the agent
        input_text = f"Generate Gherkin scenarios (Given-When-Then) for the following manual test cases:\n\nManual Test Cases:\n{test_cases_str}"
        
        if context:
            input_text += f"\n\nAdditional Context:\n{context}"
        else:
            input_text += "\n\nAdditional Context:\nNo additional context provided."
        
        # Run the agent
        response = agent.run(input_text)
        
        # Extract Gherkin scenarios from the response
        scenarios = self._extract_scenarios_from_response(response)
        
        return {
            "data": {
                "scenarios": scenarios
            },
            "metadata": {
                "test_cases_count": len(manual_test_cases),
                "context": context,
                "provider": provider,
                "model": model,
                "status": "success"
            },
            "raw_response": str(response)
        }
    
    def _extract_scenarios_from_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract Gherkin scenarios from the agent's response.
        
        Args:
            response (str): The raw response from the agent
            
        Returns:
            List[Dict[str, Any]]: Extracted Gherkin scenarios
        """
        # If response is an object with content attribute, get the content
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        # Try to find JSON array in the response
        json_match = re.search(r'\[\s*\{[\s\S]*\}\s*\]', response_text)
        if json_match:
            try:
                scenarios = json.loads(json_match.group())
                # Validate that scenarios is a list of dictionaries
                if isinstance(scenarios, list) and all(isinstance(s, dict) for s in scenarios):
                    # Ensure each scenario has an entry point URL in the first Given step
                    for scenario in scenarios:
                        if "given" in scenario and isinstance(scenario["given"], str) and scenario["given"]:
                            # Check if the first Given step already has an entry point URL
                            if not re.search(r'I am on "https?://[^"]+"', scenario["given"]):
                                # If no entry point URL is found, extract it from entry_point_url field or use a default
                                url = scenario.get("entry_point_url", "https://example.com")
                                # Replace the Given step with one that includes the entry point URL
                                scenario["given"] = f'I am on "{url}"\n{scenario["given"]}'
                    return self._normalize_scenarios(scenarios)
            except json.JSONDecodeError:
                pass
        
        # If JSON parsing fails, try to extract Gherkin content from the response
        # Look for Feature: or Scenario: patterns in the response
        gherkin_match = re.search(r'(Feature:|Scenario:)[\s\S]*', response_text)
        
        # If we found Gherkin content, try to parse it into structured scenarios
        if gherkin_match:
            gherkin_content = gherkin_match.group(0)
            # Try to parse the Gherkin content into structured format
            parsed_scenarios = self._parse_gherkin_text_to_structured(gherkin_content)
            if parsed_scenarios:
                return self._normalize_scenarios(parsed_scenarios)
        
        # Create a fallback scenario with better handling
        scenario = {
            "title": "Generated Gherkin Scenario",
            "tags": [],
            "given": "I am on \"https://example.com\"",
            "when": "",
            "then": gherkin_match.group(0) if gherkin_match else "No valid Gherkin content found",
            "and": [],
            "but": "",
            "entry_point_url": "https://example.com"
        }
        
        # Try to extract a real URL from the response if present
        url_match = re.search(r'https?://[^\s"]+', response_text)
        if url_match:
            url = url_match.group(0)
            scenario["given"] = f'I am on "{url}"'
            scenario["entry_point_url"] = url
            
        return [scenario]
    
    def _parse_gherkin_text_to_structured(self, gherkin_text: str) -> List[Dict[str, Any]]:
        """
        Parse Gherkin text content into structured scenario dictionaries.
        
        Args:
            gherkin_text (str): The Gherkin text content
            
        Returns:
            List[Dict[str, Any]]: Parsed structured scenarios
        """
        scenarios = []
        lines = gherkin_text.strip().split('\n')
        
        current_scenario = None
        in_scenario = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Scenario:'):
                # Save previous scenario if exists
                if current_scenario:
                    scenarios.append(current_scenario)
                
                # Start new scenario
                title = line.replace('Scenario:', '').strip()
                current_scenario = {
                    "title": title,
                    "tags": [],
                    "given": "",
                    "when": "",
                    "then": "",
                    "and": [],
                    "but": "",
                    "entry_point_url": "https://example.com"
                }
                in_scenario = True
                
            elif line.startswith('@') and not in_scenario:
                # Handle tags
                if current_scenario and current_scenario["tags"]:
                    current_scenario["tags"].append(line)
                elif current_scenario:
                    current_scenario["tags"] = [line]
                    
            elif line.startswith('Given'):
                if current_scenario:
                    given_text = line.replace('Given', '').strip()
                    current_scenario["given"] = given_text
                    # Extract URL if present
                    url_match = re.search(r'I am on "([^"]+)"', given_text)
                    if url_match:
                        current_scenario["entry_point_url"] = url_match.group(1)
                        
            elif line.startswith('When'):
                if current_scenario:
                    current_scenario["when"] = line.replace('When', '').strip()
                    
            elif line.startswith('Then'):
                if current_scenario:
                    current_scenario["then"] = line.replace('Then', '').strip()
                    
            elif line.startswith('And'):
                if current_scenario:
                    and_text = line.replace('And', '').strip()
                    current_scenario["and"].append(and_text)
                    
            elif line.startswith('But'):
                if current_scenario:
                    current_scenario["but"] = line.replace('But', '').strip()
        
        # Add the last scenario
        if current_scenario:
            scenarios.append(current_scenario)
            
        return scenarios if scenarios else []
    
    def _normalize_scenarios(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize scenarios to ensure consistent structure for frontend display.
        
        Args:
            scenarios (List[Dict[str, Any]]): Raw scenarios
            
        Returns:
            List[Dict[str, Any]]: Normalized scenarios
        """
        normalized = []
        
        for i, scenario in enumerate(scenarios):
            # Ensure all required fields are present with proper defaults
            normalized_scenario = {
                "title": str(scenario.get("title", f"Scenario {i+1}")),
                "tags": scenario.get("tags", []),
                "feature": str(scenario.get("feature", "User Story Automation")),
                "given": scenario.get("given", ""),
                "when": scenario.get("when", ""),
                "then": scenario.get("then", ""),
                "and": scenario.get("and", []),
                "but": scenario.get("but", ""),
                "background": scenario.get("background", ""),
                "examples": scenario.get("examples", []),
                "entry_point_url": scenario.get("entry_point_url", "")
            }
            
            # Ensure tags is a list of strings
            if not isinstance(normalized_scenario["tags"], list):
                normalized_scenario["tags"] = [str(normalized_scenario["tags"])] if normalized_scenario["tags"] else []
            else:
                normalized_scenario["tags"] = [str(tag) for tag in normalized_scenario["tags"]]
                
            # Ensure and is a list of strings
            if not isinstance(normalized_scenario["and"], list):
                normalized_scenario["and"] = [str(normalized_scenario["and"])] if normalized_scenario["and"] else []
            else:
                normalized_scenario["and"] = [str(step) for step in normalized_scenario["and"]]
                
            # Ensure examples is a list
            if not isinstance(normalized_scenario["examples"], list):
                normalized_scenario["examples"] = [str(normalized_scenario["examples"])] if normalized_scenario["examples"] else []
            
            # Extract entry point URL from given step if not explicitly provided
            if not normalized_scenario["entry_point_url"] and normalized_scenario["given"]:
                given_text = normalized_scenario["given"]
                if isinstance(given_text, str):
                    url_match = re.search(r'I am on "([^"]+)"', given_text)
                    if url_match:
                        normalized_scenario["entry_point_url"] = url_match.group(1)
                elif isinstance(given_text, list) and given_text:
                    # Check first item in list
                    first_given = given_text[0]
                    if isinstance(first_given, str):
                        url_match = re.search(r'I am on "([^"]+)"', first_given)
                        if url_match:
                            normalized_scenario["entry_point_url"] = url_match.group(1)
            
            normalized.append(normalized_scenario)
        
        return normalized

# Global instance of the service
gherkin_service = GherkinService()
