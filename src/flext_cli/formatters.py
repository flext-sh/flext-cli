"""Core formatters.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import csv
import io
import json
from typing import ClassVar, cast, override

import yaml
from rich.console import Console
from rich.table import Table


class OutputFormatter:
    """Base class for output formatters."""

    def format(self, data: object, console: Console) -> None:
        """Format the data and print it to the console."""
        raise NotImplementedError


class TableFormatter(OutputFormatter):
    """Formats data as a table."""

    @override
    def format(self, data: object, console: Console) -> None:
        """Format data as a table."""
        table = Table()
        if isinstance(data, list) and data:
            first_item = cast("object", data[0])
            if isinstance(first_item, dict):
                # Type-safe dict handling for table headers
                first_dict_raw = cast("dict[object, object]", first_item)
                first_dict: dict[str, object] = {
                    str(k): v for k, v in first_dict_raw.items()
                }
                headers: list[str] = list(first_dict.keys())
                for header_str in headers:
                    table.add_column(header_str)

                # Type-safe list iteration for table rows
                data_list = cast("list[object]", data)
                for item in data_list:
                    if isinstance(item, dict):
                        # Type-safe dict access for row values
                        item_dict_raw = cast("dict[object, object]", item)
                        item_dict: dict[str, object] = {
                            str(k): v for k, v in item_dict_raw.items()
                        }
                        row_values = [str(item_dict.get(h, "")) for h in headers]
                        table.add_row(*row_values)
        elif isinstance(data, dict):
            table.add_column("Key")
            table.add_column("Value")
            data_dict = cast("dict[object, object]", data)
            for k, v in data_dict.items():
                table.add_row(str(k), str(v))
        else:
            table.add_column("Value")
            if isinstance(data, list):
                list_data = cast("list[object]", data)
                for list_item in list_data:
                    table.add_row(str(list_item))
            else:
                table.add_row(str(data))
        console.print(table)


class JSONFormatter(OutputFormatter):
    """Formats data as JSON."""

    @override
    def format(self, data: object, console: Console) -> None:
        """Format data as JSON."""
        console.print(json.dumps(data, indent=2, default=str))


class YAMLFormatter(OutputFormatter):
    """Formats data as YAML."""

    @override
    def format(self, data: object, console: Console) -> None:
        """Format data as YAML."""
        console.print(yaml.dump(data, default_flow_style=False))


class CSVFormatter(OutputFormatter):
    """Formats data as CSV."""

    @override
    def format(self, data: object, console: Console) -> None:
        """Format data as CSV."""
        output = io.StringIO()
        if isinstance(data, list) and data:
            first_item = cast("object", data[0])
            if isinstance(first_item, dict):
                first_dict = cast("dict[object, object]", first_item)
                fieldnames: list[str] = [str(k) for k in first_dict]
                dict_writer = csv.DictWriter(output, fieldnames=fieldnames)
                dict_writer.writeheader()

                # Convert all dict items for CSV writing
                csv_rows: list[dict[str, object]] = []
                data_list = cast("list[object]", data)
                for item in data_list:
                    if isinstance(item, dict):
                        item_dict = cast("dict[object, object]", item)
                        str_dict: dict[str, object] = {
                            str(k): v for k, v in item_dict.items()
                        }
                        csv_rows.append(str_dict)
                dict_writer.writerows(csv_rows)
        elif isinstance(data, list):
            list_writer = csv.writer(output)
            list_data = cast("list[object]", data)
            for item in list_data:
                list_writer.writerow([str(item)])
        elif isinstance(data, dict):
            csv_writer = csv.writer(output)
            data_dict = cast("dict[object, object]", data)
            keys_list: list[str] = [str(k) for k in data_dict]
            values_list: list[str] = [str(v) for v in data_dict.values()]
            csv_writer.writerow(keys_list)
            csv_writer.writerow(values_list)
        else:
            single_writer = csv.writer(output)
            single_writer.writerow([str(data)])
        console.print(output.getvalue())


class PlainFormatter(OutputFormatter):
    """Formats data as plain text."""

    @override
    def format(self, data: object, console: Console) -> None:
        """Format data as plain text."""
        if isinstance(data, dict):
            data_dict = cast("dict[object, object]", data)
            for k, v in data_dict.items():
                console.print(f"{k}: {v}")
        elif isinstance(data, list):
            plain_list = cast("list[object]", data)
            if plain_list:
                first_item = plain_list[0]
                if isinstance(first_item, dict):
                    # Print each dict item as key: value lines to satisfy tests
                    for item in plain_list:
                        if isinstance(item, dict):
                            item_dict = cast("dict[object, object]", item)
                            for k, v in item_dict.items():
                                console.print(f"{k}: {v}")
                else:
                    for item in plain_list:
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
