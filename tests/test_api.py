"""Tests for FLEXT CLI API functions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_cli.api import (
    flext_cli_aggregate_data,
    flext_cli_batch_export,
    flext_cli_export,
    flext_cli_format,
    flext_cli_table,
    flext_cli_transform_data,
    flext_cli_unwrap_or_default,
    flext_cli_unwrap_or_none,
)
from flext_core.result import FlextResult
from rich.table import Table

# Constants
EXPECTED_BULK_SIZE = 2


class TestFlextCliFormat:
    """Test cases for flext_cli_format function."""

    def test_format_list_of_dicts_as_table(self) -> None:
        """Test formatting list of dicts as table."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        result = flext_cli_format(data, "table")
        assert result.is_success
        output = result.unwrap()
        if "Alice" not in output:
            msg = f"Expected {'Alice'} in {output}"
            raise AssertionError(msg)
        assert "Bob" in output

    def test_format_as_json(self) -> None:
        """Test formatting as JSON."""
        data = {"key": "value", "number": 42}
        result = flext_cli_format(data, "json")
        assert result.is_success
        output = result.unwrap()
        if "key" not in output:
            msg = f"Expected {'key'} in {output}"
            raise AssertionError(msg)
        assert "value" in output

    def test_format_invalid_type(self) -> None:
        """Test formatting with invalid format type."""
        data = {"test": "data"}
        result = flext_cli_format(data, "invalid_format")
        assert not result.is_success
        if "Format error" not in result.error:
            msg = f"Expected {'Format error'} in {result.error}"
            raise AssertionError(msg)


class TestFlextCliTable:
    """Test cases for flext_cli_table function."""

    def test_create_table_from_list_of_dicts(self) -> None:
        """Test creating table from list of dictionaries."""
        data = [
            {"name": "Alice", "role": "Engineer"},
            {"name": "Bob", "role": "Designer"},
        ]
        result = flext_cli_table(data, "Team Members")
        assert result.is_success
        table = result.unwrap()
        assert isinstance(table, Table)
        if table.title != "Team Members":
            msg = f"Expected {'Team Members'}, got {table.title}"
            raise AssertionError(msg)

    def test_create_table_from_single_dict(self) -> None:
        """Test creating table from single dictionary."""
        data = {"name": "Alice", "age": 30}
        result = flext_cli_table(data)
        assert result.is_success
        table = result.unwrap()
        assert isinstance(table, Table)

    def test_create_table_from_simple_list(self) -> None:
        """Test creating table from simple list."""
        data = ["item1", "item2", "item3"]
        result = flext_cli_table(data)
        assert result.is_success
        table = result.unwrap()
        assert isinstance(table, Table)

    def test_create_table_from_single_value(self) -> None:
        """Test creating table from single value."""
        data = "single value"
        result = flext_cli_table(data)
        assert result.is_success
        table = result.unwrap()
        assert isinstance(table, Table)


class TestFlextCliTransformData:
    """Test cases for flext_cli_transform_data function."""

    def test_transform_with_filter(self) -> None:
        """Test data transformation with filter."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 20},
            {"name": "Carol", "age": 35},
        ]
        result = flext_cli_transform_data(
            data,
            filter_func=lambda x: x["age"] >= 30,
        )
        assert result.is_success
        filtered_data = result.unwrap()
        if len(filtered_data) != EXPECTED_BULK_SIZE:
            msg = f"Expected {2}, got {len(filtered_data)}"
            raise AssertionError(msg)
        if all(item["age"] < 30 for item in filtered_data):
            msg = f"Expected all ages >= 30, got {[item['age'] for item in filtered_data]}"
            raise AssertionError(msg)

    def test_transform_with_sort(self) -> None:
        """Test data transformation with sorting."""
        data = [
            {"name": "Carol", "age": 35},
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 20},
        ]
        result = flext_cli_transform_data(data, sort_key="age")
        assert result.is_success
        sorted_data = result.unwrap()
        ages = [item["age"] for item in sorted_data]
        if ages != [20, 30, 35]:
            msg = f"Expected {[20, 30, 35]}, got {ages}"
            raise AssertionError(msg)

    def test_transform_with_reverse_sort(self) -> None:
        """Test data transformation with reverse sorting."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 20},
            {"name": "Carol", "age": 35},
        ]
        result = flext_cli_transform_data(data, sort_key="age", reverse=True)
        assert result.is_success
        sorted_data = result.unwrap()
        ages = [item["age"] for item in sorted_data]
        if ages != [35, 30, 20]:
            msg = f"Expected {[35, 30, 20]}, got {ages}"
            raise AssertionError(msg)

    def test_transform_invalid_data_type(self) -> None:
        """Test transformation with invalid data type."""
        result = flext_cli_transform_data("not a list")
        assert not result.is_success
        if "Data must be a list" not in result.error:
            msg = f"Expected {'Data must be a list'} in {result.error}"
            raise AssertionError(msg)


class TestFlextCliAggregateData:
    """Test cases for flext_cli_aggregate_data function."""

    def test_aggregate_with_count(self) -> None:
        """Test data aggregation with count."""
        data = [
            {"department": "Engineering", "salary": 100000},
            {"department": "Engineering", "salary": 110000},
            {"department": "Sales", "salary": 80000},
        ]
        result = flext_cli_aggregate_data(data, group_by="department")
        assert result.is_success
        aggregated = result.unwrap()
        if len(aggregated) != EXPECTED_BULK_SIZE:
            msg = f"Expected {2}, got {len(aggregated)}"
            raise AssertionError(msg)

        # Find Engineering department
        eng_dept = next(
            item for item in aggregated if item["department"] == "Engineering"
        )
        if eng_dept["count"] != EXPECTED_BULK_SIZE:
            msg = f"Expected {2}, got {eng_dept['count']}"
            raise AssertionError(msg)

    def test_aggregate_with_sum_fields(self) -> None:
        """Test data aggregation with sum fields."""
        data = [
            {"department": "Engineering", "salary": 100000, "bonus": 5000},
            {"department": "Engineering", "salary": 110000, "bonus": 6000},
            {"department": "Sales", "salary": 80000, "bonus": 3000},
        ]
        result = flext_cli_aggregate_data(
            data,
            group_by="department",
            sum_fields=["salary", "bonus"],
        )
        assert result.is_success
        aggregated = result.unwrap()

        # Find Engineering department
        eng_dept = next(
            item for item in aggregated if item["department"] == "Engineering"
        )
        if eng_dept["salary_sum"] != 210000:
            msg = f"Expected {210000}, got {eng_dept['salary_sum']}"
            raise AssertionError(msg)
        assert eng_dept["bonus_sum"] == 11000

    def test_aggregate_invalid_data_type(self) -> None:
        """Test aggregation with invalid data type."""
        result = flext_cli_aggregate_data("not a list", group_by="field")
        assert not result.is_success
        if "Data must be a list" not in result.error:
            msg = f"Expected {'Data must be a list'} in {result.error}"
            raise AssertionError(msg)


class TestFlextCliExport:
    """Test cases for flext_cli_export function."""

    def test_export_json(self) -> None:
        """Test exporting data as JSON."""
        data = {"name": "Alice", "age": 30}

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            result = flext_cli_export(data, tmp.name, "json")
            assert result.is_success
            if "Data exported" not in result.unwrap():
                msg = f"Expected {'Data exported'} in {result.unwrap()}"
                raise AssertionError(msg)

            # Verify file exists and has content
            path = Path(tmp.name)
            assert path.exists()
            content = path.read_text(encoding="utf-8")
            if "Alice" not in content:
                msg = f"Expected {'Alice'} in {content}"
                raise AssertionError(msg)
            path.unlink()  # Cleanup

    def test_export_yaml(self) -> None:
        """Test exporting data as YAML."""
        data = {"name": "Bob", "age": 25}

        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
            result = flext_cli_export(data, tmp.name, "yaml")
            assert result.is_success

            # Verify file exists and has content
            path = Path(tmp.name)
            assert path.exists()
            content = path.read_text(encoding="utf-8")
            if "Bob" not in content:
                msg = f"Expected {'Bob'} in {content}"
                raise AssertionError(msg)
            path.unlink()  # Cleanup

    def test_export_csv(self) -> None:
        """Test exporting data as CSV."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            result = flext_cli_export(data, tmp.name, "csv")
            assert result.is_success

            # Verify file exists and has content
            path = Path(tmp.name)
            assert path.exists()
            content = path.read_text(encoding="utf-8")
            if "Alice" not in content:
                msg = f"Expected {'Alice'} in {content}"
                raise AssertionError(msg)
            assert "Bob" in content
            path.unlink()  # Cleanup

    def test_export_csv_invalid_data(self) -> None:
        """Test CSV export with invalid data."""
        result = flext_cli_export("not a list", "test.csv", "csv")
        assert not result.is_success
        if "CSV export requires list of dictionaries" not in result.error:
            msg = f"Expected {'CSV export requires list of dictionaries'} in {result.error}"
            raise AssertionError(msg)

    def test_export_unsupported_format(self) -> None:
        """Test export with unsupported format."""
        data = {"test": "data"}
        result = flext_cli_export(data, "test.txt", "unsupported")
        assert not result.is_success
        if "Unsupported export format" not in result.error:
            msg = f"Expected {'Unsupported export format'} in {result.error}"
            raise AssertionError(msg)


class TestFlextCliBatchExport:
    """Test cases for flext_cli_batch_export function."""

    def test_batch_export_json(self) -> None:
        """Test batch export of multiple datasets."""
        datasets = {
            "users": [{"name": "Alice"}, {"name": "Bob"}],
            "config": {"version": "1.0", "debug": True},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = flext_cli_batch_export(datasets, tmpdir, "json")
            assert result.is_success

            files = result.unwrap()
            if len(files) != EXPECTED_BULK_SIZE:
                msg = f"Expected {2}, got {len(files)}"
                raise AssertionError(msg)

            # Verify files exist
            users_file = Path(tmpdir) / "users.json"
            config_file = Path(tmpdir) / "config.json"
            assert users_file.exists()
            assert config_file.exists()

    def test_batch_export_with_error(self) -> None:
        """Test batch export with one dataset causing error."""
        datasets = {
            "valid": [{"name": "Alice"}],
            "invalid": "not valid for csv",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = flext_cli_batch_export(datasets, tmpdir, "csv")
            assert not result.is_success
            if "Failed to export invalid" not in result.error:
                msg = f"Expected {'Failed to export invalid'} in {result.error}"
                raise AssertionError(msg)


class TestFlextCliUnwrapFunctions:
    """Test cases for unwrap helper functions."""

    def test_unwrap_or_default_success(self) -> None:
        """Test unwrap_or_default with successful result."""
        result = FlextResult.ok("success_value")
        unwrapped = flext_cli_unwrap_or_default(result, "default")
        if unwrapped != "success_value":
            msg = f"Expected {'success_value'}, got {unwrapped}"
            raise AssertionError(msg)

    def test_unwrap_or_default_failure(self) -> None:
        """Test unwrap_or_default with failed result."""
        result = FlextResult.fail("error message")
        unwrapped = flext_cli_unwrap_or_default(result, "default")
        if unwrapped != "default":
            msg = f"Expected {'default'}, got {unwrapped}"
            raise AssertionError(msg)

    def test_unwrap_or_none_success(self) -> None:
        """Test unwrap_or_none with successful result."""
        result = FlextResult.ok("success_value")
        unwrapped = flext_cli_unwrap_or_none(result)
        if unwrapped != "success_value":
            msg = f"Expected {'success_value'}, got {unwrapped}"
            raise AssertionError(msg)

    def test_unwrap_or_none_failure(self) -> None:
        """Test unwrap_or_none with failed result."""
        result = FlextResult.fail("error message")
        unwrapped = flext_cli_unwrap_or_none(result)
        assert unwrapped is None
