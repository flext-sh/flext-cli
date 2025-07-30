"""FLEXT CLI Entry Point - Clean Architecture with flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Modern CLI implementation using flext-core and Click patterns.
"""

from __future__ import annotations

import sys
import traceback

import click
from rich.console import Console

from flext_cli.__version__ import __version__
from flext_cli.commands import auth, config, debug
from flext_cli.domain.cli_context import CLIContext
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
    debug: bool,  # noqa: FBT001 - Click CLI parameter pattern
    quiet: bool,  # noqa: FBT001 - Click CLI parameter pattern
) -> None:
    """FLEXT Command Line Interface."""
    # Load configuration
    config = get_config()
    settings = CLISettings()

    # Override config with CLI options
    config.profile = profile
    config.output_format = output
    config.debug = debug
    config.quiet = quiet

    # Setup click context with components
    console = Console(quiet=quiet)

    # Create CLI context with required fields
    cli_context = CLIContext(
        config=config,
        settings=settings,
        console=console
    )

    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["settings"] = settings
    ctx.obj["cli_context"] = cli_context
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
cli.add_command(debug.debug_cmd)


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
    ctx.obj["settings"]

    console.print(f"FLEXT CLI version {__version__}")
    console.print(f"Python {sys.version}")
    if ctx.obj.get("debug"):
        config = ctx.obj["config"]
        # Format config for debug output (SOLID: Single Responsibility)
        config_display = (
            config.model_dump() if hasattr(config, "model_dump") else str(config)
        )
        console.print(f"[dim]Configuration: {config_display}[/dim]")


def main() -> None:
    """Execute the main CLI entry point."""
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
