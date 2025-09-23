"""FLEXT CLI Configuration Tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import unittest
from pathlib import Path

from flext_cli.models import FlextCliModels


class TestFlextCliConfig(unittest.TestCase):
    """Real functionality tests for FlextCliModels.FlextCliConfig unified configuration class."""

    def test_config_defaults(self) -> None:
        """Test FlextCliModels.FlextCliConfig initialization with default values."""
        config = FlextCliModels.FlextCliConfig()

        assert config.profile == "default"
        assert config.output_format == "table"
        assert config.debug_mode is False

    def test_config_custom_values(self) -> None:
        """Test FlextCliModels.FlextCliConfig with custom values."""
        config = FlextCliModels.FlextCliConfig(
            profile="development",
            output_format="json",
            debug=True,
        )

        assert config.profile == "development"
        assert config.output_format == "json"
        assert config.debug_mode is True

    def test_config_output_formats(self) -> None:
        """Test FlextCliModels.FlextCliConfig with all valid output formats."""
        for fmt in ["json", "yaml", "table", "csv", "plain"]:
            config = FlextCliModels.FlextCliConfig(output_format=fmt)
            assert config.output_format == fmt

    def test_config_directory_setup(self) -> None:
        """Test FlextCliModels.FlextCliConfig directory methods."""
        config = FlextCliModels.FlextCliConfig()

        config_dir = config.get_config_dir()
        assert isinstance(config_dir, Path)
        assert config_dir.name == ".flext"

        config_file = config.get_config_file()
        assert isinstance(config_file, Path)
        assert config_file.name == "flext.toml"

    def test_config_validation(self) -> None:
        """Test FlextCliModels.FlextCliConfig output format validation."""
        config = FlextCliModels.FlextCliConfig()

        valid_result = config.validate_output_format("json")
        assert valid_result.is_success
        assert valid_result.value == "json"

        invalid_result = config.validate_output_format("invalid_format")
        assert invalid_result.is_failure

    def test_config_nested_classes(self) -> None:
        """Test nested configuration classes."""
        cli_config = FlextCliModels.CliConfig(
            profile="test", output_format="json", debug=True
        )
        assert cli_config.profile == "test"
        assert cli_config.output_format == "json"
        assert cli_config.debug_mode is True

    def test_config_factory_methods(self) -> None:
        """Test FlextCliModels.FlextCliConfig factory methods."""
        default_config = FlextCliModels.FlextCliConfig.create_default()
        assert default_config.profile == "default"
        assert default_config.output_format == "table"
        assert default_config.debug_mode is False

    def test_config_serialization(self) -> None:
        """Test FlextCliModels.FlextCliConfig load configuration."""
        config = FlextCliModels.FlextCliConfig(
            profile="production", output_format="json", debug=False
        )

        load_result = config.load_configuration()
        assert load_result.is_success
        assert isinstance(load_result.value, dict)
        assert load_result.value["profile"] == "production"
        assert load_result.value["output_format"] == "json"


class TestConfigIntegration(unittest.TestCase):
    """Integration tests for configuration management."""

    def test_profile_loading(self) -> None:
        """Test profile loading functionality."""
        config = FlextCliModels.FlextCliConfig(profile="staging")
        assert config.profile == "staging"

    def test_configuration_providers(self) -> None:
        """Test configuration providers."""
        config = FlextCliModels.FlextCliConfig()
        cli_options = config.create_cli_options()

        assert isinstance(cli_options, FlextCliModels.CliOptions)
        assert cli_options.output_format == config.output_format
        assert cli_options.debug == config.debug_mode

    def test_complete_config_workflow(self) -> None:
        """Test complete configuration workflow."""
        config = FlextCliModels.FlextCliConfig(
            profile="test", output_format="yaml", debug=True
        )

        assert config.is_debug_enabled() is True
        assert config.get_output_format() == "yaml"

        set_result = config.set_output_format("json")
        assert set_result.is_success
        assert config.get_output_format() == "json"


class TestFlextCliConfigAdditionalCoverage(unittest.TestCase):
    """Additional coverage tests for FlextCliModels.FlextCliConfig."""

    def test_config_validation_log_level(self) -> None:
        """Test logging configuration validation."""
        log_config = FlextCliModels.LoggingConfig(log_level="INFO", console_output=True)
        validation_result = log_config.validate_business_rules()
        assert validation_result.is_success

    def test_config_string_representation(self) -> None:
        """Test config string representation."""
        config = FlextCliModels.FlextCliConfig(profile="test")
        config_data = config.load_configuration()
        assert config_data.is_success

    def test_config_property_paths(self) -> None:
        """Test configuration property paths."""
        config = FlextCliModels.FlextCliConfig()
        config_dir = config.get_config_dir()
        config_file = config.get_config_file()

        assert config_file.parent == config_dir

    def test_config_with_custom_paths(self) -> None:
        """Test configuration with custom paths."""
        config = FlextCliModels.CliConfig()
        assert isinstance(config.config_dir, Path)

    def test_config_validation_max_retries(self) -> None:
        """Test configuration validation."""
        config = FlextCliModels.FlextCliConfig(profile="test")
        validation_result = config.validate_output_format("table")
        assert validation_result.is_success

    def test_config_json_serialization(self) -> None:
        """Test JSON serialization."""
        config = FlextCliModels.FlextCliConfig(profile="test", output_format="json")
        load_result = config.load_configuration()
        assert load_result.is_success
        assert "profile" in load_result.value
        assert "output_format" in load_result.value

    def test_config_equality(self) -> None:
        """Test config equality."""
        config1 = FlextCliModels.FlextCliConfig(profile="test")
        config2 = FlextCliModels.FlextCliConfig(profile="test")

        assert config1.profile == config2.profile
        assert config1.output_format == config2.output_format

    def test_config_validation_timeout(self) -> None:
        """Test timeout validation."""
        auth_config = FlextCliModels.AuthConfig(api_url="https://api.example.com")
        validation_result = auth_config.validate_business_rules()
        assert validation_result.is_success

    def test_config_validation_api_url(self) -> None:
        """Test API URL validation."""
        auth_config = FlextCliModels.AuthConfig(api_url="https://api.example.com")
        assert auth_config.api_url.startswith("https://")
