"""FLEXT CLI Output Utilities - Rich Console Output and Formatting Functions.

This module provides comprehensive output formatting utilities for FLEXT CLI
commands, ensuring consistent and beautiful terminal output across all CLI
operations. Uses Rich library for enhanced terminal UX and supports multiple
output formats for different use cases.

Output Functions:
    - Console setup and configuration with color and quiet mode support
    - Pipeline and plugin formatting for tables and JSON output
    - Success, error, warning, and info message formatting
    - JSON and YAML formatting utilities
    - Debug path display and system information

Architecture:
    - Rich console integration for enhanced terminal output
    - Consistent styling and formatting across all commands
    - Support for multiple output formats (table, JSON, YAML)
    - Color-coded status indicators and icons
    - Responsive table layouts with proper column sizing

Current Implementation Status:
    ✅ Rich console setup and configuration
    ✅ Pipeline and plugin formatting with tables
    ✅ Success, error, warning, info message utilities
    ✅ JSON and YAML formatting functions
    ✅ Debug path display with existence checking
    ✅ Consistent styling and color coding
    ⚠️ Basic implementation (TODO: Sprint 2 - enhance formatting features)

TODO (docs/TODO.md):
    Sprint 2: Add progress bars and spinners for long operations
    Sprint 3: Add interactive table formatting with pagination
    Sprint 5: Add export capabilities for different formats
    Sprint 7: Add performance metrics display and monitoring
    Sprint 8: Add interactive charts and graphs for data visualization

Features:
    - Beautiful Rich tables with color coding and icons
    - Multiple output format support (table, JSON, YAML)
    - Console configuration with color and quiet mode
    - Consistent message formatting (success, error, warning, info)
    - Pipeline and plugin display with status indicators
    - Debug information display with path validation

Usage Examples:
    Console setup:
    >>> console = setup_console(no_color=False, quiet=False)

    Success message:
    >>> print_success(console, "Operation completed successfully")

    Error with details:
    >>> print_error(console, "Failed to connect", "Connection timeout")

    Pipeline list formatting:
    >>> format_pipeline_list(console, pipeline_list)

Integration:
    - Used by all CLI commands for consistent output
    - Integrates with Rich console for enhanced UX
    - Supports debugging and diagnostic display
    - Provides foundation for interactive CLI features

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from rich.console import Console
from rich.table import Table

from flext_cli.utils.config import get_config

if TYPE_CHECKING:
    from flext_cli.client import Pipeline, PipelineList


def setup_console(*, no_color: bool = False, quiet: bool = False) -> Console:
    """Set up Rich console with configuration.

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
    plugins: list[dict[str, object]],
    output_format: str,
) -> None:
    """Format plugin list for display.

    Args:
        console: Rich console instance
        plugins: List of plugin dictionaries
        output_format: Output format (table or json)

    """
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
                str(plugin.get("name", "Unknown")),
                str(plugin.get("type", "Unknown")),
                str(plugin.get("version", "Unknown")),
                str(plugin.get("description", "No description")),
            )

        console.print(table)
    else:
        # JSON format
        console.print(json.dumps(plugins, indent=2))


def format_json(data: object) -> str:
    """Format object as JSON string.

    Args:
        data: Object to format as JSON

    Returns:
        JSON string representation

    """
    return json.dumps(data, indent=2, default=str)


def format_yaml(data: object) -> str:
    """Format object as YAML string.

    Args:
        data: Object to format as YAML

    Returns:
        YAML string representation

    """
    result = yaml.dump(data, default_flow_style=False)
    return str(result)


def print_error(console: Console, message: str, details: str | None = None) -> None:
    """Print error message with optional details.

    Args:
        console: Rich console instance
        message: Error message to display
        details: Optional detailed error information

    """
    console.print(f"[bold red]Error:[/bold red] {message}")
    if details:
        console.print(f"[dim]{details}[/dim]")


def print_success(console: Console, message: str) -> None:
    """Print success message.

    Args:
        console: Rich console instance
        message: Success message to display

    """
    console.print(f"[bold green]✓[/bold green] {message}")


def print_warning(console: Console, message: str) -> None:
    """Print warning message.

    Args:
        console: Rich console instance
        message: Warning message to display

    """
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(console: Console, message: str) -> None:
    """Print info message.

    Args:
        console: Rich console instance
        message: Info message to display

    """
    console.print(f"[bold blue]i[/bold blue] {message}")


def show_flext_cli_paths(console: Console) -> None:
    """Show FLEXT CLI paths in a formatted table.

    REFACTORED: DRY principle - eliminates duplicate paths display code.
    Used by debug commands across all CLI implementations.
    """
    paths = {
        "Config Directory": Path.home() / ".flext",
        "Config File": get_config().config_dir / "config.yaml",
        "Cache Directory": Path.home() / ".flext" / "cache",
        "Log Directory": Path.home() / ".flext" / "logs",
        "Token File": Path.home() / ".flext" / ".token",
    }

    table = Table(title="FLEXT CLI Paths")
    table.add_column("Path Type", style="cyan")
    table.add_column("Location", style="white")
    table.add_column("Exists", style="green")

    for name, path in paths.items():
        exists = "✅" if path.exists() else "❌"
        table.add_row(name, str(path), exists)

    console.print(table)
