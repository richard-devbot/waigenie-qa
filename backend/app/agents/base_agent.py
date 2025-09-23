from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    @abstractmethod
    def run(self, prompt: str) -> Any:
        """Run the agent with the given prompt.
        
        Args:
            prompt (str): The prompt to run the agent with
            
        Returns:
            Any: The result of running the agent
        """
        pass