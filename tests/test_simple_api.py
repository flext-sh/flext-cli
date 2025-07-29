"""Tests for simple API functions in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from flext_cli.simple_api import __all__
from flext_cli.simple_api import (


from __future__ import annotations

from unittest.mock import patch

import pytest
from flext_cli.simple_api import (
    create_development_cli_config,
    create_production_cli_config,
    get_cli_settings,
    setup_cli,
)
from flext_cli.utils.config import CLISettings


class TestSetupCli:
    """Test cases for setup_cli function."""

    def test_setup_cli_without_settings(self) -> None:
        """Test CLI setup without providing settings."""
        result = setup_cli()
        assert result.is_success
        if not (result.unwrap()):
            raise AssertionError(f"Expected True, got {result.unwrap()}")

    def test_setup_cli_with_settings(self) -> None:
        """Test CLI setup with provided settings."""
        settings = CLISettings(debug=True, log_level="DEBUG")
        result = setup_cli(settings)
        assert result.is_success
        if not (result.unwrap()):
            raise AssertionError(f"Expected True, got {result.unwrap()}")

    def test_setup_cli_with_exception(self) -> None:
        """Test CLI setup when an exception occurs."""
        # Mock CLISettings to raise an exception
        with patch("flext_cli.simple_api.CLISettings") as mock_settings:
            mock_settings.side_effect = RuntimeError("Test error")

            result = setup_cli()
            assert not result.is_success
            if "Failed to setup CLI: Test error" not in result.error:
                raise AssertionError(f"Expected {"Failed to setup CLI: Test error"} in {result.error}")


class TestCreateDevelopmentCliConfig:
    """Test cases for create_development_cli_config function."""

    def test_create_development_config_defaults(self) -> None:
        """Test development config with default values."""
        config = create_development_cli_config()

        if not (config.debug):

            raise AssertionError(f"Expected True, got {config.debug}")
        if config.log_level != "DEBUG":
            raise AssertionError(f"Expected {"DEBUG"}, got {config.log_level}")
        assert config.config_path is None
        # Check that default CLISettings fields are present
        if config.project_name != "flext-cli":
            raise AssertionError(f"Expected {"flext-cli"}, got {config.project_name}")
        assert config.project_version == "0.8.0"

    def test_create_development_config_with_overrides(self) -> None:
        """Test development config with overrides."""
        config = create_development_cli_config(
            debug=False,
            log_level="INFO",
            config_path="/custom/path",
        )

        if config.debug:

            raise AssertionError(f"Expected False, got {config.debug}")\ n        assert config.log_level == "INFO"
        if config.config_path != "/custom/path":
            raise AssertionError(f"Expected {"/custom/path"}, got {config.config_path}")
        # Default values should still be present
        if config.project_name != "flext-cli":
            raise AssertionError(f"Expected {"flext-cli"}, got {config.project_name}")
        assert config.project_version == "0.8.0"

    def test_create_development_config_with_all_overrides(self) -> None:
        """Test development config with all available overrides."""
        overrides = {
            "debug": False,
            "log_level": "WARNING",
            "config_path": "/test/config/path",
        }

        config = create_development_cli_config(**overrides)

        if config.debug:

            raise AssertionError(f"Expected False, got {config.debug}")\ n        assert config.log_level == "WARNING"
        if config.config_path != "/test/config/path":
            raise AssertionError(f"Expected {"/test/config/path"}, got {config.config_path}")
        # Default fields should still be present
        if config.project_name != "flext-cli":
            raise AssertionError(f"Expected {"flext-cli"}, got {config.project_name}")
        assert config.project_version == "0.8.0"


class TestCreateProductionCliConfig:
    """Test cases for create_production_cli_config function."""

    def test_create_production_config_defaults(self) -> None:
        """Test production config with default values."""
        config = create_production_cli_config()

        if config.debug:

            raise AssertionError(f"Expected False, got {config.debug}")\ n        assert config.log_level == "INFO"
        assert config.config_path is None
        # Check that default CLISettings fields are present
        if config.project_name != "flext-cli":
            raise AssertionError(f"Expected {"flext-cli"}, got {config.project_name}")
        assert config.project_version == "0.8.0"

    def test_create_production_config_with_overrides(self) -> None:
        """Test production config with overrides."""
        config = create_production_cli_config(
            debug=True,
            log_level="DEBUG",
            config_path="/staging/config",
        )

        if not (config.debug):

            raise AssertionError(f"Expected True, got {config.debug}")
        if config.log_level != "DEBUG":
            raise AssertionError(f"Expected {"DEBUG"}, got {config.log_level}")
        assert config.config_path == "/staging/config"
        # Default values should still be present
        if config.project_name != "flext-cli":
            raise AssertionError(f"Expected {"flext-cli"}, got {config.project_name}")
        assert config.project_version == "0.8.0"

    def test_create_production_config_with_all_overrides(self) -> None:
        """Test production config with all available overrides."""
        overrides = {
            "debug": True,
            "log_level": "DEBUG",
            "config_path": "/production/config/path",
        }

        config = create_production_cli_config(**overrides)

        if not (config.debug):

            raise AssertionError(f"Expected True, got {config.debug}")
        if config.log_level != "DEBUG":
            raise AssertionError(f"Expected {"DEBUG"}, got {config.log_level}")
        assert config.config_path == "/production/config/path"
        # Default fields should still be present
        if config.project_name != "flext-cli":
            raise AssertionError(f"Expected {"flext-cli"}, got {config.project_name}")
        assert config.project_version == "0.8.0"


class TestGetCliSettings:
    """Test cases for get_cli_settings function."""

    def test_get_cli_settings(self) -> None:
        """Test getting CLI settings."""
        settings = get_cli_settings()
        assert isinstance(settings, CLISettings)

        # Should have default values
        assert hasattr(settings, "debug")
        assert hasattr(settings, "log_level")
        assert hasattr(settings, "config_path")
        assert hasattr(settings, "project_name")
        assert hasattr(settings, "project_version")

    def test_get_cli_settings_returns_fresh_instance(self) -> None:
        """Test that get_cli_settings returns fresh instances."""
        settings1 = get_cli_settings()
        settings2 = get_cli_settings()

        # Should be different instances
        assert settings1 is not settings2

        # But should have same default values
        if settings1.debug != settings2.debug:
            raise AssertionError(f"Expected {settings2.debug}, got {settings1.debug}")
        assert settings1.log_level == settings2.log_level
        if settings1.project_name != settings2.project_name:
            raise AssertionError(f"Expected {settings2.project_name}, got {settings1.project_name}")


class TestSimpleApiExports:
    """Test cases for module exports."""

    def test_all_exports_accessible(self) -> None:
        """Test that all exported functions are accessible."""


        expected_exports = [
            "create_development_cli_config",
            "create_production_cli_config",
            "get_cli_settings",
            "setup_cli",
        ]

        if set(__all__) != set(expected_exports):

            raise AssertionError(f"Expected {set(expected_exports)}, got {set(__all__)}")

    def test_functions_can_be_imported(self) -> None:
        """Test that all functions can be imported directly."""
        # Should not raise ImportError

            create_development_cli_config,
            create_production_cli_config,
            get_cli_settings,
            setup_cli,
        )

        # Should all be callable
        assert callable(create_development_cli_config)
        assert callable(create_production_cli_config)
        assert callable(get_cli_settings)
        assert callable(setup_cli)


class TestConfigValidation:
    """Test cases for configuration validation."""

    def test_development_config_validation_error(self) -> None:
        """Test development config with invalid values."""
        with pytest.raises(ValueError, match="validation error"):
            create_development_cli_config(debug="invalid")  # type: ignore[arg-type]

    def test_production_config_validation_error(self) -> None:
        """Test production config with invalid values."""
        with pytest.raises(ValueError, match="validation error"):
            create_production_cli_config(debug="invalid")  # type: ignore[arg-type]

    def test_development_config_with_none_values(self) -> None:
        """Test development config handles None values properly."""
        # This should work - None values should be valid for config_path
        config = create_development_cli_config(config_path=None)
        assert isinstance(config, CLISettings)
        assert config.config_path is None

    def test_production_config_with_none_values(self) -> None:
        """Test production config handles None values properly."""
        # This should work - None values should be valid for config_path
        config = create_production_cli_config(config_path=None)
        assert isinstance(config, CLISettings)
        assert config.config_path is None
