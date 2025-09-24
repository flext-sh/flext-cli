"""FLEXT CLI API - Direct flext-core integration without over-abstraction.

Main public API for the FLEXT CLI ecosystem. Provides essential CLI functionality
by directly extending FlextService and using Rich/Click appropriately.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from flext_cli.auth import FlextCliAuth
from flext_cli.commands import FlextCliCommands
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.models import FlextCliModels
from flext_cli.output import FlextCliOutput
from flext_cli.prompts import FlextCliPrompts
from flext_cli.utilities import FlextCliUtilities
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)


class FlextCliApi(FlextService[FlextTypes.Core.Dict]):
    """Main CLI API tools.

    Renamed from FlextCliApi for PEP 8 compliance.
    Provides essential CLI functionality for the FLEXT ecosystem.
    """

    def __init__(self) -> None:
        """Initialize FlextCliApi with direct flext-core integration."""
        super().__init__()
        self._logger: FlextLogger = FlextLogger(__name__)
        self._container: FlextContainer = FlextContainer.get_global()

        # Initialize all CLI tools for unified access
        self._output: FlextCliOutput = FlextCliOutput()
        self._files: FlextCliFileTools = FlextCliFileTools()
        self._commands: FlextCliCommands = FlextCliCommands()
        self._auth: FlextCliAuth = FlextCliAuth()
        self._prompts: FlextCliPrompts = FlextCliPrompts()
        self._utils: FlextCliUtilities = FlextCliUtilities()

        self._logger.info("FlextCliApi initialized with direct flext-core integration")

    @property
    def output(self) -> FlextCliOutput:
        """Get output formatter."""
        return self._output

    @property
    def files(self) -> FlextCliFileTools:
        """Get file tools."""
        return self._files

    @property
    def commands(self) -> FlextCliCommands:
        """Get commands handler."""
        return self._commands

    @property
    def auth(self) -> FlextCliAuth:
        """Get auth handler."""
        return self._auth

    @property
    def prompts(self) -> FlextCliPrompts:
        """Get prompts handler."""
        return self._prompts

    @property
    def utils(self) -> FlextCliUtilities:
        """Get utilities handler."""
        return self._utils

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
                return self._output.format_json(data)
            case "yaml":
                return self._output.format_yaml(data)
            case "table":
                # Handle different data types for table formatting
                if isinstance(data, dict):
                    return self._output.format_table(
                        cast("dict[str, object]", data), title=options.title
                    )
                if isinstance(data, list):
                    if data and isinstance(data[0], dict):
                        # List of dictionaries - perfect for table
                        return self._output.format_table(
                            cast("list[dict[str, object]]", data), title=options.title
                        )
                    # Simple list - convert to list of dicts with index
                    indexed_data: list[dict[str, object]] = [
                        {"Index": i, "Value": str(item)}
                        for i, item in enumerate(cast("list[object]", data))
                    ]
                    return self._output.format_table(indexed_data, title=options.title)
                # Single value - convert to dict format
                single_data: list[dict[str, object]] = [
                    {"Key": "Value", "Value": str(data)}
                ]
                return self._output.format_table(single_data, title=options.title)
            case "csv":
                return self._output.format_csv(data)
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

        formatted_str = str(format_result.unwrap())
        print_result = self._output.print_message(formatted_str)
        if print_result.is_failure:
            return FlextResult[None].fail(print_result.error or "Print failed")
        return FlextResult[None].ok(None)

    def export_data(
        self,
        data: object,
        output_path: object,
        format_type: str = "json",
    ) -> FlextResult[None]:
        """Export data to a file.

        Args:
            data: Data to export
            output_path: Path to output file
            format_type: Format type for export

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            path = Path(str(output_path))
            # Check if parent directory exists before creating
            if not path.parent.exists():
                return FlextResult[None].fail("No such file or directory")
            path.parent.mkdir(parents=True, exist_ok=True)

            format_result = self.format_data(data, format_type)
            if format_result.is_failure:
                return FlextResult[None].fail(format_result.error or "Format failed")

            path.write_text(format_result.unwrap(), encoding="utf-8")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Export failed: {e}")

    def batch_export(
        self,
        datasets: dict[str, object],
        output_dir: object,
        format_type: str = "json",
    ) -> FlextResult[dict[str, bool]]:
        """Export multiple datasets to files.

        Args:
            datasets: Dictionary of dataset names to data
            output_dir: Directory to export files to
            format_type: Format type for export

        Returns:
            FlextResult[dict[str, bool]]: Results for each dataset

        """
        try:
            output_path = Path(str(output_dir))
            output_path.mkdir(parents=True, exist_ok=True)

            results: dict[str, bool] = {}

            for name, data in datasets.items():
                file_path = output_path / f"{name}.{format_type}"
                export_result = self.export_data(data, file_path, format_type)
                results[name] = export_result.is_success

            return FlextResult[dict[str, bool]].ok(results)

        except Exception as e:
            return FlextResult[dict[str, bool]].fail(f"Batch export failed: {e}")

    def display_message(
        self,
        message: str,
        message_type: str = "info",
    ) -> FlextResult[None]:
        """Display a message with specified type.

        Args:
            message: Message to display
            message_type: Type of message (info, warning, error, success)

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            if message_type == "error":
                print_result = self._output.print_error(message)
            elif message_type == "warning":
                print_result = self._output.print_warning(message)
            elif message_type == "success":
                print_result = self._output.print_success(message)
            else:
                print_result = self._output.print_message(message)

            if print_result.is_failure:
                return FlextResult[None].fail(print_result.error or "Print failed")

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Message display failed: {e}")

    def create_command(
        self,
        name: str,
        description: str,
        handler: object,
        arguments: list[str] | None = None,
    ) -> FlextResult[FlextTypes.Core.Dict]:
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
            return FlextResult[FlextTypes.Core.Dict].ok(command_def)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Command creation failed: {e}"
            )


__all__ = [
    "FlextCliApi",
]
