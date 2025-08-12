"""Tests for flext_cli module.

Tests for the public interface functions in flext_cli module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import inspect
import tempfile
from enum import StrEnum
from unittest.mock import MagicMock, patch

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3


class MockOutputFormat(StrEnum):
    """Mock OutputFormat for testing."""

    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    TABLE = "table"
    PLAIN = "plain"


mock_api = MagicMock()
mock_plugin = MagicMock()

with patch.dict(
    "sys.modules",
    {
        "flext_cli.api": MagicMock(FlextCliApi=mock_api),
        "flext_cli.domain.entities": MagicMock(FlextCliPlugin=mock_plugin),
        "flext_cli.types": MagicMock(
            TCliData=str,
            TCliFormat=str,
            TCliPath=str,
            OutputFormat=MockOutputFormat,
        ),
    },
):
    from flext_cli import flext_cli

# Now we can use the mocked FlextCliPlugin
FlextCliPlugin = mock_plugin

# Add to flext_cli module for test access
flext_cli.FlextCliPlugin = mock_plugin
flext_cli.FlextCliApi = mock_api
flext_cli.TCliData = str
flext_cli.TCliFormat = str
flext_cli.TCliPath = str


class TestFlextCliExport:
    """Test flext_cli_export function."""

    def test_flext_cli_export_success(self) -> None:
        """Test successful data export."""
        with patch.object(
            flext_cli._api, "flext_cli_export", return_value=True
        ) as mock_export:
            data = {"key": "value"}
            with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
                path = tmp.name
            format_type = "json"

            result = flext_cli.flext_cli_export(data, path, format_type)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_export.assert_called_once_with(data, path, format_type)

    def test_flext_cli_export_failure(self) -> None:
        """Test failed data export."""
        with patch.object(
            flext_cli._api, "flext_cli_export", return_value=False
        ) as mock_export:
            data = {"key": "value"}
            path = "/invalid/path.json"

            result = flext_cli.flext_cli_export(data, path)

            if result:
                raise AssertionError(f"Expected False, got {result}")
            mock_export.assert_called_once()

    def test_flext_cli_export_default_format(self) -> None:
        """Test export with default format."""
        with (
            patch.object(
                flext_cli._api, "flext_cli_export", return_value=True
            ) as mock_export,
            tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file,
        ):
            data = {"test": "data"}
            path = temp_file.name

            result = flext_cli.flext_cli_export(data, path)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_export.assert_called_once_with(data, path, "json")

    def test_flext_cli_export_different_formats(self) -> None:
        """Test export with different formats."""
        formats = ["json", "yaml", "csv", "table", "plain"]

        for fmt in formats:
            with (
                patch.object(
                    flext_cli._api, "flext_cli_export", return_value=True
                ) as mock_export,
                tempfile.NamedTemporaryFile(
                    suffix=f".{fmt}", delete=False
                ) as temp_file,
            ):
                data = {"format": fmt}
                path = temp_file.name

                result = flext_cli.flext_cli_export(data, path, fmt)

                if not (result):
                    raise AssertionError(f"Expected True, got {result}")
                mock_export.assert_called_once_with(data, path, fmt)

    def test_flext_cli_export_complex_data(self) -> None:
        """Test export with complex data structures."""
        with (
            patch.object(
                flext_cli._api, "flext_cli_export", return_value=True
            ) as mock_export,
            tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file,
        ):
            complex_data = {
                "nested": {"deep": {"value": 42}},
                "list": [1, 2, 3],
                "boolean": True,
                "null": None,
            }
            path = temp_file.name

            result = flext_cli.flext_cli_export(complex_data, path)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_export.assert_called_once_with(complex_data, path, "json")


class TestFlextCliFormat:
    """Test flext_cli_format function."""

    def test_flext_cli_format_success(self) -> None:
        """Test successful data formatting."""
        with patch.object(
            flext_cli._api, "flext_cli_format", return_value='{"key": "value"}'
        ) as mock_format:
            data = {"key": "value"}
            format_type = "json"

            result = flext_cli.flext_cli_format(data, format_type)

            if result != '{"key": "value"}':
                raise AssertionError(f"Expected {'{"key": "value"}'}, got {result}")
            mock_format.assert_called_once_with(data, format_type)

    def test_flext_cli_format_default_format(self) -> None:
        """Test formatting with default format."""
        with patch.object(
            flext_cli._api, "flext_cli_format", return_value='{"test": "data"}'
        ) as mock_format:
            data = {"test": "data"}

            result = flext_cli.flext_cli_format(data)

            if result != '{"test": "data"}':
                raise AssertionError(f"Expected {'{"test": "data"}'}, got {result}")
            mock_format.assert_called_once_with(data, "json")

    def test_flext_cli_format_different_formats(self) -> None:
        """Test formatting with different formats."""
        formats = ["json", "yaml", "csv", "table", "plain"]
        expected_outputs = [
            '{"key": "value"}',
            "key: value\n",
            "key,value\ntest,data\n",
            "| key | value |\n|-----|-------|\n| test | data |",
            "key: value",
        ]

        for fmt, expected in zip(formats, expected_outputs, strict=False):
            with patch.object(
                flext_cli._api, "flext_cli_format", return_value=expected
            ) as mock_format:
                data = {"key": "value"}

                result = flext_cli.flext_cli_format(data, fmt)

                if result != expected:
                    raise AssertionError(f"Expected {expected}, got {result}")
                mock_format.assert_called_once_with(data, fmt)

    def test_flext_cli_format_empty_data(self) -> None:
        """Test formatting empty data."""
        with patch.object(
            flext_cli._api, "flext_cli_format", return_value="{}"
        ) as mock_format:
            data: dict[str, object] = {}

            result = flext_cli.flext_cli_format(data)

            if result != "{}":
                raise AssertionError(f"Expected {'{}'}, got {result}")
            mock_format.assert_called_once_with(data, "json")

    def test_flext_cli_format_list_data(self) -> None:
        """Test formatting list data."""
        with patch.object(
            flext_cli._api, "flext_cli_format", return_value="[1, 2, 3]"
        ) as mock_format:
            data = [1, 2, 3]

            result = flext_cli.flext_cli_format(data)

            if result != "[1, 2, 3]":
                raise AssertionError(f"Expected {'[1, 2, 3]'}, got {result}")
            mock_format.assert_called_once_with(data, "json")


class TestFlextCliConfigure:
    """Test flext_cli_configure function."""

    def test_flext_cli_configure_success(self) -> None:
        """Test successful configuration."""
        with patch.object(
            flext_cli._api, "flext_cli_configure", return_value=True
        ) as mock_configure:
            config = {"setting": "value", "debug": True}

            result = flext_cli.flext_cli_configure(config)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_configure.assert_called_once_with(config)

    def test_flext_cli_configure_failure(self) -> None:
        """Test failed configuration."""
        with patch.object(
            flext_cli._api, "flext_cli_configure", return_value=False
        ) as mock_configure:
            config = {"invalid": "config"}

            result = flext_cli.flext_cli_configure(config)

            if result:
                raise AssertionError(f"Expected False, got {result}")
            mock_configure.assert_called_once_with(config)

    def test_flext_cli_configure_empty_config(self) -> None:
        """Test configuration with empty config."""
        with patch.object(
            flext_cli._api, "flext_cli_configure", return_value=True
        ) as mock_configure:
            config = {}

            result = flext_cli.flext_cli_configure(config)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_configure.assert_called_once_with(config)

    def test_flext_cli_configure_complex_config(self) -> None:
        """Test configuration with complex configuration."""
        with patch.object(
            flext_cli._api, "flext_cli_configure", return_value=True
        ) as mock_configure:
            config = {
                "database": {"url": "sqlite:///test.db", "pool_size": 10},
                "logging": {"level": "DEBUG", "format": "json"},
                "features": ["auth", "metrics", "cache"],
            }

            result = flext_cli.flext_cli_configure(config)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_configure.assert_called_once_with(config)


class TestFlextCliHealth:
    """Test flext_cli_health function."""

    def test_flext_cli_health_success(self) -> None:
        """Test successful health check."""
        expected_health = {"status": "healthy", "version": "0.9.0", "uptime": 3600}

        with patch.object(
            flext_cli._api, "flext_cli_health", return_value=expected_health
        ) as mock_health:
            result = flext_cli.flext_cli_health()

            if result != expected_health:
                raise AssertionError(f"Expected {expected_health}, got {result}")
            mock_health.assert_called_once()

    def test_flext_cli_health_unhealthy(self) -> None:
        """Test unhealthy status."""
        expected_health = {
            "status": "unhealthy",
            "errors": ["database_connection_failed"],
        }

        with patch.object(
            flext_cli._api, "flext_cli_health", return_value=expected_health
        ) as mock_health:
            result = flext_cli.flext_cli_health()

            if result != expected_health:
                raise AssertionError(f"Expected {expected_health}, got {result}")
            assert result["status"] == "unhealthy"
            mock_health.assert_called_once()

    def test_flext_cli_health_detailed_status(self) -> None:
        """Test detailed health status."""
        expected_health = {
            "status": "healthy",
            "services": {
                "database": {"status": "up", "response_time": 15},
                "cache": {"status": "up", "response_time": 5},
                "auth": {"status": "degraded", "response_time": 100},
            },
            "metadata": {"checked_at": "2025-01-01T00:00:00Z"},
        }

        with patch.object(
            flext_cli._api, "flext_cli_health", return_value=expected_health
        ) as mock_health:
            result = flext_cli.flext_cli_health()

            if result != expected_health:
                raise AssertionError(f"Expected {expected_health}, got {result}")
            if "services" not in result:
                raise AssertionError(f"Expected {'services'} in {result}")
            if len(result["services"]) != 3:
                raise AssertionError(f"Expected {3}, got {len(result['services'])}")
            mock_health.assert_called_once()


class TestFlextCliCreateContext:
    """Test flext_cli_create_context function."""

    def test_flext_cli_create_context_with_config(self) -> None:
        """Test creating context with configuration."""
        config = {"user": "test_user", "profile": "development"}
        expected_context = MagicMock()

        # Test that it properly handles API response and creates context
        with patch.object(
            flext_cli._api, "flext_cli_create_context", return_value=expected_context
        ) as mock_create:
            result = flext_cli.flext_cli_create_context(config)

            # Should return a FlextCliContext instance (via fallback since mock isn't FlextCliContext)
            if not hasattr(
                result, "session_id"
            ):  # FlextCliContext has session_id attribute
                raise AssertionError(
                    f"Expected FlextCliContext instance, got {type(result)}"
                )
            mock_create.assert_called_once_with(config)

    def test_flext_cli_create_context_without_config(self) -> None:
        """Test creating context without configuration."""
        expected_context = MagicMock()

        # Test that it properly handles API response and creates context
        with patch.object(
            flext_cli._api, "flext_cli_create_context", return_value=expected_context
        ) as mock_create:
            result = flext_cli.flext_cli_create_context()

            # Should return a FlextCliContext instance (via fallback since mock isn't FlextCliContext)
            if not hasattr(
                result, "session_id"
            ):  # FlextCliContext has session_id attribute
                raise AssertionError(
                    f"Expected FlextCliContext instance, got {type(result)}"
                )
            mock_create.assert_called_once_with(None)

    def test_flext_cli_create_context_none_config(self) -> None:
        """Test creating context with None config."""
        expected_context = MagicMock()

        # Test that it properly handles API response and creates context
        with patch.object(
            flext_cli._api, "flext_cli_create_context", return_value=expected_context
        ) as mock_create:
            result = flext_cli.flext_cli_create_context(None)

            # Should return a FlextCliContext instance (via fallback since mock isn't FlextCliContext)
            if not hasattr(
                result, "session_id"
            ):  # FlextCliContext has session_id attribute
                raise AssertionError(
                    f"Expected FlextCliContext instance, got {type(result)}"
                )
            mock_create.assert_called_once_with(None)

    def test_flext_cli_create_context_return_type(self) -> None:
        """Test context creation return type."""
        config = {"environment": "test"}

        with patch.object(flext_cli._api, "flext_cli_create_context") as mock_create:
            # Test that it always returns FlextCliContext regardless of API return value
            for return_value in [{"context": "dict"}, "string_context", 42, [1, 2, 3]]:
                mock_create.return_value = return_value

                result = flext_cli.flext_cli_create_context(config)

                # Should always return a FlextCliContext instance (via fallback)
                if not hasattr(
                    result, "session_id"
                ):  # FlextCliContext has session_id attribute
                    raise AssertionError(
                        f"Expected FlextCliContext instance, got {type(result)}"
                    )


class TestFlextCliCreateCommand:
    """Test flext_cli_create_command function."""

    def test_flext_cli_create_command_success(self) -> None:
        """Test successful command creation."""
        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.success = True

        with patch.object(
            flext_cli._api, "flext_cli_create_command", return_value=mock_result
        ) as mock_create:
            name = "test_command"
            command_line = "echo hello"

            result = flext_cli.flext_cli_create_command(name, command_line)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_create.assert_called_once_with(name, command_line)

    def test_flext_cli_create_command_with_options(self) -> None:
        """Test command creation with options."""
        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.success = True

        with patch.object(
            flext_cli._api, "flext_cli_create_command", return_value=mock_result
        ) as mock_create:
            name = "complex_command"
            command_line = "python script.py"
            options = {"timeout": 30, "async": True, "env": {"PATH": "/usr/bin"}}

            result = flext_cli.flext_cli_create_command(name, command_line, **options)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_create.assert_called_once_with(name, command_line, **options)

    def test_flext_cli_create_command_failure(self) -> None:
        """Test failed command creation."""
        with patch.object(
            flext_cli._api, "flext_cli_create_command", return_value=False
        ) as mock_create:
            name = "invalid_command"
            command_line = ""

            result = flext_cli.flext_cli_create_command(name, command_line)

            if result:
                raise AssertionError(f"Expected False, got {result}")
            mock_create.assert_called_once_with(name, command_line)

    def test_flext_cli_create_command_various_options(self) -> None:
        """Test command creation with various option types."""
        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.success = True

        with patch.object(
            flext_cli._api, "flext_cli_create_command", return_value=mock_result
        ) as mock_create:
            name = "test_cmd"
            command_line = "test"

            # Test different option combinations
            with tempfile.TemporaryDirectory() as temp_dir:
                test_cases = [
                    {"retries": 3},
                    {"working_dir": temp_dir, "shell": True},
                    {"env": {"VAR": "value"}, "capture_output": False},
                    {"timeout": 60, "retries": 2, "async": True},
                ]

                for options in test_cases:
                    result = flext_cli.flext_cli_create_command(
                        name, command_line, **options
                    )
                    if not (result):
                        raise AssertionError(f"Expected True, got {result}")
                    mock_create.assert_called_with(name, command_line, **options)


class TestFlextCliCreateSession:
    """Test flext_cli_create_session function."""

    def test_flext_cli_create_session_with_user_id(self) -> None:
        """Test session creation with user ID."""
        # Mock to return FlextResult
        expected_result = "Session created: session_123"
        mock_result = MagicMock()
        mock_result.unwrap.return_value = expected_result
        mock_result.success = True

        with patch.object(
            flext_cli._api,
            "flext_cli_create_session",
            return_value=mock_result,
        ) as mock_create:
            user_id = "user_456"

            result = flext_cli.flext_cli_create_session(user_id)

            if result != expected_result:
                raise AssertionError(f"Expected {expected_result}, got {result}")
            mock_create.assert_called_once_with(user_id)

    def test_flext_cli_create_session_without_user_id(self) -> None:
        """Test session creation without user ID."""
        # Mock to return FlextResult
        expected_result = "Session created: anonymous_789"
        mock_result = MagicMock()
        mock_result.unwrap.return_value = expected_result
        mock_result.success = True

        with patch.object(
            flext_cli._api,
            "flext_cli_create_session",
            return_value=mock_result,
        ) as mock_create:
            result = flext_cli.flext_cli_create_session()

            if result != expected_result:
                raise AssertionError(f"Expected {expected_result}, got {result}")
            mock_create.assert_called_once_with(None)

    def test_flext_cli_create_session_none_user_id(self) -> None:
        """Test session creation with None user ID."""
        # Mock to return FlextResult
        expected_result = "Session created: session_none"
        mock_result = MagicMock()
        mock_result.unwrap.return_value = expected_result
        mock_result.success = True

        with patch.object(
            flext_cli._api,
            "flext_cli_create_session",
            return_value=mock_result,
        ) as mock_create:
            result = flext_cli.flext_cli_create_session(None)

            if result != expected_result:
                raise AssertionError(f"Expected {expected_result}, got {result}")
            mock_create.assert_called_once_with(None)

    def test_flext_cli_create_session_different_responses(self) -> None:
        """Test session creation with different response types."""
        responses = [
            "Session created successfully",
            "Error: Unable to create session",
            "session_id_12345",
            "",
        ]

        for response in responses:
            # Mock to return FlextResult
            mock_result = MagicMock()
            mock_result.unwrap.return_value = response
            mock_result.success = True

            with patch.object(
                flext_cli._api, "flext_cli_create_session", return_value=mock_result
            ) as mock_create:
                result = flext_cli.flext_cli_create_session("test_user")

                if result != response:
                    raise AssertionError(f"Expected {response}, got {result}")
                mock_create.assert_called_once_with("test_user")


class TestFlextCliRegisterHandler:
    """Test flext_cli_register_handler function."""

    def test_flext_cli_register_handler_success(self) -> None:
        """Test successful handler registration."""

        def test_handler() -> str:
            return "test result"

        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.success = True

        with patch.object(
            flext_cli._api, "flext_cli_register_handler", return_value=mock_result
        ) as mock_register:
            name = "test_handler"

            result = flext_cli.flext_cli_register_handler(name, test_handler)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_register.assert_called_once_with(name, test_handler)

    def test_flext_cli_register_handler_failure(self) -> None:
        """Test failed handler registration."""
        with patch.object(
            flext_cli._api, "flext_cli_register_handler", return_value=False
        ) as mock_register:
            name = "invalid_handler"
            handler = None

            result = flext_cli.flext_cli_register_handler(name, handler)

            if result:
                raise AssertionError(f"Expected False, got {result}")
            mock_register.assert_called_once_with(name, handler)

    def test_flext_cli_register_handler_callable_types(self) -> None:
        """Test registering different types of callable handlers."""
        handlers = [
            lambda x: x * 2,  # lambda
            str.upper,  # method
            len,  # builtin function
            MagicMock(),  # mock object
        ]

        for handler in handlers:
            # Import FlextResult for proper mock
            from flext_core import FlextResult

            with patch.object(
                flext_cli._api,
                "flext_cli_register_handler",
                return_value=FlextResult.ok(None),
            ) as mock_register:
                name = f"handler_{id(handler)}"

                result = flext_cli.flext_cli_register_handler(name, handler)

                if not (result):
                    raise AssertionError(f"Expected True, got {result}")
                mock_register.assert_called_once_with(name, handler)

    def test_flext_cli_register_handler_class_instance(self) -> None:
        """Test registering class instance as handler."""

        class TestHandler:
            def __call__(self) -> str:
                return "called"

            def process(self) -> str:
                return "processed"

        handler_instance = TestHandler()

        # Import FlextResult for proper mock
        from flext_core import FlextResult

        with patch.object(
            flext_cli._api,
            "flext_cli_register_handler",
            return_value=FlextResult.ok(None),
        ) as mock_register:
            name = "class_handler"

            result = flext_cli.flext_cli_register_handler(name, handler_instance)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_register.assert_called_once_with(name, handler_instance)


class TestFlextCliRegisterPlugin:
    """Test flext_cli_register_plugin function."""

    def test_flext_cli_register_plugin_success(self) -> None:
        """Test successful plugin registration."""
        plugin = MagicMock()

        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.success = True

        with patch.object(
            flext_cli._api, "flext_cli_register_plugin", return_value=mock_result
        ) as mock_register:
            name = "test_plugin"

            result = flext_cli.flext_cli_register_plugin(name, plugin)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_register.assert_called_once_with(name, plugin)

    def test_flext_cli_register_plugin_failure(self) -> None:
        """Test failed plugin registration."""
        plugin = MagicMock()

        with patch.object(
            flext_cli._api, "flext_cli_register_plugin", return_value=False
        ) as mock_register:
            name = "invalid_plugin"

            result = flext_cli.flext_cli_register_plugin(name, plugin)

            if result:
                raise AssertionError(f"Expected False, got {result}")
            mock_register.assert_called_once_with(name, plugin)

    def test_flext_cli_register_plugin_with_real_plugin(self) -> None:
        """Test registering with plugin-like object."""
        # Create a mock that behaves like FlextCliPlugin
        plugin = MagicMock()
        plugin.name = "test_plugin"
        plugin.version = "0.9.0"
        plugin.description = "Test plugin"

        # Import FlextResult for proper mock
        from flext_core import FlextResult

        with patch.object(
            flext_cli._api,
            "flext_cli_register_plugin",
            return_value=FlextResult.ok(None),
        ) as mock_register:
            name = "real_plugin"

            result = flext_cli.flext_cli_register_plugin(name, plugin)

            if not (result):
                raise AssertionError(f"Expected True, got {result}")
            mock_register.assert_called_once_with(name, plugin)

    def test_flext_cli_register_plugin_none_plugin(self) -> None:
        """Test registering None as plugin."""
        with patch.object(
            flext_cli._api, "flext_cli_register_plugin", return_value=False
        ) as mock_register:
            name = "none_plugin"
            plugin = None

            result = flext_cli.flext_cli_register_plugin(name, plugin)

            if result:
                raise AssertionError(f"Expected False, got {result}")
            mock_register.assert_called_once_with(name, plugin)


class TestFlextCliExecuteHandler:
    """Test flext_cli_execute_handler function."""

    def test_flext_cli_execute_handler_success(self) -> None:
        """Test successful handler execution."""
        expected_result = {"status": "success", "data": "test_data"}

        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.unwrap.return_value = expected_result
        mock_result.success = True

        with patch.object(
            flext_cli._api, "flext_cli_execute_handler", return_value=mock_result
        ) as mock_execute:
            name = "test_handler"

            result = flext_cli.flext_cli_execute_handler(name)

            if result != expected_result:
                raise AssertionError(f"Expected {expected_result}, got {result}")
            mock_execute.assert_called_once_with(name)

    def test_flext_cli_execute_handler_with_args(self) -> None:
        """Test handler execution with positional arguments."""
        expected_result = "processed: arg1, arg2"

        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.unwrap.return_value = expected_result
        mock_result.success = True

        with patch.object(
            flext_cli._api, "flext_cli_execute_handler", return_value=mock_result
        ) as mock_execute:
            name = "args_handler"
            args = ("arg1", "arg2")

            result = flext_cli.flext_cli_execute_handler(name, *args)

            if result != expected_result:
                raise AssertionError(f"Expected {expected_result}, got {result}")
            mock_execute.assert_called_once_with(name, *args)

    def test_flext_cli_execute_handler_with_kwargs(self) -> None:
        """Test handler execution with keyword arguments."""
        expected_result = {"processed": True, "key1": "value1", "key2": "value2"}

        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.unwrap.return_value = expected_result
        mock_result.success = True

        with patch.object(
            flext_cli._api, "flext_cli_execute_handler", return_value=mock_result
        ) as mock_execute:
            name = "kwargs_handler"
            kwargs = {"key1": "value1", "key2": "value2"}

            result = flext_cli.flext_cli_execute_handler(name, **kwargs)

            if result != expected_result:
                raise AssertionError(f"Expected {expected_result}, got {result}")
            mock_execute.assert_called_once_with(name, **kwargs)

    def test_flext_cli_execute_handler_with_args_and_kwargs(self) -> None:
        """Test handler execution with both args and kwargs."""
        expected_result = "mixed_result"

        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.unwrap.return_value = expected_result
        mock_result.success = True

        with patch.object(
            flext_cli._api, "flext_cli_execute_handler", return_value=mock_result
        ) as mock_execute:
            name = "mixed_handler"
            args = ("pos1", "pos2")
            kwargs = {"kw1": "val1", "kw2": "val2"}

            result = flext_cli.flext_cli_execute_handler(name, *args, **kwargs)

            if result != expected_result:
                raise AssertionError(f"Expected {expected_result}, got {result}")
            mock_execute.assert_called_once_with(name, *args, **kwargs)

    def test_flext_cli_execute_handler_error_result(self) -> None:
        """Test handler execution returning error."""
        error_result = {
            "error": "Handler execution failed",
            "details": "Something went wrong",
        }

        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.unwrap.return_value = error_result
        mock_result.success = True

        with patch.object(
            flext_cli._api, "flext_cli_execute_handler", return_value=mock_result
        ) as mock_execute:
            name = "error_handler"

            result = flext_cli.flext_cli_execute_handler(name)

            if result != error_result:
                raise AssertionError(f"Expected {error_result}, got {result}")
            if "error" not in result:
                raise AssertionError(f"Expected {'error'} in {result}")
            mock_execute.assert_called_once_with(name)

    def test_flext_cli_execute_handler_different_return_types(self) -> None:
        """Test handler execution with different return types."""
        return_values = [
            "string_result",
            42,
            [1, 2, 3],
            {"dict": "result"},
            None,
            True,
        ]

        for return_value in return_values:
            # Mock to return FlextResult
            mock_result = MagicMock()
            mock_result.unwrap.return_value = return_value
            mock_result.success = True

            with patch.object(
                flext_cli._api, "flext_cli_execute_handler", return_value=mock_result
            ) as mock_execute:
                name = "type_test_handler"

                result = flext_cli.flext_cli_execute_handler(name)

                if result != return_value:
                    raise AssertionError(f"Expected {return_value}, got {result}")
                mock_execute.assert_called_once_with(name)


class TestFlextCliRenderWithContext:
    """Test flext_cli_render_with_context function."""

    def test_flext_cli_render_with_context_with_context(self) -> None:
        """Test rendering with context."""
        data = {"message": "Hello, {{user}}!"}
        context = {"user": "Alice"}
        expected_result = "Hello, Alice!"

        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.unwrap.return_value = expected_result
        mock_result.success = True

        with patch.object(
            flext_cli._api,
            "flext_cli_render_with_context",
            return_value=mock_result,
        ) as mock_render:
            result = flext_cli.flext_cli_render_with_context(data, context)

            if result != expected_result:
                raise AssertionError(f"Expected {expected_result}, got {result}")
            mock_render.assert_called_once_with(data, context)

    def test_flext_cli_render_with_context_without_context(self) -> None:
        """Test rendering without context."""
        data = "Simple text without templates"
        expected_result = "Simple text without templates"

        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.unwrap.return_value = expected_result
        mock_result.success = True

        with patch.object(
            flext_cli._api,
            "flext_cli_render_with_context",
            return_value=mock_result,
        ) as mock_render:
            result = flext_cli.flext_cli_render_with_context(data)

            if result != expected_result:
                raise AssertionError(f"Expected {expected_result}, got {result}")
            mock_render.assert_called_once_with(data, None)

    def test_flext_cli_render_with_context_none_context(self) -> None:
        """Test rendering with None context."""
        data = {"template": "data"}
        expected_result = "rendered_data"

        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.unwrap.return_value = expected_result
        mock_result.success = True

        with patch.object(
            flext_cli._api,
            "flext_cli_render_with_context",
            return_value=mock_result,
        ) as mock_render:
            result = flext_cli.flext_cli_render_with_context(data, None)

            if result != expected_result:
                raise AssertionError(f"Expected {expected_result}, got {result}")
            mock_render.assert_called_once_with(data, None)

    def test_flext_cli_render_with_context_complex_data(self) -> None:
        """Test rendering with complex data and context."""
        data = {
            "title": "{{title}}",
            "items": ["{{item1}}", "{{item2}}"],
            "meta": {"author": "{{author}}", "date": "{{date}}"},
        }
        context = {
            "title": "Test Report",
            "item1": "First Item",
            "item2": "Second Item",
            "author": "Test User",
            "date": "2025-01-01",
        }
        expected_result = "Complex rendered template"

        # Mock to return FlextResult
        mock_result = MagicMock()
        mock_result.unwrap.return_value = expected_result
        mock_result.success = True

        with patch.object(
            flext_cli._api,
            "flext_cli_render_with_context",
            return_value=mock_result,
        ) as mock_render:
            result = flext_cli.flext_cli_render_with_context(data, context)

            if result != expected_result:
                raise AssertionError(f"Expected {expected_result}, got {result}")
            mock_render.assert_called_once_with(data, context)

    def test_flext_cli_render_with_context_different_data_types(self) -> None:
        """Test rendering with different data types."""
        data_types = [
            "string template",
            ["list", "of", "items"],
            42,
            {"nested": {"template": "value"}},
            None,
        ]

        for data in data_types:
            expected = f"rendered_{type(data).__name__}"
            context = {"test": "value"}

            # Mock to return FlextResult
            mock_result = MagicMock()
            mock_result.unwrap.return_value = expected
            mock_result.success = True

            with patch.object(
                flext_cli._api,
                "flext_cli_render_with_context",
                return_value=mock_result,
            ) as mock_render:
                result = flext_cli.flext_cli_render_with_context(data, context)

                if result != expected:
                    raise AssertionError(f"Expected {expected}, got {result}")
                mock_render.assert_called_once_with(data, context)


class TestFlextCliGetCommands:
    """Test flext_cli_get_commands function."""

    def test_flext_cli_get_commands_success(self) -> None:
        """Test successful commands retrieval."""
        expected_commands = {
            "cmd1": {"name": "cmd1", "status": "active"},
            "cmd2": {"name": "cmd2", "status": "inactive"},
        }

        with patch.object(
            flext_cli._api, "flext_cli_get_commands", return_value=expected_commands
        ) as mock_get:
            result = flext_cli.flext_cli_get_commands()

            if result != expected_commands:
                raise AssertionError(f"Expected {expected_commands}, got {result}")
            assert len(result) == EXPECTED_BULK_SIZE
            mock_get.assert_called_once()

    def test_flext_cli_get_commands_empty(self) -> None:
        """Test commands retrieval with empty result."""
        expected_commands = {}

        with patch.object(
            flext_cli._api, "flext_cli_get_commands", return_value=expected_commands
        ) as mock_get:
            result = flext_cli.flext_cli_get_commands()

            if result != expected_commands:
                raise AssertionError(f"Expected {expected_commands}, got {result}")
            assert len(result) == 0
            mock_get.assert_called_once()

    def test_flext_cli_get_commands_detailed(self) -> None:
        """Test commands retrieval with detailed information."""
        expected_commands = {
            "deploy": {
                "name": "deploy",
                "description": "Deploy application",
                "status": "active",
                "last_run": "2025-01-01T12:00:00Z",
                "success_count": 10,
                "error_count": 2,
            },
            "backup": {
                "name": "backup",
                "description": "Backup database",
                "status": "scheduled",
                "next_run": "2025-01-02T02:00:00Z",
                "success_count": 50,
                "error_count": 0,
            },
        }

        with patch.object(
            flext_cli._api, "flext_cli_get_commands", return_value=expected_commands
        ) as mock_get:
            result = flext_cli.flext_cli_get_commands()

            if result != expected_commands:
                raise AssertionError(f"Expected {expected_commands}, got {result}")
            if "deploy" not in result:
                raise AssertionError(f"Expected {'deploy'} in {result}")
            assert "backup" in result
            if result["deploy"]["success_count"] != 10:
                raise AssertionError(
                    f"Expected {10}, got {result['deploy']['success_count']}"
                )
            mock_get.assert_called_once()


class TestFlextCliGetSessions:
    """Test flext_cli_get_sessions function."""

    def test_flext_cli_get_sessions_success(self) -> None:
        """Test successful sessions retrieval."""
        expected_sessions = {
            "session1": {"id": "session1", "user": "alice", "active": True},
            "session2": {"id": "session2", "user": "bob", "active": False},
        }

        with patch.object(
            flext_cli._api, "flext_cli_get_sessions", return_value=expected_sessions
        ) as mock_get:
            result = flext_cli.flext_cli_get_sessions()

            if result != expected_sessions:
                raise AssertionError(f"Expected {expected_sessions}, got {result}")
            assert len(result) == EXPECTED_BULK_SIZE
            mock_get.assert_called_once()

    def test_flext_cli_get_sessions_empty(self) -> None:
        """Test sessions retrieval with empty result."""
        expected_sessions = {}

        with patch.object(
            flext_cli._api, "flext_cli_get_sessions", return_value=expected_sessions
        ) as mock_get:
            result = flext_cli.flext_cli_get_sessions()

            if result != expected_sessions:
                raise AssertionError(f"Expected {expected_sessions}, got {result}")
            assert len(result) == 0
            mock_get.assert_called_once()

    def test_flext_cli_get_sessions_detailed(self) -> None:
        """Test sessions retrieval with detailed information."""
        expected_sessions = {
            "sess_123": {
                "id": "sess_123",
                "user_id": "user_456",
                "created_at": "2025-01-01T10:00:00Z",
                "last_activity": "2025-01-01T15:30:00Z",
                "active": True,
                "commands_executed": 25,
                "environment": "production",
            },
            "sess_789": {
                "id": "sess_789",
                "user_id": "user_101",
                "created_at": "2025-01-01T09:00:00Z",
                "last_activity": "2025-01-01T11:00:00Z",
                "active": False,
                "commands_executed": 5,
                "environment": "development",
            },
        }

        with patch.object(
            flext_cli._api, "flext_cli_get_sessions", return_value=expected_sessions
        ) as mock_get:
            result = flext_cli.flext_cli_get_sessions()

            if result != expected_sessions:
                raise AssertionError(f"Expected {expected_sessions}, got {result}")
            if not (result["sess_123"]["active"]):
                raise AssertionError(
                    f"Expected True, got {result['sess_123']['active']}"
                )
            if result["sess_789"]["active"]:
                raise AssertionError(
                    f"Expected False, got {result['sess_789']['active']}"
                )
            assert result["sess_123"]["commands_executed"] == 25
            mock_get.assert_called_once()


class TestFlextCliGetPlugins:
    """Test flext_cli_get_plugins function."""

    def test_flext_cli_get_plugins_success(self) -> None:
        """Test successful plugins retrieval."""
        expected_plugins = {
            "auth_plugin": {"name": "auth_plugin", "version": "0.9.0", "enabled": True},
            "metrics_plugin": {
                "name": "metrics_plugin",
                "version": "2.1.0",
                "enabled": False,
            },
        }

        with patch.object(
            flext_cli._api, "flext_cli_get_plugins", return_value=expected_plugins
        ) as mock_get:
            result = flext_cli.flext_cli_get_plugins()

            if result != expected_plugins:
                raise AssertionError(f"Expected {expected_plugins}, got {result}")
            assert len(result) == EXPECTED_BULK_SIZE
            mock_get.assert_called_once()

    def test_flext_cli_get_plugins_empty(self) -> None:
        """Test plugins retrieval with empty result."""
        expected_plugins = {}

        with patch.object(
            flext_cli._api, "flext_cli_get_plugins", return_value=expected_plugins
        ) as mock_get:
            result = flext_cli.flext_cli_get_plugins()

            if result != expected_plugins:
                raise AssertionError(f"Expected {expected_plugins}, got {result}")
            assert len(result) == 0
            mock_get.assert_called_once()

    def test_flext_cli_get_plugins_detailed(self) -> None:
        """Test plugins retrieval with detailed information."""
        expected_plugins = {
            "database_plugin": {
                "name": "database_plugin",
                "version": "3.2.1",
                "description": "Database connectivity plugin",
                "author": "FLEXT Team",
                "enabled": True,
                "dependencies": ["sqlalchemy", "psycopg2"],
                "config": {"host": "localhost", "port": 5432},
            },
            "notification_plugin": {
                "name": "notification_plugin",
                "version": "1.5.0",
                "description": "Notification system plugin",
                "author": "External Contributor",
                "enabled": False,
                "dependencies": ["requests", "smtplib"],
                "config": {"smtp_host": "smtp.example.com"},
            },
        }

        with patch.object(
            flext_cli._api, "flext_cli_get_plugins", return_value=expected_plugins
        ) as mock_get:
            result = flext_cli.flext_cli_get_plugins()

            if result != expected_plugins:
                raise AssertionError(f"Expected {expected_plugins}, got {result}")
            if not (result["database_plugin"]["enabled"]):
                raise AssertionError(
                    f"Expected True, got {result['database_plugin']['enabled']}"
                )
            if result["notification_plugin"]["enabled"]:
                raise AssertionError(
                    f"Expected False, got {result['notification_plugin']['enabled']}"
                )
            assert len(result["database_plugin"]["dependencies"]) == EXPECTED_BULK_SIZE
            mock_get.assert_called_once()


class TestFlextCliGetHandlers:
    """Test flext_cli_get_handlers function."""

    def test_flext_cli_get_handlers_success(self) -> None:
        """Test successful handlers retrieval."""
        expected_handlers = {
            "data_handler": {
                "name": "data_handler",
                "type": "function",
                "active": True,
            },
            "file_handler": {"name": "file_handler", "type": "class", "active": True},
        }

        with patch.object(
            flext_cli._api, "flext_cli_get_handlers", return_value=expected_handlers
        ) as mock_get:
            result = flext_cli.flext_cli_get_handlers()

            if result != expected_handlers:
                raise AssertionError(f"Expected {expected_handlers}, got {result}")
            assert len(result) == EXPECTED_BULK_SIZE
            mock_get.assert_called_once()

    def test_flext_cli_get_handlers_empty(self) -> None:
        """Test handlers retrieval with empty result."""
        expected_handlers = {}

        with patch.object(
            flext_cli._api, "flext_cli_get_handlers", return_value=expected_handlers
        ) as mock_get:
            result = flext_cli.flext_cli_get_handlers()

            if result != expected_handlers:
                raise AssertionError(f"Expected {expected_handlers}, got {result}")
            assert len(result) == 0
            mock_get.assert_called_once()

    def test_flext_cli_get_handlers_detailed(self) -> None:
        """Test handlers retrieval with detailed information."""
        expected_handlers = {
            "request_handler": {
                "name": "request_handler",
                "type": "async_function",
                "description": "Handles HTTP requests",
                "active": True,
                "last_execution": "2025-01-01T14:30:00Z",
                "execution_count": 1500,
                "average_execution_time": 0.025,
            },
            "error_handler": {
                "name": "error_handler",
                "type": "callable_class",
                "description": "Handles application errors",
                "active": True,
                "last_execution": "2025-01-01T12:45:00Z",
                "execution_count": 42,
                "average_execution_time": 0.008,
            },
            "deprecated_handler": {
                "name": "deprecated_handler",
                "type": "function",
                "description": "Legacy handler (deprecated)",
                "active": False,
                "last_execution": "2024-12-15T10:00:00Z",
                "execution_count": 10,
                "average_execution_time": 0.150,
            },
        }

        with patch.object(
            flext_cli._api, "flext_cli_get_handlers", return_value=expected_handlers
        ) as mock_get:
            result = flext_cli.flext_cli_get_handlers()

            if result != expected_handlers:
                raise AssertionError(f"Expected {expected_handlers}, got {result}")
            if not (result["request_handler"]["active"]):
                raise AssertionError(
                    f"Expected True, got {result['request_handler']['active']}"
                )
            if result["deprecated_handler"]["active"]:
                raise AssertionError(
                    f"Expected False, got {result['deprecated_handler']['active']}"
                )
            assert result["request_handler"]["execution_count"] == 1500
            if len(result) != EXPECTED_DATA_COUNT:
                raise AssertionError(f"Expected {3}, got {len(result)}")
            mock_get.assert_called_once()


class TestFlextCliModuleIntegration:
    """Integration tests for flext_cli module."""

    def test_global_api_instance_exists(self) -> None:
        """Test that global API instance exists."""
        assert flext_cli._api is not None
        assert hasattr(flext_cli._api, "flext_cli_export")
        assert hasattr(flext_cli._api, "flext_cli_format")

    def test_all_functions_accessible(self) -> None:
        """Test that all public functions are accessible."""
        public_functions = [
            "flext_cli_export",
            "flext_cli_format",
            "flext_cli_configure",
            "flext_cli_health",
            "flext_cli_create_context",
            "flext_cli_create_command",
            "flext_cli_create_session",
            "flext_cli_register_handler",
            "flext_cli_register_plugin",
            "flext_cli_execute_handler",
            "flext_cli_render_with_context",
            "flext_cli_get_commands",
            "flext_cli_get_sessions",
            "flext_cli_get_plugins",
            "flext_cli_get_handlers",
        ]

        for func_name in public_functions:
            assert hasattr(flext_cli, func_name), f"Function {func_name} not found"
            func = getattr(flext_cli, func_name)
            assert callable(func), f"Function {func_name} is not callable"

    def test_module_imports(self) -> None:
        """Test that module imports work correctly."""
        # Test that imported classes/types are accessible
        assert hasattr(flext_cli, "FlextCliApi")
        assert hasattr(flext_cli, "FlextCliPlugin")
        assert hasattr(flext_cli, "TCliData")
        assert hasattr(flext_cli, "TCliFormat")
        assert hasattr(flext_cli, "TCliPath")

    def test_type_annotations(self) -> None:
        """Test that functions have proper type annotations."""
        # Test a few key functions for type annotations
        functions_to_test = [
            flext_cli.flext_cli_export,
            flext_cli.flext_cli_format,
            flext_cli.flext_cli_configure,
            flext_cli.flext_cli_health,
        ]

        for func in functions_to_test:
            sig = inspect.signature(func)
            # Verify that functions have return type annotations
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Function {func.__name__} missing return annotation"
            )

    def test_api_delegation_pattern(self) -> None:
        """Test that functions properly delegate to API instance."""
        # This test verifies that our module follows the delegation pattern
        # All functions should delegate to the _api instance

        with patch.object(
            flext_cli._api, "flext_cli_health", return_value={"status": "ok"}
        ) as mock_health:
            result = flext_cli.flext_cli_health()

            if result != {"status": "ok"}:
                raise AssertionError(f'Expected {{"status": "ok"}}, got {result}')
            mock_health.assert_called_once()

    def test_function_docstrings(self) -> None:
        """Test that functions have proper docstrings."""
        functions_to_test = [
            flext_cli.flext_cli_export,
            flext_cli.flext_cli_format,
            flext_cli.flext_cli_configure,
            flext_cli.flext_cli_health,
            flext_cli.flext_cli_create_context,
        ]

        for func in functions_to_test:
            assert func.__doc__ is not None, (
                f"Function {func.__name__} missing docstring"
            )
            assert len(func.__doc__.strip()) > 0, (
                f"Function {func.__name__} has empty docstring"
            )
            # Verify docstring contains Args and Returns sections for better documentation
            if "Args:" not in func.__doc__ and "Returns:" not in func.__doc__:
                raise AssertionError(
                    f"Function {func.__name__} missing Args/Returns documentation"
                )
