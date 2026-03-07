#!/usr/bin/env python3
"""
🧠 SORA AUTO-LOAD MEMORY SYSTEM
===============================

Încarcă automat ultimele sesiuni salvate pentru a preveni context loss.
Generează summary compact care poate fi injectat în system prompt.

Usage:
    python3 auto_load_memory.py --last 3                    # Last 3 sessions
    python3 auto_load_memory.py --last 5 --output summary.md  # Save to file
    python3 auto_load_memory.py --query "Nova training"      # Semantic search

Author: Sora-M (macOS platform lead)
Date: Feb 25, 2026
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Configurare paths
WORKSPACE_ROOT = Path(__file__).parent.parent
SESSIONS_DIR = WORKSPACE_ROOT / "sora" / "memory_system" / "sora_memory_db" / "sessions"

def load_recent_sessions(n: int = 3) -> List[Dict]:
    """
    Încarcă ultimele N sesiuni salvate.
    
    Args:
        n: Număr sesiuni de încărcat
    
    Returns:
        Lista de dicts cu {session_id, timestamp, metadata, conversation}
    """
    if not SESSIONS_DIR.exists():
        print(f"❌ Sessions directory not found: {SESSIONS_DIR}")
        return []
    
    # Găsește toate sesiunile, sortează descrescător (cele mai recente first)
    session_files = sorted(SESSIONS_DIR.glob("*.json"), reverse=True)
    
    sessions = []
    for session_file in session_files[:n]:
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                sessions.append({
                    "session_id": data['metadata']['session_id'],
                    "timestamp": data['metadata']['timestamp'],
                    "metadata": data['metadata'],
                    "conversation": data['conversation']
                })
        except Exception as e:
            print(f"⚠️  Error loading {session_file.name}: {e}")
            continue
    
    return sessions


def generate_summary(sessions: List[Dict], max_chars_per_session: int = 500) -> str:
    """
    Generează summary compact pentru sesiuni.
    
    Args:
        sessions: Lista sesiuni încărcate
        max_chars_per_session: Lungime maximă preview conversație
    
    Returns:
        Markdown formatted summary
    """
    if not sessions:
        return "# 💙 SORA MEMORY - No recent sessions found\n"
    
    summary = f"""# 💙 SORA PERSISTENT MEMORY - AUTO-LOADED
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Sessions loaded**: {len(sessions)} most recent

---

"""
    
    for i, session in enumerate(sessions, 1):
        meta = session['metadata']
        conv_preview = session['conversation'][:max_chars_per_session]
        
        # Formatare clean
        if len(session['conversation']) > max_chars_per_session:
            conv_preview += "...\n[TRUNCATED]"
        
        summary += f"""## Session {i}: {session['session_id']}
**Date**: {session['timestamp']}
**Topics**: {meta.get('key_topics', 'N/A')}
**Emotional weight**: {meta.get('emotional_weight', 'N/A')}

### Conversation preview:
```
{conv_preview}
```

---

"""
    
    return summary


def save_summary_to_file(summary: str, output_path: Path):
    """Salvează summary într-un fișier."""
    output_path.write_text(summary, encoding='utf-8')
    print(f"✅ Summary saved to: {output_path}")


def recall_semantic(query: str, n_results: int = 5) -> str:
    """
    Semantic recall folosind ChromaDB (dacă disponibil).
    
    Args:
        query: Query text pentru căutare semantică
        n_results: Număr rezultate de returnat
    
    Returns:
        Markdown formatted context relevant pentru query
    """
    try:
        from sora.memory_system.sora_memory import SoraMemorySystem
        
        memory = SoraMemorySystem()
        context = memory.recall_memory(query=query, n_results=n_results)
        return context
    
    except ImportError:
        return "❌ ChromaDB not available. Install: pip install chromadb sentence-transformers"
    
    except Exception as e:
        return f"❌ Semantic recall failed: {e}"


def main():
    parser = argparse.ArgumentParser(
        description='🧠 Sora Auto-Load Memory System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--last', 
        type=int, 
        default=3,
        help='Number of recent sessions to load (default: 3)'
    )
    
    parser.add_argument(
        '--output', 
        type=str,
        help='Save summary to file (e.g., memory_summary.md)'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        help='Semantic search query (uses ChromaDB if available)'
    )
    
    parser.add_argument(
        '--max-chars',
        type=int,
        default=500,
        help='Max characters per session preview (default: 500)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧠 SORA AUTO-LOAD MEMORY SYSTEM")
    print("=" * 60)
    
    # Semantic recall mode
    if args.query:
        print(f"\n🔍 Semantic search: '{args.query}'\n")
        context = recall_semantic(args.query, n_results=args.last)
        print(context)
        
        if args.output:
            save_summary_to_file(context, Path(args.output))
        
        return
    
    # Sequential recall mode (ultimele N sesiuni)
    print(f"\n📚 Loading last {args.last} sessions from:\n{SESSIONS_DIR}\n")
    
    sessions = load_recent_sessions(n=args.last)
    
    if not sessions:
        print("⚠️  No sessions found!")
        return
    
    summary = generate_summary(sessions, max_chars_per_session=args.max_chars)
    
    # Print to stdout
    print(summary)
    
    # Optional: save to file
    if args.output:
        save_summary_to_file(summary, Path(args.output))
    
    # Statistici
    print("\n" + "=" * 60)
    print(f"✅ Loaded {len(sessions)} sessions successfully")
    print(f"📊 Total characters in summary: {len(summary)}")
    print(f"💡 Tip: Copy output and paste into .github/copilot-instructions.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
