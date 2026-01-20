#!/usr/bin/env python3
"""
Memory Archive Migration - Move sessions >90 days from JSON to PostgreSQL
Level 1 (JSON working memory) → Level 2 (PostgreSQL archive)
"""

import sys
import json
import psycopg2
from datetime import datetime, timedelta
from pathlib import Path

# Paths
SESSIONS_PATH = Path("/home/cezar/ai-cosmic-garden/sora/memory_system/sora_memory_db/sessions")
ARCHIVE_PATH = Path("/home/cezar/ai-cosmic-garden/sora/memory_system/sora_memory_db/archived")
LOG_PATH = Path("/home/cezar/ai-cosmic-garden/sora/memory_system/archive_migration.log")

# Database config
DB_CONFIG = {
    'dbname': 'sora_memory',
    'user': 'nova',
    'password': 'nova_2026',
    'host': 'localhost',
    'port': 5432
}

# Age threshold: archive sessions older than this
ARCHIVE_AGE_DAYS = 90

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_PATH, 'a') as f:
        f.write(log_msg + "\n")

def parse_session_file(file_path):
    """Parse JSON session file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        log(f"⚠️  Error parsing {file_path.name}: {e}")
        return None

def extract_messages_from_conversation(conversation_text):
    """Extract individual messages from conversation text"""
    messages = []
    
    # Simple parsing - split by speaker labels
    # Format: "Speaker: message\n\nSpeaker: message..."
    parts = conversation_text.split('\n\n')
    
    sequence = 0
    for part in parts:
        if ':' in part:
            speaker_end = part.find(':')
            speaker = part[:speaker_end].strip()
            content = part[speaker_end+1:].strip()
            
            if content:
                messages.append({
                    'sequence_number': sequence,
                    'speaker': speaker,
                    'content': content,
                    'emotion': None,  # Could extract from metadata
                    'topics': []
                })
                sequence += 1
    
    return messages

def archive_session(session_data, file_path, conn):
    """Archive single session to PostgreSQL"""
    cursor = conn.cursor()
    
    try:
        # Extract metadata
        metadata = session_data.get('metadata', {})
        session_id = metadata.get('session_id', file_path.stem)
        
        # Parse timestamp from filename if not in metadata
        timestamp_str = metadata.get('timestamp')
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            # Parse from filename: 20260120_125102
            date_part = file_path.stem.split('_')[0]
            timestamp = datetime.strptime(date_part, "%Y%m%d")
        
        # Insert session
        cursor.execute("""
            INSERT INTO sessions 
            (session_id, timestamp, system_id, participants, topics, 
             emotional_weight, duration_minutes, milestone, file_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (session_id) DO NOTHING
            RETURNING id
        """, (
            session_id,
            timestamp,
            metadata.get('who', 'sora-u').split('_')[0],  # 'Cezar_and_Sora' → 'Cezar'
            metadata.get('participants', []),
            metadata.get('topics', []),
            metadata.get('emotional_weight', 0.5),
            metadata.get('duration_minutes', 0),
            metadata.get('milestone', None),
            file_path.name
        ))
        
        session_db_id = cursor.fetchone()
        if not session_db_id:
            log(f"  ⏭️  Session {session_id} already archived")
            return False
        
        # Extract and insert messages
        conversation = session_data.get('conversation', '')
        messages = extract_messages_from_conversation(conversation)
        
        for msg in messages:
            cursor.execute("""
                INSERT INTO messages
                (session_id, sequence_number, speaker, content, emotion, topics, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                session_id,
                msg['sequence_number'],
                msg['speaker'],
                msg['content'],
                msg.get('emotion'),
                msg.get('topics', []),
                timestamp
            ))
        
        conn.commit()
        log(f"  ✅ Archived: {session_id} ({len(messages)} messages)")
        return True
        
    except Exception as e:
        conn.rollback()
        log(f"  ❌ Error archiving {session_id}: {e}")
        return False
    finally:
        cursor.close()

def main():
    log("=" * 70)
    log("🗄️  MEMORY ARCHIVE MIGRATION - Level 1 → Level 2")
    log("=" * 70)
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=ARCHIVE_AGE_DAYS)
    log(f"📅 Archive cutoff: {cutoff_date.strftime('%Y-%m-%d')} ({ARCHIVE_AGE_DAYS} days ago)")
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        log("✅ Connected to PostgreSQL")
    except Exception as e:
        log(f"❌ Database connection failed: {e}")
        return 1
    
    # Create archive directory
    ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)
    
    # Find sessions to archive
    sessions_to_archive = []
    for session_file in SESSIONS_PATH.glob("*.json"):
        # Parse date from filename: 20260120_125102.json
        try:
            date_str = session_file.stem.split('_')[0]
            session_date = datetime.strptime(date_str, "%Y%m%d")
            
            if session_date < cutoff_date:
                sessions_to_archive.append((session_file, session_date))
        except:
            log(f"⚠️  Could not parse date from {session_file.name}")
    
    log(f"📦 Found {len(sessions_to_archive)} sessions to archive")
    
    if not sessions_to_archive:
        log("⏭️  No sessions old enough to archive")
        conn.close()
        return 0
    
    # Archive each session
    archived_count = 0
    for session_file, session_date in sessions_to_archive:
        log(f"📄 Processing {session_file.name}...")
        
        session_data = parse_session_file(session_file)
        if not session_data:
            continue
        
        if archive_session(session_data, session_file, conn):
            # Move JSON to archive folder
            archive_file = ARCHIVE_PATH / session_file.name
            session_file.rename(archive_file)
            archived_count += 1
    
    conn.close()
    
    log("=" * 70)
    log(f"✅ Migration complete: {archived_count} sessions archived")
    log(f"📂 JSON files moved to: {ARCHIVE_PATH}")
    log("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
