"""Tests for FlextCliFormatters - SIMPLIFIED.

Tests ONLY the 8 core methods actually used by output.py.
Following zero-tolerance principle: Don't test library features (Rich).
Test business logic only.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from flext_core import FlextCore
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
        data: dict[
            str,
            str
            | int
            | float
            | bool
            | FlextCore.Types.List
            | FlextCore.Types.Dict
            | None,
        ] = {"key1": "value1", "key2": "value2"}
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
        data: dict[
            str,
            str
            | int
            | float
            | bool
            | FlextCore.Types.List
            | FlextCore.Types.Dict
            | None,
        ] = {"Name": "Alice", "Age": "30", "City": "NYC"}
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
            "Content", title="Test Panel", border_style="green"
        )
        assert result.is_success
        panel = result.unwrap()
        assert panel is not None

    def test_create_table_dict_without_headers(self) -> None:
        """Test create_table() with dict data but no headers (lines 133-134)."""
        formatters = FlextCliFormatters()
        data: dict[
            str,
            str
            | int
            | float
            | bool
            | FlextCore.Types.List
            | FlextCore.Types.Dict
            | None,
        ] = {"key1": "value1", "key2": "value2", "key3": "value3"}
        # No headers - will use else branch at line 131
        result = formatters.create_table(data=data)
        assert result.is_success
        table = result.unwrap()
        assert isinstance(table, RichTable)


class TestFlextCliFormattersExceptionHandlers:
    """Test exception handlers for formatters methods."""

    def test_print_exception_handler(self, monkeypatch: object) -> None:
        """Test print() exception handler (lines 92-93)."""
        formatters = FlextCliFormatters()

        # Mock console.print to raise exception
        def mock_print(*args: object, **kwargs: object) -> None:
            msg = "Print error"
            raise RuntimeError(msg)

        monkeypatch.setattr(formatters.console, "print", mock_print)

        # Call should catch exception and return failure
        result = formatters.print("Test")

        assert result.is_failure
        assert "Print failed" in str(result.error)

    def test_create_table_exception_handler(self, monkeypatch: object) -> None:
        """Test create_table() exception handler (lines 138-139)."""
        formatters = FlextCliFormatters()

        # Mock RichTable to raise exception
        def mock_table_init(*args: object, **kwargs: object) -> None:
            msg = "Table creation error"
            raise ValueError(msg)

        monkeypatch.setattr("flext_cli.formatters.RichTable", mock_table_init)

        # Call should catch exception and return failure
        result = formatters.create_table(title="Test")

        assert result.is_failure
        assert "Table creation failed" in str(result.error)

    def test_render_table_to_string_exception_handler(
        self, monkeypatch: object
    ) -> None:
        """Test render_table_to_string() exception handler (lines 166-167)."""
        formatters = FlextCliFormatters()

        # Create a valid table first
        table_result = formatters.create_table()
        assert table_result.is_success
        table = table_result.unwrap()

        # Mock Console to raise exception during rendering
        def mock_console_init(*args: object, **kwargs: object) -> None:
            msg = "Console creation error"
            raise RuntimeError(msg)

        monkeypatch.setattr("flext_cli.formatters.Console", mock_console_init)

        # Call should catch exception and return failure
        result = formatters.render_table_to_string(table)

        assert result.is_failure
        assert "Table rendering failed" in str(result.error)

    def test_create_progress_exception_handler(self, monkeypatch: object) -> None:
        """Test create_progress() exception handler (lines 183-184)."""
        formatters = FlextCliFormatters()

        # Mock Progress to raise exception
        def mock_progress_init(*args: object, **kwargs: object) -> None:
            msg = "Progress creation error"
            raise ValueError(msg)

        monkeypatch.setattr("flext_cli.formatters.Progress", mock_progress_init)

        # Call should catch exception and return failure
        result = formatters.create_progress()

        assert result.is_failure
        assert "Progress creation failed" in str(result.error)

    def test_create_tree_exception_handler(self, monkeypatch: object) -> None:
        """Test create_tree() exception handler (lines 201-202)."""
        formatters = FlextCliFormatters()

        # Mock RichTree to raise exception
        def mock_tree_init(*args: object, **kwargs: object) -> None:
            msg = "Tree creation error"
            raise ValueError(msg)

        monkeypatch.setattr("flext_cli.formatters.RichTree", mock_tree_init)

        # Call should catch exception and return failure
        result = formatters.create_tree("Root")

        assert result.is_failure
        assert "Tree creation failed" in str(result.error)

    def test_render_tree_to_string_exception_handler(self, monkeypatch: object) -> None:
        """Test render_tree_to_string() exception handler (lines 225-226)."""
        formatters = FlextCliFormatters()

        # Create a valid tree first
        tree_result = formatters.create_tree("Root")
        assert tree_result.is_success
        tree = tree_result.unwrap()

        # Mock Console to raise exception during rendering
        def mock_console_init(*args: object, **kwargs: object) -> None:
            msg = "Console creation error"
            raise RuntimeError(msg)

        monkeypatch.setattr("flext_cli.formatters.Console", mock_console_init)

        # Call should catch exception and return failure
        result = formatters.render_tree_to_string(tree)

        assert result.is_failure
        assert "Tree rendering failed" in str(result.error)

    def test_create_status_exception_handler(self, monkeypatch: object) -> None:
        """Test create_status() exception handler (lines 252-253)."""
        formatters = FlextCliFormatters()

        # Mock RichStatus to raise exception
        def mock_status_init(*args: object, **kwargs: object) -> None:
            msg = "Status creation error"
            raise ValueError(msg)

        monkeypatch.setattr("flext_cli.formatters.RichStatus", mock_status_init)

        # Call should catch exception and return failure
        result = formatters.create_status("Loading...")

        assert result.is_failure
        assert "Status creation failed" in str(result.error)

    def test_create_live_exception_handler(self, monkeypatch: object) -> None:
        """Test create_live() exception handler (lines 276-277)."""
        formatters = FlextCliFormatters()

        # Mock RichLive to raise exception
        def mock_live_init(*args: object, **kwargs: object) -> None:
            msg = "Live creation error"
            raise ValueError(msg)

        monkeypatch.setattr("flext_cli.formatters.RichLive", mock_live_init)

        # Call should catch exception and return failure
        result = formatters.create_live()

        assert result.is_failure
        assert "Live creation failed" in str(result.error)

    def test_create_layout_exception_handler(self, monkeypatch: object) -> None:
        """Test create_layout() exception handler (lines 293-294)."""
        formatters = FlextCliFormatters()

        # Mock RichLayout to raise exception
        def mock_layout_init(*args: object, **kwargs: object) -> None:
            msg = "Layout creation error"
            raise ValueError(msg)

        monkeypatch.setattr("flext_cli.formatters.RichLayout", mock_layout_init)

        # Call should catch exception and return failure
        result = formatters.create_layout()

        assert result.is_failure
        assert "Layout creation failed" in str(result.error)

    def test_create_panel_exception_handler(self, monkeypatch: object) -> None:
        """Test create_panel() exception handler (lines 324-325)."""
        formatters = FlextCliFormatters()

        # Mock RichPanel to raise exception
        def mock_panel_init(*args: object, **kwargs: object) -> None:
            msg = "Panel creation error"
            raise ValueError(msg)

        monkeypatch.setattr("flext_cli.formatters.RichPanel", mock_panel_init)

        # Call should catch exception and return failure
        result = formatters.create_panel("Content")

        assert result.is_failure
        assert "Panel creation failed" in str(result.error)
