"""FLEXT CLI Unified Integration - Transparent CLI parameter and configuration management.

This module provides a unified interface for applications to integrate with flext-cli
without needing to handle logging, output formats, or configuration themselves.
Applications simply provide their business logic and flext-cli handles all infrastructure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import sys
import traceback
from collections.abc import Callable
from typing import Protocol, TypeVar

import click

from flext_cli.configs import FlextCliConfigs
from flext_cli.formatters import FlextCliFormatters
from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_core import FlextConfig, FlextDomainService, FlextLogger, FlextResult

T = TypeVar("T")

# Expected tuple length for option entries: (param_decls, param_kwargs)
OPT_ENTRY_TUPLE_LEN = 2


class FlextCliApplication(Protocol):
    """Protocol for applications that integrate with flext-cli."""

    def execute_command(
        self,
        command: str,
        parameters: dict[str, object],
        context: FlextCliApplicationContext,
    ) -> FlextResult[object]:
        """Execute a command with the given parameters and context."""
        ...


class FlextCliApplicationContext:
    """Context provided to applications by flext-cli with all configuration handled."""

    def __init__(
        self,
        config: FlextCliConfigs,
        logger: FlextLogger,
        formatter: FlextCliFormatters,
        output_handler: FlextCliOutputHandler,
    ) -> None:
        """Initialize application context."""
        self.config = config
        self.logger = logger
        self.formatter = formatter
        self.output_handler = output_handler

    @property
    def is_verbose(self) -> bool:
        """Check if verbose mode is enabled."""
        return self.config.verbose

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.config.debug

    @property
    def output_format(self) -> str:
        """Get configured output format."""
        return self.config.output_format

    def format_data(self, data: object, format_override: str | None = None) -> str:
        """Format data using configured or override format."""
        target_format = format_override or self.output_format
        result = self.formatter.format_output(data, target_format)
        return result.unwrap() if result.is_success else str(data)

    def display_success(self, message: str, data: object = None) -> None:
        """Display success message with optional data."""
        self.output_handler.display_success(message, data)

    def display_error(self, message: str, error: Exception | None = None) -> None:
        """Display error message with optional exception details."""
        self.output_handler.display_error(message, error)

    def display_warning(self, message: str) -> None:
        """Display warning message."""
        self.output_handler.display_warning(message)

    def display_info(self, message: str) -> None:
        """Display info message."""
        self.output_handler.display_info(message)


class FlextCliOutputHandler:
    """Handles all output formatting and display for applications."""

    def __init__(self, config: FlextCliConfigs, formatter: FlextCliFormatters) -> None:
        """Initialize output handler."""
        self.config = config
        self.formatter = formatter

    def display_success(self, message: str, data: object = None) -> None:
        """Display success message with optional data."""
        if not self.config.quiet:
            if self.config.no_color:
                click.echo(f"SUCCESS: {message}")
            else:
                click.echo(click.style(f"SUCCESS: {message}", fg="green"))

            if data is not None and self.config.verbose:
                formatted_data = self.formatter.format_output(
                    data, self.config.output_format
                )
                if formatted_data.is_success:
                    click.echo(formatted_data.unwrap())

    def display_error(self, message: str, error: Exception | None = None) -> None:
        """Display error message with optional exception details."""
        if self.config.no_color:
            click.echo(f"ERROR: {message}", err=True)
        else:
            click.echo(click.style(f"ERROR: {message}", fg="red"), err=True)

        if error is not None and self.config.debug:
            click.echo("Exception details:", err=True)
            click.echo(traceback.format_exc(), err=True)

    def display_warning(self, message: str) -> None:
        """Display warning message."""
        if not self.config.quiet:
            if self.config.no_color:
                click.echo(f"WARNING: {message}")
            else:
                click.echo(click.style(f"WARNING: {message}", fg="yellow"))

    def display_info(self, message: str) -> None:
        """Display info message."""
        if self.config.verbose and not self.config.quiet:
            click.echo(f"INFO: {message}")


class FlextUnifiedCli(FlextDomainService[object]):
    """Unified CLI service that handles all configuration and provides transparent integration.

    Applications register their commands and business logic, while flext-cli handles:
    - Logging configuration
    - Output formatting
    - Parameter parsing
    - Configuration management
    - Error handling
    """

    def __init__(self, app_name: str, app_version: str = "1.0.0") -> None:
        """Initialize unified CLI service."""
        super().__init__()
        self.app_name = app_name
        self.app_version = app_version

        self._commands: dict[str, click.Command] = {}
        self._application: FlextCliApplication | None = None
        self._logger = FlextLogger(__name__)

    async def execute(self) -> FlextResult[object]:
        """Execute CLI operation - required by FlextDomainService."""
        return FlextResult[object].ok(
            {"status": "operational", "service": "flext-unified-cli"}
        )

    def register_application(self, application: FlextCliApplication) -> None:
        """Register the main application that will handle commands."""
        self._application = application

    def create_cli_group(self) -> click.Group:
        """Create a Click CLI group with unified configuration handling."""

        @click.group(invoke_without_command=True)
        @click.option("--debug", is_flag=True, help="Enable debug mode.")
        @click.option("--verbose", is_flag=True, help="Enable verbose output.")
        @click.option("--trace", is_flag=True, help="Enable trace logging.")
        @click.option("--quiet", is_flag=True, help="Suppress output.")
        @click.option("--no-color", is_flag=True, help="Disable colored output.")
        @click.option(
            "--log-level",
            type=click.Choice(
                ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
            ),
            default="INFO",
            help="Set log level.",
        )
        @click.option(
            "--output-format",
            type=click.Choice(
                ["table", "json", "yaml", "csv", "plain"], case_sensitive=False
            ),
            default="table",
            help="Set output format.",
        )
        @click.option(
            "--profile", default="default", help="Configuration profile to use."
        )
        @click.option(
            "--version",
            is_flag=True,
            expose_value=False,
            is_eager=True,
            callback=self._print_version,
            help="Show version and exit.",
        )
        @click.pass_context
        def cli_group(
            ctx: click.Context,
            *,
            debug: bool,
            verbose: bool,
            trace: bool,
            quiet: bool,
            no_color: bool,
            log_level: str,
            output_format: str,
            profile: str,
        ) -> None:
            """Unified CLI application with automatic configuration management."""
            # Create unified configuration
            config_data = {
                "app_name": self.app_name,
                "debug": debug,
                "verbose": verbose,
                "trace": trace,
                "quiet": quiet,
                "no_color": no_color,
                "log_level": log_level.upper(),
                "output_format": output_format.lower(),
                "profile": profile,
            }

            # Apply CLI overrides to configuration
            config_result = FlextCliConfigs.apply_cli_overrides(config_data)
            if config_result.is_failure:
                click.echo(f"Configuration error: {config_result.error}", err=True)
                ctx.exit(1)

            config = config_result.unwrap()

            # Initialize logging setup for side-effects and configure unified logging.
            # Use the initializer directly (no local variable) to avoid unused-variable lints.
            FlextCliLoggingSetup(config)
            self._setup_unified_logging(config)

            # Store configuration in context
            ctx.ensure_object(dict)
            ctx.obj["config"] = config
            ctx.obj["context"] = self._create_application_context(config)

            # Show help if no command provided
            if ctx.invoked_subcommand is None:
                click.echo(ctx.get_help())

        return cli_group

    def add_command(
        self,
        name: str,
        _callback: Callable,
        help_text: str = "",
        click_options: dict[str, object] | None = None,
    ) -> click.Command:
        """Add a command to the CLI with automatic parameter handling."""

        def command_wrapper(ctx: click.Context, **kwargs: object) -> None:
            """Wrapper that provides application context and handles errors."""
            if not self._application:
                click.echo("No application registered", err=True)
                ctx.exit(1)

            # Get application context from parent context
            app_context = ctx.obj.get("context")
            if not app_context:
                click.echo("Application context not available", err=True)
                ctx.exit(1)

            try:
                # Execute command through application
                result = self._application.execute_command(name, kwargs, app_context)

                if result.is_failure:
                    app_context.display_error(
                        f"Command '{name}' failed", Exception(result.error)
                    )
                    ctx.exit(1)

                # Display success if verbose
                if app_context.is_verbose:
                    app_context.display_success(
                        f"Command '{name}' completed successfully"
                    )

            except Exception as e:
                app_context.display_error(f"Unexpected error in command '{name}'", e)
                ctx.exit(1)

        # Create the Click Command object directly to satisfy static typing
        command = click.Command(name, callback=command_wrapper, help=help_text)

        # Apply additional Click options if provided in a list form
        options_list = []
        if isinstance(click_options, dict):
            options_list = click_options.get("options", [])
        if isinstance(options_list, list):
            for opt_entry in options_list:
                # Expect each entry to be a tuple/list: (param_decls, param_kwargs)
                if (
                    isinstance(opt_entry, (list, tuple))
                    and len(opt_entry) == OPT_ENTRY_TUPLE_LEN
                ):
                    param_decls, param_kwargs = opt_entry
                    if isinstance(param_decls, (list, tuple)) and isinstance(
                        param_kwargs, dict
                    ):
                        opt = click.Option(list(param_decls), **param_kwargs)
                        command.params.append(opt)

        # Store and return the command
        self._commands[name] = command
        return command

    def _setup_unified_logging(self, config: FlextCliConfigs) -> None:
        """Setup unified logging configuration automatically."""
        try:
            # Initialize logging setup for side-effects only (don't keep unused var)
            FlextCliLoggingSetup(config)

            # Configure logging based on unified config
            log_level = "DEBUG" if config.trace or config.debug else config.log_level
            verbosity = (
                "full"
                if config.trace
                else ("detailed" if config.verbose else "compact")
            )

            # Configure FlextLogger globally
            FlextLogger.configure(
                log_level=log_level,
                structured_output=True,
                json_output=False,
                include_source=config.debug,
                log_verbosity=verbosity,
            )

            # Set environment variables for cross-project consistency
            os.environ["FLEXT_LOG_LEVEL"] = log_level
            os.environ["FLEXT_LOG_VERBOSITY"] = verbosity

            self._logger.debug(
                f"Unified logging configured: level={log_level}, verbosity={verbosity}"
            )

        except Exception as e:
            # Fallback logging configuration
            FlextLogger.configure(log_level="INFO")
            self._logger.warning(f"Failed to setup unified logging: {e}")

    def _create_application_context(
        self, config: FlextCliConfigs
    ) -> FlextCliApplicationContext:
        """Create application context with all required components."""
        logger = FlextLogger(self.app_name)
        formatter = FlextCliFormatters()
        output_handler = FlextCliOutputHandler(config, formatter)

        return FlextCliApplicationContext(config, logger, formatter, output_handler)

    def _print_version(
        self, ctx: click.Context, _param: click.Parameter, value: object
    ) -> None:
        """Print version and exit.

        The callback signature is adjusted to match Click's typing expectations
        where the callback receives (ctx, param, value). Use a permissive type
        for value to satisfy static checkers.
        """
        if not value or ctx.resilient_parsing:
            return

        click.echo(f"{self.app_name} v{self.app_version}")
        click.echo(f"FLEXT CLI Framework: {FlextConfig.get_global_instance().version}")
        click.echo(
            f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )
        ctx.exit()

    def run(self, args: list[str] | None = None) -> None:
        """Run the CLI application."""
        cli_group = self.create_cli_group()

        # Add all registered commands to the group
        for name, command in self._commands.items():
            cli_group.add_command(command, name=name)

        # Execute the CLI
        cli_group.main(args=args, standalone_mode=False)


# Convenience decorator for easy command registration
def flext_cli_command(
    cli: FlextUnifiedCli,
    name: str | None = None,
    help_text: str = "",
    click_options: dict[str, object] | None = None,
) -> Callable:
    """Decorator to register a command with FlextUnifiedCli."""

    def decorator(func: Callable) -> Callable:
        command_name = name or func.__name__
        # Forward click options as a dictionary to match add_command signature
        options_dict = click_options if isinstance(click_options, dict) else None
        cli.add_command(command_name, func, help_text, click_options=options_dict)
        return func

    return decorator


__all__ = [
    "FlextCliApplication",
    "FlextCliApplicationContext",
    "FlextCliOutputHandler",
    "FlextUnifiedCli",
    "flext_cli_command",
]
