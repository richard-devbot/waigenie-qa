from typing import List, Dict, Any, Optional
from app.agents.test_case_agent import create_test_case_agent
from app.models.agent_outputs import TestCaseList, TestCase
import json
import re

class TestCaseService:
    """Service for generating manual test cases from user stories or requirements."""
    
    def __init__(self):
        """Initialize the TestCaseService."""
        pass
    
    def generate_test_cases(
        self,
        user_story: str,
        context: Optional[str] = None,
        provider: str = "Google",
        model: str = "gemini-2.0-flash"
    ) -> Dict[str, Any]:
        """
        Generate manual test cases from a user story or requirement.
        
        Args:
            user_story (str): The user story or requirement to generate test cases for
            context (str, optional): Additional context for test case generation
            provider (str): The model provider to use
            model (str): The specific model to use
            
        Returns:
            Dict[str, Any]: Generated test cases and metadata
        """
        # Validate inputs
        if not user_story:
            raise ValueError("User story is required")
        
        # Create the agent
        agent = create_test_case_agent(model_provider=provider, model_name=model)
        
        # Prepare the input for the agent
        input_text = f"Generate comprehensive manual test cases for the following user story or requirement:\n\nUser Story/Requirement:\n{user_story}"
        
        if context:
            input_text += f"\n\nAdditional Context:\n{context}"
        else:
            input_text += "\n\nAdditional Context:\nNo additional context provided."
        
        # Run the agent
        response = agent.run(input_text)

        # Extract structured output from the response
        raw = response.content if hasattr(response, 'content') else response
        if isinstance(raw, TestCaseList):
            result = raw
        elif isinstance(raw, dict):
            result = TestCaseList(**raw)
        else:
            # Parse JSON string fallback
            try:
                data = json.loads(str(raw))
                if isinstance(data, list):
                    result = TestCaseList(test_cases=[TestCase(**tc) if isinstance(tc, dict) else tc for tc in data])
                else:
                    result = TestCaseList(test_cases=[])
            except Exception:
                result = TestCaseList(test_cases=[])

        return {
            "data": {
                "test_cases": [tc.model_dump() for tc in result.test_cases],
                "test_count": result.total_count,
            },
            "metadata": {
                "user_story": user_story,
                "context": context,
                "provider": provider,
                "model": model,
                "status": "success"
            },
            "raw_response": str(response)
        }
    
    def _extract_test_cases_from_response(self, response) -> List[Dict[str, Any]]:
        """
        Extract test cases from the agent's response.
        
        Args:
            response: The raw response from the agent
            
        Returns:
            List[Dict[str, Any]]: Extracted test cases
        """
        # If response is an object with content attribute, get the content
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        # Try to find JSON array in the response
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            try:
                test_cases = json.loads(json_match.group())
                # Validate that test_cases is a list of dictionaries
                if isinstance(test_cases, list) and all(isinstance(tc, dict) for tc in test_cases):
                    return self._normalize_test_cases(test_cases)
            except json.JSONDecodeError:
                pass
        
        # If JSON parsing fails, return the response as a single test case
        return [{
            "id": "TC_001",
            "title": "Generated Test Cases",
            "description": response_text,
            "pre_conditions": "",
            "steps": [response_text],
            "expected_results": [""],
            "test_data": "",
            "priority": "Medium",
            "test_type": "Functional",
            "status": "Not Executed",
            "post_conditions": ""
        }]
    
    def _normalize_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize test cases to ensure consistent structure for frontend display.
        
        Args:
            test_cases (List[Dict[str, Any]]): Raw test cases
            
        Returns:
            List[Dict[str, Any]]: Normalized test cases
        """
        normalized = []
        
        for i, tc in enumerate(test_cases):
            # Ensure all required fields are present with proper defaults
            normalized_tc = {
                "id": str(tc.get("id", f"TC_{i+1:03d}")),
                "title": str(tc.get("title", f"Test Case {i+1}")),
                "description": str(tc.get("description", "")),
                "pre_conditions": str(tc.get("pre_conditions", tc.get("preconditions", tc.get("preConditions", "")))),
                "steps": tc.get("steps", []),
                "expected_results": tc.get("expected_results", tc.get("expectedResults", [])),
                "test_data": str(tc.get("test_data", "")),
                "priority": str(tc.get("priority", "Medium")),
                "test_type": str(tc.get("test_type", tc.get("testType", "Functional"))),
                "status": str(tc.get("status", "Not Executed")),
                "post_conditions": str(tc.get("post_conditions", tc.get("postConditions", ""))),
                "environment": str(tc.get("environment", "")),
                "automation_status": str(tc.get("automation_status", tc.get("automationStatus", "Not Automated")))
            }
            
            # Ensure steps and expected_results are lists of strings
            if not isinstance(normalized_tc["steps"], list):
                normalized_tc["steps"] = [str(normalized_tc["steps"])] if normalized_tc["steps"] else []
            else:
                normalized_tc["steps"] = [str(step) for step in normalized_tc["steps"]]
                
            if not isinstance(normalized_tc["expected_results"], list):
                normalized_tc["expected_results"] = [str(normalized_tc["expected_results"])] if normalized_tc["expected_results"] else []
            else:
                normalized_tc["expected_results"] = [str(result) for result in normalized_tc["expected_results"]]
            
            normalized.append(normalized_tc)
        
        return normalized

# Global instance of the service
test_case_service = TestCaseService()