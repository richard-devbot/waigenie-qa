from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.code_generation_service import code_generation_service

router = APIRouter()

class CodeGenerationRequest(BaseModel):
    gherkin_steps: str
    history_data: Dict[str, Any]
    framework: str
    provider: str = "Google"
    model: str = "gemini-2.0-flash"

class CodeGenerationResponse(BaseModel):
    code: str
    gherkin_steps: str
    framework: str
    provider: str
    model: str

@router.post("/generate", response_model=CodeGenerationResponse)
async def generate_automation_code(request: CodeGenerationRequest):
    """
    Generate automation code for a specific framework based on Gherkin scenarios and execution history.
    
    Args:
        request (CodeGenerationRequest): The request containing Gherkin steps, history data, and framework
        
    Returns:
        CodeGenerationResponse: Generated automation code
    """
    try:
        result = code_generation_service.generate_automation_code(
            gherkin_steps=request.gherkin_steps,
            history_data=request.history_data,
            framework=request.framework,
            provider=request.provider,
            model=request.model
        )
        
        return CodeGenerationResponse(
            code=result["data"]["code"],
            gherkin_steps=result["metadata"]["gherkin_steps"],
            framework=result["data"].get("framework", request.framework),
            provider=result["metadata"].get("provider", request.provider),
            model=result["metadata"].get("model", request.model),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate automation code: {str(e)}")