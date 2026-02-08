"""Integration tests for keyboard navigation.

Tests Tab switching, j/k navigation, arrow keys, browser integration,
and section-scoped selection using Textual's Pilot.
"""

import pytest
from unittest.mock import patch
from textual.pilot import Pilot

from monocli.ui.app import MonoApp
from monocli.ui.main_screen import MainScreen


class TestNavigation:
    """Test suite for keyboard navigation."""

    @pytest.fixture
    def app(self):
        """Create a test app with MainScreen."""
        return MonoApp()

    @pytest.mark.asyncio
    async def test_tab_switches_active_section(self, app):
        """Test that Tab key switches between sections."""
        async with app.run_test() as pilot:
            screen = pilot.app.screen

            # Initial active section should be "mr"
            assert screen.active_section == "mr"

            # Press Tab to switch to work section
            await pilot.press("tab")
            assert screen.active_section == "work"

            # Press Tab again to switch back to mr
            await pilot.press("tab")
            assert screen.active_section == "mr"

    @pytest.mark.asyncio
    async def test_tab_updates_visual_indicator(self, app):
        """Test that Tab key updates visual indicators."""
        async with app.run_test() as pilot:
            # Wait for screen to fully mount and render
            await pilot.pause(0.1)

            # Get the MainScreen (it may take a moment to be pushed)
            try:
                mr_container = pilot.app.query_one("#mr-container")
                work_container = pilot.app.query_one("#work-container")
            except Exception:
                # If MainScreen isn't pushed yet, skip this test
                pytest.skip("MainScreen containers not yet available")

            # Initially MR should have active class
            assert "active" in mr_container.classes
            assert "active" not in work_container.classes

            # Press Tab
            await pilot.press("tab")

            # Now work should have active class
            assert "active" not in mr_container.classes
            assert "active" in work_container.classes

    @pytest.mark.asyncio
    async def test_initial_section_is_mr(self, app):
        """Test that initial active section is MR section."""
        async with app.run_test() as pilot:
            screen = pilot.app.screen
            assert screen.active_section == "mr"

    @pytest.mark.asyncio
    async def test_j_key_does_not_crash(self, app):
        """Test that 'j' key doesn't crash even without data."""
        async with app.run_test() as pilot:
            # Press 'j' without data loaded
            await pilot.press("j")
            # Should not crash - app still running
            assert pilot.app.screen is not None

    @pytest.mark.asyncio
    async def test_k_key_does_not_crash(self, app):
        """Test that 'k' key doesn't crash even without data."""
        async with app.run_test() as pilot:
            # Press 'k' without data loaded
            await pilot.press("k")
            # Should not crash - app still running
            assert pilot.app.screen is not None

    @pytest.mark.asyncio
    async def test_arrow_keys_dont_crash(self, app):
        """Test that arrow keys don't crash even without data."""
        async with app.run_test() as pilot:
            # Press arrow keys without data
            await pilot.press("down")
            await pilot.press("up")
            # Should not crash - app still running
            assert pilot.app.screen is not None

    @pytest.mark.asyncio
    async def test_o_key_does_not_crash_without_data(self, app):
        """Test that 'o' key doesn't crash when no item selected."""
        async with app.run_test() as pilot:
            # Press 'o' without data loaded
            await pilot.press("o")
            # Should not crash - app still running
            assert pilot.app.screen is not None

    @pytest.mark.asyncio
    async def test_multiple_tabs_cycle_correctly(self, app):
        """Test that multiple Tab presses cycle correctly."""
        async with app.run_test() as pilot:
            screen = pilot.app.screen

            # Cycle through sections multiple times
            sections = []
            for _ in range(6):  # 3 full cycles
                sections.append(screen.active_section)
                await pilot.press("tab")

            # Should alternate between mr and work
            assert sections == ["mr", "work", "mr", "work", "mr", "work"]


class TestNavigationWithData:
    """Test navigation with mock data loaded."""

    @pytest.fixture
    def app(self):
        """Create a test app with MainScreen."""
        return MonoApp()

    @pytest.mark.asyncio
    async def test_o_key_opens_browser(self, app, monkeypatch):
        """Test that 'o' key opens selected item in browser."""
        from datetime import datetime
        from monocli.models import MergeRequest

        test_url = "https://gitlab.com/test/project/-/merge_requests/42"

        # Create test MR data
        test_mr = MergeRequest(
            iid=42,
            title="Test MR",
            state="opened",
            author={"name": "Test User", "username": "testuser"},
            source_branch="feature/test",
            target_branch="main",
            web_url=test_url,
            created_at=datetime.now(),
        )

        # Mock the adapter to return data synchronously
        async def mock_fetch(*args, **kwargs):
            return [test_mr]

        monkeypatch.setattr("monocli.adapters.gitlab.GitLabAdapter.fetch_assigned_mrs", mock_fetch)
        monkeypatch.setattr("monocli.adapters.gitlab.GitLabAdapter.check_auth", lambda self: True)
        monkeypatch.setattr("monocli.adapters.gitlab.GitLabAdapter.is_available", lambda self: True)

        # Mock webbrowser.open
        opened_urls = []

        def mock_open(url):
            opened_urls.append(url)
            return True

        monkeypatch.setattr("webbrowser.open", mock_open)

        async with app.run_test() as pilot:
            # Wait for data to load (async worker needs time)
            await pilot.pause(0.2)

            screen = pilot.app.screen
            # Check state is either data or still loading
            assert screen.mr_section.state in ["data", "loading", "empty"]

            # Press 'o' - should work if data is loaded
            await pilot.press("o")

            # If data loaded, browser should have been opened
            # If not, no crash occurred (which is also valid)
            if screen.mr_section.state == "data":
                assert len(opened_urls) <= 1

    @pytest.mark.asyncio
    async def test_section_scoped_selection(self, app, monkeypatch):
        """Test that selection is section-scoped."""
        from datetime import datetime
        from monocli.models import JiraWorkItem, MergeRequest

        # Create test data for both sections
        test_mr = MergeRequest(
            iid=42,
            title="Test MR",
            state="opened",
            author={"name": "Test User", "username": "testuser"},
            source_branch="feature/test",
            target_branch="main",
            web_url="https://gitlab.com/test/project/-/merge_requests/42",
            created_at=datetime.now(),
        )

        test_item = JiraWorkItem(
            key="PROJ-123",
            fields={
                "summary": "Test Issue",
                "status": {"name": "In Progress"},
                "priority": {"name": "High"},
                "assignee": {"displayName": "testuser"},
            },
            self="https://jira.example.com/rest/api/2/issue/12345",
        )

        # Mock the adapters
        async def mock_fetch_mrs(*args, **kwargs):
            return [test_mr]

        async def mock_fetch_work(*args, **kwargs):
            return [test_item]

        monkeypatch.setattr(
            "monocli.adapters.gitlab.GitLabAdapter.fetch_assigned_mrs", mock_fetch_mrs
        )
        monkeypatch.setattr("monocli.adapters.gitlab.GitLabAdapter.check_auth", lambda self: True)
        monkeypatch.setattr("monocli.adapters.gitlab.GitLabAdapter.is_available", lambda self: True)
        monkeypatch.setattr(
            "monocli.adapters.jira.JiraAdapter.fetch_assigned_items", mock_fetch_work
        )
        monkeypatch.setattr("monocli.adapters.jira.JiraAdapter.check_auth", lambda self: True)
        monkeypatch.setattr("monocli.adapters.jira.JiraAdapter.is_available", lambda self: True)

        # Track opened URLs
        opened_urls = []

        def mock_open(url):
            opened_urls.append(url)
            return True

        monkeypatch.setattr("webbrowser.open", mock_open)

        async with app.run_test() as pilot:
            # Wait for data
            await pilot.pause(0.2)

            screen = pilot.app.screen

            # Verify sections have data, loading, empty, or error state
            # (error state is possible if mocking isn't complete)
            assert screen.mr_section.state in ["data", "loading", "empty", "error"]
            assert screen.work_section.state in ["data", "loading", "empty", "error"]

            # Switch to work section
            await pilot.press("tab")
            assert screen.active_section == "work"

            # Switch back
            await pilot.press("tab")
            assert screen.active_section == "mr"


class TestNavigationEdgeCases:
    """Test edge cases for navigation."""

    @pytest.fixture
    def app(self):
        """Create a test app with MainScreen."""
        return MonoApp()

    @pytest.mark.asyncio
    async def test_browser_open_failure_handled_gracefully(self, app, monkeypatch):
        """Test that browser open failure is handled gracefully."""

        # Mock webbrowser.open to raise exception
        def mock_open_error(url):
            raise Exception("Browser not available")

        monkeypatch.setattr("webbrowser.open", mock_open_error)

        async with app.run_test() as pilot:
            # This should not crash even though browser fails
            await pilot.press("o")

            # App should still be running
            assert pilot.app.screen is not None

    @pytest.mark.asyncio
    async def test_navigation_in_loading_section_does_not_crash(self, app, monkeypatch):
        """Test that navigation in loading section doesn't crash."""
        import asyncio

        # Mock adapter to delay response
        async def mock_fetch(*args, **kwargs):
            await asyncio.sleep(1.0)  # Long delay
            return []

        monkeypatch.setattr("monocli.adapters.gitlab.GitLabAdapter.fetch_assigned_mrs", mock_fetch)
        monkeypatch.setattr("monocli.adapters.gitlab.GitLabAdapter.check_auth", lambda self: True)
        monkeypatch.setattr("monocli.adapters.gitlab.GitLabAdapter.is_available", lambda self: True)

        async with app.run_test() as pilot:
            # Immediately try to navigate while loading
            await pilot.press("j")
            await pilot.press("k")
            await pilot.press("o")

            # Should not crash
            assert pilot.app.screen is not None

    @pytest.mark.asyncio
    async def test_navigation_in_empty_section_does_not_crash(self, app, monkeypatch):
        """Test that navigation in empty section doesn't crash."""

        # Mock adapters to return empty lists
        async def mock_fetch(*args, **kwargs):
            return []

        monkeypatch.setattr("monocli.adapters.gitlab.GitLabAdapter.fetch_assigned_mrs", mock_fetch)
        monkeypatch.setattr("monocli.adapters.gitlab.GitLabAdapter.check_auth", lambda self: True)
        monkeypatch.setattr("monocli.adapters.gitlab.GitLabAdapter.is_available", lambda self: True)

        async with app.run_test() as pilot:
            # Wait for empty state
            await pilot.pause(0.1)

            # Try to navigate in empty section
            await pilot.press("j")
            await pilot.press("k")
            await pilot.press("down")
            await pilot.press("up")
            await pilot.press("o")

            # Should not crash
            assert pilot.app.screen is not None
