import logging
import sys
from fastapi import APIRouter, HTTPException
from typing import Dict
from models.translate import TranslateRequest, TranslateResponse, FeedbackRequest
import services.azoai as azoai

feedback_router = APIRouter()

@feedback_router.post("/feedback")
async def feedback(request: FeedbackRequest):
    """Handle feedback."""
    try:
        print(f"Feedback received: {request.feedback}")
        return {"message": "Feedback received"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing query: {str(e)}")
