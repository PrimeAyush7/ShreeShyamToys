-- ==========================================================
-- SHREE SHYAM TOYS - v2.0 B2B CONVERSION & STORAGE UPGRADES
-- Migration: 003_v2_upgrades.sql
-- ==========================================================

-- 1. Permanent Database Binary Media Table (PostgreSQL BYTEA / SQLite BLOB)
CREATE TABLE IF NOT EXISTS stored_media (
    id VARCHAR(64) PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(64) NOT NULL,
    file_size INTEGER DEFAULT 0,
    file_data BYTEA NOT NULL,
    entity_type VARCHAR(64) DEFAULT 'product',
    entity_id VARCHAR(64) DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stored_media_entity ON stored_media(entity_type, entity_id);
