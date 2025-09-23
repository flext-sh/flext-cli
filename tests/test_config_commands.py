"""Tests for config commands - Real API only.

Tests configuration functionality using actual implemented methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCliApi, FlextCliMain
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class TestFlextCliConfig:
    """Test FlextCliConfig with real API."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.config = FlextCliModels.FlextCliConfig()

    def test_config_creation_basic(self) -> None:
        """Test config creation with default values."""
        assert self.config.profile == "default"
        assert self.config.output_format == "table"
        assert self.config.debug_mode is False

    def test_config_creation_custom(self) -> None:
        """Test config creation with custom values."""
        config = FlextCliModels.FlextCliConfig(
            profile="test",
            output_format="json",
            debug=True,
        )

        assert config.profile == "test"
        assert config.output_format == "json"
        assert config.debug_mode is True

    def test_config_serialization(self) -> None:
        """Test config serialization to dict."""
        config_dict = self.config.model_dump()

        assert isinstance(config_dict, dict)
        assert "profile" in config_dict
        assert "output_format" in config_dict
        assert "debug" in config_dict

    def test_config_get_config_dir(self) -> None:
        """Test get_config_dir method."""
        config_dir = self.config.get_config_dir()
        assert config_dir is not None
        assert config_dir.name == ".flext"

    def test_config_get_config_file(self) -> None:
        """Test get_config_file method."""
        config_file = self.config.get_config_file()
        assert config_file is not None
        assert config_file.name == "flext.toml"

    def test_config_validate_output_format_valid(self) -> None:
        """Test output format validation with valid format."""
        result = self.config.validate_output_format("json")
        assert result.is_success
        assert result.value == "json"

    def test_config_validate_output_format_invalid(self) -> None:
        """Test output format validation with invalid format."""
        result = self.config.validate_output_format("invalid")
        assert result.is_failure

    def test_config_is_debug_enabled(self) -> None:
        """Test is_debug_enabled method."""
        config_debug = FlextCliModels.FlextCliConfig(debug=True)
        config_no_debug = FlextCliModels.FlextCliConfig(debug=False)

        assert config_debug.is_debug_enabled() is True
        assert config_no_debug.is_debug_enabled() is False

    def test_config_get_output_format(self) -> None:
        """Test get_output_format method."""
        config = FlextCliModels.FlextCliConfig(output_format="yaml")
        assert config.get_output_format() == "yaml"

    def test_config_set_output_format_valid(self) -> None:
        """Test set_output_format with valid format."""
        result = self.config.set_output_format("json")
        assert result.is_success
        assert self.config.get_output_format() == "json"

    def test_config_set_output_format_invalid(self) -> None:
        """Test set_output_format with invalid format."""
        result = self.config.set_output_format("invalid")
        assert result.is_failure

    def test_config_create_cli_options(self) -> None:
        """Test create_cli_options method."""
        config = FlextCliModels.FlextCliConfig(
            output_format="json",
            debug=True,
        )
        cli_options = config.create_cli_options()

        assert isinstance(cli_options, FlextCliModels.CliOptions)
        assert cli_options.output_format == "json"
        assert cli_options.debug is True

    def test_config_create_default(self) -> None:
        """Test create_default class method."""
        config = FlextCliModels.FlextCliConfig.create_default()

        assert isinstance(config, FlextCliModels.FlextCliConfig)
        assert config.profile == "default"
        assert config.output_format == "table"
        assert config.debug_mode is False

    def test_config_load_configuration(self) -> None:
        """Test load_configuration method."""
        config = FlextCliModels.FlextCliConfig(
            profile="test",
            output_format="json",
            debug=True,
        )
        result = config.load_configuration()

        assert result.is_success
        config_data = result.value
        assert isinstance(config_data, dict)
        assert config_data["profile"] == "test"
        assert config_data["output_format"] == "json"
        assert config_data["debug_mode"] is True


class TestConfigWithCliApi:
    """Test config integration with CLI API."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.cli_api = FlextCliApi()
        self.config = FlextCliModels.FlextCliConfig()

    def test_config_format_as_json(self) -> None:
        """Test formatting config as JSON."""
        config_dict = self.config.model_dump()
        result = self.cli_api.format_data(config_dict, "json")

        assert result.is_success
        assert isinstance(result.value, str)
        assert "profile" in result.value

    def test_config_format_as_table(self) -> None:
        """Test formatting config as table."""
        config_dict = self.config.model_dump()
        result = self.cli_api.format_data(config_dict, "table")

        assert result.is_success
        assert isinstance(result.value, str)

    def test_config_display_data(self) -> None:
        """Test displaying config data."""
        config_dict = self.config.model_dump()

        format_result = self.cli_api.format_data(config_dict, "table")
        assert format_result.is_success

        display_result = self.cli_api.display_data(format_result.value)
        assert isinstance(display_result, FlextResult)
        assert display_result.is_success


class TestConfigCommandsWithMain:
    """Test config commands with FlextCliMain."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.config = FlextCliModels.FlextCliConfig.create_default()
        self.cli_main = FlextCliMain(
            name="test-config",
            description="Test config CLI",
        )

    def test_cli_main_creation(self) -> None:
        """Test CLI main creation for config commands."""
        assert self.cli_main is not None
        assert isinstance(self.cli_main, FlextCliMain)

    def test_config_with_cli_main(self) -> None:
        """Test using config with CLI main."""
        assert self.config is not None
        assert self.cli_main is not None

        config_dict = self.config.model_dump(exclude_unset=True)
        assert isinstance(config_dict, dict)
        assert len(config_dict) == 3  # profile, output_format, debug
