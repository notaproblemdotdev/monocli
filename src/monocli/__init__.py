"""Mono CLI - Unified terminal dashboard for PRs and work items."""

__version__ = "0.1.0"

from monocli.logging_config import configure_logging
from monocli.logging_config import get_logger

__all__ = ["configure_logging", "get_logger"]


def main() -> None:
    print("Hello from monocli!")
