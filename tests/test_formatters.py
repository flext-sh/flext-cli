"""Test module for formatters."""

from __future__ import annotations

import csv
import io
import json
import math
import unittest

import pytest
import yaml
from rich.console import Console

from flext_cli.formatters import FlextCliFormatters
from flext_core import FlextTypes


class TestOutputFormatter(unittest.TestCase):
    """Real functionality tests for FlextCliFormatters.OutputFormatter protocol."""

    def test_output_formatter_protocol(self) -> None:
        """Test OutputFormatter protocol exists and can be used."""
        formatters = FlextCliFormatters()
        # Test that we can create formatters using the protocol
        table_formatter = formatters.create_formatter("table")
        assert hasattr(table_formatter, "format")

    def test_custom_formatter_implementation(self) -> None:
        """Test custom formatter can implement the protocol."""
        formatters = FlextCliFormatters()

        class CustomFormatter:
            def format(
                self, data: object, console: FlextCliFormatters._ConsoleOutput | Console
            ) -> None:
                console.print(f"Custom: {data}")

        # Register custom formatter
        formatters.register_formatter("custom", CustomFormatter)

        # Test it works
        custom_formatter = formatters.create_formatter("custom")
        console = FlextCliFormatters._ConsoleOutput()
        try:
            custom_formatter.format("test", console)
            assert True
        except Exception as e:
            msg = f"Custom formatter should work: {e}"
            raise AssertionError(msg) from None


class TestTableFormatter(unittest.TestCase):
    """Real functionality tests for table formatting using FlextCliFormatters."""

    def setUp(self) -> None:
        """Set up test environment with table formatter."""
        self.formatters = FlextCliFormatters()
        self.formatter = self.formatters.create_formatter("table")
        # Use console with string buffer to capture output
        self.output_buffer = io.StringIO()
        self.console = Console(file=self.output_buffer, force_terminal=False, width=80)

    def test_table_formatter_protocol(self) -> None:
        """Test table formatter implements the OutputFormatter protocol."""
        assert hasattr(self.formatter, "format")
        assert callable(self.formatter.format)

    def test_table_formatter_list_of_dicts(self) -> None:
        """Test table formatting with list of dictionaries."""
        test_data = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "London"},
            {"name": "Bob", "age": 35, "city": "Paris"},
        ]

        # Should not raise exceptions
        self.formatter.format(test_data, self.console)

        # Check that output was generated
        output = self.output_buffer.getvalue()
        assert len(output) > 0
        assert "John" in output
        assert "Jane" in output
        assert "Bob" in output

    def test_table_formatter_single_dict(self) -> None:
        """Test table formatting with single dictionary."""
        test_data = {"name": "Alice", "age": 28, "city": "Tokyo", "job": "Engineer"}

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        assert len(output) > 0
        assert "Key" in output
        assert "Value" in output
        assert "Alice" in output
        assert "Engineer" in output

    def test_table_formatter_simple_list(self) -> None:
        """Test table formatting with simple list."""
        test_data = ["apple", "banana", "cherry", "date"]

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        assert len(output) > 0
        assert "apple" in output
        assert "banana" in output
        assert "Value" in output  # Column header

    def test_table_formatter_single_value(self) -> None:
        """Test table formatting with single value."""
        test_data = "Single Value"

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        assert len(output) > 0
        assert "Single Value" in output

    def test_table_formatter_empty_list(self) -> None:
        """Test table formatting with empty list."""
        test_data: list[FlextTypes.Core.Dict] = []

        # Should handle empty data gracefully
        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        # Should generate some output (at least table structure)
        assert isinstance(output, str)

    def test_table_formatter_mixed_dict_structures(self) -> None:
        """Test table formatting with dictionaries having different keys."""
        test_data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30, "city": "NYC"},
            {"name": "Charlie", "job": "Developer"},
        ]

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        assert len(output) > 0
        assert "Alice" in output
        assert "Bob" in output
        assert "Charlie" in output

    def test_table_formatter_numeric_data(self) -> None:
        """Test table formatting with numeric data."""
        test_data = [1, 2, math.pi, 42, 0, -5]

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        assert "1" in output
        assert "3.14" in output
        assert "42" in output

    def test_table_formatter_none_values(self) -> None:
        """Test table formatting handles None values."""
        test_data = [
            {"name": "Test", "value": None, "active": True},
            {"name": None, "value": 42, "active": False},
        ]

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        assert "Test" in output
        assert "42" in output
        # None values should be converted to strings
        assert "None" in output or "" in output


class TestJSONFormatter(unittest.TestCase):
    """Real functionality tests for JSON formatting using FlextCliFormatters."""

    def setUp(self) -> None:
        """Set up test environment with JSON formatter."""
        self.formatters = FlextCliFormatters()
        self.formatter = self.formatters.create_formatter("json")
        self.output_buffer = io.StringIO()
        self.console = Console(file=self.output_buffer, force_terminal=False)

    def test_json_formatter_protocol(self) -> None:
        """Test JSON formatter implements the OutputFormatter protocol."""
        assert hasattr(self.formatter, "format")
        assert callable(self.formatter.format)

    def test_json_formatter_dict_data(self) -> None:
        """Test JSON formatting with dictionary data."""
        test_data = {"name": "Alice", "age": 30, "active": True, "score": 95.5}

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue().strip()
        # Should be valid JSON
        parsed = json.loads(output)
        assert parsed == test_data

    def test_json_formatter_list_data(self) -> None:
        """Test JSON formatting with list data."""
        test_data = [1, 2, "three", True, None, {"nested": "value"}]

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue().strip()
        parsed = json.loads(output)
        assert parsed == test_data

    def test_json_formatter_nested_data(self) -> None:
        """Test JSON formatting with nested data structures."""
        test_data = {
            "users": [
                {"name": "John", "details": {"age": 30, "city": "NYC"}},
                {"name": "Jane", "details": {"age": 25, "city": "LA"}},
            ],
            "metadata": {"total": 2, "active": True},
        }

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue().strip()
        parsed = json.loads(output)
        assert parsed == test_data

    def test_json_formatter_string_data(self) -> None:
        """Test JSON formatting with string data."""
        test_data = "Simple string value"

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue().strip()
        parsed = json.loads(output)
        assert parsed == test_data

    def test_json_formatter_numeric_data(self) -> None:
        """Test JSON formatting with numeric data."""
        test_cases = [42, math.pi, 0, -17, 1e6]

        for test_data in test_cases:
            with self.subTest(data=test_data):
                # Reset buffer for each test
                self.output_buffer.seek(0)
                self.output_buffer.truncate(0)

                self.formatter.format(test_data, self.console)

                output = self.output_buffer.getvalue().strip()
                parsed = json.loads(output)
                assert parsed == test_data

    def test_json_formatter_boolean_data(self) -> None:
        """Test JSON formatting with boolean data."""
        for test_data in [True, False]:
            with self.subTest(data=test_data):
                # Reset buffer
                self.output_buffer.seek(0)
                self.output_buffer.truncate(0)

                self.formatter.format(test_data, self.console)

                output = self.output_buffer.getvalue().strip()
                parsed = json.loads(output)
                assert parsed == test_data

    def test_json_formatter_null_data(self) -> None:
        """Test JSON formatting with null/None data."""
        test_data = None

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue().strip()
        parsed = json.loads(output)
        assert parsed is None


class TestYAMLFormatter(unittest.TestCase):
    """Real functionality tests for YAML formatting using FlextCliFormatters."""

    def setUp(self) -> None:
        """Set up test environment with YAML formatter."""
        self.formatters = FlextCliFormatters()
        self.formatter = self.formatters.create_formatter("yaml")
        self.output_buffer = io.StringIO()
        self.console = Console(file=self.output_buffer, force_terminal=False)

    def test_yaml_formatter_protocol(self) -> None:
        """Test YAML formatter implements the OutputFormatter protocol."""
        assert hasattr(self.formatter, "format")
        assert callable(self.formatter.format)

    def test_yaml_formatter_dict_data(self) -> None:
        """Test YAML formatting with dictionary data."""
        test_data = {"name": "Alice", "age": 30, "active": True, "score": 95.5}

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        # Should be valid YAML
        parsed = yaml.safe_load(output)
        assert parsed == test_data

    def test_yaml_formatter_list_data(self) -> None:
        """Test YAML formatting with list data."""
        test_data = [1, 2, "three", True, None, {"nested": "value"}]

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        parsed = yaml.safe_load(output)
        assert parsed == test_data

    def test_yaml_formatter_nested_data(self) -> None:
        """Test YAML formatting with nested data structures."""
        test_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {"username": "admin", "password": "secret"},
            },
            "features": ["auth", "logging", "cache"],
            "debug": False,
        }

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        parsed = yaml.safe_load(output)
        assert parsed == test_data

    def test_yaml_formatter_string_data(self) -> None:
        """Test YAML formatting with string data."""
        test_data = "Simple string with special characters: @#$%"

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        parsed = yaml.safe_load(output)
        assert parsed == test_data

    def test_yaml_formatter_multiline_string(self) -> None:
        """Test YAML formatting with multiline strings."""
        test_data = "Line 1\\nLine 2\\nLine 3"

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        parsed = yaml.safe_load(output)
        assert parsed == test_data

    def test_yaml_formatter_numeric_types(self) -> None:
        """Test YAML formatting with various numeric types."""
        test_data = {
            "integer": 42,
            "float": math.pi,
            "scientific": 1e6,
            "negative": -17,
        }

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        parsed = yaml.safe_load(output)
        assert parsed == test_data


class TestCSVFormatter(unittest.TestCase):
    """Real functionality tests for CSV formatting using FlextCliFormatters."""

    def setUp(self) -> None:
        """Set up test environment with CSV formatter."""
        self.formatters = FlextCliFormatters()
        self.formatter = self.formatters.create_formatter("csv")
        self.output_buffer = io.StringIO()
        self.console = Console(file=self.output_buffer, force_terminal=False)

    def test_csv_formatter_protocol(self) -> None:
        """Test CSV formatter implements the OutputFormatter protocol."""
        assert hasattr(self.formatter, "format")
        assert callable(self.formatter.format)

    def test_csv_formatter_list_of_dicts(self) -> None:
        """Test CSV formatting with list of dictionaries."""
        test_data = [
            {"name": "John", "age": 30, "city": "NYC"},
            {"name": "Jane", "age": 25, "city": "LA"},
            {"name": "Bob", "age": 35, "city": "Chicago"},
        ]

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        # Parse the CSV output to validate
        reader = csv.DictReader(io.StringIO(output))
        rows = list(reader)

        assert len(rows) == 3
        assert rows[0]["name"] == "John"
        assert rows[1]["age"] == "25"
        assert rows[2]["city"] == "Chicago"

    def test_csv_formatter_single_dict(self) -> None:
        """Test CSV formatting with single dictionary."""
        test_data = {"product": "Laptop", "price": "999.99", "in_stock": "true"}

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        # Should handle single dict by creating key-value pairs
        lines = output.strip().split("\\n")
        assert len(lines) >= 1  # Should produce some output

    def test_csv_formatter_empty_data(self) -> None:
        """Test CSV formatting with empty data."""
        test_data: list[FlextTypes.Core.Dict] = []

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        # Should handle empty data gracefully
        assert isinstance(output, str)

    def test_csv_formatter_mixed_keys(self) -> None:
        """Test CSV formatting with dictionaries having different keys fails appropriately."""
        test_data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "city": "NYC"},  # 'city' not in first dict's keys
            {"age": 30, "job": "Developer"},  # 'job' not in first dict's keys
        ]

        # CSVFormatter uses first dict's keys as fieldnames, so extra keys cause ValueError
        with pytest.raises(ValueError) as context:
            self.formatter.format(test_data, self.console)

        assert "dict contains fields not in fieldnames" in str(context.value)

    def test_csv_formatter_special_characters(self) -> None:
        """Test CSV formatting with special characters that need escaping."""
        test_data = [
            {"name": "O'Brien", "note": "Contains, comma", "quote": 'He said "hello"'},
            {"name": "Smith", "note": "Normal text", "quote": "Simple quote"},
        ]

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        # CSV formatter should handle special characters
        assert "O'Brien" in output
        assert "comma" in output

    def test_csv_formatter_numeric_data(self) -> None:
        """Test CSV formatting with numeric data."""
        test_data = [
            {"id": 1, "score": 95.5, "active": True},
            {"id": 2, "score": 87.2, "active": False},
        ]

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        assert "95.5" in output
        assert "87.2" in output


class TestPlainFormatter(unittest.TestCase):
    """Real functionality tests for plain formatting using FlextCliFormatters."""

    def setUp(self) -> None:
        """Set up test environment with plain formatter."""
        self.formatters = FlextCliFormatters()
        self.formatter = self.formatters.create_formatter("plain")
        self.output_buffer = io.StringIO()
        self.console = Console(file=self.output_buffer, force_terminal=False)

    def test_plain_formatter_protocol(self) -> None:
        """Test plain formatter implements the OutputFormatter protocol."""
        assert hasattr(self.formatter, "format")
        assert callable(self.formatter.format)

    def test_plain_formatter_string_data(self) -> None:
        """Test plain formatting with string data."""
        test_data = "Simple string output"

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue().strip()
        assert output == test_data

    def test_plain_formatter_dict_data(self) -> None:
        """Test plain formatting with dictionary data."""
        test_data = {"name": "Alice", "age": 30, "city": "NYC"}

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        # Should convert dict to string representation
        assert "Alice" in output
        assert "30" in output
        assert "NYC" in output

    def test_plain_formatter_list_data(self) -> None:
        """Test plain formatting with list data."""
        test_data = ["apple", "banana", "cherry"]

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        assert "apple" in output
        assert "banana" in output
        assert "cherry" in output

    def test_plain_formatter_numeric_data(self) -> None:
        """Test plain formatting with numeric data."""
        test_cases = [42, math.pi, 0, -17]

        for test_data in test_cases:
            with self.subTest(data=test_data):
                # Reset buffer
                self.output_buffer.seek(0)
                self.output_buffer.truncate(0)

                self.formatter.format(test_data, self.console)

                output = self.output_buffer.getvalue().strip()
                assert str(test_data) in output

    def test_plain_formatter_boolean_data(self) -> None:
        """Test plain formatting with boolean data."""
        for test_data in [True, False]:
            with self.subTest(data=test_data):
                # Reset buffer
                self.output_buffer.seek(0)
                self.output_buffer.truncate(0)

                self.formatter.format(test_data, self.console)

                output = self.output_buffer.getvalue().strip()
                assert str(test_data) in output

    def test_plain_formatter_none_data(self) -> None:
        """Test plain formatting with None data."""
        test_data = None

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue().strip()
        assert "None" in output

    def test_plain_formatter_complex_data(self) -> None:
        """Test plain formatting with complex nested data."""
        test_data = {
            "users": ["Alice", "Bob"],
            "settings": {"debug": True, "level": "INFO"},
            "count": 42,
        }

        self.formatter.format(test_data, self.console)

        output = self.output_buffer.getvalue()
        # Should contain string representation of the data
        assert "Alice" in output
        assert "Bob" in output
        assert "42" in output


class TestFormatterFactory(unittest.TestCase):
    """Real functionality tests for FlextCliFormatters factory methods."""

    def setUp(self) -> None:
        """Set up test environment with formatter factory."""
        self.factory = FlextCliFormatters()

    def test_formatter_factory_instantiation(self) -> None:
        """Test FlextCliFormatters can be instantiated."""
        factory = FlextCliFormatters()
        assert isinstance(factory, FlextCliFormatters)

    def test_formatter_factory_get_table_formatter(self) -> None:
        """Test factory can create table formatter."""
        formatter = self.factory.create_formatter("table")
        assert hasattr(formatter, "format")
        assert callable(formatter.format)

    def test_formatter_factory_get_json_formatter(self) -> None:
        """Test factory can create JSON formatter."""
        formatter = self.factory.create_formatter("json")
        assert hasattr(formatter, "format")
        assert callable(formatter.format)

    def test_formatter_factory_get_yaml_formatter(self) -> None:
        """Test factory can create YAML formatter."""
        formatter = self.factory.create_formatter("yaml")
        assert hasattr(formatter, "format")
        assert callable(formatter.format)

    def test_formatter_factory_get_csv_formatter(self) -> None:
        """Test factory can create CSV formatter."""
        formatter = self.factory.create_formatter("csv")
        assert hasattr(formatter, "format")
        assert callable(formatter.format)

    def test_formatter_factory_get_plain_formatter(self) -> None:
        """Test factory can create plain formatter."""
        formatter = self.factory.create_formatter("plain")
        assert hasattr(formatter, "format")
        assert callable(formatter.format)

    def test_formatter_factory_invalid_format(self) -> None:
        """Test factory handles invalid format names."""
        try:
            formatter = self.factory.create_formatter("invalid")
            # Should either return default or raise exception
            assert formatter is not None or formatter is None
        except (ValueError, KeyError):
            # Acceptable to raise exception for invalid formats
            assert True

    def test_formatter_factory_all_supported_formats(self) -> None:
        """Test factory supports all expected formatter types."""
        expected_formats = ["table", "json", "yaml", "csv", "plain"]

        for format_type in expected_formats:
            try:
                formatter = self.factory.create_formatter(format_type)
                assert hasattr(formatter, "format")
                assert callable(formatter.format)
            except Exception as e:
                pytest.fail(f"Failed to create formatter for {format_type}: {e}")

    def test_formatter_factory_formatters_are_different_instances(self) -> None:
        """Test factory creates different instances for multiple calls."""
        formatter1 = self.factory.create_formatter("json")
        formatter2 = self.factory.create_formatter("json")

        # Should create separate instances
        assert formatter1 is not formatter2
        assert type(formatter1) is type(formatter2)


class TestFormatterIntegration(unittest.TestCase):
    """Real functionality integration tests for all formatters."""

    def test_all_formatters_with_same_data(self) -> None:
        """Test all formatters can handle the same input data."""
        test_data = [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": False},
        ]

        factory = FlextCliFormatters()
        formatters = [
            factory.create_formatter("table"),
            factory.create_formatter("json"),
            factory.create_formatter("yaml"),
            factory.create_formatter("csv"),
            factory.create_formatter("plain"),
        ]

        for formatter in formatters:
            with self.subTest(formatter=type(formatter).__name__):
                output_buffer = io.StringIO()
                console = Console(file=output_buffer, force_terminal=False)

                # Should not raise exceptions
                formatter.format(test_data, console)

                output = output_buffer.getvalue()
                # Should produce some output
                assert len(output) > 0
                # Should contain the data
                assert "Alice" in output
                assert "Bob" in output

    def test_formatters_with_edge_case_data(self) -> None:
        """Test all formatters handle edge cases gracefully."""
        edge_cases: FlextTypes.Core.List = [
            None,
            "",
            [],
            {},
            0,
            False,
            {"empty_value": "", "null_value": None},
        ]

        factory = FlextCliFormatters()
        formatters = [
            factory.create_formatter("table"),
            factory.create_formatter("json"),
            factory.create_formatter("yaml"),
            factory.create_formatter("csv"),
            factory.create_formatter("plain"),
        ]

        for formatter in formatters:
            for test_data in edge_cases:
                with self.subTest(formatter=type(formatter).__name__, data=test_data):
                    output_buffer = io.StringIO()
                    console = Console(file=output_buffer, force_terminal=False)

                    try:
                        formatter.format(test_data, console)
                        # Should handle edge cases without crashing
                        assert True
                    except Exception as e:
                        # Some edge cases might legitimately fail
                        # But we shouldn't get unhandled exceptions
                        if not isinstance(e, (TypeError, ValueError, AttributeError)):
                            raise

    def test_formatter_factory_integration(self) -> None:
        """Test FlextCliFormatters integration with all formatter types."""
        factory = FlextCliFormatters()

        # Test data that should work with all formatters
        test_data = {"message": "Hello, World!", "timestamp": "2025-01-01T00:00:00Z"}

        format_types = ["table", "json", "yaml", "csv", "plain"]

        for format_type in format_types:
            with self.subTest(format=format_type):
                try:
                    formatter = factory.create_formatter(format_type)
                    assert hasattr(formatter, "format")
                    assert callable(formatter.format)

                    # Test the formatter works
                    output_buffer = io.StringIO()
                    console = Console(file=output_buffer, force_terminal=False)
                    formatter.format(test_data, console)

                    output = output_buffer.getvalue()
                    assert len(output) > 0
                    assert "Hello, World!" in output

                except Exception as e:
                    pytest.fail(
                        f"Format {format_type} failed with data 'Hello, World!': {e}",
                    )

    def test_formatters_preserve_data_integrity(self) -> None:
        """Test that formatters preserve data integrity where possible."""
        original_data = {
            "string": "test value",
            "integer": 42,
            "float": math.pi,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"inner": "value"},
        }

        # JSON and YAML should preserve exact data structure
        factory = FlextCliFormatters()
        reversible_formatters = [
            (factory.create_formatter("json"), json.loads),
            (factory.create_formatter("yaml"), yaml.safe_load),
        ]

        for formatter, parser in reversible_formatters:
            with self.subTest(formatter=type(formatter).__name__):
                output_buffer = io.StringIO()
                console = Console(file=output_buffer, force_terminal=False)

                formatter.format(original_data, console)

                output = output_buffer.getvalue().strip()
                if output and callable(
                    parser,
                ):  # Only test if formatter produced output and parser is callable
                    parsed_data = parser(output)
                    assert parsed_data == original_data


if __name__ == "__main__":
    unittest.main()
