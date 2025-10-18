"""Common utilities for FLEXT CLI examples.

Eliminates code duplication across example files by providing shared patterns
and common functionality using ONLY FlextCli wrappers - NO direct Rich imports!

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli import FlextCli


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
    result: FlextResult[dict[str, object]],
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
    cli: FlextCli, demo_name: str, error: str, *, style: str = "red"
) -> None:
    """Print standardized demo error message.

    Args:
        cli: FlextCli instance
        demo_name: Name of the failed demo
        error: Error message
        style: Message style

    """
    cli.print(f"❌ {demo_name} failed: {error}", style=f"bold {style}")
    cli.print("This failure demonstrates FlextResult error handling!", style="yellow")
    cli.print(
        "The error was caught and wrapped in a FlextResult for clean handling.",
        style="white",
    )


__all__ = ["handle_command_result", "print_demo_completion", "print_demo_error"]
