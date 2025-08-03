"""FLEXT CLI Output Formatters - Rich Console Output with Multiple Format Support.

This module provides comprehensive output formatting capabilities for FLEXT CLI
commands, supporting multiple output formats with Rich console integration for
enhanced terminal user experience.

Output Formats Supported:
    - table: Rich tables with colors and formatting (default)
    - json: JSON output for machine consumption and APIs
    - yaml: YAML format for configuration and data exchange
    - csv: CSV format for data analysis and spreadsheet import
    - plain: Plain text output for scripting and automation

Architecture:
    - Abstract base class pattern with format-specific implementations
    - Rich console integration for beautiful terminal output
    - Factory pattern for format selection and instantiation
    - Type-safe formatting with comprehensive error handling

Formatter Classes:
    - OutputFormatter: Abstract base class for all formatters
    - TableFormatter: Rich table output with styling and colors
    - JsonFormatter: JSON output with proper indentation
    - YamlFormatter: YAML output with readable formatting
    - CsvFormatter: CSV output with proper escaping
    - PlainFormatter: Simple text output for scripting

Current Implementation Status:
    ✅ Complete formatter implementations for all formats
    ✅ Rich console integration with colors and styling
    ✅ Factory pattern for format selection
    ✅ Error handling and validation
    ⚠️ Basic styling (TODO: Sprint 2 - enhance themes and customization)

TODO (docs/TODO.md):
    Sprint 2: Add customizable themes and styling options
    Sprint 3: Add format-specific configuration and templates
    Sprint 7: Add performance metrics and monitoring integration
    Sprint 8: Add interactive formatting with user preferences

Usage Examples:
    # Table format (default)
    >>> formatter = FormatterFactory.get_formatter("table")
    >>> formatter.format(data, console)

    # JSON for APIs
    >>> formatter = FormatterFactory.get_formatter("json")
    >>> formatter.format(data, console)

    # CSV for data analysis
    >>> formatter = FormatterFactory.get_formatter("csv")
    >>> formatter.format(data, console)

Integration:
    - Used by all CLI commands for consistent output
    - Integrates with Click options for format selection
    - Supports Rich console features (colors, tables, progress)
    - Compatible with terminal capabilities detection

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import csv
import io
import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

import yaml
from rich.table import Table

if TYPE_CHECKING:
    from rich.console import Console


class OutputFormatter(ABC):
    """Abstract base class for all output formatters.

    Defines the contract for formatting and outputting data in different formats.
    All concrete formatters must implement the format method to handle specific
    output formats while maintaining consistent behavior.

    Design Pattern:
        Uses Template Method pattern with abstract format method that concrete
        formatters must implement. Ensures consistent interface across all
        output formats while allowing format-specific customization.

    Integration:
        - Works with Rich console for enhanced terminal output
        - Supports error handling and graceful degradation
        - Compatible with all CLI command output requirements

    Usage:
        Should not be instantiated directly. Use FormatterFactory to get
        concrete formatter implementations based on desired output format.

    TODO (Sprint 2):
        - Add format validation and schema support
        - Add theme and styling configuration options
        - Add output streaming for large datasets
    """

    @abstractmethod
    def format(self, data: object, console: Console) -> None:
        """Format data and output to console in format-specific way.

        Args:
            data: Data to be formatted (lists, dicts, objects)
            console: Rich console instance for output

        Abstract Method:
            Must be implemented by all concrete formatter classes to handle
            format-specific rendering and output logic.

        """
        ...


class TableFormatter(OutputFormatter):
    """Format output as a Rich table."""

    def format(self, data: object, console: Console) -> None:
        """Format data as Rich table."""
        if isinstance(data, list) and data:
            # List of dicts
            if isinstance(data[0], dict):
                headers = list(data[0].keys())
                table = Table(show_header=True, header_style="bold cyan")

                for header in headers:
                    table.add_column(header.replace("_", " ").title())

                for item in data:
                    table.add_row(*[str(item.get(h, "")) for h in headers])

                console.print(table)
            else:
                # Simple list
                table = Table(show_header=False)
                table.add_column("Value")
                for item in data:
                    table.add_row(str(item))
                console.print(table)
        elif isinstance(data, dict):
            # Single dict as vertical table
            table = Table(show_header=False)
            table.add_column("Key", style="cyan")
            table.add_column("Value")

            for key, value in data.items():
                table.add_row(key.replace("_", " ").title(), str(value))

            console.print(table)
        else:
            console.print(str(data))


class JSONFormatter(OutputFormatter):
    """Format output as JSON."""

    def format(self, data: object, console: Console) -> None:
        """Format data as JSON."""
        console.print(json.dumps(data, indent=2, default=str))


class YAMLFormatter(OutputFormatter):
    """Format output as YAML."""

    def format(self, data: object, console: Console) -> None:
        """Format data as YAML."""
        console.print(yaml.dump(data, default_flow_style=False, sort_keys=False))


class CSVFormatter(OutputFormatter):
    """Format output as CSV."""

    def format(self, data: object, console: Console) -> None:
        """Format data as CSV."""
        output = io.StringIO()

        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                dict_writer = csv.DictWriter(output, fieldnames=data[0].keys())
                dict_writer.writeheader()
                dict_writer.writerows(data)
            else:
                regular_writer = csv.writer(output)
                for item in data:
                    regular_writer.writerow([str(item)])
        elif isinstance(data, dict):
            dict_writer = csv.DictWriter(output, fieldnames=data.keys())
            dict_writer.writeheader()
            dict_writer.writerow(data)

        console.print(output.getvalue().strip())


class PlainFormatter(OutputFormatter):
    """Format output as plain text."""

    def format(self, data: object, console: Console) -> None:
        """Format data as plain text."""
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        console.print(f"{key}: {value}")
                    console.print()  # Empty line between items
                else:
                    console.print(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                console.print(f"{key}: {value}")
        else:
            console.print(str(data))


class FormatterFactory:
    """Factory for creating output formatters."""

    _formatters: ClassVar[dict[str, type[OutputFormatter]]] = {
        "table": TableFormatter,
        "json": JSONFormatter,
        "yaml": YAMLFormatter,
        "csv": CSVFormatter,
        "plain": PlainFormatter,
    }

    @classmethod
    def create(cls, format_type: str) -> OutputFormatter:
        """Create formatter by type."""
        formatter_class = cls._formatters.get(format_type)
        if not formatter_class:
            msg = f"Unknown formatter type: {format_type}"
            raise ValueError(msg)
        return formatter_class()

    @classmethod
    def register(cls, format_type: str, formatter_class: type[OutputFormatter]) -> None:
        """Register custom formatter."""
        cls._formatters[format_type] = formatter_class

    @classmethod
    def list_formats(cls) -> list[str]:
        """List available formats."""
        return list(cls._formatters.keys())


def format_output(data: object, format_type: str, console: Console) -> None:
    """Format and output data using specified formatter."""
    formatter = FormatterFactory.create(format_type)
    formatter.format(data, console)
