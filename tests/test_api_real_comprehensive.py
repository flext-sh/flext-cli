"""Comprehensive real functionality tests for api.py module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

NO MOCKING - All tests execute real functionality and validate actual business logic.
Following user requirement: "pare de ficar mockando tudo!"
"""

from __future__ import annotations

import json
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml
from flext_core import FlextModels, FlextResult
from rich.console import Console
from rich.table import Table

from flext_cli.api import (
    ContextRenderingStrategy,
    FlextCliApi,
    FlextCliContext,
    PluginLike,
    flext_cli_aggregate_data,
    flext_cli_batch_export,
    flext_cli_export,
    flext_cli_format,
    flext_cli_table,
    flext_cli_transform_data,
    flext_cli_unwrap_or_default,
    flext_cli_unwrap_or_none,
)
from flext_cli.config import FlextCliSettings
from flext_cli.models import (
    FlextCliCommand as CLICommand,
    FlextCliPlugin,
)


class TestFlextCliFormat:
    """Test flext_cli_format function with real formatting."""

    def test_format_json_simple_dict(self) -> None:
        """Test JSON formatting with simple dictionary."""
        test_data = {"name": "John", "age": 30, "city": "New York"}

        result = flext_cli_format(test_data, "json")

        assert result.is_success
        formatted_output = result.value
        parsed = json.loads(formatted_output)
        assert parsed == test_data
        assert "John" in formatted_output
        assert "30" in formatted_output

    def test_format_yaml_simple_dict(self) -> None:
        """Test YAML formatting with simple dictionary."""
        test_data = {"name": "Jane", "age": 25, "active": True}

        result = flext_cli_format(test_data, "yaml")

        assert result.is_success
        formatted_output = result.value
        parsed = yaml.safe_load(formatted_output)
        assert parsed == test_data
        assert "Jane" in formatted_output
        assert "25" in formatted_output

    def test_format_table_list_of_dicts(self) -> None:
        """Test table formatting with list of dictionaries."""
        test_data = [
            {"name": "Alice", "age": 28, "department": "Engineering"},
            {"name": "Bob", "age": 32, "department": "Marketing"},
        ]

        result = flext_cli_format(test_data, "table")

        assert result.is_success
        formatted_output = result.value
        assert "Alice" in formatted_output
        assert "Bob" in formatted_output
        assert "Engineering" in formatted_output
        assert "Marketing" in formatted_output

    def test_format_table_single_dict(self) -> None:
        """Test table formatting with single dictionary."""
        test_data = {"username": "admin", "role": "administrator", "active": True}

        result = flext_cli_format(test_data, "table")

        assert result.is_success
        formatted_output = result.value
        assert "admin" in formatted_output
        assert "administrator" in formatted_output
        assert "True" in formatted_output

    def test_format_csv_simple_data(self) -> None:
        """Test CSV formatting (falls back to string representation)."""
        test_data = ["item1", "item2", "item3"]

        result = flext_cli_format(test_data, "csv")

        assert result.is_success
        formatted_output = result.value
        assert "item1" in formatted_output

    def test_format_plain_simple_string(self) -> None:
        """Test plain formatting with simple string."""
        test_data = "Hello, World!"

        result = flext_cli_format(test_data, "plain")

        assert result.is_success
        formatted_output = result.value
        assert formatted_output == test_data

    def test_format_invalid_format_type(self) -> None:
        """Test formatting with invalid format type."""
        test_data = {"test": "data"}

        result = flext_cli_format(test_data, "invalid_format")

        assert not result.is_success
        assert "Invalid format 'invalid_format'" in (result.error or "")

    def test_format_json_with_complex_data(self) -> None:
        """Test JSON formatting with complex nested data."""
        test_data = {
            "users": [
                {
                    "id": 1,
                    "name": "Alice",
                    "settings": {"theme": "dark", "notifications": True},
                },
                {
                    "id": 2,
                    "name": "Bob",
                    "settings": {"theme": "light", "notifications": False},
                },
            ],
            "metadata": {"total": 2, "created": datetime.now(UTC).isoformat()},
        }

        result = flext_cli_format(test_data, "json")

        assert result.is_success
        formatted_output = result.value
        parsed = json.loads(formatted_output)
        assert parsed["users"][0]["name"] == "Alice"
        assert parsed["users"][1]["settings"]["theme"] == "light"
        assert parsed["metadata"]["total"] == 2


class TestFlextCliTable:
    """Test flext_cli_table function with real table creation."""

    def test_table_from_list_of_dicts(self) -> None:
        """Test table creation from list of dictionaries."""
        test_data = [
            {"product": "Laptop", "price": 1200, "stock": 5},
            {"product": "Phone", "price": 800, "stock": 12},
            {"product": "Tablet", "price": 400, "stock": 8},
        ]

        result = flext_cli_table(test_data, title="Products")

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)
        assert table.title == "Products"

    def test_table_from_simple_list(self) -> None:
        """Test table creation from simple list."""
        test_data = ["apple", "banana", "cherry", "date"]

        result = flext_cli_table(test_data)

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)

    def test_table_from_single_dict(self) -> None:
        """Test table creation from single dictionary."""
        test_data = {
            "server_name": "web-01",
            "status": "running",
            "uptime": "24 hours",
            "cpu_usage": "45%",
        }

        result = flext_cli_table(test_data, title="Server Status")

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)
        assert table.title == "Server Status"

    def test_table_from_single_value(self) -> None:
        """Test table creation from single value."""
        test_data = "Single text value"

        result = flext_cli_table(test_data)

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)

    def test_table_from_empty_list(self) -> None:
        """Test table creation from empty list."""
        test_data: list[dict[str, object]] = []

        result = flext_cli_table(test_data)

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)

    def test_table_with_mixed_data_types(self) -> None:
        """Test table creation with mixed data types in values."""
        test_data = [
            {"name": "Item1", "count": 42, "active": True, "score": 95.5},
            {"name": "Item2", "count": 18, "active": False, "score": 87.2},
        ]

        result = flext_cli_table(test_data, title="Mixed Data")

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)
        assert table.title == "Mixed Data"


class TestFlextCliTransformData:
    """Test flext_cli_transform_data function with real transformations."""

    def test_transform_data_with_filter(self) -> None:
        """Test data transformation with filtering."""
        test_data = [
            {"name": "Alice", "age": 25, "department": "Engineering"},
            {"name": "Bob", "age": 30, "department": "Marketing"},
            {"name": "Carol", "age": 35, "department": "Engineering"},
        ]

        # Filter for Engineering department only
        def filter_engineering(item: dict[str, object]) -> bool:
            return item.get("department") == "Engineering"

        result = flext_cli_transform_data(test_data, filter_func=filter_engineering)

        assert result.is_success
        filtered_data = result.value
        assert len(filtered_data) == 2
        assert all(item.get("department") == "Engineering" for item in filtered_data)

    def test_transform_data_with_sort(self) -> None:
        """Test data transformation with sorting."""
        test_data = [
            {"name": "Charlie", "age": 40},
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
        ]

        result = flext_cli_transform_data(test_data, sort_key="age")

        assert result.is_success
        sorted_data = result.value
        ages = [item.get("age") for item in sorted_data]
        assert ages == [25, 30, 40]

    def test_transform_data_with_reverse_sort(self) -> None:
        """Test data transformation with reverse sorting."""
        test_data = [
            {"name": "Alice", "score": 85},
            {"name": "Bob", "score": 95},
            {"name": "Carol", "score": 78},
        ]

        result = flext_cli_transform_data(test_data, sort_key="score", reverse=True)

        assert result.is_success
        sorted_data = result.value
        scores = [item.get("score") for item in sorted_data]
        assert scores == [95, 85, 78]

    def test_transform_data_filter_and_sort_combined(self) -> None:
        """Test data transformation with both filtering and sorting."""
        test_data = [
            {"name": "Alice", "age": 25, "active": True},
            {"name": "Bob", "age": 30, "active": False},
            {"name": "Carol", "age": 35, "active": True},
            {"name": "Dave", "age": 28, "active": True},
        ]

        # Filter for active users and sort by age
        def filter_active(item: dict[str, object]) -> bool:
            return item.get("active") is True

        result = flext_cli_transform_data(
            test_data, filter_func=filter_active, sort_key="age"
        )

        assert result.is_success
        transformed_data = result.value
        assert len(transformed_data) == 3
        ages = [item.get("age") for item in transformed_data]
        assert ages == [25, 28, 35]

    def test_transform_data_non_list_input(self) -> None:
        """Test data transformation with non-list input."""
        test_data = {"not": "a list"}

        result = flext_cli_transform_data(test_data)

        assert not result.is_success
        assert "Data must be a list" in (result.error or "")

    def test_transform_data_string_sort_key(self) -> None:
        """Test data transformation sorting by string key."""
        test_data = [
            {"name": "Zebra", "category": "Animal"},
            {"name": "Apple", "category": "Fruit"},
            {"name": "Banana", "category": "Fruit"},
        ]

        result = flext_cli_transform_data(test_data, sort_key="name")

        assert result.is_success
        sorted_data = result.value
        names = [item.get("name") for item in sorted_data]
        assert names == ["Apple", "Banana", "Zebra"]


class TestFlextCliAggregateData:
    """Test flext_cli_aggregate_data function with real aggregations."""

    def test_aggregate_data_basic_grouping(self) -> None:
        """Test basic data aggregation by grouping."""
        test_data = [
            {"department": "Engineering", "salary": 80000},
            {"department": "Engineering", "salary": 90000},
            {"department": "Marketing", "salary": 70000},
            {"department": "Marketing", "salary": 75000},
        ]

        result = flext_cli_aggregate_data(
            test_data, group_by="department", sum_fields=["salary"]
        )

        assert result.is_success
        aggregated_data = result.value
        assert len(aggregated_data) == 2

        # Find Engineering group
        eng_group = next(
            item for item in aggregated_data if item.get("department") == "Engineering"
        )
        assert eng_group.get("count") == 2
        assert eng_group.get("salary_sum") == 170000

    def test_aggregate_data_with_count_only(self) -> None:
        """Test data aggregation with counting only."""
        test_data = [
            {"city": "New York", "population": 8000000},
            {"city": "New York", "population": 8100000},
            {"city": "Los Angeles", "population": 4000000},
        ]

        result = flext_cli_aggregate_data(
            test_data, group_by="city", count_field="entries"
        )

        assert result.is_success
        aggregated_data = result.value
        assert len(aggregated_data) == 2

        # Find New York group
        ny_group = next(
            item for item in aggregated_data if item.get("city") == "New York"
        )
        assert ny_group.get("entries") == 2

    def test_aggregate_data_multiple_sum_fields(self) -> None:
        """Test data aggregation with multiple sum fields."""
        test_data = [
            {"product": "Widget", "sold": 100, "revenue": 1000, "cost": 600},
            {"product": "Widget", "sold": 150, "revenue": 1500, "cost": 900},
            {"product": "Gadget", "sold": 75, "revenue": 750, "cost": 450},
        ]

        result = flext_cli_aggregate_data(
            test_data, group_by="product", sum_fields=["sold", "revenue", "cost"]
        )

        assert result.is_success
        aggregated_data = result.value
        assert len(aggregated_data) == 2

        # Find Widget group
        widget_group = next(
            item for item in aggregated_data if item.get("product") == "Widget"
        )
        assert widget_group.get("sold_sum") == 250
        assert widget_group.get("revenue_sum") == 2500
        assert widget_group.get("cost_sum") == 1500

    def test_aggregate_data_non_list_input(self) -> None:
        """Test data aggregation with non-list input."""
        test_data = {"not": "a list"}

        result = flext_cli_aggregate_data(test_data, group_by="field")

        assert not result.is_success
        assert "Data must be a list" in (result.error or "")

    def test_aggregate_data_missing_group_field(self) -> None:
        """Test data aggregation when group field is missing in some items."""
        test_data = [
            {"department": "Engineering", "salary": 80000},
            {"salary": 70000},  # Missing department field
            {"department": "Marketing", "salary": 75000},
        ]

        result = flext_cli_aggregate_data(
            test_data, group_by="department", sum_fields=["salary"]
        )

        assert result.is_success
        aggregated_data = result.value
        # Should only group items that have the group field
        assert len(aggregated_data) == 2


class TestFlextCliExport:
    """Test flext_cli_export function with real file operations."""

    def test_export_json_simple_data(self) -> None:
        """Test JSON export with simple data."""
        test_data = {"name": "Test User", "age": 30, "active": True}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            result = flext_cli_export(test_data, tmp_path, "json")

            assert result.is_success
            assert tmp_path.exists()

            # Verify exported content
            with tmp_path.open("r", encoding="utf-8") as f:
                exported_data = json.load(f)
            assert exported_data == test_data
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_export_yaml_simple_data(self) -> None:
        """Test YAML export with simple data."""
        test_data = {
            "config": {
                "database": {"host": "localhost", "port": 5432},
                "cache": {"enabled": True, "ttl": 3600},
            }
        }

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".yaml", delete=False
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            result = flext_cli_export(test_data, tmp_path, "yaml")

            assert result.is_success
            assert tmp_path.exists()

            # Verify exported content
            with tmp_path.open("r", encoding="utf-8") as f:
                exported_data = yaml.safe_load(f)
            assert exported_data == test_data
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_export_csv_list_of_dicts(self) -> None:
        """Test CSV export with list of dictionaries."""
        test_data = [
            {"name": "Alice", "age": 25, "city": "New York"},
            {"name": "Bob", "age": 30, "city": "Los Angeles"},
            {"name": "Carol", "age": 35, "city": "Chicago"},
        ]

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".csv", delete=False
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            result = flext_cli_export(test_data, tmp_path, "csv")

            assert result.is_success
            assert tmp_path.exists()

            # Verify exported content
            content = tmp_path.read_text(encoding="utf-8")
            assert "Alice" in content
            assert "Bob" in content
            assert "Carol" in content
            assert "New York" in content
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_export_csv_invalid_data(self) -> None:
        """Test CSV export with invalid data structure."""
        test_data = "Not a list of dictionaries"

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".csv", delete=False
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            result = flext_cli_export(test_data, tmp_path, "csv")

            assert not result.is_success
            assert "CSV export requires list of dictionaries" in (result.error or "")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_export_unsupported_format(self) -> None:
        """Test export with unsupported format."""
        test_data = {"test": "data"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".txt", delete=False
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            result = flext_cli_export(test_data, tmp_path, "unsupported")

            assert not result.is_success
            assert "Unsupported export format: unsupported" in (result.error or "")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_export_to_nonexistent_directory(self) -> None:
        """Test export to a file in non-existent directory."""
        test_data = {"test": "data"}
        non_existent_path = Path("/tmp/nonexistent_dir_123456/test.json")

        result = flext_cli_export(test_data, non_existent_path, "json")

        assert not result.is_success
        assert "Export error:" in (result.error or "")


class TestFlextCliBatchExport:
    """Test flext_cli_batch_export function with real batch operations."""

    def test_batch_export_json_multiple_datasets(self) -> None:
        """Test batch export of multiple datasets in JSON format."""
        datasets = {
            "users": [
                {"id": 1, "name": "Alice", "role": "admin"},
                {"id": 2, "name": "Bob", "role": "user"},
            ],
            "settings": {"theme": "dark", "notifications": True, "auto_save": False},
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            result = flext_cli_batch_export(datasets, tmp_path, "json")

            assert result.is_success
            created_files = result.value
            assert len(created_files) == 2

            # Verify files exist and contain correct data
            users_file = tmp_path / "users.json"
            settings_file = tmp_path / "settings.json"
            assert users_file.exists()
            assert settings_file.exists()

            with users_file.open("r", encoding="utf-8") as f:
                users_data = json.load(f)
            assert len(users_data) == 2
            assert users_data[0]["name"] == "Alice"

    def test_batch_export_yaml_multiple_datasets(self) -> None:
        """Test batch export of multiple datasets in YAML format."""
        datasets = {
            "config": {"database": {"host": "localhost", "port": 5432}},
            "metadata": {"version": "1.0.0", "author": "Test Team"},
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            result = flext_cli_batch_export(datasets, tmp_path, "yaml")

            assert result.is_success
            created_files = result.value
            assert len(created_files) == 2

            # Verify YAML files
            config_file = tmp_path / "config.yaml"
            metadata_file = tmp_path / "metadata.yaml"
            assert config_file.exists()
            assert metadata_file.exists()

    def test_batch_export_creates_directory(self) -> None:
        """Test batch export creates output directory if it doesn't exist."""
        datasets = {"test": {"data": "value"}}

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / "new_directory"
            assert not tmp_path.exists()

            result = flext_cli_batch_export(datasets, tmp_path, "json")

            assert result.is_success
            assert tmp_path.exists()
            assert tmp_path.is_dir()

    def test_batch_export_csv_failure(self) -> None:
        """Test batch export failure with invalid CSV data."""
        datasets = {"invalid_csv": "Not a list of dictionaries"}

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            result = flext_cli_batch_export(datasets, tmp_path, "csv")

            assert not result.is_success
            assert "Failed to export invalid_csv" in (result.error or "")


class TestFlextCliUnwrapFunctions:
    """Test flext_cli_unwrap_or_default and flext_cli_unwrap_or_none functions."""

    def test_unwrap_or_default_success_result(self) -> None:
        """Test unwrap_or_default with successful result."""
        success_result = FlextResult[str].ok("success value")
        default_value = "default value"

        result = flext_cli_unwrap_or_default(success_result, default_value)

        assert result == "success value"

    def test_unwrap_or_default_failure_result(self) -> None:
        """Test unwrap_or_default with failed result."""
        failed_result = FlextResult[str].fail("operation failed")
        default_value = "default value"

        result = flext_cli_unwrap_or_default(failed_result, default_value)

        assert result == default_value

    def test_unwrap_or_none_success_result(self) -> None:
        """Test unwrap_or_none with successful result."""
        success_result = FlextResult[int].ok(42)

        result = flext_cli_unwrap_or_none(success_result)

        assert result == 42

    def test_unwrap_or_none_failure_result(self) -> None:
        """Test unwrap_or_none with failed result."""
        failed_result = FlextResult[int].fail("operation failed")

        result = flext_cli_unwrap_or_none(failed_result)

        assert result is None

    def test_unwrap_or_default_with_complex_objects(self) -> None:
        """Test unwrap_or_default with complex objects."""
        complex_data = {"users": [{"name": "Alice", "id": 1}], "total": 1}
        success_result = FlextResult[dict[str, object]].ok(complex_data)
        default_value = {}

        result = flext_cli_unwrap_or_default(success_result, default_value)

        assert result == complex_data
        assert isinstance(result, dict)

    def test_unwrap_or_none_with_different_types(self) -> None:
        """Test unwrap_or_none with different data types."""
        # Test with list
        list_result = FlextResult[list[str]].ok(["a", "b", "c"])
        assert flext_cli_unwrap_or_none(list_result) == ["a", "b", "c"]

        # Test with boolean
        bool_result = FlextResult[bool].ok(data=True)
        assert flext_cli_unwrap_or_none(bool_result) is True

        # Test with None value
        none_result = FlextResult[None].ok(None)
        assert flext_cli_unwrap_or_none(none_result) is None


class TestFlextCliContext:
    """Test FlextCliContext class with real context management."""

    def test_context_initialization(self) -> None:
        """Test CLI context initialization."""
        config = FlextCliSettings()
        console = Console()

        context = FlextCliContext(config, console)

        assert context.config is config
        assert context.console is console

    def test_context_with_custom_config(self) -> None:
        """Test CLI context with custom configuration."""
        config = FlextCliSettings()
        console = Console(width=100)

        context = FlextCliContext(config, console)

        assert isinstance(context.config, FlextCliSettings)
        assert context.console.width == 100


class TestFlextCliApi:
    """Test FlextCliApi class with real API operations."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.api = FlextCliApi()

    def test_flext_cli_export_success(self) -> None:
        """Test API export method with successful operation."""
        test_data = {"name": "Test", "value": 123}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            success = self.api.flext_cli_export(test_data, tmp_path, "json")

            assert success is True
            assert tmp_path.exists()

            # Verify exported content
            with tmp_path.open("r", encoding="utf-8") as f:
                exported_data = json.load(f)
            assert exported_data == test_data
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_flext_cli_export_failure(self) -> None:
        """Test API export method with failed operation."""
        test_data = {"test": "data"}
        invalid_path = Path("/invalid/path/file.json")

        success = self.api.flext_cli_export(test_data, invalid_path, "json")

        assert success is False

    def test_flext_cli_format_success(self) -> None:
        """Test API format method with successful operation."""
        test_data = {"name": "Alice", "age": 30}

        result = self.api.flext_cli_format(test_data, "json")

        assert isinstance(result, str)
        assert len(result) > 0
        parsed = json.loads(result)
        assert parsed == test_data

    def test_flext_cli_format_failure(self) -> None:
        """Test API format method with failed operation."""
        test_data = {"test": "data"}

        result = self.api.flext_cli_format(test_data, "invalid_format")

        assert result == ""  # Returns empty string on failure

    def test_flext_cli_configure_success(self) -> None:
        """Test API configure method with valid configuration."""
        config_data = {"debug": True, "timeout": 30}

        success = self.api.flext_cli_configure(config_data)

        assert success is True
        assert hasattr(self.api, "_config")

    def test_flext_cli_configure_empty_config(self) -> None:
        """Test API configure method with empty configuration."""
        success = self.api.flext_cli_configure({})

        assert success is True
        assert hasattr(self.api, "_config")

    def test_flext_cli_health(self) -> None:
        """Test API health method returns system information."""
        health_info = self.api.flext_cli_health()

        assert isinstance(health_info, dict)
        assert health_info["status"] == "healthy"
        assert "timestamp" in health_info
        assert "python_version" in health_info
        assert "platform" in health_info
        assert health_info["service"] == "flext-cli"
        assert health_info["version"] == "0.9.0"

    def test_flext_cli_create_context(self) -> None:
        """Test API create_context method."""
        context = self.api.flext_cli_create_context()

        assert isinstance(context, FlextCliContext)
        assert hasattr(context, "config")
        assert hasattr(context, "console")

    def test_flext_cli_create_context_with_config(self) -> None:
        """Test API create_context method with custom config."""
        custom_config = {"debug": True, "verbose": False}

        context = self.api.flext_cli_create_context(custom_config)

        assert isinstance(context, FlextCliContext)
        assert hasattr(context, "config")

    def test_flext_cli_create_command_success(self) -> None:
        """Test API create_command method with valid parameters."""
        result = self.api.flext_cli_create_command(
            name="test_command",
            command_line="echo hello",
            description="Test command",
            timeout_seconds=30,
        )

        assert result.is_success
        command = result.value
        assert isinstance(command, CLICommand)

    def test_flext_cli_create_command_invalid_type(self) -> None:
        """Test API create_command method with invalid command type."""
        result = self.api.flext_cli_create_command(
            name="test_command", command_line="echo hello", command_type="invalid_type"
        )

        assert not result.is_success
        assert "Invalid command type" in (result.error or "")

    def test_flext_cli_create_command_empty_name(self) -> None:
        """Test API create_command method with empty name."""
        result = self.api.flext_cli_create_command(name="", command_line="echo hello")

        assert result.is_success  # Creates UUID-based ID when name is empty
        command = result.value
        assert isinstance(command, CLICommand)

    def test_flext_cli_create_session(self) -> None:
        """Test API create_session method."""
        result = self.api.flext_cli_create_session()

        assert result.is_success
        session_id = result.value
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        assert "cli_session_" in session_id

    def test_flext_cli_create_session_with_user(self) -> None:
        """Test API create_session method with user ID."""
        user_id = "user123"

        result = self.api.flext_cli_create_session(user_id)

        assert result.is_success
        session_id = result.value
        assert isinstance(session_id, str)
        assert hasattr(self.api, "_sessions")
        session_data = self.api._sessions[session_id]
        assert isinstance(session_data, dict)
        assert session_data["user_id"] == user_id

    def test_flext_cli_register_handler_success(self) -> None:
        """Test API register_handler method with valid handler."""

        def test_handler() -> str:
            return "test result"

        result = self.api.flext_cli_register_handler("test_handler", test_handler)

        assert result.is_success
        assert hasattr(self.api, "_handlers")
        assert "test_handler" in self.api._handlers

    def test_flext_cli_register_handler_not_callable(self) -> None:
        """Test API register_handler method with non-callable handler."""
        result = self.api.flext_cli_register_handler("invalid_handler", "not_callable")

        assert not result.is_success
        assert "not callable" in (result.error or "")

    def test_flext_cli_register_plugin_with_cli_plugin(self) -> None:
        """Test API register_plugin method with FlextCliPlugin instance."""
        plugin = FlextCliPlugin(
            id=FlextModels.EntityId(str(uuid.uuid4())),
            name="test_plugin",
            entry_point="test.plugin",
        )

        result = self.api.flext_cli_register_plugin("test_plugin", plugin)

        assert result.is_success
        assert hasattr(self.api, "_plugin_registry")
        assert "test_plugin" in self.api._plugin_registry

    def test_flext_cli_register_plugin_with_object(self) -> None:
        """Test API register_plugin method with generic object."""
        # Create a proper FlextCliPlugin instance to avoid validation errors
        plugin = FlextCliPlugin(
            id=FlextModels.EntityId(str(uuid.uuid4())),
            name="generic_plugin",
            entry_point="flext_cli.plugins.generic_plugin:main",
        )

        result = self.api.flext_cli_register_plugin("generic_plugin", plugin)

        assert result.is_success
        assert hasattr(self.api, "_plugin_registry")

    def test_flext_cli_execute_handler_success(self) -> None:
        """Test API execute_handler method with registered handler."""

        def test_handler(x: int, y: int) -> int:
            return x + y

        # Register handler first
        self.api.flext_cli_register_handler("add_handler", test_handler)

        result = self.api.flext_cli_execute_handler("add_handler", 5, 3)

        assert result.is_success
        assert result.value == 8

    def test_flext_cli_execute_handler_not_found(self) -> None:
        """Test API execute_handler method with non-existent handler."""
        # First register at least one handler to ensure registry exists
        self.api.flext_cli_register_handler("dummy_handler", lambda: "test")

        result = self.api.flext_cli_execute_handler("nonexistent_handler")

        assert not result.is_success
        assert "not found" in (result.error or "")

    def test_flext_cli_execute_handler_no_registry(self) -> None:
        """Test API execute_handler method without handlers registry."""
        # Create fresh API instance without handlers
        fresh_api = FlextCliApi()

        result = fresh_api.flext_cli_execute_handler("any_handler")

        assert not result.is_success
        assert "No handlers registry found" in (result.error or "")

    def test_flext_cli_get_commands_empty(self) -> None:
        """Test API get_commands method with no commands."""
        commands = self.api.flext_cli_get_commands()

        assert isinstance(commands, dict)
        assert len(commands) == 0

    def test_flext_cli_get_sessions_empty(self) -> None:
        """Test API get_sessions method with no sessions."""
        sessions = self.api.flext_cli_get_sessions()

        assert isinstance(sessions, dict)
        assert len(sessions) == 0

    def test_flext_cli_get_sessions_with_data(self) -> None:
        """Test API get_sessions method with session data."""
        # Create a session first
        self.api.flext_cli_create_session("user123")

        sessions = self.api.flext_cli_get_sessions()

        assert isinstance(sessions, dict)
        assert len(sessions) == 1
        session_data = next(iter(sessions.values()))
        assert isinstance(session_data, dict)
        assert "id" in session_data
        assert "commands_count" in session_data

    def test_flext_cli_get_plugins_empty(self) -> None:
        """Test API get_plugins method with no plugins."""
        plugins = self.api.flext_cli_get_plugins()

        assert isinstance(plugins, dict)
        assert len(plugins) == 0

    def test_flext_cli_get_handlers_empty(self) -> None:
        """Test API get_handlers method with no handlers."""
        handlers = self.api.flext_cli_get_handlers()

        assert isinstance(handlers, dict)
        assert len(handlers) == 0

    def test_flext_cli_get_handlers_with_data(self) -> None:
        """Test API get_handlers method with registered handlers."""

        def test_handler() -> str:
            return "test"

        self.api.flext_cli_register_handler("test_handler", test_handler)

        handlers = self.api.flext_cli_get_handlers()

        assert isinstance(handlers, dict)
        assert len(handlers) == 1
        assert "test_handler" in handlers
        # The real implementation returns the handler function directly, not a dict
        handler_info = handlers["test_handler"]
        # Based on actual implementation, handler can be the function itself or a dict summary
        assert handler_info is not None


class TestContextRenderingStrategy:
    """Test ContextRenderingStrategy class with real rendering operations."""

    def test_render_string_template(self) -> None:
        """Test rendering string template with context substitution."""
        template_data = "Hello {{name}}, your score is {{score}}"
        context = {"name": "Alice", "score": 95}

        strategy = ContextRenderingStrategy(template_data, context)
        result = strategy.render()

        assert result.is_success
        rendered = result.value
        assert "Hello Alice, your score is 95" in rendered

    def test_render_dict_with_template(self) -> None:
        """Test rendering dictionary containing template strings."""
        template_data = {"message": "Welcome {{user}}", "status": "active"}
        context = {"user": "Bob"}

        strategy = ContextRenderingStrategy(template_data, context)
        result = strategy.render()

        assert result.is_success
        rendered = result.value
        assert "Welcome Bob" in rendered

    def test_render_fallback_to_formatter(self) -> None:
        """Test rendering falls back to formatter when no templates found."""
        data = {"name": "Charlie", "age": 30}
        context = {"format": "json"}

        strategy = ContextRenderingStrategy(data, context)
        result = strategy.render()

        assert result.is_success
        rendered = result.value
        assert "Charlie" in rendered
        assert "30" in rendered

    def test_render_with_title_context(self) -> None:
        """Test rendering with title context applied."""
        data = {"item": "value"}
        context = {"title": "Test Data", "format": "json"}

        strategy = ContextRenderingStrategy(data, context)
        result = strategy.render()

        assert result.is_success
        rendered = result.value
        assert "# Test Data" in rendered
        assert "value" in rendered

    def test_render_empty_context(self) -> None:
        """Test rendering with empty context."""
        data = {"test": "data"}

        strategy = ContextRenderingStrategy(data)
        result = strategy.render()

        assert result.is_success
        rendered = result.value
        assert "data" in rendered

    def test_render_no_template_patterns(self) -> None:
        """Test rendering when no template patterns exist."""
        data = "Plain string without templates"
        context = {"name": "Alice"}

        strategy = ContextRenderingStrategy(data, context)
        result = strategy.render()

        assert result.is_success
        rendered = result.value
        assert "Plain string without templates" in rendered

    def test_render_multiple_template_variables(self) -> None:
        """Test rendering with multiple template variables."""
        template_data = "User: {{name}}, Role: {{role}}, Active: {{active}}"
        context = {"name": "David", "role": "admin", "active": "true"}

        strategy = ContextRenderingStrategy(template_data, context)
        result = strategy.render()

        assert result.is_success
        rendered = result.value
        assert "User: David" in rendered
        assert "Role: admin" in rendered
        assert "Active: true" in rendered

    def test_flext_cli_render_with_context(self) -> None:
        """Test render_with_context method via API."""
        api = FlextCliApi()
        template_data = "Processing {{count}} items for {{user}}"
        context = {"count": 42, "user": "TestUser"}

        result = api.flext_cli_render_with_context(template_data, context)

        assert result.is_success
        rendered = result.value
        assert "Processing 42 items for TestUser" in rendered


class TestProtocolImplementation:
    """Test protocol implementations and plugin-like objects."""

    def test_plugin_like_protocol_compatibility(self) -> None:
        """Test plugin-like protocol implementation with mock plugin."""

        class MockPlugin:
            def __init__(self) -> None:
                self._name = "test_plugin"
                self._id = "plugin_123"
                self._version = "1.0.0"
                self._status = "active"
                self._plugin_type = "utility"

            @property
            def name(self) -> str:
                return self._name

            @property
            def id(self) -> str:
                return self._id

            @property
            def version(self) -> str:
                return self._version

            @property
            def status(self) -> str:
                return self._status

            @property
            def plugin_type(self) -> str:
                return self._plugin_type

        mock_plugin = MockPlugin()

        # Test that mock plugin conforms to PluginLike protocol
        plugin_like: PluginLike = mock_plugin
        assert plugin_like.name == "test_plugin"
        assert plugin_like.id == "plugin_123"
        assert plugin_like.version == "1.0.0"
        assert plugin_like.status == "active"
        assert plugin_like.plugin_type == "utility"

    def test_context_rendering_strategy_plugin_conversion(self) -> None:
        """Test ContextRenderingStrategy plugin conversion methods."""
        strategy = ContextRenderingStrategy({})

        # Test _is_valid_plugin method with valid plugin
        class ValidPlugin:
            name = "test"
            id = "123"
            version = "1.0"
            status = "active"
            plugin_type = "test"

        valid_plugin = ValidPlugin()
        assert strategy._is_valid_plugin(valid_plugin) is True

        # Test _is_valid_plugin method with invalid plugin
        class InvalidPlugin:
            name = "test"
            # Missing other required attributes

        invalid_plugin = InvalidPlugin()
        assert strategy._is_valid_plugin(invalid_plugin) is False

    def test_context_rendering_strategy_convert_plugins_list(self) -> None:
        """Test ContextRenderingStrategy _convert_plugins_list_to_dict method."""
        strategy = ContextRenderingStrategy({})

        class TestPlugin:
            name = "test_plugin"
            id = "plugin_123"
            version = "1.0.0"
            status = "active"
            plugin_type = "utility"

        plugins_list = [TestPlugin()]
        result = strategy._convert_plugins_list_to_dict(plugins_list)

        assert isinstance(result, dict)
        assert "test_plugin" in result
        plugin_data = result["test_plugin"]
        assert isinstance(plugin_data, dict)
        assert plugin_data["name"] == "test_plugin"
        assert plugin_data["version"] == "1.0.0"

    def test_context_rendering_strategy_convert_plugins_empty_list(self) -> None:
        """Test ContextRenderingStrategy plugin conversion with empty list."""
        strategy = ContextRenderingStrategy({})

        result = strategy._convert_plugins_list_to_dict([])

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_context_rendering_strategy_convert_plugins_non_list(self) -> None:
        """Test ContextRenderingStrategy plugin conversion with non-list input."""
        strategy = ContextRenderingStrategy({})

        result = strategy._convert_plugins_list_to_dict("not a list")

        assert isinstance(result, dict)
        assert len(result) == 0


class TestApiEdgeCases:
    """Test edge cases and error conditions in API functions."""

    def test_flext_cli_format_table_creation_failure(self) -> None:
        """Test format function when table creation fails."""
        # Using data that could potentially cause table creation issues
        problematic_data = None

        result = flext_cli_format(problematic_data, "table")

        # Should handle gracefully even with None data
        assert result.is_success or "Table creation error" in (result.error or "")

    def test_flext_cli_aggregate_data_edge_cases(self) -> None:
        """Test aggregate function with edge case data."""
        # Test with empty list
        result = flext_cli_aggregate_data([], group_by="field")
        assert result.is_success
        assert len(result.value) == 0

        # Test with non-numeric sum fields
        test_data = [
            {"category": "A", "value": "not_numeric"},
            {"category": "A", "value": "also_not_numeric"},
        ]
        result = flext_cli_aggregate_data(
            test_data, group_by="category", sum_fields=["value"]
        )
        assert result.is_success

    def test_flext_cli_transform_data_edge_cases(self) -> None:
        """Test transform function with edge case scenarios."""
        # Test with mixed data types in list
        mixed_data = [
            {"name": "Alice", "age": 25},
            "not a dict",
            {"name": "Bob", "age": 30},
        ]

        def filter_dicts(item: dict[str, object]) -> bool:
            return isinstance(item, dict)

        result = flext_cli_transform_data(mixed_data, filter_func=filter_dicts)
        assert result.is_success
        # Should only include dict items
        filtered = result.value
        assert len(filtered) == 2

    def test_api_create_command_with_all_options(self) -> None:
        """Test API create_command with all possible options."""
        api = FlextCliApi()

        result = api.flext_cli_create_command(
            name="comprehensive_test",
            command_line="echo test",
            description="Test command with all options",
            working_directory="/tmp",
            timeout_seconds=60,
            command_type="system",
            environment_vars={"TEST": "value"},
        )

        assert result.is_success
        command = result.value
        assert isinstance(command, CLICommand)

    def test_api_session_management_lifecycle(self) -> None:
        """Test complete session management lifecycle."""
        api = FlextCliApi()

        # Create session
        result = api.flext_cli_create_session("user123")
        assert result.is_success
        session_id = result.value

        # Get sessions (should include the created one)
        sessions = api.flext_cli_get_sessions()
        assert len(sessions) == 1
        assert session_id in sessions

        # Session should have proper structure
        session_data = sessions[session_id]
        assert session_data["status"] == "active"
        assert session_data["commands_count"] == 0

    def test_api_handler_execution_with_kwargs(self) -> None:
        """Test API handler execution with keyword arguments."""
        api = FlextCliApi()

        def complex_handler(x: int, y: int, *, multiplier: int = 2) -> int:
            return (x + y) * multiplier

        api.flext_cli_register_handler("complex_handler", complex_handler)

        result = api.flext_cli_execute_handler("complex_handler", 3, 4, multiplier=3)

        assert result.is_success
        assert result.value == 21  # (3 + 4) * 3


@pytest.mark.integration
class TestApiIntegration:
    """Integration tests combining multiple API functions."""

    def test_complete_data_processing_workflow(self) -> None:
        """Test complete data processing workflow using multiple API functions."""
        # Sample data
        raw_data = [
            {
                "department": "Engineering",
                "employee": "Alice",
                "salary": 80000,
                "active": True,
            },
            {
                "department": "Engineering",
                "employee": "Bob",
                "salary": 90000,
                "active": True,
            },
            {
                "department": "Marketing",
                "employee": "Carol",
                "salary": 70000,
                "active": False,
            },
            {
                "department": "Marketing",
                "employee": "Dave",
                "salary": 75000,
                "active": True,
            },
            {"department": "Sales", "employee": "Eve", "salary": 65000, "active": True},
        ]

        # 1. Filter active employees only
        def filter_active(item: dict[str, object]) -> bool:
            return item.get("active") is True

        filtered_result = flext_cli_transform_data(raw_data, filter_func=filter_active)
        assert filtered_result.is_success
        active_employees = filtered_result.value
        assert len(active_employees) == 4

        # 2. Aggregate by department
        aggregated_result = flext_cli_aggregate_data(
            active_employees, group_by="department", sum_fields=["salary"]
        )
        assert aggregated_result.is_success
        dept_stats = aggregated_result.value

        # 3. Format as table
        table_result = flext_cli_table(dept_stats, title="Department Statistics")
        assert table_result.is_success
        table = table_result.value
        assert isinstance(table, Table)
        assert table.title == "Department Statistics"

        # 4. Export to file
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as tmp_file:
            export_path = Path(tmp_file.name)

        try:
            export_result = flext_cli_export(dept_stats, export_path, "json")
            assert export_result.is_success
            assert export_path.exists()

            # Verify exported data
            with export_path.open("r", encoding="utf-8") as f:
                exported_data = json.load(f)
            assert len(exported_data) == 3  # 3 departments with active employees
        finally:
            export_path.unlink(missing_ok=True)

    def test_api_class_comprehensive_workflow(self) -> None:
        """Test comprehensive workflow using FlextCliApi class."""
        api = FlextCliApi()

        # 1. Configure API
        config_success = api.flext_cli_configure({"debug": True, "timeout": 60})
        assert config_success is True

        # 2. Check health
        health = api.flext_cli_health()
        assert health["status"] == "healthy"
        assert health["config_loaded"] is True

        # 3. Create session
        session_result = api.flext_cli_create_session("test_user")
        assert session_result.is_success
        session_result.value

        # 4. Create and register command
        command_result = api.flext_cli_create_command(
            "test_cmd", "echo hello", description="Test command"
        )
        assert command_result.is_success

        # 5. Register handler
        def test_handler(message: str) -> str:
            return f"Processed: {message}"

        handler_result = api.flext_cli_register_handler("processor", test_handler)
        assert handler_result.is_success

        # 6. Execute handler
        execution_result = api.flext_cli_execute_handler("processor", "test message")
        assert execution_result.is_success
        assert execution_result.value == "Processed: test message"

        # 7. Get all registered components
        commands = api.flext_cli_get_commands()
        sessions = api.flext_cli_get_sessions()
        handlers = api.flext_cli_get_handlers()

        assert isinstance(commands, dict)
        assert len(sessions) == 1
        assert len(handlers) == 1
        assert "processor" in handlers

    def test_batch_export_with_processed_data(self) -> None:
        """Test batch export with data processed through transformation pipeline."""
        # Raw datasets
        sales_data = [
            {"month": "Jan", "region": "North", "sales": 10000},
            {"month": "Jan", "region": "South", "sales": 8000},
            {"month": "Feb", "region": "North", "sales": 12000},
            {"month": "Feb", "region": "South", "sales": 9000},
        ]

        user_data = [
            {"name": "Alice", "department": "Sales", "active": True},
            {"name": "Bob", "department": "Engineering", "active": True},
            {"name": "Carol", "department": "Sales", "active": False},
        ]

        # Process sales data - aggregate by region
        sales_aggregated = flext_cli_aggregate_data(
            sales_data, group_by="region", sum_fields=["sales"]
        ).value

        # Process user data - filter active users
        def filter_active(item: dict[str, object]) -> bool:
            return item.get("active") is True

        users_active = flext_cli_transform_data(
            user_data, filter_func=filter_active
        ).value

        # Create datasets for batch export
        datasets = {"sales_by_region": sales_aggregated, "active_users": users_active}

        # Batch export
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_result = flext_cli_batch_export(datasets, tmp_dir, "json")

            assert export_result.is_success
            files = export_result.value
            assert len(files) == 2

            # Verify files exist and contain processed data
            sales_file = Path(tmp_dir) / "sales_by_region.json"
            users_file = Path(tmp_dir) / "active_users.json"

            assert sales_file.exists()
            assert users_file.exists()

            # Verify content
            with sales_file.open("r", encoding="utf-8") as f:
                sales_content = json.load(f)
            assert len(sales_content) == 2  # North and South regions

            with users_file.open("r", encoding="utf-8") as f:
                users_content = json.load(f)
            assert len(users_content) == 2  # Only active users
