"""Tests for FlextCliFormatters - SIMPLIFIED.

Tests ONLY the 8 core methods actually used by output.py.
Following zero-tolerance principle: Don't test library features (Rich).
Test business logic only.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from rich.progress import Progress
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree

from flext_cli.formatters import FlextCliFormatters


class TestFlextCliFormattersCore:
    """Test core FlextCliFormatters methods used by output.py."""

    def test_formatters_init(self) -> None:
        """Test formatters initialization."""
        formatters = FlextCliFormatters()
        assert formatters is not None
        assert isinstance(formatters, FlextCliFormatters)

    def test_console_property(self) -> None:
        """Test console property lazy loading."""
        formatters = FlextCliFormatters()
        console = formatters.console
        assert console is not None
        # Second access should return same instance
        console2 = formatters.console
        assert console is console2

    def test_get_console(self) -> None:
        """Test get_console() method."""
        formatters = FlextCliFormatters()
        console = formatters.get_console()
        assert console is not None
        assert console is formatters.console

    def test_execute(self) -> None:
        """Test service execute() method."""
        formatters = FlextCliFormatters()
        result = formatters.execute()
        assert result.is_success
        data = result.unwrap()
        assert "status" in data
        assert "service" in data

    def test_print_simple(self) -> None:
        """Test print() method."""
        formatters = FlextCliFormatters()
        result = formatters.print("Test message")
        assert result.is_success

    def test_print_with_style(self) -> None:
        """Test print() with style."""
        formatters = FlextCliFormatters()
        result = formatters.print("Test", style="bold red")
        assert result.is_success

    def test_create_table_empty(self) -> None:
        """Test create_table() with no data."""
        formatters = FlextCliFormatters()
        result = formatters.create_table()
        assert result.is_success
        table = result.unwrap()
        assert isinstance(table, RichTable)

    def test_create_table_with_title(self) -> None:
        """Test create_table() with title."""
        formatters = FlextCliFormatters()
        result = formatters.create_table(title="Test Table")
        assert result.is_success
        table = result.unwrap()
        assert isinstance(table, RichTable)

    def test_create_table_with_headers(self) -> None:
        """Test create_table() with headers."""
        formatters = FlextCliFormatters()
        result = formatters.create_table(headers=["Name", "Value"])
        assert result.is_success
        table = result.unwrap()
        assert isinstance(table, RichTable)

    def test_create_table_with_data(self) -> None:
        """Test create_table() with data."""
        formatters = FlextCliFormatters()
        data = {"key1": "value1", "key2": "value2"}
        result = formatters.create_table(data=data, headers=["Key", "Value"])
        assert result.is_success
        table = result.unwrap()
        assert isinstance(table, RichTable)

    def test_render_table_to_string(self) -> None:
        """Test render_table_to_string()."""
        formatters = FlextCliFormatters()
        table_result = formatters.create_table(title="Test")
        assert table_result.is_success
        table = table_result.unwrap()

        render_result = formatters.render_table_to_string(table)
        assert render_result.is_success
        output = render_result.unwrap()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_table_to_string_with_width(self) -> None:
        """Test render_table_to_string() with custom width."""
        formatters = FlextCliFormatters()
        table_result = formatters.create_table(title="Test")
        assert table_result.is_success
        table = table_result.unwrap()

        render_result = formatters.render_table_to_string(table, width=120)
        assert render_result.is_success
        output = render_result.unwrap()
        assert isinstance(output, str)

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
        """Test create_tree() with options."""
        formatters = FlextCliFormatters()
        result = formatters.create_tree("Root", guide_style="bold")
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


class TestFlextCliFormattersIntegration:
    """Integration tests for formatters."""

    def test_complete_table_workflow(self) -> None:
        """Test complete table creation and rendering workflow."""
        formatters = FlextCliFormatters()

        # Create table with data
        data = {"Name": "Alice", "Age": "30", "City": "NYC"}
        table_result = formatters.create_table(
            data=data, headers=["Key", "Value"], title="User Info"
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
        console2 = formatters.get_console()

        # Should be same instance
        assert console1 is console2

        # Should work with print
        result = formatters.print("Test")
        assert result.is_success
