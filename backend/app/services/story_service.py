from typing import Dict, Any, Optional
from app.agents.user_story_agent import create_user_story_enhancement_agent
from app.utils.model_factory import get_llm_instance
from app.config.settings import Settings
from app.models.agent_outputs import EnhancedStory
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re

class StoryService:
    """Service class for handling user story enhancement operations."""
    
    def __init__(self):
        self.settings = Settings()
    
    async def enhance_user_story(self, raw_story: str, provider: str = "Google", model: str = "gemini-2.0-flash", context: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhance a raw user story using AI agents.
        
        Args:
            raw_story: The raw user story to enhance
            provider: The LLM provider to use
            model: The specific model to use
            context: Additional context for the story
            
        Returns:
            Dictionary containing the enhanced story and metadata
        """
        if not raw_story:
            raise ValueError("User story cannot be empty")
        
        try:
            # Get the LLM instance for agno
            agno_llm = get_llm_instance(provider, model, for_agno=True)
            
            if not agno_llm:
                raise Exception("Failed to initialize the model. Please check your API keys.")
            
            # Create the agent
            agent = create_user_story_enhancement_agent(provider, model)
            
            # Add context to the user story
            if context:
                raw_story = f"{raw_story}\n\nAdditional context: {context}"
            
            # Enhance the user story (run in thread pool to avoid blocking)
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                run_response = await loop.run_in_executor(
                    executor, 
                    agent.run, 
                    raw_story
                )
            
            # Extract structured output from the response
            raw = run_response.content if hasattr(run_response, 'content') else run_response
            if isinstance(raw, EnhancedStory):
                story = raw
            elif isinstance(raw, dict):
                story = EnhancedStory(**raw)
            else:
                # String fallback — try to extract JSON or use as text
                story = EnhancedStory(
                    title="Enhanced Story",
                    as_a="user",
                    i_want="to complete the described task",
                    so_that="I can achieve the stated goal",
                    elaboration=str(raw) if raw else "",
                    acceptance_criteria=[],
                )

            return {
                "data": {
                    "enhanced_story": f"As a {story.as_a}, I want {story.i_want}, so that {story.so_that}.\n\n{story.elaboration}",
                    "parsed_story": story.model_dump(),
                    "acceptance_criteria": story.acceptance_criteria,
                },
                "metadata": {
                    "provider": provider,
                    "model": model,
                    "status": "success"
                },
                "raw_response": str(run_response)
            }
            
        except Exception as e:
            raise Exception(f"Error enhancing user story: {str(e)}")
    
    def _parse_enhanced_story(self, enhanced_story: str) -> Dict[str, Any]:
        """
        Process the enhanced story with minimal parsing.
        
        Args:
            enhanced_story (str): The enhanced story content in markdown format
            
        Returns:
            Dict[str, Any]: Story data with the raw markdown content and minimal extracted metadata
        """
        # Keep the raw markdown content
        parsed = {
            "raw_markdown": enhanced_story,
            "title": "",
            "acceptance_criteria": []
        }
        
        # Extract only essential metadata for indexing/searching
        lines = enhanced_story.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                parsed["title"] = line.strip().lstrip('#').strip()
                break
        
        # Extract acceptance criteria (numbered list) - useful for test generation
        criteria_section = re.search(r"##\s*Acceptance Criteria.*?(?=\n##|\Z)", enhanced_story, re.IGNORECASE | re.DOTALL)
        if criteria_section:
            criteria_text = criteria_section.group()
            # Find all numbered items
            criteria_items = re.findall(r"\d+\.\s*(.*?)(?=\n\d+\.|\n##|\Z)", criteria_text, re.DOTALL)
            parsed["acceptance_criteria"] = [item.strip() for item in criteria_items]
        
        return parsed
    
    def validate_input(self, raw_story: str) -> bool:
        """
        Validate the input user story.
        
        Args:
            raw_story: The user story to validate
            
        Returns:
            Boolean indicating if the input is valid
        """
        if not raw_story or not raw_story.strip():
            return False
        return True