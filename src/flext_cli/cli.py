"""FLEXT CLI - Typer/Click Abstraction Layer.

This is the ONLY file in the entire FLEXT ecosystem allowed to import Typer/Click.
All CLI framework functionality is exposed through this unified interface.

ZERO TOLERANCE ENFORCEMENT: No other file may import Typer or Click directly.

Implementation: Uses Typer as the backend framework. Since Typer is built on Click,
it generates Click-compatible commands internally, ensuring backward compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import IO

import click
import typer
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextTypes,
)
from typer.testing import CliRunner

# Type aliases
Context = typer.Context
ClickContext = typer.Context
ClickCliRunner = CliRunner

# FlextCliMain is imported inside main() to avoid circular import


class FlextCliCli:
    """Complete CLI framework abstraction layer.

    This class provides a unified CLI interface using Typer as the backend framework.
    Since Typer is built on Click, it generates Click-compatible commands internally,
    ensuring full backward compatibility while enabling modern type-driven development.

    Provides direct APIs for:

    - Command and group creation (Typer-based, Click-compatible)
    - Decorators (option, argument, command)
    - Parameter types (Choice, Path, File, IntRange, etc.)
    - Context management
    - Command execution and testing

    Examples:
        >>> cli = FlextCliCli()
        >>>
        >>> # Create command decorator (Typer backend, Click-compatible output)
        >>> command = cli.create_command_decorator(name="greet")
        >>>
        >>> # Create option decorator
        >>> option = cli.create_option_decorator(
        ...     "--count", "-c", default=1, help="Number of greetings"
        ... )
        >>>
        >>> # Execute command with CliRunner
        >>> runner = cli.create_cli_runner()
        >>> result = runner.invoke(my_command, ["--count", "3"])

    Note:
        ALL CLI framework functionality MUST be accessed through this class.
        Direct Typer or Click imports are FORBIDDEN in ecosystem projects.

    """

    def __init__(self) -> None:
        """Initialize CLI abstraction layer with Typer backend."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer()

    # =========================================================================
    # COMMAND AND GROUP CREATION
    # =========================================================================

    def create_command_decorator(
        self,
        name: str | None = None,
        **kwargs: object,
    ) -> Callable[[Callable[..., object]], click.Command]:
        """Create Click command decorator without exposing Click.

        Args:
            name: Command name (optional, uses function name if None)
            **kwargs: Click command options (help, context_settings, etc.)

        Returns:
            Command decorator function

        Example:
            >>> cli = FlextCliCli()
            >>> decorator = cli.create_command_decorator(
            ...     name="hello", help="Greet someone"
            ... )
            >>> @decorator
            ... def hello():
            ...     click.echo("Hello!")

        """
        command_kwargs: dict[str, object] = {"name": name}
        command_kwargs.update(kwargs)
        decorator = click.command(**command_kwargs)
        self._logger.debug(
            "Created command decorator",
            extra={"command_name": name, "options": kwargs},
        )
        return decorator

    def create_group_decorator(
        self,
        name: str | None = None,
        **kwargs: object,
    ) -> Callable[[Callable[..., object]], click.Group]:
        """Create Click group decorator for command groups.

        Args:
            name: Group name (optional, uses function name if None)
            **kwargs: Click group options

        Returns:
            Group decorator function

        Example:
            >>> cli = FlextCliCli()
            >>> group = cli.create_group_decorator(name="db")
            >>> @group
            ... def db():
            ...     '''Database commands'''
            ...     pass

        """
        group_kwargs: dict[str, object] = {"name": name}
        group_kwargs.update(kwargs)
        decorator = click.group(**group_kwargs)
        self._logger.debug(
            "Created group decorator",
            extra={"group_name": name, "options": kwargs},
        )
        return decorator

    # =========================================================================
    # PARAMETER DECORATORS (OPTION, ARGUMENT)
    # =========================================================================

    def create_option_decorator(
        self,
        *param_decls: str,
        **attrs: object,
    ) -> object:
        """Create Click option decorator.

        Args:
            *param_decls: Parameter declarations (e.g., "--count", "-c")
            **attrs: Option attributes (default, help, type, required, etc.)

        Returns:
            Option decorator

        Example:
            >>> cli = FlextCliCli()
            >>> option = cli.create_option_decorator(
            ...     "--verbose", "-v", is_flag=True, help="Enable verbose output"
            ... )

        """
        decorator = click.option(*param_decls, **attrs)
        self._logger.debug(
            "Created option decorator",
            extra={"param_decls": param_decls, "attrs": attrs},
        )
        return decorator

    def create_argument_decorator(
        self,
        *param_decls: str,
        **attrs: object,
    ) -> object:
        """Create Click argument decorator.

        Args:
            *param_decls: Parameter declarations (e.g., "filename")
            **attrs: Argument attributes (type, required, nargs, etc.)

        Returns:
            Argument decorator

        Example:
            >>> cli = FlextCliCli()
            >>> argument = cli.create_argument_decorator(
            ...     "filename", type=cli.get_path_type()
            ... )

        """
        decorator = click.argument(*param_decls, **attrs)
        self._logger.debug(
            "Created argument decorator",
            extra={"param_decls": param_decls, "attrs": attrs},
        )
        return decorator

    # =========================================================================
    # PARAMETER TYPES
    # =========================================================================

    def get_choice_type(
        self, choices: Sequence[str], *, case_sensitive: bool = True
    ) -> click.Choice:
        """Get Click Choice parameter type.

        Args:
            choices: Available choices
            case_sensitive: Whether choices are case-sensitive

        Returns:
            Click Choice type

        Example:
            >>> cli = FlextCliCli()
            >>> choice_type = cli.get_choice_type(["json", "yaml", "csv"])

        """
        return click.Choice(choices, case_sensitive=case_sensitive)

    def get_path_type(
        self,
        *,
        exists: bool = False,
        file_okay: bool = True,
        dir_okay: bool = True,
        writable: bool = False,
        readable: bool = True,
        resolve_path: bool = False,
        path_type: type[str | Path] = str,
    ) -> click.Path:
        """Get Click Path parameter type.

        Args:
            exists: Path must exist
            file_okay: Accept files
            dir_okay: Accept directories
            writable: Path must be writable
            readable: Path must be readable
            resolve_path: Resolve to absolute path
            path_type: Return type (str or Path)

        Returns:
            Click Path type

        """
        return click.Path(
            exists=exists,
            file_okay=file_okay,
            dir_okay=dir_okay,
            writable=writable,
            readable=readable,
            resolve_path=resolve_path,
            path_type=path_type,
        )

    def get_file_type(
        self,
        mode: str = "r",
        encoding: str | None = None,
        errors: str | None = "strict",
        *,
        lazy: bool | None = None,
        atomic: bool = False,
    ) -> click.File:
        """Get Click File parameter type.

        Args:
            mode: File mode (r, w, rb, wb, etc.)
            encoding: Text encoding
            errors: Error handling strategy
            lazy: Lazy file opening
            atomic: Atomic file writing

        Returns:
            Click File type

        """
        return click.File(
            mode=mode,
            encoding=encoding,
            errors=errors,
            lazy=lazy,
            atomic=atomic,
        )

    def get_int_range_type(
        self,
        min_val: int | None = None,
        max_val: int | None = None,
        *,
        min_open: bool = False,
        max_open: bool = False,
        clamp: bool = False,
    ) -> click.IntRange:
        """Get Click IntRange parameter type.

        Args:
            min_val: Minimum value (inclusive unless min_open=True)
            max_val: Maximum value (inclusive unless max_open=True)
            min_open: Minimum is exclusive
            max_open: Maximum is exclusive
            clamp: Clamp values to range instead of error

        Returns:
            Click IntRange type

        """
        return click.IntRange(
            min=min_val,
            max=max_val,
            min_open=min_open,
            max_open=max_open,
            clamp=clamp,
        )

    def get_float_range_type(
        self,
        min_val: float | None = None,
        max_val: float | None = None,
        *,
        min_open: bool = False,
        max_open: bool = False,
        clamp: bool = False,
    ) -> click.FloatRange:
        """Get Click FloatRange parameter type.

        Args:
            min_val: Minimum value (inclusive unless min_open=True)
            max_val: Maximum value (inclusive unless max_open=True)
            min_open: Minimum is exclusive
            max_open: Maximum is exclusive
            clamp: Clamp values to range instead of error

        Returns:
            Click FloatRange type

        """
        return click.FloatRange(
            min=min_val,
            max=max_val,
            min_open=min_open,
            max_open=max_open,
            clamp=clamp,
        )

    def get_datetime_type(
        self,
        formats: Sequence[str] | None = None,
    ) -> click.DateTime:
        """Get Click DateTime parameter type.

        Args:
            formats: Accepted datetime formats (default: ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'])

        Returns:
            Click DateTime type

        Example:
            >>> cli = FlextCliCli()
            >>> dt_type = cli.get_datetime_type(formats=["%Y-%m-%d", "%d/%m/%Y"])

        """
        if formats is None:
            formats = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]
        return click.DateTime(formats=formats)

    def get_uuid_type(self) -> click.ParamType:
        """Get Click UUID parameter type.

        Returns:
            Click UUID parameter type instance

        Example:
            >>> cli = FlextCliCli()
            >>> uuid_type = cli.get_uuid_type()
            >>> # Use in option: type=uuid_type

        """
        return click.UUID

    def get_tuple_type(
        self,
        types: Sequence[type[object] | click.ParamType],
    ) -> click.Tuple:
        """Get Click Tuple parameter type.

        Args:
            types: Sequence of types for tuple elements

        Returns:
            Click Tuple type

        Example:
            >>> cli = FlextCliCli()
            >>> # Tuple of (int, int, int) for RGB values
            >>> rgb_type = cli.get_tuple_type([int, int, int])
            >>> # Tuple of (str, int) for name and age
            >>> person_type = cli.get_tuple_type([str, int])

        """
        return click.Tuple(types)

    def get_bool_type(self) -> type[bool]:
        """Get bool parameter type.

        Returns:
            bool type for Click parameters

        Example:
            >>> cli = FlextCliCli()
            >>> bool_type = cli.get_bool_type()
            >>> # Use in option: type=bool_type

        """
        return bool

    def get_string_type(self) -> type[str]:
        """Get string parameter type.

        Returns:
            str type for Click parameters

        Example:
            >>> cli = FlextCliCli()
            >>> str_type = cli.get_string_type()

        """
        return str

    def get_int_type(self) -> type[int]:
        """Get integer parameter type.

        Returns:
            int type for Click parameters

        Example:
            >>> cli = FlextCliCli()
            >>> int_type = cli.get_int_type()

        """
        return int

    def get_float_type(self) -> type[float]:
        """Get float parameter type.

        Returns:
            float type for Click parameters

        Example:
            >>> cli = FlextCliCli()
            >>> float_type = cli.get_float_type()

        """
        return float

    # =========================================================================
    # CONTEXT MANAGEMENT
    # =========================================================================

    def get_current_context(self) -> click.Context | None:
        """Get current CLI context.

        Returns:
            Current CLI context or None if not available

        Example:
            >>> cli = FlextCliCli()
            >>> ctx = cli.get_current_context()
            >>> if ctx:
            ...     print(ctx.command.name)

        """
        return click.get_current_context(silent=True)

    def create_pass_context_decorator(
        self,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Create pass_context decorator.

        Returns:
            pass_context decorator

        Example:
            >>> cli = FlextCliCli()
            >>> pass_ctx = cli.create_pass_context_decorator()
            >>>
            >>> @pass_ctx
            >>> def my_command(ctx):
            ...     print(f"Command: {ctx.command.name}")

        """
        return click.pass_context

    # =========================================================================
    # COMMAND EXECUTION
    # =========================================================================

    def echo(
        self,
        message: str | None = None,
        file: IO[str] | None = None,
        *,
        nl: bool = True,
        err: bool = False,
        color: bool | None = None,
    ) -> FlextResult[None]:
        """Output message using Typer.echo (Typer backend).

        Args:
            message: Message to output
            file: File to write to (default: stdout)
            nl: Add newline
            err: Write to stderr
            color: Force color on/off

        Returns:
            FlextResult[None]: Success or failure of echo operation

        """
        typer.echo(message=message, file=file, nl=nl, err=err, color=color)
        return FlextResult[None].ok(None)

    def confirm(
        self,
        text: str,
        *,
        default: bool = False,
        abort: bool = False,
        prompt_suffix: str = ": ",
        show_default: bool = True,
        err: bool = False,
    ) -> FlextResult[bool]:
        """Prompt for confirmation using Typer backend.

        Args:
            text: Prompt text
            default: Default value
            abort: Abort if not confirmed
            prompt_suffix: Suffix after prompt
            show_default: Show default in prompt
            err: Write to stderr

        Returns:
            FlextResult[bool]: Success with confirmation value or failure

        Raises:
            typer.Abort: If user aborts

        """
        try:
            result = typer.confirm(
                text=text,
                default=default,
                abort=abort,
                prompt_suffix=prompt_suffix,
                show_default=show_default,
                err=err,
            )
            return FlextResult[bool].ok(result)
        except typer.Abort as e:
            return FlextResult[bool].fail(f"User aborted confirmation: {e}")

    def prompt(
        self,
        text: str,
        default: object | None = None,
        type_hint: object | None = None,
        value_proc: Callable[[str], object] | None = None,
        prompt_suffix: str = ": ",
        *,
        hide_input: bool = False,
        confirmation_prompt: bool = False,
        show_default: bool = True,
        err: bool = False,
        show_choices: bool = True,
    ) -> FlextResult[object]:
        """Prompt for input using Typer backend.

        Args:
            text: Prompt text
            default: Default value
            hide_input: Hide user input (for passwords)
            confirmation_prompt: Ask for confirmation
            type_hint: Value type
            value_proc: Value processor function
            prompt_suffix: Suffix after prompt
            show_default: Show default in prompt
            err: Write to stderr
            show_choices: Show available choices

        Returns:
            FlextResult[object]: Success with user input or failure

        Raises:
            typer.Abort: If user aborts

        """
        try:
            result = typer.prompt(
                text=text,
                default=default,
                hide_input=hide_input,
                confirmation_prompt=confirmation_prompt,
                type=type_hint,
                value_proc=value_proc,
                prompt_suffix=prompt_suffix,
                show_default=show_default,
                err=err,
                show_choices=show_choices,
            )
            return FlextResult[object].ok(result)
        except typer.Abort as e:
            return FlextResult[object].fail(f"User aborted prompt: {e}")

    # =========================================================================
    # TESTING SUPPORT
    # =========================================================================

    def create_cli_runner(
        self,
        charset: str = "utf-8",
        env: FlextTypes.StringDict | None = None,
        *,
        echo_stdin: bool = False,
    ) -> FlextResult[ClickCliRunner]:
        """Create Click CliRunner for testing.

        Args:
            charset: Character encoding
            env: Environment variables
            echo_stdin: Echo stdin to output

        Returns:
            FlextResult[ClickCliRunner]: Success with CliRunner instance or failure

        Example:
            >>> cli = FlextCliCli()
            >>> result = cli.create_cli_runner()
            >>> assert result.is_success
            >>> runner = result.unwrap()
            >>> test_result = runner.invoke(my_cli, ["--help"])
            >>> assert test_result.exit_code == 0

        """
        runner = ClickCliRunner(
            charset=charset,
            env=env,
            echo_stdin=echo_stdin,
        )
        self._logger.debug("Created CliRunner for testing")
        return FlextResult[ClickCliRunner].ok(runner)

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def format_filename(
        self,
        filename: str | Path,
        *,
        shorten: bool = False,
    ) -> str:
        """Format filename for display.

        Args:
            filename: Filename to format
            shorten: Shorten filename

        Returns:
            Formatted filename string

        """
        return click.format_filename(filename, shorten=shorten)

    def get_terminal_size(self) -> tuple[int, int]:
        """Get terminal size.

        Returns:
            Tuple of (width, height)

        """
        size = click.get_terminal_size()
        return (size[0], size[1])

    def clear_screen(self) -> FlextResult[None]:
        """Clear terminal screen.

        Returns:
            FlextResult[None]: Success or failure of clear operation

        """
        click.clear()
        return FlextResult[None].ok(None)

    def pause(self, info: str = "Press any key to continue...") -> FlextResult[None]:
        """Pause execution until key press.

        Args:
            info: Information message to display

        Returns:
            FlextResult[None]: Success or failure of pause operation

        """
        click.pause(info=info)
        return FlextResult[None].ok(None)

    def execute(self) -> FlextResult[object]:
        """Execute Click abstraction layer operations.

        Returns:
            FlextResult[object]: Success with CLI status or failure with error

        """
        return FlextResult[object].ok({"service": "flext-cli", "status": "operational"})


__all__ = [
    "FlextCliCli",
]
