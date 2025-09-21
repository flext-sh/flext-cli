"""FLEXT CLI API - Unified single-class implementation.

Uses Python 3.13 cutting-edge patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_cli.unified_service import get_unified_cli_service
from flext_core import (
    FlextDomainService,
    FlextLogger,
    FlextResult,
    FlextTypes,
)


class FlextCliApi(FlextDomainService[FlextTypes.Core.Dict]):
    """Unified CLI API service - simplified through advanced flext-core patterns.

    This class now serves as a lightweight facade over the FlextCliUnifiedService,
    which uses advanced flext-core features for consolidation and complexity reduction.
    """

    def __init__(self) -> None:
        """Initialize FlextCliApi using unified service backend."""
        super().__init__()
        self._logger = FlextLogger(__name__)

        # Use the unified service from flext-core container

        self._unified_service = get_unified_cli_service()

    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute the main domain service operation - required by FlextDomainService.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Health status of the unified service.

        """
        return self._unified_service.get_health_status()

    def execute_command(
        self, command: str = "", **kwargs: object
    ) -> FlextResult[FlextTypes.Core.Dict | str]:
        """Execute CLI operation using railway pattern.

        Returns:
            FlextResult[FlextTypes.Core.Dict | str]: Result of command execution or formatted data.

        """

        def handle_format_command(data: object, format_type: str) -> FlextResult[str]:
            """Handle format command with monadic composition.

            Returns:
                FlextResult[str]: Formatted data result.

            """
            return self._unified_service.format_data(data, format_type)

        # Railway pattern for format command
        if command == "format":
            data = kwargs.get("data")
            format_type = str(kwargs.get("format_type", "table"))
            if data is not None:
                return (
                    FlextResult[object]
                    .ok(data)
                    .flat_map(lambda d: handle_format_command(d, format_type))
                    .map(lambda result: result)  # Cast to union type
                )

        # Default execution - direct delegation
        return (
            self._unified_service.execute().map(
                lambda result: result
            )  # Cast to union type
        )

    def format_output(
        self,
        data: object,
        format_type: str = "table",
        **options: object,
    ) -> FlextResult[str]:
        """Format data using unified service - reduced complexity.

        Returns:
            FlextResult[str]: Formatted data string or error result.

        """
        return self._unified_service.format_data(data, format_type, **options)

    def display_output(self, formatted_data: str) -> FlextResult[None]:
        """Display formatted data using unified service.

        Returns:
            FlextResult[None]: Success or failure result of display operation.

        """
        return self._unified_service.display_output(formatted_data)

    def display_message(
        self, message: str, style: str = "", prefix: str = ""
    ) -> FlextResult[None]:
        """Display formatted message with optional styling.

        Returns:
            FlextResult[None]: Success or failure result of message display operation.

        """
        return self._unified_service.display_message(message, style, prefix)

    def create_command(
        self,
        command_line: str,
        **options: object,
    ) -> FlextResult[dict[str, object]]:
        """Create CLI command using unified service.

        Returns:
            FlextResult[dict[str, object]]: Created command metadata or error result.

        """
        return self._unified_service.create_command(command_line, **options)

    def get_health_status(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get API health status using monadic composition.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Health status data or error result.

        """
        return self._unified_service.get_health_status()

    def export_data(
        self, data: object, file_path: object, format_type: str = "json"
    ) -> FlextResult[None]:
        """Export data using unified service with railway pattern validation.

        Returns:
            FlextResult[None]: Success or failure result of export operation.

        """

        def validate_path(path_obj: object) -> FlextResult[Path]:
            """Validate file path parameter.

            Returns:
                FlextResult[Path]: Validated Path object or error result.

            """
            if not isinstance(path_obj, Path):
                return FlextResult[Path].fail("file_path must be a Path object")
            return FlextResult[Path].ok(path_obj)

        def perform_export(validated_path: Path) -> FlextResult[None]:
            """Perform the actual export operation.

            Returns:
                FlextResult[None]: Success or failure result of export operation.

            """
            return self._unified_service.export_data(data, validated_path, format_type)

        return validate_path(file_path).flat_map(perform_export)

    def batch_export(
        self, datasets: object, output_dir: object, format_type: str = "json"
    ) -> FlextResult[None]:
        """Export multiple datasets using unified service with railway pattern validation.

        Returns:
            FlextResult[None]: Success or failure result of batch export operation.

        """

        def validate_output_dir(dir_obj: object) -> FlextResult[Path]:
            """Validate output directory parameter.

            Returns:
                FlextResult[Path]: Validated Path object or error result.

            """
            if not isinstance(dir_obj, Path):
                return FlextResult[Path].fail("output_dir must be a Path object")
            return FlextResult[Path].ok(dir_obj)

        def validate_datasets(datasets_obj: object) -> FlextResult[dict[str, object]]:
            """Validate datasets parameter.

            Returns:
                FlextResult[dict[str, object]]: Validated datasets or error result.

            """
            if not isinstance(datasets_obj, dict):
                return FlextResult[dict[str, object]].fail(
                    "datasets must be a dictionary"
                )
            return FlextResult[dict[str, object]].ok(datasets_obj)

        def perform_batch_export(validated_dir: Path) -> FlextResult[None]:
            """Perform the actual batch export operation.

            Returns:
                FlextResult[None]: Success or failure result of batch export operation.

            """
            return validate_datasets(datasets).flat_map(
                lambda valid_datasets: self._unified_service.batch_export(
                    valid_datasets, validated_dir, format_type
                )
            )

        return validate_output_dir(output_dir).flat_map(perform_batch_export)

    def format_and_display(
        self, data: object, format_type: str = "table", **options: object
    ) -> FlextResult[None]:
        """Format and display data in one operation using unified service.

        Returns:
            FlextResult[None]: Success or failure result of format and display operation.

        """
        return self._unified_service.format_and_display(data, format_type, **options)

    # Simplified convenience methods (much less code than before)
    def format_data(self, data: object, format_type: str) -> FlextResult[str]:
        """Format data - delegates to unified service.

        Returns:
            FlextResult[str]: Formatted data string or error result.

        """
        return self._unified_service.format_data(data, format_type)

    def create_table(
        self, data: object, title: str | None = None, **options: object
    ) -> FlextResult[str]:
        """Create table - delegates to unified service.

        Returns:
            FlextResult[str]: Formatted table string or error result.

        """
        table_options = options.copy()
        if title:
            table_options["title"] = title
        return self._unified_service.format_data(data, "table", **table_options)

    def get_command_history(self) -> FlextResult[list[dict[str, object]]]:
        """Get command history using unified service.

        Returns:
            FlextResult[list[dict[str, object]]]: Command history list or error result.

        """
        return self._unified_service.get_command_history()

    # Legacy compatibility methods (simplified)
    def execute_with_command(
        self, command: str | None = None, **kwargs: object
    ) -> FlextResult[object | str]:
        """Execute CLI operation with command using railway pattern composition.

        Returns:
            FlextResult[object | str]: Success or failure result of command execution.

        """

        def handle_format_command(
            cmd_data: object, fmt_type: str
        ) -> FlextResult[object | str]:
            """Handle format command with railway pattern.

            Returns:
                FlextResult[object | str]: Formatted data or error result.

            """
            if cmd_data is None:
                return FlextResult[object | str].fail("No data provided for formatting")

            return (
                self._unified_service.format_data(cmd_data, fmt_type).map(
                    lambda result: result
                )  # Cast to union type
            )

        def execute_default_operation() -> FlextResult[object | str]:
            """Execute default operation.

            Returns:
                FlextResult[object | str]: Default operational status or error result.

            """
            return FlextResult[object | str].ok({"status": "operational"})

        def execute_command_with_args(cmd: str) -> FlextResult[object | str]:
            """Execute specific command with arguments.

            Returns:
                FlextResult[object | str]: Command execution result or error result.

            """
            if cmd == "format":
                data = kwargs.get("data")
                format_type = str(kwargs.get("format_type", "json"))
                return handle_format_command(data, format_type)

            return FlextResult[object | str].ok({
                "status": "operational",
                "command": cmd,
            })

        # Railway pattern for command execution
        if command is None:
            return execute_default_operation()

        return execute_command_with_args(command)

    # Utility methods


__all__ = [
    "FlextCliApi",
]
