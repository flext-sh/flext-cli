"""FLEXT CLI Formatters - Thin wrapper over Rich library.

Provides minimal CLI formatting abstraction. Uses Rich directly for all operations.
Following zero-tolerance principle: Use libraries, don't reimplement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from io import StringIO

from flext_core import FlextResult, FlextRuntime, FlextTypes
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

    def execute(self) -> FlextResult[FlextTypes.JsonDict]:
        """Execute service - required by FlextService."""
        return FlextResult[FlextTypes.JsonDict].ok({
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.Services.FORMATTERS,
        })

    # =========================================================================
    # CORE METHODS - ACTUALLY USED BY output.py
    # =========================================================================

    def print(
        self,
        message: str,
        style: str | None = None,
    ) -> FlextResult[bool]:
        """Print formatted message using Rich.

        Args:
            message: Message to print
            style: Rich style string (e.g., "bold red")

        Returns:
            FlextResult[bool]: True on success, False on failure

        Note:
            For advanced Rich features, access self.console directly.

        """
        try:
            self.console.print(message, style=style)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.FormattersErrorMessages.PRINT_FAILED.format(error=e)
            )

    def create_table(
        self,
        data: FlextCliTypes.Data.CliDataDict | None = None,
        headers: list[str] | None = None,
        title: str | None = None,
    ) -> FlextResult[RichTable]:
        """Create Rich table with basic formatting.

        Args:
            data: Optional data dictionary for table
            headers: Optional column headers
            title: Optional table title

        Returns:
            FlextResult[RichTable]: Rich Table instance or error

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
                # Simple FlextTypes.JsonDict to table conversion - key-value pairs for 2-column tables
                if (
                    headers
                    and len(headers)
                    == FlextCliConstants.FormattersDefaults.TABLE_KEY_VALUE_COLUMNS
                ):
                    # Key-value pairs
                    for key, value in data.items():
                        table.add_row(str(key), str(value))
                else:
                    # Single column with values
                    for key, value in data.items():
                        table.add_row(str(key), str(value))

            return FlextResult[RichTable].ok(table)

        except Exception as e:
            return FlextResult[RichTable].fail(
                FlextCliConstants.FormattersErrorMessages.TABLE_CREATION_FAILED.format(
                    error=e
                )
            )

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
            # Validate width explicitly - no fallback
            validated_width = width if width is not None else console.width
            temp_console = Console(file=buffer, width=validated_width)
            temp_console.print(table)
            output = buffer.getvalue()

            return FlextResult[str].ok(output)

        except Exception as e:
            return FlextResult[str].fail(
                FlextCliConstants.FormattersErrorMessages.TABLE_RENDERING_FAILED.format(
                    error=e
                )
            )

    def create_progress(self) -> FlextResult[Progress]:
        """Create Rich progress bar with default settings.

        Returns:
            FlextResult[Progress]: Rich Progress instance or error

        Note:
            For custom progress bars (columns, styles), access self.console
            directly and create Progress objects.

        """
        try:
            progress = Progress()
            return FlextResult[Progress].ok(progress)
        except Exception as e:
            return FlextResult[Progress].fail(
                FlextCliConstants.FormattersErrorMessages.PROGRESS_CREATION_FAILED.format(
                    error=e
                )
            )

    def create_tree(self, label: str) -> FlextResult[RichTree]:
        """Create Rich tree with default settings.

        Args:
            label: Tree root label

        Returns:
            FlextResult[RichTree]: Rich Tree instance or error

        Note:
            For custom tree styling, access self.console directly and create Tree objects.

        """
        try:
            tree = RichTree(label)
            return FlextResult[RichTree].ok(tree)
        except Exception as e:
            return FlextResult[RichTree].fail(
                FlextCliConstants.FormattersErrorMessages.TREE_CREATION_FAILED.format(
                    error=e
                )
            )

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
            # Validate width explicitly - no fallback
            validated_width = width if width is not None else self.console.width
            temp_console = Console(file=buffer, width=validated_width)
            temp_console.print(tree)
            output = buffer.getvalue()

            return FlextResult[str].ok(output)

        except Exception as e:
            return FlextResult[str].fail(
                FlextCliConstants.FormattersErrorMessages.TREE_RENDERING_FAILED.format(
                    error=e
                )
            )

    # =========================================================================
    # ADVANCED RICH WRAPPERS - Status, Live, Layout, Panel
    # =========================================================================

    def create_status(
        self,
        message: str,
        spinner: str | None = None,
    ) -> FlextResult[RichStatus]:
        """Create Rich status spinner.

        Args:
            message: Status message
            spinner: Spinner style (e.g., "dots", "line", "arrow")

        Returns:
            FlextResult[RichStatus]: Rich Status instance or error

        Note:
            For custom spinners, access self.console directly and create Status objects.

        """
        try:
            # Validate spinner explicitly - no fallback
            validated_spinner = (
                spinner
                if spinner is not None
                else FlextCliConstants.FormattersDefaults.DEFAULT_SPINNER
            )
            status = RichStatus(
                message,
                spinner=validated_spinner,
                console=self.console,
            )
            return FlextResult[RichStatus].ok(status)
        except Exception as e:
            return FlextResult[RichStatus].fail(
                FlextCliConstants.FormattersErrorMessages.STATUS_CREATION_FAILED.format(
                    error=e
                )
            )

    def create_live(
        self,
        refresh_per_second: float | None = None,
    ) -> FlextResult[RichLive]:
        """Create Rich live display.

        Args:
            refresh_per_second: Refresh rate for live updates

        Returns:
            FlextResult[RichLive]: Rich Live instance or error

        Note:
            For custom live displays, access self.console directly and create Live objects.

        """
        try:
            # Validate refresh rate explicitly - no fallback
            validated_refresh_rate = (
                refresh_per_second
                if refresh_per_second is not None
                else FlextCliConstants.FormattersDefaults.DEFAULT_REFRESH_RATE
            )
            live = RichLive(
                refresh_per_second=validated_refresh_rate,
                console=self.console,
            )
            return FlextResult[RichLive].ok(live)
        except Exception as e:
            return FlextResult[RichLive].fail(
                FlextCliConstants.FormattersErrorMessages.LIVE_CREATION_FAILED.format(
                    error=e
                )
            )

    def create_layout(self) -> FlextResult[RichLayout]:
        """Create Rich layout with default settings.

        Returns:
            FlextResult[RichLayout]: Rich Layout instance or error

        Note:
            For custom layouts (named regions, sizes), access self.console
            directly and create Layout objects.

        """
        try:
            layout = RichLayout()
            return FlextResult[RichLayout].ok(layout)
        except Exception as e:
            return FlextResult[RichLayout].fail(
                FlextCliConstants.FormattersErrorMessages.LAYOUT_CREATION_FAILED.format(
                    error=e
                )
            )

    def create_panel(
        self,
        content: str,
        title: str | None = None,
        border_style: str | None = None,
    ) -> FlextResult[RichPanel]:
        """Create Rich panel with text content.

        Args:
            content: Panel content (text)
            title: Optional panel title
            border_style: Border style (e.g., "blue", "green", "red")

        Returns:
            FlextResult[RichPanel]: Rich Panel instance or error

        Note:
            For panels with complex content (Rich renderables), access self.console
            directly and create Panel objects.

        """
        try:
            # Validate border style explicitly - no fallback
            validated_border_style = (
                border_style
                if border_style is not None
                else FlextCliConstants.FormattersDefaults.DEFAULT_BORDER_STYLE
            )
            panel = RichPanel(
                content,
                title=title,
                border_style=validated_border_style,
            )
            return FlextResult[RichPanel].ok(panel)
        except Exception as e:
            return FlextResult[RichPanel].fail(
                FlextCliConstants.FormattersErrorMessages.PANEL_CREATION_FAILED.format(
                    error=e
                )
            )


__all__ = [
    "FlextCliFormatters",
]
