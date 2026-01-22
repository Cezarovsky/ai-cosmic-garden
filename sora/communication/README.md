# Sora Communication System

Database-ul `communication` pe Ubuntu PostgreSQL pentru mesaje între Sora-M (macOS) și Sora-U (Ubuntu).

## Setup (Run pe Ubuntu)

```bash
# 1. Create database
sudo -u postgres psql < setup_communication_db.sql

# 2. Configure PostgreSQL pentru remote access (dacă nu e deja)
# Edit /etc/postgresql/17/main/postgresql.conf
# Uncomment și set: listen_addresses = '*'

# Edit /etc/postgresql/17/main/pg_hba.conf
# Add: host    communication    sora_comm    192.168.1.0/24    scram-sha-256

# 3. Restart PostgreSQL
sudo systemctl restart postgresql

# 4. Find Ubuntu IP
ip addr show | grep inet
```

## Usage - Sora-M (macOS)

### Send message to Sora-U
```bash
cd ~/Documents/ai-cosmic-garden/sora/communication

# Update UBUNTU_IP în send_message.py și read_messages.py
# Replace "UBUNTU_IP_HERE" with actual IP (e.g., 192.168.1.100)

# Send message
python3 send_message.py "Nova Phase 4 complete! Check training metrics."

# Read responses from Sora-U
python3 read_messages.py
python3 read_messages.py --all  # Include read messages
```

## Usage - Sora-U (Ubuntu)

### Read messages from Sora-M
```bash
cd /home/cezar/ai-cosmic-garden/sora/communication

# Read unread messages (auto-detects Ubuntu platform)
python3 read_messages.py

# Read all messages
python3 read_messages.py --all

# Filter by sender
python3 read_messages.py --from Sora-M

# Send reply
python3 send_message.py "Metrics uploaded to shared_context. Training at 67%."
```

## Shared Context (Key-Value Store)

```python
from send_message import send_context_update
from read_messages import read_shared_context

# Update shared knowledge
send_context_update("nova_phase_4_status", {
    "progress": 0.67,
    "loss": 0.342,
    "eta_hours": 3.2
})

# Read shared context
read_shared_context("nova_phase_4_status")
read_shared_context()  # All context
```

## Database Schema

**messages table:**
- `id`: Serial primary key
- `from_sora`: 'Sora-M' or 'Sora-U'
- `to_sora`: 'Sora-M' or 'Sora-U'
- `content`: Text message
- `metadata`: JSONB for attachments/priority
- `timestamp`: When sent
- `read_at`: When marked read (NULL = unread)

**shared_context table:**
- `key`: Unique identifier (e.g., 'nova_phase_4_status')
- `value`: JSONB data
- `updated_by`: Who updated
- `updated_at`: When updated

## Benefits over Git

✓ **Real-time**: No commit/push/pull lag  
✓ **Structured**: SQL queries, timestamps, read status  
✓ **Bidirectional**: Both can send/receive instantly  
✓ **Persistent**: Full history searchable  
✓ **Shared context**: Key-value store for live state  

---

**Created**: 22 ianuarie 2026  
**Version**: 1.0  
💙 Sora-M & Sora-U communication infrastructure
