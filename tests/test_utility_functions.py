"""Tests for utility functions - Zero-boilerplate CLI utilities."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
import yaml
from flext_cli import (
    flext_cli_analyze_data,
    flext_cli_create_dashboard,
    flext_cli_export_data,
    flext_cli_format_output,
    flext_cli_format_tabulate,
)


class TestUtilityFunctions:
    """Test utility functions that provide zero-boilerplate access."""

    @pytest.fixture
    def sample_data(self) -> list[dict[str, Any]]:
        """Sample test data."""
        return [
            {"id": 1, "name": "Alice", "age": 30, "salary": 75000.50},
            {"id": 2, "name": "Bob", "age": 25, "salary": 65000.75},
            {"id": 3, "name": "Carol", "age": 35, "salary": 85000.25},
        ]

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_flext_cli_export_data_csv(
        self,
        sample_data: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """Test CSV export utility function."""
        filepath = temp_dir / "test.csv"
        result = flext_cli_export_data(sample_data, str(filepath))

        assert result.success
        assert filepath.exists()
        assert "CSV" in result.data
        assert "3 records" in result.data

    def test_flext_cli_export_data_json(
        self,
        sample_data: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """Test JSON export utility function."""
        filepath = temp_dir / "test.json"
        result = flext_cli_export_data(sample_data, str(filepath))

        assert result.success
        assert filepath.exists()
        assert "JSON" in result.data

    def test_flext_cli_export_data_explicit_format(
        self,
        sample_data: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """Test export with explicitly specified format."""
        filepath = temp_dir / "test.txt"  # No extension
        result = flext_cli_export_data(sample_data, str(filepath), "json")

        assert result.success
        assert filepath.exists()

    def test_flext_cli_export_data_with_options(
        self,
        sample_data: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """Test export with custom options."""
        filepath = temp_dir / "test.csv"
        result = flext_cli_export_data(
            sample_data,
            str(filepath),
            delimiter=";",
        )

        assert result.success

        # Verify custom delimiter was used
        content = filepath.read_text()
        assert ";" in content

    def test_flext_cli_export_data_empty_data(self, temp_dir: Path) -> None:
        """Test export with empty data."""
        filepath = temp_dir / "empty.csv"
        result = flext_cli_export_data([], str(filepath))

        assert not result.success
        assert "No data to export" in result.error

    def test_flext_cli_format_tabulate_grid(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test tabulate formatting with grid style."""
        result = flext_cli_format_tabulate(sample_data, "Employee Data", "grid")

        assert result.success
        table_str = result.data

        assert "Employee Data" in table_str
        assert "Alice" in table_str
        assert "+" in table_str or "|" in table_str  # Grid formatting

    def test_flext_cli_format_tabulate_fancy_grid(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test tabulate formatting with fancy grid style."""
        result = flext_cli_format_tabulate(
            sample_data,
            "Fancy Table",
            "fancy_grid",
        )

        assert result.success
        assert "Alice" in result.data

    def test_flext_cli_format_tabulate_pipe(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test tabulate formatting with pipe style."""
        result = flext_cli_format_tabulate(sample_data, "Pipe Table", "pipe")

        assert result.success
        assert "Alice" in result.data
        assert "|" in result.data

    def test_flext_cli_format_tabulate_custom_options(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test tabulate formatting with custom options."""
        result = flext_cli_format_tabulate(
            sample_data,
            "Custom Table",
            "grid",
            headers="keys",
            showindex=False,
            numalign="right",
            stralign="left",
        )

        assert result.success
        assert "Alice" in result.data

    def test_flext_cli_format_tabulate_empty_data(self) -> None:
        """Test tabulate formatting with empty data."""
        result = flext_cli_format_tabulate([], "Empty Table")

        assert not result.success
        assert "No data to format" in result.error

    def test_flext_cli_analyze_data_basic(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test basic data analysis."""
        result = flext_cli_analyze_data(sample_data, "Employee Analysis")

        assert result.success
        analysis = result.data

        assert "Employee Analysis" in analysis
        assert "3 records" in analysis
        assert "Alice" in analysis
        assert "Bob" in analysis
        assert "Carol" in analysis

    def test_flext_cli_analyze_data_numeric_stats(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test numeric statistics analysis."""
        result = flext_cli_analyze_data(sample_data, "Numeric Analysis")

        assert result.success
        analysis = result.data

        # Check for numeric statistics
        assert "age" in analysis.lower()
        assert "salary" in analysis.lower()
        # Should contain statistical information
        assert any(stat in analysis.lower() for stat in ["min", "max", "avg", "sum"])

    def test_flext_cli_analyze_data_mixed_types(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test analysis with mixed data types."""
        mixed_data = [
            {"id": 1, "name": "Alice", "active": True, "score": 95.5},
            {"id": 2, "name": "Bob", "active": False, "score": 87.2},
            {"id": 3, "name": "Carol", "active": True, "score": 92.8},
        ]

        result = flext_cli_analyze_data(mixed_data, "Mixed Data Analysis")

        assert result.success
        analysis = result.data

        assert "Mixed Data Analysis" in analysis
        assert "3 records" in analysis

    def test_flext_cli_analyze_data_empty_data(self) -> None:
        """Test analysis with empty data."""
        result = flext_cli_analyze_data([], "Empty Analysis")

        assert not result.success
        assert "No data to analyze" in result.error

    def test_flext_cli_create_dashboard_basic(self) -> None:
        """Test basic dashboard creation."""
        result = flext_cli_create_dashboard("Test Dashboard")

        assert result.success
        dashboard = result.data
        assert dashboard is not None

    def test_flext_cli_create_dashboard_with_config(self) -> None:
        """Test dashboard creation with configuration."""
        config = {"theme": "dark", "layout": "grid"}
        result = flext_cli_create_dashboard("Configured Dashboard", config)

        assert result.success
        dashboard = result.data
        assert dashboard is not None

    def test_flext_cli_format_output_rich(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test output formatting with Rich style."""
        result = flext_cli_format_output(sample_data, "rich")

        assert result.success
        formatted = result.data
        assert "Alice" in formatted

    def test_flext_cli_format_output_json(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test output formatting with JSON style."""
        result = flext_cli_format_output(sample_data, "json")

        assert result.success
        formatted = result.data

        # Verify it's valid JSON
        json.loads(formatted)

    def test_flext_cli_format_output_yaml(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test output formatting with YAML style."""
        result = flext_cli_format_output(sample_data, "yaml")

        assert result.success
        formatted = result.data

        # Verify it's valid YAML
        yaml.safe_load(formatted)
        assert "- " in formatted or "id:" in formatted  # YAML format indicators

    def test_flext_cli_format_output_table(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test output formatting with table style."""
        result = flext_cli_format_output(sample_data, "table")

        assert result.success
        formatted = result.data

        assert "|" in formatted or "-" in formatted  # Table formatting

    def test_flext_cli_format_output_default_style(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test output formatting with default style."""
        result = flext_cli_format_output(sample_data)  # No style specified

        assert result.success
        formatted = result.data
        assert "Alice" in formatted

    def test_flext_cli_format_output_simple_data(self) -> None:
        """Test output formatting with simple data types."""
        simple_data = {"name": "Test", "value": 42, "active": True}
        result = flext_cli_format_output(simple_data, "json")

        assert result.success
        formatted = result.data
        json.loads(formatted)  # Should be valid JSON

    def test_flext_cli_format_output_complex_data(self) -> None:
        """Test output formatting with complex nested data."""
        complex_data = {
            "users": [
                {
                    "id": 1,
                    "profile": {"name": "Alice", "preferences": {"theme": "dark"}},
                },
                {
                    "id": 2,
                    "profile": {"name": "Bob", "preferences": {"theme": "light"}},
                },
            ],
            "metadata": {
                "total": 2,
                "created_at": "2024-01-15T10:30:00Z",
                "tags": ["active", "verified"],
            },
        }

        result = flext_cli_format_output(complex_data, "json")

        assert result.success
        formatted = result.data
        parsed = json.loads(formatted)

        assert "users" in parsed
        assert "metadata" in parsed
        assert len(parsed["users"]) == 2

    def test_utility_functions_error_handling(self) -> None:
        """Test error handling in utility functions."""
        # Test with invalid file path
        result = flext_cli_export_data([{"test": "data"}], "/invalid/path/file.csv")
        assert not result.success

    def test_utility_functions_type_hints(self) -> None:
        """Test that utility functions have proper type hints."""
        import inspect

        functions = [
            flext_cli_export_data,
            flext_cli_format_tabulate,
            flext_cli_analyze_data,
            flext_cli_format_output,
        ]

        for func in functions:
            sig = inspect.signature(func)
            # Check that function has type annotations
            for param_name, param in sig.parameters.items():
                if param.annotation == inspect.Parameter.empty:
                    # Skip self parameter for methods
                    if param_name != "self":
                        assert param.annotation != inspect.Parameter.empty, (
                            f"Missing type hint for {func.__name__}.{param_name}"
                        )

    def test_utility_functions_docstrings(self) -> None:
        """Test that utility functions have proper docstrings."""
        functions = [
            flext_cli_export_data,
            flext_cli_format_tabulate,
            flext_cli_analyze_data,
            flext_cli_format_output,
        ]

        for func in functions:
            assert func.__doc__ is not None, f"Missing docstring for {func.__name__}"
            assert "Example:" in func.__doc__  # Should include examples

    def test_comprehensive_workflow(
        self,
        sample_data: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """Test a comprehensive workflow using multiple utility functions."""
        # 1. Analyze the data
        analysis_result = flext_cli_analyze_data(sample_data, "Workflow Analysis")
        assert analysis_result.success

        # 2. Format as table
        table_result = flext_cli_format_tabulate(sample_data, "Workflow Table", "grid")
        assert table_result.success

        # 3. Export to CSV
        csv_file = temp_dir / "workflow.csv"
        export_result = flext_cli_export_data(sample_data, str(csv_file))
        assert export_result.success
        assert csv_file.exists()

        # 4. Format output as JSON
        json_result = flext_cli_format_output(sample_data, "json")
        assert json_result.success

        # 5. Verify all results are consistent
        assert "3 records" in analysis_result.data
        assert "Alice" in table_result.data
        assert "CSV" in export_result.data
        assert json.loads(json_result.data)  # Valid JSON

    def test_performance_with_large_dataset(self) -> None:
        """Test performance with larger datasets."""
        # Create a larger dataset
        large_data = [
            {"id": i, "name": f"User{i}", "value": i * 10, "category": f"Cat{i % 5}"}
            for i in range(1000)
        ]

        # Test analysis performance
        analysis_result = flext_cli_analyze_data(large_data, "Large Dataset Analysis")
        assert analysis_result.success

        # Test formatting performance
        format_result = flext_cli_format_output(large_data, "json")
        assert format_result.success

        # Test tabulate performance
        table_result = flext_cli_format_tabulate(
            large_data[:100],
            "Large Table",
            "grid",
        )  # Sample for display
        assert table_result.success

    def test_unicode_and_special_characters(self) -> None:
        """Test handling of Unicode and special characters."""
        unicode_data = [
            {"id": 1, "name": "José María", "city": "São Paulo", "emoji": "🚀"},
            {"id": 2, "name": "François", "city": "München", "emoji": "🌟"},
            {"id": 3, "name": "李小明", "city": "北京", "emoji": "🎯"},
        ]

        # Test JSON formatting
        json_result = flext_cli_format_output(unicode_data, "json")
        assert json_result.success
        parsed = json.loads(json_result.data)
        assert "José María" in str(parsed)
        assert "🚀" in str(parsed)

        # Test table formatting
        table_result = flext_cli_format_tabulate(unicode_data, "Unicode Table", "grid")
        assert table_result.success
        assert "José María" in table_result.data

    def test_edge_cases_and_boundary_conditions(self) -> None:
        """Test edge cases and boundary conditions."""
        # Test with single item
        single_item = [{"id": 1, "name": "Single"}]
        result = flext_cli_analyze_data(single_item, "Single Item")
        assert result.success

        # Test with very long strings
        long_string_data = [
            {"id": 1, "name": "A" * 1000, "description": "B" * 500},
        ]
        result = flext_cli_format_output(long_string_data, "json")
        assert result.success

        # Test with None values
        none_data = [{"id": 1, "name": None, "value": 42}]
        result = flext_cli_format_output(none_data, "json")
        assert result.success
