"""FLEXT CLI Configuration Tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from flext_cli.configs import FlextCliConfigs
from flext_core import FlextResult


class TestFlextCliConfigs(unittest.TestCase):
    """Real functionality tests for FlextCliConfigs unified configuration class."""

    def test_config_defaults(self) -> None:
        """Test FlextCliConfigs initialization with default values."""
        config = FlextCliConfigs()

        # Output configuration defaults
        assert config.output_format == "table"
        assert config.no_color is False
        assert config.quiet is False
        assert config.verbose is False
        assert config.pager is None

        # API configuration defaults
        assert config.api_url.startswith("http")
        assert config.api_timeout == 30
        assert config.connect_timeout == 30
        assert config.read_timeout == 60  # DEFAULT_READ_TIMEOUT = 60
        assert config.retries == 3
        assert config.verify_ssl is True

        # Project identity defaults
        assert config.project_name == "flext-cli"
        assert (
            config.project_description == "FLEXT CLI - Developer Command Line Interface"
        )
        assert config.project_version == "0.9.0"

        # Directory paths are Path objects
        assert isinstance(config.config_dir, Path)
        assert isinstance(config.cache_dir, Path)
        assert isinstance(config.log_dir, Path)
        assert isinstance(config.data_dir, Path)

        # Auth configuration defaults
        assert isinstance(config.token_file, Path)
        assert isinstance(config.refresh_token_file, Path)
        assert config.auto_refresh is True

    def test_config_custom_values(self) -> None:
        """Test FlextCliConfigs with custom values."""
        config = FlextCliConfigs(
            output_format="json",
            no_color=True,
            quiet=True,
            verbose=False,
            debug=True,
            timeout_seconds=60,
            max_command_retries=5,
            app_name="custom-project",
        )

        assert config.output_format == "json"
        assert config.no_color is True
        assert config.quiet is True
        assert config.verbose is False
        assert config.debug is True
        assert config.timeout_seconds == 60
        assert config.max_command_retries == 5
        assert config.app_name == "custom-project"

    def test_config_output_formats(self) -> None:
        """Test FlextCliConfigs with all valid output formats."""
        valid_formats = ["table", "json", "yaml", "csv"]

        for format_type in valid_formats:
            config = FlextCliConfigs(output_format=format_type)
            assert config.output_format == format_type

    def test_config_directory_setup(self) -> None:
        """Test FlextCliConfigs directory creation and validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config = FlextCliConfigs(
                config_dir=temp_path / "config",
                cache_dir=temp_path / "cache",
                log_dir=temp_path / "logs",
                data_dir=temp_path / "data",
            )

            # Test directory setup
            setup_result = config.ensure_setup()
            assert isinstance(setup_result, FlextResult)
            assert setup_result.is_success

            # Verify directories were created
            assert config.config_dir.exists()
            assert config.cache_dir.exists()
            assert config.log_dir.exists()
            assert config.data_dir.exists()

    def test_config_validation(self) -> None:
        """Test FlextCliConfigs business rules validation."""
        # Valid configuration should pass validation
        config = FlextCliConfigs()
        validation_result = config.validate_business_rules()
        assert isinstance(validation_result, FlextResult)
        assert validation_result.is_success

    def test_config_nested_classes(self) -> None:
        """Test FlextCliConfigs simplified structure."""
        config = FlextCliConfigs()

        # Test that configuration fields are accessible directly
        assert hasattr(config, "profile")
        assert hasattr(config, "debug")
        assert hasattr(config, "output_format")
        assert hasattr(config, "api_url")
        assert hasattr(config, "command_timeout")

        # Test that configuration values are properly set
        assert config.profile == "default"
        assert config.debug is False
        assert config.output_format == "table"

    def test_config_factory_methods(self) -> None:
        """Test FlextCliConfigs factory methods for different environments."""
        # Development configuration
        dev_result = FlextCliConfigs.create_development_config()
        assert isinstance(dev_result, FlextResult)
        assert dev_result.is_success
        dev_config = dev_result.value
        assert dev_config.debug is True
        assert dev_config.trace is True

        # Production configuration
        prod_result = FlextCliConfigs.create_production_config()
        assert isinstance(prod_result, FlextResult)
        assert prod_result.is_success
        prod_config = prod_result.value
        assert prod_config.debug is False
        assert prod_config.quiet is True

    def test_config_serialization(self) -> None:
        """Test FlextCliConfigs serialization and property access."""
        config = FlextCliConfigs(output_format="json", debug=True, timeout_seconds=45)

        # Test model serialization
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert config_dict["output_format"] == "json"
        assert config_dict["debug"] is True
        assert config_dict["timeout_seconds"] == 45

        # Test properties
        assert config.is_development_mode is True
        assert config.is_production_mode is False
        assert config.base_url == config.api_url.rstrip("/")


class TestConfigIntegration(unittest.TestCase):
    """Real functionality integration tests for complete configuration system."""

    def test_complete_config_workflow(self) -> None:
        """Test complete configuration creation, setup, and usage workflow."""
        # Create configuration with directories
        config_result = FlextCliConfigs.create_with_directories(
            {"debug": True, "output_format": "json", "timeout_seconds": 60},
        )

        assert isinstance(config_result, FlextResult)
        assert config_result.is_success

        config = config_result.value
        assert config.debug is True
        assert config.output_format == "json"
        assert config.timeout_seconds == 60

        # Test validation
        validation_result = config.validate_business_rules()
        assert validation_result.is_success

    def test_profile_loading(self) -> None:
        """Test configuration profile loading."""
        profile_result = FlextCliConfigs.load_from_profile("test-profile")
        assert isinstance(profile_result, FlextResult)
        assert profile_result.is_success

        config = profile_result.value
        assert config.profile == "test-profile"

    def test_configuration_providers(self) -> None:
        """Test FlextCliConfigs simplified configuration management."""
        config = FlextCliConfigs()

        # Test that configuration can be updated directly
        config.debug = True
        config.output_format = "yaml"

        assert config.debug is True
        assert config.output_format == "yaml"

        # Test validation still works
        validation_result = config.validate_business_rules()
        assert validation_result.is_success

        # Test that configuration values are properly accessible
        assert config.profile is not None
        assert config.api_url is not None
        assert config.command_timeout > 0


if __name__ == "__main__":
    unittest.main()
