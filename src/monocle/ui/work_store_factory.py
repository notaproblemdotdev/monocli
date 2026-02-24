"""Factory for creating WorkStore instances with configured sources.

Provides a clean separation between WorkStore creation and UI code.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from monocle import get_logger
from monocle.db import WorkStore

if TYPE_CHECKING:
    from monocle.config import Config
    from monocle.sources.registry import SourceRegistry

logger = get_logger(__name__)


def create_work_store(config: Config) -> WorkStore:
    """Create a WorkStore instance with all configured sources.

    This factory function initializes the source registry with all
    available sources (GitLab, GitHub, Jira, Todoist) based on the
    provided configuration.

    Args:
        config: Application configuration.

    Returns:
        Configured WorkStore instance ready for data fetching.

    Example:
        from monocle.config import get_config
        from monocle.ui.work_store_factory import create_work_store

        config = get_config()
        store = create_work_store(config)
        result = await store.get_code_reviews("assigned")
    """
    from monocle.sources import SourceRegistry

    registry = SourceRegistry()

    _register_code_review_sources(registry, config)
    _register_work_sources(registry, config)
    _register_azuredevops(registry, config)

    return WorkStore(
        source_registry=registry,
        code_review_ttl=config.cache_ttl,
        work_item_ttl=config.cache_ttl * 2,  # Work items change less frequently
    )


def _register_code_review_sources(registry: SourceRegistry, config: Config) -> None:
    """Register all configured code review sources."""
    _register_gitlab(registry, config)
    _register_github(registry)


def _register_work_sources(registry: SourceRegistry, config: Config) -> None:
    """Register all configured work item sources."""
    _register_github_work_items(registry)
    _register_jira(registry, config)
    _register_todoist(registry, config)


def _register_gitlab(registry: SourceRegistry, config: Config) -> None:
    """Register GitLab source."""
    from monocle.sources import GitLabSource

    try:
        group = config.gitlab_group
        gitlab_source = GitLabSource(group=group)
        registry.register_code_review_source(gitlab_source)
        logger.debug("Registered GitLab source")
    except Exception as e:
        logger.warning("Failed to initialize GitLab source", error=str(e))


def _register_github(registry: SourceRegistry) -> None:
    """Register GitHub source."""
    from monocle.sources import GitHubSource

    try:
        github_source = GitHubSource()
        registry.register_code_review_source(github_source)
        logger.debug("Registered GitHub source")
    except Exception as e:
        logger.warning("Failed to initialize GitHub source", error=str(e))


def _register_github_work_items(registry: SourceRegistry) -> None:
    """Register GitHub source for work items (issues)."""
    from monocle.sources import GitHubSource

    try:
        github_source = GitHubSource()
        registry.register_piece_of_work_source(github_source)
        logger.debug("Registered GitHub work source")
    except Exception as e:
        logger.warning("Failed to initialize GitHub work source", error=str(e))


def _register_jira(registry: SourceRegistry, config: Config) -> None:
    """Register Jira source."""
    from monocle.sources import JiraSource

    try:
        base_url = config.jira_base_url
        jira_source = JiraSource(base_url=base_url)
        registry.register_piece_of_work_source(jira_source)
        logger.debug("Registered Jira source")
    except Exception as e:
        logger.warning("Failed to initialize Jira source", error=str(e))


def _register_todoist(registry: SourceRegistry, config: Config) -> None:
    """Register Todoist source if token is available."""
    from monocle.sources import TodoistSource

    if not config.todoist_token:
        logger.debug("Todoist not configured, skipping")
        return

    try:
        todoist_source = TodoistSource(
            token=config.todoist_token,
            project_names=config.todoist_projects,
            show_completed=config.todoist_show_completed,
            show_completed_for_last=config.todoist_show_completed_for_last,
        )
        registry.register_piece_of_work_source(todoist_source)
        logger.debug("Registered Todoist source")
    except Exception as e:
        logger.warning("Failed to initialize Todoist source", error=str(e))


def _register_azuredevops(registry: SourceRegistry, config: Config) -> None:
    """Register Azure DevOps source if configured.

    AzureDevOpsSource implements both CodeReviewSource and PieceOfWorkSource,
    so it is registered for both interfaces.
    """
    from monocle.sources import AzureDevOpsSource

    token = config.azuredevops_token
    organizations = config.azuredevops_organizations

    if not token or not organizations:
        logger.debug("Azure DevOps not configured, skipping")
        return

    try:
        azuredevops_source = AzureDevOpsSource(
            token=token,
            organizations=organizations,
        )
        registry.register_code_review_source(azuredevops_source)
        registry.register_piece_of_work_source(azuredevops_source)
        logger.debug("Registered Azure DevOps source")
    except Exception as e:
        logger.warning("Failed to initialize Azure DevOps source", error=str(e))
