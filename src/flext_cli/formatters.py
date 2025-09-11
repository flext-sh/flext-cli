"""FLEXT CLI Formatters - Consolidated output formatting and display.

Provides FlextCliFormatters class for comprehensive output formatting operations
including table, JSON, YAML, CSV, and plain text formats following flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import csv
from collections.abc import Callable
from io import StringIO
from typing import ClassVar, Protocol, runtime_checkable

import yaml
from flext_core import FlextResult, FlextTypes, FlextUtilities
from rich.console import Console
from rich.table import Table


class FlextCliFormatters:
    """Consolidated output formatting following flext-core patterns.

    Provides comprehensive formatting operations including table, JSON, YAML, CSV,
    and plain text formats with FlextResult error handling and Rich integration.
    Unified class containing ALL formatter functionality including protocols.

    Features:
        - Multiple output formats (table, JSON, YAML, CSV, plain)
        - Rich table formatting with auto-detection
        - Type-safe formatting with FlextResult
        - Protocol-based formatter registry
        - Console output management
        - Error handling and validation
    """

    @runtime_checkable
    class OutputFormatter(Protocol):
        """Protocol for formatter classes used by the CLI."""

        def format(self, data: object, console: Console) -> None: ...

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
        console: Console | None = None,
        default_format: str = "table",
    ) -> None:
        """Initialize formatters with console and default format.

        Args:
            console: Rich console instance for output
            default_format: Default output format to use

        """
        self.console = console or Console()
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

        def format(self, data: object, console: Console) -> None:
            table = Table(title="Data")
            if isinstance(data, list) and data and isinstance(data[0], dict):
                # Add columns from dict keys
                for key in data[0]:
                    table.add_column(str(key))
                for row in data:
                    table.add_row(*[str(row.get(k, "")) for k in data[0]])
            elif isinstance(data, dict):
                table.add_column("Key")
                table.add_column("Value")
                for k, v in data.items():
                    table.add_row(str(k), str(v))
            else:
                table.add_column("Value")
                if isinstance(data, list):
                    for item in data:
                        table.add_row(str(item))
                else:
                    table.add_row(str(data))
            console.print(table)

    class _JSONFormatter:
        """Internal JSON formatter implementation."""

        def format(self, data: object, console: Console) -> None:
            try:
                formatted = FlextUtilities.safe_json_stringify(data)
                console.print(formatted)
            except (TypeError, ValueError, RuntimeError) as e:
                console.print(f"[red]JSON formatting failed:[/red] {e}")
                console.print(f"Data (as string): {data}")

    class _YAMLFormatter:
        """Internal YAML formatter implementation."""

        def format(self, data: object, console: Console) -> None:
            formatted = yaml.safe_dump(data, default_flow_style=False)
            console.print(formatted)

    class _CSVFormatter:
        """Internal CSV formatter implementation."""

        def __init__(self, formatters_instance: FlextCliFormatters) -> None:
            """Initialize with reference to parent formatters instance."""
            self._formatters = formatters_instance

        def format(self, data: object, console: Console) -> None:
            """Format data as CSV using the consolidated CSV implementation."""
            result = self._formatters.format_csv(data)
            if result.is_success:
                console.print(result.value)
            else:
                raise ValueError(result.error)

    class _PlainFormatter:
        """Internal plain text formatter implementation."""

        def format(self, data: object, console: Console) -> None:
            if isinstance(data, dict):
                for k, v in data.items():
                    console.print(f"{k}: {v}")
            elif isinstance(data, list):
                for v in data:
                    if isinstance(v, dict):
                        for k, val in v.items():
                            console.print(f"{k}: {val}")
                        console.print()  # Empty line between dict entries
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
            msg = f"Unknown formatter type: {name}"
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
            # Capture output using StringIO
            string_buffer = StringIO()
            temp_console = Console(file=string_buffer, width=120)
            formatter = self.create_formatter(format_type)
            formatter.format(data, temp_console)

            result = string_buffer.getvalue()
            return FlextResult[str].ok(result)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[str].fail(f"Format data failed: {e}")

    def format_table(
        self,
        data: object,
        title: str | None = None,
    ) -> FlextResult[Table]:
        """Format data as Rich Table using FlextPipeline and match-case patterns.

        Args:
            data: Data to format as table
            title: Optional table title

        Returns:
            FlextResult[Table]: Rich Table object or error

        """

        def create_base_table() -> FlextResult[Table]:
            """Create base table with title."""
            return FlextResult[Table].ok(Table(title=title or "Data"))

        def populate_table_by_type(table: Table) -> FlextResult[Table]:
            """Populate table based on data type using Python 3.13+ match-case."""
            match data:
                case list() if data and isinstance(data[0], dict):
                    return self._populate_dict_list_table(table, data)
                case dict():
                    return self._populate_dict_table(table, data)
                case list():
                    return self._populate_list_table(table, data)
                case _:
                    return self._populate_scalar_table(table, data)

        base_result = create_base_table()
        if base_result.is_failure:
            return base_result

        return populate_table_by_type(base_result.value)

    def _populate_dict_list_table(
        self,
        table: Table,
        data: list[FlextTypes.Core.Dict],
    ) -> FlextResult[Table]:
        """Populate table with list of dictionaries."""
        try:
            # Add columns from first dictionary keys
            for key in data[0]:
                table.add_column(str(key))

            # Add rows from all dictionaries
            for row in data:
                table.add_row(*[str(row.get(k, "")) for k in data[0]])

            return FlextResult[Table].ok(table)
        except (IndexError, KeyError) as e:
            return FlextResult[Table].fail(f"Failed to populate dict list table: {e}")

    def _populate_dict_table(
        self,
        table: Table,
        data: FlextTypes.Core.Dict,
    ) -> FlextResult[Table]:
        """Populate table with single dictionary."""
        try:
            table.add_column("Key")
            table.add_column("Value")

            for k, v in data.items():
                table.add_row(str(k), str(v))

            return FlextResult[Table].ok(table)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[Table].fail(f"Failed to populate dict table: {e}")

    def _populate_list_table(
        self,
        table: Table,
        data: FlextTypes.Core.List,
    ) -> FlextResult[Table]:
        """Populate table with list of items."""
        try:
            table.add_column("Value")

            for item in data:
                table.add_row(str(item))

            return FlextResult[Table].ok(table)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[Table].fail(f"Failed to populate list table: {e}")

    def _populate_scalar_table(self, table: Table, data: object) -> FlextResult[Table]:
        """Populate table with scalar value."""
        try:
            table.add_column("Value")
            table.add_row(str(data))

            return FlextResult[Table].ok(table)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[Table].fail(f"Failed to populate scalar table: {e}")

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
                    plain_writer = csv.writer(output)
                    if isinstance(data, list):
                        for item in data:
                            plain_writer.writerow([str(item)])
                    else:
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
            self.console.print(f"[bold green]✓[/bold green] {message}")
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
            self.console.print(f"[bold red]✗[/bold red] {message}")
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
            self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")
            return FlextResult[None].ok(None)
        except (ImportError, AttributeError, ValueError) as e:
            return FlextResult[None].fail(f"Print warning failed: {e}")


__all__ = [
    "FlextCliFormatters",
]
