"""Comprehensive tests for core.py module (simplified).

Tests all core service functionality for 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path
from typing import Never
from unittest.mock import patch

import flext_cli.core

# Import directly from the core.py file to avoid conflicts
core_path = Path(__file__).parent.parent / "src" / "flext_cli" / "core.py"
spec = importlib.util.spec_from_file_location("flext_cli_core", core_path)
core_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core_module)

FlextCliService = core_module.FlextCliService
FlextService = core_module.FlextService


# Mock the flext_cli.types imports needed for testing
class MockFlextCliConfig:
    def __init__(self, data: dict | None = None) -> None:
        data = data or {}
        self.debug = data.get("debug", False)
        self.trace = data.get("trace", False)
        self.format_type = data.get("output_format", data.get("format_type", "table"))
        self.profile = data.get("profile", "default")
        self.api_url = data.get("api_url", "http://localhost:8000")


class MockFlextCliCommand:
    def __init__(
        self,
        entity_id: str | None = None,
        name: str | None = None,
        command_line: str | None = None,
        **options: object,
    ) -> None:
        self.id = entity_id or f"cmd_{name or 'unknown'}"
        self.name = name or "unknown"
        self.command_line = command_line or "echo test"
        self.options = options
        self.entity_id = self.id  # For backward compatibility


class MockFlextCliSession:
    def __init__(
        self, entity_id: str | None = None, user_id: str | None = None
    ) -> None:
        self.id = entity_id or f"session_{'_'.join(str(hash(self)).split())}"
        self.user_id = user_id
        self.entity_id = self.id  # For backward compatibility


class MockFlextCliPlugin:
    def __init__(self, name: str, version: str) -> None:
        self.name = name
        self.version = version


class MockFlextCliContext:
    def __init__(self, config: MockFlextCliConfig | None, **overrides: object) -> None:
        self.config = config or MockFlextCliConfig()
        self.output_format = overrides.get("output_format", self.config.format_type)


class TestFlextService:
    """Test FlextService base class."""

    def test_base_service_creation(self) -> None:
        """Test that FlextService can be instantiated."""
        service = FlextService()
        assert isinstance(service, FlextService)


class TestFlextCliService:
    """Test FlextCliService class."""

    def setup_method(self) -> None:
        """Setup mocks for each test."""
        # Patch the imports in core module (dynamic assignment for testing)
        core_module.FlextCliConfig = MockFlextCliConfig
        core_module.FlextCliCommand = MockFlextCliCommand
        core_module.FlextCliSession = MockFlextCliSession
        core_module.FlextCliPlugin = MockFlextCliPlugin
        core_module.FlextCliContext = MockFlextCliContext

    def test_service_initialization(self) -> None:
        """Test service initialization."""
        service = FlextCliService()

        assert service._config is None
        assert isinstance(service._handlers, dict)
        assert isinstance(service._plugins, dict)
        assert isinstance(service._sessions, dict)
        assert isinstance(service._commands, dict)
        if service._formats != {"json", "yaml", "csv", "table", "plain"}:
            raise AssertionError(
                f'Expected {{"json", "yaml", "csv", "table", "plain"}}, got {service._formats}'
            )

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
            raise AssertionError(f"Expected True, got {service._config.debug}")

    def test_configure_with_config_object(self) -> None:
        """Test configuring service with config object."""
        service = FlextCliService()
        config = MockFlextCliConfig({"debug": False, "output_format": "yaml"})

        result = service.configure(config)
        assert result.is_success
        assert service._config is config

    def test_configure_with_invalid_type(self) -> None:
        """Test configuring service with invalid config type."""
        service = FlextCliService()
        invalid_config = "invalid"

        result = service.configure(invalid_config)
        assert not result.is_success
        if "Invalid config type:" not in result.error:
            raise AssertionError(f"Expected {'Invalid config type:'} in {result.error}")

    def test_configure_exception_handling(self) -> None:
        """Test configure method exception handling."""
        service = FlextCliService()

        # Mock FlextCliConfig to raise exception
        with patch.object(
            core_module, "FlextCliConfig", side_effect=Exception("Config error")
        ):
            result = service.configure({"test": "data"})
            assert not result.is_success
            if "Configuration failed:" not in result.error:
                raise AssertionError(
                    f"Expected {'Configuration failed:'} in {result.error}"
                )

    def test_flext_cli_export_json(self) -> None:
        """Test exporting data as JSON."""
        service = FlextCliService()
        data = {"name": "test", "value": 42}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as tmp:
            temp_path = tmp.name

        try:
            result = service.flext_cli_export(data, temp_path, "json")
            assert result.is_success
            if not (result.unwrap()):
                raise AssertionError(f"Expected True, got {result.unwrap()}")

            # Verify file content
            exported_data = json.loads(Path(temp_path).read_text(encoding="utf-8"))
            if exported_data != data:
                raise AssertionError(f"Expected {data}, got {exported_data}")
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

    def test_flext_cli_export_format_error(self) -> None:
        """Test export with invalid format."""
        service = FlextCliService()
        data = {"test": "data"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False
        ) as tmp:
            temp_path = tmp.name

        try:
            result = service.flext_cli_export(data, temp_path, "invalid_format")
            assert not result.is_success
            if "Unsupported format:" not in result.error:
                raise AssertionError(
                    f"Expected {'Unsupported format:'} in {result.error}"
                )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_flext_cli_format_json(self) -> None:
        """Test formatting data as JSON."""
        service = FlextCliService()
        data = {"name": "test", "values": [1, 2, 3]}

        result = service.flext_cli_format(data, "json")
        assert result.is_success
        formatted = result.unwrap()
        assert isinstance(formatted, str)

        # Verify it's valid JSON
        parsed = json.loads(formatted)
        if parsed != data:
            raise AssertionError(f"Expected {data}, got {parsed}")

    def test_flext_cli_format_yaml(self) -> None:
        """Test formatting data as YAML."""
        service = FlextCliService()
        data = {"name": "test", "enabled": True}

        result = service.flext_cli_format(data, "yaml")
        assert result.is_success
        formatted = result.unwrap()
        if "name: test" not in formatted:
            raise AssertionError(f"Expected {'name: test'} in {formatted}")

    def test_flext_cli_format_csv_dict_list(self) -> None:
        """Test formatting list of dictionaries as CSV."""
        service = FlextCliService()
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        result = service.flext_cli_format(data, "csv")
        assert result.is_success
        formatted = result.unwrap()
        lines = formatted.strip().split("\n")
        if "name,age" not in lines[0]:
            raise AssertionError(f"Expected {'name,age'} in {lines[0]}")

    def test_flext_cli_format_csv_empty_list(self) -> None:
        """Test formatting empty list as CSV."""
        service = FlextCliService()
        data: list[dict[str, object]] = []

        result = service.flext_cli_format(data, "csv")
        assert result.is_success
        formatted = result.unwrap()
        if formatted != "":
            raise AssertionError(f"Expected {''}, got {formatted}")

    def test_flext_cli_format_table_dict(self) -> None:
        """Test formatting dictionary as table."""
        service = FlextCliService()
        data = {"name": "Alice", "age": 30}

        result = service.flext_cli_format(data, "table")
        assert result.is_success
        formatted = result.unwrap()
        if "name" not in formatted:
            raise AssertionError(f"Expected {'name'} in {formatted}")
        assert "Alice" in formatted

    def test_flext_cli_format_table_empty_dict(self) -> None:
        """Test formatting empty dict as table."""
        service = FlextCliService()
        data: dict[str, object] = {}

        result = service.flext_cli_format(data, "table")
        assert result.is_success
        formatted = result.unwrap()
        if formatted != "":
            raise AssertionError(f"Expected {''}, got {formatted}")

    def test_flext_cli_format_plain(self) -> None:
        """Test formatting data as plain text."""
        service = FlextCliService()
        data = {"name": "test", "value": 42}

        result = service.flext_cli_format(data, "plain")
        assert result.is_success
        formatted = result.unwrap()
        if "test" not in formatted:
            raise AssertionError(f"Expected {'test'} in {formatted}")

    def test_flext_cli_format_unsupported(self) -> None:
        """Test formatting with unsupported format."""
        service = FlextCliService()
        data = {"test": "data"}

        result = service.flext_cli_format(data, "unsupported")
        assert not result.is_success
        if "Unsupported format:" not in result.error:
            raise AssertionError(f"Expected {'Unsupported format:'} in {result.error}")

    def test_flext_cli_health_without_config(self) -> None:
        """Test health check without configuration."""
        service = FlextCliService()

        result = service.flext_cli_health()
        assert result.is_success
        health_data = result.unwrap()

        if health_data["service"] != "FlextCliService":
            raise AssertionError(
                f"Expected {'FlextCliService'}, got {health_data['service']}"
            )
        assert health_data["status"] == "healthy"
        if health_data["configured"]:
            raise AssertionError(f"Expected False, got {health_data['configured']}")

    def test_flext_cli_health_with_config(self) -> None:
        """Test health check with configuration."""
        service = FlextCliService()
        config = MockFlextCliConfig(
            {"debug": True, "output_format": "json", "profile": "test"}
        )
        service.configure(config)

        result = service.flext_cli_health()
        assert result.is_success
        health_data = result.unwrap()

        if not (health_data["configured"]):
            raise AssertionError(f"Expected True, got {health_data['configured']}")
        if "config" not in health_data:
            raise AssertionError(f"Expected {'config'} in {health_data}")

    def test_flext_cli_validate_format_valid(self) -> None:
        """Test format validation with valid format."""
        service = FlextCliService()

        for format_type in ["json", "yaml", "csv", "table", "plain"]:
            result = service.flext_cli_validate_format(format_type)
            assert result.is_success
            if result.unwrap() != format_type:
                raise AssertionError(f"Expected {format_type}, got {result.unwrap()}")

    def test_flext_cli_validate_format_invalid(self) -> None:
        """Test format validation with invalid format."""
        service = FlextCliService()

        result = service.flext_cli_validate_format("invalid")
        assert not result.is_success
        if "Unsupported format: invalid" not in result.error:
            raise AssertionError(
                f"Expected {'Unsupported format: invalid'} in {result.error}"
            )

    def test_flext_cli_create_command(self) -> None:
        """Test creating command."""
        service = FlextCliService()

        result = service.flext_cli_create_command("test-cmd", "echo hello", timeout=30)
        assert result.is_success
        created_message = result.unwrap()
        if "Command 'test-cmd' created" not in created_message:
            raise AssertionError(
                f"Expected {"Command 'test-cmd' created"} in {created_message}"
            )

    def test_flext_cli_create_session(self) -> None:
        """Test creating session."""
        service = FlextCliService()

        result = service.flext_cli_create_session("test-user")
        assert result.is_success
        created_message = result.unwrap()
        if "Session" not in created_message:
            raise AssertionError(f"Expected {'Session'} in {created_message}")
        assert "created" in created_message

    def test_flext_cli_register_handler(self) -> None:
        """Test registering handler."""
        service = FlextCliService()

        def handler(x: int) -> int:
            return x * 2

        result = service.flext_cli_register_handler("multiply", handler)
        assert result.is_success

    def test_flext_cli_register_handler_duplicate(self) -> None:
        """Test registering duplicate handler."""
        service = FlextCliService()

        def handler1(x: int) -> int:
            return x * 2

        def handler2(x: int) -> int:
            return x * 3

        # Register first handler
        result1 = service.flext_cli_register_handler("test", handler1)
        assert result1.is_success

        # Try to register duplicate
        result2 = service.flext_cli_register_handler("test", handler2)
        assert not result2.is_success
        if "already registered" not in result2.error:
            raise AssertionError(f"Expected {'already registered'} in {result2.error}")

    def test_flext_cli_register_plugin(self) -> None:
        """Test registering plugin."""
        service = FlextCliService()
        plugin = MockFlextCliPlugin("test-plugin", "0.9.0")

        result = service.flext_cli_register_plugin("test-plugin", plugin)
        assert result.is_success

    def test_flext_cli_register_plugin_duplicate(self) -> None:
        """Test registering duplicate plugin."""
        service = FlextCliService()
        plugin1 = MockFlextCliPlugin("test-plugin", "0.9.0")
        plugin2 = MockFlextCliPlugin("test-plugin", "0.9.0")

        # Register first plugin
        result1 = service.flext_cli_register_plugin("test-plugin", plugin1)
        assert result1.is_success

        # Try to register duplicate
        result2 = service.flext_cli_register_plugin("test-plugin", plugin2)
        assert not result2.is_success
        if "already registered" not in result2.error:
            raise AssertionError(f"Expected {'already registered'} in {result2.error}")

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
        if result.unwrap() != 15:
            raise AssertionError(f"Expected {15}, got {result.unwrap()}")

    def test_flext_cli_execute_handler_not_found(self) -> None:
        """Test executing non-existent handler."""
        service = FlextCliService()

        result = service.flext_cli_execute_handler("nonexistent")
        assert not result.is_success
        if "not found" not in result.error:
            raise AssertionError(f"Expected {'not found'} in {result.error}")

    def test_flext_cli_execute_handler_exception(self) -> None:
        """Test executing handler that raises exception."""
        service = FlextCliService()

        def handler() -> float:
            return 1 / 0  # Division by zero

        # Register handler
        service.flext_cli_register_handler("error", handler)

        # Execute handler
        result = service.flext_cli_execute_handler("error")
        assert not result.is_success
        if "division by zero" not in result.error:
            raise AssertionError(f"Expected {'division by zero'} in {result.error}")

    def test_flext_cli_render_with_context(self) -> None:
        """Test rendering with context."""
        service = FlextCliService()
        config = MockFlextCliConfig({"output_format": "json"})
        service.configure(config)

        data = {"name": "test", "value": 42}
        result = service.flext_cli_render_with_context(data)
        assert result.is_success

    def test_flext_cli_get_commands(self) -> None:
        """Test getting commands."""
        service = FlextCliService()

        result = service.flext_cli_get_commands()
        assert result.is_success
        commands = result.unwrap()
        assert isinstance(commands, dict)

    def test_flext_cli_get_sessions(self) -> None:
        """Test getting sessions."""
        service = FlextCliService()

        result = service.flext_cli_get_sessions()
        assert result.is_success
        sessions = result.unwrap()
        assert isinstance(sessions, dict)

    def test_flext_cli_get_plugins(self) -> None:
        """Test getting plugins."""
        service = FlextCliService()

        result = service.flext_cli_get_plugins()
        assert result.is_success
        plugins = result.unwrap()
        assert isinstance(plugins, dict)

    def test_flext_cli_get_handlers(self) -> None:
        """Test getting handlers."""
        service = FlextCliService()

        result = service.flext_cli_get_handlers()
        assert result.is_success
        handlers = result.unwrap()
        assert isinstance(handlers, dict)

    def test_format_table_with_dict_list(self) -> None:
        """Test table formatting with list of dicts."""
        service = FlextCliService()
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        result = service.flext_cli_format(data, "table")
        assert result.is_success
        formatted = result.unwrap()
        if "Alice" not in formatted:
            raise AssertionError(f"Expected {'Alice'} in {formatted}")
        assert "Bob" in formatted
        if "|" not in formatted:
            raise AssertionError(f"Expected {'|'} in {formatted}")

    def test_format_table_with_simple_list(self) -> None:
        """Test table formatting with simple list."""
        service = FlextCliService()
        data = ["apple", "banana", "cherry"]

        result = service.flext_cli_format(data, "table")
        assert result.is_success
        formatted = result.unwrap()
        if "apple" not in formatted:
            raise AssertionError(f"Expected {'apple'} in {formatted}")

    def test_format_csv_with_single_dict(self) -> None:
        """Test CSV formatting with single dict."""
        service = FlextCliService()
        data = {"name": "Alice", "age": 30}

        result = service.flext_cli_format(data, "csv")
        assert result.is_success
        formatted = result.unwrap()
        if "Alice" not in formatted:
            raise AssertionError(f"Expected {'Alice'} in {formatted}")

    def test_format_csv_with_simple_list(self) -> None:
        """Test CSV formatting with simple list."""
        service = FlextCliService()
        data = ["apple", "banana"]

        result = service.flext_cli_format(data, "csv")
        assert result.is_success
        formatted = result.unwrap()
        if "apple" not in formatted:
            raise AssertionError(f"Expected {'apple'} in {formatted}")

    def test_format_csv_with_simple_value(self) -> None:
        """Test CSV formatting with simple value."""
        service = FlextCliService()
        data = "simple_value"

        result = service.flext_cli_format(data, "csv")
        assert result.is_success
        formatted = result.unwrap()
        if "simple_value" not in formatted:
            raise AssertionError(f"Expected {'simple_value'} in {formatted}")

    def test_format_yaml_fallback_to_json(self) -> None:
        """Test YAML formatter fallback to JSON when yaml not available."""
        service = FlextCliService()
        data = {"test": "data"}

        # Mock yaml import to fail
        with patch(
            "builtins.__import__",
            side_effect=lambda name, *args: ImportError()
            if name == "yaml"
            else __import__(name, *args),
        ):
            result = service.flext_cli_format(data, "yaml")
            assert result.is_success
            formatted = result.unwrap()
            # Should fallback to JSON format
            if '"test"' not in formatted:
                raise AssertionError(f"Expected {'"test"'} in {formatted}")

    def test_health_check_exception_handling(self) -> None:
        """Test health check with exception."""
        service = FlextCliService()

        # Mock FlextUtilities to raise exception

        flext_cli.core.__dict__.get("FlextUtilities")

        def mock_utilities() -> Never:
            msg = "Utilities error"
            raise RuntimeError(msg)

        with patch.dict(
            "sys.modules",
            {
                "flext_core.utilities": type(
                    "MockModule",
                    (),
                    {
                        "FlextUtilities": type(
                            "MockUtils", (), {"generate_iso_timestamp": mock_utilities}
                        )
                    },
                )()
            },
        ):
            result = service.flext_cli_health()
            assert not result.is_success
            if "Health check failed:" not in result.error:
                raise AssertionError(
                    f"Expected {'Health check failed:'} in {result.error}"
                )

    def test_export_exception_handling(self) -> None:
        """Test export with file write exception."""
        service = FlextCliService()
        data = {"test": "data"}

        # Use invalid path to trigger exception
        result = service.flext_cli_export(data, "/invalid/path/file.json")
        assert not result.is_success
        if "Export failed:" not in result.error:
            raise AssertionError(f"Expected {'Export failed:'} in {result.error}")

    def test_create_command_exception_handling(self) -> None:
        """Test create command with exception."""
        service = FlextCliService()

        # Mock FlextCliCommand to raise exception
        with patch.object(
            core_module, "FlextCliCommand", side_effect=Exception("Command error")
        ):
            result = service.flext_cli_create_command("test", "echo")
            assert not result.is_success

    def test_create_session_exception_handling(self) -> None:
        """Test create session with exception."""
        service = FlextCliService()

        # Mock FlextCliSession to raise exception
        with patch.object(
            core_module, "FlextCliSession", side_effect=Exception("Session error")
        ):
            result = service.flext_cli_create_session()
            assert not result.is_success
