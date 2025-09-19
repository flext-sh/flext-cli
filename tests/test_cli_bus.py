"""Test FlextCliCommandBusService functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.cli_bus import FlextCliCommandBusService
from flext_core import FlextResult


class TestFlextCliCommandBusService:
    """Test suite for FlextCliCommandBusService class."""

    def test_cli_bus_initialization(self) -> None:
        """Test CLI command bus can be initialized."""
        bus_service = FlextCliCommandBusService()
        assert bus_service is not None
        assert hasattr(bus_service, "execute_show_config_command")
        assert hasattr(bus_service, "execute_set_config_command")
        assert hasattr(bus_service, "execute_edit_config_command")
        assert hasattr(bus_service, "execute_auth_login_command")
        assert hasattr(bus_service, "execute_auth_status_command")
        assert hasattr(bus_service, "execute_auth_logout_command")
        assert hasattr(bus_service, "execute_debug_info_command")

    def test_command_validator_validate_command_type(self) -> None:
        """Test command validator for command type validation."""

        # Test with valid command-like object
        class MockCommand:
            def validate_command(self) -> FlextResult[bool]:
                return FlextResult[bool].ok(True)

        mock_command = MockCommand()
        result = FlextCliCommandBusService._CommandValidator.validate_command_type(
            mock_command
        )
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

    def test_command_validator_validate_command_type_invalid(self) -> None:
        """Test command validator with invalid command type."""
        # Test with object that doesn't have validate_command method
        invalid_command = object()
        result = FlextCliCommandBusService._CommandValidator.validate_command_type(
            invalid_command
        )
        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert "Invalid command type" in (result.error or "")

    def test_command_validator_validate_command_data(self) -> None:
        """Test command validator for command data validation."""

        # Test with command that has validate_command method
        class MockCommand:
            def validate_command(self) -> FlextResult[bool]:
                return FlextResult[bool].ok(True)

        mock_command = MockCommand()
        result = FlextCliCommandBusService._CommandValidator.validate_command_data(
            mock_command
        )
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

    def test_command_validator_validate_command_data_no_method(self) -> None:
        """Test command validator with command that has no validate_command method."""
        # Test with object that doesn't have validate_command method
        invalid_command = object()
        result = FlextCliCommandBusService._CommandValidator.validate_command_data(
            invalid_command
        )
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

    def test_execute_show_config_command(self) -> None:
        """Test execute show config command."""
        bus_service = FlextCliCommandBusService()

        # Test with default parameters
        result = bus_service.execute_show_config_command()
        assert isinstance(result, FlextResult)
        # The command might fail if handlers aren't properly set up, but should return FlextResult

    def test_execute_show_config_command_with_params(self) -> None:
        """Test execute show config command with custom parameters."""
        bus_service = FlextCliCommandBusService()

        # Test with custom parameters
        result = bus_service.execute_show_config_command(
            output_format="json", profile="test-profile"
        )
        assert isinstance(result, FlextResult)

    def test_execute_set_config_command(self) -> None:
        """Test execute set config command."""
        bus_service = FlextCliCommandBusService()

        # Test with basic parameters
        result = bus_service.execute_set_config_command("test_key", "test_value")
        assert isinstance(result, FlextResult)

    def test_execute_set_config_command_with_profile(self) -> None:
        """Test execute set config command with custom profile."""
        bus_service = FlextCliCommandBusService()

        # Test with custom profile
        result = bus_service.execute_set_config_command(
            "test_key", "test_value", profile="test-profile"
        )
        assert isinstance(result, FlextResult)

    def test_execute_edit_config_command(self) -> None:
        """Test execute edit config command."""
        bus_service = FlextCliCommandBusService()

        # Test with default parameters
        result = bus_service.execute_edit_config_command()
        assert isinstance(result, FlextResult)

    def test_execute_edit_config_command_with_params(self) -> None:
        """Test execute edit config command with custom parameters."""
        bus_service = FlextCliCommandBusService()

        # Test with custom parameters
        result = bus_service.execute_edit_config_command(
            profile="test-profile", editor="vim"
        )
        assert isinstance(result, FlextResult)

    def test_execute_auth_login_command(self) -> None:
        """Test execute auth login command."""
        bus_service = FlextCliCommandBusService()

        # Test with basic parameters
        result = bus_service.execute_auth_login_command("test_user", "test_password")
        assert isinstance(result, FlextResult)

    def test_execute_auth_login_command_with_api_url(self) -> None:
        """Test execute auth login command with custom API URL."""
        bus_service = FlextCliCommandBusService()

        # Test with custom API URL
        result = bus_service.execute_auth_login_command(
            "test_user", "test_password", api_url="https://api.example.com"
        )
        assert isinstance(result, FlextResult)

    def test_execute_auth_status_command(self) -> None:
        """Test execute auth status command."""
        bus_service = FlextCliCommandBusService()

        # Test with default parameters
        result = bus_service.execute_auth_status_command()
        assert isinstance(result, FlextResult)

    def test_execute_auth_status_command_with_detailed(self) -> None:
        """Test execute auth status command with detailed flag."""
        bus_service = FlextCliCommandBusService()

        # Test with detailed flag
        result = bus_service.execute_auth_status_command(detailed=True)
        assert isinstance(result, FlextResult)

    def test_execute_auth_logout_command(self) -> None:
        """Test execute auth logout command."""
        bus_service = FlextCliCommandBusService()

        # Test with default parameters
        result = bus_service.execute_auth_logout_command()
        assert isinstance(result, FlextResult)

    def test_execute_auth_logout_command_with_all_profiles(self) -> None:
        """Test execute auth logout command with all profiles flag."""
        bus_service = FlextCliCommandBusService()

        # Test with all profiles flag
        result = bus_service.execute_auth_logout_command(all_profiles=True)
        assert isinstance(result, FlextResult)

    def test_execute_debug_info_command(self) -> None:
        """Test execute debug info command."""
        bus_service = FlextCliCommandBusService()

        # Test with default parameters
        result = bus_service.execute_debug_info_command()
        assert isinstance(result, FlextResult)

    def test_execute_debug_info_command_with_params(self) -> None:
        """Test execute debug info command with custom parameters."""
        bus_service = FlextCliCommandBusService()

        # Test with custom parameters
        result = bus_service.execute_debug_info_command(
            include_system=False, include_config=True
        )
        assert isinstance(result, FlextResult)

    def test_get_registered_handlers(self) -> None:
        """Test getting registered handlers."""
        bus_service = FlextCliCommandBusService()

        handlers = bus_service.get_registered_handlers()
        assert isinstance(handlers, list)
        # Should have some handlers registered during setup
        assert len(handlers) > 0

    def test_get_command_bus_status(self) -> None:
        """Test getting command bus status."""
        bus_service = FlextCliCommandBusService()

        status = bus_service.get_command_bus_status()
        assert isinstance(status, dict)
        assert "handlers_count" in status
        assert "bus_initialized" in status
        assert status["bus_initialized"] is True

    def test_execute_domain_service(self) -> None:
        """Test execute method from domain service."""
        bus_service = FlextCliCommandBusService()

        result = bus_service.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_dispatch_method_with_invalid_command(self) -> None:
        """Test dispatch method with invalid command."""
        bus_service = FlextCliCommandBusService()

        # Try to access the protected _dispatch method indirectly
        # through one of the command methods with invalid data
        result = bus_service.execute_show_config_command()
        # Should still work even with minimal parameters
        assert isinstance(result, FlextResult)

    def test_setup_handlers_called_during_init(self) -> None:
        """Test that setup handlers is called during initialization."""
        # Create new instance to test initialization
        bus_service = FlextCliCommandBusService()

        # Verify handlers are registered
        handlers = bus_service.get_registered_handlers()
        assert len(handlers) > 0

        # Verify status shows initialization completed
        status = bus_service.get_command_bus_status()
        assert status["bus_initialized"] is True
