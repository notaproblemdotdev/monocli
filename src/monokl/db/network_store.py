"""Network ping storage for connectivity tracking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from monokl.db.connection import DatabaseManager


@dataclass
class PingResult:
    """Result of a network ping check."""

    url: str
    timestamp: datetime
    response_time_ms: int | None
    status_code: int | None
    success: bool
    error: str | None


class NetworkStore:
    """Store and retrieve network ping results."""

    def __init__(self, db: DatabaseManager | None = None) -> None:
        """Initialize the network store.

        Args:
            db: Optional database manager instance.
        """
        self._db = db
        self._owns_db = db is None

    async def _get_db(self) -> DatabaseManager:
        """Get or create database manager."""
        if self._db is None:
            self._db = DatabaseManager()
            await self._db.initialize()
        return self._db

    async def close(self) -> None:
        """Close database connection if we own it."""
        if self._owns_db and self._db is not None:
            await self._db.close()

    async def save_ping(
        self,
        url: str,
        response_time_ms: int | None,
        status_code: int | None,
        *,
        success: bool,
        error: str | None = None,
    ) -> None:
        """Save a ping result to the database.

        Args:
            url: The URL that was pinged.
            response_time_ms: Response time in milliseconds.
            status_code: HTTP status code.
            success: Whether the ping was successful.
            error: Error message if failed.
        """
        db = await self._get_db()
        conn = await db.get_connection()
        await conn.execute(
            """
            INSERT INTO network_pings (url, response_time_ms, status_code, success, error)
            VALUES (?, ?, ?, ?, ?)
            """,
            (url, response_time_ms, status_code, 1 if success else 0, error),
        )

    async def get_pings(
        self,
        url: str | None = None,
        limit: int = 100,
    ) -> list[PingResult]:
        """Get ping history.

        Args:
            url: Filter by URL (optional).
            limit: Maximum number of results.

        Returns:
            List of PingResult objects, newest first.
        """
        db = await self._get_db()
        conn = await db.get_connection()

        if url:
            cursor = await conn.execute(
                """
                SELECT url, timestamp, response_time_ms, status_code, success, error
                FROM network_pings
                WHERE url = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (url, limit),
            )
        else:
            cursor = await conn.execute(
                """
                SELECT url, timestamp, response_time_ms, status_code, success, error
                FROM network_pings
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )

        rows = await cursor.fetchall()
        return [
            PingResult(
                url=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                response_time_ms=row[2],
                status_code=row[3],
                success=bool(row[4]),
                error=row[5],
            )
            for row in rows
        ]

    async def clear_pings(self, url: str | None = None) -> int:
        """Clear ping history.

        Args:
            url: Clear only this URL (optional, clears all if None).

        Returns:
            Number of rows deleted.
        """
        db = await self._get_db()
        conn = await db.get_connection()

        if url:
            cursor = await conn.execute("DELETE FROM network_pings WHERE url = ?", (url,))
        else:
            cursor = await conn.execute("DELETE FROM network_pings")

        return cursor.rowcount
