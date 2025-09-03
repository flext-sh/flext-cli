"""Tests for FlextCliConfig utilities - Real functionality testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Testing FlextCliConfig unified configuration class and utility functions
with real functionality, no mocking.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from flext_core import FlextResult
from flext_cli.config import FlextCliConfig, FlextCliSettings, get_config


class TestFlextCliConfigUtilities(unittest.TestCase):
    """Test FlextCliConfig utilities and factory functions."""

    def test_get_config_function(self) -> None:
        """Test get_config factory function."""
        config = get_config()

        assert isinstance(config, FlextCliConfig)
        assert config.output_format == "table"
        assert config.debug is False
        assert config.profile == "default"

    def test_config_factory_methods(self) -> None:
        """Test FlextCliConfig factory methods."""
        # Test development config
        dev_result = FlextCliConfig.create_development_config()
        assert isinstance(dev_result, FlextResult)
        assert dev_result.is_success

        dev_config = dev_result.value
        assert dev_config.debug is True
        assert dev_config.verbose is True

        # Test production config
        prod_result = FlextCliConfig.create_production_config()
        assert isinstance(prod_result, FlextResult)
        assert prod_result.is_success

        prod_config = prod_result.value
        assert prod_config.debug is False
        assert prod_config.quiet is True

    def test_config_with_directories(self) -> None:
        """Test FlextCliConfig with custom directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = FlextCliConfig.create_with_directories(
                {
                    "config_dir": str(temp_path / "config"),
                    "cache_dir": str(temp_path / "cache"),
                    "log_dir": str(temp_path / "logs"),
                    "data_dir": str(temp_path / "data"),
                    "debug": True,
                }
            )

            assert isinstance(result, FlextResult)
            assert result.is_success

            config = result.value
            assert config.debug is True
            assert config.config_dir == temp_path / "config"
            assert config.cache_dir == temp_path / "cache"
            assert config.log_dir == temp_path / "logs"
            assert config.data_dir == temp_path / "data"

    def test_config_validation_workflow(self) -> None:
        """Test complete configuration validation workflow."""
        config = FlextCliConfig(
            output_format="json", api_timeout=45, retries=5, debug=True
        )

        # Test validation
        validation_result = config.validate_business_rules()
        assert isinstance(validation_result, FlextResult)
        assert validation_result.is_success

        # Test directory setup
        setup_result = config.ensure_setup()
        assert isinstance(setup_result, FlextResult)
        assert setup_result.is_success

    def test_config_serialization_utilities(self) -> None:
        """Test configuration serialization utilities."""
        config = FlextCliConfig(
            output_format="yaml",
            debug=True,
            api_timeout=60,
            project_name="test-project",
        )

        # Test model serialization
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)

        # Verify key fields
        assert config_dict["output_format"] == "yaml"
        assert config_dict["debug"] is True
        assert config_dict["api_timeout"] == 60
        assert config_dict["project_name"] == "test-project"

    def test_config_property_utilities(self) -> None:
        """Test configuration property utilities."""
        config = FlextCliConfig(
            profile="development", debug=True, api_url="https://api.example.com/"
        )

        # Test computed properties
        assert config.is_development is True
        assert config.is_production is False
        assert config.base_url == "https://api.example.com"  # Without trailing slash


class TestFlextCliSettingsAlias(unittest.TestCase):
    """Test FlextCliSettings backward compatibility alias."""

    def test_settings_is_config_alias(self) -> None:
        """Test FlextCliSettings is proper alias for FlextCliConfig."""
        settings = FlextCliSettings()

        assert isinstance(settings, FlextCliConfig)
        assert hasattr(settings, "output_format")
        assert hasattr(settings, "api_url")
        assert hasattr(settings, "debug")

    def test_settings_functionality(self) -> None:
        """Test FlextCliSettings has same functionality as FlextCliConfig."""
        settings = FlextCliSettings(debug=True, output_format="json", api_timeout=90)

        assert settings.debug is True
        assert settings.output_format == "json"
        assert settings.api_timeout == 90

        # Test methods work
        validation = settings.validate_business_rules()
        assert isinstance(validation, FlextResult)
        assert validation.is_success


class TestConfigurationProviders(unittest.TestCase):
    """Test FlextCliConfig configuration providers."""

    def test_args_provider(self) -> None:
        """Test ArgsProvider functionality."""
        config = FlextCliConfig()

        args = {"debug": True, "output_format": "yaml", "api_timeout": 120}

        provider = config.ArgsProvider(args)

        # Test priority
        assert provider.get_priority() > 0

        # Test config retrieval
        debug_result = provider.get_config("debug")
        assert isinstance(debug_result, FlextResult)
        assert debug_result.is_success
        assert debug_result.value is True

        # Test get_all
        all_args = provider.get_all()
        assert isinstance(all_args, dict)
        assert all_args["debug"] is True

    def test_constants_provider(self) -> None:
        """Test ConstantsProvider functionality."""
        config = FlextCliConfig()

        constants = {"default_timeout": 30, "max_retries": 3, "api_host": "localhost"}

        provider = config.ConstantsProvider(constants)

        # Test priority (should be lowest)
        assert provider.get_priority() == 0

        # Test config retrieval
        timeout_result = provider.get_config("default_timeout")
        assert isinstance(timeout_result, FlextResult)
        assert timeout_result.is_success
        assert timeout_result.value == 30

        # Test get_all
        all_constants = provider.get_all()
        assert isinstance(all_constants, dict)
        assert all_constants["max_retries"] == 3


class TestConfigurationIntegration(unittest.TestCase):
    """Integration tests for configuration utilities."""

    def test_complete_config_workflow(self) -> None:
        """Test complete configuration creation and usage workflow."""
        # Create config through factory
        config = get_config()

        # Verify it's properly initialized
        assert isinstance(config, FlextCliConfig)
        assert config.output_format in ["table", "json", "yaml", "csv"]
        assert isinstance(config.api_timeout, int)
        assert config.api_timeout > 0

        # Test nested classes work
        defaults = config.CliDefaults()
        assert hasattr(defaults, "Command")
        assert hasattr(defaults, "Output")

        # Test directory manager
        dir_manager = config.CliDirectories(config)
        assert hasattr(dir_manager, "create_directories")
        assert hasattr(dir_manager, "validate_directories")

    def test_config_profile_loading(self) -> None:
        """Test configuration profile loading workflow."""
        result = FlextCliConfig.load_from_profile("test-profile")

        assert isinstance(result, FlextResult)
        assert result.is_success

        config = result.value
        assert config.profile == "test-profile"
        assert isinstance(config, FlextCliConfig)

    def test_config_environment_consistency(self) -> None:
        """Test configuration consistency across different creation methods."""
        # Different ways to create config should be consistent
        config1 = FlextCliConfig()
        config2 = get_config()
        result = FlextCliConfig.create_with_directories({})
        assert result.is_success
        config3 = result.value

        # All should be FlextCliConfig instances
        assert isinstance(config1, FlextCliConfig)
        assert isinstance(config2, FlextCliConfig)
        assert isinstance(config3, FlextCliConfig)

        # Default values should be consistent
        assert config1.output_format == config2.output_format == config3.output_format
        assert config1.api_timeout == config2.api_timeout == config3.api_timeout


if __name__ == "__main__":
    unittest.main()
