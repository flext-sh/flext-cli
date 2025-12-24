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

import pytest
from flext import t
from flext_tests import tm

from flext_cli import FlextCliTables, r
from flext_cli.models import m

from ..conftest import c

# from ..fixtures.constants import TestTables  # Fixtures removed - use conftest.py and flext_tests

# Use flext_cli_t.Cli.TableData from CLI typings
# (t is FlextTypes from flext-core, flext_cli_t is FlextCliTypes)
# Both should work after import, no need to set alias here


@pytest.fixture
def tables() -> FlextCliTables:
    """Create FlextCliTables instance for testing."""
    return FlextCliTables()


@pytest.fixture
def test_data() -> dict[str, t.GeneralValueType]:
    """Create comprehensive table test data."""
    return {
        "empty": {},
        "headers": ["Name", "Value"],
        "rows": [["Test", "42"], ["Example", "100"]],
        "with_none": [{"name": "alice", "value": None}, {"name": "bob", "value": 42}],
        "list_of_dicts": [{"name": "alice", "value": 10}, {"name": "bob", "value": 20}],
        "custom_headers": ["Custom1", "Custom2"],
        "simple_data": [["alice", "10"], ["bob", "20"]],
        "with_float": [
            {"name": "alice", "score": 98.5},
            {"name": "bob", "score": 87.3},
        ],
        "with_show_index": [{"name": "alice"}, {"name": "bob"}],
        "latex_data": [["col1", "col2"], ["val1", "val2"]],
        "people_dict": [
            {"name": "alice", "role": "developer"},
            {"name": "bob", "role": "manager"},
        ],
        "people_list": [
            {"id": 1, "name": "alice", "status": "active"},
            {"id": 2, "name": "bob", "status": "inactive"},
        ],
        "single_row": [{"name": "alice", "role": "developer"}],
        "specialized_cases": [
            {
                "format": "grid",
                "data": [{"name": "alice", "role": "dev"}],
                "expected_content": ["alice", "dev"],
            },
            {
                "format": "fancy_grid",
                "data": [{"x": 1, "y": 2}],
                "expected_content": ["x", "y"],
            },
        ],
    }


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
        # Verify basic formats are available
        for fmt in [c.GRID, c.FANCY_GRID]:
            assert fmt in formats

    def test_get_format_description_success(self, tables: FlextCliTables) -> None:
        """Test get_format_description with valid format."""
        result = tables.get_format_description(c.GRID)
        assert result.is_success

    def test_get_format_description_failure(self, tables: FlextCliTables) -> None:
        """Test get_format_description with invalid format."""
        result = tables.get_format_description(c.INVALID)
        assert result.is_failure

    def test_print_available_formats(self, tables: FlextCliTables) -> None:
        """Test print_available_formats method."""
        result = tables.print_available_formats()
        assert result.is_success
        assert result.value is True

    # ========================================================================
    # BASIC TABLE CREATION
    # ========================================================================

    @pytest.mark.parametrize(
        ("format_name", "assertions"),
        [
            (
                "simple",
                [
                    c.CliTest.TestData.ALICE,
                    "name",  # Table uses dict keys (lowercase) as headers
                ],
            ),
            (
                c.GRID,
                [
                    c.CliTest.TestData.ALICE,
                    c.Table.Borders.PLUS,
                ],
            ),
            (
                c.FANCY_GRID,
                [c.CliTest.TestData.ALICE],
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
        config = m.Cli.TableConfig.model_construct(table_format=format_name)
        # Get and validate test data
        people_dict: object = test_data["people_dict"]
        if not isinstance(people_dict, (dict, list)):
            pytest.fail(
                f"Expected dict or list for people_dict, got {type(people_dict)}"
            )
        # Type is now narrowed to dict | list which is acceptable for table creation
        result = tables.create_table(data=people_dict, config=config)

        assert result.is_success
        table_str = result.value
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
        config = m.Cli.TableConfig.model_construct(
            headers=("ID", "Name", "Status"),
            table_format="simple",
        )
        data_val: object = test_data["people_list"]
        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for people_list, got {type(data_val)}")

        result = tables.create_table(
            data=data_val,
            config=config,
        )

        assert result.is_success
        assert c.CliTest.TestData.ALICE in result.value

    def test_create_table_with_alignment(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with alignment option."""
        config = m.Cli.TableConfig.model_construct(
            table_format="simple",
            align="center",
        )
        data_val: object = test_data["people_dict"]
        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for people_dict, got {type(data_val)}")

        result = tables.create_table(
            data=data_val,
            config=config,
        )

        assert result.is_success

    def test_create_table_with_float_formatting(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with float formatting."""
        config = m.Cli.TableConfig.model_construct(
            table_format="simple",
            floatfmt=".2g",
        )
        data_val: object = test_data["people_dict"]
        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for people_dict, got {type(data_val)}")

        result = tables.create_table(
            data=data_val,
            config=config,
        )

        assert result.is_success

    def test_create_table_with_show_index(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with show index option."""
        config = m.Cli.TableConfig.model_construct(
            table_format="simple",
            showindex=True,
        )
        data_val: object = test_data["people_dict"]
        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for people_dict, got {type(data_val)}")

        result = tables.create_table(
            data=data_val,
            config=config,
        )

        assert result.is_success

    def test_create_table_with_colalign(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with column alignment."""
        config = m.Cli.TableConfig.model_construct(
            table_format="simple",
            colalign=("left", "center", "right"),
        )
        data_val: object = test_data["people_dict"]
        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for people_dict, got {type(data_val)}")

        result = tables.create_table(
            data=data_val,
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
        data_value: object = test_data["people_dict"]
        if not isinstance(data_value, (dict, list)):
            pytest.fail(
                f"Expected dict or list for people_dict, got {type(data_value)}"
            )
        # Type is now narrowed to dict | list which is acceptable for table methods
        data = data_value

        match method_name:
            case "simple":
                result = tables.create_simple_table(data)
            case "grid":
                result = tables.create_grid_table(data)
            case "fancy_grid":
                result = tables.create_table(data, table_format="fancy_grid")
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
        table_str = result.value
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
        data_value: object = test_data["people_dict"]
        if not isinstance(data_value, (dict, list)):
            pytest.fail(
                f"Expected dict or list for people_dict, got {type(data_value)}"
            )
        data = data_value

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
        config = m.Cli.TableConfig.model_construct(table_format="simple")
        # Get and validate test data
        data_val: object = test_data["single_row"]
        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for single_row, got {type(data_val)}")
        result = tables.create_table(
            data=data_val,
            config=config,
        )
        assert result.is_success

    def test_table_with_none_values(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation with None values."""
        config = m.Cli.TableConfig.model_construct(table_format="simple")
        # Get and validate test data
        data_val: object = test_data["with_none"]
        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for with_none, got {type(data_val)}")
        result = tables.create_table(
            data=data_val,
            config=config,
        )
        assert result.is_success
        assert c.CliTest.TestData.ALICE in result.value

    def test_list_of_dicts_with_custom_headers(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test list of dicts with custom headers."""
        config = m.Cli.TableConfig.model_construct(
            headers=("ID", "Name", "Status"),
            table_format="simple",
        )
        data_val: object = test_data["people_dict"]
        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for people_dict, got {type(data_val)}")

        result = tables.create_table(
            data=data_val,
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
        config = m.Cli.TableConfig.model_construct(table_format="simple")
        # Get and validate test data
        data_val: object = test_data["empty"]
        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for empty, got {type(data_val)}")
        result = tables.create_table(
            data=data_val,
            config=config,
        )
        assert isinstance(result, r)

    def test_invalid_format_handling(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test handling of invalid format."""
        config = m.Cli.TableConfig.model_construct(table_format=c.INVALID)
        # Get and validate test data
        data_val: object = test_data["people_dict"]
        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for people_dict, got {type(data_val)}")
        result = tables.create_table(
            data=data_val,
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
        data_value: object = test_data["people_dict"]
        if not isinstance(data_value, (dict, list)):
            pytest.fail(
                f"Expected dict or list for people_dict, got {type(data_value)}"
            )
        data = data_value

        formats = tables.list_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0

        first_format = formats[0]
        config = m.Cli.TableConfig.model_construct(table_format=first_format)
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
        config = m.Cli.TableConfig.model_construct(table_format="simple")
        data_val: object = test_data["people_dict"]

        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for people_dict, got {type(data_val)}")

        result = tables.create_table(
            data=data_val,
            config=config,
        )

        tm.ok(result)

    def test_table_error_handling_with_validation(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table error handling with validation helpers."""
        config = m.Cli.TableConfig.model_construct(table_format="simple")
        data_val: object = test_data["empty"]

        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for empty, got {type(data_val)}")

        result = tables.create_table(
            data=data_val,
            config=config,
        )

        assert isinstance(result, r)

    def test_table_format_validation(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table format validation."""
        config = m.Cli.TableConfig.model_construct(table_format=c.GRID)
        data_val: object = test_data["people_dict"]
        if not isinstance(data_val, (dict, list)):
            pytest.fail(f"Expected dict or list for people_dict, got {type(data_val)}")

        result = tables.create_table(
            data=data_val,
            config=config,
        )

        assert result.is_success
        # Validate table result directly - result is successful and contains string
        table_output = result.value
        assert isinstance(table_output, str)
        assert len(table_output) > 0
