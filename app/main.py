from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class FeedbackRequest(BaseModel):
    translation_id: str
    feedback: str

async def translate_text(text: str, source_language: str, target_language: str) -> str:
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "prompt": f"Translate this text from {source_language} to {target_language}: {text}",
        "max_tokens": 100
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["text"].strip()

@app.post("/translate/")
async def translate(request: TranslationRequest):
    try:
        translated_text = await translate_text(request.text, request.source_language, request.target_language)
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback/")
async def feedback(request: FeedbackRequest):
    # Here you can handle the feedback, e.g., store it in a database
    return {"message": "Feedback received"}
