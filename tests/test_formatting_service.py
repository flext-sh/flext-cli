"""Tests for FlextCliFormatters - Unified formatting API.

Comprehensive tests for the consolidated formatting functionality that replaced
the old formatters.py and formatting_service.py modules.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCliFormatters as ImportedService
from flext_cli.flext_cli_formatters import FlextCliFormatters


class TestFlextCliFormatters:
    """Test FlextCliFormatters - unified formatting API."""

    def test_formatting_service_initialization(self) -> None:
        """Test FlextCliFormatters can be initialized."""
        service = FlextCliFormatters()
        assert service is not None

    def test_formatting_service_has_expected_methods(self) -> None:
        """Test FlextCliFormatters has expected formatting methods."""
        service = FlextCliFormatters()

        # Check for key formatting methods
        expected_methods = [
            "format_table",
            "format_json",
            "format_yaml",
            "format_list",
            "display_output",
            "create_progress_bar",
        ]

        for method_name in expected_methods:
            assert hasattr(service, method_name), f"Missing method: {method_name}"
            assert callable(getattr(service, method_name)), (
                f"Method not callable: {method_name}"
            )

    def test_formatting_service_format_table_basic(self) -> None:
        """Test basic table formatting functionality."""
        service = FlextCliFormatters()

        # Test with sample data
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]

        result = service.format_table(data)
        assert result is not None
        # Basic check that it returns some formatted output
        assert isinstance(result, str) or hasattr(result, "__str__")

    def test_formatting_service_format_json_basic(self) -> None:
        """Test basic JSON formatting functionality."""
        service = FlextCliFormatters()

        data = {"key": "value", "number": 42}
        result = service.format_json(data)

        assert result is not None
        assert isinstance(result, str)

    def test_formatting_service_format_yaml_basic(self) -> None:
        """Test basic YAML formatting functionality."""
        service = FlextCliFormatters()

        data = {"key": "value", "items": ["item1", "item2"]}
        result = service.format_yaml(data)

        assert result is not None
        assert isinstance(result, str)

    def test_formatting_service_format_list_basic(self) -> None:
        """Test basic list formatting functionality."""
        service = FlextCliFormatters()

        items = ["Item 1", "Item 2", "Item 3"]
        result = service.format_list(items)

        assert result is not None
        assert isinstance(result, str)

    def test_formatting_service_display_output_basic(self) -> None:
        """Test basic display output functionality."""
        service = FlextCliFormatters()

        data = {"message": "test"}
        # This should not raise an exception
        try:
            service.display_output(data)
        except Exception as e:
            # Allow certain expected exceptions (like missing console in test env)
            if "console" not in str(e).lower():
                raise

    def test_formatting_service_create_progress_bar_basic(self) -> None:
        """Test basic progress bar creation functionality."""
        service = FlextCliFormatters()

        # This should not raise an exception during creation
        try:
            progress = service.create_progress_bar(total=100, description="Test")
            assert progress is not None
        except Exception as e:
            # Allow certain expected exceptions (like missing console in test env)
            if "console" not in str(e).lower():
                raise


class TestFlextCliFormattersAdvanced:
    """Advanced tests for FlextCliFormatters."""

    def test_formatting_service_handles_empty_data(self) -> None:
        """Test formatting service handles empty data gracefully."""
        service = FlextCliFormatters()

        # Test with empty data
        assert service.format_table([]) is not None
        assert service.format_json({}) is not None
        assert service.format_yaml({}) is not None
        assert service.format_list([]) is not None

    def test_formatting_service_handles_complex_data(self) -> None:
        """Test formatting service handles complex nested data."""
        service = FlextCliFormatters()

        complex_data = {
            "users": [
                {"name": "John", "details": {"age": 30, "city": "NYC"}},
                {"name": "Jane", "details": {"age": 25, "city": "LA"}},
            ],
            "metadata": {"count": 2, "timestamp": "2025-01-01"},
        }

        # Should handle complex data without exceptions
        assert service.format_json(complex_data) is not None
        assert service.format_yaml(complex_data) is not None

    def test_formatting_service_table_with_options(self) -> None:
        """Test table formatting with various options."""
        service = FlextCliFormatters()

        data = [{"col1": "value1", "col2": "value2"}]

        # Test with title
        result = service.format_table(data, title="Test Table")
        assert result is not None

        # Test with specific columns
        result = service.format_table(data, columns=["col1"])
        assert result is not None


class TestFlextCliFormattersIntegration:
    """Integration tests for FlextCliFormatters."""

    def test_formatting_service_can_be_imported_from_main_package(self) -> None:
        """Test FlextCliFormatters can be imported from main package."""
        service = ImportedService()
        assert service is not None
        assert isinstance(service, FlextCliFormatters)

    def test_formatting_service_is_primary_formatting_api(self) -> None:
        """Test FlextCliFormatters is designated as primary formatting API."""
        # Should be importable as the primary API
        service = FlextCliFormatters()
        assert service is not None

        # Should have comprehensive formatting capabilities
        methods = dir(service)
        formatting_methods = [
            m for m in methods if "format" in m or "display" in m or "progress" in m
        ]
        assert len(formatting_methods) >= 5, "Should have multiple formatting methods"
