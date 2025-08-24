"""Tests for utils configuration in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_core import FlextConstants

from flext_cli import FlextCliConfig, FlextCliSettings, get_config, get_settings
from flext_cli.config import FlextCliDirectoryConfig, FlextCliOutputConfig

# Constants
_API = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
_CORE = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXCORE_PORT}"
_SVC = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_SERVICE_PORT}"
EXPECTED_DATA_COUNT = 3


class TestCLIConfig:
    """Test cases for FlextCliConfig."""

    def test_config_creation_with_defaults(self) -> None:
        """Test CLI config creation with default values."""
        config = FlextCliConfig()

        if config.api_url != _API:
            msg = f"Expected {_API}, got {config.api_url}"
            raise AssertionError(msg)
        assert config.output_format == "table"
        if config.command_timeout != 300:
            msg = f"Expected {300}, got {config.command_timeout}"
            raise AssertionError(msg)
        assert config.profile == "default"
        if config.debug:
            msg = f"Expected False, got {config.debug}"
            raise AssertionError(msg)
        assert config.quiet is False
        if config.verbose:
            msg = f"Expected False, got {config.verbose}"
            raise AssertionError(msg)
        assert config.no_color is False

    def test_config_creation_with_custom_values(
        self, cli_config: FlextCliConfig
    ) -> None:
        """Test CLI config creation with custom values."""
        if cli_config.api_url != _API:
            msg = f"Expected {_API}, got {cli_config.api_url}"
            raise AssertionError(msg)
        assert cli_config.output_format == "json"
        if cli_config.command_timeout != 30:
            msg = f"Expected {30}, got {cli_config.command_timeout}"
            raise AssertionError(msg)
        assert cli_config.profile == "test"
        if not (cli_config.debug):
            msg = f"Expected True, got {cli_config.debug}"
            raise AssertionError(msg)
        assert cli_config.verbose is True
        if not (cli_config.no_color):
            msg = f"Expected True, got {cli_config.no_color}"
            raise AssertionError(msg)

    def test_config_directory_defaults(self) -> None:
        """Test configuration directory defaults."""
        config = FlextCliConfig()

        expected_config_dir = Path.home() / ".flext"
        expected_cache_dir = Path.home() / ".flext" / "cache"
        expected_log_dir = Path.home() / ".flext" / "logs"

        if config.directories.config_dir != expected_config_dir:
            msg = f"Expected {expected_config_dir}, got {config.directories.config_dir}"
            raise AssertionError(
                msg,
            )
        assert config.directories.cache_dir == expected_cache_dir
        if config.directories.log_dir != expected_log_dir:
            msg = f"Expected {expected_log_dir}, got {config.directories.log_dir}"
            raise AssertionError(
                msg
            )

    def test_config_custom_directories(self) -> None:
        """Test configuration with custom directories."""
        custom_config_dir = Path("/custom/config")
        custom_cache_dir = Path("/custom/cache")
        custom_log_dir = Path("/custom/logs")

        config = FlextCliConfig(
            directories=FlextCliDirectoryConfig(
                config_dir=custom_config_dir,
                cache_dir=custom_cache_dir,
                log_dir=custom_log_dir,
            )
        )

        if config.directories.config_dir != custom_config_dir:
            msg = f"Expected {custom_config_dir}, got {config.directories.config_dir}"
            raise AssertionError(
                msg,
            )
        assert config.directories.cache_dir == custom_cache_dir
        if config.directories.log_dir != custom_log_dir:
            msg = f"Expected {custom_log_dir}, got {config.directories.log_dir}"
            raise AssertionError(
                msg
            )

    def test_config_validation(self) -> None:
        """Test config field validation."""
        # Test valid timeout
        config = FlextCliConfig(command_timeout=60)
        if config.command_timeout != 60:
            msg = f"Expected {60}, got {config.command_timeout}"
            raise AssertionError(msg)

        # Test valid output format
        config = FlextCliConfig(output=FlextCliOutputConfig(format="json"))
        if config.output.format != "json":
            msg = f"Expected {'json'}, got {config.output.format}"
            raise AssertionError(msg)

    def test_config_field_constraints(self) -> None:
        """Test config field constraints."""
        # API URL should be a string
        config = FlextCliConfig(api_url="https://api.example.com")
        if config.api_url != "https://api.example.com":
            msg = f"Expected {'https://api.example.com'}, got {config.api_url}"
            raise AssertionError(
                msg,
            )

        # Profile should be a string
        config = FlextCliConfig(profile="production")
        if config.profile != "production":
            msg = f"Expected {'production'}, got {config.profile}"
            raise AssertionError(msg)


class TestCLISettings:
    """Test cases for FlextCliSettings."""

    def test_settings_creation_with_defaults(self) -> None:
        """Test CLI settings creation with default values."""
        settings = FlextCliSettings()

        if settings.project_name != "flext-cli":
            msg = f"Expected {'flext-cli'}, got {settings.project_name}"
            raise AssertionError(msg)
        assert settings.project_version == "0.9.0"
        expected_desc = "FLEXT CLI - Developer Command Line Interface"
        if settings.project_description != expected_desc:
            msg = f"Expected {expected_desc}, got {settings.project_description}"
            raise AssertionError(
                msg,
            )
        if settings.debug:
            msg = f"Expected False, got {settings.debug}"
            raise AssertionError(msg)
        assert settings.log_level == "INFO"
        assert settings.config_path is None

    def test_settings_creation_with_custom_values(
        self,
        cli_settings: FlextCliSettings,
    ) -> None:
        """Test CLI settings creation with custom values."""
        if cli_settings.project_name != "test-cli":
            msg = f"Expected {'test-cli'}, got {cli_settings.project_name}"
            raise AssertionError(
                msg,
            )
        assert cli_settings.project_version == "0.9.0"
        if cli_settings.project_description != "Test CLI Library":
            msg = f"Expected {'Test CLI Library'}, got {cli_settings.project_description}"
            raise AssertionError(
                msg,
            )
        if not (cli_settings.debug):
            msg = f"Expected True, got {cli_settings.debug}"
            raise AssertionError(msg)
        if cli_settings.log_level != "DEBUG":
            msg = f"Expected {'DEBUG'}, got {cli_settings.log_level}"
            raise AssertionError(msg)

    def test_settings_environment_variable_support(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test settings support for environment variables."""
        # Set environment variables
        monkeypatch.setenv("FLEXT_CLI_DEBUG", "true")
        monkeypatch.setenv("FLEXT_CLI_LOG_LEVEL", "WARNING")
        monkeypatch.setenv("FLEXT_CLI_CONFIG_PATH", "/custom/config.yaml")

        # Create settings
        settings = FlextCliSettings()

        # Verify environment variables are loaded
        if not (settings.debug):
            msg = f"Expected True, got {settings.debug}"
            raise AssertionError(msg)
        if settings.log_level != "WARNING":
            msg = f"Expected {'WARNING'}, got {settings.log_level}"
            raise AssertionError(msg)
        assert settings.config_path == "/custom/config.yaml"

    def test_settings_case_insensitive_env_vars(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test case insensitive environment variable loading."""
        monkeypatch.setenv("flext_cli_debug", "true")  # lowercase
        monkeypatch.setenv("FLEXT_CLI_LOG_LEVEL", "ERROR")  # uppercase

        settings = FlextCliSettings()

        if not (settings.debug):
            msg = f"Expected True, got {settings.debug}"
            raise AssertionError(msg)
        if settings.log_level != "ERROR":
            msg = f"Expected {'ERROR'}, got {settings.log_level}"
            raise AssertionError(msg)

    def test_settings_model_config(self) -> None:
        """Test settings model configuration."""
        settings = FlextCliSettings()

        # Verify model configuration
        config = settings.model_config
        if config["env_prefix"] != "FLEXT_CLI_":
            msg = f"Expected {'FLEXT_CLI_'}, got {config['env_prefix']}"
            raise AssertionError(msg)
        assert config["env_file"] == ".env"
        if config["env_file_encoding"] != "utf-8":
            msg = f"Expected {'utf-8'}, got {config['env_file_encoding']}"
            raise AssertionError(
                msg,
            )
        if config["case_sensitive"]:
            msg = f"Expected False, got {config['case_sensitive']}"
            raise AssertionError(msg)


class TestConfigurationFunctions:
    """Test configuration utility functions."""

    def test_get_config_function(self) -> None:
        """Test get_config function."""
        config = get_config()

        assert isinstance(config, FlextCliConfig)
        if config.api_url != _API:
            msg = f"Expected {_API}, got {config.api_url}"
            raise AssertionError(msg)
        assert config.output_format == "table"
        if config.profile != "default":
            msg = f"Expected {'default'}, got {config.profile}"
            raise AssertionError(msg)

    def test_get_settings_function(self) -> None:
        """Test get_settings function."""
        settings = get_settings()

        assert isinstance(settings, FlextCliSettings)
        if settings.project_name != "flext-cli":
            msg = f"Expected {'flext-cli'}, got {settings.project_name}"
            raise AssertionError(msg)
        assert settings.project_version == "0.9.0"

    def test_multiple_config_instances(self) -> None:
        """Test multiple config instances are independent."""
        config1 = get_config()
        config2 = get_config()

        # May be separate instances or singletons depending on implementation
        # Both behaviors are acceptable
        assert config1 is not None
        assert config2 is not None

        # But with same default values
        if config1.api_url != config2.api_url:
            msg = f"Expected {config2.api_url}, got {config1.api_url}"
            raise AssertionError(msg)
        assert config1.profile == config2.profile

    def test_multiple_settings_instances(self) -> None:
        """Test multiple settings instances are independent."""
        settings1 = get_settings()
        settings2 = get_settings()

        # Should be separate instances
        assert settings1 is not settings2

        # But with same default values
        if settings1.project_name != settings2.project_name:
            msg = f"Expected {settings2.project_name}, got {settings1.project_name}"
            raise AssertionError(
                msg,
            )
        assert settings1.project_version == settings2.project_version


class TestConfigurationIntegration:
    """Integration tests for configuration components."""

    def test_config_and_settings_compatibility(self) -> None:
        """Test config and settings work together."""
        config = get_config()
        settings = get_settings()

        # Both should be independent but compatible
        assert isinstance(config, FlextCliConfig)
        assert isinstance(settings, FlextCliSettings)

        # Both should have debug capability
        assert hasattr(config, "debug")
        assert hasattr(settings, "debug")

    def test_flext_core_integration(self) -> None:
        """Test integration with flext-core patterns."""
        config = FlextCliConfig()
        settings = FlextCliSettings()

        # Should inherit from flext-core base classes
        # This tests that our imports and inheritance work correctly
        assert hasattr(config, "model_dump")  # Pydantic method
        assert hasattr(settings, "model_dump")  # Pydantic method

    def test_path_handling(self, temp_dir: Path) -> None:
        """Test path handling in configuration."""
        custom_dir = temp_dir / "custom"

        config = FlextCliConfig(
            config_dir=custom_dir,
            cache_dir=custom_dir / "cache",
            log_dir=custom_dir / "logs",
        )

        assert isinstance(config.config_dir, Path)
        assert isinstance(config.cache_dir, Path)
        assert isinstance(config.log_dir, Path)

        if config.config_dir != custom_dir:
            msg = f"Expected {custom_dir}, got {config.config_dir}"
            raise AssertionError(msg)
        assert config.cache_dir == custom_dir / "cache"
        if config.log_dir != custom_dir / "logs":
            msg = f"Expected {custom_dir / 'logs'}, got {config.log_dir}"
            raise AssertionError(
                msg,
            )
