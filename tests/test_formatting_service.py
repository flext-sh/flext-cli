"""Tests for FlextCliFormatters - Real API only.

Tests FlextCliFormatters using actual implemented methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCliFormatters as ImportedService
from flext_cli.flext_cli_formatters import FlextCliFormatters


class TestFlextCliFormatters:
    """Test FlextCliFormatters - real API."""

    def test_formatting_service_initialization(self) -> None:
        """Test FlextCliFormatters can be initialized."""
        service = FlextCliFormatters()
        assert service is not None

    def test_formatting_service_has_real_methods(self) -> None:
        """Test FlextCliFormatters has actual formatting methods."""
        service = FlextCliFormatters()

        # Real methods from actual API
        expected_methods = [
            "format_table",
            "format_data",
            "create_table",
            "create_progress_bar",
            "print_message",
            "print_error",
            "print_success",
            "print_warning",
        ]

        for method_name in expected_methods:
            assert hasattr(service, method_name), f"Missing method: {method_name}"
            assert callable(getattr(service, method_name)), (
                f"Method not callable: {method_name}"
            )

    def test_format_table_with_dict_list(self) -> None:
        """Test format_table with list of dictionaries."""
        service = FlextCliFormatters()

        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        result = service.format_table(data)

        assert result.is_success
        assert result.value is not None

    def test_format_data_json(self) -> None:
        """Test format_data with JSON format."""
        service = FlextCliFormatters()

        data = {"key": "value", "number": 42}
        result = service.format_data(data, "json")

        assert result.is_success
        assert isinstance(result.value, str)
        assert "key" in result.value
        assert "value" in result.value

    def test_format_data_table(self) -> None:
        """Test format_data with table format."""
        service = FlextCliFormatters()

        data = {"key": "value", "number": 42}
        result = service.format_data(data, "table")

        assert result.is_success
        assert isinstance(result.value, str)

    def test_format_data_unsupported_format(self) -> None:
        """Test format_data with unsupported format."""
        service = FlextCliFormatters()

        data = {"key": "value"}
        result = service.format_data(data, "xml")

        assert result.is_failure
        assert "Unsupported format type" in (result.error or "")

    def test_create_progress_bar(self) -> None:
        """Test create_progress_bar method."""
        service = FlextCliFormatters()

        # Real signature: create_progress_bar(total: int, description: str = "Processing")
        result = service.create_progress_bar(total=100, description="Test")

        assert result.is_success
        assert result.value is not None

    def test_print_message(self) -> None:
        """Test print_message method."""
        service = FlextCliFormatters()

        result = service.print_message("Test message")
        assert result.is_success

    def test_print_error(self) -> None:
        """Test print_error method."""
        service = FlextCliFormatters()

        result = service.print_error("Error message")
        assert result.is_success

    def test_print_success(self) -> None:
        """Test print_success method."""
        service = FlextCliFormatters()

        result = service.print_success("Success message")
        assert result.is_success

    def test_print_warning(self) -> None:
        """Test print_warning method."""
        service = FlextCliFormatters()

        result = service.print_warning("Warning message")
        assert result.is_success


class TestFlextCliFormattersAdvanced:
    """Advanced tests for FlextCliFormatters."""

    def test_format_data_empty_data(self) -> None:
        """Test format_data handles empty data."""
        service = FlextCliFormatters()

        result = service.format_data({}, "json")
        assert result.is_success

    def test_format_data_complex_data(self) -> None:
        """Test format_data handles complex nested data."""
        service = FlextCliFormatters()

        complex_data = {
            "users": [
                {"name": "John", "details": {"age": 30, "city": "NYC"}},
                {"name": "Jane", "details": {"age": 25, "city": "LA"}},
            ],
            "metadata": {"count": 2, "timestamp": "2025-01-01"},
        }

        result = service.format_data(complex_data, "json")
        assert result.is_success
        assert "John" in result.value
        assert "Jane" in result.value

    def test_format_table_with_title(self) -> None:
        """Test format_table with title option."""
        service = FlextCliFormatters()

        data = [{"col1": "value1", "col2": "value2"}]
        result = service.format_table(data, title="Test Table")

        assert result.is_success
        assert result.value is not None

    def test_format_table_with_headers(self) -> None:
        """Test format_table with specific headers."""
        service = FlextCliFormatters()

        data = [{"col1": "value1", "col2": "value2"}]
        result = service.format_table(data, headers=["col1"])

        assert result.is_success
        assert result.value is not None


class TestFlextCliFormattersIntegration:
    """Integration tests for FlextCliFormatters."""

    def test_can_be_imported_from_main_package(self) -> None:
        """Test FlextCliFormatters can be imported from main package."""
        service = ImportedService()
        assert service is not None
        assert isinstance(service, FlextCliFormatters)

    def test_has_comprehensive_formatting_capabilities(self) -> None:
        """Test FlextCliFormatters has comprehensive formatting capabilities."""
        service = FlextCliFormatters()
        assert service is not None

        # Check it has multiple formatting methods
        methods = dir(service)
        formatting_methods = [
            m for m in methods if "format" in m or "print" in m or "create" in m
        ]
        assert len(formatting_methods) >= 5, "Should have multiple formatting methods"
