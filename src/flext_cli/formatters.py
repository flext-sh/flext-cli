"""FLEXT CLI Formatters - Thin wrapper over Rich library.

Provides minimal CLI formatting abstraction. Uses Rich directly for all operations.
Following zero-tolerance principle: Use libraries, don't reimplement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from flext_core import FlextCore
from rich.console import Console
from rich.layout import Layout as RichLayout
from rich.live import Live as RichLive
from rich.panel import Panel as RichPanel
from rich.progress import (
    Progress,
)
from rich.status import Status as RichStatus
from rich.table import Table as RichTable
from rich.tree import Tree as RichTree

from flext_cli.constants import FlextCliConstants

if TYPE_CHECKING:
    from flext_cli.typings import FlextCliTypes


class FlextCliFormatters:
    """Thin Rich formatters facade - delegates to Rich library directly.

    ZERO TOLERANCE: Use Rich directly, minimal wrapper only for CLI abstraction.
    Removed 24 unused methods - keep ONLY what output.py actually uses.
    """

    def __init__(self) -> None:
        """Initialize Rich formatters with direct console initialization."""
        # Direct initialization - no lazy loading, no @property wrapper
        self.console: Console = Console()

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
        **kwargs: object,
    ) -> FlextCore.Result[None]:
        """Print formatted message using Rich - direct delegation.

        Args:
            message: Message to print
            style: Rich style string (e.g., "bold red")
            **kwargs: Additional Rich console.print() kwargs

        Returns:
            FlextCore.Result[None]: Success or error

        """
        try:
            # Direct delegation to Rich - duck typing handles kwargs
            self.console.print(message, style=style, **kwargs)  # type: ignore[arg-type]
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(f"Print failed: {e}")

    def create_table(
        self,
        data: FlextCliTypes.Data.CliDataDict | None = None,
        headers: FlextCore.Types.StringList | None = None,
        title: str | None = None,
        **kwargs: object,
    ) -> FlextCore.Result[RichTable]:
        """Create Rich table - direct delegation to Rich.Table.

        Args:
            data: Optional data dictionary for table
            headers: Optional column headers
            title: Optional table title
            **kwargs: Additional Rich Table() kwargs

        Returns:
            FlextCore.Result[RichTable]: Rich Table instance or error

        """
        try:
            # Create Rich table directly - duck typing handles kwargs
            table = RichTable(title=title, **kwargs)  # type: ignore[arg-type]

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

    def create_progress(self, **kwargs: object) -> FlextCore.Result[Progress]:
        """Create Rich progress bar - direct delegation.

        Args:
            **kwargs: Rich Progress() kwargs

        Returns:
            FlextCore.Result[Progress]: Rich Progress instance or error

        """
        try:
            # Direct delegation to Rich - duck typing handles kwargs
            progress = Progress(**kwargs)  # type: ignore[arg-type]
            return FlextCore.Result[Progress].ok(progress)
        except Exception as e:
            return FlextCore.Result[Progress].fail(f"Progress creation failed: {e}")

    def create_tree(self, label: str, **kwargs: object) -> FlextCore.Result[RichTree]:
        """Create Rich tree - direct delegation.

        Args:
            label: Tree root label
            **kwargs: Rich Tree() kwargs

        Returns:
            FlextCore.Result[RichTree]: Rich Tree instance or error

        """
        try:
            # Direct delegation to Rich - duck typing handles kwargs
            tree = RichTree(label, **kwargs)  # type: ignore[arg-type]
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
        self, message: str, spinner: str = "dots", **kwargs: object
    ) -> FlextCore.Result[RichStatus]:
        """Create Rich status spinner - direct delegation.

        Args:
            message: Status message
            spinner: Spinner style (e.g., "dots", "line", "arrow")
            **kwargs: Additional Rich Status() kwargs

        Returns:
            FlextCore.Result[RichStatus]: Rich Status instance or error

        """
        try:
            # Direct delegation to Rich - duck typing handles kwargs
            status = RichStatus(
                message, spinner=spinner, console=self.console, **kwargs  # type: ignore[arg-type]
            )
            return FlextCore.Result[RichStatus].ok(status)
        except Exception as e:
            return FlextCore.Result[RichStatus].fail(f"Status creation failed: {e}")

    def create_live(
        self, refresh_per_second: float = 4, **kwargs: object
    ) -> FlextCore.Result[RichLive]:
        """Create Rich live display - direct delegation.

        Args:
            refresh_per_second: Refresh rate for live updates
            **kwargs: Additional Rich Live() kwargs

        Returns:
            FlextCore.Result[RichLive]: Rich Live instance or error

        """
        try:
            # Direct delegation to Rich - duck typing handles kwargs
            live = RichLive(
                refresh_per_second=refresh_per_second,
                console=self.console,
                **kwargs,  # type: ignore[arg-type]
            )
            return FlextCore.Result[RichLive].ok(live)
        except Exception as e:
            return FlextCore.Result[RichLive].fail(f"Live creation failed: {e}")

    def create_layout(self, **kwargs: object) -> FlextCore.Result[RichLayout]:
        """Create Rich layout - direct delegation.

        Args:
            **kwargs: Additional Rich Layout() kwargs

        Returns:
            FlextCore.Result[RichLayout]: Rich Layout instance or error

        """
        try:
            # Direct delegation to Rich - duck typing handles kwargs
            layout = RichLayout(**kwargs)  # type: ignore[arg-type]
            return FlextCore.Result[RichLayout].ok(layout)
        except Exception as e:
            return FlextCore.Result[RichLayout].fail(f"Layout creation failed: {e}")

    def create_panel(
        self,
        content: object,
        title: str | None = None,
        border_style: str = "blue",
        **kwargs: object,
    ) -> FlextCore.Result[RichPanel]:
        """Create Rich panel - direct delegation.

        Args:
            content: Panel content
            title: Optional panel title
            border_style: Border style (e.g., "blue", "green", "red")
            **kwargs: Additional Rich Panel() kwargs

        Returns:
            FlextCore.Result[RichPanel]: Rich Panel instance or error

        """
        try:
            # Direct delegation to Rich - duck typing handles kwargs
            panel = RichPanel(
                content,  # type: ignore[arg-type]
                title=title,
                border_style=border_style,
                **kwargs,  # type: ignore[arg-type]
            )
            return FlextCore.Result[RichPanel].ok(panel)
        except Exception as e:
            return FlextCore.Result[RichPanel].fail(f"Panel creation failed: {e}")


__all__ = [
    "FlextCliFormatters",
]
