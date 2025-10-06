"""FLEXT CLI - Typer Abstraction Layer.

This module provides the Typer abstraction layer for the FLEXT CLI ecosystem.
It is the ONLY module allowed to import Typer directly, maintaining ZERO TOLERANCE
for direct Typer imports anywhere else in the ecosystem.

ZERO TOLERANCE ENFORCEMENT:
- ONLY this file (typer_cli.py) may import Typer
- All Typer functionality must be abstracted through FlextCliTyper
- Ecosystem projects MUST NOT import Typer directly

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any

import typer
from flext_core import (
    FlextResult,
    FlextService,
)


class FlextCliTyper(FlextService[object]):
    """Typer abstraction layer for FLEXT CLI ecosystem.

    Provides complete abstraction over Typer framework, enabling modern
    type-driven CLI development while maintaining ZERO TOLERANCE policy
    for direct Typer imports in ecosystem projects.

    Features:
        - Type-driven command creation from function signatures
        - Automatic validation from type hints
        - Native async/await support
        - Pydantic model integration
        - Rich formatting integration (via existing FlextCliFormatters)
        - Complete Click compatibility (Typer built on Click)

    Examples:
        >>> typer_cli = FlextCliTyper()
        >>>
        >>> # Create Typer app
        >>> app_result = typer_cli.create_app(name="myapp")
        >>> app = app_result.unwrap()
        >>>
        >>> # Create type-driven command
        >>> def greet(name: str, count: int = 1):
        ...     '''Greet someone.'''
        ...     print(f"Hello {name}!" * count)
        >>>
        >>> cmd_result = typer_cli.create_command(
        ...     func=greet,
        ...     name="greet",
        ... )

    Note:
        This is the ONLY file in the entire FLEXT ecosystem allowed to
        import Typer directly. All other modules must use FlextCliTyper.

    """

    def __init__(self) -> None:
        """Initialize Typer abstraction layer with Phase 1 context enrichment."""
        super().__init__()
        # Logger and container inherited from FlextService via FlextMixins

        if self.logger:
            self.logger.debug(
                "Initialized Typer abstraction layer",
                extra={
                    "typer_version": typer.__version__,
                },
            )

    # =========================================================================
    # TYPER APP CREATION
    # =========================================================================

    def create_app(
        self,
        name: str = "app",
        help_text: str | None = None,
        *,
        add_completion: bool = True,
        pretty_exceptions_enable: bool = True,
        **kwargs: object,
    ) -> FlextResult[typer.Typer]:
        """Create a Typer application.

        Args:
            name: Application name
            help_text: Application help text
            add_completion: Enable shell completion
            pretty_exceptions_enable: Enable pretty exceptions
            **kwargs: Additional Typer options

        Returns:
            FlextResult containing Typer app

        Example:
            >>> typer_cli = FlextCliTyper()
            >>> app_result = typer_cli.create_app(
            ...     name="myapp",
            ...     help_text="My application",
            ... )
            >>> if app_result.is_success:
            ...     app = app_result.unwrap()

        """
        try:
            app = typer.Typer(
                name=name,
                help=help_text,
                add_completion=add_completion,
                pretty_exceptions_enable=pretty_exceptions_enable,
                **kwargs,
            )

            if self.logger:
                self.logger.debug(
                    "Created Typer app",
                    extra={
                        "app_name": name,
                    },
                )

            return FlextResult[typer.Typer].ok(app)

        except Exception as e:
            error_msg = f"Failed to create Typer app: {e}"
            if self.logger:
                self.logger.exception(error_msg)
            return FlextResult[typer.Typer].fail(error_msg)

    # =========================================================================
    # COMMAND CREATION
    # =========================================================================

    def create_command(
        self,
        func: Callable[..., Any],
        name: str | None = None,
        help_text: str | None = None,
        **kwargs: object,
    ) -> FlextResult[Callable[..., Any]]:
        """Create a Typer command from a function.

        The function signature determines the CLI interface:
        - Regular parameters → CLI arguments
        - Parameters with defaults → CLI options
        - Type hints → automatic validation
        - Docstring → help text

        Args:
            func: Function to convert to command
            name: Command name (optional, uses function name if None)
            help_text: Help text (optional, uses docstring if None)
            **kwargs: Additional Typer command options

        Returns:
            FlextResult containing command function

        Example:
            >>> def greet(name: str, count: int = 1):
            ...     '''Greet someone multiple times.'''
            ...     for _ in range(count):
            ...         print(f"Hello {name}!")
            >>>
            >>> cmd_result = typer_cli.create_command(
            ...     func=greet,
            ...     name="greet",
            ... )

        """
        try:
            # Note: Typer commands are created via decorator or app.command()
            # This method prepares the function for registration
            command_name = name or func.__name__

            if self.logger:
                self.logger.debug(
                    "Created Typer command",
                    extra={
                        "command_name": command_name,
                        "function": func.__name__,
                        "help_provided": help_text is not None,
                        "kwargs_count": len(kwargs),
                    },
                )

            # Store metadata for potential future use
            if hasattr(func, "__flext_cli_metadata__"):
                getattr(func, "__flext_cli_metadata__").update({
                    "name": command_name,
                    "help": help_text,
                    "kwargs": kwargs,
                })
            else:
                func.__flext_cli_metadata__ = {
                    "name": command_name,
                    "help": help_text,
                    "kwargs": kwargs,
                }

            return FlextResult[Callable[..., Any]].ok(func)

        except Exception as e:
            error_msg = f"Failed to create Typer command: {e}"
            if self.logger:
                self.logger.exception(error_msg)
            return FlextResult[Callable[..., Any]].fail(error_msg)

    # =========================================================================
    # COMMAND DECORATOR CREATION
    # =========================================================================

    def create_command_decorator(
        self,
        app: typer.Typer,
        name: str | None = None,
        help_text: str | None = None,
        **kwargs: object,
    ) -> FlextResult[Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Create a command decorator for a Typer app.

        Args:
            app: Typer application to register command with
            name: Command name (optional)
            help_text: Help text (optional)
            **kwargs: Additional Typer command options

        Returns:
            FlextResult containing command decorator

        Example:
            >>> app_result = typer_cli.create_app()
            >>> app = app_result.unwrap()
            >>>
            >>> decorator_result = typer_cli.create_command_decorator(
            ...     app=app,
            ...     name="greet",
            ... )
            >>> command_decorator = decorator_result.unwrap()
            >>>
            >>> @command_decorator
            >>> def greet(name: str):
            ...     print(f"Hello {name}!")

        """
        try:
            decorator = app.command(
                name=name,
                help=help_text,
                **kwargs,
            )

            if self.logger:
                self.logger.debug(
                    "Created Typer command decorator",
                    extra={
                        "command_name": name,
                    },
                )

            return FlextResult[Callable[[Callable[..., Any]], Callable[..., Any]]].ok(
                decorator,
            )

        except Exception as e:
            error_msg = f"Failed to create command decorator: {e}"
            if self.logger:
                self.logger.exception(error_msg)
            return FlextResult[Callable[[Callable[..., Any]], Callable[..., Any]]].fail(
                error_msg,
            )

    # =========================================================================
    # ASYNC COMMAND SUPPORT
    # =========================================================================

    def create_async_command(
        self,
        func: Callable[..., Any],
        name: str | None = None,
        help_text: str | None = None,
        **kwargs: object,
    ) -> FlextResult[Callable[..., Any]]:
        """Create an async Typer command from an async function.

        Typer has native support for async commands, providing better
        async/await handling than Click.

        Args:
            func: Async function to convert to command
            name: Command name (optional)
            help_text: Help text (optional)
            **kwargs: Additional Typer command options

        Returns:
            FlextResult containing async command function

        Example:
            >>> async def fetch_data(url: str):
            ...     '''Fetch data from URL.'''
            ...     async with httpx.AsyncClient() as client:
            ...         response = await client.get(url)
            ...         print(response.text)
            >>>
            >>> cmd_result = typer_cli.create_async_command(
            ...     func=fetch_data,
            ...     name="fetch",
            ... )

        """
        try:
            # Verify function is async
            if not inspect.iscoroutinefunction(func):
                return FlextResult[Callable[..., Any]].fail(
                    f"Function '{func.__name__}' is not async",
                )

            command_name = name or func.__name__

            if self.logger:
                self.logger.debug(
                    "Created async Typer command",
                    extra={
                        "command_name": command_name,
                        "function": func.__name__,
                        "help_provided": help_text is not None,
                        "kwargs_count": len(kwargs),
                    },
                )

            # Store metadata for potential future use
            if hasattr(func, "__flext_cli_metadata__"):
                getattr(func, "__flext_cli_metadata__").update({
                    "name": command_name,
                    "help": help_text,
                    "kwargs": kwargs,
                })
            else:
                func.__flext_cli_metadata__ = {
                    "name": command_name,
                    "help": help_text,
                    "kwargs": kwargs,
                }

            return FlextResult[Callable[..., Any]].ok(func)

        except Exception as e:
            error_msg = f"Failed to create async command: {e}"
            if self.logger:
                self.logger.exception(error_msg)
            return FlextResult[Callable[..., Any]].fail(error_msg)

    # =========================================================================
    # ARGUMENT AND OPTION CREATION
    # =========================================================================

    def create_argument(
        self,
        default: object = ...,
        help_text: str | None = None,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Create a Typer Argument for explicit argument definition.

        Args:
            default: Default value (... for required)
            help_text: Help text for the argument
            **kwargs: Additional Typer Argument options

        Returns:
            FlextResult containing Typer Argument

        Example:
            >>> arg_result = typer_cli.create_argument(
            ...     help_text="Name to greet",
            ... )
            >>> name_arg = arg_result.unwrap()
            >>>
            >>> def greet(name: str = name_arg):
            ...     print(f"Hello {name}!")

        """
        try:
            argument = typer.Argument(
                default,
                help=help_text,
                **kwargs,
            )

            return FlextResult[object].ok(argument)

        except Exception as e:
            error_msg = f"Failed to create Typer Argument: {e}"
            if self.logger:
                self.logger.exception(error_msg)
            return FlextResult[object].fail(error_msg)

    def create_option(
        self,
        default: object = None,
        help_text: str | None = None,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Create a Typer Option for explicit option definition.

        Args:
            default: Default value
            help_text: Help text for the option
            **kwargs: Additional Typer Option options

        Returns:
            FlextResult containing Typer Option

        Example:
            >>> opt_result = typer_cli.create_option(
            ...     default=1,
            ...     help_text="Number of times to greet",
            ... )
            >>> count_opt = opt_result.unwrap()
            >>>
            >>> def greet(name: str, count: int = count_opt):
            ...     for _ in range(count):
            ...         print(f"Hello {name}!")

        """
        try:
            option = typer.Option(
                default,
                help=help_text,
                **kwargs,
            )

            return FlextResult[object].ok(option)

        except Exception as e:
            error_msg = f"Failed to create Typer Option: {e}"
            if self.logger:
                self.logger.exception(error_msg)
            return FlextResult[object].fail(error_msg)

    # =========================================================================
    # TYPER UTILITIES
    # =========================================================================

    def echo(self, message: str, **kwargs: object) -> FlextResult[None]:
        """Echo a message using Typer's echo (which uses Rich internally).

        Args:
            message: Message to echo
            **kwargs: Additional echo options

        Returns:
            FlextResult[None]

        Example:
            >>> typer_cli.echo("Hello, World!")
            >>> typer_cli.echo("Error!", fg="red", err=True)

        """
        try:
            typer.echo(message, **kwargs)
            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to echo message: {e}"
            if self.logger:
                self.logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def secho(
        self,
        message: str,
        fg: str | None = None,
        bg: str | None = None,
        *,
        bold: bool = False,
        **kwargs: object,
    ) -> FlextResult[None]:
        """Echo a styled message using Typer.

        Args:
            message: Message to echo
            fg: Foreground color
            bg: Background color
            bold: Make text bold
            **kwargs: Additional style options

        Returns:
            FlextResult[None]

        Example:
            >>> typer_cli.secho("Success!", fg="green", bold=True)
            >>> typer_cli.secho("Warning", fg="yellow")

        """
        try:
            typer.secho(
                message,
                fg=fg,
                bg=bg,
                bold=bold,
                **kwargs,
            )
            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to echo styled message: {e}"
            if self.logger:
                self.logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    # =========================================================================
    # FLEXT SERVICE METHODS
    # =========================================================================

    def execute(self) -> FlextResult[object]:
        """Execute Typer CLI operations.

        Returns:
            FlextResult[None]

        """
        return FlextResult[object].ok(None)


__all__ = [
    "FlextCliTyper",
]
