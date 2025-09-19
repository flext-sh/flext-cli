"""FLEXT CLI API - Unified single-class implementation.

Uses Python 3.13 cutting-edge patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import yaml

from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import FlextCliModels
from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextLogger,
    FlextResult,
    FlextTypes,
)


class FlextCliApi(FlextDomainService[FlextTypes.Core.Dict]):
    """Unified CLI API service using single responsibility principle.

    Provides core CLI functionality expected by the ecosystem.
    ARCHITECTURAL COMPLIANCE: One class per module, nested helpers pattern.
    """

    class _StateHelper:
        """Nested helper for state management - no loose functions."""

        @staticmethod
        def create_initial_state() -> FlextCliModels.ApiState:
            """Create initial API state with proper defaults."""
            return FlextCliModels.ApiState(
                service_name="flext-cli-api",
                enable_session_tracking=True,
                enable_command_history=True,
                command_history=[],
                sessions={},
            )

    class _ValidationHelper:
        """Nested helper for input validation - no loose functions."""

        @staticmethod
        def validate_format_type(format_type: str) -> FlextResult[str]:
            """Validate format type parameter."""
            if not format_type or not isinstance(format_type, str):
                return FlextResult[str].fail("Format type must be a non-empty string")

            valid_formats = {"json", "yaml", "csv", "table", "plain"}
            if format_type.lower() not in valid_formats:
                return FlextResult[str].fail(f"Unsupported format type: {format_type}")

            return FlextResult[str].ok(format_type.lower())

        @staticmethod
        def validate_command_line(command_line: object) -> FlextResult[str]:
            """Validate command line parameter."""
            if not isinstance(command_line, str) or not command_line.strip():
                return FlextResult[str].fail("Command line must be a non-empty string")

            return FlextResult[str].ok(command_line.strip())

    def __init__(self) -> None:
        """Initialize FlextCliApi with proper state management."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()
        self._formatters = FlextCliFormatters()
        self._state = self._StateHelper.create_initial_state()

    def execute(
        self, command: str | None = None, **kwargs: object
    ) -> FlextResult[object | str]:
        """Execute CLI operation - supports both parent interface and backward compatibility."""
        if command is None:
            # Parent class interface
            self._logger.info("Executing CLI API operation")
            return FlextResult[object].ok(
                {"status": "operational", "service": "flext-cli-api"}
            )

        # Backward compatibility interface
        self._logger.info(f"Executing CLI API operation: {command}")

        if command == "format":
            data = kwargs.get("data")
            format_type = kwargs.get("format_type", "json")
            if data is not None:
                # format_output returns FlextResult[str]; adapt to declared return
                fmt_res = self.format_output(data, str(format_type))
                if fmt_res.is_failure:
                    return FlextResult[object | str].fail(
                        fmt_res.error or "Formatting failed"
                    )
                return FlextResult[object | str].ok(fmt_res.unwrap())
            return FlextResult[object].fail("No data provided for formatting")

        return FlextResult[object].ok({"status": "operational", "command": command})

    def execute_command(
        self, command: str = "status", **kwargs: object
    ) -> FlextResult[object | str]:
        """Execute CLI operation with command and parameters - delegates to execute."""
        return self.execute(command, **kwargs)

    def format_output(
        self,
        data: object,
        format_type: str = "table",
        **options: object,
    ) -> FlextResult[str]:
        """Format data using specified format type - core CLI functionality."""
        # Input validation using nested helper
        format_validation = self._ValidationHelper.validate_format_type(format_type)
        if format_validation.is_failure:
            return FlextResult[str].fail(
                format_validation.error or "Format validation failed"
            )

        validated_format = format_validation.unwrap()

        # Delegate to appropriate formatter based on type
        match validated_format:
            case "json":
                return self._format_as_json(data)
            case "yaml":
                return self._format_as_yaml(data)
            case "table":
                return self._format_as_table(data, **options)
            case "plain":
                return FlextResult[str].ok(str(data))
            case _:
                return FlextResult[str].fail(f"Unsupported format: {validated_format}")

    def _format_as_json(self, data: object) -> FlextResult[str]:
        """Format data as JSON using standard library."""
        try:
            result = json.dumps(data, default=str, indent=2)
            return FlextResult[str].ok(result)
        except Exception as e:
            return FlextResult[str].fail(f"JSON formatting failed: {e}")

    def _format_as_yaml(self, data: object) -> FlextResult[str]:
        """Format data as YAML using standard library."""
        try:
            result = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            return FlextResult[str].ok(result)
        except Exception as e:
            return FlextResult[str].fail(f"YAML formatting failed: {e}")

    def _format_as_table(self, data: object, **options: object) -> FlextResult[str]:
        """Format data as table with proper type casting."""
        if not data:
            return FlextResult[str].fail("Cannot format empty data as table")

        try:
            headers_value = options.get("headers")
            headers = headers_value if isinstance(headers_value, list) else None

            title_value = options.get("title")
            title = title_value if isinstance(title_value, str) else None

            show_lines_value = options.get("show_lines", True)
            show_lines = (
                show_lines_value if isinstance(show_lines_value, bool) else True
            )

            table_result = self._formatters.create_table(
                data=data, headers=headers, title=title, show_lines=show_lines
            )

            if table_result.is_failure:
                return FlextResult[str].fail(
                    f"Table creation failed: {table_result.error or 'Unknown error'}"
                )

            return FlextResult[str].ok(str(table_result.unwrap()))
        except Exception as e:
            return FlextResult[str].fail(f"Table formatting failed: {e!s}")

    def display_output(self, formatted_data: str) -> FlextResult[None]:
        """Display formatted data using flext-cli display system."""
        try:
            # Use flext-cli display system (abstracts Rich internally)
            display_result = self._formatters.display_message(formatted_data)
            if display_result.is_failure:
                return FlextResult[None].fail(display_result.error or "Display failed")

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Display failed: {e}")

    def create_command(
        self,
        command_line: str,
        **_options: object,
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Create CLI command with validation - core CLI functionality."""
        # Input validation using nested helper
        validation_result = self._ValidationHelper.validate_command_line(command_line)
        if validation_result.is_failure:
            return FlextResult[FlextCliModels.CliCommand].fail(
                validation_result.error or "Command validation failed"
            )

        validated_command = validation_result.unwrap()

        # Create command with proper metadata
        try:
            command = FlextCliModels.CliCommand(
                id=str(uuid4()),
                command_line=validated_command,
                execution_time=datetime.now(UTC),
            )

            # Add to command history if enabled
            if self._state.enable_command_history:
                self._state.command_history.append(command)

            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Command creation failed: {e}"
            )

    def get_health_status(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get API health status - core CLI functionality."""
        try:
            health_data = {
                "status": "healthy",
                "version": "1.0.0",
                "service": self._state.service_name,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                "platform": platform.system(),
                "timestamp": datetime.now(UTC).isoformat(),
                "sessions": self._state.session_count,
                "handlers": self._state.handler_count,
                "features": {
                    "session_tracking": self._state.enable_session_tracking,
                    "command_history": self._state.enable_command_history,
                },
            }

            return FlextResult[FlextTypes.Core.Dict].ok(health_data)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(f"Health check failed: {e}")

    def configure_api(self, config: dict[str, object]) -> FlextResult[None]:
        """Configure API with validation - core CLI functionality."""
        if not isinstance(config, dict) or not config:
            return FlextResult[None].fail(
                "Configuration must be a non-empty dictionary"
            )

        try:
            # Apply configuration settings using pattern matching
            for key, value in config.items():
                match key:
                    case "enable_session_tracking":
                        self._state.enable_session_tracking = bool(value)
                    case "enable_command_history":
                        self._state.enable_command_history = bool(value)
                    case "version":
                        # Version is now hardcoded, ignore configuration attempts
                        pass

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Configuration failed: {e}")

    def get_command_history(self) -> FlextResult[list[FlextCliModels.CliCommand]]:
        """Get command history - core CLI functionality."""
        if not self._state.enable_command_history:
            return FlextResult[list[FlextCliModels.CliCommand]].fail(
                "Command history is disabled"
            )

        return FlextResult[list[FlextCliModels.CliCommand]].ok(
            self._state.command_history.copy()
        )

    def clear_command_history(self) -> FlextResult[None]:
        """Clear command history - core CLI functionality."""
        if not self._state.enable_command_history:
            return FlextResult[None].fail("Command history is disabled")

        self._state.command_history.clear()
        return FlextResult[None].ok(None)

    def api_state(self) -> FlextCliModels.ApiState:
        """Get current API state for inspection and testing."""
        return self._state

    def format_data(self, data: object, format_type: str) -> FlextResult[str]:
        """Format data using specified format type."""
        return self.format_output(data, format_type)

    def create_table(
        self, data: object, title: str | None = None, **options: object
    ) -> FlextResult[str]:
        """Create table from data with optional title and options."""
        return self._format_as_table(data, title=title, **options)

    def create_rich_table(
        self, data: object, title: str | None = None, **options: object
    ) -> FlextResult[str]:
        """Create Rich table from data - alias for create_table."""
        return self.create_table(data, title=title, **options)

    def transform_data(self, data: object, transform_fn: object) -> FlextResult[object]:
        """Transform data using provided function."""
        if not callable(transform_fn):
            return FlextResult[object].fail("Transform function must be callable")

        try:
            if isinstance(data, list):
                transformed = [transform_fn(item) for item in data]
            else:
                transformed = transform_fn(data)
            return FlextResult[object].ok(transformed)
        except Exception as e:
            return FlextResult[object].fail(f"Data transformation failed: {e!s}")

    def aggregate_data(self, data: object, **kwargs: object) -> FlextResult[object]:
        """Aggregate data based on provided parameters."""
        if not isinstance(data, list):
            return FlextResult[object].fail("Aggregation requires list data")

        group_by = kwargs.get("_group_by")
        sum_fields = kwargs.get("_sum_fields", [])

        if not group_by:
            return FlextResult[object].fail(
                "group_by parameter required for aggregation"
            )

        try:
            # Simple aggregation implementation
            groups: dict[str, list[object]] = {}
            for item in data:
                if isinstance(item, dict) and group_by in item:
                    key = str(item[group_by])
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(item)

            # Sum numeric fields if specified
            if sum_fields and isinstance(sum_fields, list):
                result_groups: dict[str, object] = {}
                for key, items in groups.items():
                    for field in sum_fields:
                        if isinstance(field, str) and items:
                            total = sum(
                                item.get(field, 0)
                                for item in items
                                if isinstance(item, dict)
                            )
                            first_item = items[0]
                            if isinstance(first_item, dict):
                                result_groups[key] = {**first_item, field: total}
                            else:
                                result_groups[key] = {field: total}
                return FlextResult[object].ok(result_groups)

            return FlextResult[object].ok(groups)
        except Exception as e:
            return FlextResult[object].fail(f"Data aggregation failed: {e!s}")

    def export_data(
        self, data: object, file_path: object, format_type: str = "json"
    ) -> FlextResult[None]:
        """Export data to file in specified format."""
        if not isinstance(file_path, Path):
            return FlextResult[None].fail("file_path must be a Path object")

        try:
            if format_type == "json":
                with file_path.open("w") as f:
                    json.dump(data, f, indent=2)
            elif format_type == "yaml":
                with file_path.open("w") as f:
                    yaml.dump(data, f)
            else:
                return FlextResult[None].fail(
                    f"Unsupported export format: {format_type}"
                )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Export failed: {e!s}")

    def batch_export(
        self, datasets: object, output_dir: object, format_type: str = "json"
    ) -> FlextResult[None]:
        """Export multiple datasets to directory."""
        if not isinstance(output_dir, Path):
            return FlextResult[None].fail("output_dir must be a Path object")

        if not isinstance(datasets, dict):
            return FlextResult[None].fail("datasets must be a dictionary")

        try:
            for name, data in datasets.items():
                file_path = output_dir / f"{name}.{format_type}"
                export_result = self.export_data(data, file_path, format_type)
                if export_result.is_failure:
                    return export_result

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Batch export failed: {e!s}")

    def unwrap_or_default(self, result: FlextResult[object], default: object) -> object:
        """Unwrap FlextResult or return default value if failed."""
        if result.is_success:
            return result.unwrap()
        return default

    def unwrap_or_none(self, result: FlextResult[object]) -> object | None:
        """Unwrap FlextResult or return None if failed."""
        if result.is_success:
            return result.unwrap()
        return None


# =========================================================================
# MODULE EXPORTS - Single unified class with all functionality encapsulated
# =========================================================================

__all__ = [
    "FlextCliApi",
]
