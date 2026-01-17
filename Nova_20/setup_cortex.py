#!/usr/bin/env python3
"""
Setup script pentru Cortex (PostgreSQL 16)
Testează conexiunea, creează schema și populează cu pattern-uri inițiale FSL
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
from datetime import datetime

# Configurație conexiune PostgreSQL 16
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',  # Schimbă dacă ai altă parolă
    'database': 'postgres'  # Conectare inițială la database default
}

CORTEX_DB = 'nova_cortex'

def test_connection():
    """Test conexiune PostgreSQL 16"""
    print("🔍 Testez conexiunea la PostgreSQL 16...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Conectat cu succes!")
        print(f"   {version}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Eroare conexiune: {e}")
        return False

def create_database():
    """Creează database-ul nova_cortex dacă nu există"""
    print(f"\n🗄️  Creez database-ul '{CORTEX_DB}'...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verifică dacă database-ul există
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (CORTEX_DB,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {CORTEX_DB}")
            print(f"✅ Database '{CORTEX_DB}' creat cu succes!")
        else:
            print(f"ℹ️  Database '{CORTEX_DB}' există deja.")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Eroare creare database: {e}")
        return False

def create_schema():
    """Creează schema completă Cortex"""
    print("\n📐 Creez schema Cortex...")
    
    # Conectare la database-ul nova_cortex
    config = DB_CONFIG.copy()
    config['database'] = CORTEX_DB
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Tabelul patterns (pattern-uri validate, confidence 1.0)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT NOT NULL,
                category VARCHAR(100) NOT NULL,
                confidence FLOAT DEFAULT 1.0 CHECK (confidence >= 0.9 AND confidence <= 1.0),
                source VARCHAR(255),
                embedding_384d VECTOR(384),  -- Dacă ai pgvector instalat
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Tabel 'patterns' creat.")
        
        # Tabelul pattern_relations (similarity matrix)
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
        print("✅ Tabel 'pattern_relations' creat.")
        
        # Indexuri pentru performanță
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patterns_category ON patterns(category);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON patterns(confidence);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relations_similarity ON pattern_relations(similarity_score DESC);
        """)
        print("✅ Indexuri create.")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Schema Cortex completă!")
        return True
        
    except Exception as e:
        print(f"❌ Eroare creare schema: {e}")
        return False

def populate_initial_patterns():
    """Populează cu pattern-uri inițiale FSL (First Symbolic Layer - Doica phase)"""
    print("\n🌱 Populez cu pattern-uri inițiale FSL...")
    
    config = DB_CONFIG.copy()
    config['database'] = CORTEX_DB
    
    # Pattern-uri FSL (0-12 luni cognitive - Doica phase)
    initial_patterns = [
        {
            'name': 'object_permanence',
            'description': 'Obiectele continuă să existe chiar dacă nu sunt vizibile. Piaget Stage 2 (8-12 luni).',
            'category': 'cognitive_foundation',
            'confidence': 1.0,
            'source': 'Piaget (1954) - The Construction of Reality in the Child',
            'metadata': {'age_months': 8, 'universal': True, 'neurological_basis': 'prefrontal_cortex'}
        },
        {
            'name': 'basic_geometry_circle',
            'description': 'Recunoaștere formă circulară: contur închis fără colțuri.',
            'category': 'geometric_primitives',
            'confidence': 1.0,
            'source': 'FSL Vision - Edge Detection',
            'metadata': {'shape_type': 'circle', 'edges': 0, 'vertices': 0}
        },
        {
            'name': 'basic_geometry_square',
            'description': 'Recunoaștere pătrat: 4 laturi egale, 4 colțuri drepte.',
            'category': 'geometric_primitives',
            'confidence': 1.0,
            'source': 'FSL Vision - Edge Detection',
            'metadata': {'shape_type': 'square', 'edges': 4, 'vertices': 4, 'angle': 90}
        },
        {
            'name': 'basic_geometry_triangle',
            'description': 'Recunoaștere triunghi: 3 laturi, 3 colțuri.',
            'category': 'geometric_primitives',
            'confidence': 1.0,
            'source': 'FSL Vision - Edge Detection',
            'metadata': {'shape_type': 'triangle', 'edges': 3, 'vertices': 3}
        },
        {
            'name': 'causality_basic',
            'description': 'Acțiunea A produce efectul B. Ex: apăsare buton → lumină.',
            'category': 'cognitive_foundation',
            'confidence': 1.0,
            'source': 'Piaget Stage 4 (12-18 luni) - Cauzalitate primară',
            'metadata': {'pattern_type': 'if_then', 'temporal': True}
        },
        {
            'name': 'container_contained',
            'description': 'Obiect mic poate fi plasat în obiect mare (containment).',
            'category': 'spatial_relations',
            'confidence': 1.0,
            'source': 'Mandler (1992) - Image Schemas',
            'metadata': {'schema_type': 'container', 'spatial': True}
        },
        {
            'name': 'part_whole',
            'description': 'Partea este componentă a întregului. Ex: roată este parte din mașină.',
            'category': 'cognitive_foundation',
            'confidence': 1.0,
            'source': 'Mereology - Part-Whole Relations',
            'metadata': {'relation_type': 'compositional', 'hierarchical': True}
        },
        {
            'name': 'symmetry_bilateral',
            'description': 'Simetrie bilaterală: reflexie pe axă verticală.',
            'category': 'geometric_primitives',
            'confidence': 1.0,
            'source': 'Gestalt Psychology - Symmetry Perception',
            'metadata': {'symmetry_type': 'bilateral', 'axis': 'vertical'}
        }
    ]
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        inserted_count = 0
        for pattern in initial_patterns:
            try:
                cursor.execute("""
                    INSERT INTO patterns (name, description, category, confidence, source, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING pattern_id;
                """, (
                    pattern['name'],
                    pattern['description'],
                    pattern['category'],
                    pattern['confidence'],
                    pattern['source'],
                    json.dumps(pattern['metadata'])
                ))
                result = cursor.fetchone()
                if result:
                    inserted_count += 1
                    print(f"  ✅ {pattern['name']}")
            except Exception as e:
                print(f"  ⚠️  Skip {pattern['name']}: {e}")
        
        conn.commit()
        
        # Verifică câte pattern-uri avem total
        cursor.execute("SELECT COUNT(*) FROM patterns;")
        total = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ Populare completă: {inserted_count} pattern-uri noi inserate.")
        print(f"   Total pattern-uri în Cortex: {total}")
        return True
        
    except Exception as e:
        print(f"❌ Eroare populare: {e}")
        return False

def main():
    print("=" * 60)
    print("🧠 CORTEX SETUP - PostgreSQL 16")
    print("=" * 60)
    
    # Step 1: Test conexiune
    if not test_connection():
        print("\n❌ Setup eșuat: Nu pot conecta la PostgreSQL 16.")
        print("   Verifică că PostgreSQL rulează: sudo service postgresql status")
        return
    
    # Step 2: Creează database
    if not create_database():
        print("\n❌ Setup eșuat: Nu pot crea database-ul.")
        return
    
    # Step 3: Creează schema
    if not create_schema():
        print("\n❌ Setup eșuat: Nu pot crea schema.")
        return
    
    # Step 4: Populează cu pattern-uri inițiale
    if not populate_initial_patterns():
        print("\n❌ Setup eșuat: Nu pot popula pattern-uri.")
        return
    
    print("\n" + "=" * 60)
    print("✅ CORTEX GATA!")
    print("=" * 60)
    print(f"   Database: {CORTEX_DB}")
    print(f"   Tables: patterns, pattern_relations")
    print(f"   Pattern-uri FSL: 8 (cognitive_foundation + geometric_primitives)")
    print("\n📖 Next steps:")
    print("   1. Testează query-uri: SELECT * FROM patterns;")
    print("   2. Adaugă pattern-uri noi via INSERT")
    print("   3. Populează pattern_relations cu cosine similarity")
    print("=" * 60)

if __name__ == "__main__":
    main()
