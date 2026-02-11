"""Database schema definitions and migrations for monocli.

Provides schema creation and version-based migration system.
"""

from __future__ import annotations

import aiosqlite

# Current schema version
SCHEMA_VERSION = 1

# Schema creation SQL
SCHEMA_SQL = """
-- Cache metadata table
CREATE TABLE IF NOT EXISTS cache_metadata (
    key TEXT PRIMARY KEY,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ttl_seconds INTEGER DEFAULT 300,
    fetch_count INTEGER DEFAULT 0,
    last_error TEXT
);

-- Merge requests cache table
CREATE TABLE IF NOT EXISTS merge_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    iid INTEGER NOT NULL,
    title TEXT NOT NULL,
    state TEXT NOT NULL,
    author_login TEXT,
    author_name TEXT,
    web_url TEXT NOT NULL,
    source_branch TEXT,
    target_branch TEXT,
    created_at TIMESTAMP,
    draft INTEGER DEFAULT 0,
    description TEXT,
    raw_json TEXT NOT NULL,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subsection TEXT NOT NULL,
    UNIQUE(iid, subsection)
);

-- Index for faster queries by subsection
CREATE INDEX IF NOT EXISTS idx_mr_subsection ON merge_requests(subsection);
CREATE INDEX IF NOT EXISTS idx_mr_cached_at ON merge_requests(cached_at);

-- Work items cache table
CREATE TABLE IF NOT EXISTS work_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL UNIQUE,
    adapter_type TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    url TEXT NOT NULL,
    priority TEXT,
    assignee TEXT,
    created_at TIMESTAMP,
    raw_json TEXT NOT NULL,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_completed INTEGER DEFAULT 0
);

-- Indexes for work items
CREATE INDEX IF NOT EXISTS idx_wi_adapter_type ON work_items(adapter_type);
CREATE INDEX IF NOT EXISTS idx_wi_cached_at ON work_items(cached_at);
CREATE INDEX IF NOT EXISTS idx_wi_is_completed ON work_items(is_completed);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


async def init_schema(conn: aiosqlite.Connection) -> None:
    """Initialize database schema.

    Creates all tables if they don't exist and sets schema version.
    Safe to call multiple times (idempotent).

    Args:
        conn: Active SQLite connection.
    """
    # Execute schema creation
    await conn.executescript(SCHEMA_SQL)

    # Record schema version if not already set
    cursor = await conn.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
    row = await cursor.fetchone()

    if row is None:
        await conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
    elif row[0] < SCHEMA_VERSION:
        # Migration needed
        await migrate_schema(conn, from_version=row[0], to_version=SCHEMA_VERSION)


async def migrate_schema(conn: aiosqlite.Connection, from_version: int, to_version: int) -> None:
    """Migrate database schema from one version to another.

    Args:
        conn: Active SQLite connection.
        from_version: Current schema version.
        to_version: Target schema version.
    """
    # Future migrations go here
    # Example:
    # if from_version < 2:
    #     await conn.execute("ALTER TABLE ...")

    # Update schema version
    await conn.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (?)", (to_version,))
