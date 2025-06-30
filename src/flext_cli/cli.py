"""FLEXT CLI Entry Point - Main command-line interface.

Copyright (c) 2025 FLEXT Team. All rights reserved.
"""

from __future__ import annotations

import sys

import click
from rich.console import Console

from flext_cli.commands import auth, config, debug, pipeline, plugin
from flext_cli.utils.output import setup_console

console = Console()


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version="0.1.0", prog_name="flext")
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
    """FLEXT Command Line Interface.

    Enterprise CLI for managing pipelines, plugins, and platform operations.
    """
    # Setup context
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile
    ctx.obj["output"] = output
    ctx.obj["debug"] = debug
    ctx.obj["quiet"] = quiet
    ctx.obj["console"] = setup_console(no_color=False, quiet=quiet)

    # Show help if no command
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Register command groups
cli.add_command(auth.auth)
cli.add_command(config.config)
cli.add_command(pipeline.pipeline)
cli.add_command(plugin.plugin)
cli.add_command(debug.debug_cmd)


@cli.command()
@click.pass_context
def interactive(ctx: click.Context) -> None:
    """Start interactive mode with command completion."""
    console = ctx.obj["console"]
    console.print("[yellow]Interactive mode coming soon![/yellow]")
    console.print("Use 'flext --help' for available commands.")


@cli.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Show version information."""
    console = ctx.obj["console"]
    console.print("FLEXT CLI version 0.1.0")
    console.print(f"Python {sys.version}")


def main() -> None:
    """Run the FLEXT CLI application."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
