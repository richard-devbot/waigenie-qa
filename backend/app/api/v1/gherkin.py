from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.gherkin_service import gherkin_service

router = APIRouter()

class GherkinRequest(BaseModel):
    manual_test_cases: List[Dict[str, Any]]
    context: Optional[str] = None
    provider: str = "Google"
    model: str = "gemini-2.0-flash"

class GherkinResponse(BaseModel):
    scenarios: List[Dict[str, Any]]
    manual_test_cases: List[Dict[str, Any]]
    context: Optional[str] = None

@router.post("/generate", response_model=GherkinResponse)
async def generate_gherkin_scenarios(request: GherkinRequest):
    """
    Generate Gherkin scenarios from manual test cases.
    
    Args:
        request (GherkinRequest): The request containing manual test cases and context
        
    Returns:
        GherkinResponse: Generated Gherkin scenarios
    """
    try:
        result = gherkin_service.generate_gherkin_scenarios(
            manual_test_cases=request.manual_test_cases,
            context=request.context,
            provider=request.provider,
            model=request.model
        )
        
        # Extract scenarios from the result
        scenarios = result.get("data", {}).get("scenarios", [])
        
        return GherkinResponse(
            scenarios=scenarios,
            manual_test_cases=request.manual_test_cases,
            context=request.context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Gherkin scenarios: {str(e)}")