"""FLEXT CLI - Click Abstraction Layer.

This is the ONLY file in the entire FLEXT ecosystem allowed to import Click.
All Click functionality is wrapped here and exposed through FlextResult-based APIs.

ZERO TOLERANCE ENFORCEMENT: No other file may import Click directly.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import IO, override

import click
from click import Context as ClickContext
from click.testing import CliRunner as ClickCliRunner
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)


class FlextCliClick(FlextService[object]):
    """Complete Click abstraction layer.

    This class wraps ALL Click functionality to prevent direct Click imports
    across the FLEXT ecosystem. Provides FlextResult-based APIs for:

    - Command and group creation
    - Decorators (option, argument, command)
    - Parameter types (Choice, Path, File, IntRange, etc.)
    - Context management
    - Command execution and testing

    Examples:
        >>> cli = FlextCliClick()
        >>>
        >>> # Create command decorator
        >>> cmd_result = cli.create_command_decorator(name="greet")
        >>> if cmd_result.is_success:
        >>>     command = cmd_result.unwrap()
        >>>
        >>> # Create option decorator
        >>> opt_result = cli.create_option_decorator(
        ...     "--count", "-c", default=1, help="Number of greetings"
        ... )
        >>>
        >>> # Execute command with CliRunner
        >>> runner_result = cli.create_cli_runner()
        >>> if runner_result.is_success:
        >>>     runner = runner_result.unwrap()
        >>>     result = runner.invoke(my_command, ["--count", "3"])

    Note:
        ALL Click functionality MUST be accessed through this class.
        Direct Click imports are FORBIDDEN in ecosystem projects.

    """

    def __init__(self) -> None:
        """Initialize Click abstraction layer."""
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
    ) -> FlextResult[Callable[[Callable[..., object]], click.Command]]:
        """Create Click command decorator without exposing Click.

        Args:
            name: Command name (optional, uses function name if None)
            **kwargs: Click command options (help, context_settings, etc.)

        Returns:
            FlextResult containing command decorator function

        Example:
            >>> cli = FlextCliClick()
            >>> decorator_result = cli.create_command_decorator(
            ...     name="hello", help="Greet someone"
            ... )
            >>> if decorator_result.is_success:
            ...
            ...     @decorator_result.unwrap()
            ...     def hello():
            ...         click.echo("Hello!")

        """
        try:
            command_kwargs = {"name": name}
            command_kwargs.update(kwargs)
            decorator = click.command(**command_kwargs)
            self._logger.debug(
                "Created command decorator",
                extra={"command_name": name, "options": kwargs},
            )
            return FlextResult[Callable[[Callable[..., object]], click.Command]].ok(
                decorator
            )
        except Exception as e:
            error_msg = f"Failed to create command decorator: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Callable[[Callable[..., object]], click.Command]].fail(
                error_msg
            )

    def create_group_decorator(
        self,
        name: str | None = None,
        **kwargs: object,
    ) -> FlextResult[Callable[[Callable[..., object]], click.Group]]:
        """Create Click group decorator for command groups.

        Args:
            name: Group name (optional, uses function name if None)
            **kwargs: Click group options

        Returns:
            FlextResult containing group decorator function

        Example:
            >>> cli = FlextCliClick()
            >>> group_result = cli.create_group_decorator(name="db")
            >>> if group_result.is_success:
            ...
            ...     @group_result.unwrap()
            ...     def db():
            ...         '''Database commands'''
            ...         pass

        """
        try:
            group_kwargs = {"name": name}
            group_kwargs.update(kwargs)
            decorator = click.group(**group_kwargs)
            self._logger.debug(
                "Created group decorator",
                extra={"group_name": name, "options": kwargs},
            )
            return FlextResult[Callable[[Callable[..., object]], click.Group]].ok(
                decorator
            )
        except Exception as e:
            error_msg = f"Failed to create group decorator: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Callable[[Callable[..., object]], click.Group]].fail(
                error_msg
            )

    # =========================================================================
    # PARAMETER DECORATORS (OPTION, ARGUMENT)
    # =========================================================================

    def create_option_decorator(
        self,
        *param_decls: str,
        **attrs: object,
    ) -> FlextResult[Callable[[Callable[..., object]], click.Option]]:
        """Create Click option decorator.

        Args:
            *param_decls: Parameter declarations (e.g., "--count", "-c")
            **attrs: Option attributes (default, help, type, required, etc.)

        Returns:
            FlextResult containing option decorator

        Example:
            >>> cli = FlextCliClick()
            >>> opt_result = cli.create_option_decorator(
            ...     "--verbose", "-v", is_flag=True, help="Enable verbose output"
            ... )

        """
        try:
            decorator = click.option(*param_decls, **attrs)
            self._logger.debug(
                "Created option decorator",
                extra={"param_decls": param_decls, "attrs": attrs},
            )
            return FlextResult[Callable[[Callable[..., object]], click.Option]].ok(
                decorator
            )
        except Exception as e:
            error_msg = f"Failed to create option decorator: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Callable[[Callable[..., object]], click.Option]].fail(
                error_msg
            )

    def create_argument_decorator(
        self,
        *param_decls: str,
        **attrs: object,
    ) -> FlextResult[Callable[[Callable[..., object]], click.Argument]]:
        """Create Click argument decorator.

        Args:
            *param_decls: Parameter declarations (e.g., "filename")
            **attrs: Argument attributes (type, required, nargs, etc.)

        Returns:
            FlextResult containing argument decorator

        Example:
            >>> cli = FlextCliClick()
            >>> arg_result = cli.create_argument_decorator(
            ...     "filename", type=cli.get_path_type()
            ... )

        """
        try:
            decorator = click.argument(*param_decls, **attrs)
            self._logger.debug(
                "Created argument decorator",
                extra={"param_decls": param_decls, "attrs": attrs},
            )
            return FlextResult[Callable[[Callable[..., object]], click.Argument]].ok(
                decorator
            )
        except Exception as e:
            error_msg = f"Failed to create argument decorator: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Callable[[Callable[..., object]], click.Argument]].fail(
                error_msg
            )

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
            >>> cli = FlextCliClick()
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
            >>> cli = FlextCliClick()
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
            >>> cli = FlextCliClick()
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
            >>> cli = FlextCliClick()
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
            >>> cli = FlextCliClick()
            >>> bool_type = cli.get_bool_type()
            >>> # Use in option: type=bool_type

        """
        return bool

    def get_string_type(self) -> type[str]:
        """Get string parameter type.

        Returns:
            str type for Click parameters

        Example:
            >>> cli = FlextCliClick()
            >>> str_type = cli.get_string_type()

        """
        return str

    def get_int_type(self) -> type[int]:
        """Get integer parameter type.

        Returns:
            int type for Click parameters

        Example:
            >>> cli = FlextCliClick()
            >>> int_type = cli.get_int_type()

        """
        return int

    def get_float_type(self) -> type[float]:
        """Get float parameter type.

        Returns:
            float type for Click parameters

        Example:
            >>> cli = FlextCliClick()
            >>> float_type = cli.get_float_type()

        """
        return float

    # =========================================================================
    # CONTEXT MANAGEMENT
    # =========================================================================

    def get_current_context(self) -> FlextResult[ClickContext]:
        """Get current Click context.

        Returns:
            FlextResult containing current Click context

        Example:
            >>> cli = FlextCliClick()
            >>> ctx_result = cli.get_current_context()
            >>> if ctx_result.is_success:
            ...     ctx = ctx_result.unwrap()
            ...     print(ctx.command.name)

        """
        try:
            ctx = click.get_current_context(silent=True)
            if ctx is None:
                return FlextResult[ClickContext].fail("No Click context available")
            return FlextResult[ClickContext].ok(ctx)
        except Exception as e:
            error_msg = f"Failed to get Click context: {e}"
            self._logger.exception(error_msg)
            return FlextResult[ClickContext].fail(error_msg)

    def create_pass_context_decorator(
        self,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Create pass_context decorator.

        Returns:
            pass_context decorator

        Example:
            >>> cli = FlextCliClick()
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
        """Output message using Click.echo.

        Args:
            message: Message to output
            file: File to write to (default: stdout)
            nl: Add newline
            err: Write to stderr
            color: Force color on/off

        Returns:
            FlextResult[None]

        """
        try:
            click.echo(message=message, file=file, nl=nl, err=err, color=color)
            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Failed to echo message: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

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
        """Prompt for confirmation.

        Args:
            text: Prompt text
            default: Default value
            abort: Abort if not confirmed
            prompt_suffix: Suffix after prompt
            show_default: Show default in prompt
            err: Write to stderr

        Returns:
            FlextResult containing user's confirmation

        """
        try:
            result = click.confirm(
                text=text,
                default=default,
                abort=abort,
                prompt_suffix=prompt_suffix,
                show_default=show_default,
                err=err,
            )
            return FlextResult[bool].ok(result)
        except click.Abort:
            return FlextResult[bool].fail("User aborted")
        except Exception as e:
            error_msg = f"Confirmation failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult[bool].fail(error_msg)

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
        """Prompt for input.

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
            FlextResult containing user input

        """
        try:
            result = click.prompt(
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
        except click.Abort:
            return FlextResult[object].fail("User aborted")
        except Exception as e:
            error_msg = f"Prompt failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult[object].fail(error_msg)

    # =========================================================================
    # TESTING SUPPORT
    # =========================================================================

    def create_cli_runner(
        self,
        charset: str = "utf-8",
        env: FlextTypes.StringDict | None = None,
        *,
        echo_stdin: bool = False,
        _mix_stderr: bool = True,
    ) -> FlextResult[ClickCliRunner]:
        """Create Click CliRunner for testing.

        Args:
            charset: Character encoding
            env: Environment variables
            echo_stdin: Echo stdin to output
            _mix_stderr: Mix stderr into stdout (ignored in newer Click versions, reserved for future use)

        Returns:
            FlextResult containing CliRunner instance

        Example:
            >>> cli = FlextCliClick()
            >>> runner_result = cli.create_cli_runner()
            >>> if runner_result.is_success:
            ...     runner = runner_result.unwrap()
            ...     result = runner.invoke(my_cli, ["--help"])
            ...     assert result.exit_code == 0

        """
        try:
            # Note: mix_stderr parameter removed in Click 8+
            runner = ClickCliRunner(
                charset=charset,
                env=env,
                echo_stdin=echo_stdin,
            )
            self._logger.debug("Created CliRunner for testing")
            return FlextResult[ClickCliRunner].ok(runner)
        except Exception as e:
            error_msg = f"Failed to create CliRunner: {e}"
            self._logger.exception(error_msg)
            return FlextResult[ClickCliRunner].fail(error_msg)

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
            FlextResult[None]

        """
        try:
            click.clear()
            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Failed to clear screen: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def pause(self, info: str = "Press any key to continue...") -> FlextResult[None]:
        """Pause execution until key press.

        Args:
            info: Information message to display

        Returns:
            FlextResult[None]

        """
        try:
            click.pause(info=info)
            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Failed to pause: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    @override
    def execute(self) -> FlextResult[object]:
        """Execute Click abstraction layer operations.

        Returns:
            FlextResult[object]: Success with CLI status or failure with error

        """
        return FlextResult[object].ok({"service": "flext-cli", "status": "operational"})

    # Attribute declarations - override FlextService optional types
    # These are guaranteed initialized in __init__
    _logger: FlextLogger
    _container: FlextContainer


__all__ = [
    "FlextCliClick",
]
