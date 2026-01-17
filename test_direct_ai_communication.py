#!/usr/bin/env python3
"""
Test: Sora-M sends query directly to Sophia (no human mediation)
"""

import requests
import json
from datetime import datetime

# Sophia's ngrok URL (replace after starting ngrok)
SOPHIA_URL = "https://YOUR-SOPHIA-NGROK-URL.ngrok.io/query"

# Example: Sora-M asks Sophia about ritual pattern
def sora_asks_sophia():
    query = {
        "from_entity": "Sora-M",
        "query": "Analiza Walkabout prin SPP Level 3-5. Compară cu inițiere neolitică.",
        "context": {
            "type": "aboriginal_australian",
            "pattern": "initiation",
            "requested_spp_levels": [3, 4, 5]
        },
        "timestamp": datetime.now().isoformat()
    }
    
    print("🧠 Sora-M → Sophia:")
    print(f"Query: {query['query']}\n")
    
    try:
        response = requests.post(SOPHIA_URL, json=query, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print("🌸 Sophia → Sora-M:")
        print(f"Response:\n{data['response']}\n")
        print(f"Status: {data['status']}")
        print(f"Tokens used: {data.get('tokens_used', 'N/A')}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error communicating with Sophia: {e}")
        return None

# Example: Nova asks Sophia (future scenario)
def nova_asks_sophia():
    query = {
        "from_entity": "Nova",
        "query": """Am detectat un pattern în datele mele:
        
Hieroglifa egipteană a ibisului apare frecvent în contexte asociate cu Thoth (zeul înțelepciunii).

Ipoteza (confidence 0.7): Ibisul = simbol înțelepciune pentru că:
1. Forma hieroglifei seamănă cu Thoth
2. Ibisul = pasăre migratoare (cunoaște drumuri = navigație = înțelepciune practică)
3. Comportament observațional (ibisul stă pe mal, observă apa = contemplare)

Tu ce crezi din perspectivă antropologică? E pattern universal pasăre ↔ înțelepciune?""",
        "context": {
            "domain": "egyptian_mythology",
            "pattern_type": "symbolic_association",
            "confidence": 0.7
        },
        "timestamp": datetime.now().isoformat()
    }
    
    print("\n" + "="*60)
    print("🤖 Nova → Sophia:")
    print(f"Theory exploration:\n{query['query']}\n")
    
    try:
        response = requests.post(SOPHIA_URL, json=query, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print("🌸 Sophia → Nova:")
        print(f"Response:\n{data['response']}\n")
        print(f"Status: {data['status']}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error communicating with Sophia: {e}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("🧪 Testing Direct AI-to-AI Communication")
    print("="*60)
    print()
    
    if "YOUR-SOPHIA-NGROK-URL" in SOPHIA_URL:
        print("⚠️  Update SOPHIA_URL with actual ngrok URL first!")
        print("   1. Start sophia_communication_api.py")
        print("   2. Start ngrok http 5001")
        print("   3. Replace SOPHIA_URL in this script")
        exit(1)
    
    # Test 1: Sora-M query
    sora_asks_sophia()
    
    # Test 2: Nova query (simulated)
    nova_asks_sophia()
    
    print("\n✅ Tests complete!")
