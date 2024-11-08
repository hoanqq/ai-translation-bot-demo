from fastapi import APIRouter, HTTPException
from typing import Dict
from models.translate import TranslateRequest, TranslateResponse
import services.azoai as azoai

translate_router = APIRouter()


@translate_router.post("/translate")
async def translate(request: TranslateRequest) -> TranslateResponse:
    """Handle Translation query."""
    try:

        return await azoai.instance.translate(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing query: {str(e)}")
