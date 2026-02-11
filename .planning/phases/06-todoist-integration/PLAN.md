# Phase 06: Todoist Integration

## Overview

Add native Todoist API support to monocli, allowing users to view their Todoist tasks alongside Jira work items in a unified dashboard view.

**Status**: Planning
**Priority**: High
**Estimated Effort**: 3-4 hours

## User Requirements

1. **API Token Authentication**: User provides Todoist API token (not CLI-based like existing adapters)
2. **Optional Project Filtering**: Configurable list of project names to filter tasks
3. **Task Display Options**:
   - Default: show only open/active tasks
   - Optional: show completed tasks
   - Optional: show completed tasks within timeframe (24h, 48h, 72h, 7days)
4. **Unified UI Display**: Todoist tasks combined with Jira items in a single table
5. **Visual Distinction**: Use emojis/icons to distinguish different adapter sources

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| SDK Approach | Official Python SDK (`todoist-api-python`) | Simplifies auth, async support, official maintenance |
| Base Architecture | Standalone `TodoistAdapter` (no base class) | YAGNI -- only one API adapter; `async_utils.py` is for CLI subprocess concerns |
| Data Model | New `TodoistTask` Pydantic model | Follows existing patterns (JiraWorkItem, MergeRequest) |
| UI Integration | Extend `WorkItemSection` for mixed types | Reuse existing UI, unified view |
| Filtering | Config-based, optional | Flexibility: show all or filter by project |

## Implementation Plan

### 1. Dependency Addition

**File**: `pyproject.toml`

```toml
dependencies = [
  ...
  "todoist-api-python>=3.1.0,<4",
]
```

### 2. New Model: TodoistTask

**File**: `src/monocli/models.py`

First, add a `DueInfo` TypedDict for type-safe due date handling (instead of a raw `dict[str, Any]`):

```python
class DueInfo(TypedDict, total=False):
    """Todoist due date information."""
    date: str                # e.g. "2025-03-15"
    datetime: str | None     # e.g. "2025-03-15T14:00:00Z"
    string: str              # e.g. "tomorrow at 2pm"
    is_recurring: bool
    timezone: str | None
```

Then add the Pydantic model following existing patterns:

```python
class TodoistTask(BaseModel):
    model_config = ConfigDict(strict=True, validate_assignment=True)

    id: str
    content: str
    # NOTE: Todoist API priority is inverted from the UI:
    # API 1=normal (UI p4), 2=medium (UI p3), 3=high (UI p2), 4=urgent (UI p1)
    priority: int
    due: DueInfo | None = None
    project_id: str
    project_name: str
    url: HttpUrl
    created_at: str | None = None
    is_completed: bool = False
    completed_at: str | None = None

    # Adapter identification
    adapter_icon: ClassVar[str] = "📝"
    adapter_type: ClassVar[str] = "todoist"

    @property
    def due_date(self) -> str | None:
        """Extract readable due date from due info."""
        if not self.due:
            return None
        return self.due.get("date") or self.due.get("datetime")

    def display_key(self) -> str:
        """Todoist task ID for display."""
        return f"TD-{self.id}"

    def display_status(self) -> str:
        """Human-readable status."""
        return "DONE" if self.is_completed else "OPEN"

    def is_open(self) -> bool:
        """Check if task is still open."""
        return not self.is_completed

    @classmethod
    def priority_label(cls, priority: int) -> str:
        """Map Todoist API priority (1-4) to standard labels.

        NOTE: Todoist API priority is inverted from the UI display:
        API 4 = p1 (urgent) in UI, API 1 = p4 (normal) in UI.
        """
        mapping = {1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "HIGHEST"}
        return mapping.get(priority, "MEDIUM")
```

**Also update `JiraWorkItem`** to add `adapter_icon` and `adapter_type` class variables:
- `JiraWorkItem.adapter_icon = "🔴"`
- `JiraWorkItem.adapter_type = "jira"`

Do **not** add `adapter_icon` to `MergeRequest` -- it is unused until MRs are mixed into the same table. Add it when needed.

### 3. New Adapter: TodoistAdapter

**File**: `src/monocli/adapters/todoist.py` (new file)

This is a standalone class (no base class). The `todoist-api-python` import is guarded to fail gracefully if the package isn't installed.

> **IMPORTANT**: The Todoist REST API v2 does **not** support fetching completed tasks via `get_tasks(is_completed=True)`. Completed tasks require the Sync API's `completed/get_all` endpoint, which the official Python SDK exposes as `get_completed_items()` (available in SDK v3.x). Verify this method exists in the SDK version pinned before implementation.

```python
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from ..logging_config import get_logger
from ..models import DueInfo, TodoistTask

logger = get_logger(__name__)

try:
    from todoist_api_python.api_async import TodoistAPIAsync
except ImportError:
    TodoistAPIAsync = None  # type: ignore[assignment,misc]

if TYPE_CHECKING:
    from todoist_api_python.models import Task


class TodoistAdapter:
    """Adapter for Todoist REST API using official Python SDK.

    Standalone adapter (not subclassing CLIAdapter) since Todoist uses
    HTTP API calls, not CLI subprocess execution.
    """

    def __init__(self, token: str) -> None:
        if TodoistAPIAsync is None:
            raise ImportError(
                "todoist-api-python is required for Todoist integration. "
                "Install it with: uv add todoist-api-python"
            )
        self.token = token
        self._api: TodoistAPIAsync | None = None

    @property
    def api(self) -> TodoistAPIAsync:
        """Lazy-init async SDK client."""
        if self._api is None:
            self._api = TodoistAPIAsync(self.token)
        return self._api

    async def check_auth(self) -> bool:
        """Verify token by fetching projects (lightweight check)."""
        try:
            await self.api.get_projects()
            return True
        except Exception as e:
            logger.debug("Todoist auth check failed", exc_info=e)
            return False

    async def fetch_tasks(
        self,
        project_names: list[str] | None = None,
        show_completed: bool = False,
        show_completed_for_last: str | None = None,
    ) -> list[TodoistTask]:
        """
        Fetch tasks with optional filtering.

        Args:
            project_names: List of project names to filter (None = all projects)
            show_completed: Include completed tasks (all completed if no timeframe)
            show_completed_for_last: Narrow completed tasks to this window
                                     ("24h", "48h", "72h", "7days").
                                     Only used when show_completed=True.

        Returns:
            List of TodoistTask models
        """
        # 1. Get all projects to build name-to-ID mapping
        try:
            projects = await self.api.get_projects()
        except Exception as e:
            logger.error("Failed to fetch Todoist projects", exc_info=e)
            return []

        project_id_to_name = {p.id: p.name for p in projects}

        # 2. Resolve project IDs if filtering by name
        target_project_ids: set[str] | None = None
        if project_names:
            target_project_ids = {
                pid for pid, pname in project_id_to_name.items()
                if pname in project_names
            }
            logger.info(
                "Filtering by projects",
                projects=project_names,
                resolved_ids=target_project_ids,
            )

        # 3. Fetch active tasks
        try:
            active_tasks = await self.api.get_tasks()
        except Exception as e:
            logger.error("Failed to fetch Todoist tasks", exc_info=e)
            return []

        # 4. Optionally fetch completed tasks
        # NOTE: Completed tasks use a separate Sync API endpoint.
        # The SDK exposes this as get_completed_items(), NOT get_tasks(is_completed=True).
        completed_tasks: list[Task] = []
        if show_completed:
            try:
                completed_tasks = await self.api.get_completed_items()
            except Exception as e:
                logger.warning(
                    "Failed to fetch completed Todoist tasks", exc_info=e
                )

        # 5. Convert to models with filtering
        all_tasks = active_tasks + completed_tasks
        tasks = []
        for t in all_tasks:
            # Filter by project if specified
            if target_project_ids and t.project_id not in target_project_ids:
                continue

            # Filter completed by time window if specified
            if t.is_completed and show_completed_for_last:
                if not self._is_within_timeframe(
                    t.completed_at, show_completed_for_last
                ):
                    continue

            tasks.append(self._task_to_model(t, project_id_to_name))

        logger.info("Fetched Todoist tasks", count=len(tasks))
        return tasks

    def _task_to_model(
        self,
        task: Task,
        project_id_to_name: dict[str, str],
    ) -> TodoistTask:
        """Convert SDK Task to TodoistTask model."""
        due_info: DueInfo | None = None
        if task.due:
            due_info = DueInfo(
                date=task.due.date,
                is_recurring=task.due.is_recurring,
                datetime=task.due.datetime,
                string=task.due.string,
                timezone=task.due.timezone,
            )

        return TodoistTask(
            id=task.id,
            content=task.content,
            priority=task.priority,
            due=due_info,
            project_id=task.project_id,
            project_name=project_id_to_name.get(task.project_id, "Unknown"),
            url=task.url,
            created_at=task.created_at,
            is_completed=task.is_completed,
            completed_at=task.completed_at,
        )

    def _is_within_timeframe(
        self, completed_at: str | None, timeframe: str
    ) -> bool:
        """
        Check if completed datetime is within specified timeframe.

        Args:
            completed_at: ISO datetime string
            timeframe: One of "24h", "48h", "72h", "7days"

        Returns:
            True if within timeframe
        """
        if not completed_at:
            return False

        hours_map = {"24h": 24, "48h": 48, "72h": 72, "7days": 168}
        hours = hours_map.get(timeframe, 0)

        if hours == 0:
            return False

        try:
            dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            return dt >= cutoff
        except (ValueError, TypeError):
            logger.warning(
                "Failed to parse completed_at", completed_at=completed_at
            )
            return False
```

### 4. Export New Adapter

**File**: `src/monocli/adapters/__init__.py`

Add `TodoistAdapter` to existing exports (note: `GitLabAdapter` is **not** currently exported from this package -- it is imported directly in `main_screen.py` -- so don't add it here):

```python
from .todoist import TodoistAdapter

__all__ = [
    "CLIDetector",
    "DetectionRegistry",
    "DetectionResult",
    "JiraAdapter",
    "TodoistAdapter",
]
```

### 5. Configuration Updates

**File**: `src/monocli/config.py`

Add Todoist configuration to `Config` class following the existing pattern (nested YAML dict + env var overrides).

**Valid timeframe values**: `"24h"`, `"48h"`, `"72h"`, `"7days"`. Invalid values should be rejected at config load time (log a warning and default to `None`).

New properties on `Config`:

```python
VALID_TIMEFRAMES = {"24h", "48h", "72h", "7days"}

@property
def todoist_token(self) -> str | None:
    """Get the configured Todoist API token."""
    return self._data.get("todoist", {}).get("token")

@property
def todoist_projects(self) -> list[str]:
    """Get the configured Todoist project filter list."""
    return self._data.get("todoist", {}).get("projects", [])

@property
def todoist_show_completed(self) -> bool:
    """Whether to include completed Todoist tasks."""
    return self._data.get("todoist", {}).get("show_completed", False)

@property
def todoist_show_completed_for_last(self) -> str | None:
    """Timeframe for completed tasks (24h, 48h, 72h, 7days)."""
    value = self._data.get("todoist", {}).get("show_completed_for_last")
    if value and value not in VALID_TIMEFRAMES:
        logger.warning(
            "Invalid todoist.show_completed_for_last value",
            value=value,
            valid=VALID_TIMEFRAMES,
        )
        return None
    return value
```

Update `_apply_env_vars` to handle the new env var:

```python
@classmethod
def _apply_env_vars(cls, data: dict[str, Any]) -> dict[str, Any]:
    # ... existing gitlab/jira env vars ...

    # Todoist settings
    if "todoist" not in data:
        data["todoist"] = {}

    todoist_token = os.getenv("MONOCLI_TODOIST_TOKEN")
    if todoist_token:
        data["todoist"]["token"] = todoist_token

    return data
```

Environment variables:
- `MONOCLI_TODOIST_TOKEN` -- overrides `todoist.token` from config file

Config file format (`~/.config/monocli/config.yaml`):
```yaml
todoist:
  token: your-api-token-here
  projects:                        # Optional: filter to specific projects
    - Work
    - Personal
  show_completed: false            # Optional: include completed tasks
  show_completed_for_last: "7days" # Optional: 24h, 48h, 72h, 7days
```

### 6. WorkItem Protocol for Unified Type Interface

**File**: `src/monocli/models.py`

Define a `Protocol` that both `JiraWorkItem` and `TodoistTask` structurally satisfy. This provides a common type for `WorkItemSection.update_data()` and the sort key in `MainScreen`, without requiring inheritance.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class WorkItem(Protocol):
    """Protocol for items displayable in the WorkItemSection.

    Both JiraWorkItem and TodoistTask satisfy this protocol structurally.
    """

    adapter_icon: ClassVar[str]
    adapter_type: ClassVar[str]

    def display_key(self) -> str: ...
    def display_status(self) -> str: ...
    def is_open(self) -> bool: ...
```

**Also update `JiraWorkItem`** to add `adapter_icon` and `adapter_type` class variables:

```python
class JiraWorkItem(BaseModel):
    adapter_icon: ClassVar[str] = "🔴"
    adapter_type: ClassVar[str] = "jira"
```

Both `JiraWorkItem` and `TodoistTask` already implement `display_key()`, `display_status()`, and `is_open()` -- they structurally satisfy `WorkItem` without any code changes beyond adding the class variables.

### 7. UI Updates: WorkItemSection

**File**: `src/monocli/ui/sections.py`

Update `WorkItemSection` to accept `list[WorkItem]` (the Protocol) instead of `list[JiraWorkItem]`:

- Change type annotation: `work_items: reactive[list[WorkItem]]`
- Change `update_data(self, work_items: list[WorkItem])` signature
- Add "Icon" column (first column, width=3)
- Use `adapter_icon` class variable from each model
- Adapt priority/context/date display per item type using `adapter_type`:
  - **Jira**: Priority from `item.priority`, Context = `item.assignee or "Unassigned"`, Date = `""`
  - **Todoist**: Priority from `TodoistTask.priority_label(item.priority)`, Context = `item.project_name`, Date = `item.due_date or ""`
- URL extraction: for Jira use `item.url`, for Todoist use `str(item.url)`
- URL stored as row key for navigation (o key)

### 8. UI Updates: MainScreen

**File**: `src/monocli/ui/main_screen.py`

Update `fetch_work_items()` to fetch from both Jira and Todoist concurrently.

**Key fix**: The sort key cannot use `item.created_at` because `JiraWorkItem` has no `created_at` attribute (it stores everything in a `fields` dict). Use `is_open()` for primary sort and `display_key()` as a stable secondary sort:

```python
async def fetch_work_items(self) -> None:
    from monocli.adapters.jira import JiraAdapter
    from monocli.adapters.todoist import TodoistAdapter
    from monocli.config import get_config
    from monocli.models import WorkItem

    self.work_section.show_loading()
    self.work_loading = True

    items: list[WorkItem] = []

    # Fetch from Jira (existing logic, refactored)
    try:
        jira_adapter = JiraAdapter()
        if jira_adapter.is_available():
            if await jira_adapter.check_auth():
                jira_items = await jira_adapter.fetch_assigned_items()
                items.extend(jira_items)
    except Exception as e:
        logger.warning("Jira fetch failed", exc_info=e)

    # Fetch from Todoist (new)
    try:
        config = get_config()
        if config.todoist_token:
            todoist_adapter = TodoistAdapter(config.todoist_token)
            if await todoist_adapter.check_auth():
                todoist_tasks = await todoist_adapter.fetch_tasks(
                    project_names=config.todoist_projects or None,
                    show_completed=config.todoist_show_completed,
                    show_completed_for_last=config.todoist_show_completed_for_last,
                )
                items.extend(todoist_tasks)
    except ImportError:
        logger.debug("todoist-api-python not installed, skipping Todoist")
    except Exception as e:
        logger.warning("Todoist fetch failed", exc_info=e)

    if not items:
        self.work_section.set_error("No work item sources available")
        self.work_loading = False
        return

    # Sort: open items first, then by display key for stability
    items.sort(key=lambda i: (not i.is_open(), i.display_key()))
    self.work_section.update_data(items)
    self.work_loading = False
```

**Note**: The existing error handling pattern (show "acli CLI not found" when Jira is unavailable) needs to be relaxed since either source being missing is now acceptable -- only show an error if *both* sources fail to produce items.

### 9. Tests

**File**: `tests/test_todoist_adapter.py` (new file)

Test cases:
- `test_check_auth_success` -- mock `get_projects()` returning data
- `test_check_auth_failure` -- mock exception
- `test_fetch_tasks_no_filter` -- all tasks returned
- `test_fetch_tasks_with_project_filter` -- only matching projects
- `test_fetch_tasks_show_completed_all` -- `show_completed=True` without timeframe returns all completed
- `test_fetch_tasks_show_completed_with_timeframe` -- time-based filtering narrows results
- `test_is_within_timeframe` -- edge cases for timeframe parsing
- `test_task_to_model_conversion` -- SDK Task to TodoistTask mapping
- `test_import_error_when_sdk_missing` -- verify graceful `ImportError` when `todoist-api-python` is not installed

**File**: `tests/test_config.py`

- `test_todoist_config_from_yaml` -- load full todoist section
- `test_todoist_config_env_override` -- `MONOCLI_TODOIST_TOKEN` overrides yaml
- `test_todoist_timeframe_validation` -- invalid timeframe returns `None` with warning logged
- `test_todoist_config_defaults` -- missing todoist section returns sensible defaults

**File**: `tests/test_models.py`

- `test_work_item_protocol_jira` -- verify `JiraWorkItem` satisfies `WorkItem` protocol
- `test_work_item_protocol_todoist` -- verify `TodoistTask` satisfies `WorkItem` protocol

**File**: `tests/ui/test_sections.py`

- `test_work_item_section_mixed_types` -- both Jira and Todoist items rendered
- `test_work_item_section_todoist_only` -- Todoist items only
- `test_icon_column_displayed` -- icons visible for each adapter type

## Files Changed

| File | Change Type |
|------|-------------|
| `pyproject.toml` | Modified -- add `todoist-api-python` dependency |
| `src/monocli/models.py` | Modified -- add `DueInfo` TypedDict, `TodoistTask` model, `WorkItem` Protocol, add `adapter_icon`/`adapter_type` to `JiraWorkItem` |
| `src/monocli/adapters/todoist.py` | **New** -- standalone `TodoistAdapter` with guarded import |
| `src/monocli/adapters/__init__.py` | Modified -- export `TodoistAdapter` |
| `src/monocli/config.py` | Modified -- add todoist config properties, env var override, timeframe validation |
| `src/monocli/ui/sections.py` | Modified -- update `WorkItemSection` to accept `list[WorkItem]` with icon column |
| `src/monocli/ui/main_screen.py` | Modified -- add Todoist fetch alongside Jira, fix sort key |
| `tests/test_todoist_adapter.py` | **New** -- adapter tests including import error handling |
| `tests/test_models.py` | Modified -- `WorkItem` protocol conformance tests |
| `tests/test_config.py` | Modified -- todoist config + timeframe validation tests |
| `tests/ui/test_sections.py` | Modified -- mixed item type tests |

## Success Criteria

1. Todoist API token configurable via YAML or `MONOCLI_TODOIST_TOKEN` env var
2. Tasks fetched and displayed in the Work Items section
3. Project filtering works when `todoist.projects` is configured
4. Only open tasks shown by default
5. `show_completed` shows all completed; `show_completed_for_last` narrows the window (independent options)
6. Invalid `show_completed_for_last` values rejected with warning at config load time
7. Jira and Todoist items visually distinguishable (emojis in icon column)
8. Both item types navigable (j/k) and openable (o key)
9. Auth failures handled gracefully (logged, non-fatal)
10. Missing `todoist-api-python` dependency handled gracefully (`ImportError` caught, Todoist skipped)
11. `JiraWorkItem` and `TodoistTask` both satisfy the `WorkItem` Protocol
12. All checks pass: `uv run ruff check .`, `uv run ty src/`, `uv run pytest`

## Dependencies

- `todoist-api-python>=3.1.0,<4` (new)

## References

- Todoist REST API v2: https://developer.todoist.com/rest/v2/
- Todoist Sync API (completed items): https://developer.todoist.com/sync/v9/
- Python SDK docs: https://doist.github.io/todoist-api-python/
- Python SDK source: https://github.com/Doist/todoist-api-python/
