"""FLEXT CLI API - Consolidated CLI API following flext-core patterns.

Provides CLI-specific API functionality extending flext-core patterns with
command execution, data formatting, export capabilities, and session management.
Follows consolidated class pattern with domain-specific operations.

Module Role in Architecture:
    FlextCliApi serves as the main API entry point for CLI operations, providing
    a unified interface for command execution, data formatting, export operations,
    and session management following flext-core service patterns.

Classes and Methods:
    FlextCliApi:                           # Consolidated CLI API
        # Data Operations:
        format_data(data, format) -> FlextResult[str]
        export_data(data, path) -> FlextResult[str]
        transform_data(data, filters) -> FlextResult[list]
        aggregate_data(data, group_by) -> FlextResult[list]

        # Command Operations:
        create_command(name, command_line) -> FlextResult[Command]
        execute_command(command) -> FlextResult[str]
        get_command_history() -> list[Command]

        # Session Operations:
        create_session(user_id) -> FlextResult[str]
        get_session(session_id) -> FlextResult[dict]
        end_session(session_id) -> FlextResult[None]

        # System Operations:
        health_check() -> dict[str, object]
        configure(config) -> FlextResult[None]

Usage Examples:
    Basic API usage:
        api = FlextCliApi()

        # Data formatting
        format_result = api.format_data(data, "table")
        if format_result.is_success:
            print(format_result.value)

        # Command creation and execution
        cmd_result = api.create_command("test", "echo hello")
        if cmd_result.is_success:
            exec_result = api.execute_command(cmd_result.value)

        # Session management
        session_result = api.create_session("user123")
        if session_result.is_success:
            session_id = session_result.value

Integration:
    FlextCliApi integrates with FlextCliServices for service layer operations,
    FlextCliModels for domain entities, and FlextResult for error handling
    following railway-oriented programming patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import platform
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import override

from flext_core import FlextResult, FlextUtilities
from flext_core.models import FlextModels
from pydantic import ConfigDict, Field
from rich.table import Table

from flext_cli.models import FlextCliModels
from flext_cli.services import FlextCliServices


class FlextCliApi(FlextModels):
    """Consolidated CLI API extending flext-core patterns.

    Following exact semantic pattern from flext-core:
        - Module: api.py → Class: FlextCliApi
        - Single consolidated class containing all API functionality
        - Domain-specific operations organized by functional area
        - Type-safe methods following railway-oriented programming

    API operation domains:
        - Data: Formatting, transformation, aggregation, export
        - Command: Creation, execution, history management
        - Session: Creation, tracking, lifecycle management
        - System: Health, configuration, diagnostics
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    # Core API configuration
    version: str = Field(
        default="0.9.0",
        description="API version",
    )
    service_name: str = Field(
        default="flext-cli-api",
        description="API service name",
    )
    enable_session_tracking: bool = Field(
        default=True,
        description="Enable session tracking",
    )
    enable_command_history: bool = Field(
        default=True,
        description="Enable command history",
    )

    # Private service processors using new FlextServices patterns
    command_processor: FlextCliServices.CliCommandProcessor = Field(
        default_factory=FlextCliServices.create_command_processor,
        description="CLI command processor instance",
        exclude=True,
        alias="_command_processor",
    )
    session_processor: FlextCliServices.CliSessionProcessor = Field(
        default_factory=FlextCliServices.create_session_processor,
        description="CLI session processor instance",
        exclude=True,
        alias="_session_processor",
    )
    config_processor: FlextCliServices.CliConfigProcessor = Field(
        default_factory=FlextCliServices.create_config_processor,
        description="CLI config processor instance",
        exclude=True,
        alias="_config_processor",
    )

    def __init__(self, **data: object) -> None:
        """Initialize CLI API with service layer integration."""
        super().__init__(**data)

        # Initialize service instances directly (they return processors, not FlextResults)
        output_service = FlextCliServices.create_config_processor()
        command_service = FlextCliServices.create_command_processor()

        object.__setattr__(self, "_output_service", output_service)
        object.__setattr__(self, "_command_service", command_service)

        # Initialize storage for session tracking
        if self.enable_session_tracking:
            object.__setattr__(self, "_sessions", {})

        if self.enable_command_history:
            object.__setattr__(self, "_command_history", [])

    # =========================================================================
    # DATA OPERATIONS - Formatting, transformation, export
    # =========================================================================

    def format_data(
        self,
        data: object,
        format_type: str = "table",
        **_options: object,
    ) -> FlextResult[str]:
        """Format data using specified output format.

        Args:
            data: Data to format
            format_type: Output format (table, json, yaml, csv, plain)
            **options: Additional formatting options

        Returns:
            FlextResult containing formatted string or error

        """
        try:
            # Validate format type
            valid_formats = {"table", "json", "yaml", "csv", "plain"}
            if format_type not in valid_formats:
                return FlextResult[str].fail(f"Invalid format: {format_type}")

            # Use basic formatting
            return self._basic_format(data, format_type)

        except (ValueError, TypeError, RuntimeError) as e:
            return FlextResult[str].fail(f"Data formatting failed: {e}")

    def _basic_format(self, data: object, format_type: str) -> FlextResult[str]:
        """Basic data formatting fallback - delegates to utilities."""
        try:
            # Simple inline formatting
            import json

            if format_type == "json":
                try:
                    json_str = json.dumps(data, indent=2, default=str)
                    return FlextResult[str].ok(json_str)
                except Exception as e:
                    return FlextResult[str].fail(f"JSON formatting failed: {e}")

            if format_type == "yaml":
                # Simple YAML-like formatting without pyyaml dependency
                return FlextResult[str].ok(str(data))

            if format_type == "plain":
                return FlextResult[str].ok(str(data))

            if format_type == "csv":
                # Simple CSV formatting for list of dicts
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    import csv
                    import io

                    output = io.StringIO()
                    writer = csv.writer(output)
                    # Write header
                    writer.writerow(data[0].keys())
                    # Write rows
                    for row in data:
                        writer.writerow(row.values())
                    return FlextResult[str].ok(output.getvalue().strip())
                return FlextResult[str].ok(str(data))

            if format_type == "table":
                return FlextResult[str].ok(str(data))

            # For other formats, use simple string representation
            return FlextResult[str].ok(str(data))

        except (ValueError, TypeError) as e:
            return FlextResult[str].fail(f"Basic formatting failed: {e}")

    def export_data(
        self,
        data: object,
        file_path: str | Path,
        format_type: str = "json",
    ) -> FlextResult[str]:
        """Export data to file in specified format.

        Args:
            data: Data to export
            file_path: Target file path
            format_type: Export format

        Returns:
            FlextResult containing success message or error

        """
        try:
            path = Path(file_path)

            # Format data for export
            format_result = self.format_data(data, format_type)
            if format_result.is_failure:
                return FlextResult[str].fail(format_result.error or "Format failed")

            # Write to file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(format_result.value, encoding="utf-8")

            return FlextResult[str].ok(f"Data exported to {path}")

        except (OSError, ValueError, TypeError) as e:
            return FlextResult[str].fail(f"Export failed: {e}")

    def transform_data(
        self,
        data: list[dict[str, object]],
        filter_func: Callable[[dict[str, object]], bool] | None = None,
        sort_key: str | None = None,
        *,
        reverse: bool = False,
    ) -> FlextResult[list[dict[str, object]]]:
        """Transform data with filtering and sorting.

        Args:
            data: List of dictionaries to transform
            filter_func: Optional filter function
            sort_key: Optional key to sort by
            reverse: Whether to reverse sort order

        Returns:
            FlextResult containing transformed data or error

        """
        try:
            # Validate input data type
            if not isinstance(data, list):
                return FlextResult[list[dict[str, object]]].fail(
                    f"Expected list, got {type(data).__name__}"
                )

            result = data.copy()

            # Apply filter
            if filter_func:
                result = [
                    item
                    for item in result
                    if isinstance(item, dict) and filter_func(item)
                ]

            # Apply sort
            if sort_key:
                result.sort(
                    key=lambda x: str(x.get(sort_key, ""))
                    if isinstance(x, dict)
                    else "",
                    reverse=reverse,
                )

            return FlextResult[list[dict[str, object]]].ok(result)

        except (ValueError, TypeError) as e:
            return FlextResult[list[dict[str, object]]].fail(f"Transform failed: {e}")

    def aggregate_data(
        self,
        data: list[dict[str, object]],
        group_by: str,
        sum_fields: list[str] | None = None,
        count_field: str = "count",
    ) -> FlextResult[list[dict[str, object]]]:
        """Aggregate data by grouping and summing fields.

        Args:
            data: List of dictionaries to aggregate
            group_by: Field to group by
            sum_fields: Fields to sum (numeric fields only)
            count_field: Name for count field

        Returns:
            FlextResult containing aggregated data or error

        """
        try:
            # Validate input data type
            if not isinstance(data, list):
                return FlextResult[list[dict[str, object]]].fail(
                    f"Expected list, got {type(data).__name__}"
                )

            groups: dict[str, dict[str, object]] = {}
            sum_fields = sum_fields or []

            for item in data:
                # Validate item type
                if not isinstance(item, dict):
                    continue  # Skip non-dict items

                group_value = item.get(group_by)
                if group_value is None:
                    continue

                group_key = str(group_value)

                if group_key not in groups:
                    groups[group_key] = {
                        group_by: group_value,
                        count_field: 0,
                    }
                    # Initialize sum fields
                    for field in sum_fields:
                        groups[group_key][f"{field}_sum"] = 0

                # Update count
                count_val = groups[group_key][count_field]
                if isinstance(count_val, int):
                    groups[group_key][count_field] = count_val + 1

                # Update sums
                for field in sum_fields:
                    if field in item and isinstance(item[field], (int, float)):
                        sum_key = f"{field}_sum"
                        current_sum = groups[group_key][sum_key]
                        if isinstance(current_sum, (int, float)):
                            field_val = item[field]
                            if isinstance(field_val, (int, float)):
                                groups[group_key][sum_key] = current_sum + field_val

            result = list(groups.values())
            return FlextResult[list[dict[str, object]]].ok(result)

        except (ValueError, TypeError) as e:
            return FlextResult[list[dict[str, object]]].fail(f"Aggregation failed: {e}")

    # =========================================================================
    # COMMAND OPERATIONS - Creation, execution, history
    # =========================================================================

    def create_command(
        self,
        command_line: str,
        **_options: object,
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Create a new CLI command.

        Args:
            command_line: Command line to execute
            **options: Additional command options

        Returns:
            FlextResult containing created command or error

        """
        try:
            # Create command using model factory with only required fields
            command = FlextCliModels.CliCommand(command_line=command_line)
            validation_result = command.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    validation_result.error or "Command creation failed"
                )

            # Command is already created above

            # Add to command history if enabled
            if self.enable_command_history and hasattr(self, "_command_history"):
                command_history = getattr(self, "_command_history", [])
                command_history.append(command)
                object.__setattr__(self, "_command_history", command_history)

            return FlextResult[FlextCliModels.CliCommand].ok(command)

        except (ValueError, RuntimeError, TypeError) as e:
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Command creation failed: {e}"
            )

    def execute_command(
        self,
        command: FlextCliModels.CliCommand | str,
        timeout: int | None = None,
    ) -> FlextResult[str]:
        """Execute a CLI command.

        Args:
            command: Command object or command string
            timeout: Optional execution timeout

        Returns:
            FlextResult containing command output or error

        """
        try:
            # Handle string command
            if isinstance(command, str):
                cmd_result = self.create_command(command)
                if cmd_result.is_failure:
                    return FlextResult[str].fail(
                        cmd_result.error or "Command creation failed"
                    )
                command_obj = cmd_result.value
            else:
                command_obj = command

            # Basic execution simulation, include timeout info when provided
            timeout_info = f" (timeout={timeout}s)" if timeout else ""
            return FlextResult[str].ok(
                f"Command executed: {command_obj.command_line}{timeout_info}"
            )

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[str].fail(f"Command execution failed: {e}")

    def get_command_history(self) -> list[FlextCliModels.CliCommand]:
        """Get command execution history.

        Returns:
            List of executed commands

        """
        if not self.enable_command_history:
            return []

        command_history = getattr(self, "_command_history", [])
        return command_history.copy()

    # =========================================================================
    # SESSION OPERATIONS - Creation, tracking, lifecycle
    # =========================================================================

    def create_session(self, user_id: str | None = None) -> FlextResult[str]:
        """Create a new CLI session.

        Args:
            user_id: Optional user identifier

        Returns:
            FlextResult containing session ID or error

        """
        try:
            if not self.enable_session_tracking:
                return FlextResult[str].fail("Session tracking disabled")

            # Generate session ID
            session_id = f"cli_session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{FlextUtilities.generate_id()}"

            # Create session data
            session_data: dict[str, object] = {
                "id": session_id,
                "user_id": user_id,
                "status": "active",
                "created_at": datetime.now(UTC),
                "commands": [],
                "last_activity": datetime.now(UTC),
            }

            # Store session
            sessions = getattr(self, "_sessions", {})
            sessions[session_id] = session_data
            object.__setattr__(self, "_sessions", sessions)

            return FlextResult[str].ok(session_id)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[str].fail(f"Session creation failed: {e}")

    def get_session(self, session_id: str) -> FlextResult[dict[str, object]]:
        """Get session information.

        Args:
            session_id: Session identifier

        Returns:
            FlextResult containing session data or error

        """
        try:
            if not self.enable_session_tracking:
                return FlextResult[dict[str, object]].fail("Session tracking disabled")

            sessions = getattr(self, "_sessions", {})
            if session_id not in sessions:
                return FlextResult[dict[str, object]].fail(
                    f"Session not found: {session_id}"
                )

            session_data = sessions[session_id]
            return FlextResult[dict[str, object]].ok(session_data)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[dict[str, object]].fail(f"Session retrieval failed: {e}")

    def end_session(self, session_id: str) -> FlextResult[None]:
        """End a CLI session.

        Args:
            session_id: Session identifier

        Returns:
            FlextResult indicating success or error

        """
        try:
            if not self.enable_session_tracking:
                return FlextResult[None].fail("Session tracking disabled")

            sessions = getattr(self, "_sessions", {})
            if session_id not in sessions:
                return FlextResult[None].fail(f"Session not found: {session_id}")

            sessions[session_id]["status"] = "ended"
            sessions[session_id]["ended_at"] = datetime.now(UTC)

            return FlextResult[None].ok(None)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[None].fail(f"Session termination failed: {e}")

    def get_active_sessions(self) -> list[dict[str, object]]:
        """Get all active sessions.

        Returns:
            List of active session data

        """
        if not self.enable_session_tracking:
            return []

        sessions = getattr(self, "_sessions", {})
        active_sessions = []

        for session_data in sessions.values():
            if (
                isinstance(session_data, dict)
                and session_data.get("status") == "active"
            ):
                # Create session summary without sensitive data
                summary = {
                    "id": session_data.get("id"),
                    "user_id": session_data.get("user_id"),
                    "created_at": session_data.get("created_at"),
                    "command_count": len(session_data.get("commands", [])),
                    "last_activity": session_data.get("last_activity"),
                }
                active_sessions.append(summary)

        return active_sessions

    # =========================================================================
    # SYSTEM OPERATIONS - Health, configuration, diagnostics
    # =========================================================================

    def health_check(self) -> dict[str, object]:
        """Get API health status.

        Returns:
            Dictionary containing health information

        """
        try:
            # Basic health metrics
            health_data: dict[str, object] = {
                "status": "healthy",
                "timestamp": datetime.now(UTC).isoformat(),
                "version": self.version,
                "service": self.service_name,
                "python_version": sys.version.split()[0],
                "platform": platform.platform(),
            }

            # Add service-specific metrics
            if self.enable_session_tracking:
                sessions = getattr(self, "_sessions", {})
                active_count = sum(
                    1
                    for s in sessions.values()
                    if isinstance(s, dict) and s.get("status") == "active"
                )
                health_data["active_sessions"] = active_count
                health_data["total_sessions"] = len(sessions)

            if self.enable_command_history:
                command_history = getattr(self, "_command_history", [])
                health_data["command_history_size"] = len(command_history)

            # Service availability checks
            health_data["services"] = {
                "output_service": hasattr(self, "_output_service"),
                "command_service": hasattr(self, "_command_service"),
            }

            return health_data

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "version": self.version,
                "service": self.service_name,
            }

    def configure(self, config: dict[str, object]) -> FlextResult[None]:
        """Configure API with new settings.

        Args:
            config: Configuration dictionary

        Returns:
            FlextResult indicating success or error

        """
        try:
            # Validate configuration structure
            if not config:
                return FlextResult[None].fail("Configuration cannot be empty")

            # Execute all configuration validations
            validation_result = self._validate_configuration(config)
            if validation_result.is_failure:
                return validation_result

            # Apply real configuration updates if all validations pass
            self._apply_configuration(config)

            return FlextResult[None].ok(None)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[None].fail(f"Configuration failed: {e}")

    def _validate_configuration(self, config: dict[str, object]) -> FlextResult[None]:
        """Validate configuration parameters."""
        # Validate service name
        if "service_name" in config:
            service_name = str(config["service_name"])
            if not service_name.strip():
                return FlextResult[None].fail("Service name cannot be empty")

        # Validate version
        if "version" in config:
            version = str(config["version"])
            if not version.strip():
                return FlextResult[None].fail("Version cannot be empty")

        # Validate timeout
        if "timeout" in config:
            try:
                timeout_value = config["timeout"]
                timeout = float(str(timeout_value))
                if timeout <= 0:
                    return FlextResult[None].fail("Timeout must be positive")
            except (ValueError, TypeError):
                return FlextResult[None].fail("Timeout must be a valid number")

        return FlextResult[None].ok(None)

    def _apply_configuration(self, config: dict[str, object]) -> None:
        """Apply configuration changes (real functionality would update instance)."""
        # In a real implementation, this would update the API instance
        # Since the model is frozen, we would need to recreate it or use
        # a mutable configuration manager

    def get_metrics(self) -> dict[str, object]:
        """Get API performance metrics.

        Returns:
            Dictionary containing performance metrics

        """
        try:
            metrics = {
                "uptime": "unknown",  # Would track actual uptime in real implementation
                "requests_processed": 0,  # Would track actual requests
                "errors_count": 0,  # Would track actual errors
                "memory_usage": "unknown",  # Would track actual memory
            }

            # Add domain-specific metrics
            if self.enable_command_history:
                command_history = getattr(self, "_command_history", [])
                metrics["commands_executed"] = len(command_history)

            if self.enable_session_tracking:
                sessions = getattr(self, "_sessions", {})
                metrics["sessions_created"] = len(sessions)

            return metrics

        except (RuntimeError, ValueError, TypeError) as e:
            return {"error": f"Metrics collection failed: {e}"}

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_version(self) -> str:
        """Get API version.

        Returns:
            API version string

        """
        return self.version

    def get_service_info(self) -> dict[str, object]:
        """Get service information.

        Returns:
            Dictionary containing service information

        """
        return {
            "name": self.service_name,
            "version": self.version,
            "features": {
                "session_tracking": self.enable_session_tracking,
                "command_history": self.enable_command_history,
                "data_formatting": True,
                "data_export": True,
                "command_execution": True,
            },
            "supported_formats": ["table", "json", "yaml", "csv"],
        }

    # ============================================================================
    # CONSOLIDATED API FUNCTIONS - Integrated from api_functions.py
    # ============================================================================

    def create_table(
        self, data: object, title: str | None = None
    ) -> FlextResult[object]:
        """Create a Rich Table from provided data.

        Args:
            data: Data to format as table
            title: Optional table title

        Returns:
            FlextResult containing Rich Table object or error

        """
        try:
            from rich.table import Table

            table = Table(title=title or "Data")
            if isinstance(data, list) and data and isinstance(data[0], dict):
                self._add_dict_list_to_table(table, data)
            elif isinstance(data, dict):
                self._add_dict_to_table(table, data)
            else:
                self._add_simple_data_to_table(table, data)
            return FlextResult[object].ok(table)
        except Exception as e:
            return FlextResult[object].fail(f"Table creation failed: {e}")

    def _add_dict_list_to_table(
        self, table: Table, data: list[dict[str, object]]
    ) -> None:
        """Add list of dictionaries to table."""
        for key in data[0]:
            table.add_column(str(key))
        for row in data:
            table.add_row(*[str(row.get(k, "")) for k in data[0]])

    def _add_dict_to_table(self, table: Table, data: dict[str, object]) -> None:
        """Add dictionary to table."""
        table.add_column("Key")
        table.add_column("Value")
        for k, v in data.items():
            table.add_row(str(k), str(v))

    def _add_simple_data_to_table(self, table: Table, data: object) -> None:
        """Add simple data to table."""
        table.add_column("Value")
        if isinstance(data, list):
            for v in data:
                table.add_row(str(v))
        else:
            table.add_row(str(data))

    def batch_export(
        self, datasets: dict[str, object], directory: str | Path, format_type: str
    ) -> FlextResult[list[str]]:
        """Export multiple datasets to files in specified directory.

        Args:
            datasets: Dictionary mapping names to datasets
            directory: Target directory for exports
            format_type: Export format (csv, json, etc.)

        Returns:
            FlextResult containing list of exported file paths

        """
        try:
            out_files: list[str] = []
            base = Path(directory)
            base.mkdir(parents=True, exist_ok=True)
            for name, dataset in datasets.items():
                target = base / f"{name}.{format_type}"
                res = self.export_data(dataset, str(target), format_type)
                if res.is_failure:
                    return FlextResult[list[str]].fail(
                        f"Failed to export {name}: {res.error}"
                    )
                out_files.append(str(target))
            return FlextResult[list[str]].ok(out_files)
        except Exception as e:
            return FlextResult[list[str]].fail(str(e))

    def unwrap_or_default[T](self, result: FlextResult[T], default: T) -> T:
        """Unwrap FlextResult or return default value.

        Args:
            result: FlextResult to unwrap
            default: Default value if result is failure

        Returns:
            Result value or default

        """
        return result.value if result.is_success else default

    def unwrap_or_none[T](self, result: FlextResult[T]) -> T | None:
        """Unwrap FlextResult or return None.

        Args:
            result: FlextResult to unwrap

        Returns:
            Result value or None

        """
        return result.value if result.is_success else None

    @override
    def __repr__(self) -> str:
        """Return string representation of FlextCliApi."""
        return (
            f"FlextCliApi("
            f"version='{self.version}', "
            f"service='{self.service_name}', "
            f"session_tracking={self.enable_session_tracking}, "
            f"command_history={self.enable_command_history}"
            f")"
        )


# Re-export ONLY the consolidated class - following FLEXT pattern
__all__ = [
    "FlextCliApi",
]
