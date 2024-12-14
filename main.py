from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI()

# Configurar CORS para producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.figma.com"],  # Solo permitir Figma en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Content(BaseModel):
    parts: List[Dict[str, Any]]

class GenerateRequest(BaseModel):
    contents: List[Content]

@app.get("/")
async def read_root():
    return {"status": "ok", "message": "Gemini Proxy Server is running"}

@app.post("/api/generate")
async def generate_content(request: GenerateRequest):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                params={"key": api_key},
                json=request.dict(),
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Gemini API error: {response.text}"
                )
                
            return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
