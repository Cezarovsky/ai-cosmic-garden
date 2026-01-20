# Nova AI REST API

API REST pentru Nova AI cu arhitectură duală Cortex/Neocortex.

## 🚀 Start Server

```bash
cd /home/cezar/ai-cosmic-garden/Nova_20
./start_api.sh
```

Server pornește pe: **http://localhost:8000**

## 📚 Documentație Interactivă

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 Autentificare

Toate endpoint-urile (except root `/` și `/api/v1/health`) necesită API key în header:

```bash
X-API-Key: nova_dev_key_2026
```

**Important**: Schimbă API key-ul în producție prin variabilă de mediu `NOVA_API_KEY`.

## 📡 Endpoints

### 1. **GET /** - Info API
```bash
curl http://localhost:8000/
```

Response:
```json
{
  "name": "Nova AI API",
  "version": "1.0.0",
  "status": "operational",
  "endpoints": {...}
}
```

### 2. **GET /api/v1/health** - Health Check
```bash
curl -H "X-API-Key: nova_dev_key_2026" http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "models_loaded": {
    "sora": true,
    "embeddings": true
  },
  "database_connected": true,
  "timestamp": "2026-01-18T17:40:54.944111"
}
```

### 3. **POST /api/v1/generate** - Generare Text

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "X-API-Key: nova_dev_key_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is courage?",
    "model": "sora",
    "max_tokens": 100,
    "temperature": null
  }'
```

**Parametri:**
- `prompt` (string, required): Text prompt
- `model` (string, optional): "doica" | "sora" | "merged" (default: "sora")
- `max_tokens` (int, optional): 1-500 (default: 150)
- `temperature` (float, optional): 0.0-2.0 (null = greedy decoding)
- `top_p` (float, optional): 0.0-1.0

Response:
```json
{
  "response": "The ability to face fear and act despite it...",
  "model_used": "sora",
  "tokens_generated": 44,
  "timestamp": "2026-01-18T17:40:54.944111"
}
```

### 4. **GET /api/v1/patterns/search** - Căutare Semantică

```bash
curl -H "X-API-Key: nova_dev_key_2026" \
  "http://localhost:8000/api/v1/patterns/search?query=courage%20fear&top_k=5"
```

**Parametri:**
- `query` (string, required): Query text
- `top_k` (int, optional): 1-20 rezultate (default: 5)

Response:
```json
{
  "query": "courage fear",
  "results": [
    {
      "name": "emotion_fear",
      "description": "Emotion of fear...",
      "category": "emotion",
      "confidence": 1.0,
      "similarity": 0.595
    }
  ],
  "timestamp": "2026-01-18T17:40:54.944111"
}
```

### 5. **GET /api/v1/patterns/related** - Pattern-uri Similare

```bash
curl -H "X-API-Key: nova_dev_key_2026" \
  "http://localhost:8000/api/v1/patterns/related?pattern=emotion_fear&top_k=3"
```

**Parametri:**
- `pattern` (string, required): Numele pattern-ului
- `top_k` (int, optional): 1-20 rezultate (default: 5)

Response:
```json
{
  "query": "Related to: emotion_fear",
  "results": [
    {
      "name": "emotion_anger",
      "similarity": 0.732,
      ...
    }
  ]
}
```

## 🧪 Test Client

```bash
cd /home/cezar/ai-cosmic-garden/Nova_20
source venv_nova/bin/activate
python3 test_api_client.py
```

## 🛑 Stop Server

```bash
pkill -f nova_api.py
```

Sau găsește PID-ul:
```bash
ps aux | grep nova_api.py
kill <PID>
```

## 📊 Logs

```bash
tail -f /home/cezar/ai-cosmic-garden/Nova_20/api_server.log
```

## 🔧 Configurare

### Variabile de Mediu

```bash
export NOVA_API_KEY="your_secure_key_here"  # API key (default: nova_dev_key_2026)
```

### CORS

Domenii permise (modifică în `nova_api.py`):
```python
allow_origins=["http://localhost:3000", "http://localhost:8080", "https://your-domain.com"]
```

### Rate Limiting

Default: 100 requests/minute (poate fi modificat în cod)

## 🏗️ Arhitectură

- **FastAPI** - framework async
- **Uvicorn** - ASGI server
- **Mistral-7B-Instruct-v0.3** - base model
- **LoRA adapters** - Sora (abstract reasoning)
- **Sentence Transformers** - embeddings (all-MiniLM-L6-v2)
- **PostgreSQL** - Cortex (validated patterns)
- **4-bit quantization** - memory optimization (7GB VRAM pentru Sora)

## 📈 Performance

- **Latență generare**: ~2-3 sec pentru 100 tokens (RTX 3090)
- **Latență search**: <100ms (PostgreSQL + embeddings)
- **VRAM usage**: ~8GB (Sora 4-bit + embeddings)
- **Capacitate**: Poate servi multiple requesturi concurrent (FastAPI async)

## 🔐 Securitate

⚠️ **Producție:**
1. Schimbă API key-ul în variabilă de mediu
2. Folosește HTTPS (reverse proxy cu Nginx/Caddy)
3. Adaugă rate limiting mai strict
4. Restricționează CORS origins
5. Adaugă logging și monitoring

## 💡 Exemple Python

```python
import requests

API_BASE = "http://localhost:8000"
headers = {"X-API-Key": "nova_dev_key_2026"}

# Generate
response = requests.post(
    f"{API_BASE}/api/v1/generate",
    headers=headers,
    json={"prompt": "What is consciousness?", "max_tokens": 100}
)
print(response.json()["response"])

# Search
response = requests.get(
    f"{API_BASE}/api/v1/patterns/search",
    headers=headers,
    params={"query": "emotion", "top_k": 5}
)
for pattern in response.json()["results"]:
    print(f"{pattern['name']}: {pattern['similarity']:.3f}")
```

## 🐛 Troubleshooting

### Server nu pornește
```bash
# Check dacă portul 8000 e ocupat
lsof -i :8000

# Check logs
tail -f api_server.log
```

### CUDA Out of Memory
- Reduce `max_tokens` în requesturi
- Restart server-ul pentru a elibera VRAM
- Verifică că nu rulează alte procese GPU

### Database connection failed
```bash
# Check PostgreSQL
systemctl status postgresql
PGPASSWORD=nova2026 psql -U nova -h localhost -d cortex -c "\l"
```

---

**Status**: ✅ Operational (Task 7 - COMPLETE)  
**Next**: Task 8 - Comprehensive model testing
