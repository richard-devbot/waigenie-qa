from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional

_DEFAULT_SECRET_KEY = "dev-secret-change-in-production"

class Settings(BaseSettings):
    # API Configuration
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 8000
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = _DEFAULT_SECRET_KEY
    API_KEY_REQUIRED: bool = False

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        if self.API_KEY_REQUIRED and self.SECRET_KEY == _DEFAULT_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY must be changed from the default value when API_KEY_REQUIRED=True. "
                "Set SECRET_KEY in your .env file."
            )
        return self
    
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

    # Confidential mode - forces all LLM calls through local Ollama
    CONFIDENTIAL_MODE: bool = False
    CONFIDENTIAL_MODEL: str = "llama3.2"

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