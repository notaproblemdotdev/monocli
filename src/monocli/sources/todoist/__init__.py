"""Todoist source for work items.

Provides TodoistSource for fetching tasks from Todoist.
Implements PieceOfWorkSource protocol.
"""

from monocli import get_logger
from monocli.models import PieceOfWork
from monocli.sources.base import PieceOfWorkSource

from ._api import TodoistAdapter

logger = get_logger(__name__)


class TodoistSource(PieceOfWorkSource):
    """Source for Todoist tasks.

    Wraps the existing TodoistAdapter to provide PieceOfWork items.

    Example:
        source = TodoistSource(token="your-token")

        # Check if available
        if await source.is_available():
            # Fetch tasks
            items = await source.fetch_items()
            for item in items:
                print(f"{item.display_key()}: {item.title}")
    """

    def __init__(
        self,
        token: str,
        project_names: list[str] | None = None,
        show_completed: bool = False,
        show_completed_for_last: str | None = None,
    ) -> None:
        """Initialize the Todoist piece of work source.

        Args:
            token: Todoist API token
            project_names: Optional list of project names to filter by
            show_completed: Whether to include completed tasks
            show_completed_for_last: Show completed tasks from last N days
                ("24h", "48h", "72h", "7days")
        """
        self._adapter = TodoistAdapter(token)
        self.project_names = project_names
        self.show_completed = show_completed
        self.show_completed_for_last = show_completed_for_last

    @property
    def source_type(self) -> str:
        """Return the source type identifier."""
        return "todoist"

    @property
    def source_icon(self) -> str:
        """Return the source icon emoji."""
        return "📝"

    async def is_available(self) -> bool:
        """Check if the Todoist API is accessible (always True if token provided)."""
        return True  # API-based, available if we have a token

    async def check_auth(self) -> bool:
        """Check if the Todoist token is valid."""
        return await self._adapter.check_auth()

    async def fetch_items(self) -> list[PieceOfWork]:
        """Fetch tasks from Todoist.

        Returns:
            List of PieceOfWork items from Todoist.
        """
        logger.info(
            "Fetching Todoist tasks",
            projects=self.project_names,
            show_completed=self.show_completed,
        )
        items = await self._adapter.fetch_tasks(
            project_names=self.project_names,
            show_completed=self.show_completed,
            show_completed_for_last=self.show_completed_for_last,
        )
        # TodoistAdapter already returns TodoistPieceOfWork models
        # which implement the PieceOfWork protocol
        return items  # type: ignore[return-value]
