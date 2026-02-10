"""Pydantic models for platform data structures.

This module provides validated data models for parsing CLI outputs from
gh (GitHub), glab (GitLab), and acli (Jira).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Protocol, runtime_checkable

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, HttpUrl
from typing_extensions import TypedDict


def parse_datetime(value: datetime | str | None) -> datetime | None:
    """Parse ISO 8601 datetime string or return datetime object."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Try parsing ISO 8601 format (handles both 'Z' and '+00:00' suffixes)
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    raise ValueError(f"Invalid datetime value: {value}")


# Type alias for datetime fields that accept ISO 8601 strings
IsoDateTime = Annotated[datetime | None, BeforeValidator(parse_datetime)]


class DueInfo(TypedDict, total=False):
    """Todoist due date information.

    All fields are optional.
    """

    date: str  # e.g. "2025-03-15"
    datetime: str | None  # e.g. "2025-03-15T14:00:00Z"
    string: str  # e.g. "tomorrow at 2pm"
    is_recurring: bool
    timezone: str | None


@runtime_checkable
class WorkItem(Protocol):
    """Protocol for items displayable in the WorkItemSection.

    Both JiraWorkItem and TodoistTask satisfy this protocol structurally.
    """

    adapter_icon: str
    adapter_type: str

    def display_key(self) -> str: ...
    def display_status(self) -> str: ...
    def is_open(self) -> bool: ...

    @property
    def url(self) -> str: ...


class WorkItemStatus(str, Enum):
    """Work item status enumeration."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class Priority(str, Enum):
    """Priority level enumeration."""

    LOWEST = "lowest"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    HIGHEST = "highest"


class PullRequest(BaseModel):
    """GitHub Pull Request model.

    Validates GitHub PR data from gh CLI --json output.

    Attributes:
        number: PR number
        title: PR title
        state: PR state ("open", "closed", "merged")
        author: Dict containing author information with 'login' key
        html_url: PR URL
        draft: Whether the PR is a draft
        created_at: When the PR was created (ISO 8601 format)
        body: Optional PR description
    """

    model_config = ConfigDict(strict=True, validate_assignment=True)

    number: int = Field(..., description="Pull request number", ge=1)
    title: str = Field(..., description="Pull request title", min_length=1)
    state: str = Field(
        ...,
        description="Pull request state",
        pattern=r"^(open|closed|merged)$",
    )
    author: dict[str, Any] = Field(
        ...,
        description="Author information with 'login' key",
    )
    html_url: HttpUrl = Field(..., description="Pull request URL")
    draft: bool = Field(default=False, description="Whether this is a draft PR")
    created_at: IsoDateTime = Field(
        default=None,
        description="When the PR was created (ISO 8601 format)",
    )
    body: str | None = Field(default=None, description="Pull request description")

    def display_key(self) -> str:
        """Return formatted key for display."""
        return f"#{self.number}"

    def display_status(self) -> str:
        """Return normalized status string."""
        return self.state.upper()

    def is_open(self) -> bool:
        """Check if PR is open/ongoing."""
        return self.state == "open"


class MergeRequest(BaseModel):
    """GitLab Merge Request model.

    Validates GitLab MR data from glab CLI --json output.

    Attributes:
        iid: MR number (internal ID)
        title: MR title
        state: MR state ("opened", "closed", "merged", "locked")
        author: Dict containing author information with 'name' and 'username' keys
        web_url: MR URL
        source_branch: Source branch name
        target_branch: Target branch name
        created_at: When the MR was created (ISO 8601 format)
        draft: Whether the MR is a draft
        description: Optional MR description
    """

    model_config = ConfigDict(strict=True, validate_assignment=True)

    iid: int = Field(..., description="Merge request internal ID", ge=1)
    title: str = Field(..., description="Merge request title", min_length=1)
    state: str = Field(
        ...,
        description="Merge request state",
        pattern=r"^(opened|closed|merged|locked)$",
    )
    author: dict[str, Any] = Field(
        ...,
        description="Author information with 'name' and 'username' keys",
    )
    web_url: HttpUrl = Field(..., description="Merge request URL")
    source_branch: str = Field(..., description="Source branch name")
    target_branch: str = Field(..., description="Target branch name")
    created_at: IsoDateTime = Field(
        default=None,
        description="When the MR was created (ISO 8601 format)",
    )
    draft: bool = Field(default=False, description="Whether this is a draft MR")
    description: str | None = Field(default=None, description="Merge request description")

    def display_key(self) -> str:
        """Return formatted key for display."""
        return f"!{self.iid}"

    def display_status(self) -> str:
        """Return normalized status string."""
        return self.state.upper()

    def is_open(self) -> bool:
        """Check if MR is open/ongoing."""
        return self.state == "opened"


class GitHubIssue(BaseModel):
    """GitHub Issue model.

    Validates GitHub Issue data from gh CLI --json output.

    Attributes:
        number: Issue number
        title: Issue title
        state: Issue state ("open", "closed")
        author: Dict containing author information with 'login' key
        html_url: Issue URL
        labels: List of label names
        created_at: When the issue was created (ISO 8601 format)
        body: Optional issue description
        assignees: List of assignee information
    """

    model_config = ConfigDict(strict=True, validate_assignment=True)

    number: int = Field(..., description="Issue number", ge=1)
    title: str = Field(..., description="Issue title", min_length=1)
    state: str = Field(
        ...,
        description="Issue state",
        pattern=r"^(open|closed)$",
    )
    author: dict[str, Any] = Field(
        ...,
        description="Author information with 'login' key",
    )
    html_url: HttpUrl = Field(..., description="Issue URL")
    labels: list[str] = Field(
        default_factory=list,
        description="List of label names",
    )
    created_at: IsoDateTime = Field(
        default=None,
        description="When the issue was created (ISO 8601 format)",
    )
    body: str | None = Field(default=None, description="Issue description")
    assignees: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of assignee information",
    )

    def display_key(self) -> str:
        """Return formatted key for display."""
        return f"#{self.number}"

    def display_status(self) -> str:
        """Return normalized status string."""
        return self.state.upper()

    def is_open(self) -> bool:
        """Check if issue is open."""
        return self.state == "open"


class JiraWorkItem(BaseModel):
    """Jira Work Item model.

    Validates Jira issue data from acli CLI --json output.

    Attributes:
        key: Issue key (e.g., "PROJ-123")
        fields: Dict containing issue fields including:
            - summary: Issue title
            - status: Dict with 'name' key
            - priority: Dict with 'name' key
            - assignee: Dict with 'displayName' key (optional)
            - description: Issue description (optional)
        self: Issue URL (API endpoint)
    """

    model_config = ConfigDict(strict=True, validate_assignment=True)

    adapter_icon: str = "🔴"
    adapter_type: str = "jira"

    key: str = Field(
        ...,
        description="Issue key (e.g., PROJ-123)",
        pattern=r"^[A-Z][A-Z0-9]*-\d+$",
        min_length=3,
    )
    fields: dict[str, Any] = Field(
        ...,
        description="Issue fields including summary, status, priority",
    )
    self: HttpUrl = Field(..., description="Issue API URL")

    @property
    def summary(self) -> str:
        """Get the issue summary/title."""
        value = self.fields.get("summary", "")
        return str(value) if value is not None else ""

    @property
    def status(self) -> str:
        """Get the issue status name."""
        status_field = self.fields.get("status", {})
        return status_field.get("name", "Unknown") if isinstance(status_field, dict) else "Unknown"

    @property
    def priority(self) -> str:
        """Get the issue priority name."""
        priority_field = self.fields.get("priority", {})
        return priority_field.get("name", "None") if isinstance(priority_field, dict) else "None"

    @property
    def assignee(self) -> str | None:
        """Get the assignee display name."""
        assignee_field = self.fields.get("assignee")
        if isinstance(assignee_field, dict):
            return assignee_field.get("displayName")
        return None

    @property
    def url(self) -> str:
        """Get the browser URL for this issue."""
        # Convert API URL to browser URL
        url_str = str(self.self)
        return url_str.replace("/rest/api/2/issue/", "/browse/").rstrip("/")

    def display_key(self) -> str:
        """Return formatted key for display."""
        return self.key

    def display_status(self) -> str:
        """Return normalized status string."""
        status_name = self.status.upper()
        # Normalize common Jira statuses
        status_map = {
            "TO DO": "TODO",
            "IN PROGRESS": "IN PROGRESS",
            "DONE": "DONE",
            "BLOCKED": "BLOCKED",
            "CLOSED": "DONE",
            "RESOLVED": "DONE",
        }
        return status_map.get(status_name, status_name)

    def is_open(self) -> bool:
        """Check if work item is open/ongoing."""
        closed_statuses = {"done", "closed", "resolved"}
        return self.status.lower() not in closed_statuses


class TodoistTask(BaseModel):
    """Todoist Task model.

    Validates Todoist task data from the Todoist REST API.

    Attributes:
        id: Task ID
        content: Task title/description
        priority: Task priority (1-4 in Todoist API, 4=urgent, 1=normal)
        due: Due date information (optional)
        project_id: ID of the project this task belongs to
        project_name: Name of the project
        url: Task URL
        created_at: When the task was created (ISO 8601 format)
        is_completed: Whether the task is completed
        completed_at: When the task was completed (ISO 8601 format)
    """

    model_config = ConfigDict(strict=True, validate_assignment=True)

    adapter_icon: str = "📝"
    adapter_type: str = "todoist"

    id: str = Field(..., description="Task ID")
    content: str = Field(..., description="Task title/description", min_length=1)
    # NOTE: Todoist API priority is inverted from the UI:
    # API 1=normal (UI p4), 2=medium (UI p3), 3=high (UI p2), 4=urgent (UI p1)
    priority: int = Field(..., description="Task priority (1-4, 4=urgent)", ge=1, le=4)
    due: DueInfo | None = Field(default=None, description="Due date information")
    project_id: str = Field(..., description="Project ID")
    project_name: str = Field(..., description="Project name")
    url_field: HttpUrl = Field(..., description="Task URL", alias="url")
    created_at: str | None = Field(default=None, description="When the task was created")
    is_completed: bool = Field(default=False, description="Whether the task is completed")
    completed_at: str | None = Field(default=None, description="When the task was completed")

    @property
    def due_date(self) -> str | None:
        """Extract readable due date from due info."""
        if not self.due:
            return None
        return self.due.get("date") or self.due.get("datetime")

    @property
    def url(self) -> str:
        """Get URL as string for browser opening."""
        return str(self.url_field)

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

        Args:
            priority: Todoist API priority value (1-4)

        Returns:
            Standard priority label
        """
        mapping = {1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "HIGHEST"}
        return mapping.get(priority, "MEDIUM")
