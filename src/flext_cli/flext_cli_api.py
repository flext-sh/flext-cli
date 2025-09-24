"""FLEXT CLI API - Direct flext-core integration without over-abstraction.

Main public API for the FLEXT CLI ecosystem. Provides essential CLI functionality
by directly extending FlextService and using Rich/Click appropriately.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import yaml

from flext_cli.flext_cli_formatters import FlextCliFormatters
from flext_cli.models import FlextCliModels
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
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

        # Use FlextCliFormatters for all output (Rich abstraction)
        self._formatters = FlextCliFormatters()

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

        # Use FlextCliFormatters for output
        print_result = self._formatters.print_message(format_result.unwrap())
        if print_result.is_failure:
            return FlextResult[None].fail(print_result.error or "Print failed")
        return FlextResult[None].ok(None)

    def format_output(
        self,
        data: object,
        format_type: str = "table",
        options: FlextCliModels.FormatOptions | None = None,
    ) -> FlextResult[str]:
        """Format output data - alias for format_data for backward compatibility.

        Args:
            data: Data to format
            format_type: Format type (table, json, yaml, csv, plain)
            options: Format options

        Returns:
            FlextResult[str]: Formatted data string or error

        """
        return self.format_data(data, format_type, options)

    def display_message(
        self,
        message: str,
        message_type: str = "info",
        format_type: str = "plain",
    ) -> FlextResult[None]:
        """Display a message with specified type and format.

        Args:
            message: Message to display
            message_type: Type of message (info, warning, error, success)
            format_type: Format type for output

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            # Create message data structure
            message_data = {
                "message": message,
                "type": message_type,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            # Format and display
            format_result = self.format_data(message_data, format_type)
            if format_result.is_failure:
                return FlextResult[None].fail(
                    format_result.error or "Message formatting failed"
                )

            # Use FlextCliFormatters for styled output
            if message_type == "error":
                print_result = self._formatters.print_error(format_result.unwrap())
            elif message_type == "warning":
                print_result = self._formatters.print_warning(format_result.unwrap())
            elif message_type == "success":
                print_result = self._formatters.print_success(format_result.unwrap())
            else:
                print_result = self._formatters.print_message(format_result.unwrap())

            if print_result.is_failure:
                return FlextResult[None].fail(print_result.error or "Print failed")

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Message display failed: {e}")

    def display_output(
        self,
        data: object,
        format_type: str = "table",
        options: FlextCliModels.FormatOptions | None = None,
    ) -> FlextResult[None]:
        """Display output data - alias for display_data for backward compatibility.

        Args:
            data: Data to display
            format_type: Format type for output
            options: Format options

        Returns:
            FlextResult[None]: Success or failure result

        """
        return self.display_data(data, format_type, options)

    def create_command(
        self,
        name: str,
        description: str,
        handler: object,
        arguments: list[str] | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Create a command definition for CLI integration.

        Args:
            name: Command name
            description: Command description
            handler: Command handler function
            arguments: Command arguments list

        Returns:
            FlextResult[dict[str, object]]: Command definition or error

        """
        try:
            command_def = {
                "name": name,
                "description": description,
                "handler": handler,
                "arguments": arguments or [],
                "created_at": datetime.now(UTC).isoformat(),
            }
            return FlextResult[dict[str, object]].ok(command_def)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Command creation failed: {e}")

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
        """Format data as JSON using consolidated service."""
        from flext_cli.utils import FlextCliUtilities

        return FlextCliUtilities.Formatting.format_json(data)

    def _format_as_yaml(self, data: object) -> FlextResult[str]:
        """Format data as YAML using consolidated service."""
        from flext_cli.utils import FlextCliUtilities

        return FlextCliUtilities.Formatting.format_yaml(data)

    def _format_as_table(
        self, data: object, options: FlextCliModels.FormatOptions
    ) -> FlextResult[str]:
        """Format data as table using consolidated service."""
        from flext_cli.utils import FlextCliUtilities

        # Use the options parameter to configure table formatting
        formatted_data: dict[str, object] | object
        if options.title:
            # Add title to the data for table formatting
            formatted_data = {"title": options.title, "data": data}
        else:
            formatted_data = data

        return FlextCliUtilities.Formatting.format_table(formatted_data)

    def _format_as_csv(self, data: object) -> FlextResult[str]:
        """Format data as CSV using consolidated service."""
        from flext_cli.utils import FlextCliUtilities

        return FlextCliUtilities.Formatting.format_csv(data)

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
