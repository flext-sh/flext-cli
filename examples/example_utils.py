"""Common utilities for FLEXT CLI examples.

Eliminates code duplication across example files by providing shared patterns
and common functionality using ONLY FlextCli wrappers - NO direct Rich imports!

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import FlextCli, FlextCliTypes


def print_demo_completion(
    cli: FlextCli,
    demo_name: str,
    features: list[str],
    *,
    style: str = "green",
) -> None:
    """Print standardized demo completion message using FlextCli.

    Args:
        cli: FlextCli instance
        demo_name: Name of the completed demo
        features: List of features demonstrated
        style: Message style

    """
    cli.output.print_message(f"\n🎉 {demo_name} Complete", style=f"bold {style}")
    cli.output.print_message(f"✅ {demo_name} Completed!", style=style)
    cli.output.print_message("\nKey Features Demonstrated:", style="cyan")
    for feature in features:
        cli.output.print_message(f"  • {feature}", style="white")
    cli.output.print_message(
        "\nAll operations used FlextResult pattern for error handling!",
        style="yellow",
    )


def handle_command_result(
    cli: FlextCli,
    result: FlextResult[t.JsonDict],
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
        cli.output.print_message(f"✅ {action.title()} successful", style="green")

        for field in success_fields:
            if field in data:
                display_name = field.replace("_", " ").title()
                cli.output.print_message(f"{display_name}: {data[field]}")
    else:
        cli.output.print_message(f"❌ Failed to {action}: {result.error}", style="red")


def print_demo_error(
    cli: FlextCli,
    demo_name: str,
    error: str,
    *,
    style: str = "red",
) -> None:
    """Print standardized demo error message.

    Args:
        cli: FlextCli instance
        demo_name: Name of the failed demo
        error: Error message
        style: Message style

    """
    cli.output.print_message(f"❌ {demo_name} failed: {error}", style=f"bold {style}")
    cli.output.print_message(
        "This failure demonstrates FlextResult error handling!", style="yellow"
    )
    cli.output.print_message(
        "The error was caught and wrapped in a FlextResult for clean handling.",
        style="white",
    )


def display_config_table(
    cli: FlextCli,
    config_data: FlextCliTypes.Data.CliDataDict,
    title: str = "Configuration",
    headers: list[str] | None = None,
) -> None:
    """Display configuration data as a formatted table using FlextCli.

    Args:
        cli: FlextCli instance
        config_data: Configuration data dictionary
        title: Table title
        headers: Table headers (default: ["Setting", "Value"])

    """
    if headers is None:
        headers = ["Setting", "Value"]
    table_result = cli.create_table(
        data=config_data,
        headers=headers,
        title=title,
    )

    if table_result.is_success:
        cli.print_table(table_result.unwrap())
    else:
        cli.print(f"❌ Failed to create table: {table_result.error}", style="red")


def display_success_summary(
    cli: FlextCli,
    operation: str,
    details: dict[str, str] | None = None,
) -> None:
    """Display a standardized success summary using FlextCli.

    Args:
        cli: FlextCli instance
        operation: Name of the operation that succeeded
        details: Optional key-value details to display

    """
    cli.output.print_message(
        f"✅ {operation} completed successfully!", style="bold green"
    )

    if details:
        for key, value in details.items():
            cli.output.print_message(f"   {key}: {value}", style="cyan")


def display_validation_errors(
    cli: FlextCli,
    errors: list[str],
    context: str = "validation",
) -> None:
    """Display validation errors in a consistent format using FlextCli.

    Args:
        cli: FlextCli instance
        errors: List of error messages
        context: Context for the errors (default: "validation")

    """
    cli.output.print_message(
        f"❌ {context.title()} failed with {len(errors)} error(s):", style="bold red"
    )

    for i, error in enumerate(errors, 1):
        cli.output.print_message(f"   {i}. {error}", style="red")


__all__ = [
    "display_config_table",
    "display_success_summary",
    "display_validation_errors",
    "handle_command_result",
    "print_demo_completion",
    "print_demo_error",
]
