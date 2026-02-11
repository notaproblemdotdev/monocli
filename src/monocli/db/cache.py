"""Cache management with TTL support and offline mode for monocli.

Provides caching layer for merge requests and work items with automatic
invalidation, offline fallback, and automatic cleanup of old records.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import aiosqlite

from monocli import get_logger
from monocli.db.connection import get_db_manager

if TYPE_CHECKING:
    from monocli.models import MergeRequest, WorkItem


logger = get_logger(__name__)

# Default cache TTL in seconds (5 minutes)
DEFAULT_CACHE_TTL = 300
# Default cleanup threshold in days (30 days)
DEFAULT_CLEANUP_DAYS = 30


class CacheManager:
    """Manage cached data with TTL and offline support.

    Provides automatic caching of fetched data with configurable TTL.
    When offline or CLI fails, returns cached data even if stale.
    Automatically cleans up old records on write operations.

    Example:
        cache = CacheManager()

        # Check cache first
        mrs = await cache.get_merge_requests("assigned")
        if mrs is None:
            # Fetch from API and cache
            mrs = await adapter.fetch_assigned_mrs(...)
            await cache.set_merge_requests("assigned", mrs)

        # Invalidate on manual refresh
        await cache.invalidate("merge_requests")
    """

    def __init__(self, ttl_seconds: int = DEFAULT_CACHE_TTL) -> None:
        """Initialize cache manager.

        Args:
            ttl_seconds: Default time-to-live for cache entries.
        """
        self.ttl_seconds = ttl_seconds

    async def get_merge_requests(
        self, subsection: str, accept_stale: bool = False
    ) -> list[MergeRequest] | None:
        """Get cached merge requests if not expired.

        Args:
            subsection: "assigned" or "opened"
            accept_stale: If True, return stale cache for offline mode.

        Returns:
            List of MergeRequest models, or None if cache miss.
            If accept_stale is True and cache exists, returns even if expired.
        """
        try:
            db = get_db_manager()
            conn = await db.get_connection()

            # Check if cache is valid
            is_valid = await self._is_cache_valid(conn, "merge_requests")

            if not is_valid and not accept_stale:
                logger.debug("Cache expired for merge_requests", subsection=subsection)
                return None

            # Fetch cached records
            cursor = await conn.execute(
                """
                SELECT raw_json FROM merge_requests
                WHERE subsection = ?
                ORDER BY iid DESC
                """,
                (subsection,),
            )
            rows = await cursor.fetchall()

            if not rows:
                logger.debug("No cached merge requests found", subsection=subsection)
                return None

            # Parse JSON back to models
            from monocli.models import MergeRequest

            mrs = []
            for row in rows:
                try:
                    data = json.loads(row[0])
                    mr = MergeRequest.model_validate(data)
                    mrs.append(mr)
                except Exception as e:
                    logger.warning("Failed to parse cached MR", error=str(e))
                    continue

            cache_status = "stale" if not is_valid else "fresh"
            logger.info(
                "Retrieved cached merge requests",
                subsection=subsection,
                count=len(mrs),
                status=cache_status,
            )

            return mrs

        except Exception as e:
            logger.error("Failed to get cached merge requests", error=str(e))
            return None

    async def set_merge_requests(self, subsection: str, mrs: list[MergeRequest]) -> None:
        """Store merge requests in cache.

        Args:
            subsection: "assigned" or "opened"
            mrs: List of MergeRequest models to cache.
        """
        try:
            db = get_db_manager()
            conn = await db.get_connection()

            # Clear existing records for this subsection
            await conn.execute("DELETE FROM merge_requests WHERE subsection = ?", (subsection,))

            # Insert new records
            cached_at = datetime.now().isoformat()
            records = []
            for mr in mrs:
                # Use by_alias=True for consistent serialization
                data = mr.model_dump(mode="json", by_alias=True)
                records.append(
                    (
                        mr.iid,
                        mr.title,
                        mr.state,
                        mr.author.get("login", ""),
                        mr.author.get("name", ""),
                        str(mr.web_url),
                        mr.source_branch,
                        mr.target_branch,
                        mr.created_at.isoformat() if mr.created_at else None,
                        int(mr.draft),
                        mr.description,
                        json.dumps(data),
                        cached_at,
                        subsection,
                    )
                )

            await conn.executemany(
                """
                INSERT INTO merge_requests
                (iid, title, state, author_login, author_name, web_url,
                 source_branch, target_branch, created_at, draft, description,
                 raw_json, cached_at, subsection)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                records,
            )

            # Update metadata
            await self._update_metadata(conn, "merge_requests", len(mrs))

            logger.info("Cached merge requests", subsection=subsection, count=len(mrs))

            # Cleanup old records periodically
            await self._cleanup_old_records(conn, "merge_requests")

        except Exception as e:
            logger.error("Failed to cache merge requests", error=str(e))

    async def get_work_items(self, accept_stale: bool = False) -> list[WorkItem] | None:
        """Get cached work items if not expired.

        Args:
            accept_stale: If True, return stale cache for offline mode.

        Returns:
            List of WorkItem models, or None if cache miss.
        """
        try:
            db = get_db_manager()
            conn = await db.get_connection()

            # Check if cache is valid
            is_valid = await self._is_cache_valid(conn, "work_items")

            if not is_valid and not accept_stale:
                logger.debug("Cache expired for work_items")
                return None

            # Fetch cached records
            cursor = await conn.execute(
                """
                SELECT adapter_type, raw_json FROM work_items
                ORDER BY cached_at DESC
                """
            )
            rows = await cursor.fetchall()

            if not rows:
                logger.debug("No cached work items found")
                return None

            # Parse JSON back to models
            from monocli.models import JiraWorkItem, TodoistTask

            items: list[WorkItem] = []
            for adapter_type, raw_json in rows:
                try:
                    data = json.loads(raw_json)
                    if adapter_type == "jira":
                        item = JiraWorkItem.model_validate(data)
                    elif adapter_type == "todoist":
                        item = TodoistTask.model_validate(data)
                    else:
                        logger.warning("Unknown adapter type", adapter_type=adapter_type)
                        continue
                    items.append(item)
                except Exception as e:
                    logger.warning("Failed to parse cached work item", error=str(e))
                    continue

            cache_status = "stale" if not is_valid else "fresh"
            logger.info("Retrieved cached work items", count=len(items), status=cache_status)

            return items

        except Exception as e:
            logger.error("Failed to get cached work items", error=str(e))
            return None

    async def set_work_items(self, items: list[WorkItem]) -> None:
        """Store work items in cache.

        Args:
            items: List of WorkItem models to cache.
        """
        try:
            db = get_db_manager()
            conn = await db.get_connection()

            # Clear existing records
            await conn.execute("DELETE FROM work_items")

            # Insert new records
            from monocli.models import JiraWorkItem, TodoistTask
            from pydantic import BaseModel

            cached_at = datetime.now().isoformat()
            records = []
            for item in items:
                if isinstance(item, BaseModel):
                    # Use by_alias=True to serialize with field aliases
                    data = item.model_dump(mode="json", by_alias=True)
                else:
                    # Fallback for non-Pydantic items (shouldn't happen)
                    data = {"external_id": getattr(item, "key", getattr(item, "id", "unknown"))}

                if isinstance(item, JiraWorkItem):
                    records.append(
                        (
                            item.key,
                            "jira",
                            item.summary,
                            item.status,
                            item.url,
                            item.priority,
                            item.assignee or "",
                            None,  # created_at not available in Jira model
                            json.dumps(data),
                            cached_at,
                            0,  # is_completed
                        )
                    )
                elif isinstance(item, TodoistTask):
                    records.append(
                        (
                            item.id,
                            "todoist",
                            item.content,
                            "DONE" if item.is_completed else "OPEN",
                            str(item.url_field),
                            TodoistTask.priority_label(item.priority),
                            "",  # assignee not available
                            item.created_at,
                            json.dumps(data),
                            cached_at,
                            int(item.is_completed),
                        )
                    )

            await conn.executemany(
                """
                INSERT INTO work_items
                (external_id, adapter_type, title, status, url, priority,
                 assignee, created_at, raw_json, cached_at, is_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                records,
            )

            # Update metadata
            await self._update_metadata(conn, "work_items", len(items))

            logger.info("Cached work items", count=len(items))

            # Cleanup old records periodically
            await self._cleanup_old_records(conn, "work_items")

        except Exception as e:
            logger.error("Failed to cache work items", error=str(e))

    async def is_cache_valid(self, key: str) -> bool:
        """Check if cache is still valid based on TTL.

        Args:
            key: Cache key (e.g., "merge_requests", "work_items").

        Returns:
            True if cache is valid, False otherwise.
        """
        try:
            db = get_db_manager()
            conn = await db.get_connection()
            return await self._is_cache_valid(conn, key)
        except Exception as e:
            logger.error("Failed to check cache validity", key=key, error=str(e))
            return False

    async def _is_cache_valid(
        self,
        conn: aiosqlite.Connection,  # type: ignore[name-defined]
        key: str,
    ) -> bool:
        """Internal method to check cache validity."""

        cursor = await conn.execute(
            """
            SELECT last_updated, ttl_seconds
            FROM cache_metadata
            WHERE key = ?
            """,
            (key,),
        )
        row = await cursor.fetchone()

        if row is None:
            return False

        last_updated_str, ttl_seconds = row
        last_updated = datetime.fromisoformat(last_updated_str)

        # Check if TTL has expired
        expires_at = last_updated + timedelta(seconds=ttl_seconds)
        return datetime.now() < expires_at

    async def _update_metadata(
        self,
        conn: aiosqlite.Connection,  # type: ignore[name-defined]
        key: str,
        count: int,
    ) -> None:
        """Update cache metadata with new fetch info."""

        await conn.execute(
            """
            INSERT INTO cache_metadata (key, last_updated, ttl_seconds, fetch_count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(key) DO UPDATE SET
                last_updated = CURRENT_TIMESTAMP,
                ttl_seconds = excluded.ttl_seconds,
                fetch_count = fetch_count + 1,
                last_error = NULL
            """,
            (key, datetime.now().isoformat(), self.ttl_seconds),
        )

    async def _cleanup_old_records(
        self,
        conn: aiosqlite.Connection,  # type: ignore[name-defined]
        table: str,
    ) -> None:
        """Remove records older than cleanup threshold."""

        cutoff = datetime.now() - timedelta(days=DEFAULT_CLEANUP_DAYS)
        cutoff_str = cutoff.isoformat()

        if table == "merge_requests":
            cursor = await conn.execute(
                "DELETE FROM merge_requests WHERE cached_at < ?", (cutoff_str,)
            )
        elif table == "work_items":
            cursor = await conn.execute("DELETE FROM work_items WHERE cached_at < ?", (cutoff_str,))
        else:
            return

        deleted = cursor.rowcount
        if deleted > 0:
            logger.info("Cleaned up old cache records", table=table, deleted=deleted)

    async def invalidate(self, key: str | None = None) -> None:
        """Invalidate specific cache or all caches.

        Args:
            key: Specific cache key to invalidate, or None to invalidate all.
        """
        try:
            db = get_db_manager()
            conn = await db.get_connection()

            if key is None or key == "all":
                # Invalidate all caches
                await conn.execute("DELETE FROM merge_requests")
                await conn.execute("DELETE FROM work_items")
                await conn.execute("DELETE FROM cache_metadata")
                logger.info("Invalidated all caches")
            elif key == "merge_requests":
                await conn.execute("DELETE FROM merge_requests")
                await conn.execute("DELETE FROM cache_metadata WHERE key = ?", ("merge_requests",))
                logger.info("Invalidated merge_requests cache")
            elif key == "work_items":
                await conn.execute("DELETE FROM work_items")
                await conn.execute("DELETE FROM cache_metadata WHERE key = ?", ("work_items",))
                logger.info("Invalidated work_items cache")
            else:
                logger.warning("Unknown cache key", key=key)

        except Exception as e:
            logger.error("Failed to invalidate cache", key=key, error=str(e))

    async def record_error(self, key: str, error: str) -> None:
        """Record an error for a cache key.

        Args:
            key: Cache key that encountered an error.
            error: Error message to record.
        """
        try:
            db = get_db_manager()
            conn = await db.get_connection()

            await conn.execute(
                """
                INSERT INTO cache_metadata (key, last_updated, ttl_seconds, last_error)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    last_error = excluded.last_error
                """,
                (key, datetime.now().isoformat(), self.ttl_seconds, error),
            )
        except Exception as e:
            logger.error("Failed to record cache error", key=key, error=str(e))

    async def get_cache_info(self, key: str) -> dict | None:
        """Get metadata about a cache entry.

        Args:
            key: Cache key to query.

        Returns:
            Dict with cache metadata, or None if not found.
        """
        try:
            db = get_db_manager()
            conn = await db.get_connection()

            cursor = await conn.execute(
                """
                SELECT last_updated, ttl_seconds, fetch_count, last_error
                FROM cache_metadata
                WHERE key = ?
                """,
                (key,),
            )
            row = await cursor.fetchone()

            if row is None:
                return None

            last_updated_str, ttl_seconds, fetch_count, last_error = row
            last_updated = datetime.fromisoformat(last_updated_str)
            expires_at = last_updated + timedelta(seconds=ttl_seconds)
            is_valid = datetime.now() < expires_at

            return {
                "key": key,
                "last_updated": last_updated,
                "ttl_seconds": ttl_seconds,
                "expires_at": expires_at,
                "is_valid": is_valid,
                "fetch_count": fetch_count,
                "last_error": last_error,
            }

        except Exception as e:
            logger.error("Failed to get cache info", key=key, error=str(e))
            return None
