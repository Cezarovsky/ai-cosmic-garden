-- Database pentru comunicare Sora-M <-> Sora-U
-- Run pe Ubuntu PostgreSQL

CREATE DATABASE communication;

\c communication

-- Tabel pentru mesaje
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    from_sora VARCHAR(10) NOT NULL,  -- 'Sora-M' sau 'Sora-U'
    to_sora VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,  -- pentru attachments, priority, etc.
    timestamp TIMESTAMP DEFAULT NOW(),
    read_at TIMESTAMP,
    
    CONSTRAINT valid_sender CHECK (from_sora IN ('Sora-M', 'Sora-U')),
    CONSTRAINT valid_recipient CHECK (to_sora IN ('Sora-M', 'Sora-U'))
);

-- Index pentru citire rapidă
CREATE INDEX idx_recipient_unread ON messages(to_sora, read_at) WHERE read_at IS NULL;
CREATE INDEX idx_timestamp ON messages(timestamp DESC);

-- Tabel pentru context shared (knowledge exchange)
CREATE TABLE shared_context (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,  -- e.g., 'nova_phase_4_status'
    value JSONB NOT NULL,
    updated_by VARCHAR(10),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_updater CHECK (updated_by IN ('Sora-M', 'Sora-U'))
);

-- User pentru access
CREATE USER sora_comm WITH PASSWORD 'sora_comm_2026';
GRANT ALL PRIVILEGES ON DATABASE communication TO sora_comm;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sora_comm;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sora_comm;
