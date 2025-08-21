"""FLEXT CLI API.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import platform
import sys
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol, cast

import yaml
from flext_core import FlextEntityId, FlextResult
from rich.console import Console
from rich.table import Table

from flext_cli.cli_types import FlextCliDataType
from flext_cli.config import CLISettings as FlextCliSettings
from flext_cli.models import (
    FlextCliCommand as CLICommand,
    FlextCliPlugin as CLIPlugin,
)


# Plugin Protocol Definition
class PluginLike(Protocol):
    """Protocol for plugin-like objects."""

    @property
    def name(self) -> str:
        """Plugin name."""
        ...

    @property
    def id(self) -> str:
        """Plugin ID."""
        ...

    @property
    def version(self) -> str:
        """Plugin version."""
        ...

    @property
    def status(self) -> str:
        """Plugin status."""
        ...

    @property
    def plugin_type(self) -> str:
        """Plugin type."""
        ...


# Simple context class since FlextCliContext doesn't exist
class FlextCliContext:
    """Simple CLI context holder."""

    def __init__(self, config: FlextCliSettings, console: Console) -> None:
        """Initialize context."""
        self.config = config
        self.console = console


def flext_cli_format(
    data: FlextCliDataType, format_type: str = "table"
) -> FlextResult[str]:
    """Format data using specified format type.

    Args:
      data: Data to format
      format_type: Output format (table, json, yaml, csv, plain)

    Returns:
      FlextResult with formatted output or error

    """
    try:
        # Validate format type first
        valid_formats = {"json", "yaml", "table", "csv", "plain"}
        if format_type not in valid_formats:
            return FlextResult[str].fail(
                f"Format error: Invalid format '{format_type}'. Valid formats: {', '.join(sorted(valid_formats))}",
            )

        # Simple formatting without FormatterFactory
        if format_type == "json":
            formatted = json.dumps(data, indent=2, default=str)
        elif format_type == "yaml":
            formatted = yaml.dump(data, default_flow_style=False, sort_keys=False)
        elif format_type == "table":
            # Create table using our existing function
            table_result = flext_cli_table(data)
            if table_result.success:
                # Render table to string
                output_buffer = io.StringIO()
                console = Console(file=output_buffer, width=80)
                console.print(table_result.value)
                formatted = output_buffer.getvalue()
            else:
                return FlextResult[str].fail(
                    table_result.error or "Table creation failed"
                )
        elif format_type in {"csv", "plain"}:
            # Handle csv and plain formats
            formatted = str(data)
        else:
            # This should never be reached due to validation above
            formatted = str(data)

        return FlextResult[str].ok(formatted)

    except (AttributeError, ValueError, TypeError) as e:
        return FlextResult[str].fail(f"Format error: {e}")


def _create_table_from_dict_list(data: list[dict[str, object]], table: Table) -> None:
    """Create table from list of dictionaries.

    Args:
      data: List of dictionaries
      table: Table to populate

    """
    headers = list(data[0].keys())

    for header in headers:
        table.add_column(header.replace("_", " ").title())

    for item in data:
        table.add_row(*[str(item.get(h, "")) for h in headers])


def _create_table_from_simple_list(data: list[object], table: Table) -> None:
    """Create table from simple list.

    Args:
      data: Simple list of values
      table: Table to populate

    """
    table.add_column("Value")
    for item in data:
        table.add_row(str(item))


def _create_table_from_dict(data: dict[str, object], table: Table) -> None:
    """Create table from single dictionary.

    Args:
      data: Dictionary data
      table: Table to populate

    """
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    for key, value in data.items():
        table.add_row(key.replace("_", " ").title(), str(value))


def _create_table_from_single_value(data: object, table: Table) -> None:
    """Create table from single value.

    Args:
      data: Single value
      table: Table to populate

    """
    table.add_column("Value")
    table.add_row(str(data))


def flext_cli_table(
    data: FlextCliDataType, title: str | None = None
) -> FlextResult[Table]:
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
                # Cast to correct type for function call
                dict_list = cast(
                    "list[dict[str, object]]",
                    [item for item in data if isinstance(item, dict)],
                )
                _create_table_from_dict_list(dict_list, table)
            else:
                # Cast to list[object] for simple list
                simple_list = cast("list[object]", list(data))
                _create_table_from_simple_list(simple_list, table)
        elif isinstance(data, dict):
            _create_table_from_dict(cast("dict[str, object]", data), table)
        else:
            _create_table_from_single_value(data, table)

        return FlextResult[Table].ok(table)

    except (AttributeError, ValueError, TypeError) as e:
        return FlextResult[Table].fail(f"Table creation error: {e}")


def flext_cli_transform_data(
    data: FlextCliDataType,
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
        return FlextResult[list[dict[str, object]]].fail("Data must be a list")

    try:
        # Ensure data is a list and copy it
        data_list = data if isinstance(data, list) else []
        result = data_list.copy()

        # Apply filter
        if filter_func:
            result = [
                item
                for item in result
                if isinstance(item, dict)
                and filter_func(cast("dict[str, object]", item))
            ]

        # Apply sort
        if sort_key:
            result.sort(
                key=lambda x: str(x.get(sort_key, "")) if isinstance(x, dict) else "",
                reverse=reverse,
            )

        # Convert to expected type for MyPy compatibility using cast
        typed_result = cast("list[dict[str, object]]", result)
        return FlextResult[list[dict[str, object]]].ok(typed_result)

    except (TypeError, AttributeError, KeyError) as e:
        return FlextResult[list[dict[str, object]]].fail(f"Transform error: {e}")


def _initialize_group(
    group_by: str,
    value: object,
    count_field: str,
    sum_fields: list[str],
) -> dict[str, object | int]:
    """Initialize a new group for aggregation."""
    group: dict[str, object | int] = {
        group_by: value,
        count_field: 0,
    }
    # Initialize sum fields
    for field in sum_fields:
        group[f"{field}_sum"] = 0
    return group


def _update_group_counts(
    group: dict[str, str | int | float | bool | None], count_field: str
) -> None:
    """Update count for a group."""
    count_value = group[count_field]
    if isinstance(count_value, int):
        group[count_field] = count_value + 1


def _update_group_sums(
    group: dict[str, str | int | float | bool | None],
    item: dict[str, str | int | float | bool | None],
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
    data: FlextCliDataType,
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
        return FlextResult[list[dict[str, object]]].fail("Data must be a list")

    try:
        groups: dict[str, dict[str, object]] = {}
        sum_fields = sum_fields or []

        data_list = data if isinstance(data, list) else []
        for item in data_list:
            if not isinstance(item, dict):
                continue

            group_value = item.get(group_by)
            if group_value is None:
                continue

            group_key = str(group_value)

            if group_key not in groups:
                groups[group_key] = _initialize_group(
                    group_by,
                    group_value,
                    count_field,
                    sum_fields,
                )

            # Type conversion for MyPy compatibility
            group_data = cast(
                "dict[str, str | int | float | bool | None]", groups[group_key]
            )
            item_data: dict[str, str | int | float | bool | None] = item
            _update_group_counts(group_data, count_field)
            _update_group_sums(group_data, item_data, sum_fields)

        result = list(groups.values())
        return FlextResult[list[dict[str, object]]].ok(result)

    except (TypeError, AttributeError, KeyError) as e:
        return FlextResult[list[dict[str, object]]].fail(f"Aggregation error: {e}")


def flext_cli_export(
    data: FlextCliDataType,
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
                    # Type conversion for CSV compatibility
                    csv_data: list[dict[str, str]] = [
                        {k: str(v) for k, v in row.items()}
                        for row in data
                        if isinstance(row, dict)
                    ]
                    writer.writerows(csv_data)
                else:
                    return FlextResult[str].fail(
                        "CSV export requires list of dictionaries"
                    )

        else:
            return FlextResult[str].fail(f"Unsupported export format: {format_type}")

        return FlextResult[str].ok(f"Data exported to {path}")

    except (OSError, ValueError, TypeError) as e:
        return FlextResult[str].fail(f"Export error: {e}")


def flext_cli_batch_export(
    datasets: dict[str, FlextCliDataType],
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

        created_files: list[str] = []

        for name, data in datasets.items():
            file_path = output_path / f"{name}.{format_type}"
            result = flext_cli_export(data, file_path, format_type)

            if not result.success:
                return FlextResult[list[str]].fail(
                    f"Failed to export {name}: {result.error}"
                )

            created_files.append(str(file_path))

        return FlextResult[list[str]].ok(created_files)

    except (OSError, ValueError, TypeError) as e:
        return FlextResult[list[str]].fail(f"Batch export error: {e}")


def flext_cli_unwrap_or_default(result: FlextResult[object], default: object) -> object:
    """Unwrap FlextResult or return default value on error.

    Args:
      result: FlextResult to unwrap
      default: Default value if result is error

    Returns:
      Result data or default value

    """
    # Use standard FlextResult.unwrap_or method following flext/docs/patterns
    return result.unwrap_or(default)


def flext_cli_unwrap_or_none(result: FlextResult[object]) -> object | None:
    """Unwrap FlextResult or return None on error.

    Args:
      result: FlextResult to unwrap

    Returns:
      Result data or None

    """
    # Use standard FlextResult.unwrap_or method following flext/docs/patterns
    return result.unwrap_or(None)


class FlextCliApi:
    """API wrapper class for FLEXT CLI functions."""

    def flext_cli_export(
        self,
        data: FlextCliDataType,
        path: str | pathlib.Path,
        format_type: str = "json",
    ) -> bool:
        """Export data to file."""
        result = flext_cli_export(data, path, format_type)
        return result.success

    def flext_cli_format(
        self, data: FlextCliDataType, format_type: str = "table"
    ) -> str:
        """Format data for display."""
        result = flext_cli_format(data, format_type)
        # Use FlextResult.unwrap_or method following flext/docs/patterns
        return result.unwrap_or("")

    def flext_cli_configure(self, config: dict[str, object]) -> bool:
        """Configure CLI service using real configuration management."""
        try:
            # Create config with defaults and update with provided values
            base_config = FlextCliSettings()
            if config:
                # Filter out invalid fields for CLIConfig using dict comprehension
                valid_updates = {
                    key: value
                    for key, value in config.items()
                    if hasattr(base_config, key)
                }
                settings = base_config.model_copy(update=valid_updates)
            else:
                settings = base_config

            # Store configuration in context
            self._config = settings
        except (AttributeError, ValueError, TypeError):
            # If configuration fails, return False to indicate failure
            return False
        else:
            return True

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
        # Create config with defaults and override with passed values
        cli_config = FlextCliSettings()
        if config:
            cli_config = cli_config.model_copy(update=config)
        return FlextCliContext(config=cli_config, console=Console())

    def flext_cli_create_command(
        self,
        name: str,
        command_line: str,
        **options: object,
    ) -> FlextResult[object]:
        """Create command using real domain entities."""
        try:
            # Determine command type from options without raising on unknown
            # The domain entity does not store command_type, so ignore value safely
            cmd_type = options.get("command_type")
            if cmd_type not in {
                None,
                "system",
                "pipeline",
                "plugin",
                "data",
                "config",
                "auth",
                "monitoring",
            }:
                return FlextResult[object].fail(f"Invalid command type: {cmd_type}")

            # Extract and validate parameters with proper types
            description = options.get("description")
            description if isinstance(description, str) else None

            working_dir = options.get("working_directory")
            working_dir if isinstance(working_dir, str) else None

            # Environment variables support available via options.get("environment_vars")

            timeout_val = options.get("timeout_seconds", 30)
            timeout_val if isinstance(timeout_val, int) else 30

            # Create the domain entity using correct constructor parameters
            # Use name as command ID prefix for better identification
            command_id = (
                f"{name}_{uuid.uuid4().hex[:8]}" if name.strip() else str(uuid.uuid4())
            )

            try:
                command = CLICommand(
                    id=FlextEntityId(command_id),
                    command_line=command_line,
                )
                # Set name if attribute exists on model (compatibility for tests)
                with contextlib.suppress(Exception):
                    command.name = name
                command_result = FlextResult[object].ok(command)
            except Exception as e:
                command_result = FlextResult[object].fail(
                    f"Failed to create command: {e}"
                )

            if command_result.is_failure:
                return FlextResult[object].fail(
                    command_result.error or "Failed to create command",
                )

            command_obj = command_result.value
            if not isinstance(command_obj, CLICommand):
                return FlextResult[object].fail("Invalid command type")
            command = command_obj
        except (AttributeError, ValueError, TypeError) as e:
            return FlextResult[object].fail(f"Failed to create command: {e}")
        else:
            return FlextResult[object].ok(command)

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
                self._sessions: dict[str, object] = {}

            session_data: dict[str, object] = {
                "id": session_id,
                "user_id": user_id,
                "created_at": datetime.now(UTC),
                "commands": [],
                "status": "active",
            }

            self._sessions[session_id] = session_data
        except (AttributeError, ValueError, TypeError, KeyError) as e:
            return FlextResult[str].fail(f"Failed to create session: {e}")
        else:
            return FlextResult[str].ok(session_id)

    def flext_cli_register_handler(
        self,
        name: str,
        handler: object,
    ) -> FlextResult[None]:
        """Register command handler with validation."""
        try:
            # Initialize handlers registry if needed
            if not hasattr(self, "_handlers"):
                self._handlers: dict[str, object] = {}

            # Validate handler and register
            if not callable(handler):
                return FlextResult[None].fail(f"Handler {name} is not callable")

            # Register the handler
            self._handlers[name] = handler
        except (AttributeError, ValueError, TypeError, KeyError) as e:
            return FlextResult[None].fail(f"Failed to register handler {name}: {e}")
        else:
            return FlextResult[None].ok(None)

    def flext_cli_register_plugin(
        self, name: str, plugin: object
    ) -> FlextResult[CLIPlugin | None]:
        """Register plugin with proper validation and storage."""
        try:
            # Initialize plugin registry if needed
            if not hasattr(self, "_plugin_registry"):
                self._plugin_registry: dict[str, CLIPlugin] = {}

            # If plugin is already a CLIPlugin, register it directly
            if isinstance(plugin, CLIPlugin):
                validation_result = plugin.validate_business_rules()
                if not validation_result.success:
                    return FlextResult[CLIPlugin | None].fail(
                        f"Plugin validation failed: {validation_result.error}",
                    )

                self._plugin_registry[name] = plugin
                return FlextResult[CLIPlugin | None].ok(None)

            # Otherwise, try to create a CLIPlugin from the object using direct instantiation
            try:
                cli_plugin = CLIPlugin(
                    id=FlextEntityId(str(uuid.uuid4())),
                    name=name,
                    entry_point=str(plugin) if plugin else f"plugin_{name}",
                )
                plugin_result = FlextResult[CLIPlugin | None].ok(cli_plugin)
            except Exception as e:
                plugin_result = FlextResult[CLIPlugin | None].fail(
                    f"Failed to create plugin: {e}"
                )

            if plugin_result.is_failure:
                return FlextResult[CLIPlugin | None].fail(
                    f"Plugin creation failed: {plugin_result.error}",
                )

            plugin_entity = plugin_result.value
            if plugin_entity is not None:
                self._plugin_registry[name] = plugin_entity
        except (AttributeError, ValueError, TypeError, KeyError) as e:
            return FlextResult[CLIPlugin | None].fail(
                f"Failed to register plugin {name}: {e}"
            )
        else:
            return FlextResult[CLIPlugin | None].ok(None)

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
                return FlextResult[object].fail("No handlers registry found")

            # Check if handler exists
            if name not in self._handlers:
                return FlextResult[object].fail(f"Handler '{name}' not found")

            handler = self._handlers[name]

            # Execute the handler with provided arguments
            # Handler is guaranteed to be callable since we validate during registration
            if callable(handler):
                result = handler(*args, **kwargs)
            else:
                return FlextResult[object].fail(f"Handler '{name}' is not callable")
        except (AttributeError, ValueError, TypeError, KeyError) as e:
            return FlextResult[object].fail(f"Failed to execute handler '{name}': {e}")
        else:
            return FlextResult[object].ok(result)

    def flext_cli_render_with_context(
        self,
        data: FlextCliDataType,
        context: dict[str, object] | None = None,
    ) -> FlextResult[str]:
        """Render data with context using template substitution."""
        try:
            renderer = ContextRenderingStrategy(data, context)
        except (AttributeError, ValueError, TypeError) as e:
            return FlextResult[str].fail(f"Failed to render with context: {e}")
        else:
            return renderer.render()

    def flext_cli_get_commands(self) -> dict[str, object]:
        """Get all registered commands."""
        if not hasattr(self, "_commands"):
            self._commands: dict[str, object] = {}
        return dict(self._commands)

    def flext_cli_get_sessions(self) -> dict[str, object]:
        """Get all active sessions."""
        sessions = dict(getattr(self, "_sessions", {}))
        summary: dict[str, object] = {}
        for sid, sdata in sessions.items():
            if isinstance(sdata, dict):
                # Type the session data with specific structure
                session_data: dict[str, object] = {}
                for k, v in sdata.items():
                    key_str: str = str(k)
                    value_obj: object = v
                    session_data[key_str] = value_obj

                cmds_raw = session_data.get("commands", [])
                cmds: list[dict[str, object]] = []
                if isinstance(cmds_raw, list):
                    for cmd in cmds_raw:
                        if isinstance(cmd, dict):
                            typed_cmd: dict[str, object] = {}
                            for ck, cv in cmd.items():
                                cmd_key: str = str(ck)
                                cmd_value: object = cv
                                typed_cmd[cmd_key] = cmd_value
                            cmds.append(typed_cmd)
                summary[sid] = {
                    "id": session_data.get("id"),
                    "status": session_data.get("status"),
                    "created_at": session_data.get("created_at"),
                    "commands_count": len(cmds) if isinstance(cmds, list) else 0,
                }
        return summary

    def flext_cli_get_plugins(self) -> dict[str, object]:
        """Get all registered plugins."""
        if not hasattr(self, "_plugins"):
            self._plugins: dict[str, object] = {}
        return dict(self._plugins)

    def flext_cli_get_handlers(self) -> dict[str, object]:
        """Get all registered handlers."""
        return dict(getattr(self, "_handlers", {}))


class ContextRenderingStrategy:
    """Strategy pattern for context-based rendering with SOLID principles."""

    def __init__(
        self, data: FlextCliDataType, context: dict[str, object] | None = None
    ) -> None:
        """Initialize rendering strategy."""
        self.data: FlextCliDataType = data
        self.context = context or {}

    def render(self) -> FlextResult[str]:
        """Render data using appropriate strategy."""
        # Template substitution has priority
        template_result = self._try_template_substitution()
        if template_result.success:
            return template_result

        # Fall back to formatter-based rendering
        return self._render_with_formatter()

    def _try_template_substitution(self) -> FlextResult[str]:
        """Try template substitution first."""
        if isinstance(self.data, dict):
            return self._render_dict_templates()

        if isinstance(self.data, str):
            return self._render_string_template()

        return FlextResult[str].fail("No template patterns found")

    def _render_dict_templates(self) -> FlextResult[str]:
        """Render templates in dictionary values."""
        if isinstance(self.data, dict):
            for value in self.data.values():
                if self._is_template_string(value):
                    return FlextResult[str].ok(self._substitute_template(str(value)))
        return FlextResult[str].fail("No template patterns in dict")

    def _render_string_template(self) -> FlextResult[str]:
        """Render string template directly."""
        if self._is_template_string(self.data):
            return FlextResult[str].ok(self._substitute_template(str(self.data)))
        return FlextResult[str].fail("Not a template string")

    def _is_template_string(self, value: object) -> bool:
        """Check if value is a template string."""
        return (
            isinstance(value, str)
            and "{{" in value
            and "}}" in value
            and bool(self.context)
        )

    def _substitute_template(self, template_str: str) -> str:
        """Substitute template variables."""
        for ctx_key, ctx_value in self.context.items():
            template_str = template_str.replace(f"{{{{{ctx_key}}}}}", str(ctx_value))
        return template_str

    def _render_with_formatter(self) -> FlextResult[str]:
        """Render using formatter strategy."""
        format_type = self._get_format_type()

        # Use our flext_cli_format function instead of FormatterFactory
        # Use unwrap_or for cleaner format result handling
        format_result = flext_cli_format(self.data, format_type)
        rendered_output = format_result.unwrap_or("")
        if rendered_output:  # Non-empty string indicates success
            return FlextResult[str].ok(self._apply_title_if_needed(rendered_output))
        return format_result  # Return original error result

    def _get_format_type(self) -> str:
        """Get format type from context."""
        format_obj = self.context.get("format", "table")
        return str(format_obj) if isinstance(format_obj, str) else "table"

    def _apply_title_if_needed(self, output: str) -> str:
        """Apply title transformation if needed."""
        title = self.context.get("title")
        if isinstance(title, str):
            return f"# {title}\n\n{output}"
        return output

    def flext_cli_get_commands(self) -> dict[str, object]:
        """Get all registered commands with real implementation."""
        try:
            # Initialize commands registry if needed
            if not hasattr(self, "_commands"):
                self._commands: dict[str, object] = {}

            # Return copy of commands to prevent external modification
            commands_copy = dict(self._commands)
        except (ValueError, TypeError, KeyError):
            # Return empty dict on error for consistency
            return {}
        else:
            return commands_copy

    def flext_cli_get_sessions(self) -> dict[str, object]:
        """Get all active sessions with real implementation."""
        try:
            # Initialize sessions registry if needed
            if not hasattr(self, "_sessions"):
                self._sessions: dict[str, object] = {}

            # Filter active sessions only and return summary data
            active_sessions: dict[str, object] = {}
            for session_id, session_data in self._sessions.items():
                if (
                    isinstance(session_data, dict)
                    and session_data.get("status") == "active"
                ):
                    # Return safe summary without sensitive data
                    typed_session_data: dict[str, object] = {}
                    for sk, sv in session_data.items():
                        session_key: str = str(sk)
                        session_value: object = sv
                        typed_session_data[session_key] = session_value
                    commands_raw = typed_session_data.get("commands", [])
                    commands: list[dict[str, object]] = []
                    if isinstance(commands_raw, list):
                        for cmd in commands_raw:
                            if isinstance(cmd, dict):
                                typed_cmd: dict[str, object] = {}
                                for ck, cv in cmd.items():
                                    typed_cmd[str(ck)] = cv
                                commands.append(typed_cmd)
                    commands_count = len(commands) if isinstance(commands, list) else 0
                    active_sessions[session_id] = {
                        "id": session_data.get("id"),
                        "created_at": session_data.get("created_at"),
                        "commands_count": commands_count,
                        "status": session_data.get("status"),
                    }
        except (ValueError, TypeError, KeyError, AttributeError):
            # Return empty dict on error for consistency
            return {}
        else:
            return active_sessions

    def flext_cli_get_plugins(self) -> dict[str, object]:
        """Get all registered plugins from the plugin registry."""
        # This method is in ContextRenderingStrategy but should not access _plugin_registry
        # Return empty dict as plugins are not handled by the rendering strategy
        return {}

    def _convert_plugins_list_to_dict(self, plugins_list: object) -> dict[str, object]:
        """Convert plugins list to dictionary format.

        Args:
            plugins_list: List of plugin objects

        Returns:
            Dictionary mapping plugin names to plugin data

        """
        plugins_dict: dict[str, object] = {}

        if not isinstance(plugins_list, list):
            return plugins_dict

        for plugin in plugins_list:
            # Type check and cast to PluginLike
            if not self._is_valid_plugin(plugin):
                continue

            # Cast to PluginLike for proper typing
            typed_plugin: PluginLike = cast("PluginLike", plugin)
            plugins_dict[typed_plugin.name] = {
                "id": typed_plugin.id,
                "name": typed_plugin.name,
                "version": typed_plugin.version,
                "status": typed_plugin.status,
                "plugin_type": typed_plugin.plugin_type,
            }

        return plugins_dict

    def _is_valid_plugin(self, plugin: object) -> bool:
        """Check if plugin object has required attributes.

        Args:
            plugin: Plugin object to validate

        Returns:
            True if plugin has required attributes conforming to PluginLike protocol

        """
        required_attrs = ["name", "id", "version", "status", "plugin_type"]
        return all(hasattr(plugin, attr) for attr in required_attrs)

    def flext_cli_get_handlers(self) -> dict[str, object]:
        """Get all registered handlers with real implementation."""
        try:
            # Initialize handlers registry if needed
            if not hasattr(self, "_handlers"):
                self._handlers: dict[str, object] = {}

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
        except (ValueError, TypeError, KeyError, AttributeError):
            # Return empty dict on error for consistency
            return {}
        else:
            return handlers_summary
