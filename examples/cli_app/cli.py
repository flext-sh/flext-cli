"""FLEXT CLI Example Application - Complete Clean Architecture Implementation.

This module demonstrates a complete CLI application using FLEXT CLI patterns with
Clean Architecture, Domain-Driven Design, and flext-core integration. Serves as
a reference implementation for production-ready CLI applications.

Architecture:
    - Clean Architecture with proper layer separation
    - Click-based command framework with Rich terminal UI
    - flext-core integration with FlextResult patterns
    - Domain-driven design with CLI entities and services
    - Sprint-aligned command implementation roadmap

Current Implementation Status:
    ✅ Core Infrastructure: CLI setup, configuration, context management
    ✅ Foundation Commands: auth, config, debug (fully functional)
    🎯 Pipeline Commands: Planned for Sprint 1 implementation
    🎯 Plugin Commands: Planned for Sprint 6 implementation
    🎯 Project Commands: Planned for Sprint 9 implementation

Command Structure:
    flext [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGS...]

    Global Options:
        --profile PROFILE    Configuration profile (dev/staging/prod)
        --output FORMAT      Output format (table/json/yaml/csv/plain)
        --debug             Enable debug mode with verbose output
        --quiet             Suppress non-error output

    Available Commands:
        auth                Authentication and session management
        config              Configuration management and profiles
        debug               Diagnostic tools and health checks
        pipeline            Data pipeline management (Sprint 1)
        plugin              Plugin system management (Sprint 6)
        projects            Project-specific integrations (Sprint 9)

Usage Examples:
    Basic usage:
    >>> python cli.py --help
    >>> python cli.py auth login --username REDACTED_LDAP_BIND_PASSWORD
    >>> python cli.py config show --format json
    >>> python cli.py debug health --verbose

    Advanced usage:
    >>> python cli.py --profile production --output json pipeline list
    >>> python cli.py --debug plugin install kubernetes-plugin
    >>> python cli.py projects client-a migration --type oud

Integration:
    - Uses main FLEXT CLI library patterns and components
    - Demonstrates proper dependency injection with flext-core
    - Shows Clean Architecture implementation in practice
    - Provides template for production CLI applications

TODO (Sprint Implementation):
    Sprint 1: Implement pipeline management commands (CRITICAL)
    Sprint 6: Add plugin system with discovery and lifecycle
    Sprint 9: Complete project-specific command integration

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys

import click
from flext_cli.__version__ import __version__
from flext_cli.commands import (  # pipeline and plugin don't exist yet
    auth,
    config,
    debug,
)
from flext_cli.commands.projects import client-a, client-b, meltano
from flext_cli.domain import CLIServiceContainer
from flext_cli.utils.config import CLISettings, get_config
from flext_core import get_flext_container
from flext_core.utilities import FlextUtilities
from rich.console import Console


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="flext")
@click.option(
    "--profile",
    default="default",
    envvar="FLX_PROFILE",
    help="Configuration profile to use",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["table", "json", "yaml", "csv", "plain"]),
    default="table",
    help="Output format",
)
@click.option(
    "--debug/--no-debug",
    default=False,
    envvar="FLX_DEBUG",
    help="Enable debug mode",
)
@click.option(
    "--quiet/--no-quiet",
    "-q",
    default=False,
    help="Suppress non-error output",
)
@click.pass_context
def cli(
    ctx: click.Context,
    profile: str,
    output: str,
    *,
    debug: bool,
    quiet: bool,
) -> None:
    """FLEXT Command Line Interface."""
    # Load configuration using flext-core
    config = get_config()
    settings = CLISettings()

    # Override config with CLI options
    config.profile = profile
    config.output_format = output
    config.no_color = False
    config.quiet = quiet
    config.verbose = debug

    # Create service container with dependency injection
    container = get_flext_container()
    service_container = CLIServiceContainer(
        name="flext-cli",
        version=__version__,
    )

    # Register services in DI container
    container.register("cli_service_container", service_container)

    # Setup click context with components
    console = Console()

    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["settings"] = settings
    ctx.obj["service_container"] = service_container
    ctx.obj["console"] = console

    # Debug information
    if debug:
        console.print(f"[dim]Profile: {profile}[/dim]")
        console.print(f"[dim]Output format: {output}[/dim]")
        console.print(f"[dim]Debug mode: {debug}[/dim]")

    # Show help if no command:
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Register command groups
cli.add_command(auth.auth)
cli.add_command(config.config)
# Pipeline and plugin commands will be added in future sprints:
# Sprint 1: pipeline management commands
# Sprint 6: plugin system commands
cli.add_command(debug.debug_cmd)

# Register project commands
cli.add_command(client-a.client-a)
cli.add_command(meltano.meltano)
cli.add_command(client-b.client-b)


@cli.command()
@click.pass_context
def interactive(ctx: click.Context) -> None:
    """Start interactive mode."""
    console = ctx.obj["console"]
    console.print("[yellow]Interactive mode coming soon![/yellow]")
    console.print("Use 'flext --help' for available commands.")


@cli.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Show version information."""
    console = ctx.obj["console"]
    settings = ctx.obj["settings"]
    config = ctx.obj["config"]

    console.print(f"FLEXT CLI version {settings.project_version}")
    console.print(f"Python {sys.version}")
    if ctx.obj.get("debug"):
        console.print(f"[dim]Configuration: {config.model_dump()}[/dim]")


def main() -> None:
    """Execute the main CLI entry point.

    REFACTORED: Uses FlextUtilities.handle_cli_main_errors to eliminate
    code duplication.
    """
    # Use centralized error handling from flext-core to follow DRY principle
    FlextUtilities.handle_cli_main_errors(cli, debug_mode=True)


if __name__ == "__main__":
    main()
