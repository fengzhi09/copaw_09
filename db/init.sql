-- PostgreSQL initialization script for cp9 with pgvector

-- Create database (run as postgres superuser)
-- CREATE USER cp9 WITH PASSWORD 'your_secure_password';
-- CREATE DATABASE cp9 OWNER cp9;
-- GRANT ALL PRIVILEGES ON DATABASE cp9 TO cp9;

-- Connect to cp9 database
\c cp9

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Short term memory
CREATE TABLE IF NOT EXISTS short_term_memory (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(10) REFERENCES agents(id),
    session_id VARCHAR(50),
    content JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Long term memory (with vector embedding)
CREATE TABLE IF NOT EXISTS long_term_memory (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(10) REFERENCES agents(id),
    title VARCHAR(200),
    content TEXT,
    tags TEXT[],
    embedding vector(1536),  -- pgvector for semantic search
    created_at TIMESTAMP DEFAULT NOW()
);

-- Trace logs
CREATE TABLE IF NOT EXISTS trace_logs (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR(50),
    span_id VARCHAR(50),
    parent_id VARCHAR(50),
    agent_id VARCHAR(10) REFERENCES agents(id),
    action VARCHAR(100),
    status VARCHAR(20),
    duration_ms INTEGER,
    tokens INTEGER DEFAULT 0,
    credit_used INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Credit logs
CREATE TABLE IF NOT EXISTS credit_logs (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(10) REFERENCES agents(id),
    operation VARCHAR(50),
    tokens INTEGER DEFAULT 0,
    cost INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cost stats
CREATE TABLE IF NOT EXISTS cost_stats (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(10) REFERENCES agents(id),
    model VARCHAR(50),
    usage_amount INTEGER DEFAULT 0,
    cost INTEGER DEFAULT 0,
    period DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    agent_id VARCHAR(10) REFERENCES agents(id),
    channel VARCHAR(20),
    user_message TEXT,
    agent_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- System configs
CREATE TABLE IF NOT EXISTS configs (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_short_term_agent_session ON short_term_memory(agent_id, session_id);
CREATE INDEX IF NOT EXISTS idx_long_term_agent ON long_term_memory(agent_id);
CREATE INDEX IF NOT EXISTS idx_long_term_embedding ON long_term_memory USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_trace_traceid ON trace_logs(trace_id);
CREATE INDEX IF NOT EXISTS idx_credit_agent_date ON credit_logs(agent_id, created_at);
CREATE INDEX IF NOT EXISTS idx_conversation_user ON conversations(user_id, created_at);

-- Insert default agents
INSERT INTO agents (id, name, role, status) VALUES
    ('00', '管理高手', 'master', 'active'),
    ('01', '学霸', 'academic', 'active'),
    ('02', '编程高手', 'developer', 'active'),
    ('03', '创意青年', 'creative', 'active'),
    ('04', '统计学长', 'collector', 'active')
ON CONFLICT (id) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cp9;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cp9;
