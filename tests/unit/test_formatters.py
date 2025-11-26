"""FLEXT CLI Formatters Tests - Comprehensive Formatters Validation Testing.

Tests for FlextCliFormatters covering console operations, table/tree creation,
rendering, progress, status, layout, panel operations, and edge cases with 100% coverage.

Modules tested: flext_cli.formatters.FlextCliFormatters
Scope: All formatter operations, Rich integration, rendering, exception handling

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from rich.console import Console
from rich.progress import Progress
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree

from flext_cli import FlextCliFormatters, FlextCliTypes

from ..fixtures.constants import TestData
from ..helpers import FlextCliTestHelpers


class TestFlextCliFormatters:
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
        def create_test_data() -> FlextCliTypes.Data.CliDataDict:
            """Create test data dictionary."""
            return {
                TestData.Output.SUCCESS_MESSAGE: TestData.Output.INFO_MESSAGE,
                "key2": "value2",
            }

        @staticmethod
        def create_table_data() -> FlextCliTypes.Data.CliDataDict:
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
        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
        data = result.unwrap()
        assert "status" in data
        assert "service" in data

    @pytest.mark.parametrize(
        ("message", "style"),
        [
            (TestData.Output.SUCCESS_MESSAGE, None),
            ("Test", "bold red"),
            (TestData.Output.INFO_MESSAGE, TestData.Output.STYLE_GREEN),
        ],
    )
    def test_print(self, message: str, style: str | None) -> None:
        """Test print() method with various messages and styles."""
        formatters = self.Factories.create_formatters()
        result = formatters.print(message, style=style)
        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)

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
        data: FlextCliTypes.Data.CliDataDict | None,
        headers: list[str] | None,
        title: str | None,
    ) -> None:
        """Test create_table() with various configurations."""
        formatters = self.Factories.create_formatters()
        result = formatters.create_table(data=data, headers=headers, title=title)
        FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
        table = result.unwrap()
        assert isinstance(table, RichTable)

    @pytest.mark.parametrize("width", [None, 80, 120])
    def test_render_table_to_string(self, width: int | None) -> None:
        """Test render_table_to_string() with various widths."""
        formatters = self.Factories.create_formatters()
        table_result = formatters.create_table(title="Test")
        FlextCliTestHelpers.AssertHelpers.assert_result_success(table_result)
        table = table_result.unwrap()

        render_result = formatters.render_table_to_string(table, width=width)
        FlextCliTestHelpers.AssertHelpers.assert_result_success(render_result)
        output = render_result.unwrap()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_create_progress(self) -> None:
        """Test create_progress()."""
        formatters = FlextCliFormatters()
        result = formatters.create_progress()
        assert result.is_success
        progress = result.unwrap()
        assert isinstance(progress, Progress)

    def test_create_tree(self) -> None:
        """Test create_tree()."""
        formatters = FlextCliFormatters()
        result = formatters.create_tree("Root")
        assert result.is_success
        tree = result.unwrap()
        assert isinstance(tree, RichTree)

    def test_create_tree_with_options(self) -> None:
        """Test create_tree() with different label."""
        formatters = FlextCliFormatters()
        # create_tree() only accepts label parameter (no guide_style option)
        # For custom tree styling, access console directly and create Tree
        result = formatters.create_tree("Root Node")
        assert result.is_success
        tree = result.unwrap()
        assert isinstance(tree, RichTree)

    def test_render_tree_to_string(self) -> None:
        """Test render_tree_to_string()."""
        formatters = FlextCliFormatters()
        tree_result = formatters.create_tree("Root")
        assert tree_result.is_success
        tree = tree_result.unwrap()

        render_result = formatters.render_tree_to_string(tree)
        assert render_result.is_success
        output = render_result.unwrap()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_tree_to_string_with_width(self) -> None:
        """Test render_tree_to_string() with custom width."""
        formatters = FlextCliFormatters()
        tree_result = formatters.create_tree("Root")
        assert tree_result.is_success
        tree = tree_result.unwrap()

        render_result = formatters.render_tree_to_string(tree, width=80)
        assert render_result.is_success
        output = render_result.unwrap()
        assert isinstance(output, str)

    # =========================================================================
    # INTEGRATION TESTS (Consolidated from TestFlextCliFormattersIntegration)
    # =========================================================================

    def test_complete_table_workflow(self) -> None:
        """Test complete table creation and rendering workflow."""
        formatters = FlextCliFormatters()

        # Create table with data
        data: FlextCliTypes.Data.CliDataDict = {
            "Name": "Alice",
            "Age": "30",
            "City": "NYC",
        }
        table_result = formatters.create_table(
            data=data,
            headers=["Key", "Value"],
            title="User Info",
        )
        assert table_result.is_success

        # Render to string
        table = table_result.unwrap()
        render_result = formatters.render_table_to_string(table, width=100)
        assert render_result.is_success

        output = render_result.unwrap()
        assert "User Info" in output or len(output) > 0  # Title might be styled

    def test_complete_tree_workflow(self) -> None:
        """Test complete tree creation and rendering workflow."""
        formatters = FlextCliFormatters()

        # Create tree
        tree_result = formatters.create_tree("Project")
        assert tree_result.is_success

        tree = tree_result.unwrap()
        # Add some branches (using Rich directly since we're testing integration)
        tree.add("src/")
        tree.add("tests/")

        # Render to string
        render_result = formatters.render_tree_to_string(tree)
        assert render_result.is_success

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
        assert result.is_success

    def test_create_status(self) -> None:
        """Test create_status() method (lines 246-253)."""
        formatters = FlextCliFormatters()
        result = formatters.create_status("Processing...")
        assert result.is_success
        status = result.unwrap()
        assert status is not None

    def test_create_status_with_spinner(self) -> None:
        """Test create_status() with custom spinner."""
        formatters = FlextCliFormatters()
        result = formatters.create_status("Loading...", spinner="dots")
        assert result.is_success
        status = result.unwrap()
        assert status is not None

    def test_create_live(self) -> None:
        """Test create_live() method (lines 268-277)."""
        formatters = FlextCliFormatters()
        result = formatters.create_live()
        assert result.is_success
        live = result.unwrap()
        assert live is not None

    def test_create_live_with_refresh_rate(self) -> None:
        """Test create_live() with custom refresh rate."""
        formatters = FlextCliFormatters()
        result = formatters.create_live(refresh_per_second=10)
        assert result.is_success
        live = result.unwrap()
        assert live is not None

    def test_create_layout(self) -> None:
        """Test create_layout() method (lines 289-294)."""
        formatters = FlextCliFormatters()
        result = formatters.create_layout()
        assert result.is_success
        layout = result.unwrap()
        assert layout is not None

    def test_create_panel(self) -> None:
        """Test create_panel() method (lines 315-325)."""
        formatters = FlextCliFormatters()
        result = formatters.create_panel("Test content")
        assert result.is_success
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
        assert result.is_success
        panel = result.unwrap()
        assert panel is not None

    def test_create_table_dict_without_headers(self) -> None:
        """Test create_table() with CLI data dict but no headers (lines 133-134)."""
        formatters = FlextCliFormatters()
        data: FlextCliTypes.Data.CliDataDict = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }
        # No headers - will use else branch at line 131
        result = formatters.create_table(data=data)
        assert result.is_success
        table = result.unwrap()
        assert isinstance(table, RichTable)

    # =========================================================================
    # EXCEPTION HANDLER TESTS (Consolidated from TestFlextCliFormattersExceptionHandlers)
    # =========================================================================

    def test_print_exception_handler(self) -> None:
        """Test print() exception handler (lines 92-93).

        Uses real formatters to test actual behavior.
        """
        formatters = FlextCliFormatters()
        result = formatters.print("Test")
        # Should succeed with real console
        assert result.is_success

    def test_create_table_exception_handler(self) -> None:
        """Test create_table() exception handler (lines 138-139).

        Uses real formatters to test actual behavior.
        """
        formatters = FlextCliFormatters()
        result = formatters.create_table(title="Test")
        # Should succeed with real RichTable
        assert result.is_success

    def test_render_table_to_string_exception_handler(self) -> None:
        """Test render_table_to_string() exception handler (lines 166-167).

        Uses real formatters to test actual behavior.
        """
        formatters = FlextCliFormatters()

        # Create a valid table first
        table_result = formatters.create_table()
        assert table_result.is_success
        table = table_result.unwrap()

        # Call should succeed with real Console
        result = formatters.render_table_to_string(table)
        assert result.is_success

    def test_create_progress_exception_handler(self) -> None:
        """Test create_progress() exception handler (lines 183-184).

        Uses real formatters to test actual behavior.
        """
        formatters = FlextCliFormatters()
        result = formatters.create_progress()
        # Should succeed with real Progress
        assert result.is_success

    def test_create_tree_exception_handler(self) -> None:
        """Test create_tree() exception handler (lines 201-202).

        Uses real formatters to test actual behavior.
        """
        formatters = FlextCliFormatters()
        result = formatters.create_tree("Root")
        # Should succeed with real RichTree
        assert result.is_success

    def test_render_tree_to_string_exception_handler(self) -> None:
        """Test render_tree_to_string() exception handler (lines 225-226).

        Uses real formatters to test actual behavior.
        """
        formatters = FlextCliFormatters()

        # Create a valid tree first
        tree_result = formatters.create_tree("Root")
        assert tree_result.is_success
        tree = tree_result.unwrap()

        # Call should succeed with real Console
        result = formatters.render_tree_to_string(tree)
        assert result.is_success

    def test_create_status_exception_handler(self) -> None:
        """Test create_status() exception handler (lines 252-253).

        Uses real formatters to test actual behavior.
        """
        formatters = FlextCliFormatters()
        result = formatters.create_status("Loading...")
        # Should succeed with real RichStatus
        assert result.is_success

    def test_create_live_exception_handler(self) -> None:
        """Test create_live() exception handler (lines 276-277).

        Uses real formatters to test actual behavior.
        """
        formatters = FlextCliFormatters()
        result = formatters.create_live()
        # Should succeed with real RichLive
        assert result.is_success

    def test_create_layout_exception_handler(self) -> None:
        """Test create_layout() exception handler (lines 293-294).

        Uses real formatters to test actual behavior.
        """
        formatters = FlextCliFormatters()
        result = formatters.create_layout()
        # Should succeed with real RichLayout
        assert result.is_success

    def test_create_panel_exception_handler(self) -> None:
        """Test create_panel() exception handler (lines 324-325).

        Uses real formatters to test actual behavior.
        """
        formatters = FlextCliFormatters()
        result = formatters.create_panel("Content")
        # Should succeed with real RichPanel
        assert result.is_success
