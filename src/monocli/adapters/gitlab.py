"""GitLab CLI adapter for fetching merge requests.

Provides GitLabAdapter class that uses glab CLI to fetch merge requests
assigned to or authored by the current user.
"""

from monocli import get_logger
from monocli.async_utils import CLIAdapter
from monocli.exceptions import CLIAuthError, CLINotFoundError
from monocli.models import MergeRequest

logger = get_logger(__name__)


class GitLabAdapter(CLIAdapter):
    """Adapter for GitLab CLI (glab) operations.

        Fetches merge requests using glab's JSON output format and validates
    them into Pydantic MergeRequest models.

        Example:
            adapter = GitLabAdapter()

            # Check if glab is available
            if adapter.is_available():
                # Fetch MRs assigned to current user
                mrs = await adapter.fetch_assigned_mrs()
                for mr in mrs:
                    print(f"{mr.display_key()}: {mr.title}")

            # Explicitly check authentication
            is_authenticated = await adapter.check_auth()
    """

    def __init__(self) -> None:
        """Initialize GitLab adapter with cli_name='glab'."""
        super().__init__("glab")

    async def fetch_assigned_mrs(
        self,
        group: str = "axpo-pl",
        assignee: str = "@me",
    ) -> list[MergeRequest]:
        """Fetch MRs assigned to current user.

        Uses glab mr list with --output json to fetch merge requests.
        Filters by assignee and group to show only relevant MRs.

        Args:
            group: GitLab group to search (e.g., "axpo-pl")
            assignee: Assignee filter ("@me" for current user, or username)

        Returns:
            List of validated MergeRequest models

        Raises:
            CLINotFoundError: If glab is not installed
            CLIAuthError: If glab is not authenticated

        Example:
            adapter = GitLabAdapter()

            # Fetch all open MRs assigned to current user
            mrs = await adapter.fetch_assigned_mrs()

            # Fetch MRs for different group
            mrs = await adapter.fetch_assigned_mrs(group="my-group")
        """
        logger.info("Fetching merge requests", group=group, assignee=assignee)
        args = [
            "mr",
            "list",
            "--all",
            "--group",
            group,
            "--assignee",
            assignee,
            "--output",
            "json",
        ]
        try:
            result = await self.fetch_and_parse(args, MergeRequest)
            logger.info("Fetched merge requests", count=len(result))
            return result
        except (CLIAuthError, CLINotFoundError):
            logger.warning("Failed to fetch merge requests", group=group)
            raise

    async def check_auth(self) -> bool:
        """Check if glab is authenticated.

        Runs glab auth status to verify authentication without
        triggering any interactive prompts.

        Returns:
            True if glab is authenticated, False otherwise

        Example:
            adapter = GitLabAdapter()

            if await adapter.check_auth():
                mrs = await adapter.fetch_assigned_mrs()
            else:
                print("Please run: glab auth login")
        """
        logger.debug("Checking GitLab authentication")
        try:
            await self.run(["auth", "status"], check=True)
            logger.debug("GitLab authenticated")
            return True
        except (CLIAuthError, CLINotFoundError):
            logger.warning("GitLab not authenticated")
            return False
