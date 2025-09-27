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
from typing import override

import yaml

from flext_cli.auth import FlextCliAuth
from flext_cli.commands import FlextCliCommands
from flext_cli.constants import FlextCliConstants
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

    @override
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

    @override
    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute the main domain service operation - required by FlextService."""
        return FlextResult[FlextTypes.Core.Dict].ok({
            "status": FlextCliConstants.OPERATIONAL,
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
                    # Convert object values to supported types
                    converted_data: dict[str, object] = {
                        k: v
                        if isinstance(v, (str, int, float, bool)) or v is None
                        else str(v)
                        for k, v in data.items()
                    }
                    return self._output.format_table(
                        converted_data, title=options.title
                    )
                if isinstance(data, list):
                    if data and isinstance(data[0], dict):
                        # List of dictionaries - convert to supported types
                        converted_list_data: list[dict[str, object]] = [
                            {
                                k: v
                                if isinstance(v, (str, int, float, bool)) or v is None
                                else str(v)
                                for k, v in item.items()
                            }
                            for item in data
                        ]
                        return self._output.format_table(
                            converted_list_data, title=options.title
                        )
                    # Simple list - convert to list of dicts with index
                    indexed_data: list[dict[str, object]] = [
                        {"Index": i, "Value": str(item)} for i, item in enumerate(data)
                    ]
                    return self._output.format_table(indexed_data, title=options.title)
                # Single value - convert to dict format
                single_data: list[dict[str, object]] = [
                    {"Key": FlextCliConstants.VALUE, "Value": str(data)}
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

    # Convenience methods for backward compatibility with tests
    def format_output(
        self, data: object, format_type: str = "table"
    ) -> FlextResult[str]:
        """Format output using specified format type (alias for format_data)."""
        return self.format_data(data, format_type)

    def display_output(self, output: str) -> FlextResult[None]:
        """Display output string."""
        try:
            # Use proper output handling instead of print
            self._output.display_text(output)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Display failed: {e}")

    def create_progress_bar(
        self,
        task_name: str,
        total: int = 100,
        *,
        show_percentage: bool = True,
        show_eta: bool = True,
    ) -> FlextResult[object]:
        """Create progress bar."""
        try:
            # Mock progress bar object
            progress_bar = {
                "task": task_name,
                "total": total,
                "current": 0,
                "show_percentage": show_percentage,
                "show_eta": show_eta,
            }
            return FlextResult[object].ok(progress_bar)
        except Exception as e:
            return FlextResult[object].fail(f"Progress bar creation failed: {e}")

    def update_progress_bar(
        self, progress_bar: object, increment: int = 1
    ) -> FlextResult[None]:
        """Update progress bar."""
        try:
            # Mock progress bar update
            if isinstance(progress_bar, dict):
                progress_bar["current"] = min(
                    progress_bar.get("current", 0) + increment,
                    progress_bar.get("total", 100),
                )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Progress bar update failed: {e}")

    def close_progress_bar(self, progress_bar: object) -> FlextResult[None]:
        """Close progress bar."""
        try:
            # Mock progress bar close - log the progress bar for debugging
            if hasattr(progress_bar, "__dict__"):
                self._logger.debug(f"Closing progress bar: {progress_bar}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Progress bar close failed: {e}")

    def read_file(self, file_path: str) -> FlextResult[str]:
        """Read file content."""
        return self._files.read_text_file(file_path)

    def write_file(self, file_path: str, content: str) -> FlextResult[bool]:
        """Write content to file."""
        return self._files.write_text_file(file_path, content)

    def copy_file(self, source_path: str, destination_path: str) -> FlextResult[bool]:
        """Copy file from source to destination."""
        return self._files.copy_file(source_path, destination_path)

    def move_file(self, source_path: str, destination_path: str) -> FlextResult[bool]:
        """Move file from source to destination."""
        return self._files.move_file(source_path, destination_path)

    def delete_file(self, file_path: str) -> FlextResult[bool]:
        """Delete file."""
        return self._files.delete_file(file_path)

    def list_files(self, directory_path: str) -> FlextResult[list[str]]:
        """List files in directory."""
        return self._files.list_directory(directory_path)

    def execute_command(self, command: str, timeout: int = 30) -> FlextResult[object]:
        """Execute shell command with timeout support."""
        return self._commands.execute_command(command, None, timeout)

    def make_http_request(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        data: str | None = None,
    ) -> FlextResult[str]:
        """Make HTTP request."""
        return self._commands.make_http_request(url, method, headers, data)

    def make_http_request_get(
        self, url: str, headers: dict[str, str] | None = None
    ) -> FlextResult[str]:
        """Make HTTP GET request."""
        return self.make_http_request(url, "GET", headers)

    def make_http_request_post(
        self, url: str, data: str, headers: dict[str, str] | None = None
    ) -> FlextResult[str]:
        """Make HTTP POST request."""
        return self.make_http_request(url, "POST", headers, data)

    def make_http_request_with_headers(
        self, url: str, headers: dict[str, str]
    ) -> FlextResult[str]:
        """Make HTTP request with headers."""
        return self.make_http_request(url, "GET", headers)

    def make_http_request_invalid_url(self, url: str) -> FlextResult[str]:
        """Make HTTP request to invalid URL (for testing)."""
        return self.make_http_request(url)

    def parse_json(self, json_data: str) -> FlextResult[dict[str, object]]:
        """Parse JSON data."""
        try:
            parsed = json.loads(json_data)
            return FlextResult[dict[str, object]].ok(parsed)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"JSON parsing failed: {e}")

    def parse_yaml(self, yaml_data: str) -> FlextResult[dict[str, object]]:
        """Parse YAML data."""
        try:
            parsed = yaml.safe_load(yaml_data)
            return FlextResult[dict[str, object]].ok(parsed)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"YAML parsing failed: {e}")

    def serialize_json(self, data: object) -> FlextResult[str]:
        """Serialize data to JSON."""
        try:
            serialized = json.dumps(data, indent=2)
            return FlextResult[str].ok(serialized)
        except Exception as e:
            return FlextResult[str].fail(f"JSON serialization failed: {e}")

    def serialize_yaml(self, data: object) -> FlextResult[str]:
        """Serialize data to YAML."""
        try:
            serialized = yaml.dump(data, default_flow_style=False)
            return FlextResult[str].ok(serialized)
        except Exception as e:
            return FlextResult[str].fail(f"YAML serialization failed: {e}")

    def prompt_user(
        self, question: str, default: str | None = None
    ) -> FlextResult[str]:
        """Prompt user for input."""
        return self._prompts.prompt(question, default=default)

    def confirm_action(self, message: str) -> FlextResult[bool]:
        """Confirm action with user."""
        return self._prompts.confirm(message)

    def select_option(
        self, options: list[str], message: str = "Select an option:"
    ) -> FlextResult[str]:
        """Let user select from options."""
        try:
            if not options:
                return FlextResult[str].fail("No options provided")

            # Use the prompts service for proper user selection
            return self._prompts.select_from_options(options, message)
        except Exception as e:
            return FlextResult[str].fail(f"Selection failed: {e}")

    def load_config(self, config_path: str) -> FlextResult[dict[str, object]]:
        """Load configuration from file."""
        return self._files.read_json_file(config_path)

    def save_config(
        self, config_path: str, config: dict[str, object]
    ) -> FlextResult[bool]:
        """Save configuration to file."""
        return self._files.write_json_file(config_path, config)

    def validate_config_dict(self, config: dict[str, object]) -> FlextResult[bool]:
        """Validate configuration."""
        try:
            # Check if it's a dict
            if not isinstance(config, dict):
                return FlextResult[bool].fail("Config must be a dictionary")

            # Validate specific fields
            if "debug" in config and not isinstance(config["debug"], bool):
                return FlextResult[bool].fail("debug must be a boolean")

            if "timeout" in config:
                timeout = config["timeout"]
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    return FlextResult[bool].fail("timeout must be a positive number")

            if "retries" in config:
                retries = config["retries"]
                if not isinstance(retries, int) or retries < 0:
                    return FlextResult[bool].fail(
                        "retries must be a non-negative integer"
                    )

            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Config validation failed: {e}")

    async def execute_async(self) -> FlextResult[dict[str, object]]:
        """Execute API service operation asynchronously."""
        return FlextResult[dict[str, object]].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": "flext-cli-api",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
            "components": {
                "output": FlextCliConstants.AVAILABLE,
                "files": FlextCliConstants.AVAILABLE,
                "commands": FlextCliConstants.AVAILABLE,
                "auth": FlextCliConstants.AVAILABLE,
                "prompts": FlextCliConstants.AVAILABLE,
                "utils": FlextCliConstants.AVAILABLE,
            },
        })


__all__ = [
    "FlextCliApi",
]
