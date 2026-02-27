"""Database schema definitions and migrations for monokl.

Provides schema creation and version-based migration system.
"""

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    import aiosqlite

# Schema version constants
SCHEMA_V2 = 2  # Unified cache table
SCHEMA_V3 = 3  # Network pings table

# Current schema version
SCHEMA_VERSION = SCHEMA_V3

# Schema creation SQL
SCHEMA_SQL = """
-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Unified cache table with source granularity (v2)
CREATE TABLE IF NOT EXISTS cached_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT NOT NULL,
    data_type TEXT NOT NULL,
    source TEXT NOT NULL,
    subsection TEXT,
    raw_json TEXT NOT NULL,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ttl_seconds INTEGER NOT NULL,
    fetch_count INTEGER DEFAULT 0,
    last_error TEXT,
    UNIQUE(cache_key)
);

-- Indexes for cached_data
CREATE INDEX IF NOT EXISTS idx_cached_data_key ON cached_data(cache_key);
CREATE INDEX IF NOT EXISTS idx_cached_data_type ON cached_data(data_type);
CREATE INDEX IF NOT EXISTS idx_cached_data_source ON cached_data(source);
CREATE INDEX IF NOT EXISTS idx_cached_data_cached_at ON cached_data(cached_at);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Network ping results table (v3)
CREATE TABLE IF NOT EXISTS network_pings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    status_code INTEGER,
    success INTEGER NOT NULL,
    error TEXT
);

-- Indexes for network_pings
CREATE INDEX IF NOT EXISTS idx_network_pings_url ON network_pings(url);
CREATE INDEX IF NOT EXISTS idx_network_pings_timestamp ON network_pings(timestamp);
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
    if from_version < SCHEMA_V2:
        # Migration v1 -> v2: Drop old cache tables, create new unified cache
        await conn.execute("DROP TABLE IF EXISTS cache_metadata")
        await conn.execute("DROP TABLE IF EXISTS merge_requests")
        await conn.execute("DROP TABLE IF EXISTS work_items")

        # Create new unified cache table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS cached_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT NOT NULL,
                data_type TEXT NOT NULL,
                source TEXT NOT NULL,
                subsection TEXT,
                raw_json TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ttl_seconds INTEGER NOT NULL,
                fetch_count INTEGER DEFAULT 0,
                last_error TEXT,
                UNIQUE(cache_key)
            )
        """)

        # Create indexes
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_cached_data_key ON cached_data(cache_key)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_cached_data_type ON cached_data(data_type)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_cached_data_source ON cached_data(source)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_cached_data_cached_at ON cached_data(cached_at)"
        )

    if from_version < SCHEMA_V3:
        # Migration v2 -> v3: Add network_pings table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS network_pings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_time_ms INTEGER,
                status_code INTEGER,
                success INTEGER NOT NULL,
                error TEXT
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_network_pings_url ON network_pings(url)")
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_network_pings_timestamp ON network_pings(timestamp)"
        )

    # Update schema version
    await conn.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (?)", (to_version,))
