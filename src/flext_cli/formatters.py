"""FLEXT CLI - Rich Abstraction Layer.

This file contains ALL Rich imports for the FLEXT CLI ecosystem.
All Rich functionality is wrapped here and exposed through FlextResult-based APIs.

ZERO TOLERANCE ENFORCEMENT: No other file may import Rich directly except this one.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Iterable
from io import StringIO
from types import ModuleType
from typing import Literal

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)
from rich.align import Align, AlignMethod, VerticalAlignMethod
from rich.console import Console, JustifyMethod, OverflowMethod, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.rule import Rule
from rich.spinner import Spinner
from rich.status import Status
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table as RichTable
from rich.text import Text
from rich.traceback import Traceback
from rich.tree import Tree


class FlextCliFormatters(FlextService[object]):
    r"""Complete Rich abstraction layer.

    This class wraps ALL Rich functionality to prevent direct Rich imports
    across the FLEXT ecosystem. Provides FlextResult-based APIs for:

    - Console operations (output, styling, emoji, hyperlinks)
    - Panels and containers
    - Layouts (rows, columns, splits)
    - Live displays (real-time updates)
    - Spinners and status indicators
    - Markdown rendering
    - Syntax highlighting
    - Tables and trees
    - Progress bars
    - Rules and dividers
    - Traceback formatting

    Examples:
        >>> formatters = FlextCliFormatters()
        >>>
        >>> # Create panel
        >>> panel_result = formatters.create_panel(
        ...     "Important Message", title="Alert", border_style="red"
        ... )
        >>>
        >>> # Render markdown
        >>> md_result = formatters.render_markdown("# Title\\n\\nContent")
        >>>
        >>> # Syntax highlighting
        >>> code_result = formatters.highlight_code("print('Hello')", language="python")

    Note:
        ALL Rich functionality MUST be accessed through this class.
        Direct Rich imports are FORBIDDEN in ecosystem projects.

    """

    def __init__(self) -> None:
        """Initialize Rich formatters layer."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()
        self._console = Console()

    # =========================================================================
    # CONSOLE OPERATIONS
    # =========================================================================

    def get_console(self) -> Console:
        """Get Rich Console instance.

        Returns:
            Rich Console instance

        Note:
            Exposed for internal flext-cli use only.
            Ecosystem should use formatter methods instead.

        """
        return self._console

    def print(
        self,
        *objects: RenderableType,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        no_wrap: bool | None = None,
        emoji: bool | None = None,
        markup: bool | None = None,
        highlight: bool | None = None,
        width: int | None = None,
        crop: bool = True,
        soft_wrap: bool = False,
    ) -> FlextResult[None]:
        """Print to console with Rich formatting.

        Args:
            *objects: Objects to print
            sep: Separator between objects
            end: End character
            style: Text style
            justify: Text justification (left, right, center, full)
            overflow: Overflow handling (crop, fold, ellipsis)
            no_wrap: Disable wrapping
            emoji: Enable emoji codes
            markup: Enable markup
            highlight: Enable automatic highlighting
            width: Force width
            crop: Crop text to fit
            soft_wrap: Enable soft wrap

        Returns:
            FlextResult[None]

        """
        try:
            self._console.print(
                *objects,
                sep=sep,
                end=end,
                style=style,
                justify=justify,
                overflow=overflow,
                no_wrap=no_wrap,
                emoji=emoji,
                markup=markup,
                highlight=highlight,
                width=width,
                crop=crop,
                soft_wrap=soft_wrap,
            )
            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Failed to print to console: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    # =========================================================================
    # PANELS
    # =========================================================================

    def create_panel(
        self,
        content: str | Text,
        title: str | None = None,
        title_align: Literal["left", "center", "right"] = "left",
        subtitle: str | None = None,
        subtitle_align: Literal["left", "center", "right"] = "left",
        border_style: str | Style = "blue",
        padding: tuple[int, int] | tuple[int, int, int, int] = (0, 1),
        *,
        expand: bool = True,
        width: int | None = None,
    ) -> FlextResult[Panel]:
        """Create Rich panel with borders.

        Args:
            content: Panel content
            title: Panel title
            title_align: Title alignment (left, center, right)
            subtitle: Panel subtitle
            subtitle_align: Subtitle alignment
            border_style: Border color/style
            padding: Padding (top/bottom, left/right) or (top, right, bottom, left)
            expand: Expand to fill width
            width: Fixed width

        Returns:
            FlextResult containing Rich Panel

        Example:
            >>> formatters = FlextCliFormatters()
            >>> panel = formatters.create_panel(
            ...     "Important message", title="Alert", border_style="red bold"
            ... )

        """
        try:
            panel = Panel(
                content,
                title=title,
                title_align=title_align,
                subtitle=subtitle,
                subtitle_align=subtitle_align,
                border_style=border_style,
                padding=padding,
                expand=expand,
                width=width,
            )
            self._logger.debug("Created Rich panel", extra={"title": title})
            return FlextResult[Panel].ok(panel)
        except Exception as e:
            error_msg = f"Failed to create panel: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Panel].fail(error_msg)

    def display_panel(
        self,
        content: str | Text,
        title: str | None = None,
        border_style: str = "blue",
    ) -> FlextResult[None]:
        """Create and display panel in one operation.

        Args:
            content: Panel content
            title: Panel title
            border_style: Border style

        Returns:
            FlextResult[None]

        """
        panel_result = self.create_panel(
            content,
            title=title,
            border_style=border_style,
        )
        if panel_result.is_failure:
            return FlextResult[None].fail(panel_result.error)

        return self.print(panel_result.unwrap())

    # =========================================================================
    # LAYOUTS
    # =========================================================================

    def create_layout(
        self,
        name: str = "root",
        size: int | None = None,
        minimum_size: int = 1,
        ratio: int = 1,
    ) -> FlextResult[Layout]:
        """Create Rich layout for complex arrangements.

        Args:
            name: Layout name
            size: Fixed size
            minimum_size: Minimum size
            ratio: Size ratio relative to siblings

        Returns:
            FlextResult containing Rich Layout

        Example:
            >>> formatters = FlextCliFormatters()
            >>> layout_result = formatters.create_layout()
            >>> if layout_result.is_success:
            ...     layout = layout_result.unwrap()
            ...     layout.split_row(
            ...         Layout(name="left"),
            ...         Layout(name="right"),
            ...     )

        """
        try:
            layout = Layout(
                name=name,
                size=size,
                minimum_size=minimum_size,
                ratio=ratio,
            )
            self._logger.debug("Created Rich layout", extra={"layout_name": name})
            return FlextResult[Layout].ok(layout)
        except Exception as e:
            error_msg = f"Failed to create layout: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Layout].fail(error_msg)

    # =========================================================================
    # LIVE DISPLAYS
    # =========================================================================

    def create_live_display(
        self,
        refresh_per_second: float = 4,
        *,
        auto_refresh: bool = True,
        transient: bool = False,
    ) -> FlextResult[Live]:
        """Create Rich Live display for real-time updates.

        Args:
            auto_refresh: Automatically refresh display
            refresh_per_second: Refresh rate
            transient: Remove display when done

        Returns:
            FlextResult containing Rich Live instance

        Example:
            >>> formatters = FlextCliFormatters()
            >>> live_result = formatters.create_live_display()
            >>> if live_result.is_success:
            ...     with live_result.unwrap() as live:
            ...         live.update("Processing...")

        """
        try:
            live = Live(
                auto_refresh=auto_refresh,
                refresh_per_second=refresh_per_second,
                transient=transient,
                console=self._console,
            )
            self._logger.debug("Created Live display")
            return FlextResult[Live].ok(live)
        except Exception as e:
            error_msg = f"Failed to create Live display: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Live].fail(error_msg)

    # =========================================================================
    # SPINNERS AND STATUS
    # =========================================================================

    def create_spinner(
        self,
        spinner_name: str = "dots",
        text: str = "",
        style: str = "cyan",
    ) -> FlextResult[Spinner]:
        """Create Rich spinner.

        Args:
            spinner_name: Spinner type (dots, line, arc, etc.)
            text: Spinner text
            style: Spinner style

        Returns:
            FlextResult containing Rich Spinner

        Example:
            >>> formatters = FlextCliFormatters()
            >>> spinner_result = formatters.create_spinner(
            ...     spinner_name="dots", text="Loading..."
            ... )

        """
        try:
            spinner = Spinner(spinner_name, text=text, style=style)
            self._logger.debug("Created spinner", extra={"spinner_type": spinner_name})
            return FlextResult[Spinner].ok(spinner)
        except Exception as e:
            error_msg = f"Failed to create spinner: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Spinner].fail(error_msg)

    def create_status(
        self,
        status: str,
        spinner: str = "dots",
        spinner_style: str = "cyan",
    ) -> FlextResult[Status]:
        """Create Rich status with spinner.

        Args:
            status: Status message
            spinner: Spinner type
            spinner_style: Spinner style

        Returns:
            FlextResult containing Rich Status

        Example:
            >>> formatters = FlextCliFormatters()
            >>> status_result = formatters.create_status("Processing...")
            >>> if status_result.is_success:
            ...     with status_result.unwrap() as status:
            ...         # Do work
            ...         status.update("Almost done...")

        """
        try:
            status_obj = Status(
                status,
                spinner=spinner,
                spinner_style=spinner_style,
                console=self._console,
            )
            self._logger.debug("Created status", extra={"status_message": status})
            return FlextResult[Status].ok(status_obj)
        except Exception as e:
            error_msg = f"Failed to create status: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Status].fail(error_msg)

    # =========================================================================
    # PROGRESS BARS
    # =========================================================================

    def create_progress(
        self,
        *columns: str
        | BarColumn
        | TaskProgressColumn
        | TextColumn
        | TimeRemainingColumn
        | SpinnerColumn,
        transient: bool = False,
        expand: bool = False,
    ) -> FlextResult[Progress]:
        """Create Rich progress bar.

        Args:
            *columns: Progress columns to display
            transient: Remove progress when done
            expand: Expand to full width

        Returns:
            FlextResult containing Rich Progress

        Example:
            >>> formatters = FlextCliFormatters()
            >>> progress_result = formatters.create_progress()
            >>> if progress_result.is_success:
            ...     progress = progress_result.unwrap()
            ...     with progress:
            ...         task = progress.add_task("Processing", total=100)
            ...         for i in range(100):
            ...             progress.update(task, advance=1)

        """
        try:
            # Default columns if none provided
            if not columns:
                columns = (
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    TimeRemainingColumn(),
                )

            progress = Progress(
                *columns,
                transient=transient,
                expand=expand,
                console=self._console,
            )
            self._logger.debug("Created progress bar")
            return FlextResult[Progress].ok(progress)
        except Exception as e:
            error_msg = f"Failed to create progress bar: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Progress].fail(error_msg)

    # =========================================================================
    # MARKDOWN RENDERING
    # =========================================================================

    def render_markdown(
        self,
        markdown_text: str,
        code_theme: str = "monokai",
        inline_code_lexer: str | None = None,
    ) -> FlextResult[Markdown]:
        r"""Render markdown with Rich.

        Args:
            markdown_text: Markdown content
            code_theme: Code block theme
            inline_code_lexer: Lexer for inline code

        Returns:
            FlextResult containing Rich Markdown

        Example:
            >>> formatters = FlextCliFormatters()
            >>> md_result = formatters.render_markdown("# Title\\n\\n**Bold** text")
            >>> if md_result.is_success:
            ...     console.print(md_result.unwrap())

        """
        try:
            markdown = Markdown(
                markdown_text,
                code_theme=code_theme,
                inline_code_lexer=inline_code_lexer,
            )
            self._logger.debug("Rendered markdown")
            return FlextResult[Markdown].ok(markdown)
        except Exception as e:
            error_msg = f"Failed to render markdown: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Markdown].fail(error_msg)

    def display_markdown(
        self,
        markdown_text: str,
        **kwargs: object,
    ) -> FlextResult[None]:
        """Render and display markdown in one operation.

        Args:
            markdown_text: Markdown content
            **kwargs: Additional markdown options

        Returns:
            FlextResult[None]

        """
        # Type narrowing for markdown options
        code_theme = kwargs.get("code_theme", "monokai")
        inline_code_lexer = kwargs.get("inline_code_lexer")

        # Ensure proper types
        code_theme_str: str = str(code_theme) if code_theme is not None else "monokai"
        inline_code_lexer_str: str | None = (
            str(inline_code_lexer) if inline_code_lexer is not None else None
        )

        md_result = self.render_markdown(
            markdown_text,
            code_theme=code_theme_str,
            inline_code_lexer=inline_code_lexer_str,
        )
        if md_result.is_failure:
            return FlextResult[None].fail(md_result.error)

        return self.print(md_result.unwrap())

    # =========================================================================
    # SYNTAX HIGHLIGHTING
    # =========================================================================

    def highlight_code(
        self,
        code: str,
        language: str = "python",
        theme: str = "monokai",
        *,
        line_numbers: bool = False,
        word_wrap: bool = False,
        line_range: tuple[int, int] | None = None,
        highlight_lines: set[int] | None = None,
        code_width: int | None = None,
    ) -> FlextResult[Syntax]:
        """Syntax highlight code with Rich.

        Args:
            code: Code to highlight
            language: Programming language
            theme: Color theme
            line_numbers: Show line numbers
            word_wrap: Enable word wrapping
            line_range: Range of lines to display
            highlight_lines: Lines to highlight
            code_width: Fixed width

        Returns:
            FlextResult containing Rich Syntax

        Example:
            >>> formatters = FlextCliFormatters()
            >>> code_result = formatters.highlight_code(
            ...     "def hello(): print('hi')", language="python", line_numbers=True
            ... )

        """
        try:
            syntax = Syntax(
                code,
                language,
                theme=theme,
                line_numbers=line_numbers,
                word_wrap=word_wrap,
                line_range=line_range,
                highlight_lines=highlight_lines,
                code_width=code_width,
            )
            self._logger.debug(
                "Created syntax highlighting", extra={"language": language}
            )
            return FlextResult[Syntax].ok(syntax)
        except Exception as e:
            error_msg = f"Failed to create syntax highlighting: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Syntax].fail(error_msg)

    def display_code(
        self,
        code: str,
        language: str = "python",
        **kwargs: object,
    ) -> FlextResult[None]:
        """Highlight and display code in one operation.

        Args:
            code: Code to display
            language: Programming language
            **kwargs: Additional syntax options

        Returns:
            FlextResult[None]

        """
        # Type narrowing for syntax highlighting options
        theme = kwargs.get("theme", "monokai")
        line_numbers = kwargs.get("line_numbers", False)
        word_wrap = kwargs.get("word_wrap", False)
        line_range = kwargs.get("line_range")
        highlight_lines = kwargs.get("highlight_lines")
        code_width = kwargs.get("code_width")

        # Ensure proper types
        theme_str: str = str(theme) if theme is not None else "monokai"
        line_numbers_bool: bool = (
            bool(line_numbers) if isinstance(line_numbers, (bool, int)) else False
        )
        word_wrap_bool: bool = (
            bool(word_wrap) if isinstance(word_wrap, (bool, int)) else False
        )
        line_range_tuple: tuple[int, int] | None = (
            line_range if isinstance(line_range, tuple) else None
        )
        highlight_lines_set: set[int] | None = (
            highlight_lines if isinstance(highlight_lines, set) else None
        )
        code_width_int: int | None = (
            int(code_width)
            if isinstance(code_width, (int, str)) and code_width
            else None
        )

        syntax_result = self.highlight_code(
            code,
            language,
            theme=theme_str,
            line_numbers=line_numbers_bool,
            word_wrap=word_wrap_bool,
            line_range=line_range_tuple,
            highlight_lines=highlight_lines_set,
            code_width=code_width_int,
        )
        if syntax_result.is_failure:
            return FlextResult[None].fail(syntax_result.error)

        return self.print(syntax_result.unwrap())

    # =========================================================================
    # RULES AND DIVIDERS
    # =========================================================================

    def create_rule(
        self,
        title: str = "",
        characters: str = "─",
        style: str | Style = "rule.line",
        align: Literal["left", "center", "right"] = "center",
    ) -> FlextResult[Rule]:
        """Create Rich rule/divider.

        Args:
            title: Rule title
            characters: Characters to use for line
            style: Line style
            align: Title alignment (left, center, right)

        Returns:
            FlextResult containing Rich Rule

        Example:
            >>> formatters = FlextCliFormatters()
            >>> rule_result = formatters.create_rule(title="Section", style="blue")

        """
        try:
            rule = Rule(
                title=title,
                characters=characters,
                style=style,
                align=align,
            )
            self._logger.debug("Created rule", extra={"rule_title": title})
            return FlextResult[Rule].ok(rule)
        except Exception as e:
            error_msg = f"Failed to create rule: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Rule].fail(error_msg)

    def display_rule(
        self,
        title: str = "",
        **kwargs: object,
    ) -> FlextResult[None]:
        """Create and display rule in one operation.

        Args:
            title: Rule title
            **kwargs: Additional rule options

        Returns:
            FlextResult[None]

        """
        # Type narrowing for rule options
        characters = kwargs.get("characters", "─")
        style = kwargs.get("style", "rule.line")
        align = kwargs.get("align", "center")

        # Ensure proper types
        characters_str: str = str(characters) if characters is not None else "─"
        style_obj: str | Style = (
            style if isinstance(style, (str, Style)) else "rule.line"
        )
        align_str: Literal["left", "center", "right"] = (
            align
            if isinstance(align, str) and align in {"left", "center", "right"}
            else "center"
        )

        rule_result = self.create_rule(
            title, characters=characters_str, style=style_obj, align=align_str
        )
        if rule_result.is_failure:
            return FlextResult[None].fail(rule_result.error)

        return self.print(rule_result.unwrap())

    # =========================================================================
    # TEXT STYLING AND ALIGNMENT
    # =========================================================================

    def create_text(
        self,
        text: str = "",
        style: str | Style | None = None,
        justify: str | None = None,
        overflow: str | None = None,
        *,
        no_wrap: bool | None = None,
        end: str = "\n",
    ) -> FlextResult[Text]:
        """Create Rich Text object with styling.

        Args:
            text: Text content
            style: Text style
            justify: Text justification
            overflow: Overflow handling
            no_wrap: Disable wrapping
            end: End character

        Returns:
            FlextResult containing Rich Text

        """
        try:
            # Convert justify and overflow to proper Rich types
            justify_method: JustifyMethod | None = (
                justify
                if isinstance(justify, str)
                and justify in {"default", "left", "center", "right", "full"}
                else None
            )
            overflow_method: OverflowMethod | None = (
                overflow
                if isinstance(overflow, str)
                and overflow in {"fold", "crop", "ellipsis", "ignore"}
                else None
            )

            text_obj = Text(
                text,
                style=style if style is not None else "",
                justify=justify_method,
                overflow=overflow_method,
                no_wrap=no_wrap,
                end=end,
            )
            self._logger.debug("Created Rich text")
            return FlextResult[Text].ok(text_obj)
        except Exception as e:
            error_msg = f"Failed to create text: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Text].fail(error_msg)

    def align_text(
        self,
        content: str | Text,
        align: str = "center",
        vertical: str = "top",
        width: int | None = None,
        height: int | None = None,
    ) -> FlextResult[Align]:
        """Align content.

        Args:
            content: Content to align
            align: Horizontal alignment (left, center, right)
            vertical: Vertical alignment (top, middle, bottom)
            width: Fixed width
            height: Fixed height

        Returns:
            FlextResult containing Rich Align

        """
        try:
            # Convert align and vertical to proper Rich types
            align_method: AlignMethod = (
                align
                if isinstance(align, str) and align in {"left", "center", "right"}
                else "center"
            )
            vertical_method: VerticalAlignMethod | None = (
                vertical
                if isinstance(vertical, str) and vertical in {"top", "middle", "bottom"}
                else None
            )

            aligned = Align(
                content,
                align=align_method,
                vertical=vertical_method,
                width=width,
                height=height,
            )
            self._logger.debug("Created alignment")
            return FlextResult[Align].ok(aligned)
        except Exception as e:
            error_msg = f"Failed to create alignment: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Align].fail(error_msg)

    # =========================================================================
    # TABLES AND TREES
    # =========================================================================

    def create_table(
        self,
        title: str | None = None,
        caption: str | None = None,
        *,
        show_header: bool = True,
        show_lines: bool = False,
        show_edge: bool = True,
        expand: bool = False,
        padding: tuple[int, int] = (0, 1),
    ) -> FlextResult[RichTable]:
        """Create Rich table.

        Args:
            title: Table title
            caption: Table caption
            show_header: Show header row
            show_lines: Show lines between rows
            show_edge: Show edge borders
            expand: Expand to full width
            padding: Cell padding

        Returns:
            FlextResult containing Rich Table

        Example:
            >>> formatters = FlextCliFormatters()
            >>> table_result = formatters.create_table(title="Data")
            >>> if table_result.is_success:
            ...     table = table_result.unwrap()
            ...     table.add_column("Name")
            ...     table.add_column("Value")
            ...     table.add_row("Item 1", "100")

        """
        try:
            table = RichTable(
                title=title,
                caption=caption,
                show_header=show_header,
                show_lines=show_lines,
                show_edge=show_edge,
                expand=expand,
                padding=padding,
            )
            self._logger.debug("Created Rich table", extra={"table_title": title})
            return FlextResult[RichTable].ok(table)
        except Exception as e:
            error_msg = f"Failed to create table: {e}"
            self._logger.exception(error_msg)
            return FlextResult[RichTable].fail(error_msg)

    def create_tree(
        self,
        label: str,
        guide_style: str = "tree.line",
    ) -> FlextResult[Tree]:
        """Create Rich tree structure.

        Args:
            label: Tree root label
            guide_style: Guide line style

        Returns:
            FlextResult containing Rich Tree

        Example:
            >>> formatters = FlextCliFormatters()
            >>> tree_result = formatters.create_tree("Root")
            >>> if tree_result.is_success:
            ...     tree = tree_result.unwrap()
            ...     branch = tree.add("Branch")
            ...     branch.add("Leaf")

        """
        try:
            tree = Tree(label, guide_style=guide_style)
            self._logger.debug("Created tree", extra={"tree_label": label})
            return FlextResult[Tree].ok(tree)
        except Exception as e:
            error_msg = f"Failed to create tree: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Tree].fail(error_msg)

    # =========================================================================
    # TRACEBACK FORMATTING
    # =========================================================================

    def format_exception(
        self,
        width: int | None = None,
        extra_lines: int = 3,
        theme: str | None = None,
        *,
        show_locals: bool = False,
        word_wrap: bool = False,
        suppress: Iterable[str | type] = (),
    ) -> FlextResult[Traceback]:
        """Format exception with Rich traceback.

        Args:
            show_locals: Show local variables
            width: Fixed width
            extra_lines: Extra lines of context
            theme: Color theme
            word_wrap: Enable word wrapping
            suppress: Modules/exceptions to suppress

        Returns:
            FlextResult containing Rich Traceback

        Example:
            >>> formatters = FlextCliFormatters()
            >>> try:
            ...     raise ValueError("Error")
            ... except Exception:
            ...     tb_result = formatters.format_exception(show_locals=True)
            ...     if tb_result.is_success:
            ...         console.print(tb_result.unwrap())

        """
        try:
            traceback = Traceback(
                show_locals=show_locals,
                width=width,
                extra_lines=extra_lines,
                theme=theme,
                word_wrap=word_wrap,
                suppress=[
                    item for item in suppress if isinstance(item, (str, ModuleType))
                ]
                if isinstance(suppress, Iterable)
                else (),
            )
            self._logger.debug("Created Rich traceback")
            return FlextResult[Traceback].ok(traceback)
        except Exception as e:
            error_msg = f"Failed to create traceback: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Traceback].fail(error_msg)

    # =========================================================================
    # INTERACTIVE FEATURES
    # =========================================================================

    def prompt(
        self,
        prompt_text: str,
        default: str = "",
        *,
        password: bool = False,
        show_default: bool = True,
    ) -> FlextResult[str]:
        """Prompt user for input with Rich styling.

        Args:
            prompt_text: Prompt message
            default: Default value
            password: Hide input for passwords
            show_default: Show default value in prompt

        Returns:
            FlextResult containing user input string

        Example:
            >>> formatters = FlextCliFormatters()
            >>> name_result = formatters.prompt("Enter your name", default="User")
            >>> if name_result.is_success:
            ...     print(f"Hello, {name_result.unwrap()}!")

        """
        try:
            value = Prompt.ask(
                prompt_text,
                default=default,
                password=password,
                show_default=show_default,
                console=self._console,
            )
            self._logger.debug(
                "Prompted user for input", extra={"prompt_msg": prompt_text}
            )
            return FlextResult[str].ok(str(value))
        except Exception as e:
            error_msg = f"Failed to prompt user: {e}"
            self._logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def confirm(
        self,
        question: str,
        *,
        default: bool = False,
        show_default: bool = True,
    ) -> FlextResult[bool]:
        """Ask user for yes/no confirmation with Rich styling.

        Args:
            question: Confirmation question
            default: Default answer
            show_default: Show default in prompt

        Returns:
            FlextResult containing boolean confirmation

        Example:
            >>> formatters = FlextCliFormatters()
            >>> confirm_result = formatters.confirm("Continue?", default=True)
            >>> if confirm_result.is_success and confirm_result.unwrap():
            ...     print("Continuing...")

        """
        try:
            result = Confirm.ask(
                question,
                default=default,
                show_default=show_default,
                console=self._console,
            )
            self._logger.debug(
                "Asked user for confirmation", extra={"confirm_question": question}
            )
            return FlextResult[bool].ok(result)
        except Exception as e:
            error_msg = f"Failed to confirm: {e}"
            self._logger.exception(error_msg)
            return FlextResult[bool].fail(error_msg)

    def prompt_choice(
        self,
        prompt_text: str,
        choices: FlextTypes.StringList,
        default: str | None = None,
    ) -> FlextResult[str]:
        """Prompt user to select from a list of choices.

        Args:
            prompt_text: Prompt message
            choices: List of available choices
            default: Default choice

        Returns:
            FlextResult containing selected choice

        Example:
            >>> formatters = FlextCliFormatters()
            >>> choice_result = formatters.prompt_choice(
            ...     "Select format", choices=["json", "yaml", "csv"], default="json"
            ... )

        """
        try:
            value = Prompt.ask(
                prompt_text,
                choices=choices,
                default=default,
                console=self._console,
            )
            self._logger.debug(
                "Prompted user for choice",
                extra={"prompt_msg": prompt_text, "choice_count": len(choices)},
            )
            return FlextResult[str].ok(str(value))
        except Exception as e:
            error_msg = f"Failed to prompt for choice: {e}"
            self._logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def prompt_int(
        self,
        prompt_text: str,
        default: int | None = None,
    ) -> FlextResult[int]:
        """Prompt user for integer input.

        Args:
            prompt_text: Prompt message
            default: Default value

        Returns:
            FlextResult containing integer input

        Example:
            >>> formatters = FlextCliFormatters()
            >>> age_result = formatters.prompt_int("Enter age", default=18)

        """
        try:
            value = IntPrompt.ask(
                prompt_text,
                default=default,
                console=self._console,
            )
            if value is None:
                return FlextResult[int].fail("No integer value provided")
            self._logger.debug(
                "Prompted user for integer", extra={"prompt_msg": prompt_text}
            )
            return FlextResult[int].ok(value)
        except Exception as e:
            error_msg = f"Failed to prompt for integer: {e}"
            self._logger.exception(error_msg)
            return FlextResult[int].fail(error_msg)

    def create_live_display_with_renderable(
        self,
        renderable: RenderableType,
        refresh_per_second: float = 4,
        *,
        transient: bool = False,
    ) -> FlextResult[Live]:
        """Create Rich Live display with initial renderable content.

        Args:
            renderable: Initial renderable content
            refresh_per_second: Refresh rate
            transient: Clear display when exiting

        Returns:
            FlextResult containing Live display context manager

        Example:
            >>> formatters = FlextCliFormatters()
            >>> table_result = formatters.create_table(title="Live Data")
            >>> if table_result.is_success:
            ...     table = table_result.unwrap()
            ...     live_result = formatters.create_live_display_with_renderable(table)
            ...     if live_result.is_success:
            ...         with live_result.unwrap() as live:
            ...             # Update table in real-time
            ...             pass

        """
        try:
            live = Live(
                renderable,
                refresh_per_second=refresh_per_second,
                transient=transient,
                console=self._console,
            )
            self._logger.debug(
                "Created live display", extra={"refresh_rate": refresh_per_second}
            )
            return FlextResult[Live].ok(live)
        except Exception as e:
            error_msg = f"Failed to create live display: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Live].fail(error_msg)

    # =========================================================================
    # RENDERING METHODS - Convert Rich objects to strings
    # =========================================================================

    def render_table_to_string(
        self,
        table: RichTable,
        width: int | None = None,
    ) -> FlextResult[str]:
        """Render Rich table to string using console.

        Args:
            table: Rich table object to render
            width: Optional console width

        Returns:
            FlextResult[str]: Table as string or error

        Example:
            >>> formatters = FlextCliFormatters()
            >>> table_result = formatters.create_table(title="Test")
            >>> if table_result.is_success:
            ...     string_result = formatters.render_table_to_string(
            ...         table_result.unwrap(), width=80
            ...     )

        """
        try:
            string_io = StringIO()
            temp_console = Console(
                file=string_io, width=width or 80, force_terminal=False
            )
            temp_console.print(table)
            return FlextResult[str].ok(string_io.getvalue())
        except Exception as e:
            error_msg = f"Failed to render table to string: {e}"
            self._logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def render_tree_to_string(
        self,
        tree: Tree,
        width: int | None = None,
    ) -> FlextResult[str]:
        """Render Rich tree to string using console.

        Args:
            tree: Rich tree object to render
            width: Optional console width

        Returns:
            FlextResult[str]: Tree as string or error

        Example:
            >>> formatters = FlextCliFormatters()
            >>> tree_result = formatters.create_tree("Root")
            >>> if tree_result.is_success:
            ...     string_result = formatters.render_tree_to_string(
            ...         tree_result.unwrap(), width=100
            ...     )

        """
        try:
            string_io = StringIO()
            temp_console = Console(
                file=string_io,
                width=width or self._console.size.width,
                force_terminal=False,
            )
            temp_console.print(tree)
            return FlextResult[str].ok(string_io.getvalue())
        except Exception as e:
            error_msg = f"Failed to render tree to string: {e}"
            self._logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def clear(self) -> FlextResult[None]:
        """Clear the console.

        Returns:
            FlextResult[None]

        """
        try:
            self._console.clear()
            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Failed to clear console: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    # Attribute declarations - override FlextService optional types
    # These are guaranteed initialized in __init__
    _logger: FlextLogger
    _container: FlextContainer

    def execute(self) -> FlextResult[object]:
        """Execute Rich formatters layer operations.

        Returns:
            FlextResult[None]

        """
        return FlextResult[None].ok(None)


__all__ = [
    "FlextCliFormatters",
]
