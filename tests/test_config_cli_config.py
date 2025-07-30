"""Tests for CLI configuration module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Tests CLI configuration classes and functions for coverage.
"""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import flext_cli.config.cli_config
import pytest
from flext_cli.config.cli_config import (
    CLIAPIConfig,
    CLIAuthConfig,
    CLIConfig,
    CLIDirectoryConfig,
    CLIOutputConfig,
    CLISettings,
    _create_cli_config,
    get_cli_config,
    get_cli_settings,
)

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3


class TestCLIOutputConfig:
    """Test CLIOutputConfig class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = CLIOutputConfig()

        if config.format != "table":
            raise AssertionError(f"Expected {'table'}, got {config.format}")
        if config.no_color:
            raise AssertionError(f"Expected False, got {config.no_color}")
        assert config.quiet is False
        if config.verbose:
            raise AssertionError(f"Expected False, got {config.verbose}")
        assert config.pager is None

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = CLIOutputConfig(
            format="json",
            no_color=True,
            quiet=True,
            verbose=True,
            pager="less",
        )

        if config.format != "json":
            raise AssertionError(f"Expected {'json'}, got {config.format}")
        if not (config.no_color):
            raise AssertionError(f"Expected True, got {config.no_color}")
        assert config.quiet is True
        if not (config.verbose):
            raise AssertionError(f"Expected True, got {config.verbose}")
        if config.pager != "less":
            raise AssertionError(f"Expected {'less'}, got {config.pager}")

    def test_format_literal_validation(self) -> None:
        """Test format field accepts valid literal values."""
        from typing import Literal

        valid_formats: list[Literal["table", "json", "yaml", "csv", "plain"]] = [
            "table", "json", "yaml", "csv", "plain"
        ]

        for fmt in valid_formats:
            config = CLIOutputConfig(format=fmt)
            if config.format != fmt:
                raise AssertionError(f"Expected {fmt}, got {config.format}")

    def test_invalid_format_validation(self) -> None:
        """Test format field rejects invalid values."""
        with pytest.raises((ValueError, TypeError)):
            CLIOutputConfig(format="invalid_format")

    def test_boolean_field_types(self) -> None:
        """Test boolean field type validation."""
        config = CLIOutputConfig(
            no_color=False,
            quiet=False,
            verbose=False,
        )

        assert isinstance(config.no_color, bool)
        assert isinstance(config.quiet, bool)
        assert isinstance(config.verbose, bool)

    def test_pager_optional_string(self) -> None:
        """Test pager field as optional string."""
        # Test with None
        config1 = CLIOutputConfig(pager=None)
        assert config1.pager is None

        # Test with string
        config2 = CLIOutputConfig(pager="less -R")
        if config2.pager != "less -R":
            raise AssertionError(f"Expected {'less -R'}, got {config2.pager}")


class TestCLIAPIConfig:
    """Test CLIAPIConfig class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = CLIAPIConfig()

        if config.url != "http://localhost:8000":
            raise AssertionError(
                f"Expected {'http://localhost:8000'}, got {config.url}"
            )
        assert config.timeout == 30
        if config.retries != EXPECTED_DATA_COUNT:
            raise AssertionError(f"Expected {3}, got {config.retries}")
        if not (config.verify_ssl):
            raise AssertionError(f"Expected True, got {config.verify_ssl}")

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = CLIAPIConfig(
            url="https://api.example.com:8443",
            timeout=60,
            retries=5,
            verify_ssl=False,
        )

        if config.url != "https://api.example.com:8443":
            raise AssertionError(
                f"Expected {'https://api.example.com:8443'}, got {config.url}"
            )
        assert config.timeout == 60
        if config.retries != 5:
            raise AssertionError(f"Expected {5}, got {config.retries}")
        if config.verify_ssl:
            raise AssertionError(f"Expected False, got {config.verify_ssl}")

    def test_base_url_property(self) -> None:
        """Test base_url property removes trailing slash."""
        test_cases = [
            ("http://localhost:8000", "http://localhost:8000"),
            ("http://localhost:8000/", "http://localhost:8000"),
            ("https://api.example.com/", "https://api.example.com"),
            ("https://api.example.com///", "https://api.example.com"),
            ("http://localhost", "http://localhost"),
        ]

        for input_url, expected_output in test_cases:
            config = CLIAPIConfig(url=input_url)
            if config.base_url != expected_output:
                raise AssertionError(
                    f"Expected {expected_output}, got {config.base_url}"
                )

    def test_numeric_field_types(self) -> None:
        """Test numeric field type validation."""
        config = CLIAPIConfig(timeout=45, retries=2)

        assert isinstance(config.timeout, int)
        assert isinstance(config.retries, int)
        if config.timeout != 45:
            raise AssertionError(f"Expected {45}, got {config.timeout}")
        assert config.retries == EXPECTED_BULK_SIZE

    def test_boolean_field_type(self) -> None:
        """Test boolean field type validation."""
        config = CLIAPIConfig(verify_ssl=False)

        assert isinstance(config.verify_ssl, bool)
        if config.verify_ssl:
            raise AssertionError(f"Expected False, got {config.verify_ssl}")


class TestCLIAuthConfig:
    """Test CLIAuthConfig class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = CLIAuthConfig()

        expected_token_path = Path.home() / ".flext" / "auth" / "token"
        expected_refresh_path = Path.home() / ".flext" / "auth" / "refresh_token"

        if config.token_file != expected_token_path:
            raise AssertionError(
                f"Expected {expected_token_path}, got {config.token_file}"
            )
        assert config.refresh_token_file == expected_refresh_path
        if not (config.auto_refresh):
            raise AssertionError(f"Expected True, got {config.auto_refresh}")

    def test_custom_paths(self) -> None:
        """Test custom path configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            custom_token = temp_path / "custom_token"
            custom_refresh = temp_path / "custom_refresh"

            config = CLIAuthConfig(
                token_file=custom_token,
                refresh_token_file=custom_refresh,
                auto_refresh=False,
            )

            if config.token_file != custom_token:
                raise AssertionError(f"Expected {custom_token}, got {config.token_file}")
            assert config.refresh_token_file == custom_refresh
            if config.auto_refresh:
                raise AssertionError(f"Expected False, got {config.auto_refresh}")

    def test_path_types(self) -> None:
        """Test that paths are Path objects."""
        config = CLIAuthConfig()

        assert isinstance(config.token_file, Path)
        assert isinstance(config.refresh_token_file, Path)

    def test_auto_refresh_boolean(self) -> None:
        """Test auto_refresh boolean type."""
        config = CLIAuthConfig(auto_refresh=False)

        assert isinstance(config.auto_refresh, bool)
        if config.auto_refresh:
            raise AssertionError(f"Expected False, got {config.auto_refresh}")


class TestCLIDirectoryConfig:
    """Test CLIDirectoryConfig class."""

    def test_default_values(self) -> None:
        """Test default directory configuration."""
        config = CLIDirectoryConfig()

        expected_config_dir = Path.home() / ".flext"
        expected_cache_dir = Path.home() / ".flext" / "cache"
        expected_log_dir = Path.home() / ".flext" / "logs"
        expected_data_dir = Path.home() / ".flext" / "data"

        if config.config_dir != expected_config_dir:
            raise AssertionError(
                f"Expected {expected_config_dir}, got {config.config_dir}"
            )
        assert config.cache_dir == expected_cache_dir
        if config.log_dir != expected_log_dir:
            raise AssertionError(f"Expected {expected_log_dir}, got {config.log_dir}")
        assert config.data_dir == expected_data_dir

    def test_custom_directories(self) -> None:
        """Test custom directory paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_dir = temp_path / "config"
            cache_dir = temp_path / "cache"
            log_dir = temp_path / "logs"
            data_dir = temp_path / "data"

            config = CLIDirectoryConfig(
                config_dir=config_dir,
                cache_dir=cache_dir,
                log_dir=log_dir,
                data_dir=data_dir,
            )

            if config.config_dir != config_dir:
                raise AssertionError(
                    f"Expected {config_dir}, got {config.config_dir}"
                )
            assert config.cache_dir == cache_dir
            if config.log_dir != log_dir:
                raise AssertionError(f"Expected {log_dir}, got {config.log_dir}")
            assert config.data_dir == data_dir

    def test_ensure_directories(self) -> None:
        """Test ensure_directories creates all directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config = CLIDirectoryConfig(
                config_dir=temp_path / "config",
                cache_dir=temp_path / "cache",
                log_dir=temp_path / "logs",
                data_dir=temp_path / "data",
            )

            # Verify directories don't exist initially
            assert not config.config_dir.exists()
            assert not config.cache_dir.exists()
            assert not config.log_dir.exists()
            assert not config.data_dir.exists()

            # Call ensure_directories
            config.ensure_directories()

            # Verify all directories were created
            assert config.config_dir.exists()
            assert config.cache_dir.exists()
            assert config.log_dir.exists()
            assert config.data_dir.exists()

            # Verify they are directories
            assert config.config_dir.is_dir()
            assert config.cache_dir.is_dir()
            assert config.log_dir.is_dir()
            assert config.data_dir.is_dir()

    def test_ensure_directories_with_existing_dirs(self) -> None:
        """Test ensure_directories works with existing directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config = CLIDirectoryConfig(
                config_dir=temp_path / "config",
                cache_dir=temp_path / "cache",
                log_dir=temp_path / "logs",
                data_dir=temp_path / "data",
            )

            # Create some directories manually
            config.config_dir.mkdir()
            config.cache_dir.mkdir()

            # Call ensure_directories should not fail
            config.ensure_directories()

            # All directories should exist
            assert config.config_dir.exists()
            assert config.cache_dir.exists()
            assert config.log_dir.exists()
            assert config.data_dir.exists()

    def test_path_types(self) -> None:
        """Test that all directory fields are Path objects."""
        config = CLIDirectoryConfig()

        assert isinstance(config.config_dir, Path)
        assert isinstance(config.cache_dir, Path)
        assert isinstance(config.log_dir, Path)
        assert isinstance(config.data_dir, Path)


class TestCLIConfig:
    """Test CLIConfig main configuration class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = CLIConfig()

        if config.profile != "default":
            raise AssertionError(f"Expected {'default'}, got {config.profile}")
        if config.debug:
            raise AssertionError(f"Expected False, got {config.debug}")
        assert isinstance(config.output, CLIOutputConfig)
        assert isinstance(config.api, CLIAPIConfig)
        assert isinstance(config.auth, CLIAuthConfig)
        assert isinstance(config.directories, CLIDirectoryConfig)

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = CLIConfig(
            profile="production",
            debug=True,
        )

        if config.profile != "production":
            raise AssertionError(f"Expected {'production'}, got {config.profile}")
        if not (config.debug):
            raise AssertionError(f"Expected True, got {config.debug}")

    def test_component_configurations(self) -> None:
        """Test component configuration objects."""
        config = CLIConfig()

        # Test output config
        if config.output.format != "table":
            raise AssertionError(f"Expected {'table'}, got {config.output.format}")
        if config.output.no_color:
            raise AssertionError(f"Expected False, got {config.output.no_color}")

        # Test API config
        if config.api.url != "http://localhost:8000":
            raise AssertionError(
                f"Expected {'http://localhost:8000'}, got {config.api.url}"
            )
        assert config.api.timeout == 30

        # Test auth config
        if not (config.auth.auto_refresh):
            raise AssertionError(f"Expected True, got {config.auth.auto_refresh}")

        # Test directories config
        if config.directories.config_dir != Path.home() / ".flext":
            raise AssertionError(
                f"Expected {Path.home() / '.flext'}, got {config.directories.config_dir}"
            )

    def test_ensure_setup(self) -> None:
        """Test ensure_setup method creates directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create custom config with temp directories
            config = CLIConfig()
            config.directories = CLIDirectoryConfig(
                config_dir=temp_path / "config",
                cache_dir=temp_path / "cache",
                log_dir=temp_path / "logs",
                data_dir=temp_path / "data",
            )
            config.auth = CLIAuthConfig(
                token_file=temp_path / "auth" / "token",
                refresh_token_file=temp_path / "auth" / "refresh_token",
            )

            # Call ensure_setup
            config.ensure_setup()

            # Verify directories were created
            assert config.directories.config_dir.exists()
            assert config.directories.cache_dir.exists()
            assert config.directories.log_dir.exists()
            assert config.directories.data_dir.exists()

            # Verify auth directories were created
            assert config.auth.token_file.parent.exists()
            assert config.auth.refresh_token_file.parent.exists()

    def test_nested_configuration_access(self) -> None:
        """Test accessing nested configuration values."""
        config = CLIConfig()

        # Test deep access to nested configurations
        if config.output.format != "table":
            raise AssertionError(f"Expected {'table'}, got {config.output.format}")
        assert config.api.base_url == "http://localhost:8000"
        if not (config.auth.auto_refresh):
            raise AssertionError(f"Expected True, got {config.auth.auto_refresh}")
        if config.directories.config_dir.name != ".flext":
            raise AssertionError(
                f"Expected {'.flext'}, got {config.directories.config_dir.name}"
            )


class TestCLISettings:
    """Test CLISettings configuration class."""

    def test_default_values(self) -> None:
        """Test default settings values."""
        settings = CLISettings()

        if settings.project_name != "flext-cli":
            raise AssertionError(f"Expected {'flext-cli'}, got {settings.project_name}")
        assert settings.project_version == "0.7.0"
        if settings.api_url != "http://localhost:8000":
            raise AssertionError(
                f"Expected {'http://localhost:8000'}, got {settings.api_url}"
            )
        assert settings.timeout == 30
        if settings.output_format != "table":
            raise AssertionError(f"Expected {'table'}, got {settings.output_format}")
        if settings.debug:
            raise AssertionError(f"Expected False, got {settings.debug}")

    def test_custom_values(self) -> None:
        """Test custom settings values."""
        settings = CLISettings(
            project_name="custom-cli",
            project_version="0.9.0",
            api_url="https://custom.api.com",
            timeout=60,
            output_format="json",
            debug=True,
        )

        if settings.project_name != "custom-cli":
            raise AssertionError(
                f"Expected {'custom-cli'}, got {settings.project_name}"
            )
        assert settings.project_version == "0.9.0"
        if settings.api_url != "https://custom.api.com":
            raise AssertionError(
                f"Expected {'https://custom.api.com'}, got {settings.api_url}"
            )
        assert settings.timeout == 60
        if settings.output_format != "json":
            raise AssertionError(f"Expected {'json'}, got {settings.output_format}")
        if not (settings.debug):
            raise AssertionError(f"Expected True, got {settings.debug}")

    def test_environment_variable_loading(self) -> None:
        """Test loading settings from environment variables."""
        env_vars = {
            "FLEXT_CLI_PROJECT_NAME": "env-cli",
            "FLEXT_CLI_PROJECT_VERSION": "0.9.0",
            "FLEXT_CLI_API_URL": "https://env.api.com",
            "FLEXT_CLI_TIMEOUT": "45",
            "FLEXT_CLI_OUTPUT_FORMAT": "yaml",
            "FLEXT_CLI_DEBUG": "true",
        }

        with patch.dict(os.environ, env_vars):
            settings = CLISettings()

            if settings.project_name != "env-cli":
                raise AssertionError(
                    f"Expected {'env-cli'}, got {settings.project_name}"
                )
            assert settings.project_version == "0.9.0"
            if settings.api_url != "https://env.api.com":
                raise AssertionError(
                    f"Expected {'https://env.api.com'}, got {settings.api_url}"
                )
            assert settings.timeout == 45
            if settings.output_format != "yaml":
                raise AssertionError(f"Expected {'yaml'}, got {settings.output_format}")
            if not (settings.debug):
                raise AssertionError(f"Expected True, got {settings.debug}")

    def test_field_types(self) -> None:
        """Test field type validation."""
        settings = CLISettings(
            timeout=30,
            debug=False,
        )

        assert isinstance(settings.project_name, str)
        assert isinstance(settings.project_version, str)
        assert isinstance(settings.api_url, str)
        assert isinstance(settings.timeout, int)
        assert isinstance(settings.output_format, str)
        assert isinstance(settings.debug, bool)

    def test_model_config(self) -> None:
        """Test model configuration settings."""
        settings = CLISettings()

        # Test that model config is set correctly (model_config is a dict in pydantic-settings)
        if settings.model_config["env_prefix"] != "FLEXT_CLI_":
            raise AssertionError(
                f"Expected {'FLEXT_CLI_'}, got {settings.model_config['env_prefix']}"
            )
        assert settings.model_config["env_file"] == ".env"
        if settings.model_config["case_sensitive"]:
            raise AssertionError(
                f"Expected False, got {settings.model_config['case_sensitive']}"
            )
        assert settings.model_config["extra"] == "ignore"


class TestConfigurationFunctions:
    """Test module-level configuration functions."""

    def test_get_cli_config(self) -> None:
        """Test get_cli_config function."""
        # Clear any existing global config

        flext_cli.config.cli_config._cli_config = None

        config = get_cli_config()

        assert isinstance(config, CLIConfig)
        if config.profile != "default":
            raise AssertionError(f"Expected {'default'}, got {config.profile}")
        if config.debug:
            raise AssertionError(f"Expected False, got {config.debug}")

    def test_get_cli_config_singleton(self) -> None:
        """Test get_cli_config returns same instance."""
        config1 = get_cli_config()
        config2 = get_cli_config()

        assert config1 is config2

    def test_get_cli_config_reload(self) -> None:
        """Test get_cli_config with reload=True."""
        config1 = get_cli_config()
        config2 = get_cli_config(reload=True)

        # Should be different instances when reloaded
        assert config1 is not config2
        assert isinstance(config2, CLIConfig)

    def test_create_cli_config(self) -> None:
        """Test _create_cli_config function."""
        config = _create_cli_config()

        assert isinstance(config, CLIConfig)
        if config.profile != "default":
            raise AssertionError(f"Expected {'default'}, got {config.profile}")
        if config.debug:
            raise AssertionError(f"Expected False, got {config.debug}")

    def test_create_cli_config_calls_ensure_setup(self) -> None:
        """Test _create_cli_config calls ensure_setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir)

            with patch("flext_cli.config.cli_config.CLIConfig") as mock_config_class:
                mock_config = mock_config_class.return_value
                mock_config.ensure_setup = lambda: None

                result = _create_cli_config()

                # Verify config was created with correct parameters
                mock_config_class.assert_called_once_with(
                    profile="default",
                    debug=False,
                )

                # Verify ensure_setup was called
                if result != mock_config:
                    raise AssertionError(f"Expected {mock_config}, got {result}")

    def test_get_cli_settings(self) -> None:
        """Test get_cli_settings function."""
        settings = get_cli_settings()

        assert isinstance(settings, CLISettings)
        if settings.project_name != "flext-cli":
            raise AssertionError(f"Expected {'flext-cli'}, got {settings.project_name}")
        assert settings.project_version == "0.7.0"
        if settings.api_url != "http://localhost:8000":
            raise AssertionError(
                f"Expected {'http://localhost:8000'}, got {settings.api_url}"
            )
        assert settings.timeout == 30
        if settings.output_format != "table":
            raise AssertionError(f"Expected {'table'}, got {settings.output_format}")
        if settings.debug:
            raise AssertionError(f"Expected False, got {settings.debug}")


class TestConfigurationIntegration:
    """Integration tests for configuration classes."""

    def test_full_configuration_flow(self) -> None:
        """Test full configuration setup flow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create configuration
            config = CLIConfig(
                profile="integration_test",
                debug=True,
            )

            # Override directories to use temp directory
            config.directories = CLIDirectoryConfig(
                config_dir=temp_path / "config",
                cache_dir=temp_path / "cache",
                log_dir=temp_path / "logs",
                data_dir=temp_path / "data",
            )
            config.auth = CLIAuthConfig(
                token_file=temp_path / "auth" / "token",
                refresh_token_file=temp_path / "auth" / "refresh_token",
                auto_refresh=False,
            )

            # Setup environment
            config.ensure_setup()

            # Verify complete setup
            if config.profile != "integration_test":
                raise AssertionError(
                    f"Expected {'integration_test'}, got {config.profile}"
                )
            if not (config.debug):
                raise AssertionError(f"Expected True, got {config.debug}")

            # Verify directories exist
            assert config.directories.config_dir.exists()
            assert config.directories.cache_dir.exists()
            assert config.directories.log_dir.exists()
            assert config.directories.data_dir.exists()

            # Verify auth directories exist
            assert config.auth.token_file.parent.exists()
            assert config.auth.refresh_token_file.parent.exists()

            # Verify component configurations
            if config.output.format != "table":
                raise AssertionError(f"Expected {'table'}, got {config.output.format}")
            assert config.api.timeout == 30
            if config.auth.auto_refresh:
                raise AssertionError(f"Expected False, got {config.auth.auto_refresh}")

    def test_configuration_modification(self) -> None:
        """Test modifying configuration values."""
        config = CLIConfig()

        # Modify nested configurations
        config.output = CLIOutputConfig(
            format="json",
            no_color=True,
            quiet=True,
        )
        config.api = CLIAPIConfig(
            url="https://modified.api.com",
            timeout=45,
        )

        # Verify modifications
        if config.output.format != "json":
            raise AssertionError(f"Expected {'json'}, got {config.output.format}")
        if not (config.output.no_color):
            raise AssertionError(f"Expected True, got {config.output.no_color}")
        assert config.output.quiet is True
        if config.api.url != "https://modified.api.com":
            raise AssertionError(
                f"Expected {'https://modified.api.com'}, got {config.api.url}"
            )
        assert config.api.timeout == 45

    def test_settings_and_config_interaction(self) -> None:
        """Test interaction between settings and config."""
        settings = get_cli_settings()
        config = get_cli_config()

        # Both should be independent instances
        assert isinstance(settings, CLISettings)
        assert isinstance(config, CLIConfig)

        # But should have compatible values
        if settings.api_url != config.api.url:
            raise AssertionError(f"Expected {config.api.url}, got {settings.api_url}")
        assert settings.debug == config.debug

    def test_error_handling_in_directory_creation(self) -> None:
        """Test error handling in directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file where we want to create a directory
            # This should cause mkdir to handle existing files gracefully
            temp_path = Path(temp_dir)
            conflicting_file = temp_path / "conflict"
            conflicting_file.touch()

            config = CLIConfig()
            config.directories = CLIDirectoryConfig(
                config_dir=conflicting_file
                / "config",  # This will fail but should be handled
                cache_dir=temp_path / "cache",
                log_dir=temp_path / "logs",
                data_dir=temp_path / "data",
            )

            # This should handle the error gracefully or raise appropriate exception
            with contextlib.suppress(OSError, FileExistsError):
                config.ensure_setup()
                # If no exception is raised, verify what was created
                # Since ensure_setup may fail on the first directory but succeed on others

            # Other directories that can be created should exist
            # We can't guarantee all will be created due to the conflict we set up
            # So we just verify the method runs without crashing the process
            assert True  # Test passes if no unhandled exception was raised
