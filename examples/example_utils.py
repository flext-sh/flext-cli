"""Common utilities for FLEXT CLI examples.

Eliminates code duplication across example files by providing shared patterns
and common functionality using ONLY FlextCli wrappers - NO direct Rich imports!
All data transport uses Pydantic v2 models from flext_cli (m.Cli).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel

from flext_cli import FlextCli, m, r


def to_json_dict(
    data: Mapping[str, object],
) -> m.Cli.DisplayData:
    """Normalize config/mapping to DisplayData for create_table/display_config_table."""
    normalized = m.Cli.CliNormalizedJson.model_validate(dict(data)).root
    resolved = m.Cli.NormalizedJsonDict(value=normalized, default={}).resolved
    result_dict: object = dict(resolved.items())
    return m.Cli.DisplayData.model_validate({"data": result_dict})


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
        "\nAll operations used r pattern for error handling!",
        style="yellow",
    )


def handle_command_result(
    cli: FlextCli,
    result: r[BaseModel],
    action: str,
    success_fields: list[str] | None = None,
) -> None:
    """Generic handler for CQRS command results. Accepts r[BaseModel] only."""
    success_fields = success_fields or ["id", "status"]

    if result.is_success:
        raw = result.value
        data = raw.model_dump()
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
        "This failure demonstrates r error handling!",
        style="yellow",
    )
    cli.print(
        "The error was caught and wrapped in a r for clean handling.",
        style="white",
    )


def display_config_table(
    cli: FlextCli,
    config_data: BaseModel,
    headers: list[str] | None = None,
) -> None:
    """Display configuration as a table. Accepts Pydantic model only; uses show_table."""
    if headers is None:
        headers = ["Setting", "Value"]
    payload = (
        config_data.data
        if isinstance(config_data, m.Cli.DisplayData)
        else config_data.model_dump()
    )
    cli.show_table(payload, headers=headers)


def display_success_summary(
    cli: FlextCli,
    operation: str,
    details: m.Cli.SuccessSummaryDetails | None = None,
) -> None:
    """Display a standardized success summary using FlextCli."""
    cli.print(
        f"✅ {operation} completed successfully!",
        style="bold green",
    )
    if details is not None:
        for key, value in details.root.items():
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
