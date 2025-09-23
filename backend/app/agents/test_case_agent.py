from agno.agent import Agent
from app.utils.model_factory import get_llm_instance
from textwrap import dedent
# Import the utility function to load instructions
from app.prompts.prompt_utils import load_agent_instructions

def create_test_case_agent(model_provider: str = "Google", model_name: str = "gemini-2.0-flash"):
    """
    Creates a Manual Test Case Generation Agent.
    
    Args:
        model_provider (str): The model provider to use (e.g., "Google", "OpenAI")
        model_name (str): The specific model to use
        
    Returns:
        Agent: Configured Manual Test Case Generation Agent
    """
    # Create the LLM model
    model = get_llm_instance(model_provider, model_name, for_agno=True)
    
    # Define Jira tools if needed
    def _create_jira_tools():
        """Create Jira tools if environment variables are set."""
        try:
            import os
            # Check if Jira environment variables are set
            jira_server = os.getenv("JIRA_SERVER_URL")
            jira_username = os.getenv("JIRA_USERNAME")
            jira_token = os.getenv("JIRA_TOKEN")
            
            if jira_server and jira_username and jira_token:
                from agno.tools.jira import JiraTools
                return [JiraTools()]
            else:
                return []
        except Exception:
            # If there's any error, return empty tools list
            return []
    
    jira_tools = _create_jira_tools()
    
    # Load instructions from the markdown file
    instructions = load_agent_instructions("test_case")
    
    # Create the agent
    agent = Agent(
        model=model,
        markdown=True,
        description=dedent("""
        You are a highly skilled Quality Assurance (QA) expert specializing in
        converting user stories and their acceptance criteria into comprehensive,
        detailed, and industry-standard manual test cases optimized for automation.
        You excel at identifying and articulating test scenarios that serve as a strong
        foundation for automated test script development, including positive, negative,
        edge, and boundary cases. You understand the importance of creating test cases
        that are both manually executable and automation-friendly, with clear element
        identification strategies and data-driven testing approaches.
        """),
        instructions=instructions,
        # tools=[ # Keep tools commented out unless explicitly needed for this agent's function
        #     ReasoningTools(
        #         think=True,
        #         analyze=True,
        #         add_instructions=True,
        #         add_few_shot=True,
        #     ),
        # ],
        expected_output=dedent("""
        [
          {
            "id": "TC_US_001_01",
            "title": "Test Case Title",
            "description": "Detailed description of what this test case verifies",
            "pre_conditions": "Pre-conditions for the test",
            "steps": [
              "Step 1: Action description with specific element names if applicable",
              "Step 2: Action description with specific element names if applicable"
            ],
            "expected_results": [
              "Expected result for step 1 with specific verification points",
              "Expected result for step 2 with specific verification points"
            ],
            "test_data": "Any specific data needed with format examples if applicable",
            "priority": "High/Medium/Low",
            "test_type": "Functional/Non-functional/UI/API/Integration/etc.",
            "status": "Not Executed",
            "post_conditions": "Any cleanup or system state expected after execution",
            "environment": "Environment requirements for test execution",
            "automation_status": "Not Automated/Automated/In Progress"
          }
        ]
        Return ONLY the JSON array of test cases, adhering to the specified structure. Ensure each field is populated with meaningful, detailed content. DO NOT wrap the JSON in markdown code blocks or any other formatting. Return only the raw JSON array.
        """),
        tools=jira_tools,
    )
    
    return agent