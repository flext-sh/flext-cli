"""Tests for core.py to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Import both services from core.py directly (not the abstract base_service.py version)
import importlib.util

spec = importlib.util.spec_from_file_location(
    "core_module", "/home/marlonsc/flext/flext-cli/src/flext_cli/core.py"
)
core_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core_module)

FlextService = core_module.FlextService
FlextCliService = core_module.FlextCliService


class TestFlextService:
    """Test FlextService basic functionality."""

    def test_service_creation(self) -> None:
        """Test service can be created."""
        service = FlextService()
        assert service is not None

    def test_service_start(self) -> None:
        """Test service start method."""
        service = FlextService()
        result = service.start()
        assert result.is_success
        assert result.value is None


class TestFlextCliService:
    """Test FlextCliService functionality."""

    def test_cli_service_creation(self) -> None:
        """Test CLI service can be created."""
        service = FlextCliService()
        assert service is not None

    def test_cli_service_format_table_data(self) -> None:
        """Test table formatting."""
        service = FlextCliService()
        data = [{"name": "test", "value": 123}]
        # Use the actual method name flext_cli_format
        result = service.flext_cli_format(data, "table")
        assert result.is_success
        assert "test" in result.value
        assert "123" in result.value

    def test_cli_service_format_json_data(self) -> None:
        """Test JSON formatting."""
        service = FlextCliService()
        data = {"test": "value", "number": 42}
        result = service.flext_cli_format(data, "json")
        assert result.is_success
        assert "test" in result.value
        assert "value" in result.value

    def test_cli_service_format_yaml_data(self) -> None:
        """Test YAML formatting."""
        service = FlextCliService()
        data = {"test": "value", "items": [1, 2, 3]}
        result = service.flext_cli_format(data, "yaml")
        assert result.is_success
        assert "test:" in result.value
        assert "value" in result.value

    def test_cli_service_format_csv_data(self) -> None:
        """Test CSV formatting."""
        service = FlextCliService()
        data = [{"name": "item1", "value": 10}, {"name": "item2", "value": 20}]
        result = service.flext_cli_format(data, "csv")
        assert result.is_success
        assert "name,value" in result.value
        assert "item1,10" in result.value

    def test_cli_service_validate_format(self) -> None:
        """Test format validation."""
        service = FlextCliService()

        # Test valid format
        result = service.flext_cli_validate_format("json")
        assert result.is_success

        # Test invalid format
        result = service.flext_cli_validate_format("invalid")
        assert result.is_failure
        assert "Unsupported format" in result.error

    def test_cli_service_health_check(self) -> None:
        """Test health check functionality."""
        service = FlextCliService()

        # Test flext_cli_health method
        result = service.flext_cli_health()
        assert result.is_success
        assert "service" in result.value
        assert result.value["service"] == "FlextCliService"

        # Test inherited health_check method
        result = service.health_check()
        assert result.is_success

    def test_cli_service_export_data(self) -> None:
        """Test data export functionality."""
        service = FlextCliService()

        # Test JSON export
        data = {"test": "value", "number": 42}
        result = service.flext_cli_export(data, "/tmp/test_export.json", "json")
        assert result.is_success

        # Test CSV export
        data = [{"name": "item1", "value": 10}, {"name": "item2", "value": 20}]
        result = service.flext_cli_export(data, "/tmp/test_export.csv", "csv")
        assert result.is_success

    def test_cli_service_render_with_context(self) -> None:
        """Test rendering with context options."""
        service = FlextCliService()

        # Test rendering with context options
        data = {"message": "Hello", "status": "active"}
        result = service.flext_cli_render_with_context(data, {"output_format": "json"})
        assert result.is_success
        assert "message" in result.value

        # Test rendering with table format
        result = service.flext_cli_render_with_context(data, {"output_format": "table"})
        assert result.is_success

    def test_cli_service_register_handler(self) -> None:
        """Test handler registration."""
        service = FlextCliService()

        def test_handler(data: object) -> object:
            return f"processed: {data}"

        result = service.flext_cli_register_handler("test_handler", test_handler)
        assert result.is_success

        # Test handler execution
        exec_result = service.flext_cli_execute_handler("test_handler", "test_data")
        assert exec_result.is_success
        assert "processed: test_data" in str(exec_result.value)
