"""FLEXT CLI Formatters Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliFormatters covering all Rich abstraction functionality
with real Rich operations and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_core import FlextResult
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress
from rich.rule import Rule
from rich.spinner import Spinner
from rich.status import Status
from rich.syntax import Syntax
from rich.table import Table as RichTable
from rich.text import Text
from rich.tree import Tree

from flext_cli.formatters import FlextCliFormatters


class TestFlextCliFormatters:
    """Comprehensive tests for FlextCliFormatters Rich abstraction."""

    @pytest.fixture
    def formatters(self) -> FlextCliFormatters:
        """Create FlextCliFormatters instance for testing."""
        return FlextCliFormatters()

    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================

    def test_formatters_initialization(self, formatters: FlextCliFormatters) -> None:
        """Test formatters initialization."""
        assert isinstance(formatters, FlextCliFormatters)
        assert hasattr(formatters, "_console")
        assert hasattr(formatters, "_logger")
        assert hasattr(formatters, "_container")

    def test_formatters_execute(self, formatters: FlextCliFormatters) -> None:
        """Test formatters execute method."""
        result = formatters.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is None

    def test_get_console(self, formatters: FlextCliFormatters) -> None:
        """Test getting Rich console."""
        console = formatters.get_console()

        assert isinstance(console, Console)

    # =========================================================================
    # CONSOLE OPERATIONS TESTS
    # =========================================================================

    def test_print_simple(self, formatters: FlextCliFormatters) -> None:
        """Test simple print operation."""
        result = formatters.print("Test message")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_print_with_style(self, formatters: FlextCliFormatters) -> None:
        """Test print with styling."""
        result = formatters.print("Styled message", style="bold red")

        assert result.is_success

    def test_print_with_formatting_options(
        self, formatters: FlextCliFormatters
    ) -> None:
        """Test print with various formatting options."""
        result = formatters.print(
            "Formatted text",
            justify="center",
            emoji=True,
            markup=True,
            highlight=True,
        )

        assert result.is_success

    # =========================================================================
    # PANEL TESTS
    # =========================================================================

    def test_create_panel_simple(self, formatters: FlextCliFormatters) -> None:
        """Test creating simple panel."""
        result = formatters.create_panel("Panel content")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), Panel)

    def test_create_panel_with_title(self, formatters: FlextCliFormatters) -> None:
        """Test creating panel with title."""
        result = formatters.create_panel(
            "Panel content", title="Test Panel", border_style="blue"
        )

        assert result.is_success
        panel = result.unwrap()
        assert isinstance(panel, Panel)

    def test_create_panel_with_all_options(
        self, formatters: FlextCliFormatters
    ) -> None:
        """Test creating panel with all options."""
        result = formatters.create_panel(
            "Content",
            title="Main Title",
            title_align="center",
            subtitle="Subtitle",
            subtitle_align="right",
            border_style="green",
            padding=(1, 2),
            expand=True,
            width=80,
        )

        assert result.is_success
        assert isinstance(result.unwrap(), Panel)

    def test_display_panel(self, formatters: FlextCliFormatters) -> None:
        """Test display panel (create + print)."""
        result = formatters.display_panel(
            "Panel content", title="Display Test", border_style="yellow"
        )

        assert result.is_success

    # =========================================================================
    # LAYOUT TESTS
    # =========================================================================

    def test_create_layout_simple(self, formatters: FlextCliFormatters) -> None:
        """Test creating simple layout."""
        result = formatters.create_layout()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), Layout)

    def test_create_layout_with_options(self, formatters: FlextCliFormatters) -> None:
        """Test creating layout with options."""
        result = formatters.create_layout(
            name="test_layout", size=10, minimum_size=5, ratio=2
        )

        assert result.is_success
        layout = result.unwrap()
        assert isinstance(layout, Layout)
        assert layout.name == "test_layout"

    # =========================================================================
    # LIVE DISPLAY TESTS
    # =========================================================================

    def test_create_live_display(self, formatters: FlextCliFormatters) -> None:
        """Test creating live display."""
        result = formatters.create_live_display()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), Live)

    def test_create_live_display_with_options(
        self, formatters: FlextCliFormatters
    ) -> None:
        """Test creating live display with options."""
        result = formatters.create_live_display(
            refresh_per_second=10, auto_refresh=True, transient=True
        )

        assert result.is_success
        assert isinstance(result.unwrap(), Live)

    def test_create_live_display_with_renderable(
        self, formatters: FlextCliFormatters
    ) -> None:
        """Test creating live display with initial renderable."""
        table_result = formatters.create_table(title="Live Table")
        assert table_result.is_success

        result = formatters.create_live_display_with_renderable(
            table_result.unwrap(), refresh_per_second=5, transient=True
        )

        assert result.is_success
        assert isinstance(result.unwrap(), Live)

    # =========================================================================
    # SPINNER AND STATUS TESTS
    # =========================================================================

    def test_create_spinner_simple(self, formatters: FlextCliFormatters) -> None:
        """Test creating simple spinner."""
        result = formatters.create_spinner()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), Spinner)

    def test_create_spinner_with_options(self, formatters: FlextCliFormatters) -> None:
        """Test creating spinner with options."""
        result = formatters.create_spinner(
            spinner_name="dots", text="Loading...", style="cyan"
        )

        assert result.is_success
        assert isinstance(result.unwrap(), Spinner)

    def test_create_status_simple(self, formatters: FlextCliFormatters) -> None:
        """Test creating simple status."""
        result = formatters.create_status("Processing...")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), Status)

    def test_create_status_with_options(self, formatters: FlextCliFormatters) -> None:
        """Test creating status with options."""
        result = formatters.create_status(
            "Working...", spinner="dots", spinner_style="green"
        )

        assert result.is_success
        assert isinstance(result.unwrap(), Status)

    # =========================================================================
    # PROGRESS BAR TESTS
    # =========================================================================

    def test_create_progress_default(self, formatters: FlextCliFormatters) -> None:
        """Test creating progress with default columns."""
        result = formatters.create_progress()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), Progress)

    def test_create_progress_with_options(self, formatters: FlextCliFormatters) -> None:
        """Test creating progress with options."""
        result = formatters.create_progress(transient=True, expand=True)

        assert result.is_success
        assert isinstance(result.unwrap(), Progress)

    # =========================================================================
    # MARKDOWN TESTS
    # =========================================================================

    def test_render_markdown_simple(self, formatters: FlextCliFormatters) -> None:
        """Test rendering simple markdown."""
        result = formatters.render_markdown("# Title\n\nParagraph text")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), Markdown)

    def test_render_markdown_with_code(self, formatters: FlextCliFormatters) -> None:
        """Test rendering markdown with code blocks."""
        markdown_text = """
# Code Example

```python
def hello():
    print("Hello, world!")
```
"""
        result = formatters.render_markdown(
            markdown_text, code_theme="monokai", inline_code_lexer="python"
        )

        assert result.is_success
        assert isinstance(result.unwrap(), Markdown)

    def test_display_markdown(self, formatters: FlextCliFormatters) -> None:
        """Test display markdown (render + print)."""
        result = formatters.display_markdown("# Test\n\n**Bold** text")

        assert result.is_success

    # =========================================================================
    # SYNTAX HIGHLIGHTING TESTS
    # =========================================================================

    def test_highlight_code_simple(self, formatters: FlextCliFormatters) -> None:
        """Test simple code highlighting."""
        result = formatters.highlight_code('print("Hello")', language="python")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), Syntax)

    def test_highlight_code_with_options(self, formatters: FlextCliFormatters) -> None:
        """Test code highlighting with options."""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
        result = formatters.highlight_code(
            code,
            language="python",
            theme="monokai",
            line_numbers=True,
            word_wrap=True,
            line_range=(1, 5),
        )

        assert result.is_success
        assert isinstance(result.unwrap(), Syntax)

    def test_highlight_code_different_languages(
        self, formatters: FlextCliFormatters
    ) -> None:
        """Test highlighting different programming languages."""
        languages = [
            ("python", 'print("test")'),
            ("javascript", 'console.log("test")'),
            ("json", '{"key": "value"}'),
            ("yaml", "key: value"),
        ]

        for language, code in languages:
            result = formatters.highlight_code(code, language=language)
            assert result.is_success, f"Failed for language: {language}"
            assert isinstance(result.unwrap(), Syntax)

    def test_display_code(self, formatters: FlextCliFormatters) -> None:
        """Test display code (highlight + print)."""
        result = formatters.display_code('print("Hello")', language="python")

        assert result.is_success

    # =========================================================================
    # RULE AND DIVIDER TESTS
    # =========================================================================

    def test_create_rule_simple(self, formatters: FlextCliFormatters) -> None:
        """Test creating simple rule."""
        result = formatters.create_rule()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), Rule)

    def test_create_rule_with_title(self, formatters: FlextCliFormatters) -> None:
        """Test creating rule with title."""
        result = formatters.create_rule(title="Section", style="blue")

        assert result.is_success
        assert isinstance(result.unwrap(), Rule)

    def test_create_rule_with_all_options(self, formatters: FlextCliFormatters) -> None:
        """Test creating rule with all options."""
        result = formatters.create_rule(
            title="Custom Rule", characters="=", style="red", align="center"
        )

        assert result.is_success
        assert isinstance(result.unwrap(), Rule)

    def test_display_rule(self, formatters: FlextCliFormatters) -> None:
        """Test display rule (create + print)."""
        result = formatters.display_rule(title="Display Rule", style="green")

        assert result.is_success

    # =========================================================================
    # TEXT STYLING AND ALIGNMENT TESTS
    # =========================================================================

    def test_create_text_simple(self, formatters: FlextCliFormatters) -> None:
        """Test creating simple text."""
        result = formatters.create_text("Simple text")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), Text)

    def test_create_text_with_style(self, formatters: FlextCliFormatters) -> None:
        """Test creating styled text."""
        result = formatters.create_text(
            "Styled text", style="bold red", justify="center", no_wrap=True
        )

        assert result.is_success
        assert isinstance(result.unwrap(), Text)

    def test_align_text_simple(self, formatters: FlextCliFormatters) -> None:
        """Test aligning text."""
        result = formatters.align_text("Centered text", align="center")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_align_text_with_dimensions(self, formatters: FlextCliFormatters) -> None:
        """Test aligning text with width and height."""
        result = formatters.align_text(
            "Aligned", align="center", vertical="middle", width=50, height=10
        )

        assert result.is_success

    # =========================================================================
    # TABLE TESTS
    # =========================================================================

    def test_create_table_simple(self, formatters: FlextCliFormatters) -> None:
        """Test creating simple Rich table."""
        result = formatters.create_table()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), RichTable)

    def test_create_table_with_title(self, formatters: FlextCliFormatters) -> None:
        """Test creating table with title."""
        result = formatters.create_table(title="Test Table", caption="Table caption")

        assert result.is_success
        table = result.unwrap()
        assert isinstance(table, RichTable)

    def test_create_table_with_all_options(
        self, formatters: FlextCliFormatters
    ) -> None:
        """Test creating table with all options."""
        result = formatters.create_table(
            title="Full Table",
            caption="Caption",
            show_header=True,
            show_lines=True,
            show_edge=True,
            expand=True,
            padding=(1, 2),
        )

        assert result.is_success
        assert isinstance(result.unwrap(), RichTable)

    def test_create_table_and_populate(self, formatters: FlextCliFormatters) -> None:
        """Test creating table and adding data."""
        table_result = formatters.create_table(title="Data Table")
        assert table_result.is_success

        table = table_result.unwrap()
        table.add_column("Name")
        table.add_column("Age")
        table.add_row("Alice", "30")
        table.add_row("Bob", "25")

        # Table should have data
        assert len(table.columns) == 2

    # =========================================================================
    # TREE TESTS
    # =========================================================================

    def test_create_tree_simple(self, formatters: FlextCliFormatters) -> None:
        """Test creating simple tree."""
        result = formatters.create_tree("Root")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), Tree)

    def test_create_tree_with_style(self, formatters: FlextCliFormatters) -> None:
        """Test creating tree with guide style."""
        result = formatters.create_tree("Root", guide_style="bold blue")

        assert result.is_success
        assert isinstance(result.unwrap(), Tree)

    def test_create_tree_and_populate(self, formatters: FlextCliFormatters) -> None:
        """Test creating tree and adding nodes."""
        tree_result = formatters.create_tree("Root")
        assert tree_result.is_success

        tree = tree_result.unwrap()
        branch1 = tree.add("Branch 1")
        branch1.add("Leaf 1.1")
        branch1.add("Leaf 1.2")

        branch2 = tree.add("Branch 2")
        branch2.add("Leaf 2.1")

        # Tree should be populated
        assert tree.label == "Root"

    # =========================================================================
    # TRACEBACK FORMATTING TESTS
    # =========================================================================

    def test_format_exception_simple(self, formatters: FlextCliFormatters) -> None:
        """Test formatting exception with Rich traceback."""
        try:
            msg = "Test error"
            raise ValueError(msg)
        except ValueError:
            result = formatters.format_exception()

            assert isinstance(result, FlextResult)
            assert result.is_success

    def test_format_exception_with_options(
        self, formatters: FlextCliFormatters
    ) -> None:
        """Test formatting exception with options."""
        try:
            msg = "Complex error"
            raise RuntimeError(msg)
        except RuntimeError:
            result = formatters.format_exception(
                show_locals=True, width=120, extra_lines=5, word_wrap=True
            )

            assert result.is_success

    # =========================================================================
    # INTERACTIVE FEATURES TESTS (Mocked Input)
    # =========================================================================

    def test_clear_console(self, formatters: FlextCliFormatters) -> None:
        """Test clearing console."""
        result = formatters.clear()

        assert isinstance(result, FlextResult)
        assert result.is_success

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_formatters_complete_workflow(self, formatters: FlextCliFormatters) -> None:
        """Test complete formatting workflow."""
        # Step 1: Create panel
        panel_result = formatters.create_panel("Workflow Test", title="Step 1")
        assert panel_result.is_success

        # Step 2: Create table
        table_result = formatters.create_table(title="Data")
        assert table_result.is_success
        table = table_result.unwrap()
        table.add_column("Item")
        table.add_column("Status")
        table.add_row("Task 1", "Complete")

        # Step 3: Create tree
        tree_result = formatters.create_tree("Project")
        assert tree_result.is_success
        tree = tree_result.unwrap()
        tree.add("Module 1")

        # Step 4: Create rule
        rule_result = formatters.create_rule(title="Section")
        assert rule_result.is_success

        # Step 5: Highlight code
        code_result = formatters.highlight_code('print("test")', language="python")
        assert code_result.is_success

    def test_formatters_real_output_operations(
        self, formatters: FlextCliFormatters
    ) -> None:
        """Test real output operations without mocks."""
        # Test various real output scenarios
        operations = [
            ("print", lambda: formatters.print("Test output")),
            (
                "panel",
                lambda: formatters.display_panel("Panel", title="Test"),
            ),
            ("rule", lambda: formatters.display_rule(title="Rule")),
            (
                "markdown",
                lambda: formatters.display_markdown("# Test\n\nContent"),
            ),
            ("code", lambda: formatters.display_code("x = 1", language="python")),
        ]

        for name, operation in operations:
            result = operation()
            assert result.is_success, f"Operation {name} failed"

    # =========================================================================
    # EDGE CASES AND ERROR HANDLING
    # =========================================================================

    def test_formatters_edge_cases(self, formatters: FlextCliFormatters) -> None:
        """Test edge cases and boundary conditions."""
        # Empty content
        result = formatters.create_panel("")
        assert result.is_success

        # Empty markdown
        result = formatters.render_markdown("")
        assert result.is_success

        # Empty code
        result = formatters.highlight_code("", language="python")
        assert result.is_success

        # Empty tree
        result = formatters.create_tree("")
        assert result.is_success
