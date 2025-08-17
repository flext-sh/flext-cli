"""Tests for utils configuration in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_core.constants import FlextConstants

from flext_cli import CLIConfig, CLISettings, get_config, get_settings

# Constants
_API = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
_CORE = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXCORE_PORT}"
_SVC = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_SERVICE_PORT}"
EXPECTED_DATA_COUNT = 3


class TestCLIConfig:
    """Test cases for CLIConfig."""

    def test_config_creation_with_defaults(self) -> None:
        """Test CLI config creation with default values."""
        config = CLIConfig()

        if config.api_url != _API:
            raise AssertionError(f"Expected {_API}, got {config.api_url}")
        assert config.output_format == "table"
        if config.timeout != 30:
            raise AssertionError(f"Expected {30}, got {config.timeout}")
        assert config.profile == "default"
        if config.debug:
            raise AssertionError(f"Expected False, got {config.debug}")
        assert config.quiet is False
        if config.verbose:
            raise AssertionError(f"Expected False, got {config.verbose}")
        assert config.no_color is False

    def test_config_creation_with_custom_values(self, cli_config: CLIConfig) -> None:
        """Test CLI config creation with custom values."""
        if cli_config.api_url != _API:
            raise AssertionError(f"Expected {_API}, got {cli_config.api_url}")
        assert cli_config.output_format == "json"
        if cli_config.timeout != 30:
            raise AssertionError(f"Expected {30}, got {cli_config.timeout}")
        assert cli_config.profile == "test"
        if not (cli_config.debug):
            raise AssertionError(f"Expected True, got {cli_config.debug}")
        assert cli_config.verbose is True
        if not (cli_config.no_color):
            raise AssertionError(f"Expected True, got {cli_config.no_color}")

    def test_config_directory_defaults(self) -> None:
        """Test configuration directory defaults."""
        config = CLIConfig()

        expected_config_dir = Path.home() / ".flext"
        expected_cache_dir = Path.home() / ".flext" / "cache"
        expected_log_dir = Path.home() / ".flext" / "logs"

        if config.config_dir != expected_config_dir:
            raise AssertionError(
                f"Expected {expected_config_dir}, got {config.config_dir}",
            )
        assert config.cache_dir == expected_cache_dir
        if config.log_dir != expected_log_dir:
            raise AssertionError(f"Expected {expected_log_dir}, got {config.log_dir}")

    def test_config_custom_directories(self) -> None:
        """Test configuration with custom directories."""
        custom_config_dir = Path("/custom/config")
        custom_cache_dir = Path("/custom/cache")
        custom_log_dir = Path("/custom/logs")

        config = CLIConfig(
            config_dir=custom_config_dir,
            cache_dir=custom_cache_dir,
            log_dir=custom_log_dir,
        )

        if config.config_dir != custom_config_dir:
            raise AssertionError(
                f"Expected {custom_config_dir}, got {config.config_dir}",
            )
        assert config.cache_dir == custom_cache_dir
        if config.log_dir != custom_log_dir:
            raise AssertionError(f"Expected {custom_log_dir}, got {config.log_dir}")

    def test_config_validation(self) -> None:
        """Test config field validation."""
        # Test valid timeout
        config = CLIConfig(timeout=60)
        if config.timeout != 60:
            raise AssertionError(f"Expected {60}, got {config.timeout}")

        # Test valid output format
        config = CLIConfig(output_format="json")
        if config.output_format != "json":
            raise AssertionError(f"Expected {'json'}, got {config.output_format}")

    def test_config_field_constraints(self) -> None:
        """Test config field constraints."""
        # API URL should be a string
        config = CLIConfig(api_url="https://api.example.com")
        if config.api_url != "https://api.example.com":
            raise AssertionError(
                f"Expected {'https://api.example.com'}, got {config.api_url}",
            )

        # Profile should be a string
        config = CLIConfig(profile="production")
        if config.profile != "production":
            raise AssertionError(f"Expected {'production'}, got {config.profile}")


class TestCLISettings:
    """Test cases for CLISettings."""

    def test_settings_creation_with_defaults(self) -> None:
        """Test CLI settings creation with default values."""
        settings = CLISettings()

        if settings.project_name != "flext-cli":
            raise AssertionError(f"Expected {'flext-cli'}, got {settings.project_name}")
        assert settings.project_version == "0.9.0"
        expected_desc = "FLEXT CLI - Developer Command Line Interface"
        if settings.project_description != expected_desc:
            raise AssertionError(
                f"Expected {expected_desc}, got {settings.project_description}",
            )
        if settings.debug:
            raise AssertionError(f"Expected False, got {settings.debug}")
        assert settings.log_level == "INFO"
        assert settings.config_path is None

    def test_settings_creation_with_custom_values(
        self,
        cli_settings: CLISettings,
    ) -> None:
        """Test CLI settings creation with custom values."""
        if cli_settings.project_name != "test-cli":
            raise AssertionError(
                f"Expected {'test-cli'}, got {cli_settings.project_name}",
            )
        assert cli_settings.project_version == "0.9.0"
        if cli_settings.project_description != "Test CLI Library":
            raise AssertionError(
                f"Expected {'Test CLI Library'}, got {cli_settings.project_description}",
            )
        if not (cli_settings.debug):
            raise AssertionError(f"Expected True, got {cli_settings.debug}")
        if cli_settings.log_level != "DEBUG":
            raise AssertionError(f"Expected {'DEBUG'}, got {cli_settings.log_level}")

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
        settings = CLISettings()

        # Verify environment variables are loaded
        if not (settings.debug):
            raise AssertionError(f"Expected True, got {settings.debug}")
        if settings.log_level != "WARNING":
            raise AssertionError(f"Expected {'WARNING'}, got {settings.log_level}")
        assert settings.config_path == "/custom/config.yaml"

    def test_settings_case_insensitive_env_vars(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test case insensitive environment variable loading."""
        monkeypatch.setenv("flext_cli_debug", "true")  # lowercase
        monkeypatch.setenv("FLEXT_CLI_LOG_LEVEL", "ERROR")  # uppercase

        settings = CLISettings()

        if not (settings.debug):
            raise AssertionError(f"Expected True, got {settings.debug}")
        if settings.log_level != "ERROR":
            raise AssertionError(f"Expected {'ERROR'}, got {settings.log_level}")

    def test_settings_model_config(self) -> None:
        """Test settings model configuration."""
        settings = CLISettings()

        # Verify model configuration
        config = settings.model_config
        if config["env_prefix"] != "FLEXT_CLI_":
            raise AssertionError(f"Expected {'FLEXT_CLI_'}, got {config['env_prefix']}")
        assert config["env_file"] == ".env"
        if config["env_file_encoding"] != "utf-8":
            raise AssertionError(
                f"Expected {'utf-8'}, got {config['env_file_encoding']}",
            )
        if config["case_sensitive"]:
            raise AssertionError(f"Expected False, got {config['case_sensitive']}")


class TestConfigurationFunctions:
    """Test configuration utility functions."""

    def test_get_config_function(self) -> None:
        """Test get_config function."""
        config = get_config()

        assert isinstance(config, CLIConfig)
        if config.api_url != _API:
            raise AssertionError(f"Expected {_API}, got {config.api_url}")
        assert config.output_format == "table"
        if config.profile != "default":
            raise AssertionError(f"Expected {'default'}, got {config.profile}")

    def test_get_settings_function(self) -> None:
        """Test get_settings function."""
        settings = get_settings()

        assert isinstance(settings, CLISettings)
        if settings.project_name != "flext-cli":
            raise AssertionError(f"Expected {'flext-cli'}, got {settings.project_name}")
        assert settings.project_version == "0.9.0"

    def test_multiple_config_instances(self) -> None:
        """Test multiple config instances are independent."""
        config1 = get_config()
        config2 = get_config()

        # Should be separate instances
        assert config1 is not config2

        # But with same default values
        if config1.api_url != config2.api_url:
            raise AssertionError(f"Expected {config2.api_url}, got {config1.api_url}")
        assert config1.profile == config2.profile

    def test_multiple_settings_instances(self) -> None:
        """Test multiple settings instances are independent."""
        settings1 = get_settings()
        settings2 = get_settings()

        # Should be separate instances
        assert settings1 is not settings2

        # But with same default values
        if settings1.project_name != settings2.project_name:
            raise AssertionError(
                f"Expected {settings2.project_name}, got {settings1.project_name}",
            )
        assert settings1.project_version == settings2.project_version


class TestConfigurationIntegration:
    """Integration tests for configuration components."""

    def test_config_and_settings_compatibility(self) -> None:
        """Test config and settings work together."""
        config = get_config()
        settings = get_settings()

        # Both should be independent but compatible
        assert isinstance(config, CLIConfig)
        assert isinstance(settings, CLISettings)

        # Both should have debug capability
        assert hasattr(config, "debug")
        assert hasattr(settings, "debug")

    def test_flext_core_integration(self) -> None:
        """Test integration with flext-core patterns."""
        config = CLIConfig()
        settings = CLISettings()

        # Should inherit from flext-core base classes
        # This tests that our imports and inheritance work correctly
        assert hasattr(config, "model_dump")  # Pydantic method
        assert hasattr(settings, "model_dump")  # Pydantic method

    def test_path_handling(self, temp_dir: Path) -> None:
        """Test path handling in configuration."""
        custom_dir = temp_dir / "custom"

        config = CLIConfig(
            config_dir=custom_dir,
            cache_dir=custom_dir / "cache",
            log_dir=custom_dir / "logs",
        )

        assert isinstance(config.config_dir, Path)
        assert isinstance(config.cache_dir, Path)
        assert isinstance(config.log_dir, Path)

        if config.config_dir != custom_dir:
            raise AssertionError(f"Expected {custom_dir}, got {config.config_dir}")
        assert config.cache_dir == custom_dir / "cache"
        if config.log_dir != custom_dir / "logs":
            raise AssertionError(
                f"Expected {custom_dir / 'logs'}, got {config.log_dir}",
            )
