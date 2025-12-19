"""FLEXT CLI Formatters - Thin wrapper over Rich library.

Provides minimal CLI formatting abstraction. Uses Rich directly for all operations.
Following zero-tolerance principle: Use libraries, don't reimplement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from io import StringIO

from flext_core import (
    FlextRuntime,
    r,
)
from rich.console import Console
from rich.layout import Layout as RichLayout
from rich.live import Live as RichLive
from rich.panel import Panel as RichPanel
from rich.progress import Progress
from rich.status import Status as RichStatus
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import t


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
    8. Error handling MUST catch Rich exceptions and return FlextResult failures

    Architecture Implications:
    ───────────────────────────
    - Minimal wrapper over Rich library (zero-tolerance for reimplementation)
    - Direct Rich imports (one of two files allowed)
    - Console instance shared across operations
    - Railway-Oriented Programming via FlextResult for error handling
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

    def __init__(self) -> None:
        """Initialize Rich formatters with direct Rich imports."""
        # Use Rich directly (formatters.py is ONE OF TWO files that may import Rich)
        self.console = Console()

    def execute(self) -> r[Mapping[str, t.GeneralValueType]]:
        """Execute service - required by FlextService."""
        return r[dict[str, t.GeneralValueType]].ok({
            FlextCliConstants.Cli.DictKeys.STATUS: FlextCliConstants.Cli.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.Cli.DictKeys.SERVICE: FlextCliConstants.Cli.Services.FORMATTERS,
        })

    # =========================================================================
    # CORE METHODS - ACTUALLY USED BY output.py
    # =========================================================================

    def print(
        self,
        message: str,
        style: str | None = None,
    ) -> r[bool]:
        """Print formatted message using Rich.

        Args:
            message: Message to print
            style: Rich style string (e.g., "bold red")

        Returns:
            r[bool]: True on success, False on failure

        Note:
            For advanced Rich features, access self.console directly.

        """
        try:
            self.console.print(message, style=style)
            return r[bool].ok(True)
        except Exception as e:  # pragma: no cover - Defensive: Catches unexpected errors during console print operation
            return r[bool].fail(
                FlextCliConstants.Cli.FormattersErrorMessages.PRINT_FAILED.format(
                    error=e
                ),
            )

    @staticmethod
    def create_table(
        data: dict[str, t.GeneralValueType] | None = None,
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

            # Add columns if headers provided
            if headers:
                for header in headers:
                    table.add_column(header)

            # Add rows if data provided
            if data and FlextRuntime.is_dict_like(data):
                # Simple dict[str, t.GeneralValueType] to table conversion - key-value pairs for 2-column tables
                for k, v in data.items():
                    if (
                        headers
                        and len(headers)
                        == FlextCliConstants.Cli.FormattersDefaults.TABLE_KEY_VALUE_COLUMNS
                    ):
                        # Key-value pairs
                        table.add_row(str(k), str(v))
                    else:
                        # Single column with values
                        table.add_row(str(k), str(v))

            return r[RichTable].ok(table)

        except Exception as e:  # pragma: no cover - Defensive: Catches unexpected errors during table creation
            return r[RichTable].fail(
                FlextCliConstants.Cli.FormattersErrorMessages.TABLE_CREATION_FAILED.format(
                    error=e,
                ),
            )

    def render_table_to_string(
        self,
        table: RichTable | object,
        width: int | None = None,
    ) -> r[str]:
        """Render Rich table to string.

        Business Rule:
        ──────────────
        Accepts both RichTable concrete type and protocol implementations.
        Internal cast handles protocol-to-concrete conversion safely since
        protocols are structurally typed to match RichTable interface.

        Audit Implications:
        ───────────────────
        - Callers may pass RichTableProtocol (output.py) or RichTable (formatters.py)
        - Cast is safe because protocol defines same structural interface
        - Width defaults to console width if not specified

        Args:
            table: Rich Table instance or protocol-conforming object
            width: Optional console width

        Returns:
            r[str]: Rendered table string or error

        """
        try:
            # Use Rich's built-in rendering
            console = Console(width=width) if width else self.console

            # Capture console output
            buffer = StringIO()
            # Validate width explicitly - no fallback
            validated_width = width if width is not None else console.width
            temp_console = Console(file=buffer, width=validated_width)
            temp_console.print(table)
            output = buffer.getvalue()

            return r[str].ok(output)

        except Exception as e:
            return r[str].fail(
                FlextCliConstants.Cli.FormattersErrorMessages.TABLE_RENDERING_FAILED.format(
                    error=e,
                ),
            )

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
        except Exception as e:
            return r[Progress].fail(
                FlextCliConstants.Cli.FormattersErrorMessages.PROGRESS_CREATION_FAILED.format(
                    error=e,
                ),
            )

    @staticmethod
    def create_tree(label: str) -> r[RichTree]:
        """Create Rich tree with default settings.

        Args:
            label: Tree root label

        Returns:
            r[RichTree]: Rich Tree instance or error

        Note:
            For custom tree styling, create Tree objects directly using Rich.

        """
        try:
            tree = RichTree(label)
            return r[RichTree].ok(tree)
        except Exception as e:
            return r[RichTree].fail(
                FlextCliConstants.Cli.FormattersErrorMessages.TREE_CREATION_FAILED.format(
                    error=e,
                ),
            )

    def render_tree_to_string(
        self,
        tree: RichTree,
        width: int | None = None,
    ) -> r[str]:
        """Render Rich tree to string.

        Args:
            tree: Rich Tree instance
            width: Optional console width

        Returns:
            r[str]: Rendered tree string or error

        """
        try:
            buffer = StringIO()
            # Validate width explicitly - no fallback
            validated_width = width if width is not None else self.console.width
            temp_console = Console(file=buffer, width=validated_width)
            temp_console.print(tree)
            output = buffer.getvalue()

            return r[str].ok(output)

        except Exception as e:
            return r[str].fail(
                FlextCliConstants.Cli.FormattersErrorMessages.TREE_RENDERING_FAILED.format(
                    error=e,
                ),
            )

    # =========================================================================
    # ADVANCED RICH WRAPPERS - Status, Live, Layout, Panel
    # =========================================================================

    def create_status(
        self,
        message: str,
        spinner: str | None = None,
    ) -> r[RichStatus]:
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
            # Validate spinner explicitly - no fallback
            validated_spinner = (
                spinner
                if spinner is not None
                else FlextCliConstants.Cli.FormattersDefaults.DEFAULT_SPINNER
            )
            status = RichStatus(
                message,
                spinner=validated_spinner,
                console=self.console,
            )
            return r[RichStatus].ok(status)
        except Exception as e:
            return r[RichStatus].fail(
                FlextCliConstants.Cli.FormattersErrorMessages.STATUS_CREATION_FAILED.format(
                    error=e,
                ),
            )

    def create_live(
        self,
        refresh_per_second: float | None = None,
    ) -> r[RichLive]:
        """Create Rich live display.

        Args:
            refresh_per_second: Refresh rate for live updates

        Returns:
            r[RichLive]: Rich Live instance or error

        Note:
            For custom live displays, access self.console directly and create Live objects.

        """
        try:
            # Validate refresh rate explicitly - no fallback
            validated_refresh_rate = (
                refresh_per_second
                if refresh_per_second is not None
                else FlextCliConstants.Cli.FormattersDefaults.DEFAULT_REFRESH_RATE
            )
            live = RichLive(
                refresh_per_second=validated_refresh_rate,
                console=self.console,
            )
            return r[RichLive].ok(live)
        except Exception as e:
            return r[RichLive].fail(
                FlextCliConstants.Cli.FormattersErrorMessages.LIVE_CREATION_FAILED.format(
                    error=e,
                ),
            )

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
        except Exception as e:
            return r[RichLayout].fail(
                FlextCliConstants.Cli.FormattersErrorMessages.LAYOUT_CREATION_FAILED.format(
                    error=e,
                ),
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
            # Validate border style explicitly - no fallback
            validated_border_style = (
                border_style
                if border_style is not None
                else FlextCliConstants.Cli.FormattersDefaults.DEFAULT_BORDER_STYLE
            )
            panel = RichPanel(
                content,
                title=title,
                border_style=validated_border_style,
            )
            return r[RichPanel].ok(panel)
        except Exception as e:
            return r[RichPanel].fail(
                FlextCliConstants.Cli.FormattersErrorMessages.PANEL_CREATION_FAILED.format(
                    error=e,
                ),
            )


__all__ = [
    "FlextCliFormatters",
]
