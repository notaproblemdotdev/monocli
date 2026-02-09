"""Configuration management for monocli.

Reads configuration from environment variables and config files.
Priority: environment variables > config file > defaults
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from monocli import get_logger

logger = get_logger(__name__)

# Default config locations (in priority order)
CONFIG_PATHS = [
    Path.home() / ".config" / "monocli" / "config.yaml",
    Path.home() / ".monocli.yaml",
    Path.cwd() / ".monocli.yaml",
]


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""

    pass


class Config:
    """Configuration manager for monocli.

    Loads configuration from environment variables and YAML config files.
    Environment variables take precedence over config file values.

    Environment variables:
        MONOCLI_GITLAB_GROUP: Default GitLab group to fetch MRs from
        MONOCLI_JIRA_PROJECT: Default Jira project to fetch issues from

    Config file format (YAML):
        gitlab:
          group: "my-group"  # Default group for MR queries
        jira:
          project: "PROJ"    # Default project for issue queries

    Example:
        config = Config.load()
        group = config.gitlab_group  # Returns env var or config file value
    """

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize config with data dictionary.

        Args:
            data: Configuration dictionary loaded from file/env.
        """
        self._data = data

    @classmethod
    def load(cls, path: Path | None = None) -> Config:
        """Load configuration from file and environment.

        Args:
            path: Optional explicit config file path. If not provided,
                  searches default locations.

        Returns:
            Config instance with loaded settings.
        """
        # Load from file if found
        data: dict[str, Any] = {}

        if path:
            data = cls._load_file(path)
        else:
            for config_path in CONFIG_PATHS:
                if config_path.exists():
                    logger.debug("Loading config from", path=str(config_path))
                    data = cls._load_file(config_path)
                    break

        # Override with environment variables
        data = cls._apply_env_vars(data)

        return cls(data)

    @classmethod
    def _load_file(cls, path: Path) -> dict[str, Any]:
        """Load YAML config file.

        Args:
            path: Path to YAML config file.

        Returns:
            Dictionary with configuration values.
        """
        try:
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning("Failed to load config file", path=str(path), error=str(e))
            return {}

    @classmethod
    def _apply_env_vars(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Apply environment variable overrides.

        Args:
            data: Current configuration dictionary.

        Returns:
            Updated dictionary with env var overrides.
        """
        # Ensure nested dicts exist
        if "gitlab" not in data:
            data["gitlab"] = {}
        if "jira" not in data:
            data["jira"] = {}

        # GitLab settings
        gitlab_group = os.getenv("MONOCLI_GITLAB_GROUP")
        if gitlab_group:
            data["gitlab"]["group"] = gitlab_group

        # Jira settings
        jira_project = os.getenv("MONOCLI_JIRA_PROJECT")
        if jira_project:
            data["jira"]["project"] = jira_project

        return data

    @property
    def gitlab_group(self) -> str | None:
        """Get the configured GitLab group.

        Returns:
            GitLab group name or None if not configured.
        """
        return self._data.get("gitlab", {}).get("group")

    @property
    def jira_project(self) -> str | None:
        """Get the configured Jira project.

        Returns:
            Jira project key or None if not configured.
        """
        return self._data.get("jira", {}).get("project")

    def require_gitlab_group(self) -> str:
        """Get GitLab group, raising error if not configured.

        Returns:
            GitLab group name.

        Raises:
            ConfigError: If group is not configured.
        """
        group = self.gitlab_group
        if not group:
            raise ConfigError(
                "GitLab group not configured.\n"
                "\nSet one of:\n"
                "  - Environment variable: export MONOCLI_GITLAB_GROUP='your-group'\n"
                "  - Config file: ~/.config/monocli/config.yaml\n"
                "\nConfig file format:\n"
                "  gitlab:\n"
                "    group: your-group"
            )
        return group


def get_config() -> Config:
    """Get the global configuration instance.

    Returns:
        Loaded Config instance.
    """
    return Config.load()
