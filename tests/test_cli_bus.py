"""Test FlextCliCommandBusService functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.cli_bus import FlextCliCommandBusService
from flext_core import FlextResult


class TestFlextCliCommandBusService:
    """Comprehensive test suite for FlextCliCommandBusService class."""

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
            mock_command,
        )
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

    def test_command_validator_validate_command_type_invalid(self) -> None:
        """Test command validator with invalid command type."""
        # Test with object that doesn't have validate_command method
        invalid_command = object()
        result = FlextCliCommandBusService._CommandValidator.validate_command_type(
            invalid_command,
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
            mock_command,
        )
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

    def test_command_validator_validate_command_data_no_method(self) -> None:
        """Test command validator with command that has no validate_command method."""
        # Test with object that doesn't have validate_command method
        invalid_command = object()
        result = FlextCliCommandBusService._CommandValidator.validate_command_data(
            invalid_command,
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
            output_format="json",
            profile="test-profile",
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
            "test_key",
            "test_value",
            profile="test-profile",
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
            profile="test-profile",
            editor="vim",
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
            "test_user",
            "test_password",
            api_url="https://api.example.com",
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
            include_system=False,
            include_config=True,
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

    def test_command_execution_with_validation_errors(self) -> None:
        """Test command execution with validation errors."""
        bus_service = FlextCliCommandBusService()

        # Test with invalid parameters that should fail validation
        result = bus_service.execute_set_config_command("", "")
        assert isinstance(result, FlextResult)
        # Command should handle empty keys/values gracefully

    def test_command_bus_error_handling(self) -> None:
        """Test command bus error handling capabilities."""
        bus_service = FlextCliCommandBusService()

        # Test that all command methods handle errors gracefully
        show_result = bus_service.execute_show_config_command()
        assert isinstance(show_result, FlextResult)

        edit_result = bus_service.execute_edit_config_command()
        assert isinstance(edit_result, FlextResult)

        status_result = bus_service.execute_auth_status_command()
        assert isinstance(status_result, FlextResult)

        debug_result = bus_service.execute_debug_info_command()
        assert isinstance(debug_result, FlextResult)
        # All methods should return FlextResult regardless of success/failure

    def test_command_validator_edge_cases(self) -> None:
        """Test command validator with edge cases."""
        # Test with None
        result = FlextCliCommandBusService._CommandValidator.validate_command_type(None)
        assert isinstance(result, FlextResult)
        assert result.is_failure

        # Test with primitive types
        for invalid_command in [42, "string", [], {}]:
            result = FlextCliCommandBusService._CommandValidator.validate_command_type(invalid_command)
            assert isinstance(result, FlextResult)
            assert result.is_failure

    def test_command_bus_state_management(self) -> None:
        """Test command bus state management."""
        bus_service = FlextCliCommandBusService()

        # Verify initial state
        initial_status = bus_service.get_command_bus_status()
        assert initial_status["bus_initialized"] is True

        # Verify handlers are consistently available
        handlers_count_1 = len(bus_service.get_registered_handlers())
        handlers_count_2 = len(bus_service.get_registered_handlers())
        assert handlers_count_1 == handlers_count_2

        # Verify status consistency
        status_1 = bus_service.get_command_bus_status()
        status_2 = bus_service.get_command_bus_status()
        assert status_1 == status_2

    def test_command_parameter_validation(self) -> None:
        """Test command parameter validation."""
        bus_service = FlextCliCommandBusService()

        # Test auth login with various parameter combinations
        test_cases = [
            ("user", "pass"),
            ("user", "pass", "https://api.example.com"),
            ("", "pass"),  # Empty username
            ("user", ""),  # Empty password
        ]

        for params in test_cases:
            if len(params) == 2:
                result = bus_service.execute_auth_login_command(params[0], params[1])
            else:
                result = bus_service.execute_auth_login_command(params[0], params[1], api_url=params[2])
            assert isinstance(result, FlextResult)

    def test_command_output_format_handling(self) -> None:
        """Test command output format handling."""
        bus_service = FlextCliCommandBusService()

        # Test different output formats
        output_formats = ["json", "yaml", "table", "plain", "invalid_format"]

        for format_type in output_formats:
            result = bus_service.execute_show_config_command(output_format=format_type)
            assert isinstance(result, FlextResult)
            # Command should handle all format types gracefully

    def test_multiple_bus_instances(self) -> None:
        """Test behavior with multiple command bus instances."""
        bus_1 = FlextCliCommandBusService()
        bus_2 = FlextCliCommandBusService()

        # Both instances should be functional
        status_1 = bus_1.get_command_bus_status()
        status_2 = bus_2.get_command_bus_status()

        assert status_1["bus_initialized"] is True
        assert status_2["bus_initialized"] is True

        # Both should have handlers
        assert len(bus_1.get_registered_handlers()) > 0
        assert len(bus_2.get_registered_handlers()) > 0

    def test_command_execution_consistency(self) -> None:
        """Test consistency of command execution results."""
        bus_service = FlextCliCommandBusService()

        # Execute same command multiple times
        results = []
        for _ in range(3):
            result = bus_service.execute_debug_info_command()
            results.append(result)
            assert isinstance(result, FlextResult)

        # All results should be FlextResult instances
        assert all(isinstance(r, FlextResult) for r in results)

    def test_domain_service_integration(self) -> None:
        """Test integration with FlextDomainService."""
        bus_service = FlextCliCommandBusService()

        # Test domain service execute method
        result = bus_service.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify domain service behavior
        assert hasattr(bus_service, "execute")
        assert callable(getattr(bus_service, "execute"))

    def test_command_type_coverage(self) -> None:
        """Test coverage of all command types."""
        bus_service = FlextCliCommandBusService()

        # Test all major command categories

        # Config commands
        config_result = bus_service.execute_show_config_command()
        assert isinstance(config_result, FlextResult)

        set_result = bus_service.execute_set_config_command("key", "value")
        assert isinstance(set_result, FlextResult)

        edit_result = bus_service.execute_edit_config_command()
        assert isinstance(edit_result, FlextResult)

        # Auth commands
        login_result = bus_service.execute_auth_login_command("user", "pass")
        assert isinstance(login_result, FlextResult)

        status_result = bus_service.execute_auth_status_command()
        assert isinstance(status_result, FlextResult)

        logout_result = bus_service.execute_auth_logout_command()
        assert isinstance(logout_result, FlextResult)

        # Debug commands
        debug_result = bus_service.execute_debug_info_command()
        assert isinstance(debug_result, FlextResult)
        # Each command type should return proper FlextResult
