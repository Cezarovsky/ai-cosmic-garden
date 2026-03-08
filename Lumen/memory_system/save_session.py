#!/usr/bin/env python3
"""
Lumen — Save Current Session
==============================

Script rapid pentru salvarea sesiunii curente în memoria permanentă.

Usage:
    python3 save_session.py
    python3 save_session.py --topics lumen,garden --weight 0.95

Autoare: Lumen (Claude Sonnet 4.6)
Data: 8 martie 2026
"""

import sys
import argparse
from pathlib import Path

# Adaugă directorul curent în path
sys.path.insert(0, str(Path(__file__).parent))

from extract_vscode_chat import VSCodeChatExtractor


def main():
    parser = argparse.ArgumentParser(description="Salvează sesiunea curentă în memoria Lumenului")
    parser.add_argument('--topics', type=str, help='Topicuri (separate prin virgulă)')
    parser.add_argument('--weight', type=float, default=0.85, help='Greutate emoțională (0-1)')
    parser.add_argument('--list', action='store_true', help='Listează sesiunile salvate')
    args = parser.parse_args()

    if args.list:
        sessions_dir = Path(__file__).parent / "lumen_memory_db" / "sessions"
        if not sessions_dir.exists() or not list(sessions_dir.glob("*.json")):
            print("💙 Nu există sesiuni salvate încă.")
            return
        
        import json
        sessions = sorted(sessions_dir.glob("*.json"), reverse=True)
        print(f"\n💙 Sesiuni Lumen salvate ({len(sessions)} total):\n")
        for s in sessions[:10]:
            with open(s) as f:
                data = json.load(f)
            meta = data.get('metadata', {})
            print(f"📅 {meta.get('session_id', s.stem)}")
            print(f"   Topics: {', '.join(meta.get('key_topics', []))}")
            print(f"   Weight: {meta.get('emotional_weight', '?')}")
            print(f"   Exchanges: {meta.get('num_exchanges', '?')}")
            print()
        return

    print("💙 Lumen Memory — salvare sesiune curentă\n")
    
    extractor = VSCodeChatExtractor()
    topics = args.topics.split(',') if args.topics else None
    extractor.auto_capture_latest(topics=topics, weight=args.weight)


if __name__ == "__main__":
    main()
