"""Output formatting utilities for FLEXT CLI."""

from __future__ import annotations

import json
from typing import Any

import yaml
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table


def setup_console(no_color: bool = False, quiet: bool = False) -> Console:
    """Set up Rich console with configuration."""
    return Console(
        no_color=no_color,
        quiet=quiet,
        highlight=True,
        markup=True,
    )


def format_pipeline_list(console: Console, pipeline_list: object) -> None:
    """Format and display pipeline list."""
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
            "active": "green",
            "inactive": "yellow",
            "error": "red",
            "running": "blue",
        }.get(pipeline.status.lower(), "white")

        table.add_row(
            pipeline.id,
            pipeline.name,
            f"[{status_color}]{pipeline.status}[/{status_color}]",
            pipeline.created_at,
        )

    console.print(table)
    console.print(f"\nTotal: {pipeline_list.total} pipelines")


def format_pipeline(console: Console, pipeline: object) -> None:
    """Format and display single pipeline details."""
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
            console.print("\n[bold]Additional Configuration:[/bold]")
            syntax = Syntax(
                yaml.dump(pipeline.config.config, default_flow_style=False),
                "yaml",
                theme="monokai",
                line_numbers=False,
            )
            console.print(syntax)


def format_plugin_list(
    console: Console, plugins: list[dict[str, Any]], output_format: str
) -> None:
    """Format and display plugin list."""
    if not plugins:
        console.print("[yellow]No plugins found[/yellow]")
        return

    if output_format == "yaml":
        console.print(yaml.dump(plugins, default_flow_style=False))
        return

    table = Table(title="Available Plugins")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="white")
    table.add_column("Type", style="yellow")
    table.add_column("Version", style="green")
    table.add_column("Status", style="blue")

    for plugin in plugins:
        status_color = {
            "installed": "green",
            "available": "yellow",
            "update": "blue",
            "error": "red",
        }.get(plugin.get("status", "").lower(), "white")

        table.add_row(
            plugin.get("id", ""),
            plugin.get("name", ""),
            plugin.get("type", ""),
            plugin.get("version", ""),
            f"[{status_color}]{plugin.get('status', '')}[/{status_color}]",
        )

    console.print(table)


def format_json(data: object) -> str:
    """Format data as JSON."""
    return json.dumps(data, indent=2, default=str)


def format_yaml(data: object) -> str:
    """Format data as YAML."""
    return yaml.dump(data, default_flow_style=False, default_str=str)


def print_error(console: Console, message: str, details: str | None = None) -> None:
    """Print error message with optional details."""
    console.print(f"[red]❌ {message}[/red]")
    if details:
        console.print(f"[dim]{details}[/dim]")


def print_success(console: Console, message: str) -> None:
    """Print success message."""
    console.print(f"[green]✅ {message}[/green]")


def print_warning(console: Console, message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def print_info(console: Console, message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ️  {message}[/blue]")
