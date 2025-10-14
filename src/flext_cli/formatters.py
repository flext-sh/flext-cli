"""FLEXT CLI Formatters - Thin wrapper over Rich library.

Provides minimal CLI formatting abstraction. Uses Rich directly for all operations.
Following zero-tolerance principle: Use libraries, don't reimplement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from io import StringIO

from flext_core import FlextCore
from rich.console import Console
from rich.layout import Layout as RichLayout
from rich.live import Live as RichLive
from rich.panel import Panel as RichPanel
from rich.progress import Progress
from rich.status import Status as RichStatus
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes


class FlextCliFormatters:
    """Thin Rich formatters facade - delegates to Rich library directly.

    ZERO TOLERANCE: Use Rich directly, minimal wrapper only for CLI abstraction.
    Removed 24 unused methods - keep ONLY what output.py actually uses.
    """

    def __init__(self) -> None:
        """Initialize Rich formatters with direct Rich imports."""
        # Use Rich directly (formatters.py is ONE OF TWO files that may import Rich)
        self.console = Console()

    def get_console(self) -> Console:
        """Get console instance - direct access."""
        return self.console

    def execute(self) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Execute service - required by FlextCore.Service."""
        return FlextCore.Result[FlextCore.Types.Dict].ok({
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.OPERATIONAL,
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.Services.FORMATTERS,
        })

    # =========================================================================
    # CORE METHODS - ACTUALLY USED BY output.py
    # =========================================================================

    def print(
        self,
        message: str,
        style: str | None = None,
    ) -> FlextCore.Result[None]:
        """Print formatted message using Rich.

        Args:
            message: Message to print
            style: Rich style string (e.g., "bold red")

        Returns:
            FlextCore.Result[None]: Success or error

        Note:
            For advanced Rich features, use get_console() to access Rich Console directly.

        """
        try:
            self.console.print(message, style=style)
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(f"Print failed: {e}")

    def create_table(
        self,
        data: FlextCliTypes.Data.CliDataDict | None = None,
        headers: FlextCore.Types.StringList | None = None,
        title: str | None = None,
    ) -> FlextCore.Result[RichTable]:
        """Create Rich table with basic formatting.

        Args:
            data: Optional data dictionary for table
            headers: Optional column headers
            title: Optional table title

        Returns:
            FlextCore.Result[RichTable]: Rich Table instance or error

        Note:
            For advanced Rich table features (box styles, padding, etc),
            use get_console() and create Rich tables directly.

        """
        try:
            table = RichTable(title=title)

            # Add columns if headers provided
            if headers:
                for header in headers:
                    table.add_column(header)

            # Add rows if data provided
            if data and isinstance(data, dict):
                # Simple dict to table conversion - key-value pairs for 2-column tables
                table_key_value_columns = 2
                if headers and len(headers) == table_key_value_columns:
                    # Key-value pairs
                    for key, value in data.items():
                        table.add_row(str(key), str(value))
                else:
                    # Single column with values
                    for key, value in data.items():
                        table.add_row(str(key), str(value))

            return FlextCore.Result[RichTable].ok(table)

        except Exception as e:
            return FlextCore.Result[RichTable].fail(f"Table creation failed: {e}")

    def render_table_to_string(
        self, table: RichTable, width: int | None = None
    ) -> FlextCore.Result[str]:
        """Render Rich table to string.

        Args:
            table: Rich Table instance
            width: Optional console width

        Returns:
            FlextCore.Result[str]: Rendered table string or error

        """
        try:
            # Use Rich's built-in rendering
            console = Console(width=width) if width else self.console

            # Capture console output
            buffer = StringIO()
            temp_console = Console(file=buffer, width=width or console.width)
            temp_console.print(table)
            output = buffer.getvalue()

            return FlextCore.Result[str].ok(output)

        except Exception as e:
            return FlextCore.Result[str].fail(f"Table rendering failed: {e}")

    def create_progress(self) -> FlextCore.Result[Progress]:
        """Create Rich progress bar with default settings.

        Returns:
            FlextCore.Result[Progress]: Rich Progress instance or error

        Note:
            For custom progress bars (columns, styles), use get_console()
            and create Progress objects directly.

        """
        try:
            progress = Progress()
            return FlextCore.Result[Progress].ok(progress)
        except Exception as e:
            return FlextCore.Result[Progress].fail(f"Progress creation failed: {e}")

    def create_tree(self, label: str) -> FlextCore.Result[RichTree]:
        """Create Rich tree with default settings.

        Args:
            label: Tree root label

        Returns:
            FlextCore.Result[RichTree]: Rich Tree instance or error

        Note:
            For custom tree styling, use get_console() and create Tree objects directly.

        """
        try:
            tree = RichTree(label)
            return FlextCore.Result[RichTree].ok(tree)
        except Exception as e:
            return FlextCore.Result[RichTree].fail(f"Tree creation failed: {e}")

    def render_tree_to_string(
        self, tree: RichTree, width: int | None = None
    ) -> FlextCore.Result[str]:
        """Render Rich tree to string.

        Args:
            tree: Rich Tree instance
            width: Optional console width

        Returns:
            FlextCore.Result[str]: Rendered tree string or error

        """
        try:
            buffer = StringIO()
            temp_console = Console(file=buffer, width=width or self.console.width)
            temp_console.print(tree)
            output = buffer.getvalue()

            return FlextCore.Result[str].ok(output)

        except Exception as e:
            return FlextCore.Result[str].fail(f"Tree rendering failed: {e}")

    # =========================================================================
    # ADVANCED RICH WRAPPERS - Status, Live, Layout, Panel
    # =========================================================================

    def create_status(
        self, message: str, spinner: str = "dots"
    ) -> FlextCore.Result[RichStatus]:
        """Create Rich status spinner.

        Args:
            message: Status message
            spinner: Spinner style (e.g., "dots", "line", "arrow")

        Returns:
            FlextCore.Result[RichStatus]: Rich Status instance or error

        Note:
            For custom spinners, use get_console() and create Status objects directly.

        """
        try:
            status = RichStatus(
                message,
                spinner=spinner,
                console=self.console,
            )
            return FlextCore.Result[RichStatus].ok(status)
        except Exception as e:
            return FlextCore.Result[RichStatus].fail(f"Status creation failed: {e}")

    def create_live(self, refresh_per_second: float = 4) -> FlextCore.Result[RichLive]:
        """Create Rich live display.

        Args:
            refresh_per_second: Refresh rate for live updates

        Returns:
            FlextCore.Result[RichLive]: Rich Live instance or error

        Note:
            For custom live displays, use get_console() and create Live objects directly.

        """
        try:
            live = RichLive(
                refresh_per_second=refresh_per_second,
                console=self.console,
            )
            return FlextCore.Result[RichLive].ok(live)
        except Exception as e:
            return FlextCore.Result[RichLive].fail(f"Live creation failed: {e}")

    def create_layout(self) -> FlextCore.Result[RichLayout]:
        """Create Rich layout with default settings.

        Returns:
            FlextCore.Result[RichLayout]: Rich Layout instance or error

        Note:
            For custom layouts (named regions, sizes), use get_console()
            and create Layout objects directly.

        """
        try:
            layout = RichLayout()
            return FlextCore.Result[RichLayout].ok(layout)
        except Exception as e:
            return FlextCore.Result[RichLayout].fail(f"Layout creation failed: {e}")

    def create_panel(
        self,
        content: str,
        title: str | None = None,
        border_style: str = "blue",
    ) -> FlextCore.Result[RichPanel]:
        """Create Rich panel with text content.

        Args:
            content: Panel content (text)
            title: Optional panel title
            border_style: Border style (e.g., "blue", "green", "red")

        Returns:
            FlextCore.Result[RichPanel]: Rich Panel instance or error

        Note:
            For panels with complex content (Rich renderables), use get_console()
            and create Panel objects directly.

        """
        try:
            panel = RichPanel(
                content,
                title=title,
                border_style=border_style,
            )
            return FlextCore.Result[RichPanel].ok(panel)
        except Exception as e:
            return FlextCore.Result[RichPanel].fail(f"Panel creation failed: {e}")


__all__ = [
    "FlextCliFormatters",
]
