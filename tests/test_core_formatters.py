"""Tests for core formatters in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import io

import pytest
from flext_cli.core.formatters import (
    CSVFormatter,
    FormatterFactory,
    JSONFormatter,
    PlainFormatter,
    TableFormatter,
    YAMLFormatter,
    format_output,
)
from rich.console import Console


class TestTableFormatter:
    """Test cases for TableFormatter."""

    def test_format_list_of_dicts(self) -> None:
        """Test formatting list of dictionaries as table."""
        formatter = TableFormatter()
        console = Console(file=io.StringIO(), width=80)

        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        formatter.format(data, console)
        # Should not raise any exceptions

    def test_format_simple_list(self) -> None:
        """Test formatting simple list as table."""
        formatter = TableFormatter()
        console = Console(file=io.StringIO(), width=80)

        data = ["item1", "item2", "item3"]

        formatter.format(data, console)
        # Should not raise any exceptions

    def test_format_single_dict(self) -> None:
        """Test formatting single dictionary as table."""
        formatter = TableFormatter()
        console = Console(file=io.StringIO(), width=80)

        data = {"name": "Alice", "age": 30}

        formatter.format(data, console)
        # Should not raise any exceptions

    def test_format_other_data_type(self) -> None:
        """Test formatting other data types."""
        formatter = TableFormatter()
        console = Console(file=io.StringIO(), width=80)

        data = "simple string"

        formatter.format(data, console)
        # Should not raise any exceptions


class TestJSONFormatter:
    """Test cases for JSONFormatter."""

    def test_format_dict(self) -> None:
        """Test formatting dictionary as JSON."""
        formatter = JSONFormatter()
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = {"name": "Alice", "age": 30}

        formatter.format(data, console)
        result = output.getvalue()
        if "Alice" not in result:
            msg = f"Expected {"Alice"} in {result}"
            raise AssertionError(msg)
        assert "30" in result

    def test_format_list(self) -> None:
        """Test formatting list as JSON."""
        formatter = JSONFormatter()
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = [{"name": "Alice"}, {"name": "Bob"}]

        formatter.format(data, console)
        result = output.getvalue()
        if "Alice" not in result:
            msg = f"Expected {"Alice"} in {result}"
            raise AssertionError(msg)
        assert "Bob" in result


class TestYAMLFormatter:
    """Test cases for YAMLFormatter."""

    def test_format_dict(self) -> None:
        """Test formatting dictionary as YAML."""
        formatter = YAMLFormatter()
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = {"name": "Alice", "age": 30}

        formatter.format(data, console)
        result = output.getvalue()
        if "name: Alice" not in result:
            msg = f"Expected {"name: Alice"} in {result}"
            raise AssertionError(msg)
        assert "age: 30" in result

    def test_format_list(self) -> None:
        """Test formatting list as YAML."""
        formatter = YAMLFormatter()
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = [{"name": "Alice"}, {"name": "Bob"}]

        formatter.format(data, console)
        result = output.getvalue()
        if "Alice" not in result:
            msg = f"Expected {"Alice"} in {result}"
            raise AssertionError(msg)
        assert "Bob" in result


class TestCSVFormatter:
    """Test cases for CSVFormatter."""

    def test_format_list_of_dicts(self) -> None:
        """Test formatting list of dictionaries as CSV."""
        formatter = CSVFormatter()
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        formatter.format(data, console)
        result = output.getvalue()
        if "name,age" not in result:
            msg = f"Expected {"name,age"} in {result}"
            raise AssertionError(msg)
        assert "Alice,30" in result
        if "Bob,25" not in result:
            msg = f"Expected {"Bob,25"} in {result}"
            raise AssertionError(msg)

    def test_format_simple_list(self) -> None:
        """Test formatting simple list as CSV."""
        formatter = CSVFormatter()
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = ["item1", "item2", "item3"]

        formatter.format(data, console)
        result = output.getvalue()
        if "item1" not in result:
            msg = f"Expected {"item1"} in {result}"
            raise AssertionError(msg)
        assert "item2" in result
        if "item3" not in result:
            msg = f"Expected {"item3"} in {result}"
            raise AssertionError(msg)

    def test_format_single_dict(self) -> None:
        """Test formatting single dictionary as CSV."""
        formatter = CSVFormatter()
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = {"name": "Alice", "age": 30}

        formatter.format(data, console)
        result = output.getvalue()
        if "name,age" not in result:
            msg = f"Expected {"name,age"} in {result}"
            raise AssertionError(msg)
        assert "Alice,30" in result


class TestPlainFormatter:
    """Test cases for PlainFormatter."""

    def test_format_list_of_dicts(self) -> None:
        """Test formatting list of dictionaries as plain text."""
        formatter = PlainFormatter()
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        formatter.format(data, console)
        result = output.getvalue()
        if "name: Alice" not in result:
            msg = f"Expected {"name: Alice"} in {result}"
            raise AssertionError(msg)
        assert "age: 30" in result
        if "name: Bob" not in result:
            msg = f"Expected {"name: Bob"} in {result}"
            raise AssertionError(msg)
        assert "age: 25" in result

    def test_format_simple_list(self) -> None:
        """Test formatting simple list as plain text."""
        formatter = PlainFormatter()
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = ["item1", "item2", "item3"]

        formatter.format(data, console)
        result = output.getvalue()
        if "item1" not in result:
            msg = f"Expected {"item1"} in {result}"
            raise AssertionError(msg)
        assert "item2" in result
        if "item3" not in result:
            msg = f"Expected {"item3"} in {result}"
            raise AssertionError(msg)

    def test_format_single_dict(self) -> None:
        """Test formatting single dictionary as plain text."""
        formatter = PlainFormatter()
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = {"name": "Alice", "age": 30}

        formatter.format(data, console)
        result = output.getvalue()
        if "name: Alice" not in result:
            msg = f"Expected {"name: Alice"} in {result}"
            raise AssertionError(msg)
        assert "age: 30" in result

    def test_format_other_data_type(self) -> None:
        """Test formatting other data types as plain text."""
        formatter = PlainFormatter()
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = "simple string"

        formatter.format(data, console)
        result = output.getvalue()
        if "simple string" not in result:
            msg = f"Expected {"simple string"} in {result}"
            raise AssertionError(msg)


class TestFormatterFactory:
    """Test cases for FormatterFactory."""

    def test_create_table_formatter(self) -> None:
        """Test creating table formatter."""
        formatter = FormatterFactory.create("table")
        assert isinstance(formatter, TableFormatter)

    def test_create_json_formatter(self) -> None:
        """Test creating JSON formatter."""
        formatter = FormatterFactory.create("json")
        assert isinstance(formatter, JSONFormatter)

    def test_create_yaml_formatter(self) -> None:
        """Test creating YAML formatter."""
        formatter = FormatterFactory.create("yaml")
        assert isinstance(formatter, YAMLFormatter)

    def test_create_csv_formatter(self) -> None:
        """Test creating CSV formatter."""
        formatter = FormatterFactory.create("csv")
        assert isinstance(formatter, CSVFormatter)

    def test_create_plain_formatter(self) -> None:
        """Test creating plain formatter."""
        formatter = FormatterFactory.create("plain")
        assert isinstance(formatter, PlainFormatter)

    def test_create_unknown_formatter(self) -> None:
        """Test creating unknown formatter raises error."""
        with pytest.raises(ValueError, match="Unknown formatter type"):
            FormatterFactory.create("unknown")

    def test_register_custom_formatter(self) -> None:
        """Test registering custom formatter."""
        from flext_cli.core.formatters import OutputFormatter

        class CustomFormatter(OutputFormatter):
            def format(self, data: object, console: Console) -> None:
                console.print("custom")

        FormatterFactory.register("custom", CustomFormatter)
        formatter = FormatterFactory.create("custom")
        assert isinstance(formatter, CustomFormatter)

    def test_list_formats(self) -> None:
        """Test listing available formats."""
        formats = FormatterFactory.list_formats()
        if "table" not in formats:
            msg = f"Expected {"table"} in {formats}"
            raise AssertionError(msg)
        assert "json" in formats
        if "yaml" not in formats:
            msg = f"Expected {"yaml"} in {formats}"
            raise AssertionError(msg)
        assert "csv" in formats
        if "plain" not in formats:
            msg = f"Expected {"plain"} in {formats}"
            raise AssertionError(msg)


class TestFormatOutput:
    """Test cases for format_output function."""

    def test_format_output_table(self) -> None:
        """Test format_output with table format."""
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = [{"name": "Alice", "age": 30}]

        format_output(data, "table", console)
        # Should not raise any exceptions

    def test_format_output_json(self) -> None:
        """Test format_output with JSON format."""
        output = io.StringIO()
        console = Console(file=output, width=80)

        data = {"name": "Alice", "age": 30}

        format_output(data, "json", console)
        result = output.getvalue()
        if "Alice" not in result:
            msg = f"Expected {"Alice"} in {result}"
            raise AssertionError(msg)

    def test_format_output_unknown_format(self) -> None:
        """Test format_output with unknown format."""
        console = Console(file=io.StringIO(), width=80)
        data = {"test": "data"}

        with pytest.raises(ValueError, match="Unknown formatter type"):
            format_output(data, "unknown", console)
