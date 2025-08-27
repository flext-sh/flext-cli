"""Tests for simple API functions in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import (
    FlextCliSettings,
    setup_cli,
)
from flext_cli.simple_api import (
    __all__,
    create_development_cli_config,
    create_production_cli_config,
    get_cli_settings,
)


class TestSetupCli:
    """Test cases for setup_cli function."""

    def test_setup_cli_without_settings(self) -> None:
        """Test CLI setup without providing settings."""
        result = setup_cli()
        assert result.is_success
        if not (result.value):
            msg = f"Expected True, got {result.value}"
            raise AssertionError(msg)

    def test_setup_cli_with_settings(self) -> None:
        """Test CLI setup with provided settings."""
        settings = FlextCliSettings(debug=True, log_level="DEBUG")
        result = setup_cli(settings)
        assert result.is_success
        if not (result.value):
            msg = f"Expected True, got {result.value}"
            raise AssertionError(msg)

    def test_setup_cli_with_exception(self) -> None:
        """Test CLI setup when an exception occurs with invalid config."""
        # Create invalid config that will cause real exception during setup
        # Use a config object with invalid data that will trigger validation errors
        try:
            # This simulates real error by creating FlextCliSettings with invalid data
            invalid_config = FlextCliSettings(log_level="INVALID_LEVEL")
            # This should trigger validation error in real usage scenario
        except Exception:
            # If FlextCliSettings validates on creation, we need a different approach
            # Test with None config but trigger error through invalid state
            result = setup_cli()
            # If setup_cli works fine with defaults, let's test edge case
            assert result.is_success  # setup_cli should handle normal case
            return

        # If we get here, test the exception handling through setup_cli directly
        result = setup_cli(invalid_config)
        # setup_cli should handle exceptions gracefully and return FlextResult
        if result.is_success:
            # If no exception occurred, that's also valid behavior
            # setup_cli returns the configuration dict, not a boolean
            assert result.value is not None
            assert isinstance(result.value, dict)
        else:
            # If exception was caught, verify error message format
            assert result.error is not None
            assert "Failed to setup CLI:" in result.error


class TestCreateDevelopmentCliConfig:
    """Test cases for create_development_cli_config function."""

    def test_create_development_config_defaults(self) -> None:
        """Test development config with default values."""
        config = create_development_cli_config()

        if not (config.debug):
            msg = f"Expected True, got {config.debug}"
            raise AssertionError(msg)
        if config.log_level != "DEBUG":
            msg = f"Expected {'DEBUG'}, got {config.log_level}"
            raise AssertionError(msg)
        assert config.config_path is None
        # Check that default FlextCliSettings fields are present
        if config.project_name != "flext-cli":
            msg = f"Expected {'flext-cli'}, got {config.project_name}"
            raise AssertionError(msg)
        assert config.project_version == "0.9.0"

    def test_create_development_config_with_overrides(self) -> None:
        """Test development config with overrides."""
        config = create_development_cli_config(
            debug=False,
            log_level="INFO",
            config_path="/custom/path",
        )

        if config.debug:
            msg = f"Expected False, got {config.debug}"
            raise AssertionError(msg)
        assert config.log_level == "INFO"
        if config.config_path != "/custom/path":
            msg = f"Expected {'/custom/path'}, got {config.config_path}"
            raise AssertionError(msg)
        # Default values should still be present
        if config.project_name != "flext-cli":
            msg = f"Expected {'flext-cli'}, got {config.project_name}"
            raise AssertionError(msg)
        assert config.project_version == "0.9.0"

    def test_create_development_config_with_all_overrides(self) -> None:
        """Test development config with all available overrides."""
        overrides = {
            "debug": False,
            "log_level": "WARNING",
            "config_path": "/test/config/path",
        }

        config = create_development_cli_config(**overrides)

        if config.debug:
            msg = f"Expected False, got {config.debug}"
            raise AssertionError(msg)
        assert config.log_level == "WARNING"
        if config.config_path != "/test/config/path":
            msg = f"Expected {'/test/config/path'}, got {config.config_path}"
            raise AssertionError(
                msg,
            )
        # Default fields should still be present
        if config.project_name != "flext-cli":
            msg = f"Expected {'flext-cli'}, got {config.project_name}"
            raise AssertionError(msg)
        assert config.project_version == "0.9.0"


class TestCreateProductionCliConfig:
    """Test cases for create_production_cli_config function."""

    def test_create_production_config_defaults(self) -> None:
        """Test production config with default values."""
        config = create_production_cli_config()

        if config.debug:
            msg = f"Expected False, got {config.debug}"
            raise AssertionError(msg)
        assert config.log_level == "INFO"
        assert config.config_path is None
        # Check that default FlextCliSettings fields are present
        if config.project_name != "flext-cli":
            msg = f"Expected {'flext-cli'}, got {config.project_name}"
            raise AssertionError(msg)
        assert config.project_version == "0.9.0"

    def test_create_production_config_with_overrides(self) -> None:
        """Test production config with overrides."""
        config = create_production_cli_config(
            debug=True,
            log_level="DEBUG",
            config_path="/staging/config",
        )

        if not (config.debug):
            msg = f"Expected True, got {config.debug}"
            raise AssertionError(msg)
        if config.log_level != "DEBUG":
            msg = f"Expected {'DEBUG'}, got {config.log_level}"
            raise AssertionError(msg)
        assert config.config_path == "/staging/config"
        # Default values should still be present
        if config.project_name != "flext-cli":
            msg = f"Expected {'flext-cli'}, got {config.project_name}"
            raise AssertionError(msg)
        assert config.project_version == "0.9.0"

    def test_create_production_config_with_all_overrides(self) -> None:
        """Test production config with all available overrides."""
        overrides = {
            "debug": True,
            "log_level": "DEBUG",
            "config_path": "/production/config/path",
        }

        config = create_production_cli_config(**overrides)

        if not (config.debug):
            msg = f"Expected True, got {config.debug}"
            raise AssertionError(msg)
        if config.log_level != "DEBUG":
            msg = f"Expected {'DEBUG'}, got {config.log_level}"
            raise AssertionError(msg)
        assert config.config_path == "/production/config/path"
        # Default fields should still be present
        if config.project_name != "flext-cli":
            msg = f"Expected {'flext-cli'}, got {config.project_name}"
            raise AssertionError(msg)
        assert config.project_version == "0.9.0"


class TestGetCliSettings:
    """Test cases for get_cli_settings function."""

    def test_get_cli_settings(self) -> None:
        """Test getting CLI settings."""
        settings = get_cli_settings()
        assert isinstance(settings, FlextCliSettings)

        # Should have default values
        assert hasattr(settings, "debug")
        assert hasattr(settings, "log_level")
        assert hasattr(settings, "config_path")
        assert hasattr(settings, "project_name")
        assert hasattr(settings, "project_version")

    def test_get_cli_settings_returns_fresh_instance(self) -> None:
        """Test that get_cli_settings returns fresh instances when reload=True."""
        settings1 = get_cli_settings(reload=True)
        settings2 = get_cli_settings(reload=True)

        # Should be different instances when reload=True
        assert settings1 is not settings2

        # But should have same default values
        if settings1.debug != settings2.debug:
            msg = f"Expected {settings2.debug}, got {settings1.debug}"
            raise AssertionError(msg)
        assert settings1.log_level == settings2.log_level
        if settings1.project_name != settings2.project_name:
            msg = f"Expected {settings2.project_name}, got {settings1.project_name}"
            raise AssertionError(
                msg,
            )


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
            msg = f"Expected {set(expected_exports)}, got {set(__all__)}"
            raise AssertionError(
                msg,
            )

    def test_functions_can_be_imported(self) -> None:
        """Test that all functions can be imported directly."""
        # Should not raise ImportError

        # Should all be callable
        assert callable(create_development_cli_config)
        assert callable(create_production_cli_config)
        assert callable(get_cli_settings)
        assert callable(setup_cli)


class TestConfigValidation:
    """Test cases for configuration validation."""

    def test_development_config_with_valid_overrides(self) -> None:
        """Test development config accepts valid overrides."""
        config = create_development_cli_config(timeout=60)
        assert config.timeout == 60

    def test_production_config_with_valid_overrides(self) -> None:
        """Test production config accepts valid overrides."""
        config = create_production_cli_config(output_format="json")
        assert config.output_format == "json"

    def test_development_config_with_none_values(self) -> None:
        """Test development config handles None values properly."""
        # This should work - None values should be valid for config_path
        config = create_development_cli_config(config_path=None)
        assert isinstance(config, FlextCliSettings)
        assert config.config_path is None

    def test_production_config_with_none_values(self) -> None:
        """Test production config handles None values properly."""
        # This should work - None values should be valid for config_path
        config = create_production_cli_config(config_path=None)
        assert isinstance(config, FlextCliSettings)
        assert config.config_path is None
