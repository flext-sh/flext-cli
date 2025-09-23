"""Tests for core functionality - Real API only.

Tests FlextCliService and FlextCliConfig using actual implemented methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.core import FlextCliService
from flext_cli.models import FlextCliModels
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
        config = FlextCliModels.FlextCliConfig()

        assert config.profile == "default"
        assert config.debug_mode is False
        assert config.output_format == "table"

    def test_config_creation_with_custom_values(self) -> None:
        """Test config creation with custom values."""
        config = FlextCliModels.FlextCliConfig(
            profile="test",
            debug=True,
            output_format="json",
        )

        assert config.profile == "test"
        assert config.debug_mode is True
        assert config.output_format == "json"

    def test_config_get_config_dir(self) -> None:
        """Test get_config_dir method."""
        config = FlextCliModels.FlextCliConfig()
        config_dir = config.get_config_dir()

        assert config_dir is not None
        assert config_dir.name == ".flext"

    def test_config_get_config_file(self) -> None:
        """Test get_config_file method."""
        config = FlextCliModels.FlextCliConfig()
        config_file = config.get_config_file()

        assert config_file is not None
        assert config_file.name == "flext.toml"

    def test_config_validate_output_format_valid(self) -> None:
        """Test output format validation with valid format."""
        config = FlextCliModels.FlextCliConfig()
        result = config.validate_output_format("json")

        assert result.is_success
        assert result.value == "json"

    def test_config_validate_output_format_invalid(self) -> None:
        """Test output format validation with invalid format."""
        config = FlextCliModels.FlextCliConfig()
        result = config.validate_output_format("invalid_format")

        assert result.is_failure
        assert "Invalid output format" in (result.error or "")

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
        config = FlextCliModels.FlextCliConfig()
        result = config.set_output_format("json")

        assert result.is_success
        assert config.get_output_format() == "json"

    def test_config_set_output_format_invalid(self) -> None:
        """Test set_output_format with invalid format."""
        config = FlextCliModels.FlextCliConfig()
        result = config.set_output_format("invalid")

        assert result.is_failure

    def test_config_create_cli_options(self) -> None:
        """Test create_cli_options method."""
        config = FlextCliModels.FlextCliConfig(output_format="json", debug=True)
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
        config = FlextCliModels.FlextCliConfig(debug=True)
        service = FlextCliService()

        health_result = service.flext_cli_health()
        assert isinstance(health_result, FlextResult)
        assert health_result.is_success

        config_result = config.load_configuration()
        assert isinstance(config_result, FlextResult)
        assert config_result.is_success

    def test_service_configure_with_config_object(self) -> None:
        """Test service configuration with FlextCliConfig object."""
        config = FlextCliModels.FlextCliConfig(
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
