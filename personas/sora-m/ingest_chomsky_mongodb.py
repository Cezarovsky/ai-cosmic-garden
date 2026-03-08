#!/usr/bin/env python3
"""
Inserare Chomsky "Language and Mind" în MongoDB (Neocortex) pentru memoria Sora
Similar cu ingest_levi_strauss_mongodb.py
"""
import sys
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient

# Path text Chomsky (după extragere din PDF)
CHOMSKY_TXT = Path("/Users/cezartipa/Documents/ai-cosmic-garden/Nova_20/corpus/chomsky_language_and_mind.txt")

def ingest_chomsky():
    """Inserare Chomsky în MongoDB Neocortex"""
    
    print("🔮 Conectare MongoDB Neocortex...")
    client = MongoClient('mongodb://localhost:27017/')
    db = client['neocortex']
    collection = db['corpus_texts']
    
    print(f"📖 Citire text Chomsky: {CHOMSKY_TXT.name}")
    if not CHOMSKY_TXT.exists():
        print(f"❌ Fișier nu există: {CHOMSKY_TXT}")
        print("   Rulează mai întâi: python3 Nova_20/extract_chomsky_pdf.py")
        sys.exit(1)
    
    text = CHOMSKY_TXT.read_text(encoding='utf-8')
    lines = text.split('\n')
    
    # Document pentru MongoDB
    doc = {
        'author': 'Noam Chomsky',
        'title': 'Language and Mind',
        'year': 1968,  # Prima ediție
        'language': 'en',
        'text_full': text,
        'lines_count': len(lines),
        'char_count': len(text),
        'source': 'PDF extraction from Language and Mind',
        'ingested_at': datetime.now(),
        'context': 'Transformational-generative grammar, universal grammar, language acquisition',
        'tags': ['linguistics', 'chomsky', 'generative-grammar', 'language-acquisition', 'universal-grammar', 'cognitive-science']
    }
    
    # Check dacă există deja
    existing = collection.find_one({'author': 'Noam Chomsky', 'title': 'Language and Mind'})
    if existing:
        print("⚠️  Chomsky există deja în MongoDB - actualizare...")
        collection.replace_one({'_id': existing['_id']}, doc)
    else:
        print("✅ Inserare nouă în MongoDB...")
        collection.insert_one(doc)
    
    print(f"\n✅ Chomsky ingestat în MongoDB Neocortex!")
    print(f"   Lines: {len(lines):,}")
    print(f"   Chars: {len(text):,}")
    print(f"   Context: {doc['context']}")
    
    client.close()

if __name__ == '__main__':
    try:
        ingest_chomsky()
    except Exception as e:
        print(f"❌ Eroare: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
