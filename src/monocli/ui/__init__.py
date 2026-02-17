"""UI package for monocli.

This package provides Textual-based widgets for the dashboard interface,
including section widgets for displaying merge requests and work items.
"""

from monocli.ui.app import MonoApp
from monocli.ui.sections import MergeRequestSection
from monocli.ui.sections import WorkItemSection
from monocli.ui.topbar import TopBar

__all__ = ["MergeRequestSection", "MonoApp", "TopBar", "WorkItemSection"]
