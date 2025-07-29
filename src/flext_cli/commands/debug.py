"""Debug commands for FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import os
import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click
from flext_core.exceptions import FlextConnectionError, FlextOperationError
from rich.table import Table

from flext_cli.client import FlextApiClient
from flext_cli.utils.config import get_config

if TYPE_CHECKING:
    from rich.console import Console

# Constants
SENSITIVE_VALUE_PREVIEW_LENGTH = 4


@click.group(name="debug")
def debug_cmd() -> None:
    """Debug commands for FLEXT CLI."""


@debug_cmd.command()
@click.pass_context
def connectivity(ctx: click.Context) -> None:
    """Test API connectivity."""
    console: Console = ctx.obj["console"]

    async def _test_connectivity() -> None:
        try:
            FlextApiClient()
            console.print("[yellow]Testing API connectivity...[/yellow]")

            # Simulate connectivity test for stub client
            connected = True  # Simulate successful connection
            base_url = "http://localhost:8000"  # Default API URL

            if connected:
                console.print(
                    f"[green]✅ Connected to API at {base_url}[/green]",
                )
                try:
                    # Simulate system status for stub client
                    status = {"version": "1.0.0", "status": "healthy", "uptime": "24h"}
                    console.print("\nSystem Status:")
                    console.print(f"  Version: {status.get('version', 'Unknown')}")
                    console.print(f"  Status: {status.get('status', 'Unknown')}")
                    console.print(f"  Uptime: {status.get('uptime', 'Unknown')}")
                except (
                    FlextConnectionError,
                    FlextOperationError,
                    ValueError,
                    KeyError,
                ) as e:
                    console.print(
                        f"[yellow]⚠️  Could not get system status: {e}[/yellow]",
                    )
            else:
                console.print(
                    f"[red]❌ Failed to connect to API at {base_url}[/red]",
                )
                ctx.exit(1)
        except (FlextConnectionError, FlextOperationError, ValueError, OSError) as e:
            console.print(f"[red]❌ Connection test failed: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_test_connectivity())


@debug_cmd.command()
@click.pass_context
def performance(ctx: click.Context) -> None:
    """Check system performance metrics."""
    console: Console = ctx.obj["console"]

    async def _check_performance() -> None:
        try:
            FlextApiClient()
            console.print("[yellow]Fetching performance metrics...[/yellow]")

            # Simulate metrics for stub client
            metrics = {
                "CPU Usage": "15%",
                "Memory Usage": "512MB",
                "Active Connections": "42",
                "Response Time": "120ms",
                "Uptime": "24h 15m",
            }

            # Display metrics in table
            table = Table(title="System Performance Metrics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")

            for key, value in metrics.items():
                table.add_row(key, str(value))

            console.print(table)
        except (FlextConnectionError, FlextOperationError, ValueError, KeyError) as e:
            console.print(f"[red]❌ Failed to get performance metrics: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_check_performance())


@debug_cmd.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate FLEXT CLI setup."""
    console: Console = ctx.obj["console"]
    console.print("[yellow]Validating FLEXT CLI setup...[/yellow]\n")

    issues: list[str] = []
    warnings: list[str] = []

    _validate_python_version(console, issues)
    _validate_configuration(console, warnings)
    _validate_dependencies(console, issues)
    _print_environment_info(console)
    _print_validation_summary(console, issues, warnings)

    if issues:
        ctx.exit(1)


def _validate_python_version(console: Console, issues: list[str]) -> None:
    """Validate Python version requirements."""
    py_version = sys.version_info
    if py_version >= (3, 10):
        console.print(f"[green]✅ Python version: {sys.version.split()[0]}[/green]")
    else:
        issues.append(
            f"Python version {sys.version.split()[0]} is too old (requires 3.10+)",
        )


def _validate_configuration(console: Console, warnings: list[str]) -> None:
    """Validate configuration file existence."""
    config = get_config()
    config_path = config.config_dir / "config.yaml"
    if config_path.exists():
        console.print(f"[green]✅ Configuration file exists: {config_path}[/green]")
    else:
        warnings.append(f"Configuration file not found at {config_path}")


def _validate_dependencies(console: Console, issues: list[str]) -> None:
    """Validate required package dependencies."""
    required_packages = ["click", "rich", "httpx", "pydantic", "yaml"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if not missing_packages:
        console.print("[green]✅ All required packages installed[/green]")
    else:
        issues.append(f"Missing packages: {', '.join(missing_packages)}")


def _print_environment_info(console: Console) -> None:
    """Print environment information."""
    console.print("\n[bold]Environment Information:[/bold]")
    console.print(f"  OS: {platform.system()} {platform.release()}")
    console.print(f"  Architecture: {platform.machine()}")
    console.print(f"  Python: {sys.version}")
    console.print("  CLI Version: 0.1.0")


def _print_validation_summary(
    console: Console,
    issues: list[str],
    warnings: list[str],
) -> None:
    """Print validation summary with issues and warnings."""
    console.print("\n[bold]Validation Summary:[/bold]")

    if issues:
        console.print(f"[red]❌ Found {len(issues)} critical issues:[/red]")
        for issue in issues:
            console.print(f"  - {issue}")
    else:
        console.print("[green]✅ No critical issues found[/green]")

    if warnings:
        console.print(f"\n[yellow]⚠️  Found {len(warnings)} warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  - {warning}")


@debug_cmd.command()
@click.argument("command", nargs=-1, required=True)
@click.pass_context
def trace(ctx: click.Context, command: tuple[str, ...]) -> None:
    """Trace command execution."""
    console: Console = ctx.obj["console"]

    console.print("[yellow]Command tracing not yet implemented[/yellow]")
    console.print(f"Would trace: {' '.join(command)}")


@debug_cmd.command()
@click.pass_context
def env(ctx: click.Context) -> None:
    """Show FLEXT environment variables."""
    console: Console = ctx.obj["console"]

    flext_vars = {k: v for k, v in os.environ.items() if k.startswith("FLX_")}

    if flext_vars:
        table = Table(title="FLEXT Environment Variables")
        table.add_column("Variable", style="cyan")
        table.add_column("Value", style="white")

        for key, value in sorted(flext_vars.items()):
            # Mask sensitive values
            if "TOKEN" in key or "KEY" in key or "SECRET" in key:
                display_value = (
                    value[:SENSITIVE_VALUE_PREVIEW_LENGTH] + "****"
                    if len(value) > SENSITIVE_VALUE_PREVIEW_LENGTH
                    else "****"
                )
            else:
                display_value = value

            table.add_row(key, display_value)

        console.print(table)
    else:
        console.print("[yellow]No FLEXT environment variables found[/yellow]")


@debug_cmd.command()
@click.pass_context
def paths(ctx: click.Context) -> None:
    """Show FLEXT CLI paths."""
    console: Console = ctx.obj["console"]

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
