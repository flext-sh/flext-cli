"""Tests for flext_cli.simple_api module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.config.cli_config import CLIConfig
from flext_cli.simple_api import (
    create_development_cli_config,
    create_production_cli_config,
    get_cli_settings,
    setup_cli,
)
from flext_core import FlextResult


class TestSetupCLI:
    """Test setup_cli function."""

    def test_setup_cli_with_default_settings(self) -> None:
        """Test setup_cli with default settings."""
        result = setup_cli()

        assert isinstance(result, FlextResult)
        assert result.success
        assert result.data == {"setup_complete": True}
        assert result.error is None

    def test_setup_cli_with_custom_settings(self) -> None:
        """Test setup_cli with custom settings."""
        settings = CLIConfig(verbose=True)

        result = setup_cli(settings)

        assert isinstance(result, FlextResult)
        assert result.success
        assert result.data == {"setup_complete": True}
        assert result.error is None

    def test_setup_cli_handles_none_settings(self) -> None:
        """Test setup_cli handles None settings properly."""
        result = setup_cli(None)

        assert isinstance(result, FlextResult)
        assert result.success
        assert result.data == {"setup_complete": True}


class TestCreateDevelopmentCLIConfig:
    """Test create_development_cli_config function."""

    def test_create_development_config_default(self) -> None:
        """Test creating development config with defaults."""
        config = create_development_cli_config()

        # Test actual CLISettings attributes
        assert config.debug is True
        assert config.project_name == "flext-cli"
        assert config.project_version == "0.7.0"
        assert config.api_url == "http://localhost:8000"
        assert config.timeout == 30
        assert config.output_format == "table"

    def test_create_development_config_with_overrides(self) -> None:
        """Test creating development config with overrides."""
        overrides = {
            "api_url": "http://dev.example.com:9000",
            "debug": False,
            "output_format": "json",
        }

        config = create_development_cli_config(**overrides)

        # Check overridden values
        assert config.api_url == "http://dev.example.com:9000"
        assert config.debug is False
        assert config.output_format == "json"

        # Check defaults
        assert config.project_name == "flext-cli"
        assert config.timeout == 30

    def test_create_development_config_partial_overrides(self) -> None:
        """Test creating development config with partial overrides."""
        overrides = {
            "timeout": 60,
        }

        config = create_development_cli_config(**overrides)

        # Check overridden values
        assert config.timeout == 60

        # Check defaults are preserved
        assert config.debug is True


class TestCreateProductionCLIConfig:
    """Test create_production_cli_config function."""

    def test_create_production_config_default(self) -> None:
        """Test creating production config with defaults."""
        config = create_production_cli_config()

        # Test actual CLISettings attributes
        assert config.debug is False
        assert config.project_name == "flext-cli"
        assert config.project_version == "0.7.0"
        assert config.api_url == "https://api.flext-platform.com"
        assert config.timeout == 30
        assert config.output_format == "table"

    def test_create_production_config_with_overrides(self) -> None:
        """Test creating production config with overrides."""
        overrides = {"api_url": "https://custom.api.com", "debug": True, "timeout": 60}

        config = create_production_cli_config(**overrides)

        # Check overridden values
        assert config.api_url == "https://custom.api.com"
        assert config.debug is True
        assert config.timeout == 60

        # Check defaults
        assert config.project_name == "flext-cli"
        assert config.output_format == "table"


class TestGetCLISettings:
    """Test get_cli_settings function."""

    def test_get_cli_settings_returns_settings_instance(self) -> None:
        """Test get_cli_settings returns a valid settings instance."""
        settings = get_cli_settings()

        # Check that it's the correct type and has expected attributes
        assert hasattr(settings, "project_name")
        assert hasattr(settings, "project_version")
        assert hasattr(settings, "api_url")
        assert hasattr(settings, "timeout")
        assert hasattr(settings, "output_format")
        assert hasattr(settings, "debug")

    def test_get_cli_settings_default_values(self) -> None:
        """Test get_cli_settings returns expected default values."""
        settings = get_cli_settings()

        assert settings.project_name == "flext-cli"
        assert settings.project_version == "0.7.0"
        assert settings.api_url == "http://localhost:8000"
        assert settings.timeout == 30
        assert settings.output_format == "table"
        assert settings.debug is False

    def test_get_cli_settings_is_consistent(self) -> None:
        """Test get_cli_settings returns consistent values across calls."""
        settings1 = get_cli_settings()
        settings2 = get_cli_settings()

        # Should have the same values (not necessarily the same instance due to singleton)
        assert settings1.project_name == settings2.project_name
        assert settings1.api_url == settings2.api_url
        assert settings1.debug == settings2.debug


class TestConfigValidation:
    """Test configuration validation and model behavior."""

    def test_development_config_model_validation(self) -> None:
        """Test that development config creates valid pydantic model."""
        config = create_development_cli_config()

        # Should be able to convert to dict
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert "debug" in config_dict
        assert "api_url" in config_dict

        # Should be able to validate from dict
        new_config = config.__class__.model_validate(config_dict)
        assert new_config.debug == config.debug
        assert new_config.api_url == config.api_url

    def test_production_config_model_validation(self) -> None:
        """Test that production config creates valid pydantic model."""
        config = create_production_cli_config()

        # Should be able to convert to dict
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert "debug" in config_dict
        assert "api_url" in config_dict

        # Should be able to validate from dict
        new_config = config.__class__.model_validate(config_dict)
        assert new_config.debug == config.debug
        assert new_config.api_url == config.api_url

    def test_config_handles_valid_values(self) -> None:
        """Test that configuration handles valid values properly."""
        config = create_development_cli_config(timeout=45, debug=False)

        # Values should be correctly set
        assert config.timeout == 45
        assert config.debug is False


class TestConfigurationTypes:
    """Test configuration type validation."""

    def test_development_config_types(self) -> None:
        """Test development config creates correct types."""
        config = create_development_cli_config()

        assert isinstance(config.debug, bool)
        assert isinstance(config.project_name, str)
        assert isinstance(config.api_url, str)
        assert isinstance(config.timeout, int)

    def test_production_config_types(self) -> None:
        """Test production config creates correct types."""
        config = create_production_cli_config()

        assert isinstance(config.debug, bool)
        assert isinstance(config.project_name, str)
        assert isinstance(config.api_url, str)
        assert isinstance(config.timeout, int)
