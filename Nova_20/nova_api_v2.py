#!/usr/bin/env python3
"""Nova API v2 — proxy simplu către Ollama nova:v2"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import httpx
import asyncio

OLLAMA_URL = "http://localhost:11434"
MODEL = "nova:v2"

app = FastAPI(title="Nova API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False


@app.get("/health")
async def health():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            models = [m["name"] for m in r.json().get("models", [])]
            nova_ready = MODEL in models
    except Exception:
        nova_ready = False

    return {
        "status": "healthy" if nova_ready else "degraded",
        "nova_model": MODEL,
        "nova_ready": nova_ready,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    payload = {
        "model": MODEL,
        "messages": [m.dict() for m in req.messages],
        "stream": False,
        "options": {"temperature": req.temperature}
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()

    return {
        "response": data["message"]["content"],
        "model": MODEL,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    return {"name": "Nova API v2", "model": MODEL, "endpoints": ["/health", "/chat"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
