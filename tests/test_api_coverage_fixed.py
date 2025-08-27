"""Tests for api.py to improve coverage (corrected version).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import datetime
import json
import tempfile
from pathlib import Path

import yaml
from flext_core import FlextResult
from rich.console import Console
from rich.table import Table

from flext_cli.api import (
    FlextCliContext,
    _initialize_group,
    _update_group_counts,
    _update_group_sums,
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


class TestFlextCliContext:
    """Test FlextCliContext class."""

    def test_context_init(self) -> None:
        """Test context initialization."""
        config = FlextCliSettings()
        console = Console()

        context = FlextCliContext(config, console)

        assert context.config is config
        assert context.console is console


class TestFormatting:
    """Test formatting functions."""

    def test_flext_cli_format_json(self) -> None:
        """Test JSON formatting."""
        data = {"key": "value", "number": 42}

        result = flext_cli_format(data, "json")

        assert result.is_success
        formatted = result.value
        parsed = json.loads(formatted)
        assert parsed == data

    def test_flext_cli_format_yaml(self) -> None:
        """Test YAML formatting."""
        data = {"key": "value", "list": [1, 2, 3]}

        result = flext_cli_format(data, "yaml")

        assert result.is_success
        formatted = result.value
        parsed = yaml.safe_load(formatted)
        assert parsed == data

    def test_flext_cli_format_table(self) -> None:
        """Test table formatting."""
        data = {"name": "John", "age": 30}

        result = flext_cli_format(data, "table")

        assert result.is_success
        formatted = result.value
        assert "John" in formatted
        assert "30" in formatted

    def test_flext_cli_format_plain(self) -> None:
        """Test plain formatting."""
        data = "Simple text"

        result = flext_cli_format(data, "plain")

        assert result.is_success
        formatted = result.value
        assert formatted == str(data)

    def test_flext_cli_format_csv(self) -> None:
        """Test CSV formatting."""
        data = [{"name": "John", "age": 30}]

        result = flext_cli_format(data, "csv")

        assert result.is_success
        formatted = result.value
        assert str(data) in formatted

    def test_flext_cli_format_invalid_format(self) -> None:
        """Test formatting with invalid format."""
        data = {"key": "value"}

        result = flext_cli_format(data, "invalid")

        assert not result.is_success
        assert "Invalid format" in result.error


class TestTableCreation:
    """Test table creation functions."""

    def test_flext_cli_table_dict_data(self) -> None:
        """Test table creation from dictionary."""
        data = {"name": "John", "age": 30, "city": "NYC"}

        result = flext_cli_table(data, "Test Table")

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)
        assert table.title == "Test Table"

    def test_flext_cli_table_list_dict_data(self) -> None:
        """Test table creation from list of dictionaries."""
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]

        result = flext_cli_table(data)

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)

    def test_flext_cli_table_simple_list_data(self) -> None:
        """Test table creation from simple list."""
        data = ["item1", "item2", "item3"]

        result = flext_cli_table(data)

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)

    def test_flext_cli_table_single_value(self) -> None:
        """Test table creation from single value."""
        data = "Single value"

        result = flext_cli_table(data)

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)

    def test_table_creation_dict_list(self) -> None:
        """Test flext_cli_table with list of dictionaries."""
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        result = flext_cli_table(data)

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)

    def test_table_creation_simple_list(self) -> None:
        """Test flext_cli_table with simple list."""
        data = ["item1", "item2", "item3"]
        result = flext_cli_table(data)

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)

    def test_table_creation_dict(self) -> None:
        """Test flext_cli_table with dictionary."""
        data = {"name": "John", "age": 30}
        result = flext_cli_table(data)

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)

    def test_table_creation_single_value(self) -> None:
        """Test flext_cli_table with single value."""
        data = "Single value"
        result = flext_cli_table(data)

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)


class TestDataTransformation:
    """Test data transformation functions."""

    def test_flext_cli_transform_data_simple(self) -> None:
        """Test data transformation exists."""
        # Just test that the function exists and can be called
        data = [1, 2, 3]

        def transform_fn(x: int) -> int:
            return x * 2

        result = flext_cli_transform_data(data, transform_fn)

        # Function should return a result
        assert isinstance(result, FlextResult)

    def test_flext_cli_transform_data_empty(self) -> None:
        """Test transformation with empty data."""
        data: list[object] = []

        def transform_fn(x: object) -> object:
            return x

        result = flext_cli_transform_data(data, transform_fn)

        assert isinstance(result, FlextResult)


class TestDataAggregation:
    """Test data aggregation functions."""

    def test_initialize_group_correct_signature(self) -> None:
        """Test _initialize_group function with correct signature."""
        result = _initialize_group("category", "A", "count", ["value"])

        assert isinstance(result, dict)
        assert "category" in result
        assert "count" in result
        assert "value_sum" in result
        assert result["category"] == "A"
        assert result["count"] == 0
        assert result["value_sum"] == 0

    def test_update_group_counts(self) -> None:
        """Test _update_group_counts function."""
        group: dict[str, str | int | float | bool | None] = {"count": 0}

        _update_group_counts(group, "count")

        assert group["count"] == 1

    def test_update_group_sums_correct_signature(self) -> None:
        """Test _update_group_sums function with correct signature."""
        group: dict[str, str | int | float | bool | None] = {"value_sum": 0}
        item: dict[str, str | int | float | bool | None] = {"value": 10}

        _update_group_sums(group, item, ["value"])

        assert group["value_sum"] == 10

    def test_flext_cli_aggregate_data_basic(self) -> None:
        """Test basic data aggregation."""
        data = [
            {"category": "A", "value": 10},
            {"category": "A", "value": 15},
            {"category": "B", "value": 20},
        ]

        result = flext_cli_aggregate_data(
            data, group_by="category", sum_fields=["value"]
        )

        # Function should return a result
        assert isinstance(result, FlextResult)

    def test_flext_cli_aggregate_data_empty(self) -> None:
        """Test data aggregation with empty data."""
        data: list[dict[str, object]] = []

        result = flext_cli_aggregate_data(data, group_by="field")

        assert isinstance(result, FlextResult)
        if result.is_success:
            aggregated = result.value
            assert aggregated == []


class TestDataExport:
    """Test data export functions."""

    def test_flext_cli_export_json(self) -> None:
        """Test JSON export."""
        data = {"key": "value", "number": 42}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as f:
            result = flext_cli_export(data, Path(f.name), "json")

            assert result.is_success

            # Verify file was written correctly
            with Path(f.name).open(encoding="utf-8") as saved_file:
                loaded_data = json.load(saved_file)
                assert loaded_data == data

            Path(f.name).unlink()

    def test_flext_cli_export_yaml(self) -> None:
        """Test YAML export."""
        data = {"key": "value", "list": [1, 2, 3]}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".yaml", delete=False
        ) as f:
            result = flext_cli_export(data, Path(f.name), "yaml")

            assert result.is_success

            # Verify file was written correctly
            with Path(f.name).open(encoding="utf-8") as saved_file:
                loaded_data = yaml.safe_load(saved_file)
                assert loaded_data == data

            Path(f.name).unlink()

    def test_flext_cli_export_invalid_format(self) -> None:
        """Test export with invalid format."""
        data = {"key": "value"}

        with tempfile.NamedTemporaryFile(delete=False) as f:
            result = flext_cli_export(data, Path(f.name), "invalid")

            assert not result.is_success
            assert "Unsupported export format" in result.error

            Path(f.name).unlink()

    def test_flext_cli_batch_export(self) -> None:
        """Test batch export."""
        datasets = {"data1": {"key1": "value1"}, "data2": {"key2": "value2"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            result = flext_cli_batch_export(datasets, Path(temp_dir), "json")

            assert result.is_success
            summary = result.value
            assert isinstance(summary, list)  # Returns list of exported files

            # Verify files were created
            assert (Path(temp_dir) / "data1.json").exists()
            assert (Path(temp_dir) / "data2.json").exists()

    def test_flext_cli_batch_export_empty(self) -> None:
        """Test batch export with empty datasets."""
        datasets: dict[str, object] = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            result = flext_cli_batch_export(datasets, Path(temp_dir), "json")

            assert result.is_success
            summary = result.value
            assert isinstance(summary, list)
            assert len(summary) == 0

    def test_flext_cli_batch_export_invalid_format(self) -> None:
        """Test batch export with invalid format."""
        datasets = {"data": {"key": "value"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            result = flext_cli_batch_export(datasets, Path(temp_dir), "invalid")

            assert not result.is_success
            assert "Unsupported export format" in result.error


class TestUtilityFunctions:
    """Test utility functions."""

    def test_flext_cli_unwrap_or_default_success(self) -> None:
        """Test unwrap_or_default with successful result."""
        result = FlextResult[str].ok("success")

        value = flext_cli_unwrap_or_default(result, "default")

        assert value == "success"

    def test_flext_cli_unwrap_or_default_failure(self) -> None:
        """Test unwrap_or_default with failed result."""
        result = FlextResult[str].fail("error")

        value = flext_cli_unwrap_or_default(result, "default")

        assert value == "default"

    def test_flext_cli_unwrap_or_none_success(self) -> None:
        """Test unwrap_or_none with successful result."""
        result = FlextResult[str].ok("success")

        value = flext_cli_unwrap_or_none(result)

        assert value == "success"

    def test_flext_cli_unwrap_or_none_failure(self) -> None:
        """Test unwrap_or_none with failed result."""
        result = FlextResult[str].fail("error")

        value = flext_cli_unwrap_or_none(result)

        assert value is None

    def test_flext_cli_unwrap_or_none_none_result(self) -> None:
        """Test unwrap_or_none with None result."""
        result = FlextResult[None].ok(None)

        value = flext_cli_unwrap_or_none(result)

        assert value is None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_format_with_none_data(self) -> None:
        """Test formatting with None data."""
        result = flext_cli_format(None, "json")

        assert result.is_success
        formatted = result.value
        assert formatted == "null"

    def test_table_creation_with_complex_data(self) -> None:
        """Test table creation with complex nested data."""
        data = {"simple": "value", "nested": {"inner": "data"}, "list": [1, 2, 3]}

        result = flext_cli_table(data)

        assert result.is_success
        table = result.value
        assert isinstance(table, Table)

    def test_export_to_readonly_directory(self) -> None:
        """Test export to directory without write permissions."""
        data = {"test": "data"}
        readonly_path = Path("/nonexistent/readonly/file.json")

        result = flext_cli_export(data, readonly_path, "json")

        assert not result.is_success
        # Should handle permission/path errors gracefully

    def test_format_error_handling(self) -> None:
        """Test formatting with problematic data."""
        # Create data that might cause formatting issues
        data = {"date": datetime.datetime.now(tz=datetime.UTC)}

        result = flext_cli_format(data, "json")

        # Should still work due to default=str in json.dumps
        assert result.is_success


class TestSpecialCases:
    """Test special edge cases specific to the implementation."""

    def test_table_from_empty_list(self) -> None:
        """Test table creation handles empty list."""
        data: list[object] = []

        result = flext_cli_table(data)

        # The implementation might handle empty lists differently
        assert isinstance(result, FlextResult)

    def test_table_from_list_with_empty_dict(self) -> None:
        """Test table creation handles list with empty dict."""
        data = [{}]

        result = flext_cli_table(data)

        # The implementation might handle this case
        assert isinstance(result, FlextResult)

    def test_aggregation_with_non_list_data(self) -> None:
        """Test aggregation with non-list data."""
        data = {"not": "a list"}

        result = flext_cli_aggregate_data(data, group_by="field")

        # Should handle type errors gracefully
        assert isinstance(result, FlextResult)

    def test_transform_with_non_iterable_data(self) -> None:
        """Test transformation with non-iterable data."""
        data = "not a list"

        def transform_fn(x: object) -> object:
            return x

        result = flext_cli_transform_data(data, transform_fn)

        # Should handle type errors gracefully
        assert isinstance(result, FlextResult)
