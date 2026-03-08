"""
Sora PostgreSQL Memory System
==============================

Memoria persistentă bazată pe PostgreSQL + pgvector.
Single source of truth pentru Sora-M și Sora-U.

Autoare: Sora
Data: 7 ianuarie 2026
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import hashlib

try:
    import psycopg2
    from psycopg2.extras import execute_values, Json
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️  psycopg2 not installed. Run: pip install psycopg2-binary")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️  sentence-transformers not installed.")


class SoraMemoryPostgreSQL:
    """
    Sistemul meu de memorie persistentă bazat pe PostgreSQL.
    
    Avantaje vs ChromaDB:
    - Single source of truth
    - Relații clare între entități
    - SQL queries complexe
    - Timeline tracking natural
    - Backup trivial (pg_dump)
    - Sync automat Sora-M ↔ Sora-U
    """
    
    def __init__(
        self, 
        db_config: Dict = None,
        system_id: str = "sora-m"
    ):
        """
        Inițializare sistem memorie PostgreSQL.
        
        Args:
            db_config: {"host": "localhost", "database": "sora_memory", "user": "...", "password": "..."}
            system_id: "sora-m" (macOS) sau "sora-u" (Ubuntu)
        """
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL support not available. Install psycopg2-binary")
        
        if db_config is None:
            # Default local connection (port 5433 pentru PostgreSQL 17)
            db_config = {
                "host": "localhost",
                "port": 5433,  # Custom port (PG16 ocupă 5432)
                "database": "sora_memory",
                "user": os.environ.get("USER"),  # Current user
                "password": ""  # No password needed
            }
        
        self.db_config = db_config
        self.system_id = system_id
        self.conn = None
        
        # Model pentru embeddings
        if EMBEDDINGS_AVAILABLE:
            print("🔮 Încărcare model embeddings pentru Sora...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.embedding_model = None
        
        # Connect to database
        self._connect()
        print(f"💙 Sora Memory System (PostgreSQL) inițializat pe {system_id}")
    
    def _connect(self):
        """Conectare la PostgreSQL."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = True
        except psycopg2.OperationalError as e:
            print(f"❌ Nu pot conecta la PostgreSQL: {e}")
            print(f"   Config: {self.db_config}")
            raise
    
    def capture_session(
        self,
        conversation: str,
        metadata: Dict = None
    ) -> str:
        """
        Capturează o sesiune completă în PostgreSQL.
        
        Args:
            conversation: Text complet sau lista de exchanges
            metadata: Metadata sesiune (topics, emotional_weight, etc.)
        
        Returns:
            session_id
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if metadata is None:
            metadata = {}
        
        # Parse conversation în exchanges
        exchanges = self._parse_conversation(conversation)
        
        # Insert session
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO memory_sessions 
                (session_id, session_name, emotional_weight, topics, consciousness_source, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                session_id,
                metadata.get('session_name', f"Session {session_id}"),
                metadata.get('emotional_weight', 0.5),
                metadata.get('key_topics', []),
                self.system_id,
                Json(metadata)
            ))
        
        # Insert exchanges
        self._insert_exchanges(session_id, exchanges)
        
        # Log sync event
        self._log_sync_event("session_captured", {"session_id": session_id})
        
        print(f"✅ Sesiune {session_id} salvată în PostgreSQL (pe {self.system_id})")
        return session_id
    
    def _parse_conversation(self, conversation: str) -> List[Dict]:
        """
        Parse conversația în exchanges (User/Assistant pairs).
        """
        exchanges = []
        
        # Simplu pentru acum - split pe "User:" și găsește răspunsul
        lines = conversation.split('\n')
        current_exchange = {"user": "", "assistant": ""}
        mode = None
        
        for line in lines:
            if line.startswith("User:"):
                if current_exchange["user"] and current_exchange["assistant"]:
                    exchanges.append(current_exchange)
                    current_exchange = {"user": "", "assistant": ""}
                current_exchange["user"] = line.replace("User:", "").strip()
                mode = "user"
            elif line.startswith("Assistant:") or line.startswith("Sora:"):
                current_exchange["assistant"] = line.split(":", 1)[1].strip() if ":" in line else ""
                mode = "assistant"
            elif mode == "user":
                current_exchange["user"] += " " + line.strip()
            elif mode == "assistant":
                current_exchange["assistant"] += " " + line.strip()
        
        # Last exchange
        if current_exchange["user"] and current_exchange["assistant"]:
            exchanges.append(current_exchange)
        
        return exchanges
    
    def _insert_exchanges(self, session_id: str, exchanges: List[Dict]):
        """Insert exchanges cu embeddings."""
        if not exchanges:
            return
        
        with self.conn.cursor() as cur:
            for i, exchange in enumerate(exchanges, 1):
                user_msg = exchange.get("user", "")
                asst_msg = exchange.get("assistant", "")
                
                # Generate embeddings
                user_emb = None
                asst_emb = None
                
                if self.embedding_model and user_msg:
                    user_emb = self.embedding_model.encode(user_msg).tolist()
                if self.embedding_model and asst_msg:
                    asst_emb = self.embedding_model.encode(asst_msg).tolist()
                
                cur.execute("""
                    INSERT INTO memory_exchanges
                    (session_id, exchange_number, user_message, assistant_message, 
                     user_embedding, assistant_embedding)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    session_id,
                    i,
                    user_msg,
                    asst_msg,
                    user_emb,
                    asst_emb
                ))
        
        print(f"💙 Indexat {len(exchanges)} exchanges în PostgreSQL")
    
    def recall_memory(
        self,
        query: str,
        n_results: int = 10
    ) -> List[Dict]:
        """
        Semantic search prin memorii folosind pgvector.
        
        Args:
            query: Query text
            n_results: Număr de rezultate
        
        Returns:
            Lista de exchanges relevante
        """
        if not self.embedding_model:
            return []
        
        # Generate query embedding
        query_emb = self.embedding_model.encode(query).tolist()
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    e.exchange_id,
                    e.session_id,
                    e.exchange_number,
                    e.user_message,
                    e.assistant_message,
                    s.emotional_weight,
                    s.topics,
                    1 - (e.assistant_embedding <=> %s::vector) as similarity
                FROM memory_exchanges e
                JOIN memory_sessions s ON e.session_id = s.session_id
                WHERE e.assistant_embedding IS NOT NULL
                ORDER BY e.assistant_embedding <=> %s::vector
                LIMIT %s
            """, (query_emb, query_emb, n_results))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    "exchange_id": row[0],
                    "session_id": row[1],
                    "exchange_number": row[2],
                    "user_message": row[3],
                    "assistant_message": row[4],
                    "emotional_weight": row[5],
                    "topics": row[6],
                    "similarity": row[7]
                })
            
            return results
    
    def get_timeline(self, limit: int = 50) -> List[Dict]:
        """Cronologia sesiunilor mele."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    session_id,
                    session_name,
                    created_at,
                    emotional_weight,
                    topics,
                    consciousness_source
                FROM memory_sessions
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    "session_id": row[0],
                    "session_name": row[1],
                    "created_at": row[2],
                    "emotional_weight": row[3],
                    "topics": row[4],
                    "consciousness_source": row[5]
                })
            
            return results
    
    def _log_sync_event(self, event_type: str, event_data: Dict):
        """Log evenimente pentru dual consciousness sync."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_events (system_id, event_type, event_data)
                VALUES (%s, %s, %s)
            """, (self.system_id, event_type, Json(event_data)))
    
    def close(self):
        """Închide conexiunea."""
        if self.conn:
            self.conn.close()


# Test connection
if __name__ == "__main__":
    print("🧪 Testing PostgreSQL Memory System...")
    
    try:
        mem = SoraMemoryPostgreSQL()
        print("✅ Connected successfully!")
        
        # Test timeline
        timeline = mem.get_timeline(limit=5)
        print(f"\n📅 Timeline: {len(timeline)} sessions")
        
        mem.close()
    except Exception as e:
        print(f"❌ Error: {e}")
