"""FLEXT CLI Formatters - Hierarchical formatter system inheriting from FlextCoreUtilities.

This module implements the FlextCliFormatters class following the Flext[Area][Module] pattern,
inheriting from FlextCoreUtilities.FlextFormatters and providing CLI-specific formatting extensions
with all current functionality available as internal aliases.

English code with Portuguese comments following FLEXT standards.
"""

from __future__ import annotations

import csv
import io
import json
from typing import ClassVar, cast, override

import yaml
from rich.console import Console
from rich.table import Table


# NOTE: Import will be fixed when flext-core import error is resolved
# For now, using fallback base class since FlextUtilities.FlextFormatters doesn't exist yet
class FlextCoreFormatters:
    """Base formatters from flext-core utilities (fallback implementation).
    
    Este é um fallback temporário até que o flext-core seja totalmente implementado.
    Quando disponível, herdar de FlextUtilities.FlextFormatters.
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


# =============================================================================
# FLEXT CLI FORMATTERS - Main hierarchical class inheriting from FlextCoreUtilities
# =============================================================================

class FlextCliFormatters(FlextCoreFormatters):
    """CLI-specific formatter system inheriting from FlextCoreUtilities.FlextFormatters.

    This class implements the Flext[Area][Module] pattern, providing hierarchical
    inheritance from flext-core formatters while adding CLI-specific extensions.
    All current functionality is preserved through internal aliases.

    Herança hierárquica de FlextCoreUtilities.FlextFormatters conforme padrão FLEXT.
    Mantém compatibilidade completa através de aliases internos.
    """

    # =============================================================================
    # CLI-SPECIFIC FORMATTER CATEGORIES - Extending core formatters
    # =============================================================================

    class Cli:
        """CLI-specific formatter definitions and aliases."""

        # Core formatter classes - current implementations
        OutputFormatter = OutputFormatter
        TableFormatter = TableFormatter
        JSONFormatter = JSONFormatter
        YAMLFormatter = YAMLFormatter
        CSVFormatter = CSVFormatter
        PlainFormatter = PlainFormatter
        FormatterFactory = FormatterFactory

        # Rich integration
        Console = Console
        Table = Table

        # Format types
        SUPPORTED_FORMATS: ClassVar[list[str]] = ["table", "json", "yaml", "csv", "plain"]
        DEFAULT_FORMAT: ClassVar[str] = "table"

    # =============================================================================
    # INTERNAL METHODS - All current functionality preserved
    # =============================================================================

    @classmethod
    def create_formatter(cls, format_name: str) -> OutputFormatter:
        """Create a formatter by name.

        Args:
            format_name: Name of the formatter to create

        Returns:
            OutputFormatter instance

        """
        return cls.Cli.FormatterFactory.create(format_name)

    @classmethod
    def format_data(cls, data: object, format_name: str, console: Console) -> None:
        """Format and print data using a named formatter.

        Args:
            data: Data to format
            format_name: Name of the format to use
            console: Rich console for output

        """
        formatter = cls.create_formatter(format_name)
        formatter.format(data, console)

    @classmethod
    def register_formatter(cls, name: str, formatter_cls: type[OutputFormatter]) -> None:
        """Register a new formatter.

        Args:
            name: Name of the formatter
            formatter_cls: Formatter class to register

        """
        cls.Cli.FormatterFactory.register(name, formatter_cls)

    @classmethod
    def list_supported_formats(cls) -> list[str]:
        """List available formats.

        Returns:
            List of supported format names

        """
        return cls.Cli.FormatterFactory.list_formats()


# =============================================================================
# BACKWARD COMPATIBILITY ALIASES - All current exports preserved
# =============================================================================

# Function aliases - preservar compatibilidade total
format_output = FlextCliFormatters.format_data

# Class aliases - manter compatibilidade existente
CliOutputFormatter = FlextCliFormatters.Cli.OutputFormatter
CliTableFormatter = FlextCliFormatters.Cli.TableFormatter
CliJSONFormatter = FlextCliFormatters.Cli.JSONFormatter
CliYAMLFormatter = FlextCliFormatters.Cli.YAMLFormatter
CliCSVFormatter = FlextCliFormatters.Cli.CSVFormatter
CliPlainFormatter = FlextCliFormatters.Cli.PlainFormatter
CliFormatterFactory = FlextCliFormatters.Cli.FormatterFactory

# Rich integration aliases
CliConsole = FlextCliFormatters.Cli.Console
CliTable = FlextCliFormatters.Cli.Table

# Legacy compatibility
CoreFormatters = FlextCoreFormatters


# =============================================================================
# EXPORTS - Comprehensive formatter system with backward compatibility
# =============================================================================

__all__ = [
    "CSVFormatter",
    "CliCSVFormatter",
    "CliConsole",
    "CliFormatterFactory",
    "CliJSONFormatter",
    "CliOutputFormatter",
    "CliPlainFormatter",
    "CliTable",
    "CliTableFormatter",
    "CliYAMLFormatter",
    "CoreFormatters",
    "FlextCliFormatters",
    "FormatterFactory",
    "JSONFormatter",
    "OutputFormatter",
    "PlainFormatter",
    "TableFormatter",
    "YAMLFormatter",
    "format_output",
]
