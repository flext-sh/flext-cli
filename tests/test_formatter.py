"""Tests for FlextCliFormatter - Output formatting utilities."""

from __future__ import annotations

import json
from typing import Any

import pytest
from flext_cli import FlextCliFormatter


class TestFlextCliFormatter:
    """Test FlextCliFormatter functionality."""

    @pytest.fixture
    def formatter(self) -> FlextCliFormatter:
        """FlextCliFormatter instance."""
        return FlextCliFormatter()

    @pytest.fixture
    def sample_data(self) -> list[dict[str, Any]]:
        """Sample test data."""
        return [
            {"id": 1, "name": "Alice", "role": "Admin", "status": "Active"},
            {"id": 2, "name": "Bob", "role": "User", "status": "Inactive"},
            {"id": 3, "name": "Charlie", "role": "Manager", "status": "Active"},
        ]

    def test_json_formatting(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test JSON formatting."""
        formatter.style = "json"
        result = formatter.format(sample_data)

        assert isinstance(result, str)
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert len(parsed) == 3
        assert parsed[0]["name"] == "Alice"

    def test_json_formatting_with_title(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test JSON formatting with title."""
        formatter.style = "json"
        result = formatter.format(sample_data, title="Test Data")

        assert isinstance(result, str)
        # Should still be valid JSON
        json.loads(result)  # Should not raise exception

    def test_yaml_formatting(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test YAML formatting."""
        formatter.style = "yaml"
        result = formatter.format(sample_data)

        assert isinstance(result, str)
        # Should contain YAML-like structure
        assert "- id: 1" in result or "id: 1" in result

    def test_table_formatting(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test table formatting."""
        formatter.style = "table"
        result = formatter.format(sample_data)

        assert isinstance(result, str)
        assert "|" in result  # Table borders

    def test_rich_formatting(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test Rich formatting."""
        formatter.style = "rich"
        result = formatter.format(sample_data)

        assert isinstance(result, str)
        assert "Alice" in result

    def test_simple_formatting(self, formatter: FlextCliFormatter) -> None:
        """Test simple text formatting."""
        formatter.style = "simple"
        result = formatter.format("test data")

        assert isinstance(result, str)
        assert result == "test data"

    def test_format_with_title(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test formatting with title."""
        result = formatter.format(sample_data, title="Employee Data")

        assert isinstance(result, str)
        assert "Employee Data" in result

    def test_get_available_styles(self, formatter: FlextCliFormatter) -> None:
        """Test getting available styles."""
        styles = formatter.get_available_styles()

        assert isinstance(styles, list)
        assert "json" in styles
        assert "yaml" in styles
        assert "table" in styles

    def test_tabulate_formatting(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test tabulate table formatting."""
        result = formatter.format_tabulate_table(sample_data, "Test Table", "grid")

        assert result.success
        table_str = result.data
        assert isinstance(table_str, str)
        assert "+" in table_str or "|" in table_str  # Table borders

    def test_tabulate_different_formats(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test different tabulate formats."""
        formats = ["grid", "fancy_grid", "pipe", "simple", "plain"]

        for fmt in formats:
            result = formatter.format_tabulate_table(sample_data, f"Table {fmt}", fmt)
            assert result.success
            assert "Alice" in result.data

    def test_tabulate_empty_data(self, formatter: FlextCliFormatter) -> None:
        """Test tabulate with empty data."""
        result = formatter.format_tabulate_table([], "Empty Table")

        assert not result.success
        assert "No data to format" in result.error

    def test_data_summary(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test data summary generation."""
        result = formatter.format_data_summary(sample_data, "Data Analysis")

        assert result.success
        summary = result.data
        assert isinstance(summary, str)
        assert "Total records: 3" in summary
        assert "name:" in summary

    def test_data_summary_with_numeric_data(self, formatter: FlextCliFormatter) -> None:
        """Test data summary with numeric statistics."""
        numeric_data = [
            {"id": 1, "value": 10.5, "count": 5},
            {"id": 2, "value": 20.3, "count": 3},
            {"id": 3, "value": 15.7, "count": 7},
        ]

        result = formatter.format_data_summary(numeric_data, "Numeric Analysis")

        assert result.success
        summary = result.data
        assert "Mean:" in summary

    def test_data_summary_empty_data(self, formatter: FlextCliFormatter) -> None:
        """Test data summary with empty data."""
        result = formatter.format_data_summary([], "Empty Analysis")

        assert not result.success
        assert "No data to summarize" in result.error

    def test_export_preview(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test export preview generation."""
        result = formatter.format_export_preview(sample_data, "csv", 2)

        assert result.success
        preview = result.data
        assert isinstance(preview, str)
        assert "Alice" in preview

    def test_export_preview_different_formats(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test export preview for different formats."""
        formats = ["csv", "json", "yaml", "table"]

        for export_format in formats:
            result = formatter.format_export_preview(sample_data, export_format)
            assert result.success
            assert export_format.upper() in result.data

    def test_export_preview_empty_data(self, formatter: FlextCliFormatter) -> None:
        """Test export preview with empty data."""
        result = formatter.format_export_preview([], "csv")

        assert not result.success
        assert "No data to preview" in result.error

    def test_comparison_table(self, formatter: FlextCliFormatter) -> None:
        """Test comparison table generation."""
        before_data = [
            {"id": 1, "name": "Alice", "status": "Active"},
            {"id": 2, "name": "Bob", "status": "Inactive"},
        ]
        after_data = [
            {"id": 1, "name": "Alice", "status": "Inactive"},  # Changed
            {"id": 2, "name": "Bob", "status": "Inactive"},  # Same
            {"id": 3, "name": "Charlie", "status": "Active"},  # Added
        ]

        result = formatter.format_comparison_table(
            before_data,
            after_data,
            "Changes Analysis",
        )

        assert result.success
        comparison = result.data
        assert "ADDED" in comparison or "MODIFIED" in comparison

    def test_comparison_table_no_changes(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test comparison table with no changes."""
        result = formatter.format_comparison_table(
            sample_data,
            sample_data,
            "No Changes",
        )

        assert result.success
        assert "No changes detected" in result.data

    def test_get_available_tabulate_formats(self, formatter: FlextCliFormatter) -> None:
        """Test getting available tabulate formats."""
        formats = formatter.get_available_tabulate_formats()

        assert isinstance(formats, list)
        assert "grid" in formats
        assert "simple" in formats

    def test_format_with_data_export_integration(
        self,
        formatter: FlextCliFormatter,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test integrated formatting with export metadata."""
        result = formatter.format_with_data_export_integration(
            sample_data,
            "Test Data",
            export_formats=["csv", "json"],
            max_preview_rows=2,
        )

        assert result.success
        metadata = result.data
        assert "formatted_data" in metadata
        assert "export_previews" in metadata
        assert "estimated_sizes" in metadata

    def test_tree_formatting(self, formatter: FlextCliFormatter) -> None:
        """Test tree structure formatting."""
        tree_data = {
            "root": {
                "branch1": {"leaf1": "value1", "leaf2": "value2"},
                "branch2": {"leaf3": "value3"},
            },
        }

        result = formatter.format_tree(tree_data, "Tree Structure")

        assert result.success
        assert "root" in result

    def test_panel_formatting(self, formatter: FlextCliFormatter) -> None:
        """Test panel formatting."""
        content = "This is panel content"
        result = formatter.format_panel(content, "Test Panel")

        assert result.success
        assert len(result) > len(content)  # Should have formatting

    def test_columns_formatting(self, formatter: FlextCliFormatter) -> None:
        """Test columns formatting."""
        items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
        result = formatter.format_columns(items, "Test Columns")

        assert result.success
        assert "Item 1" in result

    def test_status_table_formatting(self, formatter: FlextCliFormatter) -> None:
        """Test status table formatting."""
        # Capture console output for status table
        status_data = [
            {"service": "API", "status": "UP", "response_time": "120ms"},
            {"service": "Database", "status": "UP", "response_time": "45ms"},
            {"service": "Cache", "status": "DOWN", "response_time": "N/A"},
        ]

        result = formatter.format_status_table(status_data, "Service Status")

        assert result.success
        status_str = result.data
        assert "UP" in status_str
        assert "DOWN" in status_str

    def test_rich_formatter_creation(self, formatter: FlextCliFormatter) -> None:
        """Test Rich formatter creation."""
        rich_formatter = FlextCliFormatter(style="rich")
        assert rich_formatter.style == "rich"

    def test_format_error_handling(self, formatter: FlextCliFormatter) -> None:
        """Test formatting error handling."""
        # Test with data that might cause formatting issues
        problematic_data = {
            "circular_ref": None,  # Will be set to create circular reference
            "unicode": "café ☕",
            "special_chars": "!@#$%^&*()",
        }
        # Create circular reference
        problematic_data["circular_ref"] = problematic_data

        # Should handle gracefully
        result = formatter.format(problematic_data, style="json")
        assert isinstance(result, str)
        # Should contain some representation of the data

    def test_complex_nested_data_formatting(
        self,
        formatter: FlextCliFormatter,
    ) -> None:
        """Test formatting of complex nested data structures."""
        complex_data = {
            "users": [
                {
                    "id": 1,
                    "profile": {
                        "name": "Alice",
                        "email": "alice@example.com",
                        "preferences": {
                            "theme": "dark",
                            "notifications": True,
                            "languages": ["en", "pt"],
                        },
                    },
                    "roles": ["REDACTED_LDAP_BIND_PASSWORD", "user"],
                    "metadata": {
                        "created_at": "2023-01-01T00:00:00Z",
                        "last_login": "2023-12-01T10:30:00Z",
                        "login_count": 42,
                    },
                },
            ],
            "settings": {
                "app_name": "TestApp",
                "version": "1.0.0",
                "features": {
                    "feature1": {"enabled": True, "config": {"timeout": 30}},
                    "feature2": {"enabled": False, "config": {}},
                },
            },
        }

        # Test different styles
        styles = ["json", "yaml", "table"]
        for style in styles:
            formatter.style = style
            result = formatter.format(complex_data)
            assert isinstance(result, str)
            assert "alice@example.com" in result

    def test_unicode_data_handling(self, formatter: FlextCliFormatter) -> None:
        """Test handling of Unicode data."""
        unicode_data = [
            {"name": "José", "city": "São Paulo", "emoji": "🚀"},
            {"name": "Müller", "city": "München", "emoji": "🎯"},
            {"name": "李小明", "city": "北京", "emoji": "🐉"},
        ]

        result = formatter.format(unicode_data, style="json")
        assert isinstance(result, str)
        assert "José" in result
        assert "🚀" in result
