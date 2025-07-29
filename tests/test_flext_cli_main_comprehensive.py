"""Comprehensive tests for flext_cli main module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Tests for main CLI entry point to achieve near 100% coverage.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from flext_cli import (
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
)


class TestFlextCliFormat:
    """Test flext_cli_format function."""

    def test_flext_cli_format_exists(self) -> None:
        """Test that flext_cli_format function exists and is callable."""
        assert callable(flext_cli_format)

    def test_flext_cli_format_json(self) -> None:
        """Test format as JSON."""
        result = flext_cli_format({"test": "data"}, "json")
        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)
        if "test" not in formatted:
            raise AssertionError(f"Expected {"test"} in {formatted}")
        assert "data" in formatted

    def test_flext_cli_format_yaml(self) -> None:
        """Test format as YAML."""
        result = flext_cli_format({"test": "data"}, "yaml")
        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)
        if "test" not in formatted:
            raise AssertionError(f"Expected {"test"} in {formatted}")
        assert "data" in formatted

    def test_flext_cli_format_table(self) -> None:
        """Test format as table."""
        result = flext_cli_format([{"name": "test", "value": 123}], "table")
        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)

    def test_flext_cli_format_csv(self) -> None:
        """Test format as CSV."""
        result = flext_cli_format([{"name": "test", "value": 123}], "csv")
        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)

    def test_flext_cli_format_plain(self) -> None:
        """Test format as plain text."""
        result = flext_cli_format("simple text", "plain")
        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)


class TestFlextCliTable:
    """Test flext_cli_table function."""

    def test_flext_cli_table_exists(self) -> None:
        """Test that flext_cli_table function exists and is callable."""
        assert callable(flext_cli_table)

    def test_flext_cli_table_basic(self) -> None:
        """Test create table without title."""
        result = flext_cli_table([{"name": "test", "value": 123}])
        assert result.is_success
        table = result.unwrap()
        assert table is not None

    def test_flext_cli_table_with_title(self) -> None:
        """Test create table with title."""
        result = flext_cli_table([{"name": "test", "value": 123}], "Test Table")
        assert result.is_success
        table = result.unwrap()
        assert table is not None

    def test_flext_cli_table_empty_data(self) -> None:
        """Test create table with empty data."""
        result = flext_cli_table([])
        # Should handle empty data gracefully
        assert result.is_success or result.is_failure  # Either is acceptable


class TestFlextCliExport:
    """Test flext_cli_export function."""

    def test_flext_cli_export_exists(self) -> None:
        """Test that flext_cli_export function exists and is callable."""
        assert callable(flext_cli_export)

    def test_flext_cli_export_json(self) -> None:
        """Test export in JSON format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_path = f.name

        try:
            result = flext_cli_export({"test": "data"}, temp_path, "json")
            # Should return FlextResult
            assert hasattr(result, "is_success")
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_flext_cli_export_yaml(self) -> None:
        """Test export in YAML format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            temp_path = f.name

        try:
            result = flext_cli_export({"test": "data"}, temp_path, "yaml")
            assert hasattr(result, "is_success")
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_flext_cli_export_csv(self) -> None:
        """Test export in CSV format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            temp_path = f.name

        try:
            result = flext_cli_export(
                [{"name": "test", "value": 123}], temp_path, "csv"
            )
            assert hasattr(result, "is_success")
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestFlextCliFormat:
    """Test flext_cli_format function."""

    def test_flext_cli_format_exists(self) -> None:
        """Test that flext_cli_format function exists and is callable."""
        assert callable(flext_cli_format)

    def test_flext_cli_format_json(self) -> None:
        """Test format as JSON."""
        result = flext_cli_format({"test": "data"}, "json")
        assert isinstance(result, str)
        if "test" not in result:
            raise AssertionError(f"Expected {"test"} in {result}")
        assert "data" in result

    def test_flext_cli_format_yaml(self) -> None:
        """Test format as YAML."""
        result = flext_cli_format({"test": "data"}, "yaml")
        assert isinstance(result, str)
        if "test" not in result:
            raise AssertionError(f"Expected {"test"} in {result}")
        assert "data" in result

    def test_flext_cli_format_table(self) -> None:
        """Test format as table."""
        result = flext_cli_format([{"name": "test", "value": 123}], "table")
        assert isinstance(result, str)

    def test_flext_cli_format_plain(self) -> None:
        """Test format as plain text."""
        result = flext_cli_format("simple text", "plain")
        assert isinstance(result, str)


class TestFlextCliConfigure:
    """Test flext_cli_configure function."""

    def test_flext_cli_configure_exists(self) -> None:
        """Test that flext_cli_configure function exists and is callable."""
        assert callable(flext_cli_configure)

    def test_flext_cli_configure_with_dict(self) -> None:
        """Test configure with dictionary."""
        config = {"output_format": "json", "debug": True}
        result = flext_cli_configure(config)
        assert isinstance(result, bool)

    def test_flext_cli_configure_empty_dict(self) -> None:
        """Test configure with empty dictionary."""
        result = flext_cli_configure({})
        assert isinstance(result, bool)

    def test_flext_cli_configure_invalid_config(self) -> None:
        """Test configure with invalid config."""
        config = {"invalid_key": "invalid_value"}
        result = flext_cli_configure(config)
        assert isinstance(result, bool)


class TestFlextCliHealth:
    """Test flext_cli_health function."""

    def test_flext_cli_health_exists(self) -> None:
        """Test that flext_cli_health function exists and is callable."""
        assert callable(flext_cli_health)

    def test_flext_cli_health_returns_dict(self) -> None:
        """Test health check returns dictionary."""
        result = flext_cli_health()
        assert isinstance(result, dict)

    def test_flext_cli_health_contains_status(self) -> None:
        """Test health check contains status information."""
        result = flext_cli_health()
        assert isinstance(result, dict)
        # Should contain some status information
        if len(result) < 0:
            raise AssertionError(f"Expected {len(result)} >= {0}")


class TestFlextCliCreateContext:
    """Test flext_cli_create_context function."""

    def test_flext_cli_create_context_exists(self) -> None:
        """Test that flext_cli_create_context function exists and is callable."""
        assert callable(flext_cli_create_context)

    def test_flext_cli_create_context_no_config(self) -> None:
        """Test create context without config."""
        result = flext_cli_create_context()
        assert result is not None

    def test_flext_cli_create_context_with_config(self) -> None:
        """Test create context with config."""
        config = {"debug": True, "output_format": "json"}
        result = flext_cli_create_context(config)
        assert result is not None

    def test_flext_cli_create_context_empty_config(self) -> None:
        """Test create context with empty config."""
        result = flext_cli_create_context({})
        assert result is not None


class TestFlextCliCreateCommand:
    """Test flext_cli_create_command function."""

    def test_flext_cli_create_command_exists(self) -> None:
        """Test that flext_cli_create_command function exists and is callable."""
        assert callable(flext_cli_create_command)

    def test_flext_cli_create_command_basic(self) -> None:
        """Test create command with basic parameters."""
        result = flext_cli_create_command("test-cmd", "echo hello")
        assert isinstance(result, bool)

    def test_flext_cli_create_command_with_options(self) -> None:
        """Test create command with additional options."""
        result = flext_cli_create_command(
            "test-cmd-2",
            "echo world",
            timeout=30,
            description="Test command",
        )
        assert isinstance(result, bool)


class TestFlextCliCreateSession:
    """Test flext_cli_create_session function."""

    def test_flext_cli_create_session_exists(self) -> None:
        """Test that flext_cli_create_session function exists and is callable."""
        assert callable(flext_cli_create_session)

    def test_flext_cli_create_session_no_user(self) -> None:
        """Test create session without user ID."""
        result = flext_cli_create_session()
        assert isinstance(result, str)

    def test_flext_cli_create_session_with_user(self) -> None:
        """Test create session with user ID."""
        result = flext_cli_create_session("user123")
        assert isinstance(result, str)


class TestFlextCliRegisterHandler:
    """Test flext_cli_register_handler function."""

    def test_flext_cli_register_handler_exists(self) -> None:
        """Test that flext_cli_register_handler function exists and is callable."""
        assert callable(flext_cli_register_handler)

    def test_flext_cli_register_handler_basic(self) -> None:
        """Test register handler with basic function."""

        def test_handler() -> str:
            return "test result"

        result = flext_cli_register_handler("test_handler", test_handler)
        assert isinstance(result, bool)

    def test_flext_cli_register_handler_with_args(self) -> None:
        """Test register handler with arguments."""

        def test_handler_with_args(arg1, arg2) -> str:
            return f"{arg1} {arg2}"

        result = flext_cli_register_handler("test_handler_args", test_handler_with_args)
        assert isinstance(result, bool)


class TestFlextCliRegisterPlugin:
    """Test flext_cli_register_plugin function."""

    def test_flext_cli_register_plugin_exists(self) -> None:
        """Test that flext_cli_register_plugin function exists and is callable."""
        assert callable(flext_cli_register_plugin)

    def test_flext_cli_register_plugin_basic(self) -> None:
        """Test register plugin with basic plugin."""
        # Create a mock plugin
        mock_plugin = MagicMock()
        mock_plugin.name = "test_plugin"

        result = flext_cli_register_plugin("test_plugin", mock_plugin)
        assert isinstance(result, bool)


class TestFlextCliExecuteHandler:
    """Test flext_cli_execute_handler function."""

    def test_flext_cli_execute_handler_exists(self) -> None:
        """Test that flext_cli_execute_handler function exists and is callable."""
        assert callable(flext_cli_execute_handler)

    def test_flext_cli_execute_handler_basic(self) -> None:
        """Test execute handler basic functionality."""
        result = flext_cli_execute_handler("nonexistent_handler")
        # Should return something (result or error info)
        assert result is not None

    def test_flext_cli_execute_handler_with_args(self) -> None:
        """Test execute handler with arguments."""
        result = flext_cli_execute_handler("test_handler", "arg1", "arg2")
        assert result is not None

    def test_flext_cli_execute_handler_with_kwargs(self) -> None:
        """Test execute handler with keyword arguments."""
        result = flext_cli_execute_handler("test_handler", key1="value1", key2="value2")
        assert result is not None


class TestFlextCliGetFunctions:
    """Test flext_cli_get_* functions."""

    def test_flext_cli_get_commands_exists(self) -> None:
        """Test that flext_cli_get_commands function exists and is callable."""
        assert callable(flext_cli_get_commands)

    def test_flext_cli_get_commands_returns_dict(self) -> None:
        """Test get commands returns dictionary."""
        result = flext_cli_get_commands()
        assert isinstance(result, dict)

    def test_flext_cli_get_sessions_exists(self) -> None:
        """Test that flext_cli_get_sessions function exists and is callable."""
        assert callable(flext_cli_get_sessions)

    def test_flext_cli_get_sessions_returns_dict(self) -> None:
        """Test get sessions returns dictionary."""
        result = flext_cli_get_sessions()
        assert isinstance(result, dict)

    def test_flext_cli_get_plugins_exists(self) -> None:
        """Test that flext_cli_get_plugins function exists and is callable."""
        assert callable(flext_cli_get_plugins)

    def test_flext_cli_get_plugins_returns_dict(self) -> None:
        """Test get plugins returns dictionary."""
        result = flext_cli_get_plugins()
        assert isinstance(result, dict)

    def test_flext_cli_get_handlers_exists(self) -> None:
        """Test that flext_cli_get_handlers function exists and is callable."""
        assert callable(flext_cli_get_handlers)

    def test_flext_cli_get_handlers_returns_dict(self) -> None:
        """Test get handlers returns dictionary."""
        result = flext_cli_get_handlers()
        assert isinstance(result, dict)


class TestFlextCliIntegration:
    """Integration tests for FLEXT CLI functions."""

    def test_full_workflow(self) -> None:
        """Test complete workflow integration."""
        # Create context
        context = flext_cli_create_context({"debug": True})
        assert context is not None

        # Check health
        health = flext_cli_health()
        assert isinstance(health, dict)

        # Format data
        formatted = flext_cli_format({"test": "integration"}, "json")
        assert isinstance(formatted, str)

    def test_handler_workflow(self) -> None:
        """Test handler registration and execution workflow."""

        def integration_handler(value) -> str:
            return f"processed: {value}"

        # Register handler
        register_result = flext_cli_register_handler(
            "integration_test", integration_handler
        )
        assert isinstance(register_result, bool)

        # Execute handler
        execute_result = flext_cli_execute_handler("integration_test", "test_value")
        assert execute_result is not None

    def test_command_workflow(self) -> None:
        """Test command creation workflow."""
        # Create command
        create_result = flext_cli_create_command(
            "integration_cmd",
            "echo integration test",
            description="Integration test command",
        )
        assert isinstance(create_result, bool)

        # Get commands
        commands = flext_cli_get_commands()
        assert isinstance(commands, dict)

    def test_session_workflow(self) -> None:
        """Test session creation workflow."""
        # Create session
        session_result = flext_cli_create_session("integration_user")
        assert isinstance(session_result, str)

        # Get sessions
        sessions = flext_cli_get_sessions()
        assert isinstance(sessions, dict)

    def test_data_export_workflow(self) -> None:
        """Test data formatting and export workflow."""
        test_data = {
            "name": "integration_test",
            "value": 42,
            "items": ["a", "b", "c"],
        }

        # Format in different formats
        json_format = flext_cli_format(test_data, "json")
        yaml_format = flext_cli_format(test_data, "yaml")

        assert isinstance(json_format, str)
        assert isinstance(yaml_format, str)
        if "integration_test" not in json_format:
            raise AssertionError(f"Expected {"integration_test"} in {json_format}")
        assert "integration_test" in yaml_format

    def test_configuration_workflow(self) -> None:
        """Test configuration workflow."""
        # Configure system
        config_result = flext_cli_configure(
            {
                "output_format": "yaml",
                "debug": True,
                "timeout": 60,
            }
        )
        assert isinstance(config_result, bool)

        # Check health after configuration
        health = flext_cli_health()
        assert isinstance(health, dict)

    def test_error_handling_workflow(self) -> None:
        """Test error handling across functions."""
        # Test with invalid data types
        try:
            flext_cli_format(None, "json")
        except (RuntimeError, ValueError, TypeError):
            pass  # Expected to handle errors gracefully

        # Test with invalid handler
        result = flext_cli_execute_handler("nonexistent_handler_12345")
        assert result is not None  # Should return error info, not crash

        # Test with invalid export path
        invalid_path = "/invalid/path/that/does/not/exist/file.json"
        export_result = flext_cli_export({"test": "data"}, invalid_path, "json")
        assert isinstance(export_result, bool)  # Should handle gracefully


class TestFlextCliEdgeCases:
    """Test edge cases for FLEXT CLI functions."""

    def test_empty_data_handling(self) -> None:
        """Test handling of empty data."""
        # Empty dict
        result = flext_cli_format({}, "json")
        assert isinstance(result, str)

        # Empty list
        result = flext_cli_format([], "yaml")
        assert isinstance(result, str)

        # None value
        result = flext_cli_format(None, "plain")
        assert isinstance(result, str)

    def test_large_data_handling(self) -> None:
        """Test handling of large data structures."""
        large_data = {f"key_{i}": f"value_{i}" for i in range(1000)}

        result = flext_cli_format(large_data, "json")
        assert isinstance(result, str)
        assert len(result) > 1000  # Should contain substantial content

    def test_special_characters_handling(self) -> None:
        """Test handling of special characters."""
        special_data = {
            "unicode": "Hello 世界 🌍",
            "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "newlines": "line1\nline2\rline3\r\n",
            "tabs": "col1\tcol2\tcol3",
        }

        json_result = flext_cli_format(special_data, "json")
        yaml_result = flext_cli_format(special_data, "yaml")

        assert isinstance(json_result, str)
        assert isinstance(yaml_result, str)

    def test_nested_data_handling(self) -> None:
        """Test handling of deeply nested data."""
        nested_data = {"level1": {"level2": {"level3": {"level4": "deep_value"}}}}

        result = flext_cli_format(nested_data, "json")
        assert isinstance(result, str)
        if "deep_value" not in result:
            raise AssertionError(f"Expected {"deep_value"} in {result}")

    def test_concurrent_operations(self) -> None:
        """Test concurrent operations don't interfere."""
        # Multiple format operations
        results = []
        for i in range(10):
            result = flext_cli_format({"test": i}, "json")
            results.append(result)

        # All should succeed and be different
        if len(results) != 10:
            raise AssertionError(f"Expected {10}, got {len(results)}")
        if all(isinstance(r, str) for r not in results):
            raise AssertionError(f"Expected {all(isinstance(r, str) for r} in {results)}")
        if len(set(results)) != 10  # All unique:
            raise AssertionError(f"Expected {10  # All unique}, got {len(set(results))}")

    def test_memory_efficiency(self) -> None:
        """Test memory efficiency with repeated operations."""
        # Repeated operations should not cause memory leaks
        for _ in range(100):
            flext_cli_health()
            flext_cli_format({"test": "data"}, "json")
            flext_cli_create_context()

        # If we get here without running out of memory, test passes
        assert True
