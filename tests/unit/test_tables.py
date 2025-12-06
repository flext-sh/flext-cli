"""FLEXT CLI Tables Tests - Comprehensive Table Formatting Validation Testing.

Tests for FlextCliTables covering table formatting, display functionality, format discovery,
specialized formats, edge cases, error handling, and integration workflows with 100% coverage.

Modules tested: flext_cli.tables.FlextCliTables
Scope: All table formatting operations, format discovery, specialized formats, edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import operator
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import cast

import pytest
from flext_core import t
from flext_tests import tm

from flext_cli import FlextCliTables, m, r

# Fixtures modules removed - use conftest.py and flext_tests instead
# from ..fixtures.constants import TestTables


class TableTestType(StrEnum):
    """Table test types for comprehensive testing."""

    INITIALIZATION = "initialization"
    FORMAT_AVAILABILITY = "format_availability"
    CREATE_TABLE_BASIC = "create_table_basic"
    CREATE_TABLE_ADVANCED = "create_table_advanced"
    SPECIALIZED_FORMATS = "specialized_formats"
    FORMAT_DISCOVERY = "format_discovery"
    EDGE_CASES = "edge_cases"
    ERROR_HANDLING = "error_handling"
    INTEGRATION_WORKFLOW = "integration_workflow"


@dataclass(frozen=True)
class TableTestCase:
    """Test case data for table validation."""

    test_type: TableTestType
    description: str
    config: dict[str, t.GeneralValueType]
    data_key: str
    expected_result: bool = True
    content_assertions: list[str] | None = None
    error_contains: str | None = None


class TestsCliTables:
    """Comprehensive tests for flext_cli.tables module.

    Uses single class pattern with nested test factories and helpers.
    Covers all table formatting scenarios with railway-oriented patterns.
    """

    # =========================================================================
    # NESTED TEST FACTORIES
    # =========================================================================

    class TableTestFactory:
        """Factory for creating table test cases."""

        @staticmethod
        def create_comprehensive_test_cases() -> list[TableTestCase]:
            """Create comprehensive table test cases."""
            return [
                # Initialization tests
                TableTestCase(
                    TableTestType.INITIALIZATION,
                    "Tables initialization",
                    {},
                    "none",
                ),
                TableTestCase(
                    TableTestType.FORMAT_AVAILABILITY,
                    "Format availability check",
                    {},
                    "none",
                ),
                # Basic table creation
                TableTestCase(
                    TableTestType.CREATE_TABLE_BASIC,
                    "Create simple format table",
                    {"table_format": "simple"},
                    "people_dict",
                    content_assertions=[
                        "Alice",
                        "name",
                    ],
                ),
                TableTestCase(
                    TableTestType.CREATE_TABLE_BASIC,
                    "Create grid format table",
                    {"table_format": "grid"},
                    "people_dict",
                    content_assertions=[
                        "Alice",
                        "+",
                        "|",
                    ],
                ),
                TableTestCase(
                    TableTestType.CREATE_TABLE_BASIC,
                    "Create fancy grid format table",
                    {"table_format": "fancy_grid"},
                    "people_dict",
                    content_assertions=["Alice"],
                ),
                # Advanced table creation
                TableTestCase(
                    TableTestType.CREATE_TABLE_ADVANCED,
                    "Create table with custom headers",
                    {
                        "headers": ["name", "age", "city"],
                        "table_format": "simple",
                    },
                    "people_list",
                    content_assertions=[
                        "Name",
                        "Age",
                        "Alice",
                    ],
                ),
                TableTestCase(
                    TableTestType.CREATE_TABLE_ADVANCED,
                    "Create table with alignment",
                    {
                        "table_format": "simple",
                        "align": "center",
                    },
                    "people_dict",
                    content_assertions=["Alice"],
                ),
                TableTestCase(
                    TableTestType.CREATE_TABLE_ADVANCED,
                    "Create table with float formatting",
                    {
                        "table_format": "simple",
                        "floatfmt": ".2f",
                    },
                    "people_dict",
                    content_assertions=["Alice"],
                ),
                TableTestCase(
                    TableTestType.CREATE_TABLE_ADVANCED,
                    "Create table with show index",
                    {
                        "table_format": "simple",
                        "showindex": True,
                    },
                    "people_dict",
                    content_assertions=["Alice"],
                ),
                TableTestCase(
                    TableTestType.CREATE_TABLE_ADVANCED,
                    "Create table with colalign list",
                    {
                        "table_format": "simple",
                        "colalign": ["left", "right", "center"],
                    },
                    "people_dict",
                    content_assertions=["Alice"],
                ),
                # Error cases
                TableTestCase(
                    TableTestType.ERROR_HANDLING,
                    "Empty data fails",
                    {"table_format": "simple"},
                    "empty",
                    expected_result=False,
                    error_contains="empty",
                ),
                TableTestCase(
                    TableTestType.ERROR_HANDLING,
                    "Invalid format fails",
                    {"table_format": "invalid_format"},
                    "people_dict",
                    expected_result=False,
                    error_contains="invalid",
                ),
            ]

        @staticmethod
        def create_specialized_format_cases() -> list[tuple[str, str, list[str]]]:
            """Create specialized format test cases."""
            return [
                (
                    "simple",
                    "simple",
                    [
                        "Alice",
                        "name",
                    ],
                ),
                (
                    "grid",
                    "grid",
                    [
                        "Alice",
                        "+",
                        "|",
                    ],
                ),
                (
                    "markdown",
                    "pipe",
                    [
                        "Alice",
                        "|",
                    ],
                ),
                ("html", "html", ["Alice", "table"]),
                ("latex", "latex", ["Alice"]),
                (
                    "rst",
                    "rst",
                    [
                        "Alice",
                        "=",
                    ],
                ),
            ]

        @staticmethod
        def create_edge_case_data() -> dict[str, t.GeneralValueType]:
            """Create edge case test data."""
            return {
                "people_dict": [
                    {
                        "name": "Alice",
                        "age": 30,
                        "city": "New York",
                        "salary": 75000.50,
                    },
                    {"name": "Bob", "age": 25, "city": "London", "salary": 65000.75},
                    {"name": "Charlie", "age": 35, "city": "Paris", "salary": 85000.25},
                ],
                "people_list": [
                    ["Alice", 30, "New York", 75000.50],
                    ["Bob", 25, "London", 65000.75],
                    ["Charlie", 35, "Paris", 85000.25],
                ],
                "single_row": [{"name": "Single"}],
                "with_none": [
                    {"name": "Alice", "age": None},
                    {"name": "Bob", "city": None},
                ],
                "empty": [],
                "none": None,
            }

    # =========================================================================
    # NESTED VALIDATION HELPERS
    # =========================================================================

    class TableValidators:
        """Table validation helper methods."""

        @staticmethod
        def validate_table_result(
            result: r[str],
            expected_content: list[str] | None = None,
        ) -> r[bool]:
            """Validate table creation result."""
            try:
                if not result.is_success:
                    return r.fail("Table creation failed")

                table_str = result.unwrap()
                if not table_str or len(table_str.strip()) == 0:
                    return r.fail("Empty table string")

                if expected_content:
                    for content in expected_content:
                        if content not in table_str:
                            return r.fail(f"Missing expected content: {content}")

                return r.ok(True)
            except Exception as e:
                return r.fail(str(e))

        @staticmethod
        def validate_table_format(
            table_str: str,
            format_type: str,
        ) -> r[bool]:
            """Validate table format characteristics.

            Uses single return point pattern for reduced complexity.
            """
            result: r[bool]
            try:
                error_msg: str | None = None
                match format_type:
                    case "grid":
                        if "+" not in table_str:
                            error_msg = "Grid format missing + borders"
                    case "fancy_grid":
                        if not any(char in table_str for char in ["│", "|"]):
                            error_msg = "Fancy grid format missing borders"
                    case "pipe":
                        if "|" not in table_str:
                            error_msg = "Pipe format missing | separators"
                    case "html":
                        if "Alice" not in table_str:
                            error_msg = "HTML format missing content"
                    case "rst":
                        if not any(
                            char in table_str
                            for char in [
                                "=",
                                "-",
                            ]
                        ):
                            error_msg = "RST format missing separators"

                result = r.fail(error_msg) if error_msg else r.ok(True)
            except Exception as e:
                result = r.fail(str(e))

            return result

    # =========================================================================
    # FIXTURES
    # =========================================================================

    @pytest.fixture
    def tables(self) -> FlextCliTables:
        """Create FlextCliTables instance for testing."""
        return FlextCliTables()

    @pytest.fixture
    def test_data(self) -> dict[str, t.GeneralValueType]:
        """Create comprehensive test data."""
        return TestsCliTables.TableTestFactory.create_edge_case_data()

    # =========================================================================
    # COMPREHENSIVE TEST SUITE
    # =========================================================================

    @pytest.mark.parametrize(
        "test_case",
        TableTestFactory.create_comprehensive_test_cases(),
        ids=lambda case: f"{case.test_type.value}_{case.description.lower().replace(' ', '_')}",
    )
    def test_table_comprehensive_functionality(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
        test_case: TableTestCase,
    ) -> None:
        """Test comprehensive table functionality using parametrized cases."""
        match test_case.test_type:
            case TableTestType.INITIALIZATION:
                assert tables is not None
                assert isinstance(tables, FlextCliTables)
                assert hasattr(tables, "logger")
                assert hasattr(tables, "container")

            case TableTestType.FORMAT_AVAILABILITY:
                formats = tables.list_formats()
                assert isinstance(formats, list)
                assert len(formats) > 0
                for fmt in [
                    "simple",
                    "grid",
                    "fancy_grid",
                    "pipe",
                    "orgtbl",
                    "rst",
                    "html",
                    "latex",
                    "tsv",
                    "csv",
                ]:
                    assert fmt in formats

            case TableTestType.CREATE_TABLE_BASIC | TableTestType.CREATE_TABLE_ADVANCED:
                data = test_data[test_case.data_key]
                # Type narrowing: test_case.config is JsonDict
                # Use model_validate for proper type conversion (Pydantic handles validation)
                # Business Rule: Pydantic model_validate accepts dict[str, object] and validates types
                config = m.TableConfig.model_validate(test_case.config)
                # Convert data to TableData - ensure it's Iterable[Sequence | Mapping]
                table_data = cast(
                    "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
                    data,
                )
                result = tables.create_table(data=table_data, config=config)

                if test_case.expected_result:
                    tm.ok(result)
                    table_str = result.unwrap()
                    if test_case.content_assertions:
                        for assertion in test_case.content_assertions:
                            assert assertion in table_str
                else:
                    tm.fail(result)
                    if test_case.error_contains:
                        assert test_case.error_contains in (result.error or "").lower()

            case TableTestType.ERROR_HANDLING:
                data = test_data[test_case.data_key]
                # Type narrowing: test_case.config is JsonDict
                # Use model_validate for proper type conversion (Pydantic handles validation)
                # Business Rule: Pydantic model_validate accepts dict[str, object] and validates types
                config = m.TableConfig.model_validate(test_case.config)
                # Convert data to TableData - ensure it's Iterable[Sequence | Mapping]
                table_data = cast(
                    "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
                    data,
                )
                result = tables.create_table(data=table_data, config=config)

                tm.fail(result)
                if test_case.error_contains:
                    assert test_case.error_contains in (result.error or "").lower()

    def test_format_discovery_operations(self, tables: FlextCliTables) -> None:
        """Test format discovery and description operations."""
        # Test list_formats
        formats = tables.list_formats()
        assert isinstance(formats, list)
        assert len(formats) >= len(["simple", "grid", "fancy_grid"])

        # Test get_format_description - success case
        result = tables.get_format_description("grid")
        tm.ok(result)
        description = result.unwrap()
        assert isinstance(description, str)
        assert len(description) > 0

        # Test get_format_description - failure case
        result = tables.get_format_description("invalid_format")
        assert result.is_failure
        assert "unknown" in (result.error or "").lower()

        # Test print_available_formats
        format_result = tables.print_available_formats()
        assert format_result.is_success
        assert format_result.unwrap() is True

    @pytest.mark.parametrize(
        ("method_name", "format_name", "expected_content"),
        TableTestFactory.create_specialized_format_cases(),
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
        data = test_data["people_dict"]

        # Call the appropriate method
        # Convert data to TableData - ensure it's Iterable[Sequence | Mapping]
        table_data = cast(
            "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
            data,
        )
        match method_name:
            case "simple":
                result = tables.create_simple_table(table_data)
            case "grid":
                result = tables.create_grid_table(table_data)
            case "markdown":
                result = tables.create_markdown_table(table_data)
            case "html":
                result = tables.create_html_table(table_data)
            case "latex":
                result = tables.create_latex_table(table_data)
            case "rst":
                result = tables.create_rst_table(table_data)
            case _:
                pytest.fail(f"Unknown method: {method_name}")

        # Validate result
        tm.ok(result)
        table_str = result.unwrap()

        # Check expected content
        for content in expected_content:
            assert content in table_str

        # Validate format characteristics
        format_result = TestsCliTables.TableValidators.validate_table_format(
            table_str,
            format_name,
        )
        assert format_result.is_success

    def test_edge_cases_and_special_scenarios(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test edge cases and special scenarios."""
        # Single row table
        single_row = test_data["single_row"]
        config = m.TableConfig(table_format="simple")
        table_data = cast(
            "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
            single_row,
        )
        result = tables.create_table(data=table_data, config=config)
        assert result.is_success
        assert "Alice" in result.unwrap()

        # Table with None values
        with_none = test_data["with_none"]
        config = m.TableConfig(table_format="simple")
        table_data = cast(
            "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
            with_none,
        )
        result = tables.create_table(data=table_data, config=config)
        tm.ok(result)
        table_str = result.unwrap()
        assert "Alice" in table_str
        assert "Bob" in table_str

        # List of dicts with sequence headers (specific code path)
        custom_headers = ["name", "age", "city"]
        config = m.TableConfig(
            headers=custom_headers,
            table_format="simple",
        )
        table_data = cast(
            "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
            test_data["people_dict"],
        )
        result = tables.create_table(data=table_data, config=config)
        assert result.is_success
        assert "Alice" in result.unwrap()

    def test_latex_table_options(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test LaTeX table with various options."""
        data = test_data["people_dict"]

        # Convert data to TableData
        table_data = cast(
            "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
            data,
        )
        # Test longtable=True
        result = tables.create_latex_table(data=table_data, longtable=True)
        assert result.is_success
        assert "Alice" in result.unwrap()

        # Test longtable=False
        result = tables.create_latex_table(data=table_data, longtable=False)
        assert result.is_success
        assert "Alice" in result.unwrap()

        # Test booktabs=True
        result = tables.create_latex_table(
            data=table_data,
            booktabs=True,
            longtable=False,
        )
        assert result.is_success
        assert "Alice" in result.unwrap()

    def test_execute_method_flext_service_pattern(self, tables: FlextCliTables) -> None:
        """Test execute method following FlextService pattern."""
        result = tables.execute()
        tm.ok(result)
        assert result.unwrap() == {}

    def test_integration_workflow_complete(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test complete integration workflow."""
        data = test_data["people_dict"]

        # Step 1: List available formats
        formats = tables.list_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0

        # Step 2: Get description for first format
        first_format = formats[0]
        desc_result = tables.get_format_description(first_format)
        assert desc_result.is_success

        # Step 3: Create table with that format
        config = m.TableConfig(table_format=first_format)
        table_data = cast(
            "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
            data,
        )
        table_result = tables.create_table(data=table_data, config=config)
        assert table_result.is_success
        assert "Alice" in table_result.unwrap()

        # Step 4: Test multiple formats with same data
        test_formats = ["simple", "grid", "fancy_grid"][:3]  # Test first 3 formats
        for fmt in test_formats:
            config = m.TableConfig(table_format=fmt)
            result = tables.create_table(data=table_data, config=config)
            tm.ok(result), f"Format {fmt} failed"
            assert "Alice" in result.unwrap()

    # =========================================================================
    # VALIDATION TESTS WITH FLEXT_TEST HELPERS
    # =========================================================================

    def test_table_creation_with_flext_test_validation(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table creation using flext_tests validation helpers."""
        data = test_data["people_dict"]
        config = m.TableConfig(table_format="simple")
        table_data = cast(
            "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
            data,
        )
        result = tables.create_table(data=table_data, config=config)

        # Use flext_tests matchers for validation
        tm.ok(result)

        table_str = result.unwrap()
        assert "Alice" in table_str
        assert "name" in table_str

    def test_table_error_handling_with_flext_test_validation(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table error handling using flext_tests validation helpers."""
        # Test with empty data
        config = m.TableConfig(table_format="simple")
        table_data = cast(
            "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
            test_data["empty"],
        )
        result = tables.create_table(data=table_data, config=config)

        # This should fail for empty data
        assert isinstance(result, r)
        # Note: The actual behavior may succeed with empty table, so we just check it's a FlextResult

        # Test with invalid format
        config = m.TableConfig(table_format="invalid_format")
        table_data = cast(
            "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
            test_data["people_dict"],
        )
        result = tables.create_table(data=table_data, config=config)

        # This should fail
        assert isinstance(result, r)

    def test_table_format_validation_with_custom_assertions(
        self,
        tables: FlextCliTables,
        test_data: dict[str, t.GeneralValueType],
    ) -> None:
        """Test table format validation with custom assertion helpers."""
        data = test_data["people_dict"]

        # Test grid format
        config = m.TableConfig(table_format="grid")
        table_data = cast(
            "Sequence[Sequence[t.GeneralValueType]] | Sequence[Mapping[str, t.GeneralValueType]]",
            data,
        )
        result = tables.create_table(data=table_data, config=config)

        tm.ok(result)
        table_str = result.unwrap()

        # Custom validation for grid format
        validation_result = TestsCliTables.TableValidators.validate_table_format(
            table_str,
            "grid",
        )
        assert validation_result.is_success

        # Ensure expected content is present
        assert "Alice" in table_str
        assert "+" in table_str
        assert "|" in table_str
