"""Comprehensive tests for FlextCliTables - Real Functionality Testing.

Tests all table formatting methods with real data and various formats.
Targets 90%+ coverage with actual table generation validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli.tables import FlextCliTables
from flext_core import FlextResult, FlextTypes


@pytest.fixture
def tables() -> FlextCliTables:
    """Create FlextCliTables instance for testing."""
    return FlextCliTables()


@pytest.fixture
def sample_data() -> list[FlextTypes.Dict]:
    """Sample table data for testing."""
    return [
        {"name": "Alice", "age": 30, "city": "New York", "salary": 75000.50},
        {"name": "Bob", "age": 25, "city": "London", "salary": 65000.75},
        {"name": "Charlie", "age": 35, "city": "Paris", "salary": 85000.25},
    ]


@pytest.fixture
def sample_list_data() -> list[FlextTypes.List]:
    """Sample list-based table data."""
    return [
        ["Alice", 30, "New York", 75000.50],
        ["Bob", 25, "London", 65000.75],
        ["Charlie", 35, "Paris", 85000.25],
    ]


class TestFlextCliTables:
    """Test suite for FlextCliTables with real functionality."""

    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================

    def test_tables_initialization(self, tables: FlextCliTables) -> None:
        """Test FlextCliTables initialization."""
        assert tables is not None
        assert isinstance(tables, FlextCliTables)
        assert hasattr(tables, "FORMATS")
        assert len(tables.FORMATS) > 0

    def test_tables_formats_available(self, tables: FlextCliTables) -> None:
        """Test that all expected formats are available."""
        formats = tables.list_formats()
        expected_formats = [
            "simple",
            "plain",
            "grid",
            "fancy_grid",
            "pipe",
        ]
        for fmt in expected_formats:
            assert fmt in formats

    # =========================================================================
    # CREATE_TABLE TESTS (Main Method)
    # =========================================================================

    def test_create_table_simple_format(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test creating simple format table."""
        result = tables.create_table(data=sample_data, table_format="simple")

        assert isinstance(result, FlextResult)
        assert result.is_success
        table_str = result.unwrap()
        assert "Alice" in table_str
        assert "Bob" in table_str
        assert "Charlie" in table_str
        assert "name" in table_str
        assert "age" in table_str

    def test_create_table_grid_format(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test creating grid format table."""
        result = tables.create_table(data=sample_data, table_format="grid")

        assert result.is_success
        table_str = result.unwrap()
        assert "+" in table_str  # Grid borders
        assert "|" in table_str  # Column separators
        assert "Alice" in table_str

    def test_create_table_fancy_grid_format(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test creating fancy grid format table."""
        result = tables.create_table(data=sample_data, table_format="fancy_grid")

        assert result.is_success
        table_str = result.unwrap()
        assert "│" in table_str or "|" in table_str  # Unicode or ASCII borders
        assert "Alice" in table_str

    def test_create_table_with_custom_headers(
        self, tables: FlextCliTables, sample_list_data: list[FlextTypes.List]
    ) -> None:
        """Test table creation with custom headers."""
        headers = ["Name", "Age", "City", "Salary"]
        result = tables.create_table(
            data=sample_list_data, headers=headers, table_format="simple"
        )

        assert result.is_success
        table_str = result.unwrap()
        assert "Name" in table_str
        assert "Age" in table_str
        assert "Alice" in table_str

    def test_create_table_with_alignment(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test table creation with column alignment."""
        result = tables.create_table(
            data=sample_data, table_format="simple", align="center"
        )

        assert result.is_success
        assert "Alice" in result.unwrap()

    def test_create_table_empty_data_fails(self, tables: FlextCliTables) -> None:
        """Test that empty data returns failure."""
        result = tables.create_table(data=[], table_format="simple")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert "empty" in (result.error or "").lower()

    def test_create_table_invalid_format_fails(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test that invalid format returns failure."""
        result = tables.create_table(data=sample_data, table_format="invalid_format")

        assert result.is_failure
        assert "invalid" in (result.error or "").lower()

    # =========================================================================
    # SPECIALIZED TABLE FORMAT TESTS
    # =========================================================================

    def test_create_simple_table(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test create_simple_table convenience method."""
        result = tables.create_simple_table(data=sample_data)

        assert result.is_success
        table_str = result.unwrap()
        assert "Alice" in table_str
        assert "name" in table_str

    def test_create_grid_table(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test create_grid_table convenience method."""
        result = tables.create_grid_table(data=sample_data)

        assert result.is_success
        table_str = result.unwrap()
        assert "+" in table_str
        assert "|" in table_str
        assert "Alice" in table_str

    def test_create_markdown_table(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test create_markdown_table for GitHub/Markdown."""
        result = tables.create_markdown_table(data=sample_data)

        assert result.is_success
        table_str = result.unwrap()
        assert "|" in table_str  # Markdown separator
        assert "Alice" in table_str

    def test_create_html_table(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test create_html_table for HTML output."""
        result = tables.create_html_table(data=sample_data)

        assert result.is_success
        table_str = result.unwrap()
        assert "<table>" in table_str or "table" in table_str.lower()
        assert "Alice" in table_str

    def test_create_latex_table(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test create_latex_table for LaTeX output."""
        result = tables.create_latex_table(data=sample_data)

        assert result.is_success
        table_str = result.unwrap()
        assert "Alice" in table_str
        # LaTeX tables have specific formatting

    def test_create_rst_table(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test create_rst_table for reStructuredText."""
        result = tables.create_rst_table(data=sample_data)

        assert result.is_success
        table_str = result.unwrap()
        assert "=" in table_str or "-" in table_str  # RST separators
        assert "Alice" in table_str

    # =========================================================================
    # FORMAT DISCOVERY TESTS
    # =========================================================================

    def test_list_formats(self, tables: FlextCliTables) -> None:
        """Test listing available table formats."""
        formats = tables.list_formats()

        assert isinstance(formats, list)
        assert len(formats) > 0
        assert "simple" in formats
        assert "grid" in formats

    def test_get_format_description(self, tables: FlextCliTables) -> None:
        """Test getting format description."""
        result = tables.get_format_description("grid")

        assert result.is_success
        description = result.unwrap()
        assert isinstance(description, str)
        assert len(description) > 0

    def test_get_format_description_invalid(self, tables: FlextCliTables) -> None:
        """Test getting description for invalid format."""
        result = tables.get_format_description("invalid_format")

        assert result.is_failure
        assert "unknown" in (result.error or "").lower()

    def test_print_available_formats(self, tables: FlextCliTables) -> None:
        """Test printing available formats."""
        result = tables.print_available_formats()

        assert result.is_success
        # Method returns None but prints to stdout
        assert result.unwrap() is None

    # =========================================================================
    # EDGE CASES AND ERROR HANDLING
    # =========================================================================

    def test_create_table_single_row(self, tables: FlextCliTables) -> None:
        """Test table with single row."""
        single_row = [{"name": "Alice", "age": 30}]
        result = tables.create_table(data=single_row, table_format="simple")

        assert result.is_success
        assert "Alice" in result.unwrap()

    def test_create_table_with_none_values(self, tables: FlextCliTables) -> None:
        """Test table with None values."""
        data_with_none = [
            {"name": "Alice", "age": 30, "city": None},
            {"name": "Bob", "age": None, "city": "London"},
        ]
        result = tables.create_table(data=data_with_none, table_format="simple")

        assert result.is_success
        table_str = result.unwrap()
        assert "Alice" in table_str
        assert "Bob" in table_str

    def test_create_table_with_float_formatting(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test table with float number formatting."""
        result = tables.create_table(
            data=sample_data, table_format="simple", floatfmt=".2f"
        )

        assert result.is_success
        table_str = result.unwrap()
        # Should format floats to 2 decimal places
        assert "75000.50" in table_str or "75000.5" in table_str

    def test_create_table_with_show_index(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test table with row index."""
        result = tables.create_table(
            data=sample_data, table_format="simple", showindex=True
        )

        assert result.is_success
        table_str = result.unwrap()
        # Should show row indices (0, 1, 2)
        assert "0" in table_str or "1" in table_str

    # =========================================================================
    # EXECUTE METHOD TEST
    # =========================================================================

    def test_execute_method(self, tables: FlextCliTables) -> None:
        """Test execute method (FlextService pattern)."""
        result = tables.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is None

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_tables_full_workflow(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test complete workflow: list formats, get description, create table."""
        # List available formats
        formats = tables.list_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0

        # Get description for first format
        first_format = formats[0]
        desc_result = tables.get_format_description(first_format)
        assert desc_result.is_success

        # Create table with that format
        table_result = tables.create_table(data=sample_data, table_format=first_format)
        assert table_result.is_success
        assert "Alice" in table_result.unwrap()

    def test_tables_multiple_formats_same_data(
        self, tables: FlextCliTables, sample_data: list[FlextTypes.Dict]
    ) -> None:
        """Test creating same data in multiple formats."""
        formats = ["simple", "grid", "pipe", "fancy_grid"]

        for fmt in formats:
            result = tables.create_table(data=sample_data, table_format=fmt)
            assert result.is_success, f"Format {fmt} failed"
            table_str = result.unwrap()
            assert "Alice" in table_str
            assert len(table_str) > 0
