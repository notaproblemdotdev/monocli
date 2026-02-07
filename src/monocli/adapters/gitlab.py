"""GitLab CLI adapter for fetching merge requests.

Provides GitLabAdapter class that uses glab CLI to fetch merge requests
assigned to or authored by the current user.
"""

from monocli.async_utils import CLIAdapter
from monocli.exceptions import CLIAuthError, CLINotFoundError
from monocli.models import MergeRequest


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
        state: str = "opened",
        author: str = "@me",
    ) -> list[MergeRequest]:
        """Fetch MRs assigned to or authored by current user.

        Uses glab mr list with --json flag to fetch merge requests.
        Filters by author and state to show only relevant MRs.

        Args:
            state: MR state filter ("opened", "closed", "merged", "locked")
            author: Author filter ("@me" for current user, or username)

        Returns:
            List of validated MergeRequest models

        Raises:
            CLINotFoundError: If glab is not installed
            CLIAuthError: If glab is not authenticated

        Example:
            adapter = GitLabAdapter()

            # Fetch all open MRs by current user
            mrs = await adapter.fetch_assigned_mrs(state="opened")

            # Fetch merged MRs
            merged = await adapter.fetch_assigned_mrs(state="merged")
        """
        args = [
            "mr",
            "list",
            "--json",
            f"--author={author}",
            f"--state={state}",
        ]
        return await self.fetch_and_parse(args, MergeRequest)

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
        try:
            await self.run(["auth", "status"], check=True)
            return True
        except (CLIAuthError, CLINotFoundError):
            return False
