"""Debug commands for FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import os
import platform
import sys

import click
from rich.console import Console
from rich.table import Table

from flext_cli import FlextApiClient, get_config, show_flext_cli_paths

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
          async with FlextApiClient() as client:
              console.print("[yellow]Testing API connectivity...[/yellow]")

              # Test connection
              connected = await client.test_connection()

              if connected:
                  console.print(
                      f"[green]✅ Connected to API at {client.base_url}[/green]",
                  )
                  try:
                      status = await client.get_system_status()
                      console.print("\nSystem Status:")
                      console.print(f"  Version: {status.get('version', 'Unknown')}")
                      console.print(f"  Status: {status.get('status', 'Unknown')}")
                      console.print(f"  Uptime: {status.get('uptime', 'Unknown')}")
                  except (RuntimeError, ValueError, TypeError):
                      console.print("[yellow]⚠️  Could not get system status[/yellow]")
              else:
                  console.print(
                      f"[red]❌ Failed to connect to API at {client.base_url}[/red]",
                  )
                  ctx.exit(1)
      except (RuntimeError, ValueError, TypeError) as e:
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
          async with FlextApiClient() as client:
              console.print("[yellow]Fetching performance metrics...[/yellow]")

              metrics = await client.get_system_metrics()

              # Display metrics in table
              table = Table(title="System Performance Metrics")
              table.add_column("Metric", style="cyan")
              table.add_column("Value", style="white")

              for key, value in metrics.items():
                  table.add_row(key, str(value))

              console.print(table)
      except (RuntimeError, ValueError, TypeError) as e:
          console.print(f"[red]❌ Failed to get performance metrics: {e}[/red]")
          ctx.exit(1)

    asyncio.run(_check_performance())


class ValidationStrategy:
    """Strategy Pattern for validation operations - SOLID compliance."""

    def __init__(self, console: Console) -> None:
      self.console = console
      self.issues: list[str] = []
      self.warnings: list[str] = []

    def validate_python_version(self) -> None:
      """Validate Python version requirement."""
      py_version = sys.version_info
      if py_version >= (3, 10):
          self.console.print(
              f"[green]✅ Python version: {sys.version.split()[0]}[/green]",
          )
      else:
          self.issues.append(
              f"Python version {sys.version.split()[0]} is too old (requires 3.10+)",
          )

    def validate_configuration(self) -> None:
      """Validate configuration file existence."""
      config = get_config()
      config_path = config.config_dir / "config.yaml"
      if config_path.exists():
          self.console.print(
              f"[green]✅ Configuration file exists: {config_path}[/green]",
          )
      else:
          self.warnings.append(f"Configuration file not found at {config_path}")

    def validate_dependencies(self) -> None:
      """Validate required package dependencies."""
      required_packages = ["click", "rich", "httpx", "pydantic", "yaml"]
      missing_packages = []

      for package in required_packages:
          try:
              __import__(package)
          except ImportError:
              missing_packages.append(package)

      if not missing_packages:
          self.console.print("[green]✅ All required packages installed[/green]")
      else:
          self.issues.append(f"Missing packages: {', '.join(missing_packages)}")

    def display_environment_info(self) -> None:
      """Display environment information."""
      self.console.print("\n[bold]Environment Information:[/bold]")
      self.console.print(f"  OS: {platform.system()} {platform.release()}")
      self.console.print(f"  Architecture: {platform.machine()}")
      self.console.print(f"  Python: {sys.version}")
      self.console.print("  CLI Version: 0.1.0")

    def display_summary(self) -> bool:
      """Display validation summary and return success status."""
      self.console.print("\n[bold]Validation Summary:[/bold]")

      if self.issues:
          self.console.print(
              f"[red]❌ Found {len(self.issues)} critical issues:[/red]",
          )
          for issue in self.issues:
              self.console.print(f"  - {issue}")
      else:
          self.console.print("[green]✅ No critical issues found[/green]")

      if self.warnings:
          self.console.print(
              f"\n[yellow]⚠️  Found {len(self.warnings)} warnings:[/yellow]",
          )
          for warning in self.warnings:
              self.console.print(f"  - {warning}")

      return len(self.issues) == 0


@debug_cmd.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate FLEXT CLI setup using Strategy Pattern for complexity reduction."""
    console: Console = ctx.obj["console"]
    console.print("[yellow]Validating FLEXT CLI setup...[/yellow]\n")

    # Strategy Pattern implementation - Single Responsibility
    validator = ValidationStrategy(console)
    validator.validate_python_version()
    validator.validate_configuration()
    validator.validate_dependencies()
    validator.display_environment_info()

    success = validator.display_summary()
    if not success:
      ctx.exit(1)


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
    """Show FLEXT CLI paths.

    REFACTORED: Uses show_flext_cli_paths utility to eliminate code duplication.
    """
    console: Console = ctx.obj["console"]
    # Use centralized paths display function to follow DRY principle
    show_flext_cli_paths(console)
