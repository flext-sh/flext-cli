"""Output formatters for FLEXT CLI framework.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Built on flext-core foundation with Rich integration.
Provides multiple output formats for CLI commands.
"""

from __future__ import annotations

import csv
import io
import json
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any

import yaml
from rich.table import Table

if TYPE_CHECKING:
    from rich.console import Console


class OutputFormatter(ABC):
    """Base class for output formatters."""

    @abstractmethod
    def format(self, data: Any, console: Console) -> None:
        """Format data and output to console."""
        ...


class TableFormatter(OutputFormatter):
    """Format output as a Rich table."""

    def format(self, data: Any, console: Console) -> None:
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

    def format(self, data: Any, console: Console) -> None:
        """Format data as JSON."""
        console.print(json.dumps(data, indent=2, default=str))


class YAMLFormatter(OutputFormatter):
    """Format output as YAML."""

    def format(self, data: Any, console: Console) -> None:
        """Format data as YAML."""
        console.print(yaml.dump(data, default_flow_style=False, sort_keys=False))


class CSVFormatter(OutputFormatter):
    """Format output as CSV."""

    def format(self, data: Any, console: Console) -> None:
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

    def format(self, data: Any, console: Console) -> None:
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

    _formatters: dict[str, type[OutputFormatter]] = {
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
            msg = f"Unsupported format type: {format_type}"
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


def format_output(data: Any, format_type: str, console: Console) -> None:
    """Format and output data using specified formatter."""
    formatter = FormatterFactory.create(format_type)
    formatter.format(data, console)
