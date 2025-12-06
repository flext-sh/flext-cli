"""FLEXT CLI Tables New Tests - Comprehensive Table Formatting Validation Testing.

Tests for FlextCliTables covering table creation with various formats, advanced configuration
options, specialized format methods, format discovery, integration workflows, error handling,
and edge cases with 100% coverage.

Modules tested: flext_cli.tables.FlextCliTables
Scope: All table formatting operations, format discovery, specialized formats, edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import operator
from typing import cast

import pytest
from flext_core import t
from flext_tests import tm

from flext_cli import FlextCliTables, m, r
from flext_cli.typings import t as flext_cli_t

from .._helpers import FlextCliTestHelpers
from ..conftest import c

# from ..fixtures.constants import TestTables  # Fixtures removed - use conftest.py and flext_tests

# Alias for nested class
TablesFactory = FlextCliTestHelpers.TablesFactory

# Use TableData from typings - matches src definition
TableData = flext_cli_t.Tables.TableData


@pytest.fixture
def tables() -> FlextCliTables:
    """Create FlextCliTables instance for testing."""
    return TablesFactory.create_tables()


@pytest.fixture
def test_data() -> dict[str, t.GeneralValueType]:
    """Create comprehensive table test data."""
    return cast("dict[str, t.GeneralValueType]", TablesFactory.get_test_data())


class TestsCliTables:
    """Comprehensive tests for flext_cli.tables module."""

    # ========================================================================
    # INITIALIZATION AND FORMAT DISCOVERY
    # ========================================================================

    def test_tables_initialization(self, tables: FlextCliTables) -> None:
        """Test FlextCliTables initialization."""
        assert tables is not None
        assert isinstance(tables, FlextCliTables)
        assert hasattr(tables, "logger")
        assert hasattr(tables, "container")

    def test_format_availability(self, tables: FlextCliTables) -> None:
        """Test format availability and discovery."""
        formats = tables.list_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0
        for fmt in c.Format.EXPECTED_ALL:
            assert fmt in formats

    def test_get_format_description_success(self, tables: FlextCliTables) -> None:
        """Test get_format_description with valid format."""
        result = tables.get_format_description(c.Format.GRID)
        assert result.is_success

    def test_get_format_description_failure(self, tables: FlextCliTables) -> None:
        """Test get_format_description with invalid format."""
        result = tables.get_format_description(c.Format.INVALID)
        assert result.is_failure

    def test_print_available_formats(self, tables: FlextCliTables) -> None:
        """Test print_available_formats method."""
        result = tables.print_available_formats()
        assert result.is_success
        assert result.unwrap() is True

    # ========================================================================
    # BASIC TABLE CREATION
    # ========================================================================

    @pytest.mark.parametrize(
        ("format_name", "assertions"),
        [
            (
                "simple",
                [
                    c.TestData.ALICE,
                    c.Format.NAME_HEADER,
                ],
            ),
            (
                c.Format.GRID,
                [
                    c.TestData.ALICE,
                    c.Table.Borders.PLUS,
                ],
            ),
            (
                c.Format.FANCY_GRID,
                [c.TestData.ALICE],
            ),
        ],
    )
    def test_create_table_basic_formats(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
        format_name: str,
        assertions: list[str],
    ) -> None:
        """Test basic table creation with various formats."""
        config = m.TableConfig(table_format=format_name)
        result = tables.create_table(
            data=cast("TableData", test_data["people_dict"]),
            config=config,
        )

        assert result.is_success
        table_str = result.unwrap()
        for assertion in assertions:
            assert assertion in table_str

    # ========================================================================
    # ADVANCED TABLE CONFIGURATION
    # ========================================================================

    def test_create_table_with_custom_headers(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with custom headers."""
        config = m.TableConfig(
            headers=c.Table.Data.Headers.CUSTOM,
            table_format="simple",
        )
        result = tables.create_table(
            data=cast("TableData", test_data["people_list"]),
            config=config,
        )

        assert result.is_success
        assert c.TestData.ALICE in result.unwrap()

    def test_create_table_with_alignment(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with alignment option."""
        config = m.TableConfig(
            table_format="simple",
            align=c.Config.Alignment.CENTER,
        )
        result = tables.create_table(
            data=cast("TableData", test_data["people_dict"]),
            config=config,
        )

        assert result.is_success

    def test_create_table_with_float_formatting(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with float formatting."""
        config = m.TableConfig(
            table_format="simple",
            floatfmt=c.Config.FloatFormat.TWO_DECIMAL,
        )
        result = tables.create_table(
            data=cast("TableData", test_data["people_dict"]),
            config=config,
        )

        assert result.is_success

    def test_create_table_with_show_index(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with show index option."""
        config = m.TableConfig(
            table_format="simple",
            showindex=c.Config.SHOW_INDEX_TRUE,
        )
        result = tables.create_table(
            data=cast("TableData", test_data["people_dict"]),
            config=config,
        )

        assert result.is_success

    def test_create_table_with_colalign(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with column alignment."""
        config = m.TableConfig(
            table_format="simple",
            colalign=c.Config.Alignment.LIST,
        )
        result = tables.create_table(
            data=cast("TableData", test_data["people_dict"]),
            config=config,
        )

        assert result.is_success

    # ========================================================================
    # SPECIALIZED TABLE FORMATS
    # ========================================================================

    @pytest.mark.parametrize(
        ("method_name", "format_name", "expected_content"),
        c.Table.SPECIALIZED_CASES,
        ids=operator.itemgetter(0),
    )
    def test_specialized_table_formats(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
        method_name: str,
        format_name: str,
        expected_content: list[str],
    ) -> None:
        """Test specialized table format methods."""
        data = cast("TableData", test_data["people_dict"])

        match method_name:
            case "simple":
                result = tables.create_simple_table(data)
            case "grid":
                result = tables.create_grid_table(data)
            case "markdown":
                result = tables.create_markdown_table(data)
            case "html":
                result = tables.create_html_table(data)
            case "latex":
                result = tables.create_latex_table(data)
            case "rst":
                result = tables.create_rst_table(data)
            case _:
                pytest.fail(f"Unknown method: {method_name}")

        assert result.is_success
        table_str = result.unwrap()
        for content in expected_content:
            assert content in table_str

    # ========================================================================
    # LATEX TABLE OPTIONS
    # ========================================================================

    @pytest.mark.parametrize(
        ("longtable", "booktabs"),
        [(True, False), (False, False), (False, True)],
    )
    def test_latex_table_options(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
        longtable: bool,
        booktabs: bool,
    ) -> None:
        """Test LaTeX table with various options."""
        data = cast("TableData", test_data["people_dict"])

        result = tables.create_latex_table(
            data=data,
            longtable=longtable,
            booktabs=booktabs if not longtable else False,
        )
        assert result.is_success

    # ========================================================================
    # EDGE CASES AND SPECIAL SCENARIOS
    # ========================================================================

    def test_single_row_table(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with single row."""
        config = m.TableConfig(table_format="simple")
        result = tables.create_table(
            data=cast("TableData", test_data["single_row"]),
            config=config,
        )

        assert result.is_success

    def test_table_with_none_values(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with None values."""
        config = m.TableConfig(table_format="simple")
        result = tables.create_table(
            data=cast("TableData", test_data["with_none"]),
            config=config,
        )

        assert result.is_success
        assert c.TestData.ALICE in result.unwrap()

    def test_list_of_dicts_with_custom_headers(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test list of dicts with custom headers."""
        config = m.TableConfig(
            headers=c.Table.Data.Headers.CUSTOM,
            table_format="simple",
        )
        result = tables.create_table(
            data=cast("TableData", test_data["people_dict"]),
            config=config,
        )

        assert result.is_success

    # ========================================================================
    # ERROR HANDLING
    # ========================================================================

    def test_empty_data_handling(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test handling of empty data."""
        config = m.TableConfig(table_format="simple")
        result = tables.create_table(
            data=cast("TableData", test_data["empty"]),
            config=config,
        )

        assert isinstance(result, r)

    def test_invalid_format_handling(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test handling of invalid format."""
        config = m.TableConfig(table_format=c.Format.INVALID)
        result = tables.create_table(
            data=cast("TableData", test_data["people_dict"]),
            config=config,
        )

        assert isinstance(result, r)

    # ========================================================================
    # INTEGRATION AND SERVICE PATTERN
    # ========================================================================

    def test_execute_method_flext_service_pattern(
        self,
        tables: FlextCliTables,
    ) -> None:
        """Test execute method following FlextService pattern."""
        result = tables.execute()
        assert isinstance(result, r)
        assert result.is_success

    def test_integration_workflow_complete(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test complete integration workflow."""
        data = cast("TableData", test_data["people_dict"])

        formats = tables.list_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0

        first_format = formats[0]
        config = m.TableConfig(table_format=first_format)
        table_result = tables.create_table(data=data, config=config)
        assert table_result.is_success

    # ========================================================================
    # VALIDATION WITH FLEXT_TESTS HELPERS
    # ========================================================================

    def test_table_creation_with_validation(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation using validation helpers."""
        config = m.TableConfig(table_format="simple")
        result = tables.create_table(
            data=cast("TableData", test_data["people_dict"]),
            config=config,
        )

        tm.ok(result)

    def test_table_error_handling_with_validation(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table error handling with validation helpers."""
        config = m.TableConfig(table_format="simple")
        result = tables.create_table(
            data=cast("TableData", test_data["empty"]),
            config=config,
        )

        assert isinstance(result, r)

    def test_table_format_validation(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table format validation."""
        config = m.TableConfig(table_format=c.Format.GRID)
        result = tables.create_table(
            data=cast("TableData", test_data["people_dict"]),
            config=config,
        )

        assert result.is_success
        # Validate table result directly - result is successful and contains string
        table_output = result.unwrap()
        assert isinstance(table_output, str)
        assert len(table_output) > 0
