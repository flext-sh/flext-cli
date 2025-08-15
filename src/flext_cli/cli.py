"""FLEXT CLI Entry Point."""

from __future__ import annotations

import sys
from contextlib import suppress

import click
from flext_core import (
    FlextUtilities,
    __version__ as core_version,
)
from rich.console import Console

from flext_cli.__version__ import __version__
from flext_cli.cmd import auth, config, debug
from flext_cli.config import get_config
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
    """FLEXT Command Line Interface - Main entry point for ecosystem operations.

    This function serves as the root command group for the FLEXT CLI, providing
    global configuration options and context setup for all subcommands. It follows
    Click framework patterns with Rich console integration for enhanced UX.

    Global Options:
        profile: Configuration profile name (default: 'default')
                 Environment variable: FLX_PROFILE
                 Supports: dev, staging, prod profiles

        output: Output format for command results (default: 'table')
                Choices: table, json, yaml, csv, plain

        debug: Enable debug mode with verbose logging (default: False)
               Environment variable: FLX_DEBUG
               Shows configuration details and operation traces

        quiet: Suppress non-error output (default: False)
               Useful for scripting and automation

    Context Setup:
        Creates and configures CLI context with:
        - CLIConfig: User configuration with profile support
        - CLISettings: Application settings and defaults
        - Rich Console: Terminal output with color and formatting
        - Click Context: Command execution context

    Command Registration:
        Currently registered command groups:
        - auth: Authentication management (✅ implemented)
        - config: Configuration management (✅ implemented)
        - debug: Debug and diagnostic tools (✅ implemented)

        Planned command groups (docs/TODO.md):
        - pipeline: Pipeline management (Sprint 1)
        - service: Service orchestration (Sprint 1-2)
        - data: Data management (Sprint 3-4)
        - plugin: Plugin management (Sprint 4)
        - monitor: Monitoring tools (Sprint 7)

    Examples:
        $ flext --profile dev auth login
        $ flext --output json config show
        $ flext --debug --quiet service health

    TODO (Sprint 1):
        - Integrate FlextContainer for dependency injection
        - Add correlation ID tracking for operations
        - Implement service discovery for ecosystem services

    """
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
    ctx.obj["settings"] = config  # Backward compatibility alias
    ctx.obj["debug"] = debug

    # Debug information
    if debug:
        console.print(f"[dim]Profile: {profile}[/dim]")
        console.print(f"[dim]Output format: {output}[/dim]")
        console.print(f"[dim]Debug mode: {debug}[/dim]")

    # Show help if no command:
    if ctx.invoked_subcommand is None:
        # Avoid raising SystemExit(2) when invoked without a subcommand
        click.echo(ctx.get_help())


def _register_commands() -> None:
    """Register subcommand groups lazily to avoid import-time side effects."""
    with suppress(Exception):
        cli.add_command(auth)
    with suppress(Exception):
        cli.add_command(config)
    with suppress(Exception):
        cli.add_command(debug)


_register_commands()


@cli.command()
@click.pass_context
def interactive(ctx: click.Context) -> None:
    """Start interactive mode with REPL interface.

    Interactive mode provides a Read-Eval-Print Loop (REPL) interface for
    executing FLEXT CLI commands interactively with enhanced user experience
    including tab completion, command history, and context-aware help.

    Planned Features (Sprint 8):
        - Rich-based REPL with syntax highlighting
        - Tab completion for all commands and options
        - Command history with search functionality
        - Context-aware help system
        - Multi-line command support
        - Session state persistence

    Current Status:
        🚧 PLACEHOLDER - Implementation planned for Sprint 8

    TODO (docs/TODO.md - Sprint 8):
        - Implement Rich-based REPL interface
        - Add tab completion system using Click completion
        - Implement command history with readline support
        - Create context-aware help system
        - Add session management and state persistence

    Usage:
        $ flext interactive
        flext> auth login --username admin
        flext> config show --format table
        flext> pipeline list --status running
        flext> exit
    """
    console = ctx.obj["console"]
    console.print("[yellow]🚧 Interactive mode coming soon![/yellow]")
    console.print("📋 Planned for Sprint 8 - will include:")
    console.print("   • Rich REPL with syntax highlighting")
    console.print("   • Tab completion for commands")
    console.print("   • Command history and search")
    console.print("   • Context-aware help system")
    console.print("")
    console.print("Use 'flext --help' for currently available commands.")


@cli.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Display comprehensive version and environment information.

    Shows version information for FLEXT CLI and its dependencies, along with
    environment details useful for debugging and support. In debug mode,
    displays additional configuration and system information.

    Output Information:
        - FLEXT CLI version and build details
        - Python interpreter version and platform
        - flext-core library version (if available)
        - Operating system and architecture
        - Configuration details (debug mode only)

    Debug Mode:
        When --debug flag is used, shows additional information:
        - Current configuration profile and settings
        - Environment variables (FLX_*)
        - Dependency versions
        - System paths and permissions

    Examples:
        $ flext version
        FLEXT CLI version 0.9.0
        Python 3.13.0

        $ flext --debug version
        FLEXT CLI version 0.9.0 (build 2025-08-02)
        Python 3.13.0 (main, Oct  7 2024, 18:15:40)
        flext-core 0.9.0
        Configuration: {'profile': 'default', 'debug': True, ...}

    TODO (Sprint 1):
        - Add flext-core version detection
        - Include dependency version information
        - Add ecosystem service version checking
        - Implement build information display

    """
    console = ctx.obj["console"]

    # Basic version information
    console.print(f"FLEXT CLI version {__version__}")
    console.print(f"Python {sys.version.split()[0]} ({sys.platform})")

    # Issue #1: Add flext-core version detection (Sprint 1)
    if core_version:
        console.print(f"flext-core {core_version}")
    else:
        console.print("[dim]flext-core version: not detected[/dim]")

    # Debug mode information
    if ctx.obj.get("debug"):
        config = ctx.obj["config"]
        console.print("")
        console.print("[bold]Debug Information:[/bold]")

        # Configuration details
        config_display = (
            config.model_dump() if hasattr(config, "model_dump") else str(config)
        )
        console.print(f"[dim]Configuration: {config_display}[/dim]")

        # System information
        console.print(f"[dim]Python executable: {sys.executable}[/dim]")
        console.print(f"[dim]Platform: {sys.platform}[/dim]")

        # Issue #2: Add ecosystem service connectivity check (Sprint 1)
        console.print("[dim]Service connectivity: not implemented[/dim]")


def main() -> None:
    """Execute the main CLI entry point with comprehensive error handling.

    This function serves as the primary entry point for the FLEXT CLI application,
    providing centralized error handling and graceful failure modes. It leverages
    flext-core utilities for consistent error handling across the ecosystem.

    Error Handling:
        - Catches and formats all unhandled exceptions
        - Provides user-friendly error messages
        - Logs errors for debugging (debug mode)
        - Ensures clean exit codes for scripting

    Exit Codes:
        - 0: Successful execution
        - 1: General error (command failed)
        - 2: Misuse of command (invalid arguments)
        - 3: Internal error (unexpected exception)

    Integration:
        Uses FlextUtilities.handle_cli_main_errors from flext-core to ensure
        consistent error handling patterns across all FLEXT ecosystem tools.

    Examples:
        $ flext auth login          # Exit code 0 on success
        $ flext invalid-command     # Exit code 2 on invalid command
        $ flext auth login --bad    # Exit code 1 on command failure

    TODO (Sprint 1):
        - Add comprehensive logging integration
        - Implement crash report generation
        - Add performance metrics collection
        - Integrate with ecosystem monitoring

    """
    # Use centralized error handling from flext-core to follow DRY principle
    # This ensures consistent error handling across all FLEXT ecosystem tools
    FlextUtilities.handle_cli_main_errors(cli, debug_mode=True)


if __name__ == "__main__":
    main()
