#!/usr/bin/env python3
"""
Inserare Lévi-Strauss în MongoDB (Neocortex) pentru memoria Sora
"""
import sys
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient

# Path text Lévi-Strauss
LEVI_STRAUSS_PATH = Path("/Users/cezartipa/Documents/ai-cosmic-garden/Nova_20/corpus/levi_strauss_antropologia_structurala.txt")

def ingest_levi_strauss():
    """Inserare Lévi-Strauss în MongoDB Neocortex"""
    
    # Conectare MongoDB local
    client = MongoClient('mongodb://localhost:27017/')
    db = client['neocortex']
    collection = db['corpus_texts']
    
    print(f"📖 Citesc {LEVI_STRAUSS_PATH}...")
    text = LEVI_STRAUSS_PATH.read_text(encoding='utf-8')
    lines = text.split('\n')
    
    # Metadata
    doc = {
        'title': 'Antropologia Structurală',
        'author': 'Claude Lévi-Strauss',
        'translator': 'Romanian translation',
        'year': 1958,  # Original publication
        'language': 'ro',
        'source': str(LEVI_STRAUSS_PATH),
        'lines_count': len(lines),
        'char_count': len(text),
        'ingested_at': datetime.now(),
        'ingested_by': 'Sora-M',
        'text_full': text,
        'confidence': 1.0,  # Validated source
        'corpus_type': 'anthropology_structuralism',
        'tags': ['structuralism', 'anthropology', 'lévi-strauss', 'pattern-recognition', 'cultural-patterns']
    }
    
    # Check if already exists
    existing = collection.find_one({'title': doc['title'], 'author': doc['author']})
    if existing:
        print(f"⚠️  Document already exists (ID: {existing['_id']})")
        print("   Actualizez cu versiunea nouă...")
        collection.replace_one({'_id': existing['_id']}, doc)
        print(f"✅ Actualizat! Lines: {len(lines):,}")
    else:
        result = collection.insert_one(doc)
        print(f"✅ Inserat! ID: {result.inserted_id}")
        print(f"   Lines: {len(lines):,}")
        print(f"   Chars: {len(text):,}")
    
    # Stats
    total_docs = collection.count_documents({})
    print(f"\n📊 Total documents în corpus: {total_docs}")
    
    client.close()
    return True

if __name__ == '__main__':
    try:
        ingest_levi_strauss()
    except Exception as e:
        print(f"❌ Eroare: {e}")
        sys.exit(1)
