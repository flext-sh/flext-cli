"""Common utilities for FLEXT CLI examples.

Eliminates code duplication across example files by providing shared patterns
and common functionality using ONLY FlextCli wrappers - NO direct Rich imports!

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping

from flext_cli import FlextCli, r, t


def to_json_dict(
    data: Mapping[str, t.ContainerValue],
) -> dict[str, t.JsonValue]:
    """Normalize config/mapping to dict[str, JsonValue] for create_table/display_config_table.

    Use when you have dict[str, ContainerValue] (e.g. from to_dict_json or
    transform) and need to pass to APIs that expect Mapping[str, JsonValue].
    """
    out: dict[str, t.JsonValue] = {}
    for k, v in data.items():
        if v is None:
            out[k] = ""
        elif isinstance(v, (str, int, float, bool)):
            out[k] = v
        elif isinstance(v, (list, dict)):
            out[k] = str(v)
        else:
            out[k] = str(v)
    return out


def print_demo_completion(
    cli: FlextCli,
    demo_name: str,
    features: list[str],
    *,
    style: str = "green",
) -> None:
    """Print standardized demo completion message using FlextCli."""
    cli.print(f"\n🎉 {demo_name} Complete", style=f"bold {style}")
    cli.print(f"✅ {demo_name} Completed!", style=style)
    cli.print("\nKey Features Demonstrated:", style="cyan")
    for feature in features:
        cli.print(f"  • {feature}", style="white")
    cli.print(
        "\nAll operations used FlextResult pattern for error handling!",
        style="yellow",
    )


def handle_command_result(
    cli: FlextCli,
    result: r[dict[str, t.JsonValue]],
    action: str,
    success_fields: list[str] | None = None,
) -> None:
    """Generic handler for CQRS command results using FlextCli.

    Args:
        cli: FlextCli instance
        result: FlextResult from command operation
        action: Action being performed (e.g., "create project", "change status")
        success_fields: Fields to display on success (defaults to ['id', 'status'])

    """
    success_fields = success_fields or ["id", "status"]

    if result.is_success:
        data = result.value
        cli.print(f"✅ {action.title()} successful", style="green")
        for field in success_fields:
            if field in data:
                display_name = field.replace("_", " ").title()
                cli.print(f"{display_name}: {data[field]}")
    else:
        cli.print(f"❌ Failed to {action}: {result.error}", style="red")


def print_demo_error(
    cli: FlextCli,
    demo_name: str,
    error: str,
    *,
    style: str = "red",
) -> None:
    """Print standardized demo error message."""
    cli.print(f"❌ {demo_name} failed: {error}", style=f"bold {style}")
    cli.print(
        "This failure demonstrates FlextResult error handling!",
        style="yellow",
    )
    cli.print(
        "The error was caught and wrapped in a FlextResult for clean handling.",
        style="white",
    )


def display_config_table(
    cli: FlextCli,
    config_data: dict[str, t.JsonValue],
    headers: list[str] | None = None,
) -> None:
    """Display configuration as a table. Uses show_table; no result to capture."""
    if headers is None:
        headers = ["Setting", "Value"]
    cli.show_table(config_data, headers=headers)


def display_success_summary(
    cli: FlextCli,
    operation: str,
    details: dict[str, str] | None = None,
) -> None:
    """Display a standardized success summary using FlextCli."""
    cli.print(
        f"✅ {operation} completed successfully!",
        style="bold green",
    )
    if details:
        for key, value in details.items():
            cli.print(f"   {key}: {value}", style="cyan")


def display_validation_errors(
    cli: FlextCli,
    errors: list[str],
    context: str = "validation",
) -> None:
    """Display validation errors in a consistent format using FlextCli."""
    cli.print(
        f"❌ {context.title()} failed with {len(errors)} error(s):",
        style="bold red",
    )
    for i, error in enumerate(errors, 1):
        cli.print(f"   {i}. {error}", style="red")


__all__ = [
    "display_config_table",
    "display_success_summary",
    "display_validation_errors",
    "handle_command_result",
    "print_demo_completion",
    "print_demo_error",
    "to_json_dict",
]
