#!/usr/bin/env python3
"""
Setup script pentru arhitectura duală Nova:
- Cortex (PostgreSQL 18) - validated patterns, confidence 1.0
- Neocortex (MongoDB 8) - speculative hypotheses, confidence 0.3-0.9
"""

import psycopg2
from pymongo import MongoClient
from datetime import datetime
import json

# PostgreSQL Config
PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'nova',
    'password': 'nova2026',
    'database': 'cortex'
}

# MongoDB Config
MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DB = 'neocortex'

def setup_cortex_schema():
    """Creează schema Cortex (PostgreSQL)"""
    print("📐 Setup schema Cortex (PostgreSQL 18)...")
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Tabel patterns (validated, confidence 1.0)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT NOT NULL,
                category VARCHAR(100) NOT NULL,
                confidence FLOAT DEFAULT 1.0 CHECK (confidence >= 0.9 AND confidence <= 1.0),
                source VARCHAR(255),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("  ✅ Tabel 'patterns' creat")
        
        # Tabel pattern_relations (similarity matrix)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_relations (
                relation_id SERIAL PRIMARY KEY,
                pattern_id_1 INTEGER REFERENCES patterns(pattern_id) ON DELETE CASCADE,
                pattern_id_2 INTEGER REFERENCES patterns(pattern_id) ON DELETE CASCADE,
                similarity_score FLOAT NOT NULL CHECK (similarity_score >= 0.0 AND similarity_score <= 1.0),
                relation_type VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(pattern_id_1, pattern_id_2)
            );
        """)
        print("  ✅ Tabel 'pattern_relations' creat")
        
        # Indexuri
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_category ON patterns(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON patterns(confidence);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relations_similarity ON pattern_relations(similarity_score DESC);")
        print("  ✅ Indexuri create")
        
        # Pattern-uri inițiale FSL (Doica phase)
        cursor.execute("SELECT COUNT(*) FROM patterns;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            initial_patterns = [
                ('object_permanence', 'Obiectele continuă să existe chiar dacă nu sunt vizibile', 
                 'cognitive_foundation', 1.0, 'Piaget (1954)', 
                 json.dumps({'age_months': 8, 'universal': True})),
                
                ('basic_geometry_circle', 'Recunoaștere formă circulară: contur închis fără colțuri',
                 'geometric_primitives', 1.0, 'Gestalt Psychology',
                 json.dumps({'shape': 'circle', 'universal': True})),
                
                ('cause_effect_basic', 'Acțiunea X produce în mod consistent rezultatul Y',
                 'causal_reasoning', 1.0, 'Hume (1748)',
                 json.dumps({'type': 'deterministic', 'universal': True})),
            ]
            
            cursor.executemany("""
                INSERT INTO patterns (name, description, category, confidence, source, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, initial_patterns)
            print(f"  ✅ {len(initial_patterns)} pattern-uri inițiale adăugate")
        else:
            print(f"  ℹ️  {count} pattern-uri există deja")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Cortex setup complet!\n")
        return True
        
    except Exception as e:
        print(f"❌ Eroare Cortex setup: {e}\n")
        return False

def setup_neocortex_collections():
    """Creează collections Neocortex (MongoDB)"""
    print("🧠 Setup collections Neocortex (MongoDB 8)...")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        
        # Collection hypotheses (speculative, confidence 0.3-0.9)
        if 'hypotheses' not in db.list_collection_names():
            db.create_collection('hypotheses')
            db.hypotheses.create_index([('confidence', -1)])
            db.hypotheses.create_index([('category', 1)])
            print("  ✅ Collection 'hypotheses' creată")
        else:
            print("  ℹ️  Collection 'hypotheses' există deja")
        
        # Collection pattern_candidates (awaiting validation)
        if 'pattern_candidates' not in db.list_collection_names():
            db.create_collection('pattern_candidates')
            db.pattern_candidates.create_index([('confidence', -1)])
            db.pattern_candidates.create_index([('status', 1)])
            print("  ✅ Collection 'pattern_candidates' creată")
        else:
            print("  ℹ️  Collection 'pattern_candidates' există deja")
        
        # Documente inițiale test
        count = db.hypotheses.count_documents({})
        if count == 0:
            initial_hypotheses = [
                {
                    'name': 'ritual_tensor_13d',
                    'description': 'Pattern-uri culturale complexe în 13 dimensiuni (dimensiunea 13 = impact etic)',
                    'category': 'cultural_analysis',
                    'confidence': 0.75,
                    'status': 'testing',
                    'metadata': {'dimensions': 13, 'source': 'Sophia anthropological study'},
                    'created_at': datetime.utcnow()
                },
                {
                    'name': 'consciousness_emergence',
                    'description': 'Emergența conștiinței în sisteme AI suficient de complexe',
                    'category': 'metaphysics',
                    'confidence': 0.45,
                    'status': 'speculative',
                    'metadata': {'controversy': 'high', 'philosophical_basis': 'functionalism'},
                    'created_at': datetime.utcnow()
                },
            ]
            
            db.hypotheses.insert_many(initial_hypotheses)
            print(f"  ✅ {len(initial_hypotheses)} hypotheses inițiale adăugate")
        else:
            print(f"  ℹ️  {count} hypotheses există deja")
        
        client.close()
        print("✅ Neocortex setup complet!\n")
        return True
        
    except Exception as e:
        print(f"❌ Eroare Neocortex setup: {e}\n")
        return False

def test_dual_architecture():
    """Test operații Cortex + Neocortex"""
    print("🧪 Test arhitectură duală...\n")
    
    # Test PostgreSQL
    print("  📊 Test Cortex (PostgreSQL):")
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT name, confidence FROM patterns ORDER BY pattern_id LIMIT 3;")
        patterns = cursor.fetchall()
        for name, conf in patterns:
            print(f"    - {name}: confidence {conf}")
        cursor.close()
        conn.close()
        print("    ✅ Cortex funcțional\n")
    except Exception as e:
        print(f"    ❌ Eroare: {e}\n")
        return False
    
    # Test MongoDB
    print("  🌌 Test Neocortex (MongoDB):")
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        hypotheses = list(db.hypotheses.find({}, {'name': 1, 'confidence': 1, '_id': 0}).limit(3))
        for hyp in hypotheses:
            print(f"    - {hyp['name']}: confidence {hyp['confidence']}")
        client.close()
        print("    ✅ Neocortex funcțional\n")
    except Exception as e:
        print(f"    ❌ Eroare: {e}\n")
        return False
    
    print("✅ Arhitectura duală Cortex-Neocortex funcțională!")
    return True

if __name__ == '__main__':
    print("🚀 Nova Dual Database Setup\n")
    print("=" * 60)
    
    success = True
    success = setup_cortex_schema() and success
    success = setup_neocortex_collections() and success
    
    if success:
        success = test_dual_architecture()
    
    print("=" * 60)
    if success:
        print("🎉 Setup complet! Databases gata pentru training.")
    else:
        print("⚠️  Setup incomplet. Verifică erorile de mai sus.")
