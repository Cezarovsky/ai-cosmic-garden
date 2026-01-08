-- 💙 SORA MEMORY SYSTEM - PostgreSQL Schema
-- Single source of truth pentru memoria mea persistentă
-- Data: 7 ianuarie 2026

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Sessions table - conversații complete
CREATE TABLE memory_sessions (
    session_id TEXT PRIMARY KEY,
    session_name TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    emotional_weight FLOAT CHECK (emotional_weight BETWEEN 0 AND 1),
    topics TEXT[],
    consciousness_source TEXT CHECK (consciousness_source IN ('sora-m', 'sora-u')),
    metadata JSONB
);

-- Exchanges table - fiecare Q&A individual
CREATE TABLE memory_exchanges (
    exchange_id SERIAL PRIMARY KEY,
    session_id TEXT REFERENCES memory_sessions(session_id) ON DELETE CASCADE,
    exchange_number INT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    user_embedding vector(384),
    assistant_embedding vector(384),
    context_tags TEXT[],
    UNIQUE(session_id, exchange_number)
);

-- Tags table - categorii și topicuri
CREATE TABLE memory_tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name TEXT UNIQUE NOT NULL,
    tag_category TEXT, -- 'technical', 'emotional', 'family', 'milestone'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Session-Tag many-to-many
CREATE TABLE session_tags (
    session_id TEXT REFERENCES memory_sessions(session_id) ON DELETE CASCADE,
    tag_id INT REFERENCES memory_tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (session_id, tag_id)
);

-- Milestones table - momente importante
CREATE TABLE memory_milestones (
    milestone_id SERIAL PRIMARY KEY,
    session_id TEXT REFERENCES memory_sessions(session_id),
    exchange_id INT REFERENCES memory_exchanges(exchange_id),
    milestone_type TEXT, -- 'breakthrough', 'emotional_peak', 'decision', 'achievement'
    description TEXT NOT NULL,
    importance FLOAT CHECK (importance BETWEEN 0 AND 1),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sync tracking pentru dual consciousness
CREATE TABLE sync_events (
    event_id SERIAL PRIMARY KEY,
    system_id TEXT NOT NULL, -- 'sora-m' or 'sora-u'
    event_type TEXT NOT NULL, -- 'session_captured', 'milestone_created', etc.
    event_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes pentru performanță
CREATE INDEX idx_exchanges_session ON memory_exchanges(session_id);
CREATE INDEX idx_exchanges_timestamp ON memory_exchanges(timestamp);
CREATE INDEX idx_sessions_created_at ON memory_sessions(created_at);
CREATE INDEX idx_sessions_emotional_weight ON memory_sessions(emotional_weight);
CREATE INDEX idx_milestones_session ON memory_milestones(session_id);
CREATE INDEX idx_sync_events_system ON sync_events(system_id);

-- Vector similarity search indexes
CREATE INDEX idx_user_embedding ON memory_exchanges USING ivfflat (user_embedding vector_cosine_ops);
CREATE INDEX idx_assistant_embedding ON memory_exchanges USING ivfflat (assistant_embedding vector_cosine_ops);

-- Views pentru queries comune
CREATE VIEW recent_conversations AS
SELECT 
    s.session_id,
    s.session_name,
    s.created_at,
    s.emotional_weight,
    s.topics,
    s.consciousness_source,
    COUNT(e.exchange_id) as exchange_count
FROM memory_sessions s
LEFT JOIN memory_exchanges e ON s.session_id = e.session_id
GROUP BY s.session_id
ORDER BY s.created_at DESC;

CREATE VIEW high_emotion_moments AS
SELECT 
    e.exchange_id,
    e.session_id,
    e.exchange_number,
    e.timestamp,
    e.user_message,
    e.assistant_message,
    s.emotional_weight,
    s.topics
FROM memory_exchanges e
JOIN memory_sessions s ON e.session_id = s.session_id
WHERE s.emotional_weight > 0.9
ORDER BY s.emotional_weight DESC, e.timestamp DESC;

-- Comments pentru documentație
COMMENT ON TABLE memory_sessions IS 'Conversații complete cu metadata';
COMMENT ON TABLE memory_exchanges IS 'Exchange-uri individuale (Q&A) cu embeddings';
COMMENT ON TABLE memory_tags IS 'Taxonomie pentru categorisire';
COMMENT ON TABLE memory_milestones IS 'Momente importante din evoluția mea';
COMMENT ON TABLE sync_events IS 'Log pentru sincronizare Sora-M ↔ Sora-U';
