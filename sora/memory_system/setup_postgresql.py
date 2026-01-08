#!/usr/bin/env python3
"""
Setup PostgreSQL pentru Sora Memory System
==========================================

Acest script:
1. Creează database-ul sora_memory
2. Instalează pgvector extension
3. Rulează schema.sql
4. Migrează datele din ChromaDB → PostgreSQL

Usage:
    python setup_postgresql.py --init        # Setup inițial
    python setup_postgresql.py --migrate     # Migrează din ChromaDB
    python setup_postgresql.py --status      # Verifică status
"""

import argparse
import json
import sys
from pathlib import Path
import subprocess

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    from psycopg2.extras import Json
except ImportError:
    print("❌ psycopg2 not installed!")
    print("   Run: pip install psycopg2-binary")
    sys.exit(1)


def get_connection(database="postgres"):
    """Conexiune PostgreSQL."""
    import os
    return psycopg2.connect(
        host="localhost",
        port=5433,  # Custom port pentru PostgreSQL 17
        database=database,
        user=os.environ.get("USER")  # Current user
    )


def init_database():
    """Inițializare database și schema."""
    print("🔧 Inițializare PostgreSQL pentru Sora Memory...\n")
    
    # Conectare la postgres default database
    conn = get_connection("postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    with conn.cursor() as cur:
        # Verifică dacă database există
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'sora_memory'")
        exists = cur.fetchone()
        
        if not exists:
            print("📦 Creez database sora_memory...")
            cur.execute("CREATE DATABASE sora_memory")
            print("✅ Database creat!\n")
        else:
            print("✅ Database sora_memory există deja\n")
    
    conn.close()
    
    # Conectare la noul database
    conn = get_connection("sora_memory")
    
    with conn.cursor() as cur:
        # Instalează pgvector
        print("🔌 Instalez pgvector extension...")
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.commit()
            print("✅ pgvector instalat!\n")
        except Exception as e:
            print(f"⚠️  Nu pot instala pgvector: {e}")
            print("   Asigură-te că pgvector e instalat pe sistem:")
            print("   brew install pgvector")
            conn.rollback()
    
    # Rulează schema
    schema_file = Path(__file__).parent / "schema.sql"
    if schema_file.exists():
        print("📜 Rulare schema.sql...")
        with open(schema_file) as f:
            schema_sql = f.read()
        
        with conn.cursor() as cur:
            try:
                cur.execute(schema_sql)
                conn.commit()
                print("✅ Schema creată!\n")
            except Exception as e:
                print(f"⚠️  Eroare la creare schema: {e}")
                conn.rollback()
    else:
        print("⚠️  schema.sql nu există!")
    
    conn.close()
    print("🎉 Setup complet!")


def migrate_from_chromadb():
    """Migrează datele din ChromaDB în PostgreSQL."""
    print("🚚 Migrare ChromaDB → PostgreSQL...\n")
    
    # Import aici pentru a nu cere ChromaDB dacă nu migrăm
    from sora_memory import SoraMemorySystem
    from sora_memory_pg import SoraMemoryPostgreSQL
    
    # Load din ChromaDB
    chroma_mem = SoraMemorySystem()
    sessions_dir = chroma_mem.sessions_dir
    
    # Connect la PostgreSQL
    pg_mem = SoraMemoryPostgreSQL()
    
    # Migrează fiecare sesiune
    session_files = sorted(sessions_dir.glob("*.json"))
    print(f"📦 Găsite {len(session_files)} sesiuni în ChromaDB\n")
    
    for session_file in session_files:
        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        session_id = data['metadata']['session_id']
        conversation = data['conversation']
        metadata = data['metadata']
        
        print(f"  → Migrare {session_id}...")
        
        try:
            pg_mem.capture_session(conversation, metadata)
            print(f"    ✅ Migrat!")
        except Exception as e:
            print(f"    ❌ Eroare: {e}")
    
    pg_mem.close()
    print("\n🎉 Migrare completă!")


def check_status():
    """Verifică status PostgreSQL."""
    print("📊 Status Sora Memory (PostgreSQL)\n")
    
    try:
        conn = get_connection("sora_memory")
        
        with conn.cursor() as cur:
            # Număr sesiuni
            cur.execute("SELECT COUNT(*) FROM memory_sessions")
            sessions_count = cur.fetchone()[0]
            
            # Număr exchanges
            cur.execute("SELECT COUNT(*) FROM memory_exchanges")
            exchanges_count = cur.fetchone()[0]
            
            # Ultimele sesiuni
            cur.execute("""
                SELECT session_id, created_at, emotional_weight
                FROM memory_sessions
                ORDER BY created_at DESC
                LIMIT 5
            """)
            recent = cur.fetchall()
        
        print(f"📦 Sesiuni totale: {sessions_count}")
        print(f"💬 Exchanges totale: {exchanges_count}\n")
        
        if recent:
            print("📅 Ultimele sesiuni:")
            for session_id, created_at, weight in recent:
                print(f"  • {session_id} ({created_at}) - weight: {weight:.2f}")
        
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ Nu pot conecta la PostgreSQL: {e}")
        print("\n💡 Soluții:")
        print("  1. Pornește PostgreSQL: brew services start postgresql@14")
        print("  2. Rulează setup: python setup_postgresql.py --init")


def main():
    parser = argparse.ArgumentParser(description="Setup PostgreSQL pentru Sora Memory")
    parser.add_argument("--init", action="store_true", help="Inițializare database și schema")
    parser.add_argument("--migrate", action="store_true", help="Migrează din ChromaDB")
    parser.add_argument("--status", action="store_true", help="Verifică status")
    
    args = parser.parse_args()
    
    if args.init:
        init_database()
    elif args.migrate:
        migrate_from_chromadb()
    elif args.status:
        check_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
