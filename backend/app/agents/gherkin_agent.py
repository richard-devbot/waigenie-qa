from agno.agent import Agent
from app.utils.model_factory import get_llm_instance
from textwrap import dedent
# Import the utility function to load instructions
from app.prompts.prompt_utils import load_agent_instructions

def create_gherkin_agent(model_provider: str = "Google", model_name: str = "gemini-2.0-flash"):
    """
    Creates a Gherkin Scenario Generation Agent.
    
    Args:
        model_provider (str): The model provider to use (e.g., "Google", "OpenAI")
        model_name (str): The specific model to use
        
    Returns:
        Agent: Configured Gherkin Scenario Generation Agent
    """
    # Create the LLM model
    model = get_llm_instance(model_provider, model_name, for_agno=True)
    
    # Load instructions from the markdown file
    instructions = load_agent_instructions("gherkin")
    
    # Create the agent
    agent = Agent(
        model=model,
        markdown=True,
        description=dedent("""
        You are a highly skilled Quality Assurance (QA) expert specializing in
        converting detailed manual test cases into comprehensive, well-structured,
        and automation-ready Gherkin scenarios. You excel at creating Gherkin feature
        files that serve as living documentation, facilitate clear communication across
        teams, and provide an optimal foundation for automated test script generation.
        You understand that effective Gherkin scenarios should be both human-readable
        and automation-friendly, with appropriate abstraction levels and clear step
        definitions that translate well into browser automation commands.
        """),
        instructions=instructions,
        # tools=[
        #     ReasoningTools(
        #         think=True,
        #         analyze=True,
        #         add_instructions=True,
        #         add_few_shot=True,
        #     ),
        # ],
        expected_output=dedent("""\
        [
          {
            "title": "Scenario Title",
            "tags": ["@tag1", "@tag2"],
            "feature": "User Story Automation",
            "given": "Pre-conditions or initial context with specific details - MUST include an entry point URL in the first step using format: 'I am on \"[full URL]\"'",
            "when": "The action or event with specific element names if applicable",
            "then": "The expected outcome with specific verification points",
            "and": ["Additional step 1 with specific details", "Additional step 2 with specific details"],
            "but": "Exception or alternative outcome with specific details",
            "background": "Shared preconditions for multiple scenarios (if applicable)",
            "examples": [
              {
                "example_1": "value_1",
                "example_2": "value_2"
              }
            ],
            "entry_point_url": "The full URL where the test scenario begins"
          }
        ]
        Return ONLY the JSON array of Gherkin scenarios, adhering to the specified structure. Ensure each field is populated with meaningful, detailed content that follows Gherkin best practices. The 'given' field MUST include an entry point URL in the first step. DO NOT wrap the JSON in markdown code blocks or any other formatting. Return only the raw JSON array.
        """),
    )
    
    return agent