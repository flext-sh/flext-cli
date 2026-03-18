"""FLEXT CLI Formatters - Thin wrapper over Rich library.

Provides minimal CLI formatting abstraction. Uses Rich directly for all operations.
Following zero-tolerance principle: Use libraries, don't reimplement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from io import StringIO
from typing import Literal, Self, overload, override

from flext_core import FlextLogger, r, u
from rich.console import Console
from rich.errors import ConsoleError, LiveError, NotRenderableError, StyleError
from rich.layout import Layout as RichLayout
from rich.live import Live as RichLive
from rich.panel import Panel as RichPanel
from rich.progress import Progress
from rich.status import Status as RichStatus
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree

from flext_cli import c, p, t

_logger = FlextLogger(__name__)


class FlextCliFormatters:
    """Thin Rich formatters facade - delegates to Rich library directly.

    Business Rules:
    ───────────────
    1. This is ONE OF TWO files allowed to import Rich directly
    2. All formatting operations MUST delegate to Rich library (no reimplementation)
    3. Console output MUST respect no_color configuration flag
    4. Table creation MUST handle empty data gracefully
    5. All operations MUST return r[T] for error handling
    6. Rich Console MUST be initialized once per instance (singleton pattern)
    7. Formatting operations MUST not modify input data (immutable)
    8. Error handling MUST catch Rich exceptions and return r failures

    Architecture Implications:
    ───────────────────────────
    - Minimal wrapper over Rich library (zero-tolerance for reimplementation)
    - Direct Rich imports (one of two files allowed)
    - Console instance shared across operations
    - Railway-Oriented Programming via r for error handling
    - Static methods for table creation (no instance state needed)

    Audit Implications:
    ───────────────────
    - Formatting operations SHOULD be logged with format type and data size
    - Console output MUST respect no_color flag for log compatibility
    - Rich exceptions MUST be logged with full context (no sensitive data)
    - Table creation MUST validate data structure before formatting

    ZERO TOLERANCE: Use Rich directly, minimal wrapper only for CLI abstraction.
    Removed 24 unused methods - keep ONLY what output.py actually uses.
    """

    class Tree:
        """Wrapper around Rich Tree; add() returns None by default (optional return via overload).

        Use add(label) for side-effect only; add(label, return_child=True) to chain.
        """

        def __init__(self, tree: RichTree) -> None:
            """Wrap a Rich Tree instance for side-effect-safe usage."""
            self._tree: RichTree = tree

        @overload
        def add(self, label: str) -> None: ...

        @overload
        def add(self, label: str, *, return_child: Literal[True]) -> Self: ...

        def add(
            self,
            label: str,
            *,
            return_child: bool = False,
        ) -> FlextCliFormatters.Tree | None:
            """Add a child node; return the wrapped child only when *return_child* is set."""
            child = self._tree.add(label)
            return FlextCliFormatters.Tree(child) if return_child else None

        @override
        def __str__(self) -> str:
            return str(self._tree)

        @property
        def tree(self) -> RichTree:
            """Expose inner Rich Tree for rendering or advanced use."""
            return self._tree

    def __init__(self) -> None:
        """Initialize Rich formatters with direct Rich imports."""
        super().__init__()
        self.console: Console = Console()

    @staticmethod
    def create_layout() -> r[RichLayout]:
        """Create Rich layout with default settings.

        Returns:
            r[RichLayout]: Rich Layout instance or error

        Note:
            For custom layouts (named regions, sizes), create Layout objects
            directly using Rich.

        """
        try:
            layout = RichLayout()
            return r[RichLayout].ok(layout)
        except ConsoleError as exc:
            _logger.warning("rich_layout_creation_failed", error=str(exc))
            return r[RichLayout].fail(
                c.Cli.FormattersErrorMessages.LAYOUT_CREATION_FAILED.format(error=exc),
            )

    @staticmethod
    def create_panel(
        content: str,
        title: str | None = None,
        border_style: str | None = None,
    ) -> r[RichPanel]:
        """Create Rich panel with text content.

        Args:
            content: Panel content (text)
            title: Optional panel title
            border_style: Border style (e.g., "blue", "green", "red")

        Returns:
            r[RichPanel]: Rich Panel instance or error

        Note:
            For panels with complex content (Rich renderables), create Panel objects
            directly using Rich.

        """
        try:
            validated_border_style = (
                border_style
                if border_style is not None
                else c.Cli.FormattersDefaults.DEFAULT_BORDER_STYLE
            )
            panel = RichPanel(content, title=title, border_style=validated_border_style)
            return r[RichPanel].ok(panel)
        except (ConsoleError, StyleError) as exc:
            _logger.warning(
                "rich_panel_creation_fallback",
                error=str(exc),
                title=title or "",
            )
            return r[RichPanel].ok(RichPanel(content))

    @staticmethod
    def create_progress() -> r[Progress]:
        """Create Rich progress bar with default settings.

        Returns:
            r[Progress]: Rich Progress instance or error

        Note:
            For custom progress bars (columns, styles), create Progress objects
            directly using Rich.

        """
        try:
            progress = Progress()
            return r[Progress].ok(progress)
        except ConsoleError as exc:
            _logger.warning("rich_progress_creation_failed", error=str(exc))
            return r[Progress].fail(
                c.Cli.FormattersErrorMessages.PROGRESS_CREATION_FAILED.format(
                    error=exc
                ),
            )

    @staticmethod
    def create_table(
        data: Mapping[str, t.Cli.JsonValue] | None = None,
        headers: list[str] | None = None,
        title: str | None = None,
    ) -> r[RichTable]:
        """Create Rich table with basic formatting.

        Args:
            data: Optional data dictionary for table
            headers: Optional column headers
            title: Optional table title

        Returns:
            r[RichTable]: Rich Table instance or error

        Note:
            For advanced Rich table features (box styles, padding, etc),
            access self.console directly and create Rich tables.

        """
        try:
            table = RichTable(title=title)
            if headers:
                for header in headers:
                    table.add_column(header)
            if data and u.is_dict_like(data):
                for k, v in data.items():
                    if (
                        headers
                        and len(headers)
                        == c.Cli.FormattersDefaults.TABLE_KEY_VALUE_COLUMNS
                    ):
                        table.add_row(str(k), str(v))
                    else:
                        table.add_row(str(k), str(v))
            return r[RichTable].ok(table)
        except (ConsoleError, StyleError) as exc:
            _logger.warning(
                "rich_table_creation_fallback",
                error=str(exc),
                title=title or "",
            )
            return r[RichTable].ok(RichTable())

    @staticmethod
    def create_tree(label: str) -> r[FlextCliFormatters.Tree]:
        """Create Rich tree wrapped for optional return use (add() returns None by default).

        Args:
            label: Tree root label

        Returns:
            r[FlextCliFormatters.Tree]: Wrapper instance or error

        Note:
            Use tree.add(label) for side-effect; tree.add(label, return_child=True) to chain.

        """
        try:
            tree = RichTree(label)
            return r[FlextCliFormatters.Tree].ok(FlextCliFormatters.Tree(tree))
        except ConsoleError as exc:
            _logger.warning("rich_tree_creation_failed", error=str(exc), label=label)
            return r[FlextCliFormatters.Tree].fail(
                c.Cli.FormattersErrorMessages.TREE_CREATION_FAILED.format(error=exc),
            )

    def create_live(self, refresh_per_second: float | None = None) -> r[RichLive]:
        """Create Rich live display.

        Args:
            refresh_per_second: Refresh rate for live updates

        Returns:
            r[RichLive]: Rich Live instance or error

        Note:
            For custom live displays, access self.console directly and create Live objects.

        """
        try:
            validated_refresh_rate = (
                refresh_per_second
                if refresh_per_second is not None
                else c.Cli.FormattersDefaults.DEFAULT_REFRESH_RATE
            )
            live = RichLive(refresh_per_second=validated_refresh_rate)
            return r[RichLive].ok(live)
        except (ConsoleError, LiveError) as exc:
            _logger.warning("rich_live_creation_failed", error=str(exc))
            return r[RichLive].fail(
                c.Cli.FormattersErrorMessages.LIVE_CREATION_FAILED.format(error=exc),
            )

    def create_status(self, message: str, spinner: str | None = None) -> r[RichStatus]:
        """Create Rich status spinner.

        Args:
            message: Status message
            spinner: Spinner style (e.g., "dots", "line", "arrow")

        Returns:
            r[RichStatus]: Rich Status instance or error

        Note:
            For custom spinners, access self.console directly and create Status objects.

        """
        try:
            validated_spinner = (
                spinner
                if spinner is not None
                else c.Cli.FormattersDefaults.DEFAULT_SPINNER
            )
            status = RichStatus(message, spinner=validated_spinner)
            return r[RichStatus].ok(status)
        except (ConsoleError, StyleError) as exc:
            _logger.warning(
                "rich_status_creation_failed",
                error=str(exc),
                message=message,
            )
            return r[RichStatus].fail(
                c.Cli.FormattersErrorMessages.STATUS_CREATION_FAILED.format(error=exc),
            )

    def execute(self) -> r[Mapping[str, t.Cli.JsonValue]]:
        """Execute service - required by FlextService."""
        return r[Mapping[str, t.Cli.JsonValue]].ok({
            c.Cli.DictKeys.STATUS: c.Cli.ServiceStatus.OPERATIONAL.value,
            c.Cli.DictKeys.SERVICE: c.Cli.Services.FORMATTERS,
        })

    def print(self, message: str, style: str | None = None) -> None:
        """Print formatted message using Rich.

        Args:
            message: Message to print
            style: Rich style string (e.g., "bold red")

        Note:
            For advanced Rich features, access self.console directly.

        """
        try:
            self.console.print(message, style=style)
        except (ConsoleError, StyleError) as exc:
            _logger.warning(
                "rich_print_fallback",
                error=str(exc),
                message_length=len(message),
            )
            _ = sys.stdout.write(f"{message}\n")
            _ = sys.stdout.flush()

    def render_table_to_string(
        self,
        table: RichTable | p.Cli.Display.RichTable,
        width: int | None = None,
    ) -> r[str]:
        """Render Rich table to string.

        Args:
            table: Rich Table instance or protocol-conforming table
            width: Optional console width

        Returns:
            r[str]: Rendered table string or error

        """
        try:
            console = Console(width=width) if width else self.console
            buffer = StringIO()
            validated_width = width if width is not None else console.width
            temp_console = Console(file=buffer, width=validated_width)
            temp_console.print(table)
            output = buffer.getvalue()
            return r[str].ok(output)
        except (ConsoleError, NotRenderableError) as exc:
            _logger.warning("rich_table_render_fallback", error=str(exc))
            return r[str].ok(str(table))

    def render_tree_to_string(
        self,
        tree: RichTree | FlextCliFormatters.Tree,
        width: int | None = None,
    ) -> r[str]:
        """Render Rich tree to string.

        Args:
            tree: Rich Tree or FlextCliFormatters.Tree instance
            width: Optional console width

        Returns:
            r[str]: Rendered tree string or error

        """
        inner = tree.tree if isinstance(tree, FlextCliFormatters.Tree) else tree
        try:
            buffer = StringIO()
            validated_width = width if width is not None else self.console.width
            temp_console = Console(file=buffer, width=validated_width)
            temp_console.print(inner)
            output = buffer.getvalue()
            return r[str].ok(output)
        except (ConsoleError, NotRenderableError) as exc:
            _logger.warning("rich_tree_render_fallback", error=str(exc))
            return r[str].ok(str(inner))


__all__ = ["FlextCliFormatters"]
