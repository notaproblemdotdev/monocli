"""Tests for cache management."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

import pytest

from monocli.db.cache import CacheManager
from monocli.db.connection import DatabaseManager
from monocli.models import MergeRequest, TodoistTask


@pytest.fixture(autouse=True)
def reset_db_manager():
    """Reset the singleton instance before each test."""
    DatabaseManager.reset_instance()
    yield
    DatabaseManager.reset_instance()


@pytest.fixture
async def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "cache_test.db"
    db = DatabaseManager(str(db_path))
    await db.initialize()
    yield db
    await db.close()


class TestCacheManager:
    """Test cache operations."""

    @pytest.mark.asyncio
    async def test_cache_merge_requests(self, tmp_path):
        """Test caching and retrieving merge requests."""
        # Use singleton to ensure cache manager uses same db
        db_path = tmp_path / "test_cache_mr.db"
        db = DatabaseManager(str(db_path))
        await db.initialize()

        cache_manager = CacheManager(ttl_seconds=300)

        # Create test MRs
        mrs = [
            MergeRequest(
                iid=1,
                title="Test MR 1",
                state="opened",
                author={"name": "Test Author", "username": "testuser"},
                web_url="https://gitlab.com/test/repo/-/merge_requests/1",
                source_branch="feature/1",
                target_branch="main",
            ),
            MergeRequest(
                iid=2,
                title="Test MR 2",
                state="merged",
                author={"name": "Test Author", "username": "testuser"},
                web_url="https://gitlab.com/test/repo/-/merge_requests/2",
                source_branch="feature/2",
                target_branch="main",
            ),
        ]

        # Store in cache
        await cache_manager.set_merge_requests("assigned", mrs)

        # Retrieve from cache
        cached = await cache_manager.get_merge_requests("assigned")
        assert cached is not None
        assert len(cached) == 2
        # Data is ordered by iid DESC in SQL query, so iid=2 comes first
        assert cached[0].iid == 2
        assert cached[0].title == "Test MR 2"
        assert cached[1].iid == 1

        await db.close()

    @pytest.mark.asyncio
    async def test_cache_validity(self, tmp_path):
        """Test cache TTL validity check."""
        db_path = tmp_path / "test_validity.db"
        db = DatabaseManager(str(db_path))
        await db.initialize()

        cache_manager = CacheManager(ttl_seconds=300)

        # Create and cache a MR
        mrs = [
            MergeRequest(
                iid=1,
                title="Test MR",
                state="opened",
                author={"name": "Test"},
                web_url="https://gitlab.com/test/repo/-/merge_requests/1",
                source_branch="feature",
                target_branch="main",
            ),
        ]

        await cache_manager.set_merge_requests("assigned", mrs)

        # Should be valid immediately
        is_valid = await cache_manager.is_cache_valid("merge_requests")
        assert is_valid is True

        await db.close()

    @pytest.mark.asyncio
    async def test_cache_invalidation(self, tmp_path):
        """Test cache invalidation."""
        db_path = tmp_path / "test_invalidate.db"
        db = DatabaseManager(str(db_path))
        await db.initialize()

        cache_manager = CacheManager(ttl_seconds=300)

        # Create and cache a MR
        mrs = [
            MergeRequest(
                iid=1,
                title="Test MR",
                state="opened",
                author={"name": "Test"},
                web_url="https://gitlab.com/test/repo/-/merge_requests/1",
                source_branch="feature",
                target_branch="main",
            ),
        ]

        await cache_manager.set_merge_requests("assigned", mrs)

        # Verify cache exists (with accept_stale to bypass TTL check in this test)
        cached = await cache_manager.get_merge_requests("assigned", accept_stale=True)
        assert cached is not None

        # Invalidate cache
        await cache_manager.invalidate("merge_requests")

        # Should return None after invalidation (even with accept_stale)
        cached = await cache_manager.get_merge_requests("assigned", accept_stale=True)
        assert cached is None

        await db.close()

    @pytest.mark.asyncio
    async def test_cache_work_items(self, tmp_path):
        """Test caching work items."""
        db_path = tmp_path / "test_work_items.db"
        db = DatabaseManager(str(db_path))
        await db.initialize()

        cache_manager = CacheManager(ttl_seconds=300)

        # Create test todoist tasks
        tasks = [
            TodoistTask(
                id="12345",
                content="Test Task 1",
                priority=4,
                project_id="proj1",
                project_name="Work",
                url="https://todoist.com/showTask?id=12345",
                is_completed=False,
            ),
            TodoistTask(
                id="67890",
                content="Test Task 2",
                priority=1,
                project_id="proj1",
                project_name="Work",
                url="https://todoist.com/showTask?id=67890",
                is_completed=True,
            ),
        ]

        # Store in cache
        await cache_manager.set_work_items(tasks)

        # Retrieve from cache
        cached = await cache_manager.get_work_items()
        assert cached is not None
        assert len(cached) == 2

        await db.close()

    @pytest.mark.asyncio
    async def test_accept_stale(self, tmp_path):
        """Test accepting stale cache for offline mode."""
        # Create cache manager with very short TTL
        db_path = tmp_path / "test_stale.db"
        db = DatabaseManager(str(db_path))
        await db.initialize()

        short_cache = CacheManager(ttl_seconds=0)

        # Create and cache a MR
        mrs = [
            MergeRequest(
                iid=1,
                title="Test MR",
                state="opened",
                author={"name": "Test"},
                web_url="https://gitlab.com/test/repo/-/merge_requests/1",
                source_branch="feature",
                target_branch="main",
            ),
        ]

        await short_cache.set_merge_requests("assigned", mrs)

        # Wait for TTL to expire
        await asyncio.sleep(0.1)

        # Without accept_stale, should return None
        cached = await short_cache.get_merge_requests("assigned", accept_stale=False)
        assert cached is None

        # With accept_stale, should return cached data
        cached = await short_cache.get_merge_requests("assigned", accept_stale=True)
        assert cached is not None
        assert len(cached) == 1

        await db.close()
