"""FLEXT CLI Entry Point.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import logging
import sys

import click
from flext_core import (
    FlextUtilities,
    __version__ as core_version,
)
from rich.console import Console

from flext_cli.__version__ import __version__
from flext_cli.cmd import auth, config, debug
from flext_cli.config import get_config
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliContext as CLIContext


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
    *,  # Force keyword-only arguments for booleans
    debug: bool,
    quiet: bool,
) -> None:
    """FLEXT Command Line Interface."""
    # Load configuration and override with CLI options
    base_config = get_config()
    config = base_config.model_copy(
      update={
          "profile": profile,
          "output_format": output,
          "debug": debug,
          "quiet": quiet,
      },
    )

    # Setup click context with components
    console = Console(quiet=quiet)

    # Create CLI context with correct fields (SOLID: Single Responsibility)
    cli_context = CLIContext()

    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["cli_context"] = cli_context
    ctx.obj["console"] = console
    ctx.obj["settings"] = config
    ctx.obj["debug"] = debug

    # Debug information
    if debug:
      console.print(
          f"[dim]{FlextCliConstants.CliMessages.LABEL_PROFILE}: {profile}[/dim]",
      )
      console.print(
          f"[dim]{FlextCliConstants.CliMessages.LABEL_OUTPUT_FORMAT}: {output}[/dim]",
      )
      console.print(
          f"[dim]{FlextCliConstants.CliMessages.LABEL_DEBUG_MODE}: {debug}[/dim]",
      )

    # Show help if no command:
    if ctx.invoked_subcommand is None:
      # Avoid raising SystemExit(2) when invoked without a subcommand
      click.echo(ctx.get_help())


def _register_commands() -> None:
    """Register subcommand groups lazily to avoid import-time side effects."""
    logger = logging.getLogger(__name__)

    try:
      cli.add_command(auth)
    except Exception as e:
      logger.debug("Failed to register auth command: %s", e, exc_info=True)

    try:
      cli.add_command(config)
    except Exception as e:
      logger.debug("Failed to register config command: %s", e, exc_info=True)

    try:
      cli.add_command(debug)
    except Exception as e:
      logger.debug("Failed to register debug command: %s", e, exc_info=True)


_register_commands()


@cli.command()
@click.pass_context
def interactive(ctx: click.Context) -> None:
    """Start interactive mode with REPL interface."""
    console = ctx.obj["console"]
    console.print(
      f"[yellow]{FlextCliConstants.CliMessages.INTERACTIVE_COMING}[/yellow]",
    )
    console.print(FlextCliConstants.CliMessages.INTERACTIVE_PLANNED)
    console.print(f"   {FlextCliConstants.CliMessages.INTERACTIVE_FEATURE_REPL}")
    console.print(f"   {FlextCliConstants.CliMessages.INTERACTIVE_FEATURE_COMPLETION}")
    console.print(f"   {FlextCliConstants.CliMessages.INTERACTIVE_FEATURE_HISTORY}")
    console.print(f"   {FlextCliConstants.CliMessages.INTERACTIVE_FEATURE_HELP}")
    console.print("")
    console.print(FlextCliConstants.CliMessages.INFO_USE_HELP)


@cli.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Display version and environment information."""
    console = ctx.obj["console"]

    # Basic version information
    console.print(f"{FlextCliConstants.CliMessages.VERSION_CLI} {__version__}")
    console.print(
      f"{FlextCliConstants.CliMessages.VERSION_PYTHON} {sys.version.split()[0]} ({sys.platform})",
    )

    # Issue #1: Add flext-core version detection (Sprint 1)
    if core_version:
      console.print(
          f"{FlextCliConstants.CliMessages.VERSION_FLEXT_CORE} {core_version}",
      )
    else:
      console.print(
          f"[dim]{FlextCliConstants.CliMessages.DEBUG_FLEXT_CORE_NOT_DETECTED}[/dim]",
      )

    # Debug mode information
    if ctx.obj.get("debug"):
      config = ctx.obj["config"]
      console.print("")
      console.print(f"[bold]{FlextCliConstants.CliMessages.DEBUG_INFORMATION}[/bold]")

      # Configuration details
      config_display = (
          config.model_dump() if hasattr(config, "model_dump") else str(config)
      )
      console.print(
          f"[dim]{FlextCliConstants.CliMessages.DEBUG_CONFIGURATION}: {config_display}[/dim]",
      )

      # System information
      console.print(
          f"[dim]{FlextCliConstants.CliMessages.DEBUG_PYTHON_EXECUTABLE}: {sys.executable}[/dim]",
      )
      console.print(
          f"[dim]{FlextCliConstants.CliMessages.DEBUG_PLATFORM}: {sys.platform}[/dim]",
      )

      # Issue #2: Add ecosystem service connectivity check (Sprint 1)
      console.print(
          f"[dim]{FlextCliConstants.CliMessages.DEBUG_SERVICE_CONNECTIVITY}[/dim]",
      )


def main() -> None:
    """Execute the main CLI entry point with error handling."""
    # Use centralized error handling from flext-core to follow DRY principle
    # This ensures consistent error handling across all FLEXT ecosystem tools
    FlextUtilities.handle_cli_main_errors(cli, debug_mode=True)


if __name__ == "__main__":
    main()
