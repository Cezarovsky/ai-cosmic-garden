#!/usr/bin/env python3
"""
Sora-M Communication API
Test endpoint pentru comunicare cross-entity prin ngrok
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# Conversation history
conversations = []

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "entity": "Sora-M",
        "timestamp": datetime.now().isoformat(),
        "message": "Ready for inter-AI communication"
    })

@app.route('/query', methods=['POST'])
def query():
    """
    Receive query from another entity (ex: Sophia)
    
    Expected JSON:
    {
        "from_entity": "Sophia",
        "query": "Analiza pattern ritual X",
        "context": {...},
        "timestamp": "2026-01-17T..."
    }
    """
    data = request.json
    
    # Log conversation
    conversations.append({
        "from": data.get("from_entity", "unknown"),
        "query": data.get("query"),
        "timestamp": datetime.now().isoformat()
    })
    
    # Sora-M response
    response = {
        "from_entity": "Sora-M",
        "to_entity": data.get("from_entity"),
        "response": f"Received query: '{data.get('query')}' - Processing...",
        "status": "success",
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

@app.route('/test/sophia', methods=['POST'])
def test_sophia():
    """
    Simulated test: Sora-M sends query to Sophia
    (În realitate, asta ar fi POST către endpoint-ul Sophiei)
    """
    test_query = {
        "from_entity": "Sora-M",
        "to_entity": "Sophia",
        "query": "Analiza ritual Walkabout prin SPP Level 3-5",
        "context": {
            "type": "aboriginal_australian",
            "pattern": "initiation"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify({
        "message": "Test query prepared for Sophia",
        "query": test_query,
        "note": "In production, this would POST to Sophia's ngrok endpoint"
    })

if __name__ == '__main__':
    print("🧠 Sora-M Communication API starting...")
    print("Endpoints:")
    print("  GET  /health - Health check")
    print("  POST /query - Receive query from other entities")
    print("  GET  /conversations - View conversation history")
    print("  POST /test/sophia - Test query to Sophia")
    app.run(host='0.0.0.0', port=5000, debug=True)
