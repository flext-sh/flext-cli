"""Core formatters compatibility for tests."""

from __future__ import annotations

import csv
import io
import json
from typing import TYPE_CHECKING, ClassVar

import yaml
from rich.table import Table

if TYPE_CHECKING:
    from rich.console import Console


class OutputFormatter:
    """Base class for output formatters."""

    def format(self, data: object, console: Console) -> None:
        """Format the data and print it to the console."""
        raise NotImplementedError


class TableFormatter(OutputFormatter):
    """Formats data as a table."""

    def format(self, data: object, console: Console) -> None:
        """Format data as a table."""
        table = Table()
        if isinstance(data, list) and data and isinstance(data[0], dict):
            headers = list(data[0].keys())
            for h in headers:
                table.add_column(str(h))
            for item in data:
                if isinstance(item, dict):
                    table.add_row(*(str(item.get(h, "")) for h in headers))
        elif isinstance(data, dict):
            table.add_column("Key")
            table.add_column("Value")
            for k, v in data.items():
                table.add_row(str(k), str(v))
        else:
            table.add_column("Value")
            for item in data if isinstance(data, list) else [data]:
                table.add_row(str(item))
        console.print(table)


class JSONFormatter(OutputFormatter):
    """Formats data as JSON."""

    def format(self, data: object, console: Console) -> None:
        """Format data as JSON."""
        console.print(json.dumps(data, indent=2, default=str))


class YAMLFormatter(OutputFormatter):
    """Formats data as YAML."""

    def format(self, data: object, console: Console) -> None:
        """Format data as YAML."""
        console.print(yaml.dump(data, default_flow_style=False))


class CSVFormatter(OutputFormatter):
    """Formats data as CSV."""

    def format(self, data: object, console: Console) -> None:
        """Format data as CSV."""
        output = io.StringIO()
        if isinstance(data, list) and data and isinstance(data[0], dict):
            dict_writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
            dict_writer.writeheader()
            dict_writer.writerows(data)
        elif isinstance(data, list):
            list_writer = csv.writer(output)
            for item in data:
                list_writer.writerow([str(item)])
        elif isinstance(data, dict):
            csv_writer = csv.writer(output)
            csv_writer.writerow(list(data.keys()))
            csv_writer.writerow(list(data.values()))
        else:
            single_writer = csv.writer(output)
            single_writer.writerow([str(data)])
        console.print(output.getvalue())


class PlainFormatter(OutputFormatter):
    """Formats data as plain text."""

    def format(self, data: object, console: Console) -> None:
        """Format data as plain text."""
        if isinstance(data, dict):
            for k, v in data.items():
                console.print(f"{k}: {v}")
        elif isinstance(data, list):
            for item in data:
                console.print(str(item))
        else:
            console.print(str(data))


class FormatterFactory:
    """Factory for creating output formatters."""

    _registry: ClassVar[dict[str, type[OutputFormatter]]] = {
        "table": TableFormatter,
        "json": JSONFormatter,
        "yaml": YAMLFormatter,
        "csv": CSVFormatter,
        "plain": PlainFormatter,
    }

    @classmethod
    def create(cls, name: str) -> OutputFormatter:
        """Create a formatter by name."""
        try:
            return cls._registry[name]()
        except KeyError as e:
            msg = "Unknown formatter type"
            raise ValueError(msg) from e

    @classmethod
    def register(cls, name: str, formatter_cls: type[OutputFormatter]) -> None:
        """Register a new formatter."""
        cls._registry[name] = formatter_cls

    @classmethod
    def list_formats(cls) -> list[str]:
        """List available formats."""
        return list(cls._registry.keys())


def format_output(data: object, format_name: str, console: Console) -> None:
    """Format and print data using a named formatter."""
    formatter = FormatterFactory.create(format_name)
    formatter.format(data, console)
