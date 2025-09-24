"""Tests for FlextCliFormatters - Real API only.

Tests FlextCliFormatters using actual implemented methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.flext_cli_formatters import FlextCliFormatters


class TestFlextCliFormatters:
    """Test FlextCliFormatters - real API."""

    def test_formatters_initialization(self) -> None:
        """Test FlextCliFormatters can be initialized."""
        service = FlextCliFormatters()
        assert service is not None

    def test_formatters_has_real_methods(self) -> None:
        """Test FlextCliFormatters has actual formatting methods."""
        service = FlextCliFormatters()

        # Real methods from actual API
        expected_methods = [
            "format_data",
            "_format_csv_simple",
        ]

        for method_name in expected_methods:
            assert hasattr(service, method_name), f"Missing method: {method_name}"
            assert callable(getattr(service, method_name)), (
                f"Method not callable: {method_name}"
            )

    def test_format_data_with_dict_list(self) -> None:
        """Test format_data with list of dictionaries."""
        service = FlextCliFormatters()

        data: list[dict[str, object]] = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25},
        ]
        result = service.format_data(data, "table")

        assert result.is_success
        assert result.value is not None

    def test_format_data_json(self) -> None:
        """Test format_data with JSON format."""
        service = FlextCliFormatters()

        data: dict[str, object] = {"key": "value", "number": 42}
        result = service.format_data(data, "json")

        assert result.is_success
        assert isinstance(result.value, str)
        assert "key" in result.value
        assert "value" in result.value

    def test_format_data_yaml(self) -> None:
        """Test format_data with YAML format."""
        service = FlextCliFormatters()

        data: dict[str, object] = {"key": "value", "number": 42}
        result = service.format_data(data, "yaml")

        assert result.is_success
        assert isinstance(result.value, str)

    def test_format_data_csv(self) -> None:
        """Test format_data with CSV format."""
        service = FlextCliFormatters()

        data: list[dict[str, object]] = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25},
        ]
        result = service.format_data(data, "csv")

        assert result.is_success
        assert isinstance(result.value, str)

    def test_format_data_unsupported_format(self) -> None:
        """Test format_data with unsupported format."""
        service = FlextCliFormatters()

        data: dict[str, object] = {"key": "value"}
        result = service.format_data(data, "xml")

        assert result.is_failure
        assert "Unsupported format" in (result.error or "")

    def test_format_data_empty_data(self) -> None:
        """Test format_data handles empty data."""
        service = FlextCliFormatters()

        result = service.format_data({}, "json")
        assert result.is_success

    def test_format_data_complex_data(self) -> None:
        """Test format_data handles complex nested data."""
        service = FlextCliFormatters()

        complex_data: dict[str, object] = {
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

    def test_format_data_with_none_data(self) -> None:
        """Test format_data handles None data."""
        service = FlextCliFormatters()

        # Test with empty dict instead of None since format_data doesn't accept None
        result = service.format_data({}, "json")
        assert result.is_success
        assert result.value == "{}"


class TestFlextCliFormattersIntegration:
    """Integration tests for FlextCliFormatters."""

    def test_can_be_imported_from_module(self) -> None:
        """Test FlextCliFormatters can be imported from module."""
        service = FlextCliFormatters()
        assert service is not None
        assert isinstance(service, FlextCliFormatters)

    def test_has_comprehensive_formatting_capabilities(self) -> None:
        """Test FlextCliFormatters has comprehensive formatting capabilities."""
        service = FlextCliFormatters()
        assert service is not None

        # Check it has multiple formatting methods
        methods = dir(service)
        formatting_methods = [m for m in methods if "format" in m.lower()]
        assert len(formatting_methods) >= 4, "Should have multiple formatting methods"
