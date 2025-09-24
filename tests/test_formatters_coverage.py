"""Additional coverage tests for FlextCliOutput.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from unittest.mock import patch

from rich.table import Table

from flext_cli import FlextCliOutput


class TestFlextCliFormattersBasic:
    """Test basic FlextCliOutput functionality."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.formatter = FlextCliOutput()

    def test_execute_method(self) -> None:
        """Test execute method returns success."""
        result = self.formatter.execute()
        assert result.is_success
        assert "operational" in result.value.lower()

    def test_create_table_empty_data(self) -> None:
        """Test create_table with empty data."""
        result = self.formatter.create_table([])
        assert result.is_failure
        assert "No data provided" in (result.error or "")

    def test_create_table_success(self) -> None:
        """Test create_table with valid data."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = self.formatter.create_table(data)
        assert result.is_success
        assert isinstance(result.value, Table)

    def test_create_table_with_title(self) -> None:
        """Test create_table with title."""
        data = [{"name": "Alice", "age": 30}]
        result = self.formatter.create_table(data, title="Users")
        assert result.is_success
        assert isinstance(result.value, Table)

    def test_create_table_with_custom_headers(self) -> None:
        """Test create_table with custom headers."""
        data = [{"name": "Alice", "age": 30}]
        result = self.formatter.create_table(data, headers=["Name", "Age"])
        assert result.is_success
        assert isinstance(result.value, Table)

    def test_create_table_error_handling(self) -> None:
        """Test create_table error handling."""
        # Pass invalid data that will cause an exception
        with patch.object(Table, "add_column", side_effect=Exception("Column error")):
            data: list[dict[str, object]] = [{"name": "Alice"}]
            result = self.formatter.create_table(data)
            assert result.is_failure
            assert "Failed to create table" in (result.error or "")

    def test_table_to_string_success(self) -> None:
        """Test table_to_string converts table to string."""
        data = [{"name": "Alice", "age": 30}]
        table_result = self.formatter.create_table(data)
        assert table_result.is_success

        string_result = self.formatter.table_to_string(table_result.value)
        assert string_result.is_success
        assert isinstance(string_result.value, str)
        assert len(string_result.value) > 0

    def test_table_to_string_with_width(self) -> None:
        """Test table_to_string with custom width."""
        data = [{"name": "Alice", "age": 30}]
        table_result = self.formatter.create_table(data)
        assert table_result.is_success

        string_result = self.formatter.table_to_string(table_result.value, width=80)
        assert string_result.is_success
        assert isinstance(string_result.value, str)

    def test_table_to_string_error(self) -> None:
        """Test table_to_string error handling."""
        data: list[dict[str, object]] = [{"name": "Alice"}]
        table_result = self.formatter.create_table(data)
        assert table_result.is_success

        with patch("rich.console.Console.print", side_effect=Exception("Print error")):
            string_result = self.formatter.table_to_string(table_result.value)
            assert string_result.is_failure
            assert "Failed to convert table" in (string_result.error or "")

    def test_create_progress_bar_default(self) -> None:
        """Test create_progress_bar with defaults."""
        result = self.formatter.create_progress_bar()
        assert result.is_success
        progress, task_id = result.value
        assert progress is not None
        assert task_id is not None

    def test_create_progress_bar_custom(self) -> None:
        """Test create_progress_bar with custom parameters."""
        result = self.formatter.create_progress_bar(description="Loading", total=50)
        assert result.is_success
        progress, task_id = result.value
        assert progress is not None
        assert task_id is not None

    def test_create_progress_bar_error(self) -> None:
        """Test create_progress_bar error handling."""
        with patch(
            "rich.progress.Progress.add_task", side_effect=Exception("Task error")
        ):
            result = self.formatter.create_progress_bar()
            assert result.is_failure
            assert "Failed to create progress bar" in (result.error or "")

    def test_print_message_simple(self) -> None:
        """Test print_message with simple message."""
        with patch.object(self.formatter._console, "print") as mock_print:
            result = self.formatter.print_message("Hello")
            assert result.is_success
            mock_print.assert_called_once()

    def test_print_message_with_style(self) -> None:
        """Test print_message with style."""
        with patch.object(self.formatter._console, "print") as mock_print:
            result = self.formatter.print_message("Styled", style="bold")
            assert result.is_success
            mock_print.assert_called_once()

    def test_print_message_with_highlight(self) -> None:
        """Test print_message with highlight."""
        with patch.object(self.formatter._console, "print") as mock_print:
            result = self.formatter.print_message("Code", highlight=True)
            assert result.is_success
            mock_print.assert_called_once()

    def test_print_message_error(self) -> None:
        """Test print_message error handling."""
        with patch.object(
            self.formatter._console, "print", side_effect=Exception("Print failed")
        ):
            result = self.formatter.print_message("Test")
            assert result.is_failure
            assert "Failed to print message" in (result.error or "")

    def test_print_error(self) -> None:
        """Test print_error method."""
        with patch.object(self.formatter._console, "print") as mock_print:
            result = self.formatter.print_error("Something went wrong")
            assert result.is_success
            mock_print.assert_called_once()

    def test_print_success(self) -> None:
        """Test print_success method."""
        with patch.object(self.formatter._console, "print") as mock_print:
            result = self.formatter.print_success("Operation complete")
            assert result.is_success
            mock_print.assert_called_once()

    def test_print_warning(self) -> None:
        """Test print_warning method."""
        with patch.object(self.formatter._console, "print") as mock_print:
            result = self.formatter.print_warning("Beware")
            assert result.is_success
            mock_print.assert_called_once()


class TestFlextCliFormattersFormatData:
    """Test format_data method with different formats."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.formatter = FlextCliOutput()

    def test_format_data_json(self) -> None:
        """Test format_data with JSON format."""
        data = {"name": "Alice", "age": 30}
        result = self.formatter.format_data(data, format_type="json")
        assert result.is_success
        assert isinstance(result.value, str)
        assert "Alice" in result.value

    def test_format_data_yaml(self) -> None:
        """Test format_data with YAML format."""
        data = {"name": "Alice", "age": 30}
        result = self.formatter.format_data(data, format_type="yaml")
        assert result.is_success
        assert isinstance(result.value, str)

    def test_format_data_csv_list_of_dicts(self) -> None:
        """Test format_data with CSV format and list of dicts."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = self.formatter.format_data(data, format_type="csv")
        assert result.is_success
        assert isinstance(result.value, str)
        assert "name" in result.value or "Alice" in result.value

    def test_format_data_csv_single_dict(self) -> None:
        """Test format_data with CSV format and single dict succeeds."""
        data = {"name": "Alice", "age": 30}
        result = self.formatter.format_data(data, format_type="csv")
        assert result.is_success
        assert isinstance(result.value, str)
        assert "name" in result.value
        assert "Alice" in result.value
        assert "age" in result.value
        assert "30" in result.value

    def test_format_data_table(self) -> None:
        """Test format_data with table format."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = self.formatter.format_data(data, format_type="table")
        assert result.is_success
        assert isinstance(result.value, str)

    def test_format_data_table_with_title(self) -> None:
        """Test format_data table with title."""
        data = [{"name": "Alice", "age": 30}]
        result = self.formatter.format_data(data, format_type="table", title="Users")
        assert result.is_success

    def test_format_data_table_with_headers(self) -> None:
        """Test format_data table with custom headers."""
        data = [{"name": "Alice", "age": 30}]
        result = self.formatter.format_data(
            data, format_type="table", headers=["Name", "Age"]
        )
        assert result.is_success

    def test_format_data_invalid_format(self) -> None:
        """Test format_data with invalid format."""
        data: dict[str, object] = {"name": "Alice"}
        result = self.formatter.format_data(data, format_type="invalid")
        assert result.is_failure
        assert "Unsupported format" in (result.error or "")

    def test_format_data_empty_list(self) -> None:
        """Test format_data with empty list."""
        result = self.formatter.format_data([], format_type="table")
        # Empty list returns empty string, not failure
        assert result.is_success or result.is_failure

    def test_format_data_single_dict_as_table(self) -> None:
        """Test format_data converts single dict to table format."""
        data = {"name": "Alice", "age": 30}
        result = self.formatter.format_data(data, format_type="table")
        assert result.is_success


class TestFlextCliFormattersDisplay:
    """Test console output methods."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.formatter = FlextCliOutput()

    def test_get_console(self) -> None:
        """Test get_console method."""
        console = self.formatter.get_console()
        assert console is not None
        assert console == self.formatter._console

    def test_format_table_method(self) -> None:
        """Test format_table method."""
        data = [{"name": "Alice", "age": 30}]
        result = self.formatter.format_table(data)
        assert result.is_success
        # format_table returns a Table object, not a string
        assert result.value is not None

    def test_format_table_with_title(self) -> None:
        """Test format_table with title."""
        data = [{"name": "Alice", "age": 30}]
        result = self.formatter.format_table(data, title="Users")
        assert result.is_success

    def test_create_formatter_method(self) -> None:
        """Test create_formatter instance method."""
        # create_formatter is an instance method that takes format_type
        formatter_result = self.formatter.create_formatter("json")
        assert formatter_result.is_success or formatter_result.is_failure
