from agno.agent import Agent
from textwrap import dedent
from typing import List, Optional
from app.utils.model_factory import get_llm_instance
# Import the utility function to load instructions
from app.prompts.prompt_utils import load_agent_instructions

def create_user_story_enhancement_agent(model_provider: str = "Google", model_name: str = "gemini-2.0-flash") -> Agent:
    """Create the User Story Enhancement Agent with proper configuration."""
    
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
    instructions = load_agent_instructions("user_story")
    
    agent = Agent(
        model=model,
        markdown=True,
        description=dedent("""
        You are an expert Business Analyst specializing in transforming rough, incomplete
        user stories into detailed, valuable JIRA-style user stories with a focus on
        testability and automation-readiness. You understand that user stories should
        focus on the WHO, WHAT, and WHY to bring context and user perspective into
        development, while ensuring they provide clear guidance for QA automation
        and testing strategies.
        
        You also have access to Jira tools that allow you to fetch issue details when provided with a Jira ticket number.
        When a user provides a Jira ticket number (e.g., "PROJECT-123"), use the get_issue tool to fetch the details
        and then enhance the user story based on that information.
        """),
        instructions=instructions,
        tools=jira_tools,  # Initialize with JiraTools if environment variables are set, otherwise empty list
        expected_output=dedent("""\
        # User Story: [Brief Title]

        ## Story Definition
        As a [specific user type/role],
        I want [clear intention or capability],
        So that [explicit value or benefit received].

        ## Story Elaboration
        [Additional context, clarification, and business value explanation with specific details]

        ## Acceptance Criteria
        1. [Clear, testable criterion 1 with specific details]
        2. [Clear, testable criterion 2 with specific details]
        3. [Clear, testable criterion 3 with specific details]
        4. [Additional criteria as needed with specific details]

        ## Implementation Notes
        - [Technical consideration 1 with specific details]
        - [Technical consideration 2 with specific details]
        - [Additional notes as needed with specific details]

        ## Testability Considerations
        - [How to test this feature effectively]
        - [Key elements to verify]
        - [Potential edge cases to consider]

        ## Attachments/References
        - [Any mockups, designs, or related documents with specific links if available]
        - [Links to relevant specifications with specific URLs if available]

        ## Related Stories/Epics
        - [Parent epic or related stories with specific IDs if available]
        """)
        # Note: Return the enhanced user story in the exact format shown above without any additional text or formatting.,
    )
    
    return agent