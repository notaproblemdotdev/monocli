"""Data sources package for monocli.

Provides source protocols and implementations for fetching data from
various platforms (GitLab, GitHub, Jira, Todoist, Linear, etc.).
"""

from .base import (
    APIBaseAdapter,
    CLIBaseAdapter,
    CodeReviewSource,
    PieceOfWorkSource,
    Source,
)
from .github import GitHubSource
from .gitlab import GitLabSource
from .jira import JiraSource
from .registry import SourceRegistry
from .todoist import TodoistSource

__all__ = [
    "Source",
    "PieceOfWorkSource",
    "CodeReviewSource",
    "CLIBaseAdapter",
    "APIBaseAdapter",
    "SourceRegistry",
    "GitHubSource",
    "GitLabSource",
    "JiraSource",
    "TodoistSource",
    "Source",
]
