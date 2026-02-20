"""Database package for monocle."""

from __future__ import annotations

from monocle.db.connection import DatabaseManager
from monocle.db.connection import get_db_manager
from monocle.db.preferences import PreferencesManager
from monocle.db.work_store import FetchResult
from monocle.db.work_store import WorkStore

__all__ = [
    "DatabaseManager",
    "FetchResult",
    "PreferencesManager",
    "WorkStore",
    "get_db_manager",
]
