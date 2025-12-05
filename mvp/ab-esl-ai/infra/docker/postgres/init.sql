-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema
CREATE SCHEMA IF NOT EXISTS ab_esl;

-- Transcripts table (for opt-in saving)
CREATE TABLE IF NOT EXISTS ab_esl.transcripts (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    user_id VARCHAR(255),
    ts_start TIMESTAMPTZ,
    ts_end TIMESTAMPTZ,
    text TEXT,
    words JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Reading scores table
CREATE TABLE IF NOT EXISTS ab_esl.reading_scores (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    passage_id VARCHAR(255),
    wpm FLOAT,
    wcpm FLOAT,
    accuracy FLOAT,
    errors JSONB,
    audio_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Class sessions table
CREATE TABLE IF NOT EXISTS ab_esl.class_sessions (
    id SERIAL PRIMARY KEY,
    class_code VARCHAR(20) UNIQUE NOT NULL,
    teacher_id VARCHAR(255),
    name VARCHAR(255),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Users (minimal)
CREATE TABLE IF NOT EXISTS ab_esl.users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    nickname VARCHAR(255),
    l1 VARCHAR(10),
    grade_band VARCHAR(20),
    class_session_id INTEGER REFERENCES ab_esl.class_sessions(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_transcripts_session ON ab_esl.transcripts(session_id);
CREATE INDEX IF NOT EXISTS idx_transcripts_user ON ab_esl.transcripts(user_id);
CREATE INDEX IF NOT EXISTS idx_reading_scores_user ON ab_esl.reading_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_class_sessions_code ON ab_esl.class_sessions(class_code);
