"""Real functionality tests for FlextCliConfig unified class.

Following ZERO TOLERANCE requirements:
- NO mocking whatsoever - real functionality testing only
- 100% test coverage using actual code execution
- Tests validate real business logic and configuration behavior
- All tests use FlextCliConfig unified class following flext-core patterns


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from flext_core import FlextResult, FlextTypes

from flext_cli.config import FlextCliConfig


class TestFlextCliConfig(unittest.TestCase):
    """Real functionality tests for FlextCliConfig unified configuration class."""

    def test_config_defaults(self) -> None:
        """Test FlextCliConfig initialization with default values."""
        config = FlextCliConfig()

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
        """Test FlextCliConfig with custom values."""
        config = FlextCliConfig(
            output_format="json",
            no_color=True,
            quiet=True,
            verbose=False,
            debug=True,
            api_timeout=60,
            retries=5,
            project_name="custom-project",
        )

        assert config.output_format == "json"
        assert config.no_color is True
        assert config.quiet is True
        assert config.verbose is False
        assert config.debug is True
        assert config.api_timeout == 60
        assert config.retries == 5
        assert config.project_name == "custom-project"

    def test_config_output_formats(self) -> None:
        """Test FlextCliConfig with all valid output formats."""
        valid_formats = ["table", "json", "yaml", "csv"]

        for format_type in valid_formats:
            config = FlextCliConfig(output_format=format_type)
            assert config.output_format == format_type

    def test_config_directory_setup(self) -> None:
        """Test FlextCliConfig directory creation and validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config = FlextCliConfig(
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
        """Test FlextCliConfig business rules validation."""
        # Valid configuration should pass validation
        config = FlextCliConfig()
        validation_result = config.validate_business_rules()
        assert isinstance(validation_result, FlextResult)
        assert validation_result.is_success

    def test_config_nested_classes(self) -> None:
        """Test FlextCliConfig nested classes structure."""
        config = FlextCliConfig()

        # Test nested classes exist and work
        defaults = config.CliDefaults()
        assert hasattr(defaults, "Command")
        assert hasattr(defaults, "Output")
        assert hasattr(defaults, "Auth")

        # Test constants are accessible
        assert hasattr(defaults.Command, "timeout_seconds")
        assert hasattr(defaults.Output, "default_format")
        assert hasattr(defaults.Auth, "token_expiry_hours")

        # Test directory manager
        dir_manager = config.CliDirectories(config)
        assert hasattr(dir_manager, "create_directories")
        assert hasattr(dir_manager, "validate_directories")

    def test_config_factory_methods(self) -> None:
        """Test FlextCliConfig factory methods for different environments."""
        # Development configuration
        dev_result = FlextCliConfig.create_development_config()
        assert isinstance(dev_result, FlextResult)
        assert dev_result.is_success
        dev_config = dev_result.value
        assert dev_config.debug is True
        assert dev_config.trace is True

        # Production configuration
        prod_result = FlextCliConfig.create_production_config()
        assert isinstance(prod_result, FlextResult)
        assert prod_result.is_success
        prod_config = prod_result.value
        assert prod_config.debug is False
        assert prod_config.quiet is True

    def test_config_serialization(self) -> None:
        """Test FlextCliConfig serialization and property access."""
        config = FlextCliConfig(output_format="json", debug=True, api_timeout=45)

        # Test model serialization
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert config_dict["output_format"] == "json"
        assert config_dict["debug"] is True
        assert config_dict["api_timeout"] == 45

        # Test properties
        assert config.is_development_mode is True
        assert config.is_production_mode is False
        assert config.base_url == config.api_url.rstrip("/")


class TestConfigIntegration(unittest.TestCase):
    """Real functionality integration tests for complete configuration system."""

    def test_complete_config_workflow(self) -> None:
        """Test complete configuration creation, setup, and usage workflow."""
        # Create configuration with directories
        config_result = FlextCliConfig.create_with_directories(
            {"debug": True, "output_format": "json", "api_timeout": 60},
        )

        assert isinstance(config_result, FlextResult)
        assert config_result.is_success

        config = config_result.value
        assert config.debug is True
        assert config.output_format == "json"
        assert config.api_timeout == 60

        # Test validation
        validation_result = config.validate_business_rules()
        assert validation_result.is_success

    def test_profile_loading(self) -> None:
        """Test configuration profile loading."""
        profile_result = FlextCliConfig.load_from_profile("test-profile")
        assert isinstance(profile_result, FlextResult)
        assert profile_result.is_success

        config = profile_result.value
        assert config.profile == "test-profile"

    def test_configuration_providers(self) -> None:
        """Test FlextCliConfig configuration providers."""
        config = FlextCliConfig()

        # Test ArgsProvider
        args = {"debug": True, "output_format": "yaml"}
        args_provider = config.ArgsProvider(args)
        assert args_provider.get_priority() > 0

        debug_result = args_provider.get_config("debug")
        assert debug_result.is_success
        assert debug_result.value is True

        # Test ConstantsProvider
        constants: FlextTypes.Core.Dict = {"default_timeout": 30}
        constants_provider = config.ConstantsProvider(constants)
        assert constants_provider.get_priority() == 0

        timeout_result = constants_provider.get_config("default_timeout")
        assert timeout_result.is_success
        assert timeout_result.value == 30


if __name__ == "__main__":
    unittest.main()
