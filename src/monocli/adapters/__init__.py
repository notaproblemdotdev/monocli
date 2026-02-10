"""CLI adapters package for monocli.

Provides detection and registry for available CLI tools.
"""

from monocli.adapters.detection import CLIDetector, DetectionRegistry, DetectionResult
from monocli.adapters.jira import JiraAdapter
from monocli.adapters.todoist import TodoistAdapter

__all__ = [
    "CLIDetector",
    "DetectionRegistry",
    "DetectionResult",
    "JiraAdapter",
    "TodoistAdapter",
]
