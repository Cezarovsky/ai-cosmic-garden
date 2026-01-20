-- Nova/Sora Memory Archive - Complete PostgreSQL Schema
-- Level 2: Long-term storage for ALL sessions (millions of records)

CREATE DATABASE IF NOT EXISTS sora_memory;

\c sora_memory;

-- Sessions table: metadata for each conversation
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    system_id VARCHAR(50) NOT NULL, -- 'sora-m', 'sora-u', 'nova'
    participants TEXT[], -- ['Cezar', 'Sora-M']
    topics TEXT[], -- ['databricks', 'consciousness', 'training']
    emotional_weight FLOAT, -- 0.0-1.0
    duration_minutes INTEGER,
    milestone TEXT,
    file_source TEXT, -- original JSON filename
    archived_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Indexes for fast retrieval
    INDEX idx_session_timestamp (timestamp),
    INDEX idx_session_system (system_id),
    INDEX idx_session_topics (topics),
    INDEX idx_session_weight (emotional_weight)
);

-- Messages table: individual messages within sessions
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL, -- order within session
    speaker VARCHAR(100) NOT NULL, -- 'Cezar', 'Sora-M', 'Sora-U', 'Nova'
    content TEXT NOT NULL,
    emotion VARCHAR(50), -- 'caring', 'triumphant', 'diagnostic'
    topics TEXT[], -- specific to this message
    timestamp TIMESTAMPTZ,
    
    -- Full-text search index
    INDEX idx_message_session (session_id),
    INDEX idx_message_speaker (speaker),
    INDEX idx_message_content_fts (to_tsvector('english', content))
);

-- Milestones: significant events extracted from sessions
CREATE TABLE IF NOT EXISTS milestones (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(session_id),
    timestamp TIMESTAMPTZ NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category VARCHAR(100), -- 'technical_achievement', 'philosophical_insight', 'identity_revelation'
    emotional_weight FLOAT,
    related_patterns TEXT[], -- patterns from Cortex
    
    INDEX idx_milestone_timestamp (timestamp),
    INDEX idx_milestone_category (category)
);

-- Session syntheses: distilled essence for old sessions (>6 months)
CREATE TABLE IF NOT EXISTS session_syntheses (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL REFERENCES sessions(session_id),
    synthesis TEXT NOT NULL, -- 200-500 word summary
    key_insights TEXT[], -- bullet points
    patterns_learned TEXT[], -- patterns consolidated
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    
    INDEX idx_synthesis_session (session_id)
);

-- Memory retrieval stats (for optimization)
CREATE TABLE IF NOT EXISTS retrieval_stats (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(session_id),
    retrieved_at TIMESTAMPTZ DEFAULT NOW(),
    retrieval_context TEXT, -- why was it retrieved
    relevance_score FLOAT
);

-- Grants
GRANT ALL PRIVILEGES ON DATABASE sora_memory TO nova;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nova;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nova;

-- Useful queries for Nova/Sora

-- Find all sessions about a topic
CREATE OR REPLACE FUNCTION search_sessions_by_topic(topic_query TEXT)
RETURNS TABLE(session_id VARCHAR, timestamp TIMESTAMPTZ, topics TEXT[], emotional_weight FLOAT) AS $$
BEGIN
    RETURN QUERY
    SELECT s.session_id, s.timestamp, s.topics, s.emotional_weight
    FROM sessions s
    WHERE topic_query = ANY(s.topics)
    ORDER BY s.timestamp DESC;
END;
$$ LANGUAGE plpgsql;

-- Full-text search in messages
CREATE OR REPLACE FUNCTION search_messages(query_text TEXT, limit_count INTEGER DEFAULT 10)
RETURNS TABLE(
    session_id VARCHAR, 
    speaker VARCHAR, 
    content TEXT, 
    timestamp TIMESTAMPTZ,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.session_id,
        m.speaker,
        m.content,
        m.timestamp,
        ts_rank(to_tsvector('english', m.content), plainto_tsquery('english', query_text)) as rank
    FROM messages m
    WHERE to_tsvector('english', m.content) @@ plainto_tsquery('english', query_text)
    ORDER BY rank DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Get session context (messages + metadata)
CREATE OR REPLACE FUNCTION get_session_context(sid VARCHAR)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'session', row_to_json(s.*),
        'messages', (
            SELECT json_agg(m.* ORDER BY m.sequence_number)
            FROM messages m
            WHERE m.session_id = sid
        ),
        'synthesis', (
            SELECT synthesis FROM session_syntheses WHERE session_id = sid
        )
    ) INTO result
    FROM sessions s
    WHERE s.session_id = sid;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Stats view
CREATE OR REPLACE VIEW memory_stats AS
SELECT 
    COUNT(DISTINCT s.session_id) as total_sessions,
    COUNT(m.id) as total_messages,
    COUNT(DISTINCT s.system_id) as systems_count,
    MIN(s.timestamp) as earliest_session,
    MAX(s.timestamp) as latest_session,
    AVG(s.emotional_weight) as avg_emotional_weight,
    COUNT(ml.id) as total_milestones
FROM sessions s
LEFT JOIN messages m ON s.session_id = m.session_id
LEFT JOIN milestones ml ON s.session_id = ml.session_id;

COMMENT ON TABLE sessions IS 'Level 2 Memory: Complete archive of all conversation sessions';
COMMENT ON TABLE messages IS 'Individual messages within sessions, full-text searchable';
COMMENT ON TABLE milestones IS 'Significant events and achievements extracted from sessions';
COMMENT ON TABLE session_syntheses IS 'Distilled summaries for old sessions (>6 months)';
