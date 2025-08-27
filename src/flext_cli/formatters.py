"""FLEXT CLI Formatters - CONSOLIDATED Pattern following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import csv
import io
from typing import ClassVar, cast, override

import yaml
from flext_core import FlextUtilities
from rich.console import Console
from rich.table import Table


class FlextCliFormatters:
    """Single CONSOLIDATED class containing ALL CLI formatters.

    Consolidates ALL formatter definitions into one class following FLEXT patterns.
    Individual formatters available as nested classes for organization.
    Maintains backward compatibility through direct exports.
    """

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
            """Format data as JSON using FlextUtilities."""
            console.print(FlextUtilities.safe_json_stringify(data))

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
            else:
                output.write(str(data))

            console.print(output.getvalue())
            output.close()

    class PlainFormatter(OutputFormatter):
        """Formats data as plain text."""

        @override
        def format(self, data: object, console: Console) -> None:
            """Format data as plain text."""
            if isinstance(data, dict):
                for key, value in data.items():
                    console.print(f"{key}: {value}")
            elif isinstance(data, list):
                for item in data:
                    console.print(str(item))
            else:
                console.print(str(data))


# =============================================================================
# FORMATTER FACTORY - Simple factory pattern
# =============================================================================


class FormatterFactory:
    """Factory for creating output formatters."""

    _registry: ClassVar[dict[str, type[FlextCliFormatters.OutputFormatter]]] = {
        "table": FlextCliFormatters.TableFormatter,
        "json": FlextCliFormatters.JSONFormatter,
        "yaml": FlextCliFormatters.YAMLFormatter,
        "csv": FlextCliFormatters.CSVFormatter,
        "plain": FlextCliFormatters.PlainFormatter,
    }

    @classmethod
    def create(cls, name: str) -> FlextCliFormatters.OutputFormatter:
        """Create a formatter by name."""
        try:
            return cls._registry[name]()
        except KeyError as e:
            msg = "Unknown formatter type"
            raise ValueError(msg) from e

    @classmethod
    def register(
        cls, name: str, formatter_cls: type[FlextCliFormatters.OutputFormatter]
    ) -> None:
        """Register a new formatter."""
        cls._registry[name] = formatter_cls

    @classmethod
    def list_formats(cls) -> list[str]:
        """List available formats."""
        return list(cls._registry.keys())


# =============================================================================
# CONVENIENCE FUNCTIONS - Simple API for common use cases
# =============================================================================


def format_output(data: object, format_name: str, console: Console) -> None:
    """Format and print data using a named formatter."""
    formatter = FormatterFactory.create(format_name)
    formatter.format(data, console)


def create_formatter(format_name: str) -> FlextCliFormatters.OutputFormatter:
    """Create a formatter by name."""
    return FormatterFactory.create(format_name)


# =============================================================================
# EXPORTS - Comprehensive formatter system
# =============================================================================

# Export formatters from FlextCliFormatters namespace
OutputFormatter = FlextCliFormatters.OutputFormatter
PlainFormatter = FlextCliFormatters.PlainFormatter
CSVFormatter = FlextCliFormatters.CSVFormatter
JSONFormatter = FlextCliFormatters.JSONFormatter
TableFormatter = FlextCliFormatters.TableFormatter
YAMLFormatter = FlextCliFormatters.YAMLFormatter

__all__ = [
    "CSVFormatter",
    "FlextCliFormatters",
    "FormatterFactory",
    "JSONFormatter",
    "OutputFormatter",
    "PlainFormatter",
    "TableFormatter",
    "YAMLFormatter",
    "create_formatter",
    "format_output",
]
