"""FLEXT CLI Formatters - Production-ready output formatting utilities.

Provides comprehensive output formatting for CLI applications including table,
JSON, YAML, and CSV formats with Rich integration for enhanced terminal display.
Uses direct imports and standardized architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import io
import json
import sys
from typing import (
    IO,
    Protocol,
)

import yaml
from pydantic import BaseModel, ConfigDict, PrivateAttr
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from tabulate import tabulate

from flext_core import FlextResult

# JustifyOption = Literal["default", "left", "center", "right", "full"]
# OverflowOption = Literal["fold", "crop", "ellipsis", "ignore"]

# Constants
KEY_VALUE_PAIR_COLUMNS = 2


class FlextCliFormatters(BaseModel):
    """Unified CLI formatting service using Rich internally with comprehensive output support.

    ZERO TOLERANCE COMPLIANCE:
    - Single unified class with nested formatter classes
    - NO duplication of Rich functionality
    - Comprehensive format support: table, JSON, YAML, CSV, plain text
    - Explicit error handling with FlextResult
    - Professional CLI formatting standards
    """

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )

    class FormatterProtocol(Protocol):
        """Protocol for output formatters."""

        def format(
            self, data: object, console: Console | FlextCliFormatters._ConsoleOutput,
        ) -> None:
            """Format data to console output."""
            ...

    class _ConsoleOutput:
        """Simplified console output for testing and CLI operations."""

        def __init__(self, file: IO[str] | None = None) -> None:
            self.file = file or sys.stdout
            self.captured_output: list[str] = []

        def print(self, *args: object, **kwargs: object) -> None:
            """Print to output with optional capture."""
            output = " ".join(str(arg) for arg in args)
            self.captured_output.append(output)
            # Use explicit type casting for print parameters
            sep_val = kwargs.get("sep", " ")
            end_val = kwargs.get("end", "\n")
            flush_val = kwargs.get("flush", False)

            sep_val if isinstance(sep_val, (str, type(None))) else " "
            end = end_val if isinstance(end_val, (str, type(None))) else "\n"
            flush = flush_val if isinstance(flush_val, bool) else False

            print(output, end=end, file=self.file, flush=flush)

    # Private attributes for Rich console and custom formatters
    _console: Console = PrivateAttr(default_factory=Console)
    _custom_formatters: dict[str, type[FormatterProtocol]] = PrivateAttr(
        default_factory=dict,
    )

    def __init__(self, **data: object) -> None:
        """Initialize formatters with Rich console."""
        super().__init__(**data)
        self._console = Console()
        self._custom_formatters = {}

    def execute(self) -> FlextResult[str]:
        """Execute formatter service - required by FlextModels.Entity interface."""
        return FlextResult[str].ok("FlextCliFormatters service ready")

    def create_table(
        self,
        data: object,
        *,
        headers: list[str] | None = None,
        title: str | None = None,
        show_header: bool = True,
        show_lines: bool = False,
        caption: str | None = None,
    ) -> FlextResult[Table]:
        """Create Rich table with comprehensive styling options."""
        try:
            table = Table(
                title=title,
                caption=caption,
                show_header=show_header,
                show_lines=show_lines,
                header_style="bold magenta",
                border_style="blue",
            )

            # Handle different data types
            if isinstance(data, dict):
                # Dictionary format
                if headers:
                    for header in headers:
                        table.add_column(header, style="cyan", no_wrap=False)
                else:
                    table.add_column("Key", style="cyan", no_wrap=False)
                    table.add_column("Value", style="green", no_wrap=False)

                if headers and len(headers) == KEY_VALUE_PAIR_COLUMNS:
                    # Key-value pairs
                    for key, value in data.items():
                        table.add_row(str(key), str(value))
                else:
                    # Single column or multi-column data
                    table.add_row(*[str(data.get(h, "")) for h in (headers or [])])

            elif isinstance(data, list) and data:
                # List format
                if isinstance(data[0], dict):
                    # List of dictionaries
                    if headers is None:
                        headers = list(data[0].keys()) if data[0] else []

                    for header in headers:
                        table.add_column(header, style="cyan", no_wrap=False)

                    for item in data:
                        if isinstance(item, dict):
                            row_data = [str(item.get(h, "")) for h in headers]
                            table.add_row(*row_data)
                        else:
                            table.add_row(str(item))
                else:
                    # List of simple values
                    table.add_column("Value", style="cyan", no_wrap=False)
                    for item in data:
                        table.add_row(str(item))
            else:
                # Single value or other types
                table.add_column("Value", style="cyan", no_wrap=False)
                table.add_row(str(data))

            return FlextResult[Table].ok(table)

        except Exception as e:
            return FlextResult[Table].fail(f"Table creation failed: {e}")

    def format_data(self, data: object, format_type: str) -> FlextResult[str]:
        """Format data using specified format type."""
        try:
            formatter = self.create_formatter(format_type)
            console_output = FlextCliFormatters._ConsoleOutput()
            formatter.format(data, console_output)
            return FlextResult[str].ok("\n".join(console_output.captured_output))

        except Exception as e:
            return FlextResult[str].fail(f"Data formatting failed: {e}")

    def display_table(
        self,
        data: object,
        *,
        headers: list[str] | None = None,
        title: str | None = None,
        **kwargs: object,
    ) -> FlextResult[None]:
        """Display table using Rich console."""
        try:
            # Extract create_table parameters with explicit type casting
            show_header_val = kwargs.get("show_header", True)
            show_lines_val = kwargs.get("show_lines", False)
            caption_val = kwargs.get("caption")

            show_header = show_header_val if isinstance(show_header_val, bool) else True
            show_lines = show_lines_val if isinstance(show_lines_val, bool) else False
            caption = caption_val if isinstance(caption_val, (str, type(None))) else None

            table_result = self.create_table(
                data,
                headers=headers,
                title=title,
                show_header=show_header,
                show_lines=show_lines,
                caption=caption,
            )
            if table_result.is_failure:
                return FlextResult[None].fail(
                    f"Table creation failed: {table_result.error}",
                )

            self._console.print(table_result.value)
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Table display failed: {e}")

    def display_json(self, data: object, *, indent: int = 2) -> FlextResult[None]:
        """Display JSON with syntax highlighting."""
        try:
            json_str = json.dumps(data, indent=indent, default=str, ensure_ascii=False)
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
            self._console.print(syntax)
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"JSON display failed: {e}")

    def display_message(
        self, message: str, style: str = "default", **kwargs: object,
    ) -> FlextResult[None]:
        """Display styled message.

        Args:
            message: Message to display
            style: Style name (success, error, warning, info, default)
            **kwargs: Additional parameters (currently ignored for Rich console compatibility)

        """
        try:
            style_map = {
                "success": "bold green",
                "error": "bold red",
                "warning": "bold yellow",
                "info": "bold blue",
                "default": "default",
            }
            rich_style = style_map.get(style, "default")

            # Rich console.print has strict parameter types - pass only style to avoid type issues
            # kwargs are intentionally ignored to maintain API compatibility while ensuring type safety
            _ = kwargs  # Acknowledge kwargs parameter to avoid linting warnings
            self._console.print(message, style=rich_style)
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Message display failed: {e}")

    @property
    def console(self) -> Console:
        """Public access to Rich console."""
        return self._console

    def print_success(self, message: str, **kwargs: object) -> FlextResult[None]:
        """Print success message with green styling."""
        return self.display_message(message, "success", **kwargs)

    def print_error(self, message: str, **kwargs: object) -> FlextResult[None]:
        """Print error message with red styling."""
        return self.display_message(message, "error", **kwargs)

    def create_formatter(
        self, format_type: str,
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

    # Nested formatter classes following single-class-per-module architecture
    class TableFormatter(FormatterProtocol):
        """Table formatter implementation."""

        def format(
            self, data: object, console: Console | FlextCliFormatters._ConsoleOutput,
        ) -> None:
            """Format data as table."""
            if isinstance(data, dict):
                table_data = [[str(k), str(v)] for k, v in data.items()]
                headers = ["Key", "Value"]
            elif isinstance(data, list) and data:
                if isinstance(data[0], dict):
                    headers = list(data[0].keys()) if data[0] else []
                    table_data = [
                        [str(item.get(h, "")) for h in headers] for item in data
                    ]
                else:
                    headers = ["Value"]
                    table_data = [[str(item)] for item in data]
            else:
                headers = ["Value"]
                table_data = [[str(data)]]

            # Use tabulate for consistent table formatting
            try:
                formatted_table = tabulate(table_data, headers=headers, tablefmt="grid")
                console.print(formatted_table)
            except ImportError:
                # Fallback if tabulate is not available
                for header in headers:
                    console.print(f"{header:20}", end=" ")
                console.print()
                console.print("-" * (20 * len(headers)))
                for row in table_data:
                    for cell in row:
                        console.print(f"{cell!s:20}", end=" ")
                    console.print()

    class JSONFormatter(FormatterProtocol):
        """JSON formatter implementation."""

        def format(
            self, data: object, console: Console | FlextCliFormatters._ConsoleOutput,
        ) -> None:
            """Format data as JSON."""
            try:
                json_output = json.dumps(
                    data, indent=2, default=str, ensure_ascii=False,
                )
                console.print(json_output)
            except Exception as e:
                console.print(f"JSON formatting error: {e}")

    class YAMLFormatter(FormatterProtocol):
        """YAML formatter implementation."""

        def format(
            self, data: object, console: Console | FlextCliFormatters._ConsoleOutput,
        ) -> None:
            """Format data as YAML."""
            try:
                yaml_output = yaml.dump(
                    data, default_flow_style=False, allow_unicode=True,
                )
                console.print(yaml_output)
            except ImportError:
                console.print("YAML library not available, falling back to JSON")
                FlextCliFormatters.JSONFormatter().format(data, console)
            except Exception as e:
                console.print(f"YAML formatting error: {e}")

    class CSVFormatter(FormatterProtocol):
        """CSV formatter implementation."""

        def format(
            self, data: object, console: Console | FlextCliFormatters._ConsoleOutput,
        ) -> None:
            """Format data as CSV."""
            try:
                output = io.StringIO()
                if isinstance(data, dict):
                    # Convert dict to list of rows
                    writer = csv.writer(output)
                    writer.writerow(["Key", "Value"])
                    for key, value in data.items():
                        writer.writerow([str(key), str(value)])
                elif isinstance(data, list) and data:
                    writer = csv.writer(output)
                    if isinstance(data[0], dict):
                        # List of dicts
                        headers = list(data[0].keys()) if data[0] else []
                        writer.writerow(headers)
                        for item in data:
                            if isinstance(item, dict):
                                writer.writerow([str(item.get(h, "")) for h in headers])
                    else:
                        # List of values
                        writer.writerow(["Value"])
                        for item in data:
                            writer.writerow([str(item)])
                else:
                    # Single value
                    writer = csv.writer(output)
                    writer.writerow(["Value"])
                    writer.writerow([str(data)])

                console.print(output.getvalue())
            except Exception as e:
                console.print(f"CSV formatting error: {e}")

    class PlainFormatter(FormatterProtocol):
        """Plain text formatter implementation."""

        def format(
            self, data: object, console: Console | FlextCliFormatters._ConsoleOutput,
        ) -> None:
            """Format data as plain text."""
            try:
                if isinstance(data, dict):
                    for key, value in data.items():
                        console.print(f"{key}: {value}")
                elif isinstance(data, list):
                    for item in data:
                        console.print(str(item))
                else:
                    console.print(str(data))
            except Exception as e:
                console.print(f"Plain formatting error: {e}")


__all__ = [
    "FlextCliFormatters",
]
