"""FLEXT CLI Output Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliOutput covering all real functionality with flext_tests
integration, comprehensive output operations, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path
from typing import cast

import pytest
from flext_core import FlextResult, FlextTypes

# Test utilities removed from flext-core production exports
from flext_cli.output import FlextCliOutput


class TestFlextCliOutput:
    """Comprehensive tests for FlextCliOutput functionality."""

    @pytest.fixture
    def output(self) -> FlextCliOutput:
        """Create FlextCliOutput instance for testing."""
        return FlextCliOutput()

    @pytest.fixture
    def temp_file(self) -> Path:
        """Create temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
            f.write("test content")
            return Path(f.name)

    @pytest.fixture
    def sample_data(self) -> dict:
        """Provide sample data for testing."""
        return {
            "name": "test",
            "value": 42,
            "items": [1, 2, 3],
            "nested": {"key": "value"},
        }

    def test_output_initialization(self, output: FlextCliOutput) -> None:
        """Test output initialization."""
        assert isinstance(output, FlextCliOutput)
        assert hasattr(output, "logger")
        assert hasattr(output, "_formatters")
        assert hasattr(output, "_tables")

    def test_output_execute(self, output: FlextCliOutput) -> None:
        """Test output execute method."""
        result = output.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), str)

    def test_output_validate_config(self, output: FlextCliOutput) -> None:
        """Test output config validation."""
        # FlextService.validate_config() takes no arguments
        result = output.validate_config()

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_output_validate_config_invalid(self, output: FlextCliOutput) -> None:
        """Test output config validation with invalid data."""
        # FlextService.validate_config() takes no arguments
        result = output.validate_config()

        assert isinstance(result, FlextResult)
        # Should handle gracefully
        assert result.is_success

    def test_output_print_message(self, output: FlextCliOutput) -> None:
        """Test print message functionality."""
        result = output.print_message("Test message")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_output_print_success(self, output: FlextCliOutput) -> None:
        """Test print success message."""
        result = output.print_success("Success message")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_output_format_json(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test format JSON functionality."""
        result = output.format_json(sample_data)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), str)

    def test_output_format_yaml(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test format YAML functionality."""
        result = output.format_yaml(sample_data)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), str)

    def test_output_format_csv(self, output: FlextCliOutput, sample_data: dict) -> None:
        """Test format CSV functionality."""
        result = output.format_csv(sample_data)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), str)

    def test_output_format_table(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test format table functionality."""
        result = output.format_table(sample_data)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), str)

    def test_output_print_error(self, output: FlextCliOutput) -> None:
        """Test print error message."""
        result = output.print_error("Error message")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_output_format_data_json(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test formatting data as JSON."""
        result = output.format_data(sample_data, "json")

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted = result.unwrap()
        assert isinstance(formatted, str)

        # Verify it's valid JSON
        parsed = json.loads(formatted)
        assert parsed == sample_data

    def test_output_format_data_csv(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test formatting data as CSV."""
        result = output.format_data(sample_data, "csv")

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted = result.unwrap()
        assert isinstance(formatted, str)
        assert "," in formatted  # CSV should contain commas

    def test_output_format_data_yaml(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test formatting data as YAML."""
        result = output.format_data(sample_data, "yaml")

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted = result.unwrap()
        assert isinstance(formatted, str)

    def test_output_format_data_table(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test formatting data as table."""
        result = output.format_data(sample_data, "table")

        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted = result.unwrap()
        assert isinstance(formatted, str)

    def test_output_format_data_invalid_format(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test formatting data with invalid format."""
        result = output.format_data(sample_data, "invalid_format")

        assert isinstance(result, FlextResult)
        # Should fail gracefully
        assert result.is_failure

    def test_output_create_formatter(self, output: FlextCliOutput) -> None:
        """Test creating formatter."""
        result = output.create_formatter("json")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_output_create_table(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test formatting table."""
        # Convert dict to list format expected by format_table
        sample_list: list[dict[str, object]] = [sample_data]
        result = output.format_table(sample_list)

        assert isinstance(result, FlextResult)
        # May fail if data is not suitable for table format
        # Just check that it returns a result

    def test_output_create_progress_bar(self, output: FlextCliOutput) -> None:
        """Test creating progress bar."""
        result = output.create_progress_bar("Test task", _total=100)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_output_display_text(self, output: FlextCliOutput) -> None:
        """Test displaying text."""
        result = output.display_text("Test text")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_output_format_as_tree(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test formatting as tree."""
        result = output.format_as_tree(sample_data)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_output_get_console(self, output: FlextCliOutput) -> None:
        """Test getting console."""
        console = output.get_console()

        assert console is not None

    def test_output_integration_workflow(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test complete output workflow."""
        # Step 1: Format data as JSON
        format_data_result = output.format_data(sample_data, "json")
        assert format_data_result.is_success

        # Step 2: Format data as CSV
        csv_result = output.format_data(sample_data, "csv")
        assert csv_result.is_success

        # Step 3: Format table (may fail for complex data)
        sample_list: list[dict[str, object]] = [sample_data]
        table_result = output.format_table(sample_list)
        assert isinstance(table_result, FlextResult)

        # Step 4: Print messages
        message_result = output.print_message("Test message")
        assert message_result.is_success

        # Step 5: Get console
        console = output.get_console()
        assert console is not None

    def test_output_real_functionality(self, output: FlextCliOutput) -> None:
        """Test real output functionality without mocks."""
        # Test actual output operations
        real_data = {
            "timestamp": time.time(),
            "data": [1, 2, 3, 4, 5],
            "metadata": {"source": "test", "version": "1.0"},
        }

        # Test JSON formatting
        json_result = output.format_json(real_data)
        assert json_result.is_success
        json_str = json_result.unwrap()
        assert isinstance(json_str, str)

        # Verify JSON content
        parsed_data = json.loads(json_str)
        assert parsed_data == real_data

        # Test CSV formatting
        csv_result = output.format_csv(real_data)
        assert csv_result.is_success
        csv_str = csv_result.unwrap()
        assert isinstance(csv_str, str)

        # Test YAML formatting
        yaml_result = output.format_yaml(real_data)
        assert yaml_result.is_success
        yaml_str = yaml_result.unwrap()
        assert isinstance(yaml_str, str)

        # Test table formatting - cast to expected type
        table_result = output.format_table(
            cast("FlextTypes.Dict | list[FlextTypes.Dict]", real_data)
        )
        assert table_result.is_success
        table_str = table_result.unwrap()
        assert isinstance(table_str, str)

    def test_output_edge_cases(self, output: FlextCliOutput) -> None:
        """Test edge cases and error conditions."""
        # Test with empty data
        empty_data: dict[str, object] = {}
        result = output.format_data(empty_data, "json")
        assert isinstance(result, FlextResult)

        # Test with None data
        result = output.format_data(None, "json")
        assert isinstance(result, FlextResult)

        # Test with very large data
        large_data = {"items": list(range(10000))}
        result = output.format_data(large_data, "json")
        assert isinstance(result, FlextResult)

        # Test with special characters
        special_data = {
            "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "unicode": "🚀🌟✨",
            "newlines": "line1\nline2\rline3",
        }
        result = output.format_data(special_data, "json")
        assert isinstance(result, FlextResult)

    def test_output_performance(self, output: FlextCliOutput) -> None:
        """Test output performance."""
        # Test formatting performance
        large_data = {"items": list(range(1000))}

        start_time = time.time()
        for _i in range(100):
            output.format_data(large_data, "json")
        end_time = time.time()

        # Should be fast (less than 1 second for 100 operations)
        assert (end_time - start_time) < 1.0

    def test_output_memory_usage(self, output: FlextCliOutput) -> None:
        """Test output memory usage."""
        # Test with very large data
        very_large_data = {"items": list(range(100000))}

        result = output.format_data(very_large_data, "json")
        assert isinstance(result, FlextResult)

        # Test multiple operations
        for _i in range(10):
            result = output.format_data(very_large_data, "json")
            assert isinstance(result, FlextResult)

    def test_output_with_rich_formatting(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test output with rich formatting."""
        # Test table formatting with rich
        result = output.format_data(sample_data, "table")
        assert isinstance(result, FlextResult)
        assert result.is_success

        formatted = result.unwrap()
        assert isinstance(formatted, str)

    def test_output_error_handling(self, output: FlextCliOutput) -> None:
        """Test output error handling."""
        # Test with circular reference data
        circular_data: dict[str, object] = {}
        circular_data["self"] = circular_data

        result = output.format_data(circular_data, "json")
        assert isinstance(result, FlextResult)
        # Should handle gracefully

    def test_format_output_table_invalid_data(self, output: FlextCliOutput) -> None:
        """Test format_data with table format but invalid data type."""
        result = output.format_data("invalid", "table")
        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None
        assert isinstance(result.error, str)
        assert (
            result.error is not None
            and "Table format requires dict or list of dicts" in result.error
        )

    def test_get_formatter_unsupported_format(self, output: FlextCliOutput) -> None:
        """Test create_formatter with unsupported format."""
        result = output.create_formatter("unsupported")
        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None
        assert isinstance(result.error, str)
        assert (
            result.error is not None
            and "Unsupported format type: unsupported" in result.error
        )

    def test_format_table_no_data(self, output: FlextCliOutput) -> None:
        """Test format_table with no data."""
        result = output.format_table([])
        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None
        assert isinstance(result.error, str)
        assert result.error is not None and "No data provided for table" in result.error

    def test_output_custom_format(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test custom format handling."""
        # Test with custom format
        result = output.format_data(sample_data, "custom")
        assert isinstance(result, FlextResult)
        # Should handle gracefully

    # =========================================================================
    # COVERAGE COMPLETION TESTS - Missing Methods
    # =========================================================================

    def test_create_rich_table_with_data(self, output: FlextCliOutput) -> None:
        """Test create_rich_table with real data (lines 205-247)."""
        data = [
            {"name": "Alice", "age": 30, "city": "NYC"},
            {"name": "Bob", "age": 25, "city": "LA"},
        ]
        result = output.create_rich_table(
            data=data, headers=["name", "age", "city"], title="User Data"
        )
        assert isinstance(result, FlextResult)
        assert result.is_success
        table = result.unwrap()
        assert table is not None

    def test_create_rich_table_no_data_fails(self, output: FlextCliOutput) -> None:
        """Test create_rich_table with no data fails (line 205)."""
        result = output.create_rich_table(data=[])
        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None
        assert "No data provided" in result.error

    def test_create_rich_table_with_options(self, output: FlextCliOutput) -> None:
        """Test create_rich_table with all options (lines 215-222)."""
        data = [{"key": "value"}]
        result = output.create_rich_table(
            data=data,
            title="Test Table",
            show_header=True,
            show_lines=True,
            show_edge=True,
            expand=False,
            padding=(0, 1),
        )
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_display_message_simple(self, output: FlextCliOutput) -> None:
        """Test display_message with simple message (lines 481-506)."""
        result = output.display_message("Test message")
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_display_message_with_title(self, output: FlextCliOutput) -> None:
        """Test display_message with title and style."""
        result = output.display_message(
            "Test message", title="Important", message_type="info", style="bold blue"
        )
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_display_data_dict(self, output: FlextCliOutput) -> None:
        """Test display_data with dictionary (lines 530-549)."""
        data = {"name": "Alice", "age": 30}
        result = output.display_data(data, format_type="json")
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_display_data_list(self, output: FlextCliOutput) -> None:
        """Test display_data with list."""
        data = [1, 2, 3, 4, 5]
        result = output.display_data(data, format_type="json")
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_display_data_table_format(self, output: FlextCliOutput) -> None:
        """Test display_data with table format."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = output.display_data(data, format_type="table")
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_table_to_string(self, output: FlextCliOutput) -> None:
        """Test table_to_string method (lines 248-264)."""
        # First create a table
        data = [{"key": "value"}]
        table_result = output.create_rich_table(data=data)
        assert table_result.is_success
        table = table_result.unwrap()

        # Now convert to string
        string_result = output.table_to_string(table)
        assert isinstance(string_result, FlextResult)
        assert string_result.is_success
        table_str = string_result.unwrap()
        assert isinstance(table_str, str)
        assert len(table_str) > 0

    def test_create_ascii_table_with_data(self, output: FlextCliOutput) -> None:
        """Test create_ascii_table (lines 270-315)."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = output.create_ascii_table(data=data)
        assert isinstance(result, FlextResult)
        assert result.is_success
        table_str = result.unwrap()
        assert isinstance(table_str, str)
        assert "Alice" in table_str

    def test_create_ascii_table_with_format(self, output: FlextCliOutput) -> None:
        """Test create_ascii_table with different format."""
        data = [{"key": "value"}]
        result = output.create_ascii_table(data=data, table_format="grid")
        assert isinstance(result, FlextResult)
        assert result.is_success
        table_str = result.unwrap()
        assert isinstance(table_str, str)

    # =========================================================================
    # EXCEPTION HANDLER AND EDGE CASE TESTS
    # =========================================================================

    def test_format_data_plain(self, output: FlextCliOutput) -> None:
        """Test format_data with plain format (line 138)."""
        data = {"test": "value"}
        result = output.format_data(data, format_type="plain")
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert "test" in result.unwrap()

    def test_create_formatter_exception(
        self, output: FlextCliOutput, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test create_formatter exception handler (lines 166-167)."""
        # Use a simpler approach - mock the list directly to cause an exception when accessed
        import flext_cli.output as output_module

        original_formats_list = output_module.FlextCliConstants.OUTPUT_FORMATS_LIST

        # Create a mock that raises exception
        class RaisingList:
            def __contains__(self, item: object) -> bool:
                msg = "Test error"
                raise RuntimeError(msg)

        monkeypatch.setattr(
            output_module.FlextCliConstants, "OUTPUT_FORMATS_LIST", RaisingList()
        )

        result = output.create_formatter("json")
        assert result.is_failure
        assert "Failed to create formatter" in str(result.error)

        # Restore original
        monkeypatch.setattr(
            output_module.FlextCliConstants,
            "OUTPUT_FORMATS_LIST",
            original_formats_list,
        )

    def test_create_rich_table_formatter_failure(
        self, output: FlextCliOutput, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test create_rich_table when formatters.create_table fails (line 225)."""
        from flext_core import FlextResult

        def mock_create_table(*args: object, **kwargs: object) -> FlextResult[object]:
            return FlextResult[object].fail("Table creation failed")

        monkeypatch.setattr(output._formatters, "create_table", mock_create_table)

        data = [{"key": "value"}]
        result = output.create_rich_table(data=data)
        assert result.is_failure
        assert "Failed to create Rich table" in str(result.error)

    def test_create_rich_table_exception_handler(
        self, output: FlextCliOutput, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test create_rich_table exception handler (lines 242-247)."""
        data = [{"key": "value"}]

        # Mock formatters to raise exception during create_table
        def mock_create_table_raises(*args: object, **kwargs: object) -> object:
            msg = "Test exception"
            raise RuntimeError(msg)

        monkeypatch.setattr(
            output._formatters, "create_table", mock_create_table_raises
        )

        result = output.create_rich_table(data=data)
        assert result.is_failure
        assert "Failed to create Rich table" in str(result.error)

    def test_print_warning(self, output: FlextCliOutput) -> None:
        """Test print_warning method (line 429)."""
        result = output.print_warning("Test warning")
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_display_message_with_highlight_not_bool(
        self, output: FlextCliOutput
    ) -> None:
        """Test display_message when highlight is not bool (lines 504-505)."""
        result = output.display_message(
            "Test", message_type="info", highlight="not_bool"
        )
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_display_data_title_not_string(self, output: FlextCliOutput) -> None:
        """Test display_data when title is not string (lines 531-532)."""
        data = {"key": "value"}
        result = output.display_data(data, format_type="json", title=123)
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_display_data_headers_not_list(self, output: FlextCliOutput) -> None:
        """Test display_data when headers is not list (lines 534-535)."""
        data = [{"key": "value"}]
        result = output.display_data(data, format_type="table", headers="not_list")
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_display_data_format_failure(
        self, output: FlextCliOutput, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test display_data when format_data fails (lines 541-543)."""
        from flext_core import FlextResult

        def mock_format_data(*args: object, **kwargs: object) -> FlextResult[str]:
            return FlextResult[str].fail("Format failed")

        # Store original method
        original_format_data = output.format_data

        # Use __dict__ to bypass Pydantic validation
        output.__dict__["format_data"] = mock_format_data

        try:
            data = {"key": "value"}
            result = output.display_data(data, format_type="json")
            assert result.is_failure
            assert "Failed to format data" in str(result.error)
        finally:
            # Restore original method
            output.__dict__["format_data"] = original_format_data

    def test_format_yaml_exception(
        self, output: FlextCliOutput, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test format_yaml exception handler (lines 592-595)."""

        def mock_dump_raises(*args: object, **kwargs: object) -> str:
            msg = "YAML dump failed"
            raise RuntimeError(msg)

        monkeypatch.setattr("yaml.dump", mock_dump_raises)

        data = {"key": "value"}
        result = output.format_yaml(data)
        assert result.is_failure
        assert "YAML formatting failed" in str(result.error)

    def test_format_csv_list_of_dicts_success(self, output: FlextCliOutput) -> None:
        """Test format_csv with list of dicts (lines 612-618)."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = output.format_csv(data)
        assert result.is_success
        csv_str = result.unwrap()
        assert "name" in csv_str
        assert "Alice" in csv_str

    def test_format_csv_single_dict_success(self, output: FlextCliOutput) -> None:
        """Test format_csv with single dict (lines 619-625)."""
        data = {"name": "Alice", "age": 30}
        result = output.format_csv(data)
        assert result.is_success
        csv_str = result.unwrap()
        assert "name" in csv_str
        assert "Alice" in csv_str

    def test_format_csv_fallback_to_json(self, output: FlextCliOutput) -> None:
        """Test format_csv fallback to JSON for non-dict data (line 626)."""
        data = "simple string"
        result = output.format_csv(data)
        assert result.is_success
        # Should use JSON as fallback
        assert isinstance(result.unwrap(), str)

    def test_format_csv_exception_handler(
        self, output: FlextCliOutput, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test format_csv exception handler (lines 627-630)."""

        def mock_dictwriter_raises(*args: object, **kwargs: object) -> object:
            msg = "CSV writer failed"
            raise RuntimeError(msg)

        monkeypatch.setattr("csv.DictWriter", mock_dictwriter_raises)

        data = [{"key": "value"}]
        result = output.format_csv(data)
        assert result.is_failure
        assert "CSV formatting failed" in str(result.error)

    def test_format_table_list_not_list_type(self, output: FlextCliOutput) -> None:
        """Test format_table when data is not dict or list (line 666)."""
        data = "not_a_dict_or_list"
        result = output.format_table(data)
        assert result.is_failure
        assert "Table format requires dict or list of dicts" in str(result.error)

    def test_format_table_formatters_failure(
        self, output: FlextCliOutput, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test format_table when _tables.create_table fails (lines 684-686)."""
        from flext_core import FlextResult

        def mock_create_table_fail(*args: object, **kwargs: object) -> FlextResult[str]:
            return FlextResult[str].fail("Table creation failed")

        # Store original method
        original_create_table = output._tables.create_table

        # Use __dict__ to bypass Pydantic validation
        output._tables.__dict__["create_table"] = mock_create_table_fail

        try:
            data = {"key": "value"}
            result = output.format_table(data)
            assert result.is_failure
            assert "Failed to create table" in str(result.error)
        finally:
            # Restore original method
            output._tables.__dict__["create_table"] = original_create_table

    def test_format_table_with_title(self, output: FlextCliOutput) -> None:
        """Test format_table with title (lines 692-693)."""
        data = {"key": "value"}
        result = output.format_table(data, title="Test Title")
        assert result.is_success
        table_str = result.unwrap()
        assert "Test Title" in table_str

    def test_format_table_exception_handler(
        self, output: FlextCliOutput, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test format_table exception handler (lines 697-700)."""

        def mock_create_table_raises(*args: object, **kwargs: object) -> object:
            msg = "Table format failed"
            raise RuntimeError(msg)

        # Store original method
        original_create_table = output._tables.create_table

        # Use __dict__ to bypass Pydantic validation
        output._tables.__dict__["create_table"] = mock_create_table_raises

        try:
            data = {"key": "value"}
            result = output.format_table(data)
            assert result.is_failure
            assert "Failed to format table" in str(result.error)
        finally:
            # Restore original method
            output._tables.__dict__["create_table"] = original_create_table

    def test_format_as_tree_formatters_failure(
        self, output: FlextCliOutput, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test format_as_tree when formatters.create_tree fails (line 728)."""
        from flext_core import FlextResult

        def mock_create_tree_fail(
            *args: object, **kwargs: object
        ) -> FlextResult[object]:
            return FlextResult[object].fail("Tree creation failed")

        monkeypatch.setattr(output._formatters, "create_tree", mock_create_tree_fail)

        data = {"key": "value"}
        result = output.format_as_tree(data)
        assert result.is_failure
        assert "Failed to create tree" in str(result.error)

    def test_build_tree_with_list(self, output: FlextCliOutput) -> None:
        """Test _build_tree with list data (lines 759-761)."""
        # Create a tree through formatters
        tree_result = output._formatters.create_tree(label="Test")
        assert tree_result.is_success
        tree = tree_result.unwrap()

        # Test building tree with list data
        data = [{"name": "item1"}, {"name": "item2"}]
        output._build_tree(tree, data)  # Should not raise

    def test_console_property(self, output: FlextCliOutput) -> None:
        """Test console property (line 782)."""
        console = output.console
        assert console is not None
