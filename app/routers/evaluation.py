from fastapi import APIRouter, HTTPException
from models.translate import EvaluationRequest, EvaluationResponse
import services.azoai as azoai

evaluation_router = APIRouter()


@evaluation_router.post("/evaluate")
async def evaluate(request: EvaluationRequest) -> EvaluationResponse:
    """Handle Evaluation query."""
    try:
        return await azoai.instance.evaluate_translation(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing query: {str(e)}")
