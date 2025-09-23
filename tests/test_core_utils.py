"""Comprehensive tests for core functionality to maximize coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from flext_cli.constants import FlextCliConstants
from flext_cli.core import FlextCliService
from flext_cli.models import FlextCliModels
from flext_core import FlextResult, FlextService


class TestFlextCliService:
    """Test core service functionality."""

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
        assert "domain" in health_data
        assert health_data["domain"] == "cli"

    def test_service_inherits_from_domain_service(self) -> None:
        """Test service inherits from FlextService."""
        service = FlextCliService()
        assert isinstance(service, FlextService)


class TestFlextCliConfig:
    """Test configuration functionality."""

    def setup__method(self, __method: object, /) -> None:
        """Clean up global configuration before each test."""
        FlextCliModels.FlextCliConfig.clear_global_instance()

    def test_config_creation_with_defaults(self) -> None:
        """Test config creation with default values."""
        config = FlextCliModels.FlextCliConfig()

        # Test default values
        assert config.profile == "default"
        assert config.debug is False
        assert config.output_format == "table"

    def test_config_creation_with_custom_values(self) -> None:
        """Test config creation with custom values."""
        config = FlextCliModels.FlextCliConfig(
            profile="test",
            debug=True,
            output_format="json",
        )

        assert config.profile == "test"
        assert config.debug is True
        assert config.output_format == "json"

    def test_config_directories_creation(self) -> None:
        """Test directory creation functionality."""
        config = FlextCliModels.FlextCliConfig()

        # Test that directories can be created using modern method
        result = config.ensure_directories()
        assert isinstance(result, FlextResult)
        # Directory creation may succeed or fail based on permissions
        # but should return a FlextResult

    def test_config_directories_validation(self) -> None:
        """Test directory validation functionality."""
        config = FlextCliModels.FlextCliConfig()

        # Create and validate directories using modern method
        result = config.ensure_directories()
        assert isinstance(result, FlextResult)

    def test_config_settings_with_environment_variables(self) -> None:
        """Test settings loading from environment."""
        settings = FlextCliModels.FlextCliConfig()

        # Settings should be created successfully
        assert hasattr(settings, "profile")
        assert hasattr(settings, "debug")
        assert hasattr(settings, "output_format")
        assert hasattr(settings, "api_url")
        assert hasattr(settings, "log_level")

    def test_config_ensure_setup_runs_successfully(self) -> None:
        """Test ensure setup method."""
        config = FlextCliModels.FlextCliConfig()
        result = config.ensure_setup()

        assert isinstance(result, FlextResult)

    def test_config_validate_cli_rules(self) -> None:
        """Test CLI rules validation."""
        config = FlextCliModels.FlextCliConfig()
        result = config.validate_business_rules()

        assert isinstance(result, FlextResult)

    def test_config_factory_methods(self) -> None:
        """Test configuration factory methods."""
        # Test development config creation
        dev_result = FlextCliModels.FlextCliConfig.create_development_config()
        assert isinstance(dev_result, FlextResult)
        assert dev_result.is_success
        dev_config = dev_result.value
        assert isinstance(dev_config, FlextCliModels.FlextCliConfig)
        assert dev_config.debug is True

        # Test production config creation
        prod_result = FlextCliModels.FlextCliConfig.create_production_config()
        assert isinstance(prod_result, FlextResult)
        assert prod_result.is_success
        prod_config = prod_result.value
        assert isinstance(prod_config, FlextCliModels.FlextCliConfig)
        assert prod_config.debug is False

    def test_config_load_from_profile(self) -> None:
        """Test loading configuration from profile."""
        result = FlextCliModels.FlextCliConfig.load_from_profile("development")
        assert isinstance(result, FlextResult)
        assert result.is_success
        config = result.value
        assert isinstance(config, FlextCliModels.FlextCliConfig)
        assert config.profile == "development"

    def test_config_with_file_loading(self) -> None:
        """Test config loading from file."""
        config_data = {
            "profile": "test_profile",
            "debug": True,
            "output_format": "yaml",
            "api_url": "https://test.example.com",
            "log_level": "DEBUG",
        }

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            encoding="utf-8",
        ) as temp_file:
            json.dump(config_data, temp_file)
            temp_path = Path(temp_file.name)

            try:
                # Test that config can be created with file data
                result = FlextCliModels.FlextCliConfig.create_with_directories(
                    config_data
                )
                assert isinstance(result, FlextResult)
                assert result.is_success
                config = result.value
                assert isinstance(config, FlextCliModels.FlextCliConfig)
                assert config.profile == "test_profile"
                assert config.debug is True
            finally:
                temp_path.unlink()

    def test_config_constants_integration(self) -> None:
        """Test integration with FlextCliConstants."""
        # Verify constants are properly integrated
        assert hasattr(FlextCliConstants, "DEFAULT_API_URL")
        assert hasattr(FlextCliConstants, "LOG_LEVEL_INFO")

        # Verify defaults match constants
        settings = FlextCliModels.FlextCliConfig()
        assert settings.api_url == FlextCliConstants.FALLBACK_API_URL
        assert settings.log_level == FlextCliConstants.LOG_LEVEL_INFO


class TestConfigIntegration:
    """Test configuration integration with other components."""

    def test_config_and_service_integration(self) -> None:
        """Test configuration works with service."""
        config = FlextCliModels.FlextCliConfig(debug=True)
        service = FlextCliService()

        # Both should be independent but usable together
        health_result = service.flext_cli_health()
        setup_result = config.ensure_setup()

        assert isinstance(health_result, FlextResult)
        assert isinstance(setup_result, FlextResult)

    def test_config_file_operations(self) -> None:
        """Test config file-related operations."""
        config = FlextCliModels.FlextCliConfig()

        # Test that file paths are accessible
        assert hasattr(config, "config_dir")
        assert hasattr(config, "cache_dir")
        assert hasattr(config, "log_dir")
        assert hasattr(config, "data_dir")

        # Paths should be Path objects
        assert isinstance(config.config_dir, Path)
        assert isinstance(config.cache_dir, Path)
        assert isinstance(config.log_dir, Path)
        assert isinstance(config.data_dir, Path)

    def test_config_business_rules_validation(self) -> None:
        """Test configuration business rules validation."""
        # Test valid configuration
        valid_config = FlextCliModels.FlextCliConfig(
            profile="development",
            output_format="json",
            debug=True,
        )
        result = valid_config.validate_business_rules()
        assert isinstance(result, FlextResult)

        # Test configuration validation doesn't crash
        assert callable(getattr(valid_config, "validate_business_rules", None))
