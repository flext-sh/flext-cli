"""Test module for core - Real API only.

Tests FlextCliService using actual implemented methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import cast

from flext_cli.config import FlextCliConfig
from flext_cli.core import FlextCliService
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class TestFlextCliService:
    """Real functionality tests for FlextCliService class."""

    def test_service_creation_and_start(self) -> None:
        """Test FlextCliService can be created and started."""
        service = FlextCliService()
        assert isinstance(service, FlextCliService)

        start_result = service.start()
        assert start_result.is_success
        assert start_result.value is None

    def test_service_stop_functionality(self) -> None:
        """Test FlextCliService stop functionality."""
        service = FlextCliService()

        stop_result = service.stop()
        assert stop_result.is_success
        assert stop_result.value is None

    def test_service_health_check(self) -> None:
        """Test FlextCliService health check functionality."""
        service = FlextCliService()

        health_result = service.health_check()
        assert health_result.is_success
        health_status = health_result.value
        assert health_status == "healthy"

    def test_service_lifecycle_complete(self) -> None:
        """Test complete service lifecycle: start -> health -> stop."""
        service = FlextCliService()

        start_result = service.start()
        assert start_result.is_success

        health_result = service.health_check()
        assert health_result.is_success
        assert health_result.value == "healthy"

        stop_result = service.stop()
        assert stop_result.is_success


class TestFlextCliServiceConfiguration:
    """Real functionality tests for FlextCliService configuration."""

    def test_service_initialization_real(self) -> None:
        """Test FlextCliService initialization with real attributes."""
        service = FlextCliService()

        config = service.get_config()
        handlers = service.get_handlers()
        plugins = service.get_plugins()
        sessions = service.get_sessions()
        commands = service.get_commands()
        formatters = service.get_formatters()

        assert config is not None  # Service auto-initializes with default config
        assert isinstance(handlers, dict)
        assert isinstance(plugins, dict)
        assert isinstance(sessions, dict)
        assert isinstance(commands, dict)
        assert hasattr(formatters, "list_formats")

        assert len(handlers) == 0
        assert len(plugins) == 0
        assert len(sessions) == 0
        assert len(commands) == 0

    def test_configure_with_flext_cli_config_object(self) -> None:
        """Test configuring service with FlextCliConfig object."""
        service = FlextCliService()
        config = FlextCliConfig.MainConfig(
            debug=True,
            output_format="json",
            profile="test-profile",
        )

        result = service.configure(config)
        assert result.is_success

        service_config = service.get_config()
        assert service_config is not None
        assert service_config.debug_mode is True
        assert service_config.output_format == "json"
        assert service_config.profile == "test-profile"

    def test_configure_with_dict_valid_keys(self) -> None:
        """Test configuring service with dictionary containing valid keys."""
        service = FlextCliService()
        config_dict = {
            "debug_mode": False,
            "output_format": "yaml",
            "profile": "production",
        }

        result = service.configure(
            cast("dict[str, str | int | float | bool]", config_dict)
        )
        assert result.is_success

        service_config = service.get_config()
        assert service_config is not None
        assert service_config.debug_mode is False
        assert service_config.output_format == "yaml"
        assert service_config.profile == "production"


class TestFlextCliServiceFormatting:
    """Real functionality tests for FlextCliService data formatting."""

    def test_format_json_simple_data(self) -> None:
        """Test JSON formatting with simple data."""
        service = FlextCliService()
        data = {"name": "test", "value": 123, "active": True}

        result = service.format_data(
            cast("dict[str, str | int | float | bool]", data), "json"
        )
        assert result.is_success
        formatted = result.value

        parsed = json.loads(formatted)
        assert parsed["name"] == "test"
        assert parsed["value"] == 123
        assert parsed["active"] is True

    def test_format_json_complex_data(self) -> None:
        """Test JSON formatting with complex nested data."""
        service = FlextCliService()
        data = {
            "users": [
                {"id": 1, "name": "Alice", "permissions": ["read", "write"]},
                {"id": 2, "name": "Bob", "permissions": ["read"]},
            ],
            "metadata": {"total": 2, "created_at": "2025-01-01T00:00:00Z"},
        }

        result = service.format_data(
            cast("dict[str, str | int | float | bool]", data), "json"
        )
        assert result.is_success
        formatted = result.value

        parsed = json.loads(formatted)
        assert len(parsed["users"]) == 2
        assert parsed["users"][0]["name"] == "Alice"
        assert "write" in parsed["users"][0]["permissions"]
        assert parsed["metadata"]["total"] == 2

    def test_format_table_dict_data(self) -> None:
        """Test table formatting with dictionary data."""
        service = FlextCliService()
        data = {
            "server_name": "production-server",
            "port": 8080,
            "status": "active",
            "uptime": "99.9%",
        }

        result = service.format_data(
            cast("dict[str, str | int | float | bool]", data), "table"
        )
        assert result.is_success
        formatted = result.value

        assert "server_name" in formatted
        assert "production-server" in formatted
        assert "8080" in formatted
        assert "active" in formatted

    def test_format_unsupported_format(self) -> None:
        """Test formatting with unsupported format fails appropriately."""
        service = FlextCliService()
        data = {"test": "data"}

        result = service.format_data(
            cast("dict[str, str | int | float | bool]", data), "xml"
        )
        # Should default to JSON format
        assert result.is_success
        assert "test" in result.value


class TestFlextCliServiceExport:
    """Real functionality tests for FlextCliService export."""

    def test_export_json_to_file(self) -> None:
        """Test exporting JSON data to file."""
        service = FlextCliService()
        data = {"export_test": "json", "timestamp": "2025-01-01", "count": 42}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_export.json"

            result = service.flext_cli_export(
                cast("dict[str, str | int | float | bool]", data),
                str(output_file),
                "json",
            )
            assert result.is_success
            assert output_file.exists()

            with output_file.open(encoding="utf-8") as f:
                content = json.load(f)
                assert content["export_test"] == "json"
                assert content["count"] == 42

    def test_export_creates_parent_directories(self) -> None:
        """Test export creates parent directories when they don't exist."""
        service = FlextCliService()
        data = {"test": "directory_creation"}

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "level1" / "level2" / "test.json"

            result = service.flext_cli_export(
                cast("dict[str, str | int | float | bool]", data),
                str(nested_path),
                "json",
            )
            assert result.is_success
            assert nested_path.exists()
            assert nested_path.parent.exists()


class TestFlextCliServiceHealth:
    """Real functionality tests for FlextCliService health."""

    def test_health_basic_status(self) -> None:
        """Test health check returns basic service status."""
        service = FlextCliService()
        result = service.flext_cli_health()
        assert result.is_success

        health_data = result.value
        assert health_data["service"] == "FlextCliService"
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        assert health_data["configured"] is True  # Service is always configured
        assert health_data["handlers"] == 0
        assert health_data["plugins"] == 0

    def test_health_with_configuration(self) -> None:
        """Test health check after explicit configuration."""
        service = FlextCliService()
        config = FlextCliConfig.MainConfig(
            debug=True, output_format="json", profile="test"
        )
        service.configure(config)

        result = service.flext_cli_health()
        assert result.is_success

        health_data = result.value
        assert health_data["configured"] is True
        assert health_data["handlers"] == 0
        assert health_data["plugins"] == 0

    def test_get_service_health_method(self) -> None:
        """Test get_service_health method."""
        service = FlextCliService()

        result = service.get_service_health()
        assert isinstance(result, FlextResult)
        assert result.is_success

        health_data = result.unwrap()
        assert isinstance(health_data, dict)
        assert "service" in health_data
        assert "status" in health_data


class TestFlextCliServiceCommands:
    """Real functionality tests for FlextCliService commands."""

    def test_create_command_with_real_entity(self) -> None:
        """Test creating commands with real FlextCliCommand entities."""
        service = FlextCliService()
        result = service.create_command(command_line="echo 'hello world'")

        assert result.is_success
        command = result.unwrap()
        assert isinstance(command, FlextCliModels.CliCommand)
        assert command.command_line == "echo 'hello world'"


class TestFlextCliServiceSessions:
    """Real functionality tests for FlextCliService sessions."""

    def test_create_session_with_user_id(self) -> None:
        """Test creating sessions with specified user ID."""
        service = FlextCliService()
        result = service.create_session(user_id="test-user-123")

        assert result.is_success
        session = result.unwrap()
        assert session.user_id == "test-user-123"
        assert isinstance(session, FlextCliModels.CliSession)

    def test_create_session_auto_user_id(self) -> None:
        """Test creating sessions with auto-generated user ID."""
        service = FlextCliService()
        result = service.create_session()

        assert result.is_success
        session = result.unwrap()
        assert session.user_id is not None
        assert isinstance(session, FlextCliModels.CliSession)
        assert session.user_id.startswith("user_")


class TestFlextCliServiceHandlers:
    """Real functionality tests for FlextCliService handlers."""

    def test_register_and_execute_handler(self) -> None:
        """Test registering and executing handlers with real functionality."""
        service = FlextCliService()

        def test_handler(data: object) -> str:
            return f"Processed: {data}"

        register_result = service.flext_cli_register_handler(
            "test-handler", test_handler
        )
        assert register_result.is_success

        execute_result = service.flext_cli_execute_handler(
            "test-handler", data="test-data"
        )
        assert execute_result.is_success
        assert execute_result.value == "Processed: test-data"

    def test_register_duplicate_handler_fails(self) -> None:
        """Test registering duplicate handler names fails."""
        service = FlextCliService()

        def handler1(__data: object, /) -> str:
            return "handler1"

        def handler2(__data: object, /) -> str:
            return "handler2"

        result1 = service.flext_cli_register_handler("duplicate", handler1)
        assert result1.is_success

        result2 = service.flext_cli_register_handler("duplicate", handler2)
        assert result2.is_failure
        assert "Handler 'duplicate' already registered" in (result2.error or "")

    def test_execute_nonexistent_handler(self) -> None:
        """Test executing non-existent handler fails appropriately."""
        service = FlextCliService()
        result = service.flext_cli_execute_handler("nonexistent", data="data")
        assert result.is_failure
        assert "Handler 'nonexistent' not found" in (result.error or "")


class TestFlextCliServiceProperties:
    """Real functionality tests for FlextCliService properties."""

    def test_registry_property(self) -> None:
        """Test registry property."""
        service = FlextCliService()
        registry = service.registry
        assert registry is not None

    def test_orchestrator_property(self) -> None:
        """Test orchestrator property."""
        service = FlextCliService()
        orchestrator = service.orchestrator
        assert orchestrator is not None

    def test_metrics_property(self) -> None:
        """Test metrics property."""
        service = FlextCliService()
        metrics = service.metrics
        assert isinstance(metrics, dict)

    def test_update_configuration_method(self) -> None:
        """Test update_configuration method."""
        service = FlextCliService()
        service.update_configuration()
        assert hasattr(service, "update_configuration")
        assert callable(service.update_configuration)
