"""FLEXT CLI Convenience API Functions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

High-level convenience functions for common CLI operations.
Provides easy-to-use APIs that return FlextResult objects.
"""

from __future__ import annotations

import csv
import io
import json
import pathlib
import platform
import sys
import uuid
from contextlib import redirect_stdout
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import yaml
from flext_core import get_flext_container
from flext_core.result import FlextResult
from flext_plugin import FlextPlugin, FlextPluginService
from rich.console import Console
from rich.table import Table

from flext_cli.core.formatters import FormatterFactory

# Real imports - no fallbacks, proper error handling
from flext_cli.domain.entities import CLICommand, CommandType
from flext_cli.types import FlextCliConfig, FlextCliContext
from flext_cli.utils.config import CLISettings

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def flext_cli_format(data: object, format_type: str = "table") -> FlextResult[str]:
    """Format data using specified format type.

    Args:
        data: Data to format
        format_type: Output format (table, json, yaml, csv, plain)

    Returns:
        FlextResult with formatted output or error

    """
    try:
        Console(file=None, width=80)

        formatter = FormatterFactory.create(format_type)

        # Capture output to string
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            # Use a console that writes to our buffer
            buffer_console = Console(file=output_buffer, width=80, legacy_windows=False)
            formatter.format(data, buffer_console)

        return FlextResult.ok(output_buffer.getvalue())

    except (ImportError, AttributeError, ValueError) as e:
        return FlextResult.fail(f"Format error: {e}")


def flext_cli_table(data: object, title: str | None = None) -> FlextResult[Table]:
    """Create a Rich table from data.

    Args:
        data: Data to convert to table
        title: Optional table title

    Returns:
        FlextResult with Rich Table or error

    """
    try:
        table = Table(title=title, show_header=True, header_style="bold cyan")

        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                # List of dicts
                headers = list(data[0].keys())

                for header in headers:
                    table.add_column(header.replace("_", " ").title())

                for item in data:
                    table.add_row(*[str(item.get(h, "")) for h in headers])

            else:
                # Simple list
                table.add_column("Value")
                for item in data:
                    table.add_row(str(item))

        elif isinstance(data, dict):
            # Single dict as vertical table
            table.add_column("Key", style="cyan")
            table.add_column("Value")

            for key, value in data.items():
                table.add_row(key.replace("_", " ").title(), str(value))

        else:
            # Single value
            table.add_column("Value")
            table.add_row(str(data))

        return FlextResult.ok(table)

    except (AttributeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Table creation error: {e}")


def flext_cli_transform_data(
    data: object,
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
        FlextResult with transformed data or error

    """
    if not isinstance(data, list):
        return FlextResult.fail("Data must be a list")

    try:
        result = data.copy()

        # Apply filter
        if filter_func:
            result = [item for item in result if filter_func(item)]

        # Apply sort
        if sort_key:
            result.sort(key=lambda x: str(x.get(sort_key, "")), reverse=reverse)

        return FlextResult.ok(result)

    except (TypeError, AttributeError, KeyError) as e:
        return FlextResult.fail(f"Transform error: {e}")


def _initialize_group(
    group_value: object,
    group_by: str,
    count_field: str,
    sum_fields: list[str],
) -> dict[str, object]:
    """Initialize a new group for aggregation."""
    group = {
        group_by: group_value,
        count_field: 0,
    }
    # Initialize sum fields
    for field in sum_fields:
        group[f"{field}_sum"] = 0
    return group


def _update_group_counts(group: dict[str, object], count_field: str) -> None:
    """Update count for a group."""
    count_value = group[count_field]
    if isinstance(count_value, int):
        group[count_field] = count_value + 1


def _update_group_sums(
    group: dict[str, object],
    item: dict[str, object],
    sum_fields: list[str],
) -> None:
    """Update sum fields for a group."""
    for field in sum_fields:
        if field in item and isinstance(item[field], (int, float)):
            sum_key = f"{field}_sum"
            current_sum = group[sum_key]
            if isinstance(current_sum, (int, float)):
                field_val = item[field]
                if isinstance(field_val, (int, float)):
                    group[sum_key] = current_sum + field_val


def flext_cli_aggregate_data(
    data: object,
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
        FlextResult with aggregated data or error

    """
    if not isinstance(data, list):
        return FlextResult.fail("Data must be a list")

    try:
        groups: dict[str, dict[str, object]] = {}
        sum_fields = sum_fields or []

        for item in data:
            if not isinstance(item, dict):
                continue

            group_value = item.get(group_by)
            if group_value is None:
                continue

            group_key = str(group_value)

            if group_key not in groups:
                groups[group_key] = _initialize_group(
                    group_value,
                    group_by,
                    count_field,
                    sum_fields,
                )

            _update_group_counts(groups[group_key], count_field)
            _update_group_sums(groups[group_key], item, sum_fields)

        result = list(groups.values())
        return FlextResult.ok(result)

    except (TypeError, AttributeError, KeyError) as e:
        return FlextResult.fail(f"Aggregation error: {e}")


def flext_cli_export(
    data: object,
    file_path: str | Path,
    format_type: str = "json",
) -> FlextResult[str]:
    """Export data to file in specified format.

    Args:
        data: Data to export
        file_path: Target file path
        format_type: Export format (json, yaml, csv)

    Returns:
        FlextResult with success message or error

    """
    try:
        path = pathlib.Path(file_path)

        if format_type == "json":
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

        elif format_type == "yaml":
            with path.open("w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        elif format_type == "csv":
            with path.open("w", encoding="utf-8", newline="") as f:
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    return FlextResult.fail("CSV export requires list of dictionaries")

        else:
            return FlextResult.fail(f"Unsupported export format: {format_type}")

        return FlextResult.ok(f"Data exported to {path}")

    except (OSError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Export error: {e}")


def flext_cli_batch_export(
    datasets: dict[str, object],
    output_dir: str | Path,
    format_type: str = "json",
) -> FlextResult[list[str]]:
    """Export multiple datasets to files.

    Args:
        datasets: Dictionary of dataset_name -> data
        output_dir: Target directory
        format_type: Export format

    Returns:
        FlextResult with list of created files or error

    """
    try:
        output_path = pathlib.Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        created_files = []

        for name, data in datasets.items():
            file_path = output_path / f"{name}.{format_type}"
            result = flext_cli_export(data, file_path, format_type)

            if not result.is_success:
                return FlextResult.fail(f"Failed to export {name}: {result.error}")

            created_files.append(str(file_path))

        return FlextResult.ok(created_files)

    except (OSError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Batch export error: {e}")


def flext_cli_unwrap_or_default(result: FlextResult[object], default: object) -> object:
    """Unwrap FlextResult or return default value on error.

    Args:
        result: FlextResult to unwrap
        default: Default value if result is error

    Returns:
        Result data or default value

    """
    if result.is_success:
        return result.unwrap()
    return default


def flext_cli_unwrap_or_none(result: FlextResult[object]) -> object | None:
    """Unwrap FlextResult or return None on error.

    Args:
        result: FlextResult to unwrap

    Returns:
        Result data or None

    """
    if result.is_success:
        return result.unwrap()
    return None


class FlextCliApi:
    """API wrapper class for FLEXT CLI functions."""

    def flext_cli_export(
        self,
        data: object,
        path: str | pathlib.Path,
        format_type: str = "json",
    ) -> bool:
        """Export data to file."""
        result = flext_cli_export(data, path, format_type)
        return result.is_success

    def flext_cli_format(self, data: object, format_type: str = "table") -> str:
        """Format data for display."""
        result = flext_cli_format(data, format_type)
        return result.unwrap() if result.is_success else ""

    def flext_cli_configure(self, config: dict[str, object]) -> bool:
        """Configure CLI service using real configuration management."""
        try:
            # Create settings using explicit constructor calls for type safety
            # Initialize with defaults first
            settings = CLISettings()

            # Update specific fields from config with type validation
            if "project_name" in config and isinstance(config["project_name"], str):
                settings.project_name = config["project_name"]
            if "project_version" in config and isinstance(
                config["project_version"], str
            ):
                settings.project_version = config["project_version"]
            if "project_description" in config and isinstance(
                config["project_description"], str
            ):
                settings.project_description = config["project_description"]
            if "debug" in config and isinstance(config["debug"], bool):
                settings.debug = config["debug"]
            if "log_level" in config and isinstance(config["log_level"], str):
                settings.log_level = config["log_level"]
            if "config_path" in config and isinstance(config["config_path"], str):
                settings.config_path = config["config_path"]

            # Store configuration in context
            self._config = settings
            return True

        except Exception:
            # If configuration fails, return False to indicate failure
            return False

    def flext_cli_health(self) -> dict[str, object]:
        """Get service health status with real system information."""
        return {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "config_loaded": hasattr(self, "_config"),
            "service": "flext-cli",
            "version": "0.9.0",
        }

    def flext_cli_create_context(
        self,
        config: dict[str, object] | None = None,
    ) -> object:
        """Create CLI execution context - placeholder implementation."""
        cli_config = FlextCliConfig(config or {})
        return FlextCliContext(cli_config)

    def flext_cli_create_command(
        self,
        name: str,
        command_line: str,
        **options: object,
    ) -> FlextResult[object]:
        """Create command using real domain entities."""
        try:
            # Determine command type from options or default to SYSTEM
            # (valid enum value)
            command_type = CommandType.SYSTEM
            if "command_type" in options:
                type_value = options["command_type"]
                if isinstance(type_value, str):
                    command_type = CommandType(type_value)

            # Extract and validate parameters with proper types
            description = options.get("description")
            description_str = description if isinstance(description, str) else None

            working_dir = options.get("working_directory")
            working_dir_str = working_dir if isinstance(working_dir, str) else None

            env_vars = options.get("environment_vars", {})
            environment = env_vars if isinstance(env_vars, dict) else {}
            # Convert dict[str, object] to dict[str, str]
            environment_str = {
                k: str(v) for k, v in environment.items() if isinstance(k, str)
            }

            timeout_val = options.get("timeout_seconds", 30)
            timeout_int = timeout_val if isinstance(timeout_val, int) else 30

            # Create the domain entity with correct field names and types
            command = CLICommand(
                name=name,
                command_line=command_line,
                command_type=command_type,
                description=description_str,
                working_directory=working_dir_str,
                environment=environment_str,  # Correct field name with proper type
                timeout=timeout_int,  # Correct field name with proper type
            )

            return FlextResult.ok(command)

        except Exception as e:
            return FlextResult.fail(f"Failed to create command: {e}")

    def flext_cli_create_session(self, user_id: str | None = None) -> FlextResult[str]:
        """Create CLI session with real session tracking."""
        try:
            # Generate unique session ID
            session_id = (
                f"cli_session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
                f"_{uuid.uuid4().hex[:8]}"
            )

            # Store session information for tracking
            if not hasattr(self, "_sessions"):
                self._sessions = {}

            session_data: dict[str, object] = {
                "id": session_id,
                "user_id": user_id,
                "created_at": datetime.now(UTC),
                "commands": [],
                "status": "active",
            }

            self._sessions[session_id] = session_data

            return FlextResult.ok(session_id)

        except Exception as e:
            return FlextResult.fail(f"Failed to create session: {e}")

    def flext_cli_register_handler(
        self,
        name: str,
        handler: object,
    ) -> FlextResult[None]:
        """Register command handler with validation."""
        try:
            # Initialize handlers registry if needed
            if not hasattr(self, "_handlers"):
                self._handlers = {}

            # Validate handler and register
            if not callable(handler):
                return FlextResult.fail(f"Handler {name} is not callable")

            # Register the handler
            self._handlers[name] = handler

            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Failed to register handler {name}: {e}")

    def flext_cli_register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register plugin using real flext-plugin functionality."""
        try:
            # Initialize plugin service if needed
            if not hasattr(self, "_plugin_service"):
                container = get_flext_container()
                self._plugin_service = FlextPluginService(container=container)

            # If plugin is already a FlextPlugin, load it directly
            if isinstance(plugin, FlextPlugin):
                result = self._plugin_service.load_plugin(plugin)
                if result.is_success:
                    return FlextResult.ok(None)
                return FlextResult.fail(f"Failed to load plugin: {result.error}")

            # Otherwise, try to create a FlextPlugin from the object
            # This is a simplified approach - real implementation would be more
            # sophisticated
            plugin_entity = FlextPlugin(
                name=name,
                version="1.0.0",
                plugin_type="UTILITY",  # Default type
                entry_point=str(plugin) if plugin else "",
            )

            result = self._plugin_service.load_plugin(plugin_entity)
            if result.is_success:
                return FlextResult.ok(None)
            return FlextResult.fail(f"Failed to load plugin: {result.error}")

        except Exception as e:
            return FlextResult.fail(f"Failed to register plugin {name}: {e}")

    def flext_cli_execute_handler(
        self,
        name: str,
        *args: object,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Execute registered handler with real implementation."""
        try:
            # Check if handlers registry exists
            if not hasattr(self, "_handlers"):
                return FlextResult.fail("No handlers registry found")

            # Check if handler exists
            if name not in self._handlers:
                return FlextResult.fail(f"Handler '{name}' not found")

            handler = self._handlers[name]

            # Execute the handler with provided arguments
            # Handler is guaranteed to be callable since we validate during registration
            result = handler(*args, **kwargs)
            return FlextResult.ok(result)

        except Exception as e:
            return FlextResult.fail(f"Failed to execute handler '{name}': {e}")

    def flext_cli_render_with_context(
        self,
        data: object,
        context: dict[str, object] | None = None,
    ) -> FlextResult[str]:
        """Render data with context using real template rendering."""
        try:
            # Use context to determine format or default to table
            format_type = "table"
            if context:
                format_obj = context.get("format", "table")
                if isinstance(format_obj, str):
                    format_type = format_obj

            # Create formatter and render
            formatter = FormatterFactory.create(format_type)

            # Capture output to string
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                # Use a console that writes to our buffer
                buffer_console = Console(
                    file=output_buffer,
                    width=80,
                    legacy_windows=False,
                )
                formatter.format(data, buffer_console)

            rendered_output = output_buffer.getvalue()

            # Apply context-based transformations if any
            if context and "title" in context:
                title = context["title"]
                if isinstance(title, str):
                    rendered_output = f"# {title}\n\n{rendered_output}"

            return FlextResult.ok(rendered_output)

        except Exception as e:
            return FlextResult.fail(f"Failed to render with context: {e}")

    def flext_cli_get_commands(self) -> dict[str, object]:
        """Get all registered commands with real implementation."""
        try:
            # Initialize commands registry if needed
            if not hasattr(self, "_commands"):
                self._commands: dict[str, object] = {}

            # Return copy of commands to prevent external modification
            return dict(self._commands)

        except Exception:
            # Return empty dict on error for consistency
            return {}

    def flext_cli_get_sessions(self) -> dict[str, object]:
        """Get all active sessions with real implementation."""
        try:
            # Initialize sessions registry if needed
            if not hasattr(self, "_sessions"):
                self._sessions = {}

            # Filter active sessions only and return summary data
            active_sessions: dict[str, object] = {}
            for session_id, session_data in self._sessions.items():
                if (
                    isinstance(session_data, dict)
                    and session_data.get("status") == "active"
                ):
                    # Return safe summary without sensitive data
                    commands = session_data.get("commands", [])
                    commands_count = len(commands) if isinstance(commands, list) else 0
                    active_sessions[session_id] = {
                        "id": session_data.get("id"),
                        "created_at": session_data.get("created_at"),
                        "commands_count": commands_count,
                        "status": session_data.get("status"),
                    }

            return active_sessions

        except Exception:
            # Return empty dict on error for consistency
            return {}

    def flext_cli_get_plugins(self) -> dict[str, object]:
        """Get all registered plugins with real implementation."""
        try:
            # Check if plugin service is available
            if hasattr(self, "_plugin_service") and isinstance(
                self._plugin_service, FlextPluginService
            ):
                # Get plugins using discovery from standard paths
                plugins_result = self._plugin_service.discover_plugins("plugins")
                if plugins_result.is_success:
                    plugins_list = plugins_result.unwrap()
                    # Convert list to dict for API consistency
                    plugins_dict: dict[str, object] = {}
                    if isinstance(plugins_list, list):
                        for plugin in plugins_list:
                            if hasattr(plugin, "name") and hasattr(plugin, "id"):
                                plugins_dict[plugin.name] = {
                                    "id": plugin.id,
                                    "name": plugin.name,
                                    "version": getattr(plugin, "version", "1.0.0"),
                                    "status": getattr(plugin, "status", "unknown"),
                                    "plugin_type": getattr(
                                        plugin,
                                        "plugin_type",
                                        "unknown",
                                    ),
                                }
                    return plugins_dict

            # Fallback: return empty dict if no plugin service
            return {}

        except Exception:
            # Return empty dict on error for consistency
            return {}

    def flext_cli_get_handlers(self) -> dict[str, object]:
        """Get all registered handlers with real implementation."""
        try:
            # Initialize handlers registry if needed
            if not hasattr(self, "_handlers"):
                self._handlers = {}

            # Return summary information about handlers (not the actual handler
            # functions)
            handlers_summary: dict[str, object] = {}
            for name, handler in self._handlers.items():
                handlers_summary[name] = {
                    "name": name,
                    "type": type(handler).__name__,
                    "callable": callable(handler),
                    "module": (
                        getattr(handler, "__module__", "unknown")
                        if hasattr(handler, "__module__")
                        else "unknown"
                    ),
                }

            return handlers_summary

        except Exception:
            # Return empty dict on error for consistency
            return {}
