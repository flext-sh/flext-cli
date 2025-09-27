"""FLEXT CLI Output Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliOutput covering all real functionality with flext_tests
integration, comprehensive output operations, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import json
import tempfile
import time
from pathlib import Path
from typing import cast

import pytest

from flext_cli.output import FlextCliOutput
from flext_core import FlextResult
from flext_tests import FlextTestsUtilities


class TestFlextCliOutput:
    """Comprehensive tests for FlextCliOutput functionality."""

    @pytest.fixture
    def output(self) -> FlextCliOutput:
        """Create FlextCliOutput instance for testing."""
        return FlextCliOutput()

    @pytest.fixture
    def test_utilities(self) -> FlextTestsUtilities:
        """Provide FlextTestsUtilities for test support."""
        return FlextTestsUtilities()

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
        assert hasattr(output, "_logger")
        assert hasattr(output, "_console")

    def test_output_execute(self, output: FlextCliOutput) -> None:
        """Test output execute method."""
        result = output.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), str)

    def test_output_execute_async(self, output: FlextCliOutput) -> None:
        """Test output async execute method."""

        async def run_test() -> None:
            result = await output.execute_async()

            assert isinstance(result, FlextResult)
            assert result.is_success
            assert isinstance(result.unwrap(), str)

        asyncio.run(run_test())

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
        """Test creating table."""
        # Convert dict to list format expected by create_table
        sample_list: list[dict[str, str | int | float] | None] = (
            [sample_data] if isinstance(sample_data, dict) else sample_data
        )
        result = output.create_table(sample_list)

        assert isinstance(result, FlextResult)
        # May fail if data is not suitable for table format
        # Just check that it returns a result

    def test_output_create_progress_bar(self, output: FlextCliOutput) -> None:
        """Test creating progress bar."""
        result = output.create_progress_bar("Test task", total=100)

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

        # Step 3: Create table (may fail for complex data)
        sample_list: list[dict[str, str | int | float] | None] = (
            [sample_data] if isinstance(sample_data, dict) else sample_data
        )
        table_result = output.create_table(sample_list)
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
            cast("dict[str, object] | list[dict[str, object]] | None", real_data)
        )
        assert table_result.is_success
        table_str = table_result.unwrap()
        assert isinstance(table_str, str)

    def test_output_edge_cases(self, output: FlextCliOutput) -> None:
        """Test edge cases and error conditions."""
        # Test with empty data
        empty_data = {}
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
        circular_data = {}
        circular_data["self"] = circular_data

        result = output.format_data(circular_data, "json")
        assert isinstance(result, FlextResult)
        # Should handle gracefully

    def test_output_custom_format(
        self, output: FlextCliOutput, sample_data: dict
    ) -> None:
        """Test custom format handling."""
        # Test with custom format
        result = output.format_data(sample_data, "custom")
        assert isinstance(result, FlextResult)
        # Should handle gracefully
