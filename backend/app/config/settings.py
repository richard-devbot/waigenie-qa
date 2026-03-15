from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 8000
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "dev-secret-change-in-production"
    API_KEY_REQUIRED: bool = False
    
    # LLM API Keys
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Jira Configuration
    JIRA_SERVER_URL: Optional[str] = None
    JIRA_USERNAME: Optional[str] = None
    JIRA_TOKEN: Optional[str] = None
    
    # Intelligence / Memory
    MEMORY_DB_FILE: str = "./waigenie_memory.db"
    LANCEDB_URI: str = "./waigenie_knowledge"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Database
    DATABASE_URL: str = "sqlite:///./sdet_genie.db"
    
    # Browser Execution Configuration
    BROWSER_HEADLESS: bool = False
    BROWSER_WINDOW_WIDTH: int = 1280
    BROWSER_WINDOW_HEIGHT: int = 720
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()