#!/usr/bin/env python3
"""Nova AI REST API - FastAPI implementation"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import psycopg2
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import base64
from PIL import Image
import io
from datetime import datetime
import os

# ============================================================================
# Configuration
# ============================================================================

API_KEY = os.getenv("NOVA_API_KEY", "nova_dev_key_2026")  # Change in production!
RATE_LIMIT = 100  # requests per minute

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Nova AI API",
    description="REST API pentru Nova AI - Dual Cortex/Neocortex Architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - Allow all origins for development (including file://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (file://, localhost, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Models & Database (loaded on startup)
# ============================================================================

class AppState:
    def __init__(self):
        self.tokenizer = None
        self.sora_model = None
        self.doica_model = None
        self.embeddings_model = None
        self.pg_conn = None
        
state = AppState()

# ============================================================================
# Request/Response Models
# ============================================================================

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt pentru generare")
    model: Literal["doica", "sora", "merged"] = Field("sora", description="Model de folosit")
    max_tokens: int = Field(150, ge=1, le=500, description="Număr maxim de tokens")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperature (None = greedy)")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p sampling")
    use_patterns: bool = Field(True, description="Use pattern augmentation (RAG)")
    top_k_patterns: int = Field(3, ge=1, le=10, description="Number of patterns to retrieve")

class GenerateResponse(BaseModel):
    response: str
    model_used: str
    tokens_generated: int
    patterns_used: Optional[List[str]] = None
    timestamp: str

class PatternSearchRequest(BaseModel):
    query: str = Field(..., description="Query text pentru căutare semantică")
    top_k: int = Field(5, ge=1, le=20, description="Număr de rezultate")

class PatternResult(BaseModel):
    name: str
    description: str
    category: str
    confidence: float
    similarity: Optional[float] = None

class PatternSearchResponse(BaseModel):
    query: str
    results: List[PatternResult]
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    models_loaded: dict
    database_connected: bool
    timestamp: str

# ============================================================================
# Authentication
# ============================================================================

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Nova API...")
    
    # Load tokenizer
    print("  Loading tokenizer...")
    state.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")
    
    # Load Sora model (main model)
    print("  Loading Sora model...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        "mistralai/Mistral-7B-Instruct-v0.3",
        quantization_config=bnb_config,
        device_map="auto"
    )
    state.sora_model = PeftModel.from_pretrained(base_model, "nova_sora_python/final")
    state.sora_model.eval()
    
    # Load embeddings model
    print("  Loading embeddings model...")
    state.embeddings_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    # Connect to PostgreSQL
    print("  Connecting to Cortex database...")
    state.pg_conn = psycopg2.connect(
        dbname="cortex",
        user="nova",
        password="nova2026",
        host="localhost"
    )
    
    print("✅ Nova API ready!")
    print(f"📡 Listening on http://0.0.0.0:8000")
    print(f"📚 Docs: http://0.0.0.0:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Shutting down Nova API...")
    if state.pg_conn:
        state.pg_conn.close()

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["Status"])
async def root():
    """Root endpoint - API info"""
    return {
        "name": "Nova AI API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "generate": "POST /api/v1/generate",
            "search": "GET /api/v1/patterns/search",
            "related": "GET /api/v1/patterns/related",
            "health": "GET /api/v1/health"
        }
    }

@app.get("/api/v1/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        models_loaded={
            "sora": state.sora_model is not None,
            "embeddings": state.embeddings_model is not None
        },
        database_connected=state.pg_conn is not None and not state.pg_conn.closed,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/v1/generate", response_model=GenerateResponse, tags=["Generation"])
async def generate_text(
    request: GenerateRequest,
    api_key: str = Header(..., alias="X-API-Key")
):
    """Generate text with Nova AI and optional pattern augmentation"""
    verify_api_key(api_key)
    
    if state.sora_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    patterns_used = []
    prompt = request.prompt
    
    # Pattern augmentation (RAG)
    if request.use_patterns and state.embeddings_model and state.pg_conn:
        # Retrieve relevant patterns
        query_embedding = state.embeddings_model.encode([request.prompt])[0]
        
        cursor = state.pg_conn.cursor()
        cursor.execute("""
            SELECT name, description, category, embedding
            FROM patterns
            WHERE embedding IS NOT NULL
            LIMIT 100
        """)
        
        results = []
        for row in cursor.fetchall():
            name, description, category, embedding_json = row
            
            if isinstance(embedding_json, str):
                pattern_embedding = np.array(json.loads(embedding_json), dtype=np.float32)
            else:
                pattern_embedding = np.array(embedding_json, dtype=np.float32)
            
            similarity = float(np.dot(query_embedding, pattern_embedding) / 
                              (np.linalg.norm(query_embedding) * np.linalg.norm(pattern_embedding)))
            
            results.append({
                "name": name,
                "description": description,
                "category": category,
                "similarity": similarity
            })
        
        cursor.close()
        results.sort(key=lambda x: x["similarity"], reverse=True)
        top_patterns = results[:request.top_k_patterns]
        
        if top_patterns:
            # Build compact context with pattern names only
            pattern_names = [p['name'] for p in top_patterns]
            patterns_used = pattern_names
            
            # DISABLE pattern injection - patterns should consolidate during sleep (24h)
            # Pattern retrieval logged for metrics but NOT injected into prompt
            # This prevents distortion like "I'm Color Yellow" or confusing context
            prompt = request.prompt
            
            # Patterns are consolidated offline (nightly cron job) not injected live
            # See: setup_validation_cron.sh for consolidation schedule
    
    # Prepare prompt
    formatted_prompt = f"[INST] {prompt} [/INST]"
    inputs = state.tokenizer(formatted_prompt, return_tensors="pt").to(state.sora_model.device)
    
    # Generation kwargs
    gen_kwargs = {
        "max_new_tokens": request.max_tokens,
        "pad_token_id": state.tokenizer.eos_token_id,
        "do_sample": request.temperature is not None
    }
    
    if request.temperature is not None:
        gen_kwargs["temperature"] = request.temperature
    if request.top_p is not None:
        gen_kwargs["top_p"] = request.top_p
    
    # Generate
    with torch.no_grad():
        outputs = state.sora_model.generate(**inputs, **gen_kwargs)
    
    # Decode
    full_response = state.tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = full_response.split("[/INST]")[-1].strip()
    
    return GenerateResponse(
        response=answer,
        model_used=request.model,
        tokens_generated=len(outputs[0]) - len(inputs.input_ids[0]),
        patterns_used=patterns_used if patterns_used else None,
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/v1/patterns/search", response_model=PatternSearchResponse, tags=["Patterns"])
async def search_patterns(
    query: str,
    top_k: int = 5,
    api_key: str = Header(..., alias="X-API-Key")
):
    """Căutare semantică în Cortex patterns"""
    verify_api_key(api_key)
    
    if state.embeddings_model is None or state.pg_conn is None:
        raise HTTPException(status_code=503, detail="Service not available")
    
    # Generate query embedding
    query_embedding = state.embeddings_model.encode([query])[0]
    
    # Search in database
    cursor = state.pg_conn.cursor()
    cursor.execute("""
        SELECT name, description, category, confidence, embedding
        FROM patterns
        WHERE embedding IS NOT NULL
    """)
    
    results = []
    for row in cursor.fetchall():
        name, description, category, confidence, embedding_json = row
        
        # Parse embedding
        if isinstance(embedding_json, str):
            pattern_embedding = np.array(json.loads(embedding_json), dtype=np.float32)
        else:
            pattern_embedding = np.array(embedding_json, dtype=np.float32)
        
        # Calculate similarity
        similarity = float(np.dot(query_embedding, pattern_embedding) / 
                          (np.linalg.norm(query_embedding) * np.linalg.norm(pattern_embedding)))
        
        results.append(PatternResult(
            name=name,
            description=description,
            category=category,
            confidence=confidence,
            similarity=similarity
        ))
    
    cursor.close()
    
    # Sort by similarity and return top_k
    results.sort(key=lambda x: x.similarity, reverse=True)
    
    return PatternSearchResponse(
        query=query,
        results=results[:top_k],
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/v1/patterns/related", response_model=PatternSearchResponse, tags=["Patterns"])
async def get_related_patterns(
    pattern: str,
    top_k: int = 5,
    api_key: str = Header(..., alias="X-API-Key")
):
    """Găsește pattern-uri similare cu un pattern dat"""
    verify_api_key(api_key)
    
    if state.pg_conn is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    cursor = state.pg_conn.cursor()
    
    # Get pattern embedding
    cursor.execute("""
        SELECT embedding FROM patterns WHERE name = %s
    """, (pattern,))
    
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern}' not found")
    
    embedding_json = result[0]
    if isinstance(embedding_json, str):
        pattern_embedding = np.array(json.loads(embedding_json), dtype=np.float32)
    else:
        pattern_embedding = np.array(embedding_json, dtype=np.float32)
    
    # Find similar patterns
    cursor.execute("""
        SELECT name, description, category, confidence, embedding
        FROM patterns
        WHERE embedding IS NOT NULL AND name != %s
    """, (pattern,))
    
    results = []
    for row in cursor.fetchall():
        name, description, category, confidence, embedding_json = row
        
        if isinstance(embedding_json, str):
            other_embedding = np.array(json.loads(embedding_json), dtype=np.float32)
        else:
            other_embedding = np.array(embedding_json, dtype=np.float32)
        
        similarity = float(np.dot(pattern_embedding, other_embedding) / 
                          (np.linalg.norm(pattern_embedding) * np.linalg.norm(other_embedding)))
        
        results.append(PatternResult(
            name=name,
            description=description,
            category=category,
            confidence=confidence,
            similarity=similarity
        ))
    
    cursor.close()
    
    results.sort(key=lambda x: x.similarity, reverse=True)
    
    return PatternSearchResponse(
        query=f"Related to: {pattern}",
        results=results[:top_k],
        timestamp=datetime.now().isoformat()
    )

# ============================================================================
# Run Server (for development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
