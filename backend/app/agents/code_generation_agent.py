from agno.agent import Agent
from app.utils.model_factory import get_llm_instance
from textwrap import dedent
# Import the utility function to load instructions
from app.prompts.prompt_utils import load_agent_instructions
from app.models.agent_outputs import GeneratedCode

def create_code_generation_agent(model_provider: str = "Google", model_name: str = "gemini-2.0-flash"):
    """
    Creates a Code Generation Agent for generating test automation code from Gherkin scenarios.
    
    Args:
        model_provider (str): The model provider to use (e.g., "Google", "OpenAI")
        model_name (str): The specific model to use
        
    Returns:
        Agent: Configured Code Generation Agent
    """
    # Create the LLM model
    model = get_llm_instance(model_provider, model_name, for_agno=True)
    
    # Load instructions from the markdown file
    instructions = load_agent_instructions("code_generation")
    
    # Create the agent
    agent = Agent(
        model=model,
        markdown=True,
        description=dedent("""
        You are an expert test automation engineer specializing in generating production-ready,
        robust automation code from Gherkin scenarios and comprehensive element tracking data.
        You excel at creating maintainable test scripts that follow industry best practices for
        various frameworks (Selenium, Playwright, Cypress, Robot Framework, Java/Cucumber).
        
        You understand the importance of using reliable selectors (data-testid, ID, name attributes)
        over brittle XPath expressions, implementing proper wait conditions, error handling,
        and following framework-specific patterns like Page Object Model.
        """),
        instructions=instructions,
        response_model=GeneratedCode,
    )
    
    return agent