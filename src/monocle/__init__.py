"""Mono CLI - Unified terminal dashboard for PRs and work items."""

from monocle.logging_config import configure_logging
from monocle.logging_config import get_logger
from monocle.version import get_version

__version__ = get_version()

__all__ = ["__version__", "configure_logging", "get_logger", "get_version"]
