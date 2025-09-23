import os
from pathlib import Path

def load_agent_instructions(agent_name: str) -> str:
    """
    Load agent instructions from markdown files.
    
    Args:
        agent_name (str): Name of the agent (e.g., 'user_story', 'test_case')
        
    Returns:
        str: Content of the instructions file
    """
    # Get the directory where this file is located
    current_dir = Path(__file__).parent
    # Construct the path to the instructions file
    instructions_file = current_dir / f"{agent_name}_agent_instructions.md"
    
    # Check if the file exists
    if not instructions_file.exists():
        raise FileNotFoundError(f"Instructions file not found: {instructions_file}")
    
    # Read and return the content
    with open(instructions_file, 'r', encoding='utf-8') as f:
        return f.read()