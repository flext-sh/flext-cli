"""Tests for flext_cli.tables module - Table Formatting Validation.

Modules Tested:
- flext_cli.FlextCliTables: Table formatting, display, and format discovery

Scope:
- Table creation with various formats (simple, grid, fancy_grid, etc.)
- Advanced configuration options (alignment, float format, headers, etc.)
- Specialized table format methods (markdown, HTML, LaTeX, RST)
- Edge cases and special scenarios (single row, None values, empty data)
- Format discovery and description operations
- Integration workflows with multiple formats
- Error handling with invalid formats and empty data

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import operator
from typing import Any

import pytest
from flext_core import FlextResult
from flext_tests import FlextTestsMatchers

from flext_cli import FlextCliModels, FlextCliTables
from tests._helpers import FlextCliTestHelpers
from tests.fixtures.constants import TestTables

# Alias for nested class
TablesFactory = FlextCliTestHelpers.TablesFactory


@pytest.fixture
def tables() -> FlextCliTables:
    """Create FlextCliTables instance for testing."""
    return TablesFactory.create_tables()


@pytest.fixture
def test_data() -> dict[str, Any]:
    """Create comprehensive table test data."""
    return TablesFactory.get_test_data()


class TestFlextCliTables:
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
        for fmt in TestTables.Formats.ExpectedFormats.ALL:
            assert fmt in formats

    def test_get_format_description_success(self, tables: FlextCliTables) -> None:
        """Test get_format_description with valid format."""
        result = tables.get_format_description(TestTables.Formats.GRID)
        assert result.is_success

    def test_get_format_description_failure(self, tables: FlextCliTables) -> None:
        """Test get_format_description with invalid format."""
        result = tables.get_format_description(TestTables.Formats.INVALID)
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
                TestTables.Formats.SIMPLE,
                [
                    TestTables.Assertions.Content.ALICE,
                    TestTables.Assertions.Content.NAME_HEADER,
                ],
            ),
            (
                TestTables.Formats.GRID,
                [
                    TestTables.Assertions.Content.ALICE,
                    TestTables.Assertions.Borders.PLUS,
                ],
            ),
            (
                TestTables.Formats.FANCY_GRID,
                [TestTables.Assertions.Content.ALICE],
            ),
        ],
    )
    def test_create_table_basic_formats(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
        format_name: str,
        assertions: list[str],
    ) -> None:
        """Test basic table creation with various formats."""
        config = FlextCliModels.TableConfig(table_format=format_name)
        result = tables.create_table(data=test_data["people_dict"], config=config)

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
        test_data: dict[str, Any],
    ) -> None:
        """Test table creation with custom headers."""
        config = FlextCliModels.TableConfig(
            headers=TestTables.Data.Headers.CUSTOM,
            table_format=TestTables.Formats.SIMPLE,
        )
        result = tables.create_table(data=test_data["people_list"], config=config)

        assert result.is_success
        assert TestTables.Assertions.Content.ALICE in result.unwrap()

    def test_create_table_with_alignment(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test table creation with alignment option."""
        config = FlextCliModels.TableConfig(
            table_format=TestTables.Formats.SIMPLE,
            align=TestTables.Config.Alignment.CENTER,
        )
        result = tables.create_table(data=test_data["people_dict"], config=config)

        assert result.is_success

    def test_create_table_with_float_formatting(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test table creation with float formatting."""
        config = FlextCliModels.TableConfig(
            table_format=TestTables.Formats.SIMPLE,
            floatfmt=TestTables.Config.FloatFormat.TWO_DECIMAL,
        )
        result = tables.create_table(data=test_data["people_dict"], config=config)

        assert result.is_success

    def test_create_table_with_show_index(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test table creation with show index option."""
        config = FlextCliModels.TableConfig(
            table_format=TestTables.Formats.SIMPLE,
            showindex=TestTables.Config.Options.SHOW_INDEX_TRUE,
        )
        result = tables.create_table(data=test_data["people_dict"], config=config)

        assert result.is_success

    def test_create_table_with_colalign(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test table creation with column alignment."""
        config = FlextCliModels.TableConfig(
            table_format=TestTables.Formats.SIMPLE,
            colalign=TestTables.Config.Alignment.LIST,
        )
        result = tables.create_table(data=test_data["people_dict"], config=config)

        assert result.is_success

    # ========================================================================
    # SPECIALIZED TABLE FORMATS
    # ========================================================================

    @pytest.mark.parametrize(
        ("method_name", "format_name", "expected_content"),
        TestTables.SpecializedFormats.CASES,
        ids=operator.itemgetter(0),
    )
    def test_specialized_table_formats(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
        method_name: str,
        format_name: str,
        expected_content: list[str],
    ) -> None:
        """Test specialized table format methods."""
        data = test_data["people_dict"]

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
        test_data: dict[str, Any],
        longtable: bool,
        booktabs: bool,
    ) -> None:
        """Test LaTeX table with various options."""
        data = test_data["people_dict"]

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
        test_data: dict[str, Any],
    ) -> None:
        """Test table creation with single row."""
        config = FlextCliModels.TableConfig(table_format=TestTables.Formats.SIMPLE)
        result = tables.create_table(data=test_data["single_row"], config=config)

        assert result.is_success

    def test_table_with_none_values(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test table creation with None values."""
        config = FlextCliModels.TableConfig(table_format=TestTables.Formats.SIMPLE)
        result = tables.create_table(data=test_data["with_none"], config=config)

        assert result.is_success
        assert TestTables.Assertions.Content.ALICE in result.unwrap()

    def test_list_of_dicts_with_custom_headers(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test list of dicts with custom headers."""
        config = FlextCliModels.TableConfig(
            headers=TestTables.Data.Headers.CUSTOM,
            table_format=TestTables.Formats.SIMPLE,
        )
        result = tables.create_table(data=test_data["people_dict"], config=config)

        assert result.is_success

    # ========================================================================
    # ERROR HANDLING
    # ========================================================================

    def test_empty_data_handling(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test handling of empty data."""
        config = FlextCliModels.TableConfig(table_format=TestTables.Formats.SIMPLE)
        result = tables.create_table(data=test_data["empty"], config=config)

        assert isinstance(result, FlextResult)

    def test_invalid_format_handling(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test handling of invalid format."""
        config = FlextCliModels.TableConfig(table_format=TestTables.Formats.INVALID)
        result = tables.create_table(data=test_data["people_dict"], config=config)

        assert isinstance(result, FlextResult)

    # ========================================================================
    # INTEGRATION AND SERVICE PATTERN
    # ========================================================================

    def test_execute_method_flext_service_pattern(
        self,
        tables: FlextCliTables,
    ) -> None:
        """Test execute method following FlextService pattern."""
        result = tables.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_integration_workflow_complete(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test complete integration workflow."""
        data = test_data["people_dict"]

        formats = tables.list_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0

        first_format = formats[0]
        config = FlextCliModels.TableConfig(table_format=first_format)
        table_result = tables.create_table(data=data, config=config)
        assert table_result.is_success

    # ========================================================================
    # VALIDATION WITH FLEXT_TESTS HELPERS
    # ========================================================================

    def test_table_creation_with_validation(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test table creation using validation helpers."""
        config = FlextCliModels.TableConfig(table_format=TestTables.Formats.SIMPLE)
        result = tables.create_table(data=test_data["people_dict"], config=config)

        FlextTestsMatchers.assert_success(result)

    def test_table_error_handling_with_validation(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test table error handling with validation helpers."""
        config = FlextCliModels.TableConfig(table_format=TestTables.Formats.SIMPLE)
        result = tables.create_table(data=test_data["empty"], config=config)

        assert isinstance(result, FlextResult)

    def test_table_format_validation(
        self,
        tables: FlextCliTables,
        test_data: dict[str, Any],
    ) -> None:
        """Test table format validation."""
        config = FlextCliModels.TableConfig(table_format=TestTables.Formats.GRID)
        result = tables.create_table(data=test_data["people_dict"], config=config)

        assert result.is_success
        validation_result = TablesFactory.validate_table_result(result)
        assert validation_result.is_success
