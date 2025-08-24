"""Comprehensive tests for src/flext_cli/core.py module.

Tests all core service functionality for 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from flext_cli import (
    FlextCliConfig,
    FlextCliConfiguration,
    FlextCliEntityFactory,
    FlextCliPlugin,
)

# Constants
EXPECTED_BULK_SIZE = 2


def create_test_plugin(
    name: str = "test-plugin",
    entry_point: str = "test_plugin.main",
    version: str = "0.9.0",
) -> FlextCliPlugin:
    """Create a test plugin using proper factory pattern."""
    result = FlextCliEntityFactory.create_plugin(
        name=name,
        entry_point=entry_point,
        plugin_version=version,
    )
    assert result.is_success, f"Failed to create plugin: {result.error}"
    return result.value


# Import directly from the core.py file to avoid conflict with core/ directory
core_path = Path(__file__).parent.parent / "src" / "flext_cli" / "core.py"
spec = importlib.util.spec_from_file_location("flext_cli_core", core_path)
core_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core_module)

FlextCliService = core_module.FlextCliService
FlextService = core_module.FlextService


class TestFlextService:
    """Test FlextService base class."""

    def test_base_service_creation(self) -> None:
        """Test that FlextService can be instantiated."""
        service = FlextService()
        assert isinstance(service, FlextService)


class TestFlextCliService:
    """Test FlextCliService class."""

    def test_service_initialization(self) -> None:
        """Test service initialization."""
        service = FlextCliService()

        assert service._config is None
        assert isinstance(service._handlers, dict)
        assert isinstance(service._plugins, dict)
        assert isinstance(service._sessions, dict)
        assert isinstance(service._commands, dict)
        if service._formats != {"json", "yaml", "csv", "table", "plain"}:
            msg = f'Expected {{"json", "yaml", "csv", "table", "plain"}}, got {service._formats}'
            raise AssertionError(
                msg,
            )
        assert len(service._handlers) == 0
        if len(service._plugins) != 0:
            msg = f"Expected {0}, got {len(service._plugins)}"
            raise AssertionError(msg)
        assert len(service._sessions) == 0
        if len(service._commands) != 0:
            msg = f"Expected {0}, got {len(service._commands)}"
            raise AssertionError(msg)

    def test_configure_with_dict(self) -> None:
        """Test configuring service with dictionary."""
        service = FlextCliService()
        config_data = {
            "debug": True,
            "format_type": "json",
            "profile": "test",
        }

        result = service.configure(config_data)
        assert result.is_success
        assert service._config is not None
        if not (service._config.debug):
            msg = f"Expected True, got {service._config.debug}"
            raise AssertionError(msg)
        if service._config.format_type != "json":
            msg = f"Expected {'json'}, got {service._config.format_type}"
            raise AssertionError(
                msg,
            )
        assert service._config.profile == "test"

    def test_configure_with_flext_cli_config(self) -> None:
        """Test configuring service with FlextCliConfig object."""
        service = FlextCliService()
        config = FlextCliConfig(debug=False, output_format="yaml")

        result = service.configure(config)
        assert result.is_success
        assert service._config is not None
        if service._config.debug:
            msg = f"Expected False, got {service._config.debug}"
            raise AssertionError(msg)
        assert service._config.output_format == "yaml"

    def test_configure_with_invalid_type(self) -> None:
        """Test configuring service with invalid config type."""
        service = FlextCliService()
        invalid_config = "invalid"

        result = service.configure(invalid_config)
        assert not result.is_success
        if "Invalid config type:" not in result.error:
            msg = f"Expected {'Invalid config type:'} in {result.error}"
            raise AssertionError(msg)

    def test_configure_exception_handling(self) -> None:
        """Test configure method exception handling."""
        service = FlextCliService()

        # Mock FlextCliConfig to raise exception
        with patch(
            "flext_cli.core.FlextCliConfig",
            side_effect=Exception("Config error"),
        ):
            result = service.configure({"test": "data"})
            assert not result.is_success
            if "Configuration failed:" not in result.error:
                msg = f"Expected {'Configuration failed:'} in {result.error}"
                raise AssertionError(
                    msg,
                )

    def test_flext_cli_export_json(self) -> None:
        """Test exporting data as JSON."""
        service = FlextCliService()
        data = {"name": "test", "value": 42}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            delete=False,
            suffix=".json",
        ) as tmp:
            temp_path = tmp.name

        try:
            result = service.flext_cli_export(data, temp_path, "json")
            assert result.is_success
            if not (result.value):
                msg = f"Expected True, got {result.value}"
                raise AssertionError(msg)

            # Verify file content
            exported_data = json.loads(Path(temp_path).read_text(encoding="utf-8"))
            if exported_data != data:
                msg = f"Expected {data}, got {exported_data}"
                raise AssertionError(msg)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_flext_cli_export_yaml(self) -> None:
        """Test exporting data as YAML."""
        service = FlextCliService()
        data = {"name": "test", "items": ["a", "b", "c"]}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            delete=False,
            suffix=".yaml",
        ) as tmp:
            temp_path = tmp.name

        try:
            result = service.flext_cli_export(data, temp_path, "yaml")
            assert result.is_success
            if not (result.value):
                msg = f"Expected True, got {result.value}"
                raise AssertionError(msg)

            # Verify file exists and has content
            content = Path(temp_path).read_text(encoding="utf-8")
            if "name: test" not in content:
                msg = f"Expected {'name: test'} in {content}"
                raise AssertionError(msg)
            assert "items:" in content
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_flext_cli_export_creates_parent_directories(self) -> None:
        """Test that export creates parent directories."""
        service = FlextCliService()
        data = {"test": "data"}

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "path" / "file.json"

            result = service.flext_cli_export(data, str(nested_path), "json")
            assert result.is_success
            assert nested_path.exists()
            assert nested_path.parent.exists()

    def test_flext_cli_export_format_error(self) -> None:
        """Test export with invalid format."""
        service = FlextCliService()
        data = {"test": "data"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            delete=False,
        ) as tmp:
            temp_path = tmp.name

        try:
            result = service.flext_cli_export(data, temp_path, "invalid_format")
            assert not result.is_success
            if "Formatting failed:" not in result.error and "Unsupported format:" not in result.error:
                msg = f"Expected 'Formatting failed:' or 'Unsupported format:' in {result.error}"
                raise AssertionError(
                    msg,
                )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_flext_cli_export_exception_handling(self) -> None:
        """Test export method exception handling."""
        service = FlextCliService()
        data = {"test": "data"}

        # Use invalid path to trigger exception
        result = service.flext_cli_export(
            data,
            "/invalid/path/that/does/not/exist.json",
            "json",
        )
        assert not result.is_success
        if "Export failed:" not in result.error:
            msg = f"Expected {'Export failed:'} in {result.error}"
            raise AssertionError(msg)

    def test_flext_cli_format_json(self) -> None:
        """Test formatting data as JSON."""
        service = FlextCliService()
        data = {"name": "test", "values": [1, 2, 3]}

        result = service.flext_cli_format(data, "json")
        assert result.is_success
        formatted = result.value
        assert isinstance(formatted, str)

        # Verify it's valid JSON
        parsed = json.loads(formatted)
        if parsed != data:
            msg = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_flext_cli_format_yaml(self) -> None:
        """Test formatting data as YAML."""
        service = FlextCliService()
        data = {"name": "test", "enabled": True}

        result = service.flext_cli_format(data, "yaml")
        assert result.is_success
        formatted = result.value
        if "name: test" not in formatted:
            msg = f"Expected {'name: test'} in {formatted}"
            raise AssertionError(msg)
        assert "enabled: true" in formatted

    def test_flext_cli_format_csv_dict_list(self) -> None:
        """Test formatting list of dictionaries as CSV."""
        service = FlextCliService()
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        result = service.flext_cli_format(data, "csv")
        assert result.is_success
        formatted = result.value
        lines = formatted.strip().split("\n")
        if "name,age" not in lines[0]:
            msg = f"Expected {'name,age'} in {lines[0]}"
            raise AssertionError(msg)
        assert "Alice,30" in lines[1]
        if "Bob,25" not in lines[2]:
            msg = f"Expected {'Bob,25'} in {lines[2]}"
            raise AssertionError(msg)

    def test_flext_cli_format_csv_single_dict(self) -> None:
        """Test formatting single dictionary as CSV."""
        service = FlextCliService()
        data = {"name": "Alice", "age": 30}

        result = service.flext_cli_format(data, "csv")
        assert result.is_success
        formatted = result.value
        lines = formatted.strip().split("\n")
        if "name,age" not in lines[0]:
            msg = f"Expected {'name,age'} in {lines[0]}"
            raise AssertionError(msg)
        assert "Alice,30" in lines[1]

    def test_flext_cli_format_csv_simple_list(self) -> None:
        """Test formatting simple list as CSV."""
        service = FlextCliService()
        data = ["apple", "banana", "cherry"]

        result = service.flext_cli_format(data, "csv")
        assert result.is_success
        formatted = result.value
        lines = formatted.strip().split("\n")
        if "value" not in lines[0]:
            msg = f"Expected {'value'} in {lines[0]}"
            raise AssertionError(msg)
        assert "apple" in lines[1]
        if "banana" not in lines[2]:
            msg = f"Expected {'banana'} in {lines[2]}"
            raise AssertionError(msg)
        assert "cherry" in lines[3]

    def test_flext_cli_format_csv_empty_list(self) -> None:
        """Test formatting empty list as CSV."""
        service = FlextCliService()
        data: list[dict[str, object]] = []

        result = service.flext_cli_format(data, "csv")
        assert result.is_success
        formatted = result.value
        if formatted != "":
            msg = f"Expected {''}, got {formatted}"
            raise AssertionError(msg)

    def test_flext_cli_format_csv_simple_value(self) -> None:
        """Test formatting simple value as CSV."""
        service = FlextCliService()
        data = "simple_value"

        result = service.flext_cli_format(data, "csv")
        assert result.is_success
        formatted = result.value
        lines = formatted.strip().split("\n")
        if "value" not in lines[0]:
            msg = f"Expected {'value'} in {lines[0]}"
            raise AssertionError(msg)
        assert "simple_value" in lines[1]

    def test_flext_cli_format_table_dict(self) -> None:
        """Test formatting dictionary as table."""
        service = FlextCliService()
        data = {"name": "Alice", "age": 30, "city": "New York"}

        result = service.flext_cli_format(data, "table")
        assert result.is_success
        formatted = result.value
        if "name" not in formatted:
            msg = f"Expected {'name'} in {formatted}"
            raise AssertionError(msg)
        assert "Alice" in formatted
        if "age" not in formatted:
            msg = f"Expected {'age'} in {formatted}"
            raise AssertionError(msg)
        assert "30" in formatted

    def test_flext_cli_format_table_dict_list(self) -> None:
        """Test formatting list of dictionaries as table."""
        service = FlextCliService()
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        result = service.flext_cli_format(data, "table")
        assert result.is_success
        formatted = result.value
        if "name" not in formatted:
            msg = f"Expected {'name'} in {formatted}"
            raise AssertionError(msg)
        assert "age" in formatted
        if "Alice" not in formatted:
            msg = f"Expected {'Alice'} in {formatted}"
            raise AssertionError(msg)
        assert "Bob" in formatted
        if "|" not in formatted:  # Table separator
            msg = f"Expected {'|'} in {formatted}"
            raise AssertionError(msg)

    def test_flext_cli_format_table_simple_list(self) -> None:
        """Test formatting simple list as table."""
        service = FlextCliService()
        data = ["apple", "banana", "cherry"]

        result = service.flext_cli_format(data, "table")
        assert result.is_success
        formatted = result.value
        if "apple" not in formatted:
            msg = f"Expected {'apple'} in {formatted}"
            raise AssertionError(msg)
        assert "banana" in formatted
        if "cherry" not in formatted:
            msg = f"Expected {'cherry'} in {formatted}"
            raise AssertionError(msg)

    def test_flext_cli_format_table_simple_value(self) -> None:
        """Test formatting simple value as table."""
        service = FlextCliService()
        data = "simple_value"

        result = service.flext_cli_format(data, "table")
        assert result.is_success
        formatted = result.value
        if "simple_value" not in formatted:
            msg = f"Expected {'simple_value'} in {formatted}"
            raise AssertionError(msg)

    def test_flext_cli_format_table_empty_dict(self) -> None:
        """Test formatting empty dict as table."""
        service = FlextCliService()
        data: dict[str, object] = {}

        result = service.flext_cli_format(data, "table")
        assert result.is_success
        formatted = result.value
        if formatted != "":
            msg = f"Expected {''}, got {formatted}"
            raise AssertionError(msg)

    def test_flext_cli_format_plain(self) -> None:
        """Test formatting data as plain text."""
        service = FlextCliService()
        data = {"name": "test", "value": 42}

        result = service.flext_cli_format(data, "plain")
        assert result.is_success
        formatted = result.value
        if "test" not in formatted:
            msg = f"Expected {'test'} in {formatted}"
            raise AssertionError(msg)
        assert "42" in formatted

    def test_flext_cli_format_unsupported(self) -> None:
        """Test formatting with unsupported format."""
        service = FlextCliService()
        data = {"test": "data"}

        result = service.flext_cli_format(data, "unsupported")
        assert not result.is_success
        if "Unsupported format:" not in result.error:
            msg = f"Expected {'Unsupported format:'} in {result.error}"
            raise AssertionError(msg)

    def test_flext_cli_health_without_config(self) -> None:
        """Test health check without configuration."""
        service = FlextCliService()

        result = service.flext_cli_health()
        assert result.is_success
        health_data = result.value

        if health_data["service"] != "FlextCliService":
            msg = f"Expected {'FlextCliService'}, got {health_data['service']}"
            raise AssertionError(
                msg,
            )
        assert health_data["status"] == "healthy"
        if health_data["configured"]:
            msg = f"Expected False, got {health_data['configured']}"
            raise AssertionError(msg)
        assert health_data["handlers"] == 0
        if health_data["plugins"] != 0:
            msg = f"Expected {0}, got {health_data['plugins']}"
            raise AssertionError(msg)
        assert health_data["sessions"] == 0
        if health_data["commands"] != 0:
            msg = f"Expected {0}, got {health_data['commands']}"
            raise AssertionError(msg)
        assert isinstance(health_data["supported_formats"], list)
        if "json" not in health_data["supported_formats"]:
            msg = f"Expected {'json'} in {health_data['supported_formats']}"
            raise AssertionError(
                msg,
            )
        assert "config" not in health_data

    def test_flext_cli_health_with_config(self) -> None:
        """Test health check with configuration."""
        service = FlextCliService()
        config = FlextCliConfig(debug=True, output_format="json", profile="test")
        service.configure(config)

        result = service.flext_cli_health()
        assert result.is_success
        health_data = result.value

        if not (health_data["configured"]):
            msg = f"Expected True, got {health_data['configured']}"
            raise AssertionError(msg)
        if "config" not in health_data:
            msg = f"Expected {'config'} in {health_data}"
            raise AssertionError(msg)
        if health_data["config"]["format"] != "json":
            msg = f"Expected {'json'}, got {health_data['config']['format']}"
            raise AssertionError(
                msg,
            )
        if not (health_data["config"]["debug"]):
            msg = f"Expected True, got {health_data['config']['debug']}"
            raise AssertionError(msg)
        if health_data["config"]["profile"] != "test":
            msg = f"Expected {'test'}, got {health_data['config']['profile']}"
            raise AssertionError(
                msg,
            )

    def test_flext_cli_health_exception_handling(self) -> None:
        """Test health check exception handling."""
        service = FlextCliService()

        # Mock FlextUtilities to raise exception
        with patch(
            "flext_cli.core.FlextUtilities.generate_iso_timestamp",
            side_effect=Exception("Time error"),
        ):
            result = service.flext_cli_health()
            assert not result.is_success
            if "Health check failed:" not in result.error:
                msg = f"Expected {'Health check failed:'} in {result.error}"
                raise AssertionError(
                    msg,
                )

    def test_flext_cli_validate_format_valid(self) -> None:
        """Test format validation with valid format."""
        service = FlextCliService()

        for format_type in ["json", "yaml", "csv", "table", "plain"]:
            result = service.flext_cli_validate_format(format_type)
            assert result.is_success
            if result.value != format_type:
                msg = f"Expected {format_type}, got {result.value}"
                raise AssertionError(msg)

    def test_flext_cli_validate_format_invalid(self) -> None:
        """Test format validation with invalid format."""
        service = FlextCliService()

        result = service.flext_cli_validate_format("invalid")
        assert not result.is_success
        if "Unsupported format: invalid" not in result.error:
            msg = f"Expected {'Unsupported format: invalid'} in {result.error}"
            raise AssertionError(
                msg,
            )
        assert "Supported:" in result.error

    def test_flext_cli_create_command(self) -> None:
        """Test creating command."""
        service = FlextCliService()

        result = service.flext_cli_create_command("test-cmd", "echo hello", timeout=30)
        assert result.is_success
        created_message = result.value
        if "Command 'test-cmd' created" not in created_message:
            msg = f"Expected {"Command 'test-cmd' created"} in {created_message}"
            raise AssertionError(
                msg,
            )

        # Verify command was stored
        commands_result = service.flext_cli_get_commands()
        assert commands_result.is_success
        commands = commands_result.value
        if "test-cmd" not in commands:
            msg = f"Expected {'test-cmd'} in {commands}"
            raise AssertionError(msg)
        if commands["test-cmd"].name != "test-cmd":
            msg = f"Expected {'test-cmd'}, got {commands['test-cmd'].name}"
            raise AssertionError(
                msg,
            )
        assert commands["test-cmd"].command_line == "echo hello"

    def test_flext_cli_create_command_exception_handling(self) -> None:
        """Test create command exception handling."""
        service = FlextCliService()

        # Debug: Check that patch is working by showing the successful case first
        result_success = service.flext_cli_create_command(
            "test-cmd-success",
            "echo hello",
        )
        assert result_success.success, (
            f"Control test should succeed: {result_success.error}"
        )

        # Mock FlextCliCommand where it's used in the imported module
        with patch.object(
            core_module, "FlextCliCommand",
            side_effect=Exception("Command error")
        ):
            result = service.flext_cli_create_command("test-cmd", "echo hello")
            assert not result.is_success, f"Expected failure but got success: {result}"
            if result.error and "Command error" not in result.error:
                msg = f"Expected 'Command error' in {result.error}"
                raise AssertionError(msg)

    def test_flext_cli_create_session_without_user(self) -> None:
        """Test creating session without user ID."""
        service = FlextCliService()

        result = service.flext_cli_create_session()
        assert result.is_success
        created_message = result.value
        if "Session" not in created_message:
            msg = f"Expected {'Session'} in {created_message}"
            raise AssertionError(msg)
        assert "created" in created_message

        # Verify session was stored
        sessions_result = service.flext_cli_get_sessions()
        assert sessions_result.is_success
        sessions = sessions_result.value
        if len(sessions) != 1:
            msg = f"Expected {1}, got {len(sessions)}"
            raise AssertionError(msg)

    def test_flext_cli_create_session_with_user(self) -> None:
        """Test creating session with user ID."""
        service = FlextCliService()

        result = service.flext_cli_create_session("test-user-123")
        assert result.is_success
        created_message = result.value
        if "Session" not in created_message:
            msg = f"Expected {'Session'} in {created_message}"
            raise AssertionError(msg)
        assert "created" in created_message

        # Verify session was stored with user
        sessions_result = service.flext_cli_get_sessions()
        assert sessions_result.is_success
        sessions = sessions_result.value
        if len(sessions) != 1:
            msg = f"Expected {1}, got {len(sessions)}"
            raise AssertionError(msg)
        session = next(iter(sessions.values()))
        if session.user_id != "test-user-123":
            msg = f"Expected {'test-user-123'}, got {session.user_id}"
            raise AssertionError(msg)

    def test_flext_cli_create_session_exception_handling(self) -> None:
        """Test create session exception handling."""
        service = FlextCliService()

        # Mock FlextCliSession in the correct module namespace
        with patch.object(
            core_module,
            "FlextCliSession",
            side_effect=Exception("Session error"),
        ):
            result = service.flext_cli_create_session()
            assert not result.is_success
            if "Session error" not in result.error:
                msg = f"Expected {'Session error'} in {result.error}"
                raise AssertionError(msg)

    def test_flext_cli_register_handler(self) -> None:
        """Test registering handler."""
        service = FlextCliService()

        def handler(x: int) -> int:
            return x * 2

        result = service.flext_cli_register_handler("multiply", handler)
        assert result.is_success

        # Verify handler was stored
        handlers_result = service.flext_cli_get_handlers()
        assert handlers_result.is_success
        handlers = handlers_result.value
        if "multiply" not in handlers:
            msg = f"Expected {'multiply'} in {handlers}"
            raise AssertionError(msg)
        assert handlers["multiply"] is handler

    def test_flext_cli_register_handler_duplicate(self) -> None:
        """Test registering duplicate handler."""
        service = FlextCliService()

        def handler1(x: int) -> int:
            return x * 2

        def handler2(x: int) -> int:
            return x * 3

        # Register first handler
        result1 = service.flext_cli_register_handler("test", handler1)
        assert result1.success

        # Try to register duplicate
        result2 = service.flext_cli_register_handler("test", handler2)
        assert not result2.success
        if "already registered" not in result2.error:
            msg = f"Expected {'already registered'} in {result2.error}"
            raise AssertionError(msg)

    def test_flext_cli_register_plugin(self) -> None:
        """Test registering plugin."""
        service = FlextCliService()
        plugin = create_test_plugin()

        result = service.flext_cli_register_plugin("test-plugin", plugin)
        assert result.is_success

        # Verify plugin was stored
        plugins_result = service.flext_cli_get_plugins()
        assert plugins_result.is_success
        plugins = plugins_result.value
        if "test-plugin" not in plugins:
            msg = f"Expected {'test-plugin'} in {plugins}"
            raise AssertionError(msg)
        assert plugins["test-plugin"] is plugin

    def test_flext_cli_register_plugin_duplicate(self) -> None:
        """Test registering duplicate plugin."""
        service = FlextCliService()
        plugin1 = create_test_plugin("test-plugin")
        plugin2 = create_test_plugin("test-plugin")

        # Register first plugin
        result1 = service.flext_cli_register_plugin("test-plugin", plugin1)
        assert result1.success

        # Try to register duplicate
        result2 = service.flext_cli_register_plugin("test-plugin", plugin2)
        assert not result2.success
        if "already registered" not in result2.error:
            msg = f"Expected {'already registered'} in {result2.error}"
            raise AssertionError(msg)

    def test_flext_cli_execute_handler(self) -> None:
        """Test executing handler."""
        service = FlextCliService()

        def handler(x: int, y: int = 1) -> int:
            return x * y

        # Register handler
        service.flext_cli_register_handler("multiply", handler)

        # Execute handler
        result = service.flext_cli_execute_handler("multiply", 5, y=3)
        assert result.is_success
        if result.value != 15:
            msg = f"Expected {15}, got {result.value}"
            raise AssertionError(msg)

    def test_flext_cli_execute_handler_not_found(self) -> None:
        """Test executing non-existent handler."""
        service = FlextCliService()

        result = service.flext_cli_execute_handler("nonexistent")
        assert not result.is_success
        if "not found" not in result.error:
            msg = f"Expected {'not found'} in {result.error}"
            raise AssertionError(msg)

    def test_flext_cli_execute_handler_exception(self) -> None:
        """Test executing handler that raises exception."""
        service = FlextCliService()

        def handler() -> int:
            return 1 / 0  # Division by zero

        # Register handler
        service.flext_cli_register_handler("error", handler)

        # Execute handler
        result = service.flext_cli_execute_handler("error")
        assert not result.is_success
        if "division by zero" not in result.error:
            msg = f"Expected {'division by zero'} in {result.error}"
            raise AssertionError(msg)

    def test_flext_cli_render_with_context_default(self) -> None:
        """Test rendering with default context."""
        service = FlextCliService()
        config = FlextCliConfig(output_format="json")
        service.configure(config)

        data = {"name": "test", "value": 42}
        result = service.flext_cli_render_with_context(data)
        assert result.is_success

        # Should be formatted according to configured format
        formatted = result.value
        if not formatted or not isinstance(formatted, str):
            msg = f"Expected non-empty string, got {formatted!r}"
            raise AssertionError(msg)

        # Check if it's a table format (fallback) or JSON
        if formatted.startswith("name"):  # Table format
            assert "test" in formatted
            assert "42" in formatted
        else:  # JSON format
            parsed = json.loads(formatted)
            if parsed != data:
                msg = f"Expected {data}, got {parsed}"
                raise AssertionError(msg)

    def test_flext_cli_render_with_context_override(self) -> None:
        """Test rendering with context override."""
        service = FlextCliService()
        config = FlextCliConfiguration(output_format="json")
        service.configure(config)

        data = {"name": "test", "value": 42}
        context_options = {"output_format": "plain"}

        result = service.flext_cli_render_with_context(data, context_options)
        assert result.is_success

        # Should be formatted as plain text (override)
        formatted = result.value
        if "test" not in formatted:
            msg = f"Expected {'test'} in {formatted}"
            raise AssertionError(msg)
        assert "42" in formatted

    def test_flext_cli_render_with_context_no_config(self) -> None:
        """Test rendering with context when no service config."""
        service = FlextCliService()

        data = {"name": "test"}
        result = service.flext_cli_render_with_context(data, {"output_format": "json"})
        assert result.is_success

        formatted = result.value
        parsed = json.loads(formatted)
        if parsed != data:
            msg = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_flext_cli_get_commands_empty(self) -> None:
        """Test getting commands when empty."""
        service = FlextCliService()

        result = service.flext_cli_get_commands()
        assert result.is_success
        commands = result.value
        assert isinstance(commands, dict)
        if len(commands) != 0:
            msg = f"Expected {0}, got {len(commands)}"
            raise AssertionError(msg)

    def test_flext_cli_get_commands_with_data(self) -> None:
        """Test getting commands with data."""
        service = FlextCliService()

        # Create some commands
        service.flext_cli_create_command("cmd1", "echo 1")
        service.flext_cli_create_command("cmd2", "echo 2")

        result = service.flext_cli_get_commands()
        assert result.is_success
        commands = result.value
        if len(commands) != EXPECTED_BULK_SIZE:
            msg = f"Expected {2}, got {len(commands)}"
            raise AssertionError(msg)
        if "cmd1" not in commands:
            msg = f"Expected {'cmd1'} in {commands}"
            raise AssertionError(msg)
        assert "cmd2" in commands

    def test_flext_cli_get_sessions_empty(self) -> None:
        """Test getting sessions when empty."""
        service = FlextCliService()

        result = service.flext_cli_get_sessions()
        assert result.is_success
        sessions = result.value
        assert isinstance(sessions, dict)
        if len(sessions) != 0:
            msg = f"Expected {0}, got {len(sessions)}"
            raise AssertionError(msg)

    def test_flext_cli_get_sessions_with_data(self) -> None:
        """Test getting sessions with data."""
        service = FlextCliService()

        # Create some sessions
        service.flext_cli_create_session("user1")
        service.flext_cli_create_session("user2")

        result = service.flext_cli_get_sessions()
        assert result.is_success
        sessions = result.value
        if len(sessions) != EXPECTED_BULK_SIZE:
            msg = f"Expected {2}, got {len(sessions)}"
            raise AssertionError(msg)

    def test_flext_cli_get_plugins_empty(self) -> None:
        """Test getting plugins when empty."""
        service = FlextCliService()

        result = service.flext_cli_get_plugins()
        assert result.is_success
        plugins = result.value
        assert isinstance(plugins, dict)
        if len(plugins) != 0:
            msg = f"Expected {0}, got {len(plugins)}"
            raise AssertionError(msg)

    def test_flext_cli_get_plugins_with_data(self) -> None:
        """Test getting plugins with data."""
        service = FlextCliService()

        # Register some plugins
        plugin1 = create_test_plugin("plugin1", "plugin1.main")
        plugin2 = create_test_plugin("plugin2", "plugin2.main")
        service.flext_cli_register_plugin("plugin1", plugin1)
        service.flext_cli_register_plugin("plugin2", plugin2)

        result = service.flext_cli_get_plugins()
        assert result.is_success
        plugins = result.value
        if len(plugins) != EXPECTED_BULK_SIZE:
            msg = f"Expected {2}, got {len(plugins)}"
            raise AssertionError(msg)
        if "plugin1" not in plugins:
            msg = f"Expected {'plugin1'} in {plugins}"
            raise AssertionError(msg)
        assert "plugin2" in plugins

    def test_flext_cli_get_handlers_empty(self) -> None:
        """Test getting handlers when empty."""
        service = FlextCliService()

        result = service.flext_cli_get_handlers()
        assert result.is_success
        handlers = result.value
        assert isinstance(handlers, dict)
        if len(handlers) != 0:
            msg = f"Expected {0}, got {len(handlers)}"
            raise AssertionError(msg)

    def test_flext_cli_get_handlers_with_data(self) -> None:
        """Test getting handlers with data."""
        service = FlextCliService()

        # Register some handlers
        def handler1(x: int) -> int:
            return x + 1

        def handler2(x: int) -> int:
            return x * 2

        service.flext_cli_register_handler("add", handler1)
        service.flext_cli_register_handler("multiply", handler2)

        result = service.flext_cli_get_handlers()
        assert result.is_success
        handlers = result.value
        if len(handlers) != EXPECTED_BULK_SIZE:
            msg = f"Expected {2}, got {len(handlers)}"
            raise AssertionError(msg)
        if "add" not in handlers:
            msg = f"Expected {'add'} in {handlers}"
            raise AssertionError(msg)
        assert "multiply" in handlers


class TestPrivateFormatMethods:
    """Test private format methods for complete coverage."""

    def test_format_json_method(self) -> None:
        """Test _format_json method directly."""
        service = FlextCliService()
        data = {"key": "value"}

        result = service._format_json(data)
        assert result.is_success
        if json.loads(result.value) != data:
            msg = f"Expected {data}, got {json.loads(result.value)}"
            raise AssertionError(msg)

    def test_format_yaml_method(self) -> None:
        """Test _format_yaml method directly."""
        service = FlextCliService()
        data = {"key": "value"}

        result = service._format_yaml(data)
        assert result.is_success
        formatted = result.value
        if "key: value" not in formatted:
            msg = f"Expected {'key: value'} in {formatted}"
            raise AssertionError(msg)

    def test_format_csv_method_empty(self) -> None:
        """Test _format_csv method with empty data."""
        service = FlextCliService()
        data: list[dict[str, object]] = []

        result = service._format_csv(data)
        assert result.is_success
        if result.value != "":
            msg = f"Expected {''}, got {result.value}"
            raise AssertionError(msg)

    def test_format_table_method_dict(self) -> None:
        """Test _format_table method with dict."""
        service = FlextCliService()
        data = {"key": "value", "number": 42}

        result = service._format_table(data)
        assert result.is_success
        formatted = result.value
        if "key" not in formatted:
            msg = f"Expected {'key'} in {formatted}"
            raise AssertionError(msg)
        assert "value" in formatted

    def test_format_plain_method(self) -> None:
        """Test _format_plain method directly."""
        service = FlextCliService()
        data = {"key": "value"}

        result = service._format_plain(data)
        assert result.is_success
        if "key" not in result.value:
            msg = f"Expected {'key'} in {result.value}"
            raise AssertionError(msg)


class TestIntegration:
    """Integration tests for core service functionality."""

    def test_full_service_workflow(self) -> None:
        """Test complete service workflow."""
        service = FlextCliService()

        # 1. Configure service
        config_result = service.configure({"debug": True, "output_format": "json"})
        assert config_result.is_success

        # 2. Check health
        health_result = service.flext_cli_health()
        assert health_result.is_success
        health_data = health_result.value
        if not (health_data["configured"]):
            msg = f"Expected True, got {health_data['configured']}"
            raise AssertionError(msg)

        # 3. Create command
        cmd_result = service.flext_cli_create_command("test", "echo hello")
        assert cmd_result.is_success

        # 4. Create session
        session_result = service.flext_cli_create_session("test-user")
        assert session_result.is_success

        # 5. Register handler
        def handler(data: dict[str, object]) -> dict[str, object]:
            return {"processed": data}

        handler_result = service.flext_cli_register_handler("process", handler)
        assert handler_result.is_success

        # 6. Register plugin
        plugin = create_test_plugin()
        plugin_result = service.flext_cli_register_plugin("test-plugin", plugin)
        assert plugin_result.is_success

        # 7. Execute handler
        execute_result = service.flext_cli_execute_handler("process", {"input": "data"})
        assert execute_result.is_success
        processed = execute_result.value
        if processed["processed"]["input"] != "data":
            msg = f"Expected {'data'}, got {processed['processed']['input']}"
            raise AssertionError(
                msg,
            )

        # 8. Format and export data
        data = {"result": "success", "items": [1, 2, 3]}
        format_result = service.flext_cli_format(data, "json")
        assert format_result.is_success

        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            delete=False,
            suffix=".json",
        ) as tmp:
            temp_path = tmp.name

        try:
            export_result = service.flext_cli_export(data, temp_path, "json")
            assert export_result.is_success

            # Verify export
            exported = json.loads(Path(temp_path).read_text(encoding="utf-8"))
            if exported != data:
                msg = f"Expected {data}, got {exported}"
                raise AssertionError(msg)
        finally:
            Path(temp_path).unlink(missing_ok=True)

        # 9. Render with context
        render_result = service.flext_cli_render_with_context(data)
        assert render_result.is_success

        # 10. Get all resources
        commands_result = service.flext_cli_get_commands()
        sessions_result = service.flext_cli_get_sessions()
        plugins_result = service.flext_cli_get_plugins()
        handlers_result = service.flext_cli_get_handlers()

        assert commands_result.is_success
        assert sessions_result.is_success
        assert plugins_result.is_success
        assert handlers_result.is_success

        if len(commands_result.value) != 1:
            msg = f"Expected {1}, got {len(commands_result.value)}"
            raise AssertionError(msg)
        assert len(sessions_result.value) == 1
        if len(plugins_result.value) != 1:
            msg = f"Expected {1}, got {len(plugins_result.value)}"
            raise AssertionError(msg)
        assert len(handlers_result.value) == 1

    def test_service_error_handling(self) -> None:
        """Test service error handling across different methods."""
        service = FlextCliService()

        # Invalid configuration
        config_result = service.configure("invalid")
        assert not config_result.is_success

        # Invalid format validation
        format_result = service.flext_cli_validate_format("invalid")
        assert not format_result.is_success

        # Execute non-existent handler
        execute_result = service.flext_cli_execute_handler("nonexistent")
        assert not execute_result.is_success

        # Duplicate registrations
        def handler(x: int) -> int:
            return x

        plugin = create_test_plugin("test", "test.main")

        service.flext_cli_register_handler("test", handler)
        service.flext_cli_register_plugin("test", plugin)

        dup_handler_result = service.flext_cli_register_handler("test", handler)
        dup_plugin_result = service.flext_cli_register_plugin("test", plugin)

        assert not dup_handler_result.is_success
        assert not dup_plugin_result.is_success

    def test_format_compatibility(self) -> None:
        """Test format compatibility across different data types."""
        service = FlextCliService()

        test_data = [
            {"name": "dict", "data": {"key": "value", "number": 42}},
            {"name": "list", "data": [1, 2, 3, "text", True]},
            {"name": "string", "data": "simple string"},
            {"name": "number", "data": 12345},
            {"name": "boolean", "data": True},
            {
                "name": "list_of_dicts",
                "data": [{"name": "item1", "value": 1}, {"name": "item2", "value": 2}],
            },
        ]

        formats = ["json", "yaml", "csv", "table", "plain"]

        for test_case in test_data:
            for format_type in formats:
                result = service.flext_cli_format(test_case["data"], format_type)
                assert result.is_success, (
                    f"Failed to format {test_case['name']} as {format_type}"
                )
                formatted = result.value
                assert isinstance(formatted, str)
                assert len(formatted) > 0
