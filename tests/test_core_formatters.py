"""Tests for core formatters in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

from flext_cli.flext_cli_formatters import FlextCliFormatters


class TestTableFormatter:
    """Test cases for Table formatting using FlextCliFormatters."""

    def test_format_list_of_dicts(self) -> None:
        """Test formatting list of dictionaries as table."""
        formatter = FlextCliFormatters()
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        result = formatter.format_data(
            cast("list[dict[str, object]]", data), format_type="table"
        )
        assert result.is_success
        assert isinstance(result.value, str)

    def test_format_simple_list(self) -> None:
        """Test formatting simple list fails appropriately."""
        formatter = FlextCliFormatters()
        data = ["item1", "item2", "item3"]

        result = formatter.format_data(
            cast("list[dict[str, object]]", data), format_type="table"
        )
        assert result.is_failure

    def test_format_single_dict(self) -> None:
        """Test formatting single dictionary as table."""
        formatter = FlextCliFormatters()
        data = {"name": "Alice", "age": 30}

        result = formatter.format_data(
            data=cast("dict[str, object]", data),
            format_type="table",
            title="User Data",
            headers=["Field", "Value"],
        )
        assert result.is_success
        assert "Alice" in result.value

    def test_format_unsupported_type(self) -> None:
        """Test formatting unsupported data types fails."""
        formatter = FlextCliFormatters()
        data = "simple string"

        result = formatter.format_data(
            cast("dict[str, object]", data), format_type="unsupported"
        )
        assert result.is_failure


class TestJSONFormatter:
    """Test cases for JSON formatting using FlextCliFormatters."""

    def test_format_dict(self) -> None:
        """Test formatting dictionary as JSON."""
        formatter = FlextCliFormatters()
        data = {"name": "Alice", "age": 30}

        result = formatter.format_data(
            cast("dict[str, object]", data), format_type="json"
        )
        assert result.is_success
        assert "Alice" in result.value
        assert "30" in result.value

    def test_format_list(self) -> None:
        """Test formatting list as JSON."""
        formatter = FlextCliFormatters()
        data = [{"name": "Alice"}, {"name": "Bob"}]

        result = formatter.format_data(
            cast("list[dict[str, object]]", data), format_type="json"
        )
        assert result.is_success
        assert "Alice" in result.value
        assert "Bob" in result.value


class TestUnsupportedFormats:
    """Test cases for unsupported format types."""

    def test_yaml_format_not_supported(self) -> None:
        """Test that YAML format is not yet supported."""
        formatter = FlextCliFormatters()
        data = {"name": "Alice", "age": 30}

        result = formatter.format_data(
            cast("dict[str, object]", data), format_type="yaml"
        )
        assert result.is_failure
        assert result.error is not None and "Unsupported format type" in result.error

    def test_csv_format_not_supported(self) -> None:
        """Test that CSV format is not yet supported."""
        formatter = FlextCliFormatters()
        data = [{"name": "Alice", "age": 30}]

        result = formatter.format_data(
            cast("list[dict[str, object]]", data), format_type="csv"
        )
        assert result.is_failure
        assert result.error is not None and "Unsupported format type" in result.error

    def test_plain_format_not_supported(self) -> None:
        """Test that plain format is not yet supported."""
        formatter = FlextCliFormatters()
        data = {"name": "Alice"}

        result = formatter.format_data(
            cast("dict[str, object]", data), format_type="plain"
        )
        assert result.is_failure
        assert result.error is not None and "Unsupported format type" in result.error


class TestFormatterFactory:
    """Test cases for formatter factory methods."""

    def test_create_table_formatter(self) -> None:
        """Test creating table formatter."""
        formatter = FlextCliFormatters()
        result = formatter.create_formatter("table")
        assert result.is_success

    def test_create_unknown_formatter(self) -> None:
        """Test creating unknown formatter type."""
        formatter = FlextCliFormatters()
        result = formatter.create_formatter("unknown")
        assert result.is_failure

    def test_supported_formats(self) -> None:
        """Test supported format types."""
        formatter = FlextCliFormatters()

        for format_type in ["table", "json"]:
            result = formatter.format_data({"test": "data"}, format_type=format_type)
            assert result.is_success


class TestFormatterIntegration:
    """Integration tests for formatters."""

    def test_format_table_with_headers(self) -> None:
        """Test table formatting with custom headers."""
        formatter = FlextCliFormatters()
        data: dict[str, object] = {"name": "Alice", "age": 30}

        result = formatter.format_data(
            data=data,
            format_type="table",
            title="User Information",
            headers=["Property", "Value"],
        )
        assert result.is_success
        assert "Alice" in result.value

    def test_console_access(self) -> None:
        """Test console property access."""
        formatter = FlextCliFormatters()
        console = formatter.console
        assert console is not None

    def test_print_methods(self) -> None:
        """Test print methods."""
        formatter = FlextCliFormatters()

        formatter.print_success("Success message")
        formatter.print_error("Error message")
        formatter.print_warning("Warning message")
        formatter.print_message("Info message", style="info")
