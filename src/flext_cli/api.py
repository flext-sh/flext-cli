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
import uuid
from contextlib import redirect_stdout
from typing import TYPE_CHECKING

import yaml
from flext_core.result import FlextResult
from rich.console import Console
from rich.table import Table

from flext_cli.core.formatters import FormatterFactory
from flext_cli.types import FlextCliConfig, FlextCliContext

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

    def flext_cli_configure(self, _config: dict[str, object]) -> bool:
        """Configure CLI service - placeholder implementation."""
        return True

    def flext_cli_health(self) -> dict[str, object]:
        """Get service health status - placeholder implementation."""
        return {"status": "healthy", "timestamp": "2025-01-29"}

    def flext_cli_create_context(
        self,
        config: dict[str, object] | None = None,
    ) -> object:
        """Create CLI execution context - placeholder implementation."""
        cli_config = FlextCliConfig(config or {})
        return FlextCliContext(cli_config)

    def flext_cli_create_command(
        self,
        _name: str,
        _command_line: str,
        **_options: object,
    ) -> bool:
        """Create command - placeholder implementation."""
        return True

    def flext_cli_create_session(self, _user_id: str | None = None) -> str:
        """Create session - placeholder implementation."""
        return f"session_{uuid.uuid4().hex[:8]}"

    def flext_cli_register_handler(self, _name: str, _handler: object) -> bool:
        """Register handler - placeholder implementation."""
        return True

    def flext_cli_register_plugin(self, _name: str, _plugin: object) -> bool:
        """Register plugin - placeholder implementation."""
        return True

    def flext_cli_execute_handler(
        self,
        name: str,
        *_args: object,
        **_kwargs: object,
    ) -> object:
        """Execute handler - placeholder implementation."""
        return {"result": "handler_executed", "name": name}

    def flext_cli_render_with_context(
        self,
        data: object,
        _context: dict[str, object] | None = None,
    ) -> str:
        """Render with context - placeholder implementation."""
        return json.dumps(data, default=str, indent=2)

    def flext_cli_get_commands(self) -> dict[str, object]:
        """Get all commands - placeholder implementation."""
        return {}

    def flext_cli_get_sessions(self) -> dict[str, object]:
        """Get all sessions - placeholder implementation."""
        return {}

    def flext_cli_get_plugins(self) -> dict[str, object]:
        """Get all plugins - placeholder implementation."""
        return {}

    def flext_cli_get_handlers(self) -> dict[str, object]:
        """Get all handlers - placeholder implementation."""
        return {}
