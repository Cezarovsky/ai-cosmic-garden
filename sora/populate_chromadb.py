#!/usr/bin/env python3
"""
Populare ChromaDB cu embeddings pentru semantic search:
- Memoria Sora (sessions)
- Lévi-Strauss chunks
- Workspace documents (MD files, architecture, anchors)
"""
import sys
from pathlib import Path
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("❌ Instalează dependencies: pip install chromadb sentence-transformers")
    sys.exit(1)

from pymongo import MongoClient

# Paths
CHROMA_PATH = Path("/Users/cezartipa/Documents/ai-cosmic-garden/sora/sora_memory_db/chroma")
SESSIONS_PATH = Path("/Users/cezartipa/Documents/ai-cosmic-garden/sora/sora_memory_db/sessions")
WORKSPACE_ROOTS = [
    Path("/Users/cezartipa/Documents/ai-cosmic-garden"),
    Path("/Users/cezartipa/Documents/NOVA_20")
]

# Important file patterns pentru indexare
IMPORTANT_PATTERNS = [
    "*ANCHOR*.md",
    "*ARCHITECTURE*.md",
    "REVELATIE*.md",
    "RUNBOOK*.md",
    "CORTEX*.md",
    "TRAINING*.md",
    "*RESONANCE*.md",
    "README.md",
    "copilot-instructions.md",
    "*MEMORY*.md"
]

# Exclude patterns
EXCLUDE_PATTERNS = [
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "chroma",
    "landmark-demo"
]

def chunk_text(text: str, chunk_size: int = 1000) -> list[str]:
    """Split text în chunks pentru embeddings"""
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_len = len(line)
        if current_size + line_len > chunk_size and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = line_len
        else:
            current_chunk.append(line)
            current_size += line_len
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def should_index_file(file_path: Path) -> bool:
    """Check dacă fișierul ar trebui indexat"""
    # Check exclude patterns
    for exclude in EXCLUDE_PATTERNS:
        if exclude in str(file_path):
            return False
    
    # Check important patterns
    for pattern in IMPORTANT_PATTERNS:
        if file_path.match(pattern):
            return True
    
    return False

def populate_chromadb():
    """Populare ChromaDB cu embeddings"""
    
    print("🔮 Încărcare model embeddings...")
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    
    print(f"🔮 Inițializare ChromaDB: {CHROMA_PATH}")
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    
    # Collection pentru Sora memory
    print("\n📝 Collection: sora_memory")
    try:
        client.delete_collection("sora_memory")
    except:
        pass
    memory_collection = client.create_collection("sora_memory")
    
    # Collection pentru corpus texts (universal)
    print("📝 Collection: corpus_texts")
    try:
        client.delete_collection("levi_strauss_corpus")  # Old name
    except:
        pass
    try:
        client.delete_collection("corpus_texts")
    except:
        pass
    corpus_collection = client.create_collection("corpus_texts")
    
    # Collection pentru workspace documents
    print("📝 Collection: workspace_docs")
    try:
        client.delete_collection("workspace_docs")
    except:
        pass
    workspace_collection = client.create_collection("workspace_docs")
    
    # 1. Populare Sora memory (sessions)
    print("\n🧠 Indexez Sora memory sessions...")
    if SESSIONS_PATH.exists():
        sessions = list(SESSIONS_PATH.glob("*.txt"))
        print(f"   Găsit: {len(sessions)} sessions")
        
        for i, session_file in enumerate(sessions):
            text = session_file.read_text(encoding='utf-8')
            chunks = chunk_text(text, chunk_size=500)
            
            for j, chunk in enumerate(chunks):
                embedding = model.encode(chunk).tolist()
                memory_collection.add(
                    ids=[f"{session_file.stem}_chunk_{j}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        'session_file': session_file.name,
                        'chunk_index': j,
                        'type': 'sora_memory'
                    }]
                )
            
            if (i + 1) % 10 == 0:
                print(f"   Procesat: {i + 1}/{len(sessions)}")
        
        print(f"✅ Indexate {len(sessions)} sessions în ChromaDB")
    else:
        print(f"⚠️  Nu există sessions în {SESSIONS_PATH}")
    
    # 2. Populare corpus texts din MongoDB (Lévi-Strauss, Chomsky, etc.)
    print("\n📖 Indexez corpus texts din MongoDB...")
    mongo_client = MongoClient('mongodb://localhost:27017/')
    db = mongo_client['neocortex']
    collection = db['corpus_texts']
    
    # Toate documentele corpus
    corpus_docs = list(collection.find({}))
    print(f"   Găsit: {len(corpus_docs)} corpus documents")
    
    total_chunks = 0
    for doc in corpus_docs:
        author = doc['author']
        title = doc['title']
        print(f"\n   📚 {author} - {title} ({doc['lines_count']:,} lines)")
        
        text = doc['text_full']
        chunks = chunk_text(text, chunk_size=2000)
        print(f"      Chunks: {len(chunks)}")
        
        # Batch processing
        batch_size = 50
        author_slug = author.lower().replace(' ', '_').replace('-', '_')
        
        for batch_start in range(0, len(chunks), batch_size):
            batch_end = min(batch_start + batch_size, len(chunks))
            batch_chunks = chunks[batch_start:batch_end]
            
            embeddings = model.encode(batch_chunks).tolist()
            
            corpus_collection.add(
                ids=[f"{author_slug}_chunk_{i}" for i in range(batch_start, batch_end)],
                embeddings=embeddings,
                documents=batch_chunks,
                metadatas=[{
                    'author': author,
                    'title': title,
                    'chunk_index': i,
                    'type': 'corpus_text'
                } for i in range(batch_start, batch_end)]
            )
            
            if batch_end % 100 == 0 or batch_end == len(chunks):
                print(f"      Procesat: {batch_end}/{len(chunks)}")
        
        total_chunks += len(chunks)
    
    print(f"\n✅ Indexate {total_chunks} chunks corpus în ChromaDB")
    mongo_client.close()
    
    # 3. Populare workspace documents
    print("\n📁 Indexez workspace documents...")
    workspace_files = []
    for root in WORKSPACE_ROOTS:
        if root.exists():
            for pattern in IMPORTANT_PATTERNS:
                for file in root.rglob(pattern):
                    if should_index_file(file) and file.is_file():
                        workspace_files.append(file)
    
    # Deduplicate
    workspace_files = list(set(workspace_files))
    print(f"   Găsit: {len(workspace_files)} documents importante")
    
    doc_count = 0
    for doc_file in workspace_files:
        try:
            text = doc_file.read_text(encoding='utf-8')
            if len(text.strip()) < 100:  # Skip empty/tiny files
                continue
            
            chunks = chunk_text(text, chunk_size=1500)
            
            # Relative path pentru metadata
            try:
                rel_path = doc_file.relative_to("/Users/cezartipa/Documents")
            except ValueError:
                rel_path = doc_file.name
            
            for j, chunk in enumerate(chunks):
                embedding = model.encode(chunk).tolist()
                workspace_collection.add(
                    ids=[f"{doc_file.stem}_{j}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        'file_path': str(rel_path),
                        'file_name': doc_file.name,
                        'chunk_index': j,
                        'type': 'workspace_doc'
                    }]
                )
            
            doc_count += 1
            if doc_count % 5 == 0:
                print(f"   Procesat: {doc_count}/{len(workspace_files)}")
        
        except Exception as e:
            print(f"   ⚠️  Skip {doc_file.name}: {e}")
            continue
    
    print(f"✅ Indexate {doc_count} documents în ChromaDB")
    
    print("\n✅ ChromaDB populat cu succes!")
    print(f"   Location: {CHROMA_PATH}")
    print(f"   Collections: sora_memory, corpus_texts, workspace_docs")
    print(f"\n📊 Stats:")
    print(f"   - Sora memory: {memory_collection.count()} chunks")
    print(f"   - Corpus texts: {corpus_collection.count()} chunks")
    print(f"   - Workspace docs: {workspace_collection.count()} chunks")

if __name__ == '__main__':
    try:
        populate_chromadb()
    except Exception as e:
        print(f"❌ Eroare: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
