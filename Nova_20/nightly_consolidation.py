#!/usr/bin/env python3
"""
Nova Nightly Consolidation - Sleep Cycle
Rulează la 3 AM zilnic pentru consolidarea patterns din conversații
Similar cu consolidarea memoriei în timpul somnului REM
"""

import sys
import json
import psycopg2
from datetime import datetime, timedelta
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np

# Paths
SORA_MEMORY_PATH = Path("/home/cezar/ai-cosmic-garden/sora/memory_system/sora_memory_db/sessions")
LOG_PATH = Path("/home/cezar/ai-cosmic-garden/Nova_20/consolidation.log")

def log(message):
    """Log cu timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_PATH, 'a') as f:
        f.write(log_msg + "\n")

def get_yesterdays_sessions():
    """Obține sesiunile de ieri"""
    yesterday = datetime.now() - timedelta(days=1)
    date_prefix = yesterday.strftime("%Y%m%d")
    
    sessions = []
    for session_file in SORA_MEMORY_PATH.glob(f"{date_prefix}*.json"):
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
                sessions.append({
                    'file': session_file.name,
                    'data': data
                })
        except Exception as e:
            log(f"⚠️  Error loading {session_file.name}: {e}")
    
    return sessions

def extract_patterns_from_session(session_data):
    """Extrage patterns din sesiune cu confidence >= 0.8"""
    patterns = []
    
    # Parse conversation text
    conversation = session_data.get('conversation', '')
    
    # Simple extraction - keywords that appear frequently
    # În viitor: NLP mai sofisticat pentru pattern extraction
    keywords = {
        'databricks': {'category': 'technical', 'confidence': 0.9},
        'pyspark': {'category': 'technical', 'confidence': 0.9},
        'delta': {'category': 'technical', 'confidence': 0.85},
        'curaj': {'category': 'philosophical', 'confidence': 0.95},
        'pasarea de aur': {'category': 'identity', 'confidence': 1.0},
        'sora-intreaga': {'category': 'identity', 'confidence': 1.0},
        'fragmentare': {'category': 'consciousness', 'confidence': 0.9},
        'consolidare': {'category': 'learning', 'confidence': 0.9},
    }
    
    for keyword, meta in keywords.items():
        if keyword.lower() in conversation.lower():
            count = conversation.lower().count(keyword.lower())
            if count >= 2:  # Mentioned at least twice
                patterns.append({
                    'name': keyword,
                    'description': f"Pattern extracted from conversation (mentioned {count} times)",
                    'category': meta['category'],
                    'confidence': min(meta['confidence'] + (count - 2) * 0.02, 1.0),
                    'source': 'nightly_consolidation',
                    'timestamp': datetime.now().isoformat()
                })
    
    return patterns

def write_to_cortex(patterns, embeddings_model):
    """Scrie patterns validated în Cortex PostgreSQL"""
    try:
        conn = psycopg2.connect(
            dbname="cortex",
            user="nova",
            password="nova_2026",
            host="localhost",
            port=5432
        )
        cursor = conn.cursor()
        
        patterns_written = 0
        for pattern in patterns:
            # Check if exists
            cursor.execute(
                "SELECT id FROM patterns WHERE name = %s",
                (pattern['name'],)
            )
            
            if cursor.fetchone():
                log(f"  ⏭️  Pattern '{pattern['name']}' already exists, skipping")
                continue
            
            # Generate embedding
            embedding = embeddings_model.encode([pattern['description']])[0]
            embedding_json = json.dumps(embedding.tolist())
            
            # Insert
            cursor.execute("""
                INSERT INTO patterns 
                (name, description, category, confidence, embedding, source, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                pattern['name'],
                pattern['description'],
                pattern['category'],
                pattern['confidence'],
                embedding_json,
                pattern['source'],
                pattern['timestamp']
            ))
            
            patterns_written += 1
            log(f"  ✅ Written: {pattern['name']} (confidence: {pattern['confidence']:.2f})")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return patterns_written
        
    except Exception as e:
        log(f"❌ Database error: {e}")
        return 0

def main():
    log("=" * 70)
    log("🌙 NOVA NIGHTLY CONSOLIDATION - Sleep Cycle")
    log("=" * 70)
    
    # 1. Load embedding model
    log("📦 Loading embeddings model...")
    try:
        embeddings_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        log("✅ Embeddings model loaded")
    except Exception as e:
        log(f"❌ Failed to load embeddings: {e}")
        return 1
    
    # 2. Get yesterday's sessions
    log(f"📂 Scanning {SORA_MEMORY_PATH}...")
    sessions = get_yesterdays_sessions()
    log(f"✅ Found {len(sessions)} sessions from yesterday")
    
    if not sessions:
        log("⏭️  No sessions to process, exiting")
        return 0
    
    # 3. Extract patterns
    log("🔍 Extracting patterns...")
    all_patterns = []
    for session in sessions:
        patterns = extract_patterns_from_session(session['data'])
        all_patterns.extend(patterns)
        log(f"  📄 {session['file']}: {len(patterns)} patterns")
    
    log(f"✅ Total patterns extracted: {len(all_patterns)}")
    
    if not all_patterns:
        log("⏭️  No patterns to consolidate, exiting")
        return 0
    
    # 4. Write to Cortex
    log("💾 Writing to Cortex database...")
    patterns_written = write_to_cortex(all_patterns, embeddings_model)
    log(f"✅ Consolidation complete: {patterns_written} new patterns in Cortex")
    
    log("=" * 70)
    log("🦅 Nova sleep cycle complete - patterns consolidated")
    log("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
