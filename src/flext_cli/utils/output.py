"""Output formatting utilities for FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Provides consistent output formatting across CLI commands.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from flext_cli.client import Pipeline, PipelineList


def setup_console(no_color: bool = False, quiet: bool = False) -> Console:
    """Setup Rich console with configuration.

    Args:
        no_color: Disable color output
        quiet: Suppress non-error output

    Returns:
        Configured console instance

    """
    return Console(
        color_system=None if no_color else "auto",
        quiet=quiet,
    )


def format_pipeline_list(console: Console, pipeline_list: PipelineList) -> None:
    """Format pipeline list for display."""
    if not pipeline_list.pipelines:
        console.print("[yellow]No pipelines found[/yellow]")
        return

    total_pages = (
        pipeline_list.total + pipeline_list.page_size - 1
    ) // pipeline_list.page_size
    title = f"Pipelines (Page {pipeline_list.page} of {total_pages})"
    table = Table(title=title)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="white")
    table.add_column("Status", style="green")
    table.add_column("Created", style="dim")

    for pipeline in pipeline_list.pipelines:
        status_color = {
            "running": "green",
            "failed": "red",
            "pending": "yellow",
            "completed": "blue",
        }.get(pipeline.status.lower(), "white")

        table.add_row(
            pipeline.id[:8],  # Show first 8 chars of ID
            pipeline.name,
            f"[{status_color}]{pipeline.status}[/{status_color}]",
            pipeline.created_at,
        )

    console.print(table)
    console.print(f"\nTotal: {pipeline_list.total} pipelines")


def format_pipeline(console: Console, pipeline: Pipeline) -> None:
    """Format single pipeline for display."""
    console.print(f"\n[bold cyan]{pipeline.name}[/bold cyan]")
    console.print(f"ID: {pipeline.id}")
    console.print(f"Status: {pipeline.status}")
    console.print(f"Created: {pipeline.created_at}")
    console.print(f"Updated: {pipeline.updated_at}")

    if pipeline.config:
        console.print("\n[bold]Configuration:[/bold]")
        console.print(f"  Tap: {pipeline.config.tap}")
        console.print(f"  Target: {pipeline.config.target}")

        if pipeline.config.transform:
            console.print(f"  Transform: {pipeline.config.transform}")

        if pipeline.config.schedule:
            console.print(f"  Schedule: {pipeline.config.schedule}")

        if pipeline.config.config:
            console.print("  Config:")
            config_yaml = yaml.dump(pipeline.config.config, default_flow_style=False)
            for line in config_yaml.strip().split("\n"):
                console.print(f"    {line}")


def format_plugin_list(
    console: Console,
    plugins: list[dict[str, Any]],
    output_format: str,
) -> None:
    """Format plugin list for display."""
    if not plugins:
        console.print("[yellow]No plugins found[/yellow]")
        return

    if output_format == "table":
        table = Table(title="Available Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="white")
        table.add_column("Version", style="green")
        table.add_column("Description", style="dim")

        for plugin in plugins:
            table.add_row(
                plugin.get("name", "Unknown"),
                plugin.get("type", "Unknown"),
                plugin.get("version", "Unknown"),
                plugin.get("description", "No description"),
            )

        console.print(table)
    else:
        # JSON format
        import json

        console.print(json.dumps(plugins, indent=2))


def format_json(data: object) -> str:
    """Format object as JSON string."""
    import json

    return json.dumps(data, indent=2, default=str)


def format_yaml(data: object) -> str:
    """Format object as YAML string."""
    result = yaml.dump(data, default_flow_style=False)
    return str(result)


def print_error(console: Console, message: str, details: str | None = None) -> None:
    """Print error message with optional details."""
    console.print(f"[bold red]Error:[/bold red] {message}")
    if details:
        console.print(f"[dim]{details}[/dim]")


def print_success(console: Console, message: str) -> None:
    """Print success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_warning(console: Console, message: str) -> None:
    """Print warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(console: Console, message: str) -> None:
    """Print info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")
