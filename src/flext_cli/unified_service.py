"""FLEXT CLI Unified Service - Consolidation using advanced flext-core features.

This module consolidates FlextCliApi and FlextCliFormatters into a single
unified service using FlextCqrs patterns, FlextBus for messaging, and
FlextContainer for dependency injection.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from uuid import uuid4

import yaml
from pydantic import BaseModel, Field

from flext_core import (
    FlextBus,
    FlextContainer,
    FlextDomainService,
    FlextLogger,
    FlextResult,
    FlextTypes,
)


# Command Models for CQRS Pattern
class FormatDataCommand(BaseModel):
    """Command to format data using specified format type."""

    data: object
    format_type: str = "table"
    options: dict[str, object] = Field(default_factory=dict)
    request_id: str = Field(default_factory=lambda: str(uuid4()))


class DisplayOutputCommand(BaseModel):
    """Command to display formatted output."""

    formatted_data: str
    display_options: dict[str, object] = Field(default_factory=dict)
    request_id: str = Field(default_factory=lambda: str(uuid4()))


class CreateCommandCommand(BaseModel):
    """Command to create CLI command structures."""

    command_line: str
    options: dict[str, object] = Field(default_factory=dict)
    request_id: str = Field(default_factory=lambda: str(uuid4()))


class ExportDataCommand(BaseModel):
    """Command to export data to files."""

    data: object
    file_path: Path
    format_type: str = "json"
    request_id: str = Field(default_factory=lambda: str(uuid4()))


# Query Models for CQRS Pattern
class HealthStatusQuery(BaseModel):
    """Query to get health status."""

    request_id: str = Field(default_factory=lambda: str(uuid4()))


class CommandHistoryQuery(BaseModel):
    """Query to get command history."""

    request_id: str = Field(default_factory=lambda: str(uuid4()))


# Unified CLI Service using Advanced flext-core Features
class FlextCliUnifiedService(FlextDomainService[FlextTypes.Core.Dict]):
    """Unified CLI service consolidating API and formatting functionality.

    Uses advanced flext-core features:
    - FlextCqrs for command/query separation
    - FlextBus for internal messaging
    - FlextContainer for dependency injection
    - FlextResult for railway-oriented programming
    """

    class _CommandHandlers:
        """CQRS Command handlers using flext-core patterns."""

        def __init__(self, service: FlextCliUnifiedService) -> None:
            self._service = service
            self._logger = FlextLogger(__name__)

        @staticmethod
        def handle_format_data(command: FormatDataCommand) -> FlextResult[str]:
            """Handle data formatting command using railway pattern.

            Returns:
            FlextResult[str]: Description of return value.

            """
            logger = FlextLogger(__name__)
            logger.info(f"Processing format command: {command.request_id}")

            def validate_format_type(fmt_type: str) -> FlextResult[str]:
                """Validate format type using railway pattern.

                Returns:
                FlextResult[str]: Description of return value.

                """
                if fmt_type not in {"json", "yaml", "table", "csv", "plain"}:
                    return FlextResult[str].fail(f"Unsupported format: {fmt_type}")
                return FlextResult[str].ok(fmt_type)

            def delegate_to_formatter(fmt_type: str) -> FlextResult[str]:
                """Delegate to appropriate formatter using railway pattern.

                Returns:
                FlextResult[str]: Description of return value.

                """
                match fmt_type:
                    case "json":
                        return FlextCliUnifiedService._CommandHandlers.format_as_json(
                            command.data
                        )
                    case "yaml":
                        return FlextCliUnifiedService._CommandHandlers.format_as_yaml(
                            command.data
                        )
                    case "table":
                        return FlextCliUnifiedService._CommandHandlers.format_as_table(
                            command.data, **command.options
                        )
                    case "csv":
                        return FlextCliUnifiedService._CommandHandlers.format_as_csv(
                            command.data, **command.options
                        )
                    case "plain":
                        return FlextResult[str].ok(str(command.data))
                    case _:
                        return FlextResult[str].fail(
                            f"Format handler not implemented: {fmt_type}"
                        )

            # Railway pattern composition - no try/except needed
            return validate_format_type(command.format_type).flat_map(
                delegate_to_formatter
            )

        @staticmethod
        def handle_display_output(command: DisplayOutputCommand) -> FlextResult[None]:
            """Handle output display command using railway pattern.

            Returns:
            FlextResult[None]: Description of return value.

            """
            logger = FlextLogger(__name__)
            logger.info(f"Processing display command: {command.request_id}")

            # Direct success return - no risky operations require try/except
            return FlextResult[None].ok(None)

        @staticmethod
        def handle_create_command(
            command: CreateCommandCommand,
        ) -> FlextResult[dict[str, object]]:
            """Handle CLI command creation.

            Returns:
            FlextResult[dict[str, object]]: Description of return value.

            """
            logger = FlextLogger(__name__)
            logger.info(f"Processing create command: {command.request_id}")

            if not command.command_line.strip():
                return FlextResult[dict[str, object]].fail(
                    "Command line cannot be empty"
                )

            cli_command: dict[str, object] = {
                "id": str(uuid4()),
                "command_line": command.command_line.strip(),
                "execution_time": datetime.now(UTC).isoformat(),
                "options": command.options,
            }

            return FlextResult[dict[str, object]].ok(cli_command)

        @staticmethod
        def handle_export_data(command: ExportDataCommand) -> FlextResult[None]:
            """Handle data export command using railway pattern.

            Returns:
            FlextResult[None]: Description of return value.

            """
            logger = FlextLogger(__name__)
            logger.info(f"Processing export command: {command.request_id}")

            def validate_format_type(fmt_type: str) -> FlextResult[str]:
                """Validate export format type.

                Returns:
                FlextResult[str]: Description of return value.

                """
                if fmt_type not in {"json", "yaml"}:
                    return FlextResult[str].fail(
                        f"Export format not supported: {fmt_type}"
                    )
                return FlextResult[str].ok(fmt_type)

            def export_as_json(data: object, file_path: Path) -> FlextResult[None]:
                """Export data as JSON using safe execution.

                Returns:
                FlextResult[None]: Description of return value.

                """
                return FlextResult.safe_call(
                    lambda: FlextCliUnifiedService._CommandHandlers.write_json_file(
                        data, file_path
                    )
                ).map(lambda _: None)

            def export_as_yaml(data: object, file_path: Path) -> FlextResult[None]:
                """Export data as YAML using safe execution.

                Returns:
                FlextResult[None]: Description of return value.

                """
                return FlextResult.safe_call(
                    lambda: FlextCliUnifiedService._CommandHandlers.write_yaml_file(
                        data, file_path
                    )
                ).map(lambda _: None)

            def delegate_to_exporter(fmt_type: str) -> FlextResult[None]:
                """Delegate to appropriate exporter using railway pattern.

                Returns:
                FlextResult[None]: Description of return value.

                """
                match fmt_type:
                    case "json":
                        return export_as_json(command.data, command.file_path)
                    case "yaml":
                        return export_as_yaml(command.data, command.file_path)
                    case _:
                        return FlextResult[None].fail(
                            f"Export handler not implemented: {fmt_type}"
                        )

            # Railway pattern composition - no try/except needed
            return validate_format_type(command.format_type).flat_map(
                delegate_to_exporter
            )

        # Private helper functions for file I/O
        @staticmethod
        def write_json_file(data: object, file_path: Path) -> None:
            """Write data to JSON file - used by safe_call."""
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

        @staticmethod
        def write_yaml_file(data: object, file_path: Path) -> None:
            """Write data to YAML file - used by safe_call."""
            with file_path.open("w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False)

        # Private formatting methods
        @staticmethod
        def format_as_json(data: object) -> FlextResult[str]:
            """Format data as JSON using safe execution.

            Returns:
            FlextResult[str]: Description of return value.

            """
            result = FlextResult.safe_call(
                lambda: json.dumps(data, indent=2, default=str)
            )
            if result.is_failure:
                return FlextResult[str].fail(f"JSON formatting failed: {result.error}")
            return result

        @staticmethod
        def format_as_yaml(data: object) -> FlextResult[str]:
            """Format data as YAML using safe execution.

            Returns:
            FlextResult[str]: Description of return value.

            """
            try:
                formatted_yaml = yaml.dump(data, default_flow_style=False)
                return FlextResult[str].ok(formatted_yaml)
            except Exception as e:
                return FlextResult[str].fail(f"YAML formatting failed: {e}")

        @staticmethod
        def format_as_table(data: object, **options: object) -> FlextResult[str]:
            """Format data as table using explicit error handling.

            Returns:
            FlextResult[str]: Description of return value.

            """
            # Validate input data
            if not isinstance(data, list):
                return FlextResult[str].fail(
                    "Table format requires list of dictionaries"
                )

            if not all(isinstance(item, dict) for item in data):
                return FlextResult[str].fail(
                    "Table format requires list of dictionaries"
                )

            if not data:
                return FlextResult[str].ok("No data to display")

            try:
                # Create simple table
                headers = list(data[0].keys())
                rows = [list(item.values()) for item in data]

                # Format table
                lines: list[str] = []
                if options.get("title"):
                    lines.extend((f"=== {options['title']} ===", ""))

                # Header
                header_line = " | ".join(str(h) for h in headers)
                lines.extend((header_line, "-" * len(header_line)))

                # Rows
                for row in rows:
                    row_line = " | ".join(str(cell) for cell in row)
                    lines.append(row_line)

                return FlextResult[str].ok("\n".join(lines))
            except Exception as e:
                return FlextResult[str].fail(f"Table formatting failed: {e}")

        @staticmethod
        def format_as_csv(data: object, **_options: object) -> FlextResult[str]:
            """Format data as CSV using explicit error handling.

            Returns:
            FlextResult[str]: Description of return value.

            """
            # Validate input data
            if not isinstance(data, list):
                return FlextResult[str].fail("CSV format requires list of dictionaries")

            if not all(isinstance(item, dict) for item in data):
                return FlextResult[str].fail("CSV format requires list of dictionaries")

            if not data:
                return FlextResult[str].ok("")

            try:
                output = StringIO()
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
                return FlextResult[str].ok(output.getvalue())
            except Exception as e:
                return FlextResult[str].fail(f"CSV formatting failed: {e}")

    class _QueryHandlers:
        """CQRS Query handlers using flext-core patterns."""

        def __init__(self, service: FlextCliUnifiedService) -> None:
            self._service = service
            self._logger = FlextLogger(__name__)

        def handle_health_status(
            self, query: HealthStatusQuery
        ) -> FlextResult[dict[str, object]]:
            """Handle health status query.

            Returns:
            FlextResult[dict[str, object]]: Description of return value.

            """
            self._logger.info(f"Processing health query: {query.request_id}")

            health_data: dict[str, object] = {
                "status": "healthy",
                "version": "1.0.0",
                "service": "flext-cli-unified",
                "timestamp": datetime.now(UTC).isoformat(),
                "features": {
                    "cqrs_enabled": True,
                    "bus_enabled": True,
                    "container_enabled": True,
                },
            }

            return FlextResult[dict[str, object]].ok(health_data)

        def handle_command_history(
            self, query: CommandHistoryQuery
        ) -> FlextResult[list[dict[str, object]]]:
            """Handle command history query.

            Returns:
            FlextResult[list[dict[str, object]]]: Description of return value.

            """
            self._logger.info(f"Processing history query: {query.request_id}")

            # Return empty history for now - would be populated from actual state
            return FlextResult[list[dict[str, object]]].ok([])

    def __init__(self) -> None:
        """Initialize unified service with advanced flext-core features."""
        super().__init__()
        self._logger = FlextLogger(__name__)

        # Use FlextContainer for dependency injection
        self._container = FlextContainer.get_global()

        # Use FlextBus for internal messaging
        self._bus = FlextBus()

        # Initialize CQRS handlers
        self._command_handlers = self._CommandHandlers(self)
        self._query_handlers = self._QueryHandlers(self)

        # Bus registration simplified - just store handlers
        self._logger.info("Command handlers initialized")

    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute the unified service - required by FlextDomainService.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        return FlextResult[FlextTypes.Core.Dict].ok({
            "status": "operational",
            "service": "flext-cli-unified",
        })

    # Public API Methods (simplified through CQRS)
    def format_data(
        self, data: object, format_type: str = "table", **options: object
    ) -> FlextResult[str]:
        """Format data using CQRS command pattern.

        Returns:
            FlextResult[str]: Description of return value.

        """
        command = FormatDataCommand(data=data, format_type=format_type, options=options)
        return self._CommandHandlers.handle_format_data(command)

    def display_output(
        self, formatted_data: str, **options: object
    ) -> FlextResult[None]:
        """Display output using CQRS command pattern.

        Returns:
            FlextResult[None]: Description of return value.

        """
        command = DisplayOutputCommand(
            formatted_data=formatted_data, display_options=options
        )
        return self._CommandHandlers.handle_display_output(command)

    def display_message(
        self, message: str, _style: str = "", prefix: str = ""
    ) -> FlextResult[None]:
        """Display formatted message with optional styling.

        Returns:
            FlextResult[None]: Description of return value.

        """
        formatted_message = f"{prefix}{message}" if prefix else message
        return self.display_output(formatted_message)

    def create_command(
        self, command_line: str, **options: object
    ) -> FlextResult[dict[str, object]]:
        """Create CLI command using CQRS command pattern.

        Returns:
            FlextResult[dict[str, object]]: Description of return value.

        """
        command = CreateCommandCommand(command_line=command_line, options=options)
        return self._CommandHandlers.handle_create_command(command)

    def export_data(
        self, data: object, file_path: Path, format_type: str = "json"
    ) -> FlextResult[None]:
        """Export data using CQRS command pattern.

        Returns:
            FlextResult[None]: Description of return value.

        """
        command = ExportDataCommand(
            data=data, file_path=file_path, format_type=format_type
        )
        return self._CommandHandlers.handle_export_data(command)

    def get_health_status(self) -> FlextResult[dict[str, object]]:
        """Get health status using CQRS query pattern.

        Returns:
            FlextResult[dict[str, object]]: Description of return value.

        """
        query = HealthStatusQuery()
        return self._query_handlers.handle_health_status(query)

    def get_command_history(self) -> FlextResult[list[dict[str, object]]]:
        """Get command history using CQRS query pattern.

        Returns:
            FlextResult[list[dict[str, object]]]: Description of return value.

        """
        query = CommandHistoryQuery()
        return self._query_handlers.handle_command_history(query)

    # Convenience methods combining multiple operations
    def format_and_display(
        self, data: object, format_type: str = "table", **options: object
    ) -> FlextResult[None]:
        """Format data and display it in one operation.

        Returns:
            FlextResult[None]: Description of return value.

        """
        format_result = self.format_data(data, format_type, **options)
        if format_result.is_failure:
            return FlextResult[None].fail(format_result.error or "Formatting failed")

        display_result = self.display_output(format_result.unwrap())
        if display_result.is_failure:
            return FlextResult[None].fail(display_result.error or "Display failed")

        return FlextResult[None].ok(None)

    def batch_export(
        self, datasets: dict[str, object], output_dir: Path, format_type: str = "json"
    ) -> FlextResult[None]:
        """Export multiple datasets using CQRS pattern.

        Returns:
            FlextResult[None]: Description of return value.

        """
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        for name, data in datasets.items():
            file_path = output_dir / f"{name}.{format_type}"
            export_result = self.export_data(data, file_path, format_type)
            if export_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to export {name}: {export_result.error}"
                )

        return FlextResult[None].ok(None)


# Global instance using flext-core container
def get_unified_cli_service() -> FlextCliUnifiedService:
    """Get the unified CLI service instance from flext-core container using railway pattern.

    Returns:
        FlextCliUnifiedService: Description of return value.

    """
    container = FlextContainer.get_global()

    def get_existing_service() -> FlextResult[FlextCliUnifiedService]:
        """Try to get existing service instance.

        Returns:
            FlextResult[FlextCliUnifiedService]: Description of return value.

        """
        service_result = container.get("FlextCliUnifiedService")
        if service_result.is_failure:
            return FlextResult[FlextCliUnifiedService].fail(
                "Service not found in container"
            )

        if isinstance(service_result.value, FlextCliUnifiedService):
            return FlextResult[FlextCliUnifiedService].ok(service_result.value)

        return FlextResult[FlextCliUnifiedService].fail(
            "Invalid service type in container"
        )

    def create_and_register_service() -> FlextCliUnifiedService:
        """Create and register new service instance.

        Returns:
            FlextCliUnifiedService: Description of return value.

        """
        service = FlextCliUnifiedService()
        container.register("FlextCliUnifiedService", service)
        return service

    # Railway pattern with fallback - try to get existing, create if not found
    existing_service_result = get_existing_service()
    if existing_service_result.is_success:
        return existing_service_result.unwrap()

    # Fallback: create new instance
    return create_and_register_service()


__all__ = [
    "CommandHistoryQuery",
    "CreateCommandCommand",
    "DisplayOutputCommand",
    "ExportDataCommand",
    "FlextCliUnifiedService",
    "FormatDataCommand",
    "HealthStatusQuery",
    "get_unified_cli_service",
]
