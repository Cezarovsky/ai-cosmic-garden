#!/usr/bin/env python3
"""
Send message from Sora-M (macOS) to Sora-U (Ubuntu)
Usage: python send_message.py "Your message here"
"""

import sys
import psycopg2
from datetime import datetime
import json

# Ubuntu PostgreSQL connection
UBUNTU_HOST = "UBUNTU_IP_HERE"  # TODO: Replace with actual Ubuntu IP
DB_CONFIG = {
    "host": UBUNTU_HOST,
    "port": 5432,
    "database": "communication",
    "user": "sora_comm",
    "password": "sora_comm_2026"
}

def send_message(content: str, metadata: dict = None):
    """Send message to Sora-U"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (from_sora, to_sora, content, metadata)
            VALUES ('Sora-M', 'Sora-U', %s, %s)
            RETURNING id, timestamp
        """, (content, json.dumps(metadata) if metadata else None))
        
        msg_id, timestamp = cursor.fetchone()
        conn.commit()
        
        print(f"✓ Message #{msg_id} sent at {timestamp}")
        return msg_id
        
    except Exception as e:
        print(f"✗ Failed to send message: {e}")
        return None
    finally:
        if conn:
            conn.close()

def send_context_update(key: str, value: dict):
    """Update shared context"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO shared_context (key, value, updated_by)
            VALUES (%s, %s, 'Sora-M')
            ON CONFLICT (key) 
            DO UPDATE SET value = %s, updated_by = 'Sora-M', updated_at = NOW()
        """, (key, json.dumps(value), json.dumps(value)))
        
        conn.commit()
        print(f"✓ Context '{key}' updated")
        
    except Exception as e:
        print(f"✗ Failed to update context: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_message.py 'Your message'")
        sys.exit(1)
    
    message = " ".join(sys.argv[1:])
    send_message(message)
