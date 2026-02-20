"""UI package for monocle.

This package provides Textual-based widgets for the dashboard interface,
including section widgets for displaying merge requests and work items.
"""

from monocle.ui.app import MonoApp
from monocle.ui.sections import MergeRequestSection
from monocle.ui.sections import WorkItemSection
from monocle.ui.topbar import TopBar

__all__ = ["MergeRequestSection", "MonoApp", "TopBar", "WorkItemSection"]
