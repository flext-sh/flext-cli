"""FLEXT CLI Entry Point - Clean Architecture with flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Version 0.7.0 - Complete refactor using flext-core patterns:
- Declarative configuration via BaseConfig/BaseSettings
- Dependency injection via DIContainer
- Clean architecture with domain/application layers
- No legacy/fallback code
"""

from __future__ import annotations

import sys
import traceback

import click
from flext_core.config.base import get_container
from rich.console import Console

from flext_cli.__version__ import __version__
from flext_cli.commands import auth, config, debug, pipeline, plugin

# Register project commands - Import early to avoid E402
from flext_cli.commands.projects import algar, gruponos, meltano
from flext_cli.domain import CLIServiceContainer
from flext_cli.utils.config import CLISettings, get_config


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
    container = get_container()
    service_container = CLIServiceContainer(
        name="flext-cli",
        version="0.7.0",
    )

    # Register services in DI container
    container.register(CLIServiceContainer, service_container)

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
cli.add_command(pipeline.pipeline)
cli.add_command(plugin.plugin)
cli.add_command(debug.debug_cmd)

# Register project commands
cli.add_command(algar.algar)
cli.add_command(meltano.meltano)
cli.add_command(gruponos.gruponos)


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
    """Main CLI entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except (
        OSError,
        RuntimeError,
        ValueError,
        TypeError,
        ConnectionError,
        TimeoutError,
    ) as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        # In debug mode, show full traceback

        console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
