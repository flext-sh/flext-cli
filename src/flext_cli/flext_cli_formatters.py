"""FLEXT CLI Formatters - Direct Rich integration for output formatting.

Provides Rich-based formatting functionality for the FLEXT CLI ecosystem.
This is the only module allowed to import Rich components directly.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from io import StringIO

from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table
from rich.text import Text

from flext_core import (
    FlextLogger,
    FlextResult,
    FlextService,
)


class FlextCliFormatters(FlextService[str]):
    """CLI formatters using direct Rich integration.

    This class provides Rich-based formatting functionality and is the ONLY
    module in the FLEXT ecosystem allowed to import Rich components directly.
    """

    def __init__(self) -> None:
        """Initialize CLI formatters with Rich console."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._console = Console()

    def execute(self) -> FlextResult[str]:
        """Execute the main domain service operation - required by FlextService."""
        return FlextResult[str].ok("FlextCliFormatters operational")

    def create_table(
        self,
        data: list[dict[str, object]],
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> FlextResult[Table]:
        """Create a Rich table from data.

        Args:
            data: List of dictionaries to display
            title: Optional table title
            headers: Optional custom headers

        Returns:
            FlextResult[Table]: Rich table or error

        """
        if not data:
            return FlextResult[Table].fail("No data provided for table")

        try:
            table = Table(title=title)

            # Use provided headers or infer from first row
            table_headers = headers or list(data[0].keys())

            # Add columns
            for header in table_headers:
                table.add_column(str(header))

            # Add rows
            for row_data in data:
                row_values = [str(row_data.get(h, "")) for h in table_headers]
                table.add_row(*row_values)

            return FlextResult[Table].ok(table)

        except Exception as e:
            return FlextResult[Table].fail(f"Failed to create table: {e}")

    def table_to_string(
        self, table: Table, width: int | None = None
    ) -> FlextResult[str]:
        """Convert Rich table to string.

        Args:
            table: Rich table to convert
            width: Optional console width

        Returns:
            FlextResult[str]: Table as string or error

        """
        try:
            console = Console(file=StringIO(), width=width)
            console.print(table)
            return FlextResult[str].ok(console.file.getvalue())
        except Exception as e:
            return FlextResult[str].fail(f"Failed to convert table to string: {e}")

    def create_progress_bar(
        self, description: str = "Processing...", total: int = 100
    ) -> FlextResult[tuple[Progress, TaskID]]:
        """Create a Rich progress bar.

        Args:
            description: Progress description
            total: Total number of steps

        Returns:
            FlextResult[tuple[Progress, TaskID]]: Progress and task ID or error

        """
        try:
            progress = Progress()
            task_id = progress.add_task(description, total=total)
            return FlextResult[tuple[Progress, TaskID]].ok((progress, task_id))
        except Exception as e:
            return FlextResult[tuple[Progress, TaskID]].fail(
                f"Failed to create progress bar: {e}"
            )

    def print_message(
        self, message: str, style: str = "", *, highlight: bool = False
    ) -> FlextResult[None]:
        """Print a message using Rich console.

        Args:
            message: Message to print
            style: Optional Rich style
            highlight: Whether to enable syntax highlighting

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            if style:
                text = Text(message, style=style)
                self._console.print(text, highlight=highlight)
            else:
                self._console.print(message, highlight=highlight)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to print message: {e}")

    def print_error(self, message: str) -> FlextResult[None]:
        """Print an error message with red styling.

        Args:
            message: Error message to print

        Returns:
            FlextResult[None]: Success or failure result

        """
        return self.print_message(f"Error: {message}", style="bold red")

    def print_success(self, message: str) -> FlextResult[None]:
        """Print a success message with green styling.

        Args:
            message: Success message to print

        Returns:
            FlextResult[None]: Success or failure result

        """
        return self.print_message(f"Success: {message}", style="bold green")

    def print_warning(self, message: str) -> FlextResult[None]:
        """Print a warning message with yellow styling.

        Args:
            message: Warning message to print

        Returns:
            FlextResult[None]: Success or failure result

        """
        return self.print_message(f"Warning: {message}", style="bold yellow")

    def get_console(self) -> Console:
        """Get the Rich console instance.

        Returns:
            Console: Rich console instance

        """
        return self._console

    def create_formatter(self, format_type: str) -> FlextResult[object]:
        """Create a formatter for the specified format type.

        Args:
            format_type: The format type (table, json, yaml, etc.)

        Returns:
            FlextResult[object]: Formatter object or error

        """
        if format_type == "table":
            return FlextResult[object].ok(self)
        return FlextResult[object].fail(f"Unsupported format type: {format_type}")

    class _ConsoleOutput:
        """Console output wrapper for compatibility."""

        def __init__(self, file: object = None, **kwargs: object) -> None:
            """Initialize console output wrapper."""
            from rich.console import Console

            self._console = Console(file=file, **kwargs)

        def print(self, *args: object, **kwargs: object) -> None:
            """Print to console."""
            self._console.print(*args, **kwargs)

        def getvalue(self) -> str:
            """Get console output as string."""
            if hasattr(self._console.file, "getvalue"):
                value = self._console.file.getvalue()
                return str(value) if value is not None else ""
            return ""

    @property
    def console(self) -> Console:
        """Console property for backward compatibility.

        Returns:
            Console: Rich console instance

        """
        return self._console

    def format_table(
        self,
        data: dict[str, object] | list[dict[str, object]],
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> FlextResult[Table]:
        """Format data as a Rich table.

        Args:
            data: Data to format (dict or list of dicts)
            title: Optional table title
            headers: Optional column headers

        Returns:
            FlextResult[Table]: Rich Table object or error

        """
        try:
            if isinstance(data, dict):
                # Convert single dict to list of key-value pairs
                table_data: list[dict[str, object]] = [
                    {"Key": k, "Value": str(v)} for k, v in data.items()
                ]
                default_headers = ["Key", "Value"]
            else:
                # Use list of dicts as is
                table_data = data
                default_headers = list(table_data[0].keys()) if table_data else []

            table = Table(title=title)

            # Add columns
            columns = headers or default_headers
            for col in columns:
                table.add_column(col)

            # Add rows
            for row_data in table_data:
                row_values = [str(row_data.get(col, "")) for col in columns]
                table.add_row(*row_values)

            return FlextResult[Table].ok(table)

        except Exception as e:
            return FlextResult[Table].fail(f"Failed to format table: {e}")

    def format_data(
        self,
        data: dict[str, object] | list[dict[str, object]],
        format_type: str = "table",
        **options: object,
    ) -> FlextResult[str]:
        """Format data according to the specified format type.

        Args:
            data: Data to format
            format_type: Format type (table, json, etc.)
            **options: Additional formatting options

        Returns:
            FlextResult[str]: Formatted data string or error

        """
        try:
            if format_type == "table":
                title_value = options.get("title")
                headers_value = options.get("headers")
                table_result = self.format_table(
                    data=data,
                    title=str(title_value) if title_value is not None else None,
                    headers=list(headers_value)
                    if isinstance(headers_value, (list, tuple))
                    else None,
                )
                if table_result.is_failure:
                    return FlextResult[str].fail(
                        table_result.error or "Table formatting failed"
                    )

                # Capture table output to string
                with StringIO() as output:
                    temp_console = Console(file=output, width=80)
                    temp_console.print(table_result.unwrap())
                    return FlextResult[str].ok(output.getvalue())

            elif format_type == "json":
                import json

                return FlextResult[str].ok(json.dumps(data, indent=2))

            else:
                return FlextResult[str].fail(f"Unsupported format type: {format_type}")

        except Exception as e:
            return FlextResult[str].fail(f"Failed to format data: {e}")


__all__ = [
    "FlextCliFormatters",
]
