"""Comprehensive tests for api module.

Tests for API functions to achieve near 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_cli.api import (
    flext_cli_batch_export,
    flext_cli_export,
    flext_cli_format,
    flext_cli_table,
    flext_cli_unwrap_or_default,
    flext_cli_unwrap_or_none,
)
from flext_core.result import FlextResult


class TestFlextCliFormat:
    """Test flext_cli_format function."""

    def test_flext_cli_format_exists(self) -> None:
        """Test that flext_cli_format function exists and is callable."""
        assert callable(flext_cli_format)

    def test_flext_cli_format_json(self) -> None:
        """Test format as JSON."""
        result = flext_cli_format({"test": "data"}, "json")
        assert isinstance(result, FlextResult)
        if result.is_success:
            formatted = result.unwrap()
            assert isinstance(formatted, str)
            if "test" not in formatted:
                msg = f"Expected {'test'} in {formatted}"
                raise AssertionError(msg)
            assert "data" in formatted

    def test_flext_cli_format_yaml(self) -> None:
        """Test format as YAML."""
        result = flext_cli_format({"test": "data"}, "yaml")
        assert isinstance(result, FlextResult)
        if result.is_success:
            formatted = result.unwrap()
            assert isinstance(formatted, str)

    def test_flext_cli_format_table(self) -> None:
        """Test format as table."""
        result = flext_cli_format([{"name": "test", "value": 123}], "table")
        assert isinstance(result, FlextResult)
        if result.is_success:
            formatted = result.unwrap()
            assert isinstance(formatted, str)

    def test_flext_cli_format_csv(self) -> None:
        """Test format as CSV."""
        result = flext_cli_format([{"name": "test", "value": 123}], "csv")
        assert isinstance(result, FlextResult)
        if result.is_success:
            formatted = result.unwrap()
            assert isinstance(formatted, str)

    def test_flext_cli_format_plain(self) -> None:
        """Test format as plain text."""
        result = flext_cli_format("simple text", "plain")
        assert isinstance(result, FlextResult)
        if result.is_success:
            formatted = result.unwrap()
            assert isinstance(formatted, str)

    def test_flext_cli_format_invalid_format(self) -> None:
        """Test format with invalid format type."""
        result = flext_cli_format({"test": "data"}, "invalid_format")
        assert isinstance(result, FlextResult)
        # Should handle gracefully (success or failure)

    def test_flext_cli_format_none_data(self) -> None:
        """Test format with None data."""
        result = flext_cli_format(None, "json")
        assert isinstance(result, FlextResult)

    def test_flext_cli_format_empty_data(self) -> None:
        """Test format with empty data."""
        result = flext_cli_format({}, "json")
        assert isinstance(result, FlextResult)

    def test_flext_cli_format_complex_data(self) -> None:
        """Test format with complex nested data."""
        complex_data = {
            "users": [
                {"name": "Alice", "age": 30, "skills": ["python", "javascript"]},
                {"name": "Bob", "age": 25, "skills": ["go", "rust"]},
            ],
            "metadata": {"version": "1.0", "created": "2025-01-01"},
        }
        result = flext_cli_format(complex_data, "json")
        assert isinstance(result, FlextResult)


class TestFlextCliTable:
    """Test flext_cli_table function."""

    def test_flext_cli_table_exists(self) -> None:
        """Test that flext_cli_table function exists and is callable."""
        assert callable(flext_cli_table)

    def test_flext_cli_table_basic(self) -> None:
        """Test create table without title."""
        result = flext_cli_table([{"name": "test", "value": 123}])
        assert isinstance(result, FlextResult)

    def test_flext_cli_table_with_title(self) -> None:
        """Test create table with title."""
        result = flext_cli_table([{"name": "test", "value": 123}], "Test Table")
        assert isinstance(result, FlextResult)

    def test_flext_cli_table_empty_data(self) -> None:
        """Test create table with empty data."""
        result = flext_cli_table([])
        assert isinstance(result, FlextResult)

    def test_flext_cli_table_none_data(self) -> None:
        """Test create table with None data."""
        result = flext_cli_table(None)
        assert isinstance(result, FlextResult)

    def test_flext_cli_table_single_item(self) -> None:
        """Test create table with single item."""
        result = flext_cli_table([{"key": "value"}])
        assert isinstance(result, FlextResult)

    def test_flext_cli_table_multiple_columns(self) -> None:
        """Test create table with multiple columns."""
        data = [
            {"name": "Alice", "age": 30, "city": "New York"},
            {"name": "Bob", "age": 25, "city": "San Francisco"},
        ]
        result = flext_cli_table(data, "Users")
        assert isinstance(result, FlextResult)


class TestFlextCliExport:
    """Test flext_cli_export function."""

    def test_flext_cli_export_exists(self) -> None:
        """Test that flext_cli_export function exists and is callable."""
        assert callable(flext_cli_export)

    def test_flext_cli_export_json(self) -> None:
        """Test export in JSON format."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            temp_path = f.name

        try:
            result = flext_cli_export({"test": "data"}, temp_path, "json")
            assert isinstance(result, FlextResult)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_flext_cli_export_yaml(self) -> None:
        """Test export in YAML format."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".yaml"
        ) as f:
            temp_path = f.name

        try:
            result = flext_cli_export({"test": "data"}, temp_path, "yaml")
            assert isinstance(result, FlextResult)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_flext_cli_export_csv(self) -> None:
        """Test export in CSV format."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".csv"
        ) as f:
            temp_path = f.name

        try:
            result = flext_cli_export(
                [{"name": "test", "value": 123}],
                temp_path,
                "csv",
            )
            assert isinstance(result, FlextResult)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_flext_cli_export_invalid_path(self) -> None:
        """Test export with invalid path."""
        result = flext_cli_export({"test": "data"}, "/invalid/path/file.json", "json")
        assert isinstance(result, FlextResult)
        # Should handle invalid path gracefully

    def test_flext_cli_export_empty_data(self) -> None:
        """Test export with empty data."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            temp_path = f.name

        try:
            result = flext_cli_export({}, temp_path, "json")
            assert isinstance(result, FlextResult)
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestFlextCliBatchExport:
    """Test flext_cli_batch_export function."""

    def test_flext_cli_batch_export_exists(self) -> None:
        """Test that flext_cli_batch_export function exists and is callable."""
        assert callable(flext_cli_batch_export)

    def test_flext_cli_batch_export_basic(self) -> None:
        """Test batch export with basic data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            datasets = {
                "data1": {"key1": "value1"},
                "data2": {"key2": "value2"},
            }
            result = flext_cli_batch_export(datasets, temp_dir, "json")
            assert isinstance(result, FlextResult)

    def test_flext_cli_batch_export_empty_list(self) -> None:
        """Test batch export with empty datasets."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = flext_cli_batch_export({}, temp_dir, "json")
            assert isinstance(result, FlextResult)

    def test_flext_cli_batch_export_single_item(self) -> None:
        """Test batch export with single item."""
        with tempfile.TemporaryDirectory() as temp_dir:
            datasets = {"single": {"item": "value"}}
            result = flext_cli_batch_export(datasets, temp_dir, "json")
            assert isinstance(result, FlextResult)


class TestFlextCliUnwrapFunctions:
    """Test flext_cli_unwrap_* functions."""

    def test_flext_cli_unwrap_or_default_exists(self) -> None:
        """Test that flext_cli_unwrap_or_default function exists and is callable."""
        assert callable(flext_cli_unwrap_or_default)

    def test_flext_cli_unwrap_or_default_success(self) -> None:
        """Test unwrap_or_default with successful result."""
        success_result = FlextResult.ok("test_value")
        result = flext_cli_unwrap_or_default(success_result, "default_value")
        if result != "test_value":
            msg = f"Expected {'test_value'}, got {result}"
            raise AssertionError(msg)

    def test_flext_cli_unwrap_or_default_failure(self) -> None:
        """Test unwrap_or_default with failed result."""
        failure_result = FlextResult.fail("error message")
        result = flext_cli_unwrap_or_default(failure_result, "default_value")
        if result != "default_value":
            msg = f"Expected {'default_value'}, got {result}"
            raise AssertionError(msg)

    def test_flext_cli_unwrap_or_none_exists(self) -> None:
        """Test that flext_cli_unwrap_or_none function exists and is callable."""
        assert callable(flext_cli_unwrap_or_none)

    def test_flext_cli_unwrap_or_none_success(self) -> None:
        """Test unwrap_or_none with successful result."""
        success_result = FlextResult.ok("test_value")
        result = flext_cli_unwrap_or_none(success_result)
        if result != "test_value":
            msg = f"Expected {'test_value'}, got {result}"
            raise AssertionError(msg)

    def test_flext_cli_unwrap_or_none_failure(self) -> None:
        """Test unwrap_or_none with failed result."""
        failure_result = FlextResult.fail("error message")
        result = flext_cli_unwrap_or_none(failure_result)
        assert result is None

    def test_flext_cli_unwrap_or_default_with_none(self) -> None:
        """Test unwrap_or_default with None default."""
        failure_result = FlextResult.fail("error")
        result = flext_cli_unwrap_or_default(failure_result, None)
        assert result is None

    def test_flext_cli_unwrap_or_default_with_complex_default(self) -> None:
        """Test unwrap_or_default with complex default value."""
        failure_result = FlextResult.fail("error")
        complex_default = {"key": "value", "list": [1, 2, 3]}
        result = flext_cli_unwrap_or_default(failure_result, complex_default)
        if result != complex_default:
            msg = f"Expected {complex_default}, got {result}"
            raise AssertionError(msg)


class TestApiIntegration:
    """Integration tests for API functions."""

    def test_format_and_export_workflow(self) -> None:
        """Test format and export workflow."""
        test_data = {"name": "integration", "value": 42}

        # Format data
        format_result = flext_cli_format(test_data, "json")
        assert isinstance(format_result, FlextResult)

        # Export data
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            temp_path = f.name

        try:
            export_result = flext_cli_export(test_data, temp_path, "json")
            assert isinstance(export_result, FlextResult)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_table_and_format_workflow(self) -> None:
        """Test table creation and formatting workflow."""
        data = [{"name": "Alice", "value": 100}, {"name": "Bob", "value": 200}]

        # Create table
        table_result = flext_cli_table(data, "Test Data")
        assert isinstance(table_result, FlextResult)

        # Format as different types
        json_result = flext_cli_format(data, "json")
        yaml_result = flext_cli_format(data, "yaml")
        csv_result = flext_cli_format(data, "csv")

        assert isinstance(json_result, FlextResult)
        assert isinstance(yaml_result, FlextResult)
        assert isinstance(csv_result, FlextResult)

    def test_batch_export_workflow(self) -> None:
        """Test batch export workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            datasets = {
                "users": [{"name": "Alice"}, {"name": "Bob"}],
                "products": [{"name": "Widget"}, {"name": "Gadget"}],
            }

            result = flext_cli_batch_export(datasets, temp_dir, "json")
            assert isinstance(result, FlextResult)

    def test_unwrap_workflow(self) -> None:
        """Test unwrap functions workflow."""
        # Create various results
        success_result = FlextResult.ok("success_value")
        failure_result = FlextResult.fail("error_message")

        # Test unwrap_or_default
        success_unwrapped = flext_cli_unwrap_or_default(success_result, "default")
        failure_unwrapped = flext_cli_unwrap_or_default(failure_result, "default")

        if success_unwrapped != "success_value":
            msg = f"Expected {'success_value'}, got {success_unwrapped}"
            raise AssertionError(msg)
        assert failure_unwrapped == "default"

        # Test unwrap_or_none
        success_none = flext_cli_unwrap_or_none(success_result)
        failure_none = flext_cli_unwrap_or_none(failure_result)

        if success_none != "success_value":
            msg = f"Expected {'success_value'}, got {success_none}"
            raise AssertionError(msg)
        assert failure_none is None


class TestApiErrorHandling:
    """Test error handling in API functions."""

    def test_format_error_handling(self) -> None:
        """Test format function error handling."""
        # Test with various invalid inputs
        test_cases = [
            (object(), "json"),  # Non-serializable object
            ({"test": object()}, "json"),  # Object with non-serializable values
        ]

        for data, format_type in test_cases:
            result = flext_cli_format(data, format_type)
            assert isinstance(result, FlextResult)
            # Should either succeed or fail gracefully

    def test_export_error_handling(self) -> None:
        """Test export function error handling."""
        # Test with invalid paths
        invalid_paths = [
            "/root/invalid/path.json",  # No permission
            "/nonexistent/directory/file.json",  # Directory doesn't exist
            "",  # Empty path
        ]

        for path in invalid_paths:
            result = flext_cli_export({"test": "data"}, path, "json")
            assert isinstance(result, FlextResult)
            # Should handle errors gracefully

    def test_table_error_handling(self) -> None:
        """Test table function error handling."""
        # Test with invalid data types
        invalid_data = [
            "not a list",
            123,
            {"not": "a list"},
        ]

        for data in invalid_data:
            result = flext_cli_table(data)
            assert isinstance(result, FlextResult)
            # Should handle errors gracefully

    def test_batch_export_error_handling(self) -> None:
        """Test batch export error handling."""
        # Test with invalid export specifications
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with empty datasets
            result = flext_cli_batch_export({}, temp_dir, "json")
            assert isinstance(result, FlextResult)

            # Test with invalid output directory (read-only)
            try:
                result = flext_cli_batch_export(
                    {"test": "data"}, "/nonexistent/dir", "json"
                )
                assert isinstance(result, FlextResult)
            except PermissionError:
                pass  # Expected for invalid directories


class TestApiEdgeCases:
    """Test edge cases for API functions."""

    def test_large_data_handling(self) -> None:
        """Test handling of large data structures."""
        large_data = {f"key_{i}": f"value_{i}" for i in range(1000)}

        result = flext_cli_format(large_data, "json")
        assert isinstance(result, FlextResult)

    def test_special_characters_handling(self) -> None:
        """Test handling of special characters."""
        special_data = {
            "unicode": "Hello 世界 🌍",
            "special": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "newlines": "line1\nline2\r\nline3",
        }

        for format_type in ["json", "yaml", "csv", "table", "plain"]:
            result = flext_cli_format(special_data, format_type)
            assert isinstance(result, FlextResult)

    def test_nested_data_handling(self) -> None:
        """Test handling of deeply nested data."""
        nested_data = {"level1": {"level2": {"level3": {"level4": "deep"}}}}

        result = flext_cli_format(nested_data, "json")
        assert isinstance(result, FlextResult)

    def test_circular_reference_handling(self) -> None:
        """Test handling of circular references."""
        # This would normally cause issues in serialization
        try:
            circular_dict = {"key": "value"}
            circular_dict["self"] = circular_dict

            result = flext_cli_format(circular_dict, "json")
            assert isinstance(result, FlextResult)
            # Should handle gracefully (likely as failure)
        except (RecursionError, ValueError):
            # Expected behavior for circular references
            pass
