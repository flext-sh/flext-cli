"""FLEXT CLI Formatters - Output formatting utilities following flext-core patterns.

Provides comprehensive output formatting for CLI applications including table,
JSON, YAML, and CSV formats with Rich integration for enhanced terminal display.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import sys
from collections.abc import Callable
from io import StringIO
from pathlib import Path
from typing import ClassVar, Protocol, TextIO, cast, runtime_checkable

import yaml
from flext_core import FlextResult, FlextUtilities
from rich.console import Console
from rich.table import Table as RichTable
from tabulate import tabulate

# Direct rich and tabulate usage for best performance and features


class FlextCliFormatters:
    """Consolidated output formatting following flext-core patterns.

    Provides comprehensive formatting operations including table, JSON, YAML, CSV,
    and plain text formats with FlextResult error handling and console output.
    Unified class containing ALL formatter functionality including protocols.

    Features:
        - Multiple output formats (table, JSON, YAML, CSV, plain)
        - Console table formatting with auto-detection
        - Type-safe formatting with FlextResult
        - Protocol-based formatter registry
        - Console output management
        - Error handling and validation
    """

    class _ConsoleOutput:
        """Rich Console wrapper for direct rich functionality."""

        def __init__(self, file: TextIO | None = None) -> None:
            """Initialize with Rich Console."""
            self._console = Console(file=file or sys.stdout)

        def print(self, text: str, **kwargs: object) -> None:
            """Print text using Rich Console directly."""
            # Cast for Rich Console compatibility - Rich accepts flexible kwargs
            self._console.print(text, **dict(kwargs))  # type: ignore[reportArgumentType]

        def out(self, text: str) -> None:
            """Output raw text using Rich Console."""
            self._console.out(text)

        @property
        def console(self) -> Console:
            """Get the underlying Rich Console instance."""
            return self._console

    @runtime_checkable
    class OutputFormatter(Protocol):
        """Protocol for formatter classes used by the CLI."""

        def format(
            self, data: object, console: FlextCliFormatters._ConsoleOutput | Console
        ) -> None:
            """Format data using console output."""

    # Registry of available formatters
    _registry: ClassVar[
        dict[
            str,
            type[FlextCliFormatters.OutputFormatter]
            | Callable[[], FlextCliFormatters.OutputFormatter],
        ]
    ] = {}

    def __init__(
        self,
        *,
        console: _ConsoleOutput | Console | None = None,
        default_format: str = "table",
    ) -> None:
        """Initialize formatters with console and default format.

        Args:
            console: Console output instance (Rich Console or wrapper)
            default_format: Default output format to use

        """
        # Support both Rich Console and our wrapper
        if isinstance(console, Console):
            self.console = self._ConsoleOutput(file=cast("TextIO | None", console.file))
        else:
            self.console = console or self._ConsoleOutput()
        self.default_format = default_format
        self._setup_registry()

    def _setup_registry(self) -> None:
        """Setup the formatter registry with built-in formatters."""
        # Update class variable by accessing it directly
        FlextCliFormatters._registry = {
            "table": self._TableFormatter,
            "json": self._JSONFormatter,
            "yaml": self._YAMLFormatter,
            "csv": lambda: self._CSVFormatter(self),
            "plain": self._PlainFormatter,
        }

    class _TableFormatter:
        """Internal table formatter using tabulate and Rich directly."""

        def format(
            self, data: object, console: FlextCliFormatters._ConsoleOutput | Console
        ) -> None:
            # Use tabulate for high-quality table formatting
            try:
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    # List of dictionaries - use tabulate with keys as headers
                    formatted = tabulate(data, headers="keys", tablefmt="simple")
                    console.print(formatted)
                elif isinstance(data, dict):
                    # Dictionary - convert to list of key-value pairs
                    table_data = [[k, v] for k, v in data.items()]
                    formatted = tabulate(
                        table_data, headers=["Key", "Value"], tablefmt="simple"
                    )
                    console.print(formatted)
                elif isinstance(data, list):
                    # Simple list - single column
                    table_data = [[item] for item in data]
                    formatted = tabulate(
                        table_data, headers=["Value"], tablefmt="simple"
                    )
                    console.print(formatted)
                else:
                    # Single value
                    table_data = [[str(data)]]
                    formatted = tabulate(
                        table_data, headers=["Value"], tablefmt="simple"
                    )
                    console.print(formatted)
            except Exception:
                # Fallback to simple formatting
                console.print(str(data))

    class _JSONFormatter:
        """Internal JSON formatter implementation."""

        def format(
            self, data: object, console: FlextCliFormatters._ConsoleOutput | Console
        ) -> None:
            try:
                formatted = FlextUtilities.safe_json_stringify(data)
                console.out(formatted)
            except (TypeError, ValueError, RuntimeError) as e:
                console.print(f"JSON formatting failed: {e}")
                console.print(f"Data (as string): {data}")

    class _YAMLFormatter:
        """Internal YAML formatter implementation."""

        def _convert_paths_to_strings(self, obj: object) -> object:
            """Convert Path objects to strings for YAML serialization."""
            if isinstance(obj, Path):
                return str(obj)
            if isinstance(obj, dict):
                return {
                    key: self._convert_paths_to_strings(value)
                    for key, value in obj.items()
                }
            if isinstance(obj, (list, tuple)):
                return [self._convert_paths_to_strings(item) for item in obj]
            return obj

        def format(
            self, data: object, console: FlextCliFormatters._ConsoleOutput | Console
        ) -> None:
            # Convert Path objects to strings before YAML serialization
            converted_data = self._convert_paths_to_strings(data)
            formatted = yaml.safe_dump(converted_data, default_flow_style=False)
            console.print(formatted)

    class _CSVFormatter:
        """Internal CSV formatter implementation."""

        def __init__(self, formatters_instance: FlextCliFormatters) -> None:
            """Initialize with reference to parent formatters instance."""
            self._formatters = formatters_instance

        def format(
            self, data: object, console: FlextCliFormatters._ConsoleOutput | Console
        ) -> None:
            """Format data as CSV using the consolidated CSV implementation."""
            result = self._formatters.format_csv(data)
            if result.is_success:
                console.print(result.value)
            else:
                raise ValueError(result.error)

    class _PlainFormatter:
        """Internal plain text formatter implementation."""

        def format(
            self, data: object, console: FlextCliFormatters._ConsoleOutput | Console
        ) -> None:
            if isinstance(data, dict):
                for k, v in data.items():
                    console.print(f"{k}: {v}")
            elif isinstance(data, list):
                for v in data:
                    if isinstance(v, dict):
                        for k, val in v.items():
                            console.print(f"{k}: {val}")
                        console.print("")  # Empty line between dict entries
                    else:
                        console.print(str(v))
            else:
                console.print(str(data))

    def create_formatter(self, name: str) -> FlextCliFormatters.OutputFormatter:
        """Create formatter instance by name.

        Args:
            name: Formatter name from registry

        Returns:
            FlextCliFormatters.OutputFormatter: Formatter instance

        Raises:
            ValueError: If formatter name is unknown

        """
        formatter_factory = self._registry.get(name)
        if not formatter_factory:
            msg = f"Unsupported format: {name}"
            raise ValueError(msg)
        # Handle both classes and lambda factories
        return formatter_factory()

    def register_formatter(
        self,
        name: str,
        formatter_class: type[FlextCliFormatters.OutputFormatter],
    ) -> None:
        """Register custom formatter.

        Args:
            name: Formatter name for registry
            formatter_class: Formatter class implementing FlextCliFormatters.OutputFormatter protocol

        """
        self._registry[name] = formatter_class

    def list_formats(self) -> list[str]:
        """List all available formatter names.

        Returns:
            List of available formatter names

        """
        return sorted(self._registry.keys())

    def format_output(self, data: object, fmt: str | None = None) -> FlextResult[None]:
        """Format and output data to console.

        Args:
            data: Data to format and output
            fmt: Format type to use (defaults to default_format)

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            format_type = fmt or self.default_format
            formatter = self.create_formatter(format_type)
            formatter.format(data, self.console)
            return FlextResult[None].ok(None)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[None].fail(f"Format output failed: {e}")

    def format_data(self, data: object, format_type: str) -> FlextResult[str]:
        """Format data to string without outputting to console.

        Args:
            data: Data to format
            format_type: Format type to use

        Returns:
            FlextResult[str]: Formatted string or error

        """
        try:
            # Special handling for plain format to avoid newlines
            if format_type == "plain":
                return FlextResult[str].ok(str(data))

            # Capture output using StringIO
            string_buffer = StringIO()
            temp_console = self._ConsoleOutput(file=string_buffer)
            formatter = self.create_formatter(format_type)
            formatter.format(data, temp_console)

            result = string_buffer.getvalue().rstrip("\n")
            return FlextResult[str].ok(result)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[str].fail(f"Format data failed: {e}")

    def format_table(
        self, data: object, title: str | None = None
    ) -> FlextResult[str]:
        """Format data as a table using tabulate.

        Args:
            data: Data to format as table
            title: Optional table title

        Returns:
            FlextResult[str]: Formatted table string or error

        """
        try:
            # Use tabulate directly for best table formatting
            result_lines: list[str] = []

            if title:
                result_lines.extend((f"=== {title} ===", ""))

            if isinstance(data, list) and data and isinstance(data[0], dict):
                # List of dictionaries - use tabulate with keys as headers
                formatted = tabulate(data, headers="keys", tablefmt="simple")
            elif isinstance(data, dict):
                # Single dictionary - convert to list of key-value pairs
                table_data = [{"Key": k, "Value": str(v)} for k, v in data.items()]
                formatted = tabulate(table_data, headers="keys", tablefmt="simple")
            else:
                return FlextResult[str].fail("Data must be a dict or list of dicts")

            result_lines.append(formatted)
            return FlextResult[str].ok("\n".join(result_lines))

        except Exception as e:
            return FlextResult[str].fail(f"Table formatting failed: {e}")

    def format_json(self, data: object) -> FlextResult[str]:
        """Format data as JSON string.

        Args:
            data: Data to format as JSON
            indent: JSON indentation level

        Returns:
            FlextResult[str]: JSON string or error

        """
        try:
            result = FlextUtilities.safe_json_stringify(data)
            return FlextResult[str].ok(result)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[str].fail(f"JSON format failed: {e}")

    def format_yaml(self, data: object) -> FlextResult[str]:
        """Format data as YAML string.

        Args:
            data: Data to format as YAML

        Returns:
            FlextResult[str]: YAML string or error

        """
        try:
            result = yaml.safe_dump(data, default_flow_style=False)
            return FlextResult[str].ok(result)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[str].fail(f"YAML format failed: {e}")

    def format_csv(self, data: object) -> FlextResult[str]:
        """Format data as CSV string.

        Args:
            data: Data to format as CSV

        Returns:
            FlextResult[str]: CSV string or error

        """
        try:
            output = StringIO()
            try:
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    # Validate that all dictionaries have consistent keys
                    first_keys = set(data[0].keys())
                    for _i, item in enumerate(data[1:], 1):
                        if isinstance(item, dict):
                            item_keys = set(item.keys())
                            if item_keys != first_keys:
                                msg = "dict contains fields not in fieldnames"
                                raise ValueError(msg)

                    dict_writer = csv.DictWriter(output, fieldnames=data[0].keys())
                    dict_writer.writeheader()
                    dict_writer.writerows(data)
                elif isinstance(data, dict):
                    dict_writer = csv.DictWriter(output, fieldnames=data.keys())
                    dict_writer.writeheader()
                    dict_writer.writerow(data)
                else:
                    # Python 3.13+ structural pattern matching for CSV output
                    plain_writer = csv.writer(output)
                    match data:
                        case list() if data:
                            for item in data:
                                plain_writer.writerow([str(item)])
                        case _:
                            plain_writer.writerow([str(data)])
                result = output.getvalue()
                return FlextResult[str].ok(result)
            finally:
                output.close()
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[str].fail(f"CSV format failed: {e}")

    def print_success(self, message: str) -> FlextResult[None]:
        """Print success message with Rich styling.

        Args:
            message: Success message to display

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            # Use Rich styling for success messages
            self.console.print(f"[green]✓[/green] {message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print success failed: {e}")

    def print_error(self, message: str) -> FlextResult[None]:
        """Print error message with Rich styling.

        Args:
            message: Error message to display

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            # Use Rich styling for error messages
            self.console.print(f"[red]✗[/red] {message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print error failed: {e}")

    def print_warning(self, message: str) -> FlextResult[None]:
        """Print warning message with Rich styling.

        Args:
            message: Warning message to display

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            # Use Rich styling for warning messages
            self.console.print(f"[yellow]⚠[/yellow] {message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print warning failed: {e}")

    def display_message(
        self, message: str, message_type: str = "info"
    ) -> FlextResult[None]:
        """Display message with specified type.

        Args:
            message: Message to display
            message_type: Type of message (info, success, error, warning)

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            match message_type.lower():
                case "success":
                    return self.print_success(message)
                case "error":
                    return self.print_error(message)
                case "warning":
                    return self.print_warning(message)
                case "info" | _:
                    # Use Rich styling for info messages
                    self.console.print(f"[blue]i[/blue] {message}")
                    return FlextResult[None].ok(None)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[None].fail(f"Display message failed: {e}")

    def display_formatted_output(
        self, formatted_data: str, title: str | None = None
    ) -> FlextResult[None]:
        """Display formatted output with optional title.

        Args:
            formatted_data: Pre-formatted data string
            title: Optional title to display above the data

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            if title:
                self.console.print(f"\n{title}")
                self.console.print("-" * len(title))

            self.console.print(formatted_data)
            return FlextResult[None].ok(None)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[None].fail(f"Display formatted output failed: {e}")

    def create_rich_table_object(
        self,
        data: object,
        title: str | None = None,
    ) -> FlextResult[object]:
        """Create Rich Table object with enhanced styling and features."""
        try:
            # Create Rich table with enhanced styling
            rich_table = RichTable(
                title=title,
                show_header=True,
                header_style="bold magenta",
                show_lines=True,
                expand=False,
            )

            if isinstance(data, dict):
                # Add styled columns for dict data
                rich_table.add_column("Key", style="cyan", no_wrap=True)
                rich_table.add_column("Value", style="white")

                # Add rows with Rich markup support
                for key, value in data.items():
                    rich_table.add_row(str(key), str(value))
            elif isinstance(data, (list, tuple)):
                # Handle list/tuple data
                if data and isinstance(data[0], dict):
                    # List of dicts - use keys as columns with styling
                    keys = list(data[0].keys()) if data else []
                    for i, key in enumerate(keys):
                        style = "cyan" if i == 0 else "white"
                        rich_table.add_column(str(key), style=style)

                    for item in data:
                        row_values = [str(item.get(key, "")) for key in keys]
                        rich_table.add_row(*row_values)
                else:
                    # Simple list - single column with styling
                    rich_table.add_column("Value", style="white")
                    for item in data:
                        rich_table.add_row(str(item))
            else:
                # Single value with styling
                rich_table.add_column("Value", style="white")
                rich_table.add_row(str(data))

            return FlextResult[object].ok(rich_table)
        except Exception as e:
            return FlextResult[object].fail(f"Rich table creation failed: {e}")


__all__ = [
    "FlextCliFormatters",
]
