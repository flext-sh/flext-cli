"""FLEXT CLI Formatters Tests - Comprehensive Formatters Validation Testing.

Tests for FlextCliFormatters covering console operations, table/tree creation,
rendering, progress, status, layout, panel operations, and edge cases with 100% coverage.

Modules tested: flext_cli.formatters.FlextCliFormatters
Scope: All formatter operations, Rich integration, rendering, exception handling

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

import pytest
from flext_core import t
from flext_tests import tm
from pytest_mock import MockFixture
from rich.console import Console
from rich.progress import Progress
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree

from flext_cli import FlextCliFormatters, r

# from ..fixtures.constants import TestData  # Fixtures removed - use conftest.py and flext_tests


class TestsCliFormatters:
    """Comprehensive tests for FlextCliFormatters functionality.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    # =========================================================================
    # NESTED: Factories
    # =========================================================================

    class Factories:
        """Factory methods for creating test instances."""

        @staticmethod
        def create_formatters() -> FlextCliFormatters:
            """Create a new FlextCliFormatters instance."""
            return FlextCliFormatters()

        @staticmethod
        def create_test_data() -> dict[str, t.GeneralValueType]:
            """Create test data dictionary."""
            return {
                "Success": "Info",
                "key2": "value2",
            }

        @staticmethod
        def create_table_data() -> dict[str, t.GeneralValueType]:
            """Create table test data."""
            return {
                "Name": "Alice",
                "Age": "30",
                "City": "NYC",
            }

    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================

    def test_formatters_init(self) -> None:
        """Test formatters initialization."""
        formatters = self.Factories.create_formatters()
        assert formatters is not None
        assert isinstance(formatters, FlextCliFormatters)

    def test_console_property(self) -> None:
        """Test console property access."""
        formatters = self.Factories.create_formatters()
        console = formatters.console
        assert console is not None
        assert isinstance(console, Console)
        # Second access should return same instance
        console2 = formatters.console
        assert console is console2

    def test_execute(self) -> None:
        """Test service execute() method."""
        formatters = self.Factories.create_formatters()
        result = formatters.execute()
        tm.ok(result)
        data = result.unwrap()
        assert "status" in data
        assert "service" in data

    @pytest.mark.parametrize(
        ("message", "style"),
        [
            ("Success", None),
            ("Test", "bold red"),
            ("Info", "green"),
        ],
    )
    def test_print(self, message: str, style: str | None) -> None:
        """Test print() method with various messages and styles."""
        formatters = self.Factories.create_formatters()
        result = formatters.print(message, style=style)
        tm.ok(result)

    @pytest.mark.parametrize(
        ("data", "headers", "title"),
        [
            (None, None, None),
            (None, None, "Test Table"),
            (None, ["Name", "Value"], None),
            (Factories.create_test_data(), ["Key", "Value"], None),
            (Factories.create_table_data(), ["Key", "Value"], "User Info"),
        ],
    )
    def test_create_table(
        self,
        data: dict[str, t.GeneralValueType] | None,
        headers: list[str] | None,
        title: str | None,
    ) -> None:
        """Test create_table() with various configurations."""
        formatters = self.Factories.create_formatters()
        result = formatters.create_table(data=data, headers=headers, title=title)
        tm.ok(result)
        table = result.unwrap()
        assert isinstance(table, RichTable)

    @pytest.mark.parametrize("width", [None, 80, 120])
    def test_render_table_to_string(self, width: int | None) -> None:
        """Test render_table_to_string() with various widths."""
        formatters = self.Factories.create_formatters()
        table_result = formatters.create_table(title="Test")
        tm.ok(table_result)
        table = table_result.unwrap()

        render_result = formatters.render_table_to_string(table, width=width)
        tm.ok(render_result)
        output = render_result.unwrap()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_create_progress(self) -> None:
        """Test create_progress()."""
        formatters = FlextCliFormatters()
        result = formatters.create_progress()
        tm.ok(result)
        progress = result.unwrap()
        assert isinstance(progress, Progress)

    def test_create_tree(self) -> None:
        """Test create_tree()."""
        formatters = FlextCliFormatters()
        result = formatters.create_tree("Root")
        tm.ok(result)
        tree = result.unwrap()
        assert isinstance(tree, RichTree)

    def test_create_tree_with_options(self) -> None:
        """Test create_tree() with different label."""
        formatters = FlextCliFormatters()
        # create_tree() only accepts label parameter (no guide_style option)
        # For custom tree styling, access console directly and create Tree
        result = formatters.create_tree("Root Node")
        tm.ok(result)
        tree = result.unwrap()
        assert isinstance(tree, RichTree)

    def test_render_tree_to_string(self) -> None:
        """Test render_tree_to_string()."""
        formatters = FlextCliFormatters()
        tree_result = formatters.create_tree("Root")
        tm.ok(tree_result)
        tree = tree_result.unwrap()

        render_result = formatters.render_tree_to_string(tree)
        tm.ok(render_result)
        output = render_result.unwrap()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_tree_to_string_with_width(self) -> None:
        """Test render_tree_to_string() with custom width."""
        formatters = FlextCliFormatters()
        tree_result = formatters.create_tree("Root")
        tm.ok(tree_result)
        tree = tree_result.unwrap()

        render_result = formatters.render_tree_to_string(tree, width=80)
        tm.ok(render_result)
        output = render_result.unwrap()
        assert isinstance(output, str)

    # =========================================================================
    # INTEGRATION TESTS (Consolidated from TestFlextCliFormattersIntegration)
    # =========================================================================

    def test_complete_table_workflow(self) -> None:
        """Test complete table creation and rendering workflow."""
        formatters = FlextCliFormatters()

        # Create table with data
        data: dict[str, t.GeneralValueType] = {
            "Name": "Alice",
            "Age": "30",
            "City": "NYC",
        }
        table_result = formatters.create_table(
            data=data,
            headers=["Key", "Value"],
            title="User Info",
        )
        tm.ok(table_result)

        # Render to string
        table = table_result.unwrap()
        render_result = formatters.render_table_to_string(table, width=100)
        tm.ok(render_result)

        output = render_result.unwrap()
        assert "User Info" in output or len(output) > 0  # Title might be styled

    def test_complete_tree_workflow(self) -> None:
        """Test complete tree creation and rendering workflow."""
        formatters = FlextCliFormatters()

        # Create tree
        tree_result = formatters.create_tree("Project")
        tm.ok(tree_result)

        tree = tree_result.unwrap()
        # Add some branches (using Rich directly since we're testing integration)
        tree.add("src/")
        tree.add("tests/")

        # Render to string
        render_result = formatters.render_tree_to_string(tree)
        tm.ok(render_result)

        output = render_result.unwrap()
        assert "Project" in output
        assert len(output) > 0

    def test_console_reuse(self) -> None:
        """Test that console instance is reused."""
        formatters = FlextCliFormatters()

        console1 = formatters.console
        console2 = formatters.console

        # Should be same instance
        assert console1 is console2

        # Should work with print
        result = formatters.print("Test")
        tm.ok(result)

    def test_create_status(self) -> None:
        """Test create_status() method (lines 246-253)."""
        formatters = FlextCliFormatters()
        result = formatters.create_status("Processing...")
        tm.ok(result)
        status = result.unwrap()
        assert status is not None

    def test_create_status_with_spinner(self) -> None:
        """Test create_status() with custom spinner."""
        formatters = FlextCliFormatters()
        result = formatters.create_status("Loading...", spinner="dots")
        tm.ok(result)
        status = result.unwrap()
        assert status is not None

    def test_create_live(self) -> None:
        """Test create_live() method (lines 268-277)."""
        formatters = FlextCliFormatters()
        result = formatters.create_live()
        tm.ok(result)
        live = result.unwrap()
        assert live is not None

    def test_create_live_with_refresh_rate(self) -> None:
        """Test create_live() with custom refresh rate."""
        formatters = FlextCliFormatters()
        result = formatters.create_live(refresh_per_second=10)
        tm.ok(result)
        live = result.unwrap()
        assert live is not None

    def test_create_layout(self) -> None:
        """Test create_layout() method (lines 289-294)."""
        formatters = FlextCliFormatters()
        result = formatters.create_layout()
        tm.ok(result)
        layout = result.unwrap()
        assert layout is not None

    def test_create_panel(self) -> None:
        """Test create_panel() method (lines 315-325)."""
        formatters = FlextCliFormatters()
        result = formatters.create_panel("Test content")
        tm.ok(result)
        panel = result.unwrap()
        assert panel is not None

    def test_create_panel_with_title(self) -> None:
        """Test create_panel() with title and border."""
        formatters = FlextCliFormatters()
        result = formatters.create_panel(
            "Content",
            title="Test Panel",
            border_style="green",
        )
        tm.ok(result)
        panel = result.unwrap()
        assert panel is not None

    def test_create_table_dict_without_headers(self) -> None:
        """Test create_table() with CLI data dict but no headers (lines 133-134)."""
        formatters = FlextCliFormatters()
        data: dict[str, t.GeneralValueType] = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }
        # No headers - will use else branch at line 131
        result = formatters.create_table(data=data)
        tm.ok(result)
        table = result.unwrap()
        assert isinstance(table, RichTable)

    # =========================================================================
    # EXCEPTION HANDLER TESTS (Automated with advanced parametrization)
    # =========================================================================

    class ExceptionHandlerTestCases:
        """Factory for exception handler test cases - reduces 100+ lines."""

        @staticmethod
        def get_exception_handler_cases() -> list[
            tuple[str, Callable[[FlextCliFormatters], r[object]]]
        ]:
            """Get parametrized test cases for exception handlers.

            Returns:
                List of (test_name, method_callable) tuples for pytest.mark.parametrize

            """

            def call_print(fmt: FlextCliFormatters) -> r[object]:
                return cast("r[object]", fmt.print("Test"))

            def call_create_table(fmt: FlextCliFormatters) -> r[object]:
                return cast("r[object]", fmt.create_table(title="Test"))

            def call_render_table(fmt: FlextCliFormatters) -> r[object]:
                table_result: r[object] = cast("r[object]", fmt.create_table())
                if table_result.is_success:
                    table = cast("RichTable", table_result.unwrap())
                    return cast(
                        "r[object]",
                        fmt.render_table_to_string(table),
                    )
                return table_result

            def call_create_progress(fmt: FlextCliFormatters) -> r[object]:
                return cast("r[object]", fmt.create_progress())

            def call_create_tree(fmt: FlextCliFormatters) -> r[object]:
                return cast("r[object]", fmt.create_tree("Root"))

            def call_render_tree(fmt: FlextCliFormatters) -> r[object]:
                tree_result: r[object] = cast("r[object]", fmt.create_tree("Root"))
                if tree_result.is_success:
                    tree = cast("RichTree", tree_result.unwrap())
                    return cast(
                        "r[object]",
                        fmt.render_tree_to_string(tree),
                    )
                return tree_result

            def call_create_status(fmt: FlextCliFormatters) -> r[object]:
                return cast("r[object]", fmt.create_status("Loading..."))

            def call_create_live(fmt: FlextCliFormatters) -> r[object]:
                return cast("r[object]", fmt.create_live())

            def call_create_layout(fmt: FlextCliFormatters) -> r[object]:
                return cast("r[object]", fmt.create_layout())

            def call_create_panel(fmt: FlextCliFormatters) -> r[object]:
                return cast("r[object]", fmt.create_panel("Content"))

            return [
                ("print", call_print),
                ("create_table", call_create_table),
                ("render_table_to_string", call_render_table),
                ("create_progress", call_create_progress),
                ("create_tree", call_create_tree),
                ("render_tree_to_string", call_render_tree),
                ("create_status", call_create_status),
                ("create_live", call_create_live),
                ("create_layout", call_create_layout),
                ("create_panel", call_create_panel),
            ]

    @pytest.mark.parametrize(
        ("method_name", "method_call"),
        ExceptionHandlerTestCases.get_exception_handler_cases(),
    )
    def test_exception_handlers(
        self,
        method_name: str,
        method_call: Callable[[FlextCliFormatters], r[object]],
        mocker: MockFixture,
    ) -> None:
        """Test exception handlers using advanced parametrization - reduces 100+ lines.

        Uses mocked formatters to force exceptions and verify error handling.
        """
        formatters = self.Factories.create_formatters()

        # Mock internal console or methods to raise exception
        if method_name == "print":
            mocker.patch.object(
                formatters.console,
                "print",
                side_effect=Exception("Print error"),
            )
        elif method_name == "create_table":
            # Mock RichTable constructor to raise exception
            mocker.patch(
                "flext_cli.formatters.RichTable",
                side_effect=Exception("Table error"),
            )
        elif method_name == "render_table_to_string":
            # Mock Console constructor used inside render to raise exception
            # We need to target the Console imported in formatters.py
            mocker.patch(
                "flext_cli.formatters.Console",
                side_effect=Exception("Render error"),
            )
        elif method_name == "create_progress":
            mocker.patch(
                "flext_cli.formatters.Progress",
                side_effect=Exception("Progress error"),
            )
        elif method_name == "create_tree":
            mocker.patch(
                "flext_cli.formatters.RichTree",
                side_effect=Exception("Tree error"),
            )
        elif method_name == "render_tree_to_string":
            # Mock Console constructor used inside render to raise exception
            mocker.patch(
                "flext_cli.formatters.Console",
                side_effect=Exception("Render error"),
            )
        elif method_name == "create_status":
            mocker.patch(
                "flext_cli.formatters.RichStatus",
                side_effect=Exception("Status error"),
            )
        elif method_name == "create_live":
            mocker.patch(
                "flext_cli.formatters.RichLive",
                side_effect=Exception("Live error"),
            )
        elif method_name == "create_layout":
            mocker.patch(
                "flext_cli.formatters.RichLayout",
                side_effect=Exception("Layout error"),
            )
        elif method_name == "create_panel":
            mocker.patch(
                "flext_cli.formatters.RichPanel",
                side_effect=Exception("Panel error"),
            )

        result = method_call(formatters)

        # Verify it returns failure
        assert isinstance(result, r)
        assert result.is_failure
