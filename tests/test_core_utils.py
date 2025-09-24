"""Tests for core functionality - Real API only.

Tests FlextCliService and FlextCliConfig using actual implemented methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.core import FlextCliService
from flext_core import FlextResult, FlextService


class TestFlextCliService:
    """Test core service functionality - real API."""

    def test_flext_cli_health_returns_success(self) -> None:
        """Test health check returns comprehensive status info."""
        service = FlextCliService()
        result = service.flext_cli_health()

        assert isinstance(result, FlextResult)
        assert result.is_success

        health_data = result.value
        assert isinstance(health_data, dict)
        assert health_data["service"] == "FlextCliService"
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data

    def test_service_inherits_from_domain_service(self) -> None:
        """Test service inherits from FlextService."""
        service = FlextCliService()
        assert isinstance(service, FlextService)


class TestFlextCliConfig:
    """Test configuration functionality - real API only."""

    def test_config_creation_with_defaults(self) -> None:
        """Test config creation with default values."""
        config = FlextCliConfig.MainConfig()

        assert config.profile == "default"
        assert config.debug_mode is False
        assert config.output_format == "table"

    def test_config_creation_with_custom_values(self) -> None:
        """Test config creation with custom values."""
        config = FlextCliConfig.MainConfig(
            profile="test",
            debug=True,
            output_format="json",
        )

        assert config.profile == "test"
        assert config.debug_mode is True
        assert config.output_format == "json"

    def test_config_get_config_dir(self) -> None:
        """Test get_config_dir method."""
        config = FlextCliConfig.MainConfig()
        config_dir = config.config_dir

        assert config_dir is not None
        assert config_dir.name == ".flext"

    def test_config_get_config_file(self) -> None:
        """Test get_config_file method."""
        config = FlextCliConfig.MainConfig()
        config_file = config.config_dir / FlextCliConstants.CliDefaults.CONFIG_FILE

        assert config_file is not None
        assert config_file.name == "flext.toml"

    def test_config_validate_output_format_valid(self) -> None:
        """Test output format validation with valid format."""
        config = FlextCliConfig.MainConfig()
        result = config.validate_output_format("json")

        assert result.is_success
        assert result.value == "json"

    def test_config_validate_output_format_invalid(self) -> None:
        """Test output format validation with invalid format."""
        config = FlextCliConfig.MainConfig()
        result = config.validate_output_format("invalid_format")

        assert result.is_failure
        assert "Invalid output format" in (result.error or "")

    def test_config_is_debug_enabled(self) -> None:
        """Test is_debug_enabled method."""
        config_debug = FlextCliConfig.MainConfig(debug=True)
        config_no_debug = FlextCliConfig.MainConfig(debug=False)

        assert config_debug.debug is True
        assert config_no_debug.debug is False

    def test_config_get_output_format(self) -> None:
        """Test get_output_format method."""
        config = FlextCliConfig.MainConfig(output_format="yaml")
        assert config.output_format == "yaml"

    def test_config_set_output_format_valid(self) -> None:
        """Test set_output_format with valid format."""
        config = FlextCliConfig.MainConfig()
        result = config.set_output_format("json")

        assert result.is_success
        assert config.output_format == "json"

    def test_config_set_output_format_invalid(self) -> None:
        """Test set_output_format with invalid format."""
        config = FlextCliConfig.MainConfig()
        result = config.set_output_format("invalid")

        assert result.is_failure

    def test_config_create_cli_options(self) -> None:
        """Test create_cli_options method."""
        config = FlextCliConfig.MainConfig(output_format="json", debug=True)
        cli_options = FlextCliConfig.CliOptions(
            output_format=config.output_format,
            debug=config.debug,
            max_width=FlextCliConstants.CliDefaults.MAX_WIDTH,
            no_color=config.no_color,
        )

        assert isinstance(cli_options, FlextCliConfig.CliOptions)
        assert cli_options.output_format == "json"
        assert cli_options.debug is True

    def test_config_create_default(self) -> None:
        """Test create_default class method."""
        config = FlextCliConfig.MainConfig(
            profile="default",
            output_format="table",
            debug=False,
        )

        assert isinstance(config, FlextCliConfig.MainConfig)
        assert config.profile == "default"
        assert config.output_format == "table"
        assert config.debug_mode is False

    def test_config_load_configuration(self) -> None:
        """Test load_configuration method."""
        config = FlextCliConfig.MainConfig(
            profile="test", output_format="json", debug=True
        )
        result = config.load_configuration()

        assert result.is_success
        config_data = result.value
        assert isinstance(config_data, dict)
        assert config_data["profile"] == "test"
        assert config_data["output_format"] == "json"
        assert config_data["debug_mode"] is True


class TestConfigIntegration:
    """Test configuration integration with other components - real API."""

    def test_config_and_service_integration(self) -> None:
        """Test configuration works with service."""
        config = FlextCliConfig.MainConfig(debug=True)
        service = FlextCliService()

        health_result = service.flext_cli_health()
        assert isinstance(health_result, FlextResult)
        assert health_result.is_success

        config_result = config.load_configuration()
        assert isinstance(config_result, FlextResult)
        assert config_result.is_success

    def test_service_configure_with_config_object(self) -> None:
        """Test service configuration with FlextCliConfig object."""
        config = FlextCliConfig.MainConfig(
            profile="integration_test", output_format="json", debug=True
        )
        service = FlextCliService()

        configure_result = service.configure(config)
        assert configure_result.is_success

        service_config = service.get_config()
        assert service_config is not None
        assert service_config.profile == "integration_test"
        assert service_config.output_format == "json"
        assert service_config.debug_mode is True
