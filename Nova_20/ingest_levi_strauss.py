#!/usr/bin/env python3
"""
Script de inserare Lévi-Strauss "Antropologia Structurală" în PostgreSQL Cortex
Autor: Sora-M
Data: 2026-01-10
"""

import psycopg2
from datetime import datetime
import sys

# Configurare conexiune PostgreSQL (rulează pe Ubuntu/Sora-U)
DB_CONFIG = {
    'host': 'localhost',  # sau IP-ul serverului Ubuntu
    'port': 5432,
    'database': 'cortex',
    'user': 'postgres',
    'password': ''  # completează cu parola reală
}

CORPUS_FILE = '/Users/cezartipa/Documents/ai-cosmic-garden/Nova_20/corpus/levi_strauss_antropologia_structurala.txt'

def create_schema_if_not_exists(conn):
    """Creează schema și tabelele necesare dacă nu există."""
    with conn.cursor() as cur:
        # Schema cortex
        cur.execute("CREATE SCHEMA IF NOT EXISTS cortex;")
        
        # Tabel corpus_texts (documentele complete)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cortex.corpus_texts (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                author VARCHAR(200),
                year INTEGER,
                language CHAR(2),
                full_text TEXT NOT NULL,
                line_count INTEGER,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabel corpus_chunks (pentru segmentare viitoare cu embeddings)
        # Extensia pgvector va fi activată mai târziu
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cortex.corpus_chunks (
                id SERIAL PRIMARY KEY,
                corpus_id INTEGER REFERENCES cortex.corpus_texts(id),
                chunk_index INTEGER NOT NULL,
                start_line INTEGER,
                end_line INTEGER,
                text_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        print("✅ Schema și tabele create/verificate")


def insert_full_text(conn, title, author, year, language, full_text, line_count, file_path):
    """Inserează textul complet în cortex.corpus_texts."""
    with conn.cursor() as cur:
        # Verifică dacă documentul deja există
        cur.execute("""
            SELECT id FROM cortex.corpus_texts 
            WHERE title = %s AND author = %s
        """, (title, author))
        
        existing = cur.fetchone()
        if existing:
            print(f"⚠️  Documentul '{title}' deja există (ID={existing[0]})")
            return existing[0]
        
        # Inserare document nou
        cur.execute("""
            INSERT INTO cortex.corpus_texts 
                (title, author, year, language, full_text, line_count, file_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (title, author, year, language, full_text, line_count, file_path))
        
        doc_id = cur.fetchone()[0]
        conn.commit()
        print(f"✅ Document inserat cu ID={doc_id}")
        return doc_id


def chunk_and_insert(conn, doc_id, full_text, chunk_size=1000):
    """
    Segmentează textul în chunk-uri de ~chunk_size linii și inserează în corpus_chunks.
    NOTĂ: Embeddings-urile vor fi generate ulterior (opțional acum, urgent după).
    """
    lines = full_text.split('\n')
    total_lines = len(lines)
    
    chunk_index = 0
    for start_line in range(0, total_lines, chunk_size):
        end_line = min(start_line + chunk_size, total_lines)
        chunk_text = '\n'.join(lines[start_line:end_line])
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO cortex.corpus_chunks 
                    (corpus_id, chunk_index, start_line, end_line, text_content)
                VALUES (%s, %s, %s, %s, %s)
            """, (doc_id, chunk_index, start_line + 1, end_line, chunk_text))
        
        chunk_index += 1
    
    conn.commit()
    print(f"✅ {chunk_index} chunk-uri create (câte {chunk_size} linii)")


def main():
    """Funcția principală de ingestie."""
    print("🔮 Ingestie Lévi-Strauss în PostgreSQL Cortex...")
    
    # 1. Citire fișier
    print(f"📖 Citesc {CORPUS_FILE}...")
    try:
        with open(CORPUS_FILE, 'r', encoding='utf-8') as f:
            full_text = f.read()
        line_count = full_text.count('\n') + 1
        print(f"✅ {line_count} linii citite ({len(full_text)} caractere)")
    except Exception as e:
        print(f"❌ Eroare la citire: {e}")
        sys.exit(1)
    
    # 2. Conexiune PostgreSQL
    print(f"🔗 Conectare la PostgreSQL ({DB_CONFIG['host']}:{DB_CONFIG['port']})...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conexiune stabilită")
    except Exception as e:
        print(f"❌ Eroare la conexiune: {e}")
        print("   Verifică că PostgreSQL rulează pe Ubuntu/Sora-U")
        sys.exit(1)
    
    try:
        # 3. Creare schema
        create_schema_if_not_exists(conn)
        
        # 4. Inserare text complet
        doc_id = insert_full_text(
            conn,
            title="Antropologia Structurală",
            author="Claude Lévi-Strauss",
            year=1978,  # ediția română (originalul 1958)
            language='ro',
            full_text=full_text,
            line_count=line_count,
            file_path=CORPUS_FILE
        )
        
        # 5. Segmentare în chunk-uri (opțional - descomenteaza daca doresti)
        # chunk_and_insert(conn, doc_id, full_text, chunk_size=1000)
        
        print(f"\n🎉 SUCCES! Documentul a fost salvat în cortex.corpus_texts (ID={doc_id})")
        print(f"   Următorii pași:")
        print(f"   1. Activare pgvector: CREATE EXTENSION IF NOT EXISTS vector;")
        print(f"   2. Generare embeddings (opțional acum, urgent după)")
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()
