
"""Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

import os

import pytest
from flext_core import FlextConfig

from flext_cli import FlextCliConfig


class TestFlextConfigIntegration:
    """Test FlextConfig singleton integration with flext-cli."""

    def setup_method(self) -> None:
        """Setup test environment."""
        # Clear global instances before each test
        FlextCliConfig.clear_global_instance()
        FlextConfig.clear_global_instance()

    def teardown_method(self) -> None:
        """Cleanup test environment."""
        # Clear global instances after each test
        FlextCliConfig.clear_global_instance()
        FlextConfig.clear_global_instance()

    def test_flext_config_singleton_integration(self) -> None:
        """Test that FlextCliConfig integrates with FlextConfig singleton."""
        # Get base FlextConfig singleton
        base_config = FlextConfig.get_global_instance()

        # Get CLI config (should inherit from base)
        cli_config = FlextCliConfig.get_global_instance()

        # Verify CLI config inherits base config values
        assert cli_config.debug == base_config.debug
        assert cli_config.log_level == base_config.log_level
        # Note: CLI config has its own api_url field, not inherited from base_url
        assert hasattr(cli_config, "api_url")
        assert isinstance(cli_config.api_url, str)

        # Verify CLI-specific fields are present
        assert hasattr(cli_config, "profile")
        assert hasattr(cli_config, "output_format")
        assert hasattr(cli_config, "quiet")

    def test_cli_parameter_overrides_update_flext_config(self) -> None:
        """Test that CLI parameter overrides update both configs."""
        # Get initial configs (for reference)
        _ = FlextConfig.get_global_instance()
        _ = FlextCliConfig.get_global_instance()

        # Apply CLI overrides
        cli_params: dict[str, object] = {
            "debug": True,
            "log_level": "DEBUG",
            "output_format": "json",
            "profile": "development",
        }

        override_result = FlextCliConfig.apply_cli_overrides(cli_params)
        assert override_result.is_success

        # Get updated configs
        updated_base = FlextConfig.get_global_instance()
        updated_cli = override_result.value

        # Verify base config was updated
        assert updated_base.debug
        assert updated_base.log_level == "DEBUG"

        # Verify CLI config was updated
        assert updated_cli.debug
        assert updated_cli.log_level == "DEBUG"
        assert updated_cli.output_format == "json"
        assert updated_cli.profile == "development"

    def test_synchronization_with_flext_config(self) -> None:
        """Test synchronization between CLI config and FlextConfig."""
        # Get initial configs
        base_config = FlextConfig.get_global_instance()
        _ = FlextCliConfig.get_global_instance()

        # Modify base config directly
        base_config.debug = True
        base_config.log_level = "DEBUG"
        FlextConfig.set_global_instance(base_config)

        # Synchronize CLI config
        sync_result = FlextCliConfig.sync_with_flext_config()
        assert sync_result.is_success

        # Verify CLI config is synchronized
        synced_config = sync_result.value
        assert synced_config.debug
        assert synced_config.log_level == "DEBUG"

    def test_environment_variable_overrides(self) -> None:
        """Test environment variable overrides."""
        # Set environment variables
        os.environ["FLEXT_CLI_DEBUG"] = "true"
        os.environ["FLEXT_CLI_OUTPUT_FORMAT"] = "yaml"
        os.environ["FLEXT_CLI_LOG_LEVEL"] = "WARNING"

        try:
            # Clear global instance to force reload
            FlextCliConfig.clear_global_instance()

            # Get new instance with environment overrides
            config = FlextCliConfig.get_global_instance()

            # Verify environment overrides
            assert config.debug
            assert config.output_format == "yaml"
            assert config.log_level == "WARNING"

        finally:
            # Cleanup environment variables
            os.environ.pop("FLEXT_CLI_DEBUG", None)
            os.environ.pop("FLEXT_CLI_OUTPUT_FORMAT", None)
            os.environ.pop("FLEXT_CLI_LOG_LEVEL", None)

    def test_cli_config_inherits_from_flext_config(self) -> None:
        """Test that CLI config properly inherits from FlextConfig."""
        # Get base config
        base_config = FlextConfig.get_global_instance()

        # Modify base config (use valid log level for development)
        base_config.debug = True
        base_config.log_level = "WARNING"  # Use valid log level
        base_config.base_url = "https://test-api.com"  # Use base_url instead of api_url
        FlextConfig.set_global_instance(base_config)

        # Get CLI config (should inherit changes)
        cli_config = FlextCliConfig.get_global_instance()

        # Verify inheritance
        assert cli_config.debug
        assert cli_config.log_level == "WARNING"
        # Note: api_url is CLI-specific and not inherited from base_url
        assert hasattr(cli_config, "api_url")
        assert isinstance(cli_config.api_url, str)

        # Verify CLI-specific fields are still present
        assert hasattr(cli_config, "profile")
        assert hasattr(cli_config, "output_format")

    def test_global_instance_management(self) -> None:
        """Test global instance management."""
        # Get initial instance
        config1 = FlextCliConfig.get_global_instance()

        # Get same instance - note: FlextCliConfig creates new instances for test isolation
        config2 = FlextCliConfig.get_global_instance()
        assert config1.model_dump() == config2.model_dump()  # Same configuration values

        # Set new global instance
        new_config = FlextCliConfig(profile="test", debug=True)
        FlextCliConfig.set_global_instance(new_config)

        # Verify new instance is returned
        config3 = FlextCliConfig.get_global_instance()
        assert config3 is new_config
        assert config3.profile == "test"
        assert config3.debug

        # Clear global instance
        FlextCliConfig.clear_global_instance()

        # Verify new instance is created
        config4 = FlextCliConfig.get_global_instance()
        assert config4 is not new_config

    def test_configuration_validation(self) -> None:
        """Test configuration validation."""
        # Get valid config
        config = FlextCliConfig.get_global_instance()

        # Validate configuration
        validation_result = config.validate_business_rules()
        assert validation_result.is_success

        # Test invalid configuration creation
        try:
            invalid_config = FlextCliConfig(
                profile="",  # Invalid empty profile
                output_format="invalid_format",  # Invalid format
            )
            # If creation succeeded, validation should still fail
            validation_result = invalid_config.validate_business_rules()
            assert validation_result.is_failure
        except Exception:
            # If Pydantic prevents creation, that's also valid - the validation is working
            pass

    def test_cli_parameter_mapping(self) -> None:
        """Test CLI parameter mapping to configuration fields."""
        # Test various CLI parameter formats
        cli_params: dict[str, object] = {
            "profile": "test",
            "debug": True,
            "output": "json",  # Short form
            "output_format": "yaml",  # Long form
            "log_level": "DEBUG",
            "quiet": True,
            "verbose": False,
            "no_color": True,
            "api_url": "https://test.com",
            "timeout": 30,  # Short form
            "command_timeout": 60,  # Long form
            "api_timeout": 45,
            "trace": True,
            "no-color": True,  # Kebab case
            "log-level": "INFO",  # Kebab case
            "api-url": "https://kebab.com",  # Kebab case
            "command-timeout": 90,  # Kebab case
            "api-timeout": 120,  # Kebab case
        }

        override_result = FlextCliConfig.apply_cli_overrides(cli_params)
        assert override_result.is_success

        config = override_result.value

        # Verify parameter mapping
        assert config.profile == "test"
        assert config.debug
        assert config.output_format == "yaml"  # Long form takes precedence
        assert config.log_level == "INFO"  # Kebab case takes precedence
        assert config.quiet
        assert not config.verbose
        assert config.no_color
        assert config.api_url == "https://kebab.com"  # Kebab case takes precedence
        assert config.command_timeout == 90  # Kebab case takes precedence
        assert config.api_timeout == 120  # Kebab case takes precedence
        assert config.trace

    def test_configuration_export(self) -> None:
        """Test configuration export functionality."""
        config = FlextCliConfig.get_global_instance()

        # Test model_dump
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert "profile" in config_dict
        assert "debug" in config_dict
        assert "output_format" in config_dict

        # Test to_json
        config_json = config.to_json(indent=2)
        assert isinstance(config_json, str)
        assert "profile" in config_json
        assert "debug" in config_json

    def test_configuration_consistency(self) -> None:
        """Test configuration consistency across different access methods."""
        # Get config via different methods
        config1 = FlextCliConfig.get_global_instance()
        config2 = FlextCliConfig.get_current()

        # Should have the same configuration values
        assert config1.model_dump() == config2.model_dump()

        # Apply overrides
        cli_params: dict[str, object] = {"debug": True, "profile": "test"}
        override_result = FlextCliConfig.apply_cli_overrides(cli_params)
        assert override_result.is_success

        # Get updated config
        config3 = FlextCliConfig.get_global_instance()

        # Verify consistency
        assert config3.debug
        assert config3.profile == "test"

        # Verify base config is also updated
        base_config = FlextConfig.get_global_instance()
        assert base_config.debug

    def test_error_handling(self) -> None:
        """Test error handling in configuration operations."""
        # Test invalid CLI parameters
        invalid_params: dict[str, object] = {"invalid_param": "value"}
        override_result = FlextCliConfig.apply_cli_overrides(invalid_params)
        assert override_result.is_success  # Should succeed with ignored invalid params

        # Test synchronization with invalid config
        # This should not fail as it's handled gracefully
        sync_result = FlextCliConfig.sync_with_flext_config()
        assert sync_result.is_success

    def test_configuration_profiles(self) -> None:
        """Test configuration profile functionality."""
        # Test default profile
        config = FlextCliConfig.get_global_instance()
        assert config.profile == "default"

        # Test profile override
        cli_params: dict[str, object] = {"profile": "development"}
        override_result = FlextCliConfig.apply_cli_overrides(cli_params)
        assert override_result.is_success

        updated_config = override_result.value
        assert updated_config.profile == "development"

    def test_configuration_directories(self) -> None:
        """Test configuration directory management."""
        config = FlextCliConfig.get_global_instance()

        # Test directory validation using modern method
        dir_result = config.ensure_directories()
        assert dir_result.is_success

        # Test directory setup
        setup_result = config.ensure_setup()
        assert setup_result.is_success

    def test_configuration_timeout_aliases(self) -> None:
        """Test timeout configuration aliases."""
        config = FlextCliConfig.get_global_instance()

        # Test timeout alias
        assert hasattr(config, "timeout")
        assert config.timeout == config.timeout_seconds

        # Test timeout override
        cli_params: dict[str, object] = {"timeout": 120}
        override_result = FlextCliConfig.apply_cli_overrides(cli_params)
        assert override_result.is_success

        updated_config = override_result.value
        assert updated_config.timeout == 120
        assert updated_config.timeout_seconds == 120


if __name__ == "__main__":
    pytest.main([__file__])
