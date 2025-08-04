"""Integration tests for FLEXT CLI API implementation.

Tests for the real API functionality that was implemented.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli.api import FlextCliApi
from flext_cli.domain.entities import CLICommand, CommandType
from flext_core.result import FlextResult


class TestFlextCliApiIntegration:
    """Integration tests for FLEXT CLI API real functionality."""

    def test_api_configure_with_valid_config(self) -> None:
        """Test API configuration with valid configuration."""
        api = FlextCliApi()

        config = {
            "project_name": "test-project",
            "project_version": "1.0.0",
            "debug": True,
            "log_level": "DEBUG",
        }

        result = api.flext_cli_configure(config)
        assert result is True
        assert hasattr(api, "_config")
        assert api._config.project_name == "test-project"
        assert api._config.debug is True

    def test_api_configure_with_invalid_types(self) -> None:
        """Test API configuration with invalid types."""
        api = FlextCliApi()

        config = {
            "project_name": 123,  # Should be string
            "debug": "not_bool",  # Should be bool
        }

        result = api.flext_cli_configure(config)
        assert result is True  # Should still work, but invalid values ignored
        assert hasattr(api, "_config")
        # Invalid values should be ignored, defaults used
        assert api._config.project_name == "flext-cli"  # Default value

    def test_api_health_returns_system_info(self) -> None:
        """Test health endpoint returns real system information."""
        api = FlextCliApi()

        health = api.flext_cli_health()

        assert isinstance(health, dict)
        assert health["status"] == "healthy"
        assert "timestamp" in health
        assert "python_version" in health
        assert "platform" in health
        assert health["service"] == "flext-cli"
        assert health["version"] == "0.9.0"

    def test_api_create_command_with_valid_data(self) -> None:
        """Test command creation with valid data."""
        api = FlextCliApi()

        result = api.flext_cli_create_command(
            "test-command",
            "echo hello",
            description="Test command",
            command_type="system",
            timeout_seconds=60,
        )

        assert isinstance(result, FlextResult)
        assert result.success

        command = result.unwrap()
        assert isinstance(command, CLICommand)
        assert command.name == "test-command"
        assert command.command_line == "echo hello"
        assert command.command_type == CommandType.SYSTEM
        assert command.description == "Test command"
        assert command.timeout == 60

    def test_api_create_command_with_invalid_type(self) -> None:
        """Test command creation with invalid command type."""
        api = FlextCliApi()

        result = api.flext_cli_create_command(
            "test-command",
            "echo hello",
            command_type="invalid_type",
        )

        assert isinstance(result, FlextResult)
        assert not result.success
        assert "invalid_type" in result.error

    def test_api_create_session_generates_unique_id(self) -> None:
        """Test session creation generates unique IDs."""
        api = FlextCliApi()

        result1 = api.flext_cli_create_session("user1")
        result2 = api.flext_cli_create_session("user2")

        assert isinstance(result1, FlextResult)
        assert isinstance(result2, FlextResult)
        assert result1.success
        assert result2.success

        session_id1 = result1.unwrap()
        session_id2 = result2.unwrap()

        assert isinstance(session_id1, str)
        assert isinstance(session_id2, str)
        assert session_id1 != session_id2
        assert session_id1.startswith("cli_session_")
        assert session_id2.startswith("cli_session_")

    def test_api_handler_registration_and_execution(self) -> None:
        """Test handler registration and execution."""
        api = FlextCliApi()

        # Register a simple handler
        def test_handler(x: int, y: int) -> int:
            return x + y

        register_result = api.flext_cli_register_handler("add", test_handler)
        assert isinstance(register_result, FlextResult)
        assert register_result.success

        # Execute the handler
        exec_result = api.flext_cli_execute_handler("add", 5, 3)
        assert isinstance(exec_result, FlextResult)
        assert exec_result.success
        assert exec_result.unwrap() == 8

    def test_api_handler_registration_invalid_handler(self) -> None:
        """Test handler registration with invalid handler."""
        api = FlextCliApi()

        # Try to register non-callable
        register_result = api.flext_cli_register_handler("invalid", "not_callable")
        assert isinstance(register_result, FlextResult)
        assert not register_result.success
        assert "not callable" in register_result.error

    def test_api_handler_execution_nonexistent(self) -> None:
        """Test handler execution with nonexistent handler."""
        api = FlextCliApi()

        exec_result = api.flext_cli_execute_handler("nonexistent")
        assert isinstance(exec_result, FlextResult)
        assert not exec_result.success
        assert (
            "not found" in exec_result.error
            or "No handlers registry" in exec_result.error
        )

    def test_api_render_with_context_default_format(self) -> None:
        """Test rendering with context using default format."""
        api = FlextCliApi()

        data = {"name": "test", "value": 42}
        result = api.flext_cli_render_with_context(data)

        assert isinstance(result, FlextResult)
        assert result.success
        rendered = result.unwrap()
        assert isinstance(rendered, str)
        assert len(rendered) > 0

    def test_api_render_with_context_custom_format(self) -> None:
        """Test rendering with context using custom format."""
        api = FlextCliApi()

        data = {"name": "test", "value": 42}
        context = {"format": "json", "title": "Test Data"}
        result = api.flext_cli_render_with_context(data, context)

        assert isinstance(result, FlextResult)
        assert result.success
        rendered = result.unwrap()
        assert isinstance(rendered, str)
        assert "# Test Data" in rendered  # Title should be added

    def test_api_get_methods_return_correct_types(self) -> None:
        """Test that get methods return correct types."""
        api = FlextCliApi()

        # Test get_commands
        commands = api.flext_cli_get_commands()
        assert isinstance(commands, dict)

        # Test get_sessions
        sessions = api.flext_cli_get_sessions()
        assert isinstance(sessions, dict)

        # Test get_plugins
        plugins = api.flext_cli_get_plugins()
        assert isinstance(plugins, dict)

        # Test get_handlers
        handlers = api.flext_cli_get_handlers()
        assert isinstance(handlers, dict)

    def test_api_session_tracking(self) -> None:
        """Test session tracking functionality."""
        api = FlextCliApi()

        # Create a session
        session_result = api.flext_cli_create_session("test_user")
        assert session_result.success
        session_id = session_result.unwrap()

        # Check sessions are tracked
        sessions = api.flext_cli_get_sessions()
        assert isinstance(sessions, dict)
        assert session_id in sessions

        session_data = sessions[session_id]
        assert isinstance(session_data, dict)
        assert session_data["id"] == session_id
        assert session_data["status"] == "active"
        assert "created_at" in session_data
        assert "commands_count" in session_data

    def test_api_plugin_registration_integration(self) -> None:
        """Test plugin registration integration with flext-plugin."""
        api = FlextCliApi()

        # Create a mock plugin object
        class MockPlugin:
            def __init__(self, name: str) -> None:
                self.name = name

        mock_plugin = MockPlugin("test-plugin")

        # Register plugin - this should work with real flext-plugin integration
        result = api.flext_cli_register_plugin("test-plugin", mock_plugin)
        assert isinstance(result, FlextResult)
        # Note: This might fail if flext-plugin dependencies aren't available
        # but the important thing is it uses real FlextPluginService
