"""FLEXT CLI Formatters - Output formatting utilities following flext-core patterns.

Provides comprehensive output formatting for CLI applications including table,
JSON, YAML, and CSV formats with Rich integration for enhanced terminal display.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import json
from io import StringIO
from typing import (
    IO,
    Literal,
    Protocol,
)

import yaml
from rich.console import Console
from rich.table import Table as RichTable
from tabulate import tabulate

from flext_core import FlextResult

JustifyOption = Literal["default", "left", "center", "right", "full"]
OverflowOption = Literal["fold", "crop", "ellipsis", "ignore"]


class FlextCliFormatters:
    """FLEXT CLI Formatters - Rich output abstraction for CLI ecosystem.

    Provides comprehensive output formatting while abstracting Rich implementation.
    ZERO TOLERANCE: This is the ONLY place Rich should be imported in CLI ecosystem.
    """

    class FormatterProtocol(Protocol):
        """Protocol for formatters to ensure consistent interface."""

        def format(self, data: object, console: Console) -> None:
            """Format data and output to console."""
            ...

    def __init__(self) -> None:
        """Initialize CLI formatters with Rich console."""
        self._console = Console()
        self._custom_formatters: dict[
            str, type[FlextCliFormatters.FormatterProtocol]
        ] = {}

    class _ConsoleOutput:
        """Console output wrapper for tests."""

        def __init__(self, file: IO[str] | None = None) -> None:
            # Type-safe file parameter handling for Rich Console
            # Only pass file if it supports the required interface
            if file is not None and hasattr(file, "write") and hasattr(file, "flush"):
                self._console = Console(file=file)
            else:
                self._console = Console()

        def print(self, *args: object, **_kwargs: object) -> None:
            """Print to console."""
            self._console.print(*args)

    def format_data(self, data: object, format_type: str = "table") -> FlextResult[str]:
        """Format data for CLI output using Rich abstraction.

        Args:
            data: Data to format (dict, list, or other object)
            format_type: Output format ("table", "json", "yaml", "csv")

        Returns:
            FlextResult containing formatted string or error

        """
        # Allow None and other falsy values for JSON formatting - only reject undefined
        # This enables proper null value handling in JSON output

        try:
            if format_type == "table":
                return self._format_as_table(data)
            if format_type == "json":
                return self._format_as_json(data)
            if format_type == "yaml":
                return self._format_as_yaml(data)
            if format_type == "csv":
                return self._format_as_csv(data)
            if format_type == "plain":
                return self._format_as_plain(data)
            return FlextResult[str].fail(f"Unsupported format type: {format_type}")
        except Exception as e:
            return FlextResult[str].fail(f"Formatting failed: {e}")

    def _format_as_table(self, data: object) -> FlextResult[str]:
        """Format data as Rich table."""
        try:
            if isinstance(data, dict):
                # Convert dict to table format
                table_data = [[str(k), str(v)] for k, v in data.items()]
                headers = ["Key", "Value"]
            elif isinstance(data, list) and data:
                # Convert list to table format
                if isinstance(data[0], dict):
                    headers = list(data[0].keys()) if data[0] else []
                    table_data = [
                        [
                            str(row.get(h, "") if isinstance(row, dict) else "")
                            for h in headers
                        ]
                        for row in data
                    ]
                else:
                    headers = ["Value"]
                    table_data = [[str(item)] for item in data]
            else:
                # Handle other object types as single value
                headers = ["Value"]
                table_data = [[str(data)]]

            # Use tabulate for table formatting (more reliable than Rich tables)
            formatted = tabulate(table_data, headers=headers, tablefmt="grid")
            return FlextResult[str].ok(formatted)
        except Exception as e:
            return FlextResult[str].fail(f"Table formatting failed: {e}")

    def _format_as_json(self, data: object) -> FlextResult[str]:
        """Format data as JSON."""
        try:
            formatted = json.dumps(data, indent=2, default=str)
            return FlextResult[str].ok(formatted)
        except Exception as e:
            return FlextResult[str].fail(f"JSON formatting failed: {e}")

    def _format_as_yaml(self, data: object) -> FlextResult[str]:
        """Format data as YAML."""
        try:
            formatted = yaml.dump(data, default_flow_style=False, default_style=None)
            return FlextResult[str].ok(formatted)
        except Exception as e:
            return FlextResult[str].fail(f"YAML formatting failed: {e}")

    def _format_as_csv(self, data: object) -> FlextResult[str]:
        """Format data as CSV."""
        try:
            output = StringIO()
            if isinstance(data, dict):
                csv_writer = csv.writer(output)
                csv_writer.writerow(["Key", "Value"])
                for k, v in data.items():
                    csv_writer.writerow([str(k), str(v)])
            elif isinstance(data, list) and data:
                dict_writer = csv.DictWriter(
                    output,
                    fieldnames=list(data[0].keys())
                    if isinstance(data[0], dict)
                    else ["Value"],
                )
                dict_writer.writeheader()
                for row in data:
                    if isinstance(row, dict):
                        dict_writer.writerow(row)
                    else:
                        dict_writer.writerow({"Value": str(row)})
            else:
                # Handle other object types as single value CSV
                csv_writer = csv.writer(output)
                csv_writer.writerow(["Value"])
                csv_writer.writerow([str(data)])

            return FlextResult[str].ok(output.getvalue())
        except Exception as e:
            return FlextResult[str].fail(f"CSV formatting failed: {e}")

    def _format_as_plain(self, data: object) -> FlextResult[str]:
        """Format data as plain text."""
        try:
            return FlextResult[str].ok(str(data))
        except Exception as e:
            return FlextResult[str].fail(f"Plain formatting failed: {e}")

    def display_output(self, formatted_data: str) -> FlextResult[None]:
        """Display formatted data using Rich console."""
        try:
            self._console.print(formatted_data)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Display failed: {e}")

    def format_table(
        self,
        data: dict[str, object] | list[object],
        _title: str | None = None,
        **_kwargs: object,
    ) -> FlextResult[str]:
        """Format data as table (alias for format_data with table format)."""
        return self.format_data(data, "table")

    def display_message(
        self, message: str, message_type: str = "info", **_kwargs: object
    ) -> FlextResult[None]:
        """Display a message using Rich console."""
        try:
            if message_type == "error":
                self._console.print(f"[red]ERROR: {message}[/red]")
            elif message_type == "warning":
                self._console.print(f"[yellow]WARNING: {message}[/yellow]")
            elif message_type == "success":
                self._console.print(f"[green]SUCCESS: {message}[/green]")
            else:
                self._console.print(message)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Message display failed: {e}")

    def display_formatted_output(
        self, formatted_data: str, **_kwargs: object
    ) -> FlextResult[None]:
        """Display formatted output (alias for display_output)."""
        return self.display_output(formatted_data)

    def create_rich_table_object(
        self,
        data: dict[str, object] | list[object],
        title: str | None = None,
        **_kwargs: object,
    ) -> FlextResult[object]:
        """Create Rich table object and return actual Rich Table object."""
        try:
            table = RichTable(title=title)

            if isinstance(data, dict):
                # Create table from dict
                table.add_column("Key", style="cyan")
                table.add_column("Value", style="green")
                for key, value in data.items():
                    table.add_row(str(key), str(value))
            elif isinstance(data, list) and data:
                if isinstance(data[0], dict):
                    # Create table from list of dicts
                    headers = list(data[0].keys()) if data[0] else []
                    for header in headers:
                        table.add_column(str(header))
                    for row in data:
                        if isinstance(row, dict):
                            table.add_row(*[str(row.get(h, "")) for h in headers])
                else:
                    # Create table from simple list
                    table.add_column("Value")
                    for item in data:
                        table.add_row(str(item))
            else:
                return FlextResult[object].fail(
                    "Cannot create Rich table from empty data"
                )

            return FlextResult[object].ok(table)
        except Exception as e:
            return FlextResult[object].fail(f"Rich table creation failed: {e}")

    @property
    def console(self) -> Console:
        """Public access to Rich console for backward compatibility."""
        return self._console

    def print_success(self, message: str, **kwargs: object) -> FlextResult[None]:
        """Print success message with green styling."""
        return self.display_message(message, "success", **kwargs)

    def print_error(self, message: str, **kwargs: object) -> FlextResult[None]:
        """Print error message with red styling."""
        return self.display_message(message, "error", **kwargs)

    def create_formatter(
        self, format_type: str
    ) -> FlextCliFormatters.FormatterProtocol:
        """Create a formatter for the specified format type.

        Args:
            format_type: The type of formatter to create (table, json, yaml, csv, plain)

        Returns:
            A formatter object that implements the FormatterProtocol

        """
        # Check custom formatters first
        if format_type in self._custom_formatters:
            return self._custom_formatters[format_type]()

        # Built-in formatters
        if format_type == "table":
            return FlextCliFormatters.TableFormatter()
        if format_type == "json":
            return FlextCliFormatters.JSONFormatter()
        if format_type == "yaml":
            return FlextCliFormatters.YAMLFormatter()
        if format_type == "csv":
            return FlextCliFormatters.CSVFormatter()
        if format_type == "plain":
            return FlextCliFormatters.PlainFormatter()
        error_msg = f"Unsupported format type: {format_type}"
        raise ValueError(error_msg)

    def register_formatter(
        self,
        format_type: str,
        formatter_class: type[FlextCliFormatters.FormatterProtocol],
    ) -> None:
        """Register a custom formatter.

        Args:
            format_type: The format type name to register
            formatter_class: The formatter class to register

        """
        self._custom_formatters[format_type] = formatter_class

    def format_output(self, data: object, format_type: str) -> FlextResult[str]:
        """Format output using specified format type.

        Args:
            data: Data to format
            format_type: Output format type

        Returns:
            FlextResult containing formatted string

        """
        return self.format_data(data, format_type)

    def list_formats(self) -> list[str]:
        """List available format types.

        Returns:
            List of available format type names

        """
        built_in_formats = ["table", "json", "yaml", "csv", "plain"]
        custom_formats = list(self._custom_formatters.keys())
        return built_in_formats + custom_formats

    # Alias for backward compatibility with tests
    OutputFormatter = FormatterProtocol

    # Nested formatter classes following single-class-per-module architecture
    class TableFormatter(FormatterProtocol):
        """Table formatter implementation."""

        def format(self, data: object, console: Console) -> None:
            """Format data as table."""
            if isinstance(data, dict):
                table_data = [[str(k), str(v)] for k, v in data.items()]
                headers = ["Key", "Value"]
            elif isinstance(data, list) and data:
                if isinstance(data[0], dict):
                    headers = list(data[0].keys()) if data[0] else []
                    table_data = [
                        [
                            str(row.get(h, "") if isinstance(row, dict) else "")
                            for h in headers
                        ]
                        for row in data
                    ]
                else:
                    headers = ["Value"]
                    table_data = [[str(item)] for item in data]
            else:
                console.print(str(data))
                return

            formatted_table = tabulate(table_data, headers=headers, tablefmt="grid")
            console.print(formatted_table)

    class JSONFormatter(FormatterProtocol):
        """JSON formatter implementation."""

        def format(self, data: object, console: Console) -> None:
            """Format data as JSON."""
            formatted_json = json.dumps(data, indent=2, default=str)
            console.print(formatted_json)

    class YAMLFormatter(FormatterProtocol):
        """YAML formatter implementation."""

        def format(self, data: object, console: Console) -> None:
            """Format data as YAML."""
            formatted_yaml = yaml.dump(
                data, default_flow_style=False, default_style=None
            )
            console.print(formatted_yaml)

    class CSVFormatter(FormatterProtocol):
        """CSV formatter implementation."""

        def format(self, data: object, console: Console) -> None:
            """Format data as CSV."""
            output = StringIO()
            if isinstance(data, dict):
                # Treat single dict as a single record with dict keys as headers
                dict_writer = csv.DictWriter(output, fieldnames=list(data.keys()))
                dict_writer.writeheader()
                dict_writer.writerow(data)
            elif isinstance(data, list) and data:
                dict_writer = csv.DictWriter(
                    output,
                    fieldnames=list(data[0].keys())
                    if isinstance(data[0], dict)
                    else ["Value"],
                )
                dict_writer.writeheader()
                for row in data:
                    if isinstance(row, dict):
                        dict_writer.writerow(row)
                    else:
                        dict_writer.writerow({"Value": str(row)})

            formatted_csv = output.getvalue()
            console.print(formatted_csv)

    class PlainFormatter(FormatterProtocol):
        """Plain text formatter implementation."""

        def format(self, data: object, console: Console) -> None:
            """Format data as plain text."""
            if isinstance(data, dict):
                formatted_text = "\\n".join(f"{k}: {v}" for k, v in data.items())
            elif isinstance(data, list):
                # Handle list of dicts specially for readable plain text format
                if data and isinstance(data[0], dict):
                    formatted_items = []
                    for item in data:
                        if isinstance(item, dict):
                            formatted_items.append(
                                "\\n".join(f"{k}: {v}" for k, v in item.items())
                            )
                        else:
                            formatted_items.append(str(item))
                    formatted_text = "\\n".join(formatted_items)
                else:
                    formatted_text = "\\n".join(str(item) for item in data)
            else:
                formatted_text = str(data)

            console.print(formatted_text)


__all__ = [
    "FlextCliFormatters",
    "JustifyOption",
    "OverflowOption",
]
