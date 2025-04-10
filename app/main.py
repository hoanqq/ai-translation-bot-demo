from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

# Lấy OpenAI API key từ biến môi trường
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Cho phép tất cả nguồn gọi (để tương thích với frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationRequest(BaseModel):
    source_text: str
    source_language: str
    target_language: str

@app.post("/translate")
async def translate(req: TranslationRequest):
    prompt = f"Hãy dịch đoạn văn sau từ {req.source_language} sang {req.target_language}:\n\n{req.source_text}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # hoặc "gpt-4" nếu bạn có quyền
        messages=[
            {"role": "system", "content": "Bạn là một dịch giả chuyên nghiệp."},
            {"role": "user", "content": prompt}
        ]
    )
    translated = response["choices"][0]["message"]["content"].strip()
    return {"target_text": translated}
