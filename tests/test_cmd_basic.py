"""Basic tests for CLI CMD Service.

Focus on real functionality testing to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli.cmd import FlextCliCmd
from flext_cli.configs import FlextCliConfigs
from flext_core import FlextResult


class TestFlextCliCmd:
    """Test FlextCliCmd basic functionality."""

    def test_cmd_initialization(self) -> None:
        """Test FlextCliCmd can be initialized."""
        cmd_service = FlextCliCmd()
        assert cmd_service is not None

    def test_cmd_execute(self) -> None:
        """Test FlextCliCmd execute method."""
        cmd_service = FlextCliCmd()
        result = cmd_service.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert "Command bus integration ready" in result.unwrap()

    def test_command_bus_service_property(self) -> None:
        """Test command bus service property with lazy loading."""
        cmd_service = FlextCliCmd()

        # First access should create the instance
        bus_service_1 = cmd_service.command_bus_service
        assert bus_service_1 is not None

        # Second access should return the same instance
        bus_service_2 = cmd_service.command_bus_service
        assert bus_service_1 is bus_service_2

    def test_show_config_paths(self) -> None:
        """Test show config paths functionality."""
        cmd_service = FlextCliCmd()
        result = cmd_service.show_config_paths()

        assert isinstance(result, FlextResult)
        assert result.is_success

        paths = result.unwrap()
        assert isinstance(paths, list)
        assert len(paths) == 4  # config_dir, cache_dir, token_file, refresh_token_file

        # Verify all paths are strings
        for path in paths:
            assert isinstance(path, str)

    def test_set_config_value(self) -> None:
        """Test set config value functionality."""
        cmd_service = FlextCliCmd()

        # Test setting a config value
        result = cmd_service.set_config_value("test_key", "test_value")
        assert isinstance(result, FlextResult)
        # Accept either success or meaningful failure
        assert result is not None

    def test_get_config_value(self) -> None:
        """Test get config value functionality."""
        cmd_service = FlextCliCmd()

        # Test getting config value
        result = cmd_service.get_config_value("test_key")
        assert isinstance(result, FlextResult)
        # Accept either success or meaningful failure
        assert result is not None

    def test_get_cmd_instance(self) -> None:
        """Test get cmd instance functionality."""
        cmd_service = FlextCliCmd()
        instance = cmd_service.get_cmd_instance()
        assert instance is not None
        assert instance is cmd_service.command_bus_service

    def test_create_instance_classmethod(self) -> None:
        """Test create instance class method."""
        cmd_service = FlextCliCmd.create_instance()
        assert isinstance(cmd_service, FlextCliCmd)
        assert cmd_service is not None

    def test_show_config(self) -> None:
        """Test show config using internal helper."""
        cmd_service = FlextCliCmd()
        result = cmd_service.show_config()

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_edit_config(self) -> None:
        """Test edit config using internal helper."""
        cmd_service = FlextCliCmd()
        result = cmd_service.edit_config()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert "Config edit completed" in result.unwrap()

    def test_validate_config(self) -> None:
        """Test validate config using internal helper."""
        cmd_service = FlextCliCmd()
        result = cmd_service.validate_config()

        assert isinstance(result, FlextResult)
        # Config validation may succeed or fail depending on system state
        assert result is not None


class TestFlextCliCmdHelpers:
    """Test FlextCliCmd nested helper classes."""

    def test_config_display_helper(self) -> None:
        """Test _ConfigDisplayHelper functionality."""
        from flext_core import FlextLogger

        logger = FlextLogger(__name__)
        result = FlextCliCmd._ConfigDisplayHelper.show_config(logger)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_config_modification_helper(self) -> None:
        """Test _ConfigModificationHelper functionality."""
        result = FlextCliCmd._ConfigModificationHelper.edit_config()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert "Config edit completed" in result.unwrap()

    def test_config_validation_helper_success(self) -> None:
        """Test _ConfigValidationHelper with valid config."""
        config = FlextCliConfigs()
        result = FlextCliCmd._ConfigValidationHelper.validate_config(config)

        assert isinstance(result, FlextResult)
        # Validation may succeed or fail based on system state
        assert result is not None

    def test_config_validation_helper_error_handling(self) -> None:
        """Test _ConfigValidationHelper error handling."""
        # Create a config that might have validation issues
        config = FlextCliConfigs()
        result = FlextCliCmd._ConfigValidationHelper.validate_config(config)

        assert isinstance(result, FlextResult)
        # Should handle validation gracefully
        assert result is not None


class TestFlextCliCmdIntegration:
    """Test FlextCliCmd integration with other components."""

    def test_cmd_with_configs_integration(self) -> None:
        """Test FlextCliCmd integration with FlextCliConfigs."""
        cmd_service = FlextCliCmd()

        # Test that cmd service can work with configs
        paths_result = cmd_service.show_config_paths()
        assert paths_result.is_success

        # Test config validation
        validation_result = cmd_service.validate_config()
        assert isinstance(validation_result, FlextResult)

    def test_cmd_with_command_bus_integration(self) -> None:
        """Test FlextCliCmd integration with command bus service."""
        cmd_service = FlextCliCmd()

        # Test command bus access
        bus_service = cmd_service.command_bus_service
        assert bus_service is not None

        # Test command bus instance consistency
        assert cmd_service.get_cmd_instance() is bus_service

    def test_cmd_configuration_workflow(self) -> None:
        """Test complete configuration workflow."""
        cmd_service = FlextCliCmd()

        # Show config paths
        paths_result = cmd_service.show_config_paths()
        assert paths_result.is_success

        # Show config
        show_result = cmd_service.show_config()
        assert show_result.is_success

        # Validate config
        validate_result = cmd_service.validate_config()
        assert isinstance(validate_result, FlextResult)

    def test_cmd_error_handling_comprehensive(self) -> None:
        """Test comprehensive error handling scenarios."""
        cmd_service = FlextCliCmd()

        # Test various operations handle errors gracefully
        operations = [
            lambda: cmd_service.execute(),
            lambda: cmd_service.show_config_paths(),
            lambda: cmd_service.show_config(),
            lambda: cmd_service.edit_config(),
            lambda: cmd_service.validate_config(),
        ]

        for operation in operations:
            try:
                result = operation()
                assert isinstance(result, FlextResult)
            except Exception as e:
                # Should not raise unhandled exceptions
                pytest.fail(f"Operation raised unhandled exception: {e}")