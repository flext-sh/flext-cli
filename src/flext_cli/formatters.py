"""FLEXT CLI Formatters - Thin wrapper over Rich library.

Provides minimal CLI formatting abstraction. Uses Rich directly for all operations.
Following zero-tolerance principle: Use libraries, don't reimplement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from flext_core import FlextCore, FlextResult
from rich.console import Console
from rich.progress import Progress
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
        """Initialize Rich formatters - console lazy-loaded."""
        self._console: Console | None = None

    @property
    def console(self) -> Console:
        """Get Rich console instance (lazy-loaded).

        Returns:
            Console: Rich console

        """
        if self._console is None:
            self._console = Console()
        return self._console

    def get_console(self) -> Console:
        """Get console instance - same as property."""
        return self.console

    def execute(self) -> FlextResult[FlextCore.Types.Dict]:
        """Execute service - required by FlextCore.Service."""
        return FlextResult[FlextCore.Types.Dict].ok({
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
    ) -> FlextResult[None]:
        """Print formatted message using Rich - direct delegation.

        Args:
            message: Message to print
            style: Rich style string (e.g., "bold red")
            **kwargs: Additional Rich console.print() kwargs

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            self.console.print(message, style=style, **kwargs)  # type: ignore[arg-type]
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print failed: {e}")

    def create_table(
        self,
        data: FlextCliTypes.Data.CliDataDict | None = None,
        headers: FlextCore.Types.StringList | None = None,
        title: str | None = None,
        **kwargs: object,
    ) -> FlextResult[RichTable]:
        """Create Rich table - direct delegation to Rich.Table.

        Args:
            data: Optional data dictionary for table
            headers: Optional column headers
            title: Optional table title
            **kwargs: Additional Rich Table() kwargs

        Returns:
            FlextResult[RichTable]: Rich Table instance or error

        """
        try:
            # Create Rich table directly
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

            return FlextResult[RichTable].ok(table)

        except Exception as e:
            return FlextResult[RichTable].fail(f"Table creation failed: {e}")

    def render_table_to_string(
        self, table: RichTable, width: int | None = None
    ) -> FlextResult[str]:
        """Render Rich table to string.

        Args:
            table: Rich Table instance
            width: Optional console width

        Returns:
            FlextResult[str]: Rendered table string or error

        """
        try:
            # Use Rich's built-in rendering
            console = Console(width=width) if width else self.console

            # Capture console output
            buffer = StringIO()
            temp_console = Console(file=buffer, width=width or console.width)
            temp_console.print(table)
            output = buffer.getvalue()

            return FlextResult[str].ok(output)

        except Exception as e:
            return FlextResult[str].fail(f"Table rendering failed: {e}")

    def create_progress(self, **kwargs: object) -> FlextResult[Progress]:
        """Create Rich progress bar - direct delegation.

        Args:
            **kwargs: Rich Progress() kwargs

        Returns:
            FlextResult[Progress]: Rich Progress instance or error

        """
        try:
            progress = Progress(**kwargs)  # type: ignore[arg-type]
            return FlextResult[Progress].ok(progress)
        except Exception as e:
            return FlextResult[Progress].fail(f"Progress creation failed: {e}")

    def create_tree(self, label: str, **kwargs: object) -> FlextResult[RichTree]:
        """Create Rich tree - direct delegation.

        Args:
            label: Tree root label
            **kwargs: Rich Tree() kwargs

        Returns:
            FlextResult[RichTree]: Rich Tree instance or error

        """
        try:
            tree = RichTree(label, **kwargs)  # type: ignore[arg-type]
            return FlextResult[RichTree].ok(tree)
        except Exception as e:
            return FlextResult[RichTree].fail(f"Tree creation failed: {e}")

    def render_tree_to_string(
        self, tree: RichTree, width: int | None = None
    ) -> FlextResult[str]:
        """Render Rich tree to string.

        Args:
            tree: Rich Tree instance
            width: Optional console width

        Returns:
            FlextResult[str]: Rendered tree string or error

        """
        try:
            buffer = StringIO()
            temp_console = Console(file=buffer, width=width or self.console.width)
            temp_console.print(tree)
            output = buffer.getvalue()

            return FlextResult[str].ok(output)

        except Exception as e:
            return FlextResult[str].fail(f"Tree rendering failed: {e}")


__all__ = ["FlextCliFormatters"]
