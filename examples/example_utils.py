"""Common utilities for FLEXT CLI examples.

Eliminates code duplication across example files by providing shared patterns
and common functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult
from rich.console import Console
from rich.panel import Panel


def print_demo_completion(
    console: Console,
    demo_name: str,
    features: list[str],
    *,
    border_style: str = "green"
) -> None:
    """Print standardized demo completion panel.

    Args:
        console: Rich console instance
        demo_name: Name of the completed demo
        features: List of features demonstrated
        border_style: Panel border style

    """
    features_text = "\n".join(f"• {feature}" for feature in features)

    console.print(
        Panel(
            f"[bold green]✅ {demo_name} Completed![/bold green]\n\n"
            f"[cyan]Key Features Demonstrated:[/cyan]\n"
            f"{features_text}\n\n"
            "[yellow]All operations used FlextResult pattern for error handling![/yellow]",
            title=f"🎉 {demo_name} Complete",
            border_style=border_style,
            expand=False,
        )
    )


def handle_command_result(
    console: Console,
    result: FlextResult[dict[str, object]],
    action: str,
    success_fields: list[str] | None = None
) -> None:
    """Generic handler for CQRS command results to eliminate code duplication.

    Args:
        console: Rich console instance
        result: FlextResult from command operation
        action: Action being performed (e.g., "create project", "change status")
        success_fields: Fields to display on success (defaults to ['id', 'status'])

    """
    success_fields = success_fields or ["id", "status"]

    if result.is_success:
        data = result.value
        console.print(f"[green]✅ {action.title()} successful[/green]")

        for field in success_fields:
            if isinstance(data, dict) and field in data:
                display_name = field.replace("_", " ").title()
                console.print(f"{display_name}: {data[field]}")
    else:
        console.print(f"[red]❌ Failed to {action}: {result.error}[/red]")


def print_demo_error(
    console: Console,
    demo_name: str,
    error: str,
    *,
    border_style: str = "red"
) -> None:
    """Print standardized demo error panel.

    Args:
        console: Rich console instance
        demo_name: Name of the failed demo
        error: Error message
        border_style: Panel border style

    """
    console.print(
        Panel(
            f"[bold red]❌ {demo_name} failed: {error}[/bold red]\n\n"
            "[yellow]This failure demonstrates FlextResult error handling![/yellow]\n"
            "The error was caught and wrapped in a FlextResult for clean handling.",
            title="⚠️ Error Handling Demo",
            border_style=border_style,
            expand=False,
        )
    )


__all__ = ["print_demo_completion", "print_demo_error"]
