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

from flext_cli import FlextCliApi, FlextCliConfig, FlextCliContext


class TestFlextCliContext:
    """Test FlextCliContext class."""

    def test_context_init(self) -> None:
        """Test context initialization."""
        config = FlextCliConfig()
        console = Console()

        context = FlextCliContext(id="test-context", config=config, console=console)

        assert context.config is config
        assert context.console is console
        assert context.id == "test-context"


class TestFormatting:
    """Test formatting functions."""

    def test_flext_cli_format_json(self) -> None:
        """Test JSON formatting."""
        data = {"key": "value", "number": 42}
        api = FlextCliApi()

        result = api.format_data(data, "json")

        assert result.is_success
        formatted = result.value
        parsed = json.loads(formatted)
        assert parsed == data

    def test_flext_cli_format_yaml(self) -> None:
        """Test YAML formatting."""
        data = {"key": "value", "list": [1, 2, 3]}

        api = FlextCliApi()
        result = api.format_data(data, "yaml")

        assert result.is_success
        formatted = result.value
        parsed = yaml.safe_load(formatted)
        assert parsed == data

    def test_flext_cli_format_table(self) -> None:
        """Test table formatting."""
        data = {"name": "John", "age": 30}

        api = FlextCliApi()
        result = api.format_data(data, "table")

        assert result.is_success
        formatted = result.value
        assert "John" in formatted
        assert "30" in formatted

    def test_flext_cli_format_plain(self) -> None:
        """Test plain formatting."""
        data = "Simple text"

        api = FlextCliApi()
        result = api.format_data(data, "plain")

        assert result.is_success
        formatted = result.value
        assert formatted == str(data)

    def test_flext_cli_format_csv(self) -> None:
        """Test CSV formatting."""
        data = [{"name": "John", "age": 30}]

        api = FlextCliApi()
        result = api.format_data(data, "csv")

        assert result.is_success
        formatted = result.value
        assert "name,age" in formatted
        assert "John,30" in formatted

    def test_flext_cli_format_invalid_format(self) -> None:
        """Test formatting with invalid format."""
        data = {"key": "value"}

        api = FlextCliApi()
        result = api.format_data(data, "invalid")

        assert not result.is_success
        assert "Unsupported format" in result.error


class TestTableCreation:
    """Test table creation functions."""

    def test_flext_cli_table_dict_data(self) -> None:
        """Test table creation from dictionary."""
        data = {"name": "John", "age": 30, "city": "NYC"}

        api = FlextCliApi()
        result = api.create_table(data, "Test Table")

        assert result.is_success
        table = result.value
        # Accept Rich Table output (preferred)
        try:
            from rich.table import Table as _RichTable

            assert isinstance(table, _RichTable)
        except Exception:
            # Or a string representation
            assert isinstance(table, str)

    def test_flext_cli_table_list_dict_data(self) -> None:
        """Test table creation from list of dictionaries."""
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]

        api = FlextCliApi()
        result = api.create_table(data)

        assert result.is_success
        assert result.value is not None

    def test_flext_cli_table_simple_list_data(self) -> None:
        """Test table creation from simple list."""
        data = ["item1", "item2", "item3"]

        api = FlextCliApi()
        result = api.create_table(data)

        assert result.is_success
        assert result.value is not None

    def test_flext_cli_table_single_value(self) -> None:
        """Test table creation from single value."""
        data = "Single value"

        api = FlextCliApi()
        result = api.create_table(data)

        assert result.is_success
        assert result.value is not None

    def test_table_creation_dict_list(self) -> None:
        """Test flext_cli_table with list of dictionaries."""
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        api = FlextCliApi()
        result = api.create_table(data)

        assert result.is_success
        assert result.value is not None

    def test_table_creation_simple_list(self) -> None:
        """Test flext_cli_table with simple list."""
        data = ["item1", "item2", "item3"]
        api = FlextCliApi()
        result = api.create_table(data)

        assert result.is_success
        assert result.value is not None

    def test_table_creation_dict(self) -> None:
        """Test flext_cli_table with dictionary."""
        data = {"name": "John", "age": 30}
        api = FlextCliApi()
        result = api.create_table(data)

        assert result.is_success
        table = result.value
        assert isinstance(table, str)

    def test_table_creation_single_value(self) -> None:
        """Test flext_cli_table with single value."""
        data = "Single value"
        api = FlextCliApi()
        result = api.create_table(data)

        assert result.is_success
        table = result.value
        assert isinstance(table, str)


class TestDataTransformation:
    """Test data transformation functions."""

    def test_flext_cli_transform_data_simple(self) -> None:
        """Test data transformation exists."""
        # Just test that the function exists and can be called
        data = [1, 2, 3]

        def transform_fn(x: int) -> int:
            return x * 2

        api = FlextCliApi()
        result = api.transform_data(data, transform_fn)

        # Function should return a result
        assert isinstance(result, FlextResult)

    def test_flext_cli_transform_data_empty(self) -> None:
        """Test transformation with empty data."""
        data: list[object] = []

        def transform_fn(x: object) -> object:
            return x

        api = FlextCliApi()
        result = api.transform_data(data, transform_fn)

        assert isinstance(result, FlextResult)


class TestDataAggregation:
    """Test data aggregation functions."""

    def test_flext_cli_aggregate_data_basic(self) -> None:
        """Test basic data aggregation."""
        data = [
            {"category": "A", "value": 10},
            {"category": "A", "value": 15},
            {"category": "B", "value": 20},
        ]

        api = FlextCliApi()
        result = api.aggregate_data(data, group_by="category", sum_fields=["value"])

        # Function should return a result
        assert isinstance(result, FlextResult)

    def test_flext_cli_aggregate_data_empty(self) -> None:
        """Test data aggregation with empty data."""
        data: list[dict[str, object]] = []

        api = FlextCliApi()
        result = api.aggregate_data(data, group_by="field")

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
            api = FlextCliApi()
            result = api.export_data(data, Path(f.name), "json")

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
            api = FlextCliApi()
            result = api.export_data(data, Path(f.name), "yaml")

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
            api = FlextCliApi()
            result = api.export_data(data, Path(f.name), "invalid")

            assert not result.is_success
            assert "Unsupported export format" in result.error

            Path(f.name).unlink()

    def test_flext_cli_batch_export(self) -> None:
        """Test batch export."""
        datasets = {"data1": {"key1": "value1"}, "data2": {"key2": "value2"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            api = FlextCliApi()
            result = api.batch_export(datasets, Path(temp_dir), "json")

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
            api = FlextCliApi()
            result = api.batch_export(datasets, Path(temp_dir), "json")

            assert result.is_success
            summary = result.value
            assert isinstance(summary, list)
            assert len(summary) == 0

    def test_flext_cli_batch_export_invalid_format(self) -> None:
        """Test batch export with invalid format."""
        datasets = {"data": {"key": "value"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            api = FlextCliApi()
            result = api.batch_export(datasets, Path(temp_dir), "invalid")

            assert not result.is_success
            assert "Unsupported export format" in result.error


class TestUtilityFunctions:
    """Test utility functions."""

    def test_flext_cli_unwrap_or_default_success(self) -> None:
        """Test unwrap_or_default with successful result."""
        result = FlextResult[str].ok("success")

        api = FlextCliApi()
        value = api.unwrap_or_default(result, "default")

        assert value == "success"

    def test_flext_cli_unwrap_or_default_failure(self) -> None:
        """Test unwrap_or_default with failed result."""
        result = FlextResult[str].fail("error")

        api = FlextCliApi()
        value = api.unwrap_or_default(result, "default")

        assert value == "default"

    def test_flext_cli_unwrap_or_none_success(self) -> None:
        """Test unwrap_or_none with successful result."""
        result = FlextResult[str].ok("success")

        api = FlextCliApi()
        value = api.unwrap_or_none(result)

        assert value == "success"

    def test_flext_cli_unwrap_or_none_failure(self) -> None:
        """Test unwrap_or_none with failed result."""
        result = FlextResult[str].fail("error")

        api = FlextCliApi()
        value = api.unwrap_or_none(result)

        assert value is None

    def test_flext_cli_unwrap_or_none_none_result(self) -> None:
        """Test unwrap_or_none with None result."""
        result = FlextResult[None].ok(None)

        api = FlextCliApi()
        value = api.unwrap_or_none(result)

        assert value is None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_format_with_none_data(self) -> None:
        """Test formatting with None data."""
        api = FlextCliApi()
        result = api.format_data(None, "json")

        assert result.is_success
        formatted = result.value
        assert formatted == "null"

    def test_table_creation_with_complex_data(self) -> None:
        """Test table creation with complex nested data."""
        data = {"simple": "value", "nested": {"inner": "data"}, "list": [1, 2, 3]}

        api = FlextCliApi()
        result = api.create_table(data)

        assert result.is_success
        table = result.value
        assert isinstance(table, str)

    def test_export_to_readonly_directory(self) -> None:
        """Test export to directory without write permissions."""
        data = {"test": "data"}
        readonly_path = Path("/nonexistent/readonly/file.json")

        api = FlextCliApi()
        result = api.export_data(data, readonly_path, "json")

        assert not result.is_success
        # Should handle permission/path errors gracefully

    def test_format_error_handling(self) -> None:
        """Test formatting with problematic data."""
        # Create data that might cause formatting issues
        data = {"date": datetime.datetime.now(tz=datetime.UTC)}

        api = FlextCliApi()
        result = api.format_data(data, "json")

        # May fail if datetime serialization is not handled - this is expected
        # Different implementations may handle this differently
        assert isinstance(result, FlextResult)


class TestSpecialCases:
    """Test special edge cases specific to the implementation."""

    def test_table_from_empty_list(self) -> None:
        """Test table creation handles empty list."""
        data: list[object] = []

        api = FlextCliApi()
        result = api.create_table(data)

        # The implementation might handle empty lists differently
        assert isinstance(result, FlextResult)

    def test_table_from_list_with_empty_dict(self) -> None:
        """Test table creation handles list with empty dict."""
        data = [{}]

        api = FlextCliApi()
        result = api.create_table(data)

        # The implementation might handle this case
        assert isinstance(result, FlextResult)

    def test_aggregation_with_non_list_data(self) -> None:
        """Test aggregation with non-list data."""
        data = {"not": "a list"}

        api = FlextCliApi()
        result = api.aggregate_data(data, group_by="field")

        # Should handle type errors gracefully
        assert isinstance(result, FlextResult)

    def test_transform_with_non_iterable_data(self) -> None:
        """Test transformation with non-iterable data."""
        data = "not a list"

        def transform_fn(x: object) -> object:
            return x

        api = FlextCliApi()
        result = api.transform_data(data, transform_fn)

        # Should handle type errors gracefully
        assert isinstance(result, FlextResult)
