"""FLEXT CLI API - Direct flext-core integration without over-abstraction.

Main public API for the FLEXT CLI ecosystem. Provides essential CLI functionality
by directly extending FlextService and using Rich/Click appropriately.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from typing import cast

import yaml
from rich.console import Console
from rich.table import Table

from flext_cli.models import FlextCliModels
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
    FlextUtilities,
)


class FlextCliApi(FlextService[dict[str, object]]):
    """Main CLI API - direct flext-core extension without abstraction layers.

    This class provides the essential CLI functionality for the FLEXT ecosystem
    by directly extending FlextService and using Rich/Click where appropriate.
    NO delegation to unified services or over-abstracted patterns.
    """

    def __init__(self) -> None:
        """Initialize FlextCliApi with direct flext-core integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()

        # Direct Rich usage for CLI output
        self._console = Console()

        self._logger.info("FlextCliApi initialized with direct flext-core integration")

    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute the main domain service operation - required by FlextService."""
        return FlextResult[FlextTypes.Core.Dict].ok({
            "status": "operational",
            "service": "flext-cli-api",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
        })

    def format_data(
        self,
        data: object,
        format_type: str = "table",
        options: FlextCliModels.FormatOptions | None = None,
    ) -> FlextResult[str]:
        """Format data using specified format type.

        Args:
            data: Data to format
            format_type: Format type (table, json, yaml, csv, plain)
            options: Format options

        Returns:
            FlextResult[str]: Formatted data string or error

        """
        if options is None:
            options = FlextCliModels.FormatOptions()

        match format_type.lower():
            case "json":
                return self._format_as_json(data)
            case "yaml":
                return self._format_as_yaml(data)
            case "table":
                return self._format_as_table(data, options)
            case "csv":
                return self._format_as_csv(data)
            case "plain":
                return FlextResult[str].ok(str(data))
            case _:
                return FlextResult[str].fail(f"Unsupported format type: {format_type}")

    def display_data(
        self,
        data: object,
        format_type: str = "table",
        options: FlextCliModels.FormatOptions | None = None,
    ) -> FlextResult[None]:
        """Format and display data in one operation.

        Args:
            data: Data to display
            format_type: Format type for output
            options: Format options

        Returns:
            FlextResult[None]: Success or failure result

        """
        format_result = self.format_data(data, format_type, options)
        if format_result.is_failure:
            return FlextResult[None].fail(
                format_result.error or "Format operation failed"
            )

        # Direct console output using Rich
        self._console.print(format_result.unwrap())
        return FlextResult[None].ok(None)

    def export_data(
        self, data: object, file_path: Path, format_type: str = "json"
    ) -> FlextResult[None]:
        """Export data to file.

        Args:
            data: Data to export
            file_path: Target file path
            format_type: Export format (json, yaml)

        Returns:
            FlextResult[None]: Success or failure result

        """
        match format_type.lower():
            case "json":
                return self._export_as_json(data, file_path)
            case "yaml":
                return self._export_as_yaml(data, file_path)
            case _:
                return FlextResult[None].fail(
                    f"Unsupported export format: {format_type}"
                )

    def batch_export(
        self, datasets: dict[str, object], output_dir: Path, format_type: str = "json"
    ) -> FlextResult[None]:
        """Export multiple datasets to files.

        Args:
            datasets: Dictionary of name -> data mappings
            output_dir: Output directory
            format_type: Export format

        Returns:
            FlextResult[None]: Success or failure result

        """
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        for name, data in datasets.items():
            file_path = output_dir / f"{name}.{format_type}"
            export_result = self.export_data(data, file_path, format_type)
            if export_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to export {name}: {export_result.error}"
                )

        return FlextResult[None].ok(None)

    # Private formatting methods using direct Rich/standard library

    def _format_as_json(self, data: object) -> FlextResult[str]:
        """Format data as JSON."""
        return FlextResult[str].safe_call(
            lambda: json.dumps(data, indent=2, default=str)
        )

    def _format_as_yaml(self, data: object) -> FlextResult[str]:
        """Format data as YAML."""
        return FlextResult[str].safe_call(
            lambda: yaml.dump(data, default_flow_style=False)
        )

    def _format_as_table(
        self, data: object, options: FlextCliModels.FormatOptions
    ) -> FlextResult[str]:
        """Format data as table using Rich directly."""
        if data is None:
            return FlextResult[str].ok("No data to display")

        # Use FlextUtilities to convert to table format
        table_data_result = FlextUtilities.Conversion.to_table_format(data)
        if table_data_result.is_failure:
            return FlextResult[str].fail(
                f"Cannot convert to table format: {table_data_result.error}"
            )

        table_data = table_data_result.value
        if not table_data:
            return FlextResult[str].ok("No data to display")

        # Create Rich table directly
        table = Table(title=options.title)

        # Add columns
        headers = options.headers or list(table_data[0].keys())
        for header in headers:
            table.add_column(str(header))

        # Add rows
        for row_data in table_data:
            row_values = [str(row_data.get(h, "")) for h in headers]
            table.add_row(*row_values)

        # Capture Rich output as string
        string_buffer = StringIO()
        console = Console(file=string_buffer, width=options.max_width)
        console.print(table)
        return FlextResult[str].ok(string_buffer.getvalue())

    def _format_as_csv(self, data: object) -> FlextResult[str]:
        """Format data as CSV."""
        if not isinstance(data, list):
            return FlextResult[str].fail("CSV format requires list of dictionaries")

        if not data:
            return FlextResult[str].ok("")

        # Type narrowing: verify all items are dicts
        list_data = cast("list[object]", data)
        if not all(isinstance(item, dict) for item in list_data):
            return FlextResult[str].fail("CSV format requires list of dictionaries")

        try:
            output = StringIO()
            # Type narrowing: data is list and all items are dicts
            csv_data = cast("list[dict[str, object]]", list_data)
            writer = csv.DictWriter(output, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
            return FlextResult[str].ok(output.getvalue())
        except Exception as e:
            return FlextResult[str].fail(f"CSV formatting failed: {e}")

    def _export_as_json(self, data: object, file_path: Path) -> FlextResult[None]:
        """Export data as JSON file."""
        try:
            self._write_json_file(data, file_path)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"JSON export failed: {e}")

    def _export_as_yaml(self, data: object, file_path: Path) -> FlextResult[None]:
        """Export data as YAML file."""
        try:
            self._write_yaml_file(data, file_path)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"YAML export failed: {e}")

    def _write_json_file(self, data: object, file_path: Path) -> None:
        """Write data to JSON file."""
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def _write_yaml_file(self, data: object, file_path: Path) -> None:
        """Write data to YAML file."""
        with file_path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False)


__all__ = [
    "FlextCliApi",
]
