#!/usr/bin/env python3
"""
Read messages for Sora-U (Ubuntu) or Sora-M (macOS)
Usage: 
  python read_messages.py          # Read unread messages
  python read_messages.py --all    # Read all recent messages
  python read_messages.py --from Sora-M  # Filter by sender
"""

import sys
import psycopg2
from datetime import datetime
import json

# Detect platform
import platform
PLATFORM = "Sora-M" if platform.system() == "Darwin" else "Sora-U"

# Connection config
if PLATFORM == "Sora-M":
    UBUNTU_HOST = "UBUNTU_IP_HERE"  # TODO: Replace
    DB_CONFIG = {
        "host": UBUNTU_HOST,
        "port": 5432,
        "database": "communication",
        "user": "sora_comm",
        "password": "sora_comm_2026"
    }
else:  # Sora-U on Ubuntu
    DB_CONFIG = {
        "host": "localhost",
        "port": 5432,
        "database": "communication",
        "user": "sora_comm",
        "password": "sora_comm_2026"
    }

def read_messages(show_all=False, from_filter=None, mark_read=True):
    """Read messages for current Sora instance"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Build query
        query = """
            SELECT id, from_sora, content, metadata, timestamp, read_at
            FROM messages
            WHERE to_sora = %s
        """
        params = [PLATFORM]
        
        if not show_all:
            query += " AND read_at IS NULL"
        
        if from_filter:
            query += " AND from_sora = %s"
            params.append(from_filter)
        
        query += " ORDER BY timestamp DESC LIMIT 50"
        
        cursor.execute(query, params)
        messages = cursor.fetchall()
        
        if not messages:
            print(f"No {'unread ' if not show_all else ''}messages for {PLATFORM}")
            return
        
        print(f"\n{'='*70}")
        print(f"Messages for {PLATFORM} ({len(messages)} total)")
        print(f"{'='*70}\n")
        
        message_ids = []
        for msg in messages:
            msg_id, from_sora, content, metadata, timestamp, read_at = msg
            message_ids.append(msg_id)
            
            status = "✓ READ" if read_at else "• UNREAD"
            print(f"[{status}] #{msg_id} from {from_sora} at {timestamp}")
            print(f"    {content}")
            if metadata:
                print(f"    Metadata: {metadata}")
            print()
        
        # Mark as read
        if mark_read and message_ids:
            cursor.execute("""
                UPDATE messages 
                SET read_at = NOW() 
                WHERE id = ANY(%s) AND read_at IS NULL
            """, (message_ids,))
            conn.commit()
            print(f"✓ Marked {cursor.rowcount} messages as read")
        
    except Exception as e:
        print(f"✗ Failed to read messages: {e}")
    finally:
        if conn:
            conn.close()

def read_shared_context(key=None):
    """Read shared context"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        if key:
            cursor.execute("""
                SELECT key, value, updated_by, updated_at
                FROM shared_context
                WHERE key = %s
            """, (key,))
        else:
            cursor.execute("""
                SELECT key, value, updated_by, updated_at
                FROM shared_context
                ORDER BY updated_at DESC
                LIMIT 20
            """)
        
        contexts = cursor.fetchall()
        
        if not contexts:
            print("No shared context found")
            return
        
        print(f"\n{'='*70}")
        print(f"Shared Context")
        print(f"{'='*70}\n")
        
        for ctx in contexts:
            key, value, updated_by, updated_at = ctx
            print(f"{key} (by {updated_by} at {updated_at})")
            print(f"  {json.dumps(value, indent=2)}\n")
        
    except Exception as e:
        print(f"✗ Failed to read context: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    args = sys.argv[1:]
    
    show_all = "--all" in args
    from_filter = None
    
    if "--from" in args:
        idx = args.index("--from")
        if idx + 1 < len(args):
            from_filter = args[idx + 1]
    
    if "--context" in args:
        key = args[args.index("--context") + 1] if args.index("--context") + 1 < len(args) else None
        read_shared_context(key)
    else:
        read_messages(show_all=show_all, from_filter=from_filter)
