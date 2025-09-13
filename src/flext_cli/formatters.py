"""FLEXT CLI Formatters - Output formatting utilities following flext-core patterns.

Provides comprehensive output formatting for CLI applications including table,
JSON, YAML, and CSV formats with Rich integration for enhanced terminal display.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import re
import sys
from collections.abc import Callable
from io import StringIO
from typing import ClassVar, Protocol, TextIO, runtime_checkable

import yaml
from flext_core import FlextResult, FlextTypes, FlextUtilities

# Rich functionality replaced with flext-core compatible output


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
        """Minimal console output abstraction replacing Rich Console."""

        def __init__(self, file: TextIO | None = None) -> None:
            """Initialize the instance."""
            self.file = file or sys.stdout

        def print(self, text: str) -> None:
            """Print text to console with optional styling stripped."""
            # Remove Rich markup patterns like [bold green], [/bold green]
            clean_text = re.sub(r"\[/?[^\]]*\]", "", str(text))
            print(clean_text, file=self.file)

        def out(self, text: str) -> None:
            """Output raw text."""
            self.file.write(str(text))
            self.file.flush()

    @runtime_checkable
    class OutputFormatter(Protocol):
        """Protocol for formatter classes used by the CLI."""

        def format(
            self, data: object, console: FlextCliFormatters._ConsoleOutput
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
        console: _ConsoleOutput | None = None,
        default_format: str = "table",
    ) -> None:
        """Initialize formatters with console and default format.

        Args:
            console: Console output instance for output
            default_format: Default output format to use

        """
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
        """Internal table formatter implementation."""

        def format(
            self, data: object, console: FlextCliFormatters._ConsoleOutput
        ) -> None:
            # Simple text-based table formatting
            if isinstance(data, list) and data and isinstance(data[0], dict):
                # Table with headers from dict keys
                headers = list(data[0].keys())
                console.print(" | ".join(str(h) for h in headers))
                console.print(
                    "-" * (sum(len(str(h)) for h in headers) + 3 * (len(headers) - 1))
                )
                for row in data:
                    console.print(" | ".join(str(row.get(k, "")) for k in headers))
            elif isinstance(data, dict):
                # Key-value table
                console.print("Key | Value")
                console.print("-" * 20)
                for k, v in data.items():
                    console.print(f"{k} | {v}")
            else:
                # Single column table
                console.print("Value")
                console.print("-" * 10)
                if isinstance(data, list):
                    for item in data:
                        console.print(str(item))
                else:
                    console.print(str(data))

    class _JSONFormatter:
        """Internal JSON formatter implementation."""

        def format(
            self, data: object, console: FlextCliFormatters._ConsoleOutput
        ) -> None:
            try:
                formatted = FlextUtilities.safe_json_stringify(data)
                console.out(formatted)
            except (TypeError, ValueError, RuntimeError) as e:
                console.print(f"JSON formatting failed: {e}")
                console.print(f"Data (as string): {data}")

    class _YAMLFormatter:
        """Internal YAML formatter implementation."""

        def format(
            self, data: object, console: FlextCliFormatters._ConsoleOutput
        ) -> None:
            formatted = yaml.safe_dump(data, default_flow_style=False)
            console.print(formatted)

    class _CSVFormatter:
        """Internal CSV formatter implementation."""

        def __init__(self, formatters_instance: FlextCliFormatters) -> None:
            """Initialize with reference to parent formatters instance."""
            self._formatters = formatters_instance

        def format(
            self, data: object, console: FlextCliFormatters._ConsoleOutput
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
            self, data: object, console: FlextCliFormatters._ConsoleOutput
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

    def list_formats(self) -> FlextTypes.Core.StringList:
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
        self,
        data: object,
        title: str | None = None,
    ) -> FlextResult[str]:
        """Format data as text table using flext-core patterns.

        Args:
            data: Data to format as table
            title: Optional table title

        Returns:
            FlextResult[str]: Formatted table string or error

        """
        try:
            # Use the table formatter to generate text output
            string_buffer = StringIO()
            temp_console = self._ConsoleOutput(file=string_buffer)

            # Add title if provided
            if title:
                temp_console.print(f"=== {title} ===")
                temp_console.print("")

            # Format based on data type
            formatter = self._TableFormatter()
            formatter.format(data, temp_console)

            result = string_buffer.getvalue().rstrip("\n")
            return FlextResult[str].ok(result)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[str].fail(f"Table format failed: {e}")

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
        """Print success message with styling.

        Args:
            message: Success message to display

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            self.console.print(f"✓ {message}")
            return FlextResult[None].ok(None)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[None].fail(f"Print success failed: {e}")

    def print_error(self, message: str) -> FlextResult[None]:
        """Print error message with styling.

        Args:
            message: Error message to display

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            self.console.print(f"✗ {message}")
            return FlextResult[None].ok(None)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[None].fail(f"Print error failed: {e}")

    def print_warning(self, message: str) -> FlextResult[None]:
        """Print warning message with styling.

        Args:
            message: Warning message to display

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            self.console.print(f"⚠ {message}")
            return FlextResult[None].ok(None)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[None].fail(f"Print warning failed: {e}")


__all__ = [
    "FlextCliFormatters",
]
