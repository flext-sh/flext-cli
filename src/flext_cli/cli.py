"""FLEXT CLI Entry Point - Clean Architecture with flext-core.

Version 0.7.0 - Complete refactor using flext-core patterns:
    - Declarative configuration via BaseConfig/BaseSettings
- Dependency injection via DIContainer
- Clean architecture with domain/application layers
- No legacy/fallback code
"""

from __future__ import annotations

import sys
import traceback
from typing import TYPE_CHECKING

import click
from rich.console import Console

from flext_cli.__version__ import __version__
from flext_cli.commands import auth
from flext_cli.commands import config
from flext_cli.commands import debug
from flext_cli.commands import pipeline
from flext_cli.commands import plugin
from flext_cli.domain import CLIServiceContainer
from flext_cli.utils.config import CLISettings
from flext_cli.utils.config import get_config
from flext_core.config.base import get_container

if TYPE_CHECKING:
    from flext_cli.domain.cli_context import CLIContext


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
def cli(ctx: click.Context, profile: str, output: str, debug: bool, quiet: bool) -> None:
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
    service_container = CLIServiceContainer.create(
        config=config,
        settings=settings,
    )

    # Register services in DI container
    container.register(CLIServiceContainer, service_container)

    # Create CLI context
    cli_context = service_container.create_context()

    # Setup click context with our clean architecture
    ctx.ensure_object(dict)
    ctx.obj["cli_context"] = cli_context
    ctx.obj["service_container"] = service_container
    ctx.obj["console"] = cli_context.console

    # Debug information
    cli_context.print_debug(f"Profile: {profile}")
    cli_context.print_debug(f"Output format: {output}")
    cli_context.print_debug(f"Debug mode: {debug}")

    # Show help if no command:
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
    """Start interactive mode."""
    cli_context: CLIContext = ctx.obj["cli_context"]
    cli_context.print_warning("Interactive mode coming soon!")
    cli_context.print_info("Use 'flext --help' for available commands.")


@cli.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Show version information."""
    cli_context: CLIContext = ctx.obj["cli_context"]
    cli_context.print_info(f"FLEXT CLI version {cli_context.settings.project_version}")
    cli_context.print_info(f"Python {sys.version}")
    cli_context.print_debug(f"Configuration: {cli_context.config.model_dump()}")


def main() -> None:
    try:
        cli()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        # In debug mode, show full traceback

        console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
