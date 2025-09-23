from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class StoryEnhanceResponse(BaseModel):
    enhanced_story: str
    raw_markdown: Optional[str] = None  # Added to provide raw markdown content for direct rendering
    metadata: Optional[Dict[str, Any]] = None

class ManualTestGenerateResponse(BaseModel):
    manual_tests: List[Dict[str, Any]]
    test_count: int

class GherkinGenerateResponse(BaseModel):
    gherkin_scenarios: str
    feature_files: List[str]

class ExecuteStartResponse(BaseModel):
    task_id: str
    status: str

class ExecuteStatusResponse(BaseModel):
    status: str
    progress: int
    current_step: Optional[str] = None

class ExecuteResultsResponse(BaseModel):
    results: Dict[str, Any]
    artifacts: List[str]
    summary: Dict[str, Any]

class CodeGenerateResponse(BaseModel):
    generated_code: str
    file_structure: Dict[str, Any]

class FileUploadResponse(BaseModel):
    file_id: str
    message: str

class FileDownloadResponse(BaseModel):
    filename: str
    content: str  # Base64 encoded content
    content_type: str

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    timestamp: str