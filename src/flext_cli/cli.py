"""FLEXT CLI - Pure Generic Interface.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Completely generic CLI framework that discovers commands via DI.
No knowledge of specific projects - purely architectural.
"""

from __future__ import annotations

import logging
import sys

import click
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


@click.group()
@click.version_option(version="0.7.0")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """FLEXT CLI - Enterprise Data Integration Platform.

    Discovers and executes commands from installed FLEXT projects.
    Projects register commands via dependency injection.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["console"] = console

    if verbose:
        logger.info("FLEXT CLI started")


@cli.command()
@click.pass_context
def list_projects(ctx: click.Context) -> None:
    """List all available FLEXT projects with CLI support."""
    try:
        console.print("[yellow]No FLEXT projects currently registered.[/yellow]")
        console.print(
            "Install FLEXT modules and register CLI providers to see commands here.",
        )
        console.print("Use DI container to register CLI command providers:")
        console.print(
            "  [green]from flext_cli.infrastructure import register_service[/green]",
        )
        console.print(
            "  [green]register_service(CLICommandProvider, your_provider_instance)[/green]",
        )

    except Exception as e:
        logger.exception("Failed to list projects")
        console.print(f"[red]Error: {e}[/red]")
        ctx.exit(1)


@cli.command()
@click.argument("project_id")
@click.pass_context
def list_commands(ctx: click.Context, project_id: str) -> None:
    """List commands for a specific project."""
    try:
        console.print(f"[yellow]No commands found for project: {project_id}[/yellow]")
        console.print("Register CLI command providers to see available commands.")

    except Exception as e:
        logger.exception("Failed to list commands")
        console.print(f"[red]Error: {e}[/red]")
        ctx.exit(1)


@cli.command()
@click.argument("project_id")
@click.argument("command_name")
@click.argument("args", nargs=-1)
@click.pass_context
def execute(
    ctx: click.Context,
    project_id: str,
    command_name: str,
    args: tuple[str, ...],
) -> None:
    """Execute a command from a specific project.

    Args:
        ctx: Click context object
        project_id: Project identifier
        command_name: Command to execute
        args: Command arguments

    """
    try:
        console.print(
            f"[yellow]Command execution not implemented: {project_id}.{command_name}[/yellow]",
        )
        console.print("Arguments:", list(args))
        console.print("Use DI container to register command providers for execution.")

    except Exception as e:
        logger.exception("Failed to execute command")
        console.print(f"[red]Error: {e}[/red]")
        ctx.exit(1)


@cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check health status of all FLEXT projects."""
    try:
        console.print("[green]✓ FLEXT CLI is operational[/green]")
        console.print("Register CLI providers to see project health status.")

    except Exception as e:
        logger.exception("Failed to check health")
        console.print(f"[red]Error: {e}[/red]")
        ctx.exit(1)


def main() -> None:
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.exception("CLI crashed")
        console.print(f"[red]CLI error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
