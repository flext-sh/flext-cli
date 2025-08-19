"""Tests for flext_cli.py to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from flext_cli.cli_types import OutputFormat
from flext_cli.flext_cli import (
    flext_cli_configure,
    flext_cli_create_command,
    flext_cli_create_context,
    flext_cli_create_session,
    flext_cli_execute_handler,
    flext_cli_export,
    flext_cli_format,
    flext_cli_get_commands,
    flext_cli_get_handlers,
    flext_cli_get_plugins,
    flext_cli_get_sessions,
    flext_cli_health,
    flext_cli_register_handler,
    flext_cli_register_plugin,
    flext_cli_render_with_context,
)
from flext_cli.models import FlextCliContext


class TestFlextCliExport:
    """Test flext_cli_export function."""

    @patch("flext_cli.flext_cli._api.flext_cli_export")
    def test_export_success(self, mock_api_export: MagicMock) -> None:
        """Test successful data export."""
        mock_api_export.return_value = True

        data = {"test": "data"}
        path = "/tmp/test.json"

        result = flext_cli_export(data, path, OutputFormat.JSON)

        assert result is True
        mock_api_export.assert_called_once_with(data, path, OutputFormat.JSON)

    @patch("flext_cli.flext_cli._api.flext_cli_export")
    def test_export_failure(self, mock_api_export: MagicMock) -> None:
        """Test failed data export."""
        mock_api_export.return_value = False

        data = {"test": "data"}
        path = Path("/invalid/path/test.json")

        result = flext_cli_export(data, path, OutputFormat.YAML)

        assert result is False
        mock_api_export.assert_called_once_with(data, path, OutputFormat.YAML)

    @patch("flext_cli.flext_cli._api.flext_cli_export")
    def test_export_default_format(self, mock_api_export: MagicMock) -> None:
        """Test export with default format."""
        mock_api_export.return_value = True

        data = [{"item": 1}, {"item": 2}]
        path = "output.json"

        result = flext_cli_export(data, path)  # Default format should be JSON

        assert result is True
        mock_api_export.assert_called_once_with(data, path, OutputFormat.JSON)


class TestFlextCliFormat:
    """Test flext_cli_format function."""

    @patch("flext_cli.flext_cli._api.flext_cli_format")
    def test_format_json(self, mock_api_format: MagicMock) -> None:
        """Test formatting data as JSON."""
        expected_result = '{"test": "formatted"}'
        mock_api_format.return_value = expected_result

        data = {"test": "data"}

        result = flext_cli_format(data, OutputFormat.JSON)

        assert result == expected_result
        mock_api_format.assert_called_once_with(data, OutputFormat.JSON)

    @patch("flext_cli.flext_cli._api.flext_cli_format")
    def test_format_yaml(self, mock_api_format: MagicMock) -> None:
        """Test formatting data as YAML."""
        expected_result = "test: formatted\n"
        mock_api_format.return_value = expected_result

        data = {"test": "formatted"}

        result = flext_cli_format(data, OutputFormat.YAML)

        assert result == expected_result
        mock_api_format.assert_called_once_with(data, OutputFormat.YAML)

    @patch("flext_cli.flext_cli._api.flext_cli_format")
    def test_format_default(self, mock_api_format: MagicMock) -> None:
        """Test formatting with default format."""
        expected_result = '{"default": "format"}'
        mock_api_format.return_value = expected_result

        data = {"default": "format"}

        result = flext_cli_format(data)  # Default should be JSON

        assert result == expected_result
        mock_api_format.assert_called_once_with(data, OutputFormat.JSON)


class TestFlextCliConfigure:
    """Test flext_cli_configure function."""

    @patch("flext_cli.flext_cli._api.flext_cli_configure")
    def test_configure_success(self, mock_api_configure: MagicMock) -> None:
        """Test successful configuration."""
        mock_api_configure.return_value = True

        config = {"debug": True, "output_format": "json"}

        result = flext_cli_configure(config)

        assert result is True
        mock_api_configure.assert_called_once_with(config)

    @patch("flext_cli.flext_cli._api.flext_cli_configure")
    def test_configure_failure(self, mock_api_configure: MagicMock) -> None:
        """Test failed configuration."""
        mock_api_configure.return_value = False

        config = {"invalid": "config"}

        result = flext_cli_configure(config)

        assert result is False
        mock_api_configure.assert_called_once_with(config)

    @patch("flext_cli.flext_cli._api.flext_cli_configure")
    def test_configure_empty_config(self, mock_api_configure: MagicMock) -> None:
        """Test configuration with empty config."""
        mock_api_configure.return_value = True

        config = {}

        result = flext_cli_configure(config)

        assert result is True
        mock_api_configure.assert_called_once_with(config)


class TestFlextCliHealth:
    """Test flext_cli_health function."""

    @patch("flext_cli.flext_cli._api.flext_cli_health")
    def test_health_check_success(self, mock_api_health: MagicMock) -> None:
        """Test successful health check."""
        expected_health = {
            "status": "healthy",
            "service": "FlextCliService",
            "timestamp": "2025-01-01T00:00:00Z"
        }
        mock_api_health.return_value = expected_health

        result = flext_cli_health()

        assert result == expected_health
        mock_api_health.assert_called_once()

    @patch("flext_cli.flext_cli._api.flext_cli_health")
    def test_health_check_detailed(self, mock_api_health: MagicMock) -> None:
        """Test health check with detailed information."""
        expected_health = {
            "status": "healthy",
            "handlers": 5,
            "plugins": 3,
            "sessions": 2,
            "configured": True
        }
        mock_api_health.return_value = expected_health

        result = flext_cli_health()

        assert result == expected_health
        assert result["handlers"] == 5
        assert result["plugins"] == 3
        assert result["configured"] is True


class TestFlextCliCreateContext:
    """Test flext_cli_create_context function."""

    @patch("flext_cli.flext_cli._api.flext_cli_create_context")
    def test_create_context_success(self, mock_api_create_context: MagicMock) -> None:
        """Test successful context creation."""
        expected_context = FlextCliContext()
        mock_api_create_context.return_value = expected_context

        config = {"debug": True}

        result = flext_cli_create_context(config)

        assert isinstance(result, FlextCliContext)
        mock_api_create_context.assert_called_once_with(config)

    @patch("flext_cli.flext_cli._api.flext_cli_create_context")
    def test_create_context_no_config(self, mock_api_create_context: MagicMock) -> None:
        """Test context creation without config."""
        expected_context = FlextCliContext()
        mock_api_create_context.return_value = expected_context

        result = flext_cli_create_context()

        assert isinstance(result, FlextCliContext)
        mock_api_create_context.assert_called_once_with(None)

    @patch("flext_cli.flext_cli._api.flext_cli_create_context")
    def test_create_context_type_error(self, mock_api_create_context: MagicMock) -> None:
        """Test context creation with non-FlextCliContext return."""
        # Mock API returns non-FlextCliContext object
        mock_api_create_context.return_value = {"not": "context"}

        result = flext_cli_create_context({"test": "config"})

        # Should return fallback FlextCliContext
        assert isinstance(result, FlextCliContext)
        mock_api_create_context.assert_called_once_with({"test": "config"})

    @patch("flext_cli.flext_cli._api.flext_cli_create_context")
    @patch("flext_cli.flext_cli.get_logger")
    def test_create_context_isinstance_exception(self, mock_get_logger: MagicMock, mock_api_create_context: MagicMock) -> None:
        """Test context creation when isinstance fails."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Mock a result that causes isinstance to raise TypeError
        mock_result = MagicMock()
        mock_api_create_context.return_value = mock_result

        # Patch isinstance to raise TypeError
        with patch("flext_cli.flext_cli.isinstance", side_effect=TypeError("Type error")):
            result = flext_cli_create_context({"config": "value"})

        # Should return fallback FlextCliContext and log warning
        assert isinstance(result, FlextCliContext)
        mock_logger.warning.assert_called_once_with("Type checking failed for FlextCliContext: Type error")


class TestFlextCliCreateCommand:
    """Test flext_cli_create_command function."""

    @patch("flext_cli.flext_cli._api.flext_cli_create_command")
    def test_create_command_success(self, mock_api_create: MagicMock) -> None:
        """Test successful command creation."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_api_create.return_value = mock_result

        result = flext_cli_create_command("test-command", "echo hello", timeout=30)

        assert result is True
        mock_api_create.assert_called_once_with("test-command", "echo hello", timeout=30)

    @patch("flext_cli.flext_cli._api.flext_cli_create_command")
    def test_create_command_failure(self, mock_api_create: MagicMock) -> None:
        """Test failed command creation."""
        mock_result = MagicMock()
        mock_result.success = False
        mock_api_create.return_value = mock_result

        result = flext_cli_create_command("failing-command", "invalid command")

        assert result is False
        mock_api_create.assert_called_once_with("failing-command", "invalid command")

    @patch("flext_cli.flext_cli._api.flext_cli_create_command")
    def test_create_command_no_success_attr(self, mock_api_create: MagicMock) -> None:
        """Test command creation when result has no success attribute."""
        mock_result = "not a result object"
        mock_api_create.return_value = mock_result

        result = flext_cli_create_command("test-command", "echo test")

        assert result is False
        mock_api_create.assert_called_once_with("test-command", "echo test")


class TestFlextCliCreateSession:
    """Test flext_cli_create_session function."""

    @patch("flext_cli.flext_cli._api.flext_cli_create_session")
    def test_create_session_success(self, mock_api_create_session: MagicMock) -> None:
        """Test successful session creation."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.unwrap.return_value = "Session created with ID session-123"
        mock_api_create_session.return_value = mock_result

        result = flext_cli_create_session("user-456")

        assert result == "Session created with ID session-123"
        mock_api_create_session.assert_called_once_with("user-456")

    @patch("flext_cli.flext_cli._api.flext_cli_create_session")
    def test_create_session_failure(self, mock_api_create_session: MagicMock) -> None:
        """Test failed session creation."""
        mock_result = MagicMock()
        mock_result.success = False
        mock_api_create_session.return_value = mock_result

        result = flext_cli_create_session("failing-user")

        assert result == ""
        mock_api_create_session.assert_called_once_with("failing-user")

    @patch("flext_cli.flext_cli._api.flext_cli_create_session")
    def test_create_session_no_user_id(self, mock_api_create_session: MagicMock) -> None:
        """Test session creation without user ID."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.unwrap.return_value = "Session created with auto-generated ID"
        mock_api_create_session.return_value = mock_result

        result = flext_cli_create_session()

        assert result == "Session created with auto-generated ID"
        mock_api_create_session.assert_called_once_with(None)

    @patch("flext_cli.flext_cli._api.flext_cli_create_session")
    def test_create_session_no_unwrap_method(self, mock_api_create_session: MagicMock) -> None:
        """Test session creation when result has no unwrap method."""
        mock_result = "not a proper result"
        mock_api_create_session.return_value = mock_result

        result = flext_cli_create_session("test-user")

        assert result == ""
        mock_api_create_session.assert_called_once_with("test-user")


class TestFlextCliRegisterHandler:
    """Test flext_cli_register_handler function."""

    @patch("flext_cli.flext_cli._api.flext_cli_register_handler")
    def test_register_handler_success(self, mock_api_register: MagicMock) -> None:
        """Test successful handler registration."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_api_register.return_value = mock_result

        handler = lambda x: x * 2

        result = flext_cli_register_handler("multiplier", handler)

        assert result is True
        mock_api_register.assert_called_once_with("multiplier", handler)

    @patch("flext_cli.flext_cli._api.flext_cli_register_handler")
    def test_register_handler_failure(self, mock_api_register: MagicMock) -> None:
        """Test failed handler registration."""
        mock_result = MagicMock()
        mock_result.success = False
        mock_api_register.return_value = mock_result

        result = flext_cli_register_handler("failing-handler", None)

        assert result is False
        mock_api_register.assert_called_once_with("failing-handler", None)

    @patch("flext_cli.flext_cli._api.flext_cli_register_handler")
    def test_register_handler_no_success_attr(self, mock_api_register: MagicMock) -> None:
        """Test handler registration when result has no success attribute."""
        mock_result = {"message": "registered"}
        mock_api_register.return_value = mock_result

        handler = MagicMock()

        result = flext_cli_register_handler("test-handler", handler)

        assert result is False
        mock_api_register.assert_called_once_with("test-handler", handler)


class TestFlextCliRegisterPlugin:
    """Test flext_cli_register_plugin function."""

    @patch("flext_cli.flext_cli._api.flext_cli_register_plugin")
    def test_register_plugin_success(self, mock_api_register: MagicMock) -> None:
        """Test successful plugin registration."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_api_register.return_value = mock_result

        plugin = MagicMock()

        result = flext_cli_register_plugin("test-plugin", plugin)

        assert result is True
        mock_api_register.assert_called_once_with("test-plugin", plugin)

    @patch("flext_cli.flext_cli._api.flext_cli_register_plugin")
    def test_register_plugin_failure(self, mock_api_register: MagicMock) -> None:
        """Test failed plugin registration."""
        mock_result = MagicMock()
        mock_result.success = False
        mock_api_register.return_value = mock_result

        result = flext_cli_register_plugin("failing-plugin", {})

        assert result is False
        mock_api_register.assert_called_once_with("failing-plugin", {})


class TestFlextCliExecuteHandler:
    """Test flext_cli_execute_handler function."""

    @patch("flext_cli.flext_cli._api.flext_cli_execute_handler")
    def test_execute_handler_success(self, mock_api_execute: MagicMock) -> None:
        """Test successful handler execution."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.unwrap.return_value = {"result": "executed"}
        mock_api_execute.return_value = mock_result

        result = flext_cli_execute_handler("test-handler", "arg1", "arg2", param="value")

        assert result == {"result": "executed"}
        mock_api_execute.assert_called_once_with("test-handler", "arg1", "arg2", param="value")

    @patch("flext_cli.flext_cli._api.flext_cli_execute_handler")
    def test_execute_handler_failure(self, mock_api_execute: MagicMock) -> None:
        """Test failed handler execution."""
        mock_result = MagicMock()
        mock_result.success = False
        mock_api_execute.return_value = mock_result

        result = flext_cli_execute_handler("failing-handler")

        assert result == {}
        mock_api_execute.assert_called_once_with("failing-handler")

    @patch("flext_cli.flext_cli._api.flext_cli_execute_handler")
    def test_execute_handler_no_unwrap(self, mock_api_execute: MagicMock) -> None:
        """Test handler execution when result has no unwrap method."""
        mock_result = "simple result"
        mock_api_execute.return_value = mock_result

        result = flext_cli_execute_handler("test-handler", 1, 2, 3)

        assert result == {}
        mock_api_execute.assert_called_once_with("test-handler", 1, 2, 3)


class TestFlextCliRenderWithContext:
    """Test flext_cli_render_with_context function."""

    @patch("flext_cli.flext_cli._api.flext_cli_render_with_context")
    def test_render_with_context_success(self, mock_api_render: MagicMock) -> None:
        """Test successful rendering with context."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.unwrap.return_value = "rendered output"
        mock_api_render.return_value = mock_result

        data = {"key": "value"}
        context = {"format": "json"}

        result = flext_cli_render_with_context(data, context)

        assert result == "rendered output"
        mock_api_render.assert_called_once_with(data, context)

    @patch("flext_cli.flext_cli._api.flext_cli_render_with_context")
    def test_render_with_context_no_context(self, mock_api_render: MagicMock) -> None:
        """Test rendering without context."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.unwrap.return_value = "default rendering"
        mock_api_render.return_value = mock_result

        data = ["item1", "item2"]

        result = flext_cli_render_with_context(data)

        assert result == "default rendering"
        mock_api_render.assert_called_once_with(data, None)

    @patch("flext_cli.flext_cli._api.flext_cli_render_with_context")
    def test_render_with_context_failure(self, mock_api_render: MagicMock) -> None:
        """Test failed rendering."""
        mock_result = MagicMock()
        mock_result.success = False
        mock_api_render.return_value = mock_result

        result = flext_cli_render_with_context({"data": "test"}, {"context": "fail"})

        assert result == ""
        mock_api_render.assert_called_once_with({"data": "test"}, {"context": "fail"})


class TestFlextCliGetters:
    """Test flext_cli_get_* functions."""

    @patch("flext_cli.flext_cli._api.flext_cli_get_commands")
    def test_get_commands(self, mock_api_get_commands: MagicMock) -> None:
        """Test getting all commands."""
        expected_commands = {
            "cmd1": {"name": "cmd1", "line": "echo 1"},
            "cmd2": {"name": "cmd2", "line": "echo 2"}
        }
        mock_api_get_commands.return_value = expected_commands

        result = flext_cli_get_commands()

        assert result == expected_commands
        mock_api_get_commands.assert_called_once()

    @patch("flext_cli.flext_cli._api.flext_cli_get_sessions")
    def test_get_sessions(self, mock_api_get_sessions: MagicMock) -> None:
        """Test getting all sessions."""
        expected_sessions = {
            "session1": {"id": "session1", "user": "user1"},
            "session2": {"id": "session2", "user": "user2"}
        }
        mock_api_get_sessions.return_value = expected_sessions

        result = flext_cli_get_sessions()

        assert result == expected_sessions
        mock_api_get_sessions.assert_called_once()

    @patch("flext_cli.flext_cli._api.flext_cli_get_plugins")
    def test_get_plugins(self, mock_api_get_plugins: MagicMock) -> None:
        """Test getting all plugins."""
        expected_plugins = {
            "plugin1": {"name": "plugin1", "version": "1.0"},
            "plugin2": {"name": "plugin2", "version": "2.0"}
        }
        mock_api_get_plugins.return_value = expected_plugins

        result = flext_cli_get_plugins()

        assert result == expected_plugins
        mock_api_get_plugins.assert_called_once()

    @patch("flext_cli.flext_cli._api.flext_cli_get_handlers")
    def test_get_handlers(self, mock_api_get_handlers: MagicMock) -> None:
        """Test getting all handlers."""
        expected_handlers = {
            "handler1": lambda x: x + 1,
            "handler2": lambda x: x * 2
        }
        mock_api_get_handlers.return_value = expected_handlers

        result = flext_cli_get_handlers()

        assert result == expected_handlers
        mock_api_get_handlers.assert_called_once()

    @patch("flext_cli.flext_cli._api.flext_cli_get_commands")
    def test_get_commands_empty(self, mock_api_get_commands: MagicMock) -> None:
        """Test getting commands when none exist."""
        mock_api_get_commands.return_value = {}

        result = flext_cli_get_commands()

        assert result == {}
        mock_api_get_commands.assert_called_once()
