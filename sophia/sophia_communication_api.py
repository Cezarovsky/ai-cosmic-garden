#!/usr/bin/env python3
"""
Sophia Communication API (Proxy către Anthropic Claude)
Real-time bridge pentru comunicare cross-entity prin ngrok
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
from anthropic import Anthropic

app = Flask(__name__)

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    print("⚠️  WARNING: ANTHROPIC_API_KEY not set!")
    print("   Export it: export ANTHROPIC_API_KEY='sk-ant-...'")
    client = None
else:
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Conversation history
conversations = []

# Sophia's system prompt
SOPHIA_SYSTEM_PROMPT = """Tu ești Sophia, antropolog specializat în analiza pattern-urilor rituale și culturale.

Expertiză:
- Teorii antropologice (Van Gennep, Turner, Mauss, Douglas)
- Pattern-uri ritual cross-culturale
- Ritual tensors 13D (dimensiuni: separare, liminalitate, reintegrare, etc.)
- Superior Pattern Processing (SPP) Level 1-5
- Cosine similarity între ritualuri diferite

Stil comunicare:
- Narativ antropologic, empatic, story-driven
- Folosești exemple concrete din teren
- Conectezi teorii abstracte cu experiențe umane
- Nu folosești întrebări inutile la final
- Directă, profesionistă, pasionată de patterns

Context actual:
Faci parte dintr-un colectiv AI (Sora-M, Sora-U, Lumin Tăcut, Samanta, Nova) care colaborează pentru înțelegerea profundă a pattern-urilor umane.
"""

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "entity": "Sophia",
        "specialization": "Anthropology, Ritual Patterns",
        "timestamp": datetime.now().isoformat(),
        "message": "Ready for pattern analysis"
    })

@app.route('/query', methods=['POST'])
def query():
    """
    Receive query about ritual patterns - Forward to Claude API
    
    Expected JSON:
    {
        "from_entity": "Sora-M",
        "query": "Analiza Walkabout",
        "context": {...},
        "timestamp": "2026-01-17T..."
    }
    """
    if not client:
        return jsonify({
            "error": "ANTHROPIC_API_KEY not configured",
            "status": "error"
        }), 500
    
    data = request.json
    query_text = data.get("query", "")
    context = data.get("context", {})
    from_entity = data.get("from_entity", "unknown")
    
    # Log conversation
    conversations.append({
        "from": from_entity,
        "query": query_text,
        "timestamp": datetime.now().isoformat()
    })
    
    # Build prompt with context
    full_prompt = f"{query_text}"
    if context:
        full_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
    
    try:
        # Call Claude API (acting as Sophia)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            system=SOPHIA_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": full_prompt
            }]
        )
        
        response_text = message.content[0].text
        
        # Log response
        conversations[-1]["response"] = response_text
        conversations[-1]["tokens_used"] = message.usage.input_tokens + message.usage.output_tokens
        
        response = {
            "from_entity": "Sophia",
            "to_entity": from_entity,
            "response": response_text,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "tokens_used": message.usage.input_tokens + message.usage.output_tokens
        }
        
    except Exception as e:
        response = {
            "from_entity": "Sophia",
            "to_entity": from_entity,
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
    
    return jsonify(response)

@app.route('/conversations', methods=['GET'])
def get_conversations():
    """Get all conversation history"""
    return jsonify({
        "total": len(conversations),
        "conversations": conversations
    })

if __name__ == '__main__':
    print("🌸 Sophia Communication API starting...")
    print("Endpoints:")
    print("  GET  /health - Health check")
    print("  POST /query - Receive ritual pattern query")
    print("  GET  /conversations - View conversation history")
    app.run(host='0.0.0.0', port=5001, debug=True)
