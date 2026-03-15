from agno.agent import Agent
from app.utils.model_factory import get_llm_instance
from textwrap import dedent
# Import the utility function to load instructions
from app.prompts.prompt_utils import load_agent_instructions
from app.models.agent_outputs import TestCaseList
from agno.tools.reasoning import ReasoningTools

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
        tools=[
            *jira_tools,
            ReasoningTools(think=True, analyze=True, add_instructions=True),
        ],
        response_model=TestCaseList,
    )
    
    return agent