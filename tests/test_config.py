"""Tests for configuration management.

Tests for the Config class including loading from files,
environment variables, and error handling.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from monocli.config import Config, ConfigError, get_config


class TestConfigLoad:
    """Tests for Config.load method."""

    def test_load_empty_config(self, tmp_path: Path) -> None:
        """Test loading with no config files creates empty config."""
        # Create config with no files present
        config = Config.load(tmp_path / "nonexistent.yaml")
        assert config.gitlab_group is None
        assert config.jira_project is None

    def test_load_from_explicit_path(self, tmp_path: Path) -> None:
        """Test loading from explicit config file path."""
        config_file = tmp_path / "config.yaml"
        config_data = {"gitlab": {"group": "my-group"}, "jira": {"project": "PROJ"}}
        config_file.write_text(yaml.dump(config_data))

        config = Config.load(config_file)
        assert config.gitlab_group == "my-group"
        assert config.jira_project == "PROJ"

    def test_load_from_default_locations(self, tmp_path: Path) -> None:
        """Test loading from default config file locations."""
        config_file = tmp_path / ".monocli.yaml"
        config_data = {"gitlab": {"group": "default-group"}}
        config_file.write_text(yaml.dump(config_data))

        # Temporarily override CONFIG_PATHS
        with patch("monocli.config.CONFIG_PATHS", [config_file]):
            config = Config.load()
            assert config.gitlab_group == "default-group"


class TestConfigEnvironmentVariables:
    """Tests for environment variable overrides."""

    def test_gitlab_group_from_env(self) -> None:
        """Test MONOCLI_GITLAB_GROUP env var overrides config file."""
        with patch.dict(os.environ, {"MONOCLI_GITLAB_GROUP": "env-group"}):
            config = Config.load()
            assert config.gitlab_group == "env-group"

    def test_jira_project_from_env(self) -> None:
        """Test MONOCLI_JIRA_PROJECT env var overrides config file."""
        with patch.dict(os.environ, {"MONOCLI_JIRA_PROJECT": "ENVPROJ"}):
            config = Config.load()
            assert config.jira_project == "ENVPROJ"

    def test_env_var_overrides_file(self, tmp_path: Path) -> None:
        """Test env vars take precedence over config file."""
        config_file = tmp_path / "config.yaml"
        config_data = {"gitlab": {"group": "file-group"}}
        config_file.write_text(yaml.dump(config_data))

        with patch.dict(os.environ, {"MONOCLI_GITLAB_GROUP": "env-group"}):
            config = Config.load(config_file)
            assert config.gitlab_group == "env-group"

    def test_env_var_unset_uses_file_value(self, tmp_path: Path) -> None:
        """Test config file value used when env var not set."""
        config_file = tmp_path / "config.yaml"
        config_data = {"gitlab": {"group": "file-group"}}
        config_file.write_text(yaml.dump(config_data))

        # Ensure env var is not set
        with patch.dict(os.environ, {}, clear=True):
            config = Config.load(config_file)
            assert config.gitlab_group == "file-group"


class TestConfigRequireGitlabGroup:
    """Tests for require_gitlab_group method."""

    def test_require_gitlab_group_returns_value(self, tmp_path: Path) -> None:
        """Test require_gitlab_group returns the group when configured."""
        config_file = tmp_path / "config.yaml"
        config_data = {"gitlab": {"group": "my-group"}}
        config_file.write_text(yaml.dump(config_data))

        config = Config.load(config_file)
        assert config.require_gitlab_group() == "my-group"

    def test_require_gitlab_group_raises_when_missing(self) -> None:
        """Test require_gitlab_group raises ConfigError when not configured."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config.load(Path("/nonexistent/config.yaml"))

        with pytest.raises(ConfigError) as exc_info:
            config.require_gitlab_group()

        assert "GitLab group not configured" in str(exc_info.value)
        assert "MONOCLI_GITLAB_GROUP" in str(exc_info.value)
        assert "config.yaml" in str(exc_info.value)

    def test_require_gitlab_group_raises_with_empty_string(self, tmp_path: Path) -> None:
        """Test require_gitlab_group raises when group is empty string."""
        config_file = tmp_path / "config.yaml"
        config_data = {"gitlab": {"group": ""}}
        config_file.write_text(yaml.dump(config_data))

        config = Config.load(config_file)
        with pytest.raises(ConfigError):
            config.require_gitlab_group()


class TestConfigGetConfig:
    """Tests for get_config convenience function."""

    def test_get_config_returns_config_instance(self) -> None:
        """Test get_config returns a Config instance."""
        config = get_config()
        assert isinstance(config, Config)


class TestConfigFileErrors:
    """Tests for config file error handling."""

    def test_invalid_yaml_returns_empty_config(self, tmp_path: Path) -> None:
        """Test invalid YAML is handled gracefully."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [")

        config = Config.load(config_file)
        # Should not raise, returns empty config
        assert config.gitlab_group is None

    def test_nonexistent_file_returns_empty_config(self) -> None:
        """Test nonexistent file is handled gracefully."""
        config = Config.load(Path("/definitely/does/not/exist.yaml"))
        assert config.gitlab_group is None
        assert config.jira_project is None
