"""CLI Foundation - Modern Clean Architecture CLI framework.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the new CLI foundation built on flext_core patterns and
Clean Architecture principles. It replaces the old BaseCLI with semantic,
type-safe, and highly maintainable CLI framework integration.
"""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Protocol

import click
from flext_core import DomainModel, Field, ServiceResult
from rich.console import Console

from flext_cli.adapters.output import RichRenderer
from flext_cli.domain.value_objects import CLIContext, OutputFormat
from flext_cli.domain.value_objects.cli_context import CLIProfile

if TYPE_CHECKING:
    from flext_cli.application.services import CLIApplicationService


class CLIAdapterProtocol(Protocol):
    """Protocol for CLI framework adapters."""

    def create_cli_group(self) -> click.Group:
        """Create the main CLI group."""
        ...

    def handle_result(self, result: ServiceResult[Any], context: CLIContext) -> None:
        """Handle service result with proper output."""
        ...

    def setup_context(self, ctx: click.Context, **kwargs: Any) -> CLIContext:
        """Setup CLI context from Click context."""
        ...


class CLICommand(DomainModel):
    """Domain model for CLI command definition."""

    name: str = Field(..., description="Command name")
    description: str = Field(..., description="Command description")
    help_text: str | None = Field(None, description="Detailed help text")
    hidden: bool = Field(default=False, description="Hide command from help")
    deprecated: bool = Field(default=False, description="Mark command as deprecated")
    group: str | None = Field(None, description="Command group")


class CLIFoundation(ABC):
    """Modern CLI foundation built on Clean Architecture and flext_core patterns.

    This class replaces the old BaseCLI with a cleaner, more semantic approach
    that properly separates concerns and follows SOLID principles.
    """

    def __init__(
        self,
        *,
        name: str,
        version: str,
        description: str,
        app_service: CLIApplicationService,
        default_context: CLIContext | None = None,
    ) -> None:
        """Initialize CLI foundation.

        Args:
            name: Application name
            version: Application version
            description: Application description
            app_service: Application service for business logic
            default_context: Default CLI context

        """
        self.name = name
        self.version = version
        self.description = description
        self.app_service = app_service
        self.default_context = default_context or CLIContext()

        # Initialize adapters
        self.console = Console(
            no_color=self.default_context.output.no_color,
            force_terminal=not self.default_context.is_production,
        )
        self.renderer = RichRenderer(console=self.console)

    @abstractmethod
    def register_commands(self, cli_group: click.Group) -> None:
        """Register application-specific commands.

        Args:
            cli_group: Click group to register commands with

        """
        ...

    def create_cli(self) -> click.Group:
        """Create the main CLI application with proper Click integration."""

        @click.group(
            name=self.name,
            help=self.description,
            context_settings={
                "help_option_names": ["-h", "--help"],
                "show_default": True,
            },
        )
        @click.version_option(
            version=self.version,
            prog_name=self.name,
            message="%(prog)s v%(version)s",
        )
        @click.option(
            "--profile",
            default="default",
            help="CLI profile to use",
            type=click.Choice(["default", "development", "production"]),
        )
        @click.option(
            "--format",
            default=self.default_context.output.format.value,
            help="Output format",
            type=click.Choice([f.value for f in OutputFormat]),
        )
        @click.option(
            "--no-color",
            is_flag=True,
            default=self.default_context.output.no_color,
            help="Disable color output",
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            default=self.default_context.output.verbose,
            help="Enable verbose output",
        )
        @click.option(
            "--quiet",
            "-q",
            is_flag=True,
            default=self.default_context.output.quiet,
            help="Suppress non-essential output",
        )
        @click.option(
            "--debug",
            is_flag=True,
            default=self.default_context.debug,
            help="Enable debug mode",
        )
        @click.option(
            "--config",
            help="Configuration file path",
            type=click.Path(exists=True),
        )
        @click.option(
            "--timeout",
            default=self.default_context.timeout_seconds,
            help="Command timeout in seconds",
            type=float,
        )
        @click.pass_context
        def cli_main(
            ctx: click.Context,
            profile: str,
            output_format: str,
            no_color: bool,
            verbose: bool,
            quiet: bool,
            debug: bool,
            config: str | None,
            timeout: float,
        ) -> None:
            """Main CLI entry point with context setup."""
            # Create CLI context from options
            cli_context = self._create_context_from_options(
                profile=profile,
                output_format=output_format,
                no_color=no_color,
                verbose=verbose,
                quiet=quiet,
                debug=debug,
                config_file=config,
                timeout=timeout,
            )

            # Store context in Click context
            ctx.ensure_object(dict)
            ctx.obj["cli_context"] = cli_context
            ctx.obj["foundation"] = self
            ctx.obj["app_service"] = self.app_service
            ctx.obj["renderer"] = self.renderer

            # Setup console for context
            self.console = Console(
                no_color=cli_context.output.no_color,
                force_terminal=not cli_context.is_production,
            )
            self.renderer = RichRenderer(console=self.console)

        # Register application commands
        self.register_commands(cli_main)

        return cli_main

    def handle_service_result(
        self,
        result: ServiceResult[Any],
        context: CLIContext,
        success_message: str | None = None,
    ) -> None:
        """Handle service result with proper rendering and exit codes.

        Args:
            result: Service result to handle
            context: CLI context for rendering options
            success_message: Optional custom success message

        """
        if result.success:
            if success_message and not context.is_quiet:
                self.renderer.render_success(success_message)
            elif result.data is not None and not context.is_quiet:
                self.renderer.render_data(result.data, context)
        else:
            self.renderer.render_error(result.error or "Unknown error", context)
            if not context.is_debug:
                sys.exit(1)
            # In debug mode, don't exit to allow investigation

    def print_header(self, context: CLIContext) -> None:
        """Print application header if not in quiet mode.

        Args:
            context: CLI context for output options

        """
        if not context.is_quiet:
            self.renderer.render_header(
                title=f"{self.name} v{self.version}",
                description=self.description,
                context=context,
            )

    def create_command_decorator(
        self,
        *,
        requires_auth: bool = False,
        REDACTED_LDAP_BIND_PASSWORD_required: bool = False,
    ) -> Any:
        """Create decorator for CLI commands with common patterns.

        Args:
            requires_auth: Whether command requires authentication
            REDACTED_LDAP_BIND_PASSWORD_required: Whether command requires REDACTED_LDAP_BIND_PASSWORD role

        Returns:
            Decorator function for CLI commands

        """

        def decorator(func: Any) -> Any:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Get context from Click
                ctx = click.get_current_context()
                cli_context: CLIContext = ctx.obj["cli_context"]

                # Check authentication if required
                if requires_auth and not cli_context.is_authenticated:
                    self.renderer.render_error(
                        "Authentication required. Please login first.",
                        cli_context,
                    )
                    sys.exit(1)

                # Check REDACTED_LDAP_BIND_PASSWORD role if required
                if REDACTED_LDAP_BIND_PASSWORD_required and not cli_context.auth.has_REDACTED_LDAP_BIND_PASSWORD_rights:
                    self.renderer.render_error(
                        "Admin privileges required for this command.",
                        cli_context,
                    )
                    sys.exit(1)

                # Inject CLI context into function arguments
                kwargs["cli_context"] = cli_context
                kwargs["app_service"] = ctx.obj["app_service"]
                kwargs["renderer"] = ctx.obj["renderer"]

                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if cli_context.is_debug:
                        raise
                    self.renderer.render_error(str(e), cli_context)
                    sys.exit(1)

            # Preserve function metadata
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper

        return decorator

    def _create_context_from_options(
        self,
        *,
        profile: str,
        output_format: str,
        no_color: bool,
        verbose: bool,
        quiet: bool,
        debug: bool,
        config_file: str | None,
        timeout: float,
    ) -> CLIContext:
        """Create CLI context from command line options.

        Args:
            profile: CLI profile
            output_format: Output format
            no_color: No color flag
            verbose: Verbose flag
            quiet: Quiet flag
            debug: Debug flag
            config_file: Configuration file path
            timeout: Command timeout

        Returns:
            Configured CLI context

        """
        # Start with default context
        context = self.default_context

        # Apply command line options
        profile_obj = CLIProfile(name=profile, api_url="http://localhost:8000")
        context = context.with_profile(profile_obj)

        # Update output configuration
        output_config = context.output.model_copy(update={
            "format": OutputFormat(output_format),
            "verbose": verbose,
            "quiet": quiet,
        })

        # Create new context with updated values
        updates = {
            "verbose": verbose,
            "debug": debug,
            "timeout_seconds": timeout,
            "output": output_config,
        }

        if config_file:
            updates["config_path"] = config_file

        return context.model_copy(update=updates)


class ClickCLIAdapter:
    """Adapter for Click CLI framework integration."""

    def __init__(self, foundation: CLIFoundation) -> None:
        """Initialize Click adapter.

        Args:
            foundation: CLI foundation instance

        """
        self.foundation = foundation

    def create_cli_group(self) -> click.Group:
        """Create CLI group with Click framework."""
        return self.foundation.create_cli()

    def handle_result(self, result: ServiceResult[Any], context: CLIContext) -> None:
        """Handle service result using foundation."""
        self.foundation.handle_service_result(result, context)

    def setup_context(self, ctx: click.Context, **kwargs: Any) -> CLIContext:
        """Setup CLI context from Click context."""
        from typing import cast

        result = ctx.obj.get("cli_context", self.foundation.default_context)
        return cast("CLIContext", result)


# Utility functions for backward compatibility
def with_cli_context(func: Any) -> Any:
    """Decorator to inject CLI context into command functions."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        ctx = click.get_current_context()
        cli_context = ctx.obj.get("cli_context")
        if cli_context:
            kwargs["cli_context"] = cli_context
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def handle_service_result(func: Any) -> Any:
    """Decorator to automatically handle service results."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        ctx = click.get_current_context()
        foundation: CLIFoundation = ctx.obj.get("foundation")
        cli_context: CLIContext = ctx.obj.get("cli_context")

        if not foundation or not cli_context:
            msg = "CLI foundation not properly initialized"
            raise RuntimeError(msg)

        result = func(*args, **kwargs)

        # Handle ServiceResult objects
        if isinstance(result, ServiceResult):
            foundation.handle_service_result(result, cli_context)

        return result

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
