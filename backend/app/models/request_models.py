from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class StoryEnhanceRequest(BaseModel):
    raw_story: str
    context: Optional[str] = None
    provider: str = "Google"
    model: str = "gemini-2.0-flash"
    jira_server_url: Optional[str] = None
    jira_username: Optional[str] = None
    jira_token: Optional[str] = None

class ManualTestGenerateRequest(BaseModel):
    enhanced_story: str
    provider: str = "Google"
    model: str = "gemini-2.0-flash"

class GherkinGenerateRequest(BaseModel):
    manual_tests: List[Dict[str, Any]]
    story: str
    provider: str = "Google"
    model: str = "gemini-2.0-flash"

class ExecuteRequest(BaseModel):
    gherkin_scenarios: str
    config: Optional[Dict[str, Any]] = None
    provider: str = "Google"
    model: str = "gemini-2.0-flash"

class CodeGenerateRequest(BaseModel):
    execution_results: Dict[str, Any]
    framework: str
    options: Optional[Dict[str, Any]] = None
    provider: str = "Google"
    model: str = "gemini-2.0-flash"

class FileUploadRequest(BaseModel):
    filename: str
    content: str  # Base64 encoded content