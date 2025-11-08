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

import collections.abc
import contextlib
import functools
import pathlib
import re
import shutil
import sys
import typing
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import IO

import click
import typer
from flext_core import FlextContainer, FlextLogger, FlextResult, FlextTypes
from pydantic import ValidationError
from pydantic_core import PydanticUndefined
from typer.testing import CliRunner

from flext_cli.constants import FlextCliConstants


class FlextCliCli:
    """Complete CLI framework abstraction layer.

    This class provides a unified CLI interface using Typer as the backend framework.
    Since Typer is built on Click, it generates Click-compatible commands internally,
    ensuring full backward compatibility while enabling modern type-driven development.

    Provides direct APIs for:

    - Command and group creation (Typer-based, Click-compatible)
    - Decorators (option, argument, command)
    - Parameter types (Choice, Path, File, IntRange, etc.)
    - typer.Context management
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
        # Direct initialization - no @property wrapper
        self.container = FlextContainer()
        self.logger = FlextLogger(__name__)

    # =========================================================================
    # COMMAND AND GROUP CREATION
    # =========================================================================

    def create_command_decorator(
        self,
        name: str | None = None,
        help_text: str | None = None,
    ) -> typing.Callable[[typing.Callable[..., typing.Any]], click.Command]:
        """Create Click command decorator.

        Args:
            name: Command name (optional, uses function name if None)
            help_text: Help text for command

        Returns:
            Command decorator function

        Note:
            For advanced Click command options (context_settings, etc),
            import Click directly in cli.py only.

        Example:
            >>> cli = FlextCliCli()
            >>> decorator = cli.create_command_decorator(
            ...     name="hello", help_text="Greet someone"
            ... )
            >>> @decorator
            ... def hello():
            ...     typer.echo("Hello!")

        """
        # Use Click directly (cli.py is ONLY file that may import Click)
        decorator = click.command(name=name, help=help_text)
        self.logger.debug(
            "Created command decorator",
            extra={"command_name": name, "help": help_text},
        )
        return decorator

    def create_group_decorator(
        self,
        name: str | None = None,
        help_text: str | None = None,
    ) -> typing.Callable[[typing.Callable[..., typing.Any]], click.Group]:
        """Create Click group decorator for command groups.

        Args:
            name: Group name (optional, uses function name if None)
            help_text: Help text for group

        Returns:
            Group decorator function

        Note:
            For advanced Click group options, import Click directly in cli.py only.

        Example:
            >>> cli = FlextCliCli()
            >>> group = cli.create_group_decorator(
            ...     name="db", help_text="Database commands"
            ... )
            >>> @group
            ... def db():
            ...     pass

        """
        # Use Click directly (cli.py is ONLY file that may import Click)
        decorator = click.group(name=name, help=help_text)
        self.logger.debug(
            "Created group decorator",
            extra={"group_name": name, "help": help_text},
        )
        return decorator

    # =========================================================================
    # PARAMETER DECORATORS (OPTION, ARGUMENT)
    # =========================================================================

    def create_option_decorator(
        self,
        *param_decls: str,
        default: FlextTypes.JsonValue | None = None,
        type_hint: click.ParamType | type | None = None,
        required: bool = False,
        help_text: str | None = None,
        is_flag: bool = False,
        flag_value: FlextTypes.JsonValue | None = None,
        multiple: bool = False,
        count: bool = False,
        show_default: bool = False,
    ) -> Callable[
        [Callable[..., FlextTypes.JsonValue]],
        Callable[..., FlextTypes.JsonValue],
    ]:
        """Create Click option decorator with explicit parameters.

        Args:
            *param_decls: Parameter declarations (e.g., "--count", "-c")
            default: Default value
            type_hint: Parameter type (Click type or Python type)
            required: Whether option is required
            help_text: Help text for option
            is_flag: Whether this is a boolean flag
            flag_value: Value when flag is set
            multiple: Allow multiple values
            count: Count occurrences
            show_default: Show default in help

        Returns:
            Option decorator

        Note:
            For advanced Click options, import Click directly in cli.py only.

        Example:
            >>> cli = FlextCliCli()
            >>> option = cli.create_option_decorator(
            ...     "--verbose", "-v", is_flag=True, help_text="Enable verbose output"
            ... )

        """
        # Use Click directly (cli.py is ONLY file that may import Click)
        decorator = click.option(
            *param_decls,
            default=default,
            type=type_hint,
            required=required,
            help=help_text,
            is_flag=is_flag,
            flag_value=flag_value,
            multiple=multiple,
            count=count,
            show_default=show_default,
        )
        self.logger.debug(
            "Created option decorator",
            extra={"param_decls": param_decls, "required": required},
        )
        return decorator

    def create_argument_decorator(
        self,
        *param_decls: str,
        type_hint: click.ParamType | type | None = None,
        required: bool = True,
        nargs: int = 1,
    ) -> typing.Callable[
        [typing.Callable[..., typing.Any]], typing.Callable[..., typing.Any]
    ]:
        """Create Click argument decorator with explicit parameters.

        Args:
            *param_decls: Parameter declarations (e.g., "filename")
            type_hint: Parameter type (Click type or Python type)
            required: Whether argument is required
            nargs: Number of arguments (1, -1 for unlimited)

        Returns:
            Argument decorator

        Note:
            For advanced Click arguments, import Click directly in cli.py only.

        Example:
            >>> cli = FlextCliCli()
            >>> argument = cli.create_argument_decorator(
            ...     "filename", type_hint=cli.get_path_type()
            ... )

        """
        # Use Click directly (cli.py is ONLY file that may import Click)
        decorator = click.argument(
            *param_decls,
            type=type_hint,
            required=required,
            nargs=nargs,
        )
        self.logger.debug(
            "Created argument decorator",
            extra={"param_decls": param_decls, "required": required},
        )
        return decorator

    # =========================================================================
    # PARAMETER TYPES
    # =========================================================================

    def get_choice_type(
        self, choices: Sequence[str], *, case_sensitive: bool = True
    ) -> click.Choice[str]:
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
        mode: str = FlextCliConstants.FileDefaults.DEFAULT_FILE_MODE,
        encoding: str | None = None,
        errors: str | None = FlextCliConstants.FileDefaults.DEFAULT_ERROR_HANDLING,
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
            formats = FlextCliConstants.FileDefaults.DEFAULT_DATETIME_FORMATS
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
        types: Sequence[type[FlextTypes.JsonValue] | click.ParamType],
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
    ) -> typing.Callable[
        [typing.Callable[..., typing.Any]], typing.Callable[..., typing.Any]
    ]:
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
        prompt_suffix: str = FlextCliConstants.UIDefaults.DEFAULT_PROMPT_SUFFIX,
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
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.USER_ABORTED_CONFIRMATION.format(
                    error=e
                )
            )

    def prompt(
        self,
        text: str,
        default: FlextTypes.JsonValue | None = None,
        type_hint: FlextTypes.JsonValue | None = None,
        value_proc: Callable[[str], FlextTypes.JsonValue] | None = None,
        prompt_suffix: str = FlextCliConstants.UIDefaults.DEFAULT_PROMPT_SUFFIX,
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
            return FlextResult[object].fail(
                FlextCliConstants.ErrorMessages.USER_ABORTED_PROMPT.format(error=e)
            )

    # =========================================================================
    # TESTING SUPPORT
    # =========================================================================

    def create_cli_runner(
        self,
        charset: str = FlextCliConstants.Encoding.UTF8,
        env: dict[str, str] | None = None,
        *,
        echo_stdin: bool = False,
    ) -> FlextResult[CliRunner]:
        """Create Click CliRunner for testing.

        Args:
            charset: Character encoding
            env: Environment variables
            echo_stdin: Echo stdin to output

        Returns:
            FlextResult[CliRunner]: Success with CliRunner instance or failure

        Example:
            >>> cli = FlextCliCli()
            >>> result = cli.create_cli_runner()
            >>> assert result.is_success
            >>> runner = result.unwrap()
            >>> test_result = runner.invoke(my_cli, ["--help"])
            >>> assert test_result.exit_code == 0

        """
        runner = CliRunner(
            charset=charset,
            env=env,
            echo_stdin=echo_stdin,
        )
        self.logger.debug("Created CliRunner for testing")
        return FlextResult[CliRunner].ok(runner)

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
        size = shutil.get_terminal_size()
        return (size.columns, size.lines)

    def clear_screen(self) -> FlextResult[None]:
        """Clear terminal screen.

        Returns:
            FlextResult[None]: Success or failure of clear operation

        """
        click.clear()
        return FlextResult[None].ok(None)

    def pause(
        self, info: str = FlextCliConstants.UIDefaults.DEFAULT_PAUSE_MESSAGE
    ) -> FlextResult[None]:
        """Pause execution until key press.

        Args:
            info: Information message to display

        Returns:
            FlextResult[None]: Success or failure of pause operation

        """
        click.pause(info=info)
        return FlextResult[None].ok(None)

    def model_command(
        self,
        model_class: type,
        handler: typing.Callable[..., typing.Any],
        config: typing.Any | None = None,
    ) -> Callable[..., None]:
        """Create Typer command from Pydantic model with automatic config integration.

        Generic model-driven CLI automation using Field metadata introspection.
        Delegates to existing Typer infrastructure for type conversion.

        Handles optional parameters: Fields with defaults become optional CLI args
        that don't require specification on command line.

        Supports Pydantic v2 Field aliases: Field(alias="input-dir") generates
        --input-dir CLI option (not --input_dir).

        **AUTOMATIC CONFIG INTEGRATION** (NEW):
        If config singleton is provided, FlextCli automatically:
        1. Reads config field values as defaults for CLI parameters (when no CLI value provided)
        2. Updates config with CLI values using Pydantic v2's __dict__ (bypasses validators)
        3. Passes fully-populated params model to handler (no fallback logic needed)

        This enables full configuration hierarchy - completely automatic:
        - Constants (in config defaults)
        - .env file (config reads via env_prefix)
        - Environment variables (config reads via Pydantic Settings)
        - CLI Arguments (override config if different, stored via __dict__ to bypass validation)

        No custom code needed in application - framework handles it all!

        Args:
            model_class: Pydantic BaseModel subclass defining parameters
            handler: Function receiving validated model instance
            config: Optional config singleton (Pydantic Settings with env_prefix)
                   - Provides defaults for CLI parameters
                   - Gets updated with CLI values when they differ

        Returns:
            Typer command function with auto-generated parameters

        Example:
            ```python
            from pydantic import BaseModel, Field
            from pydantic_settings import BaseSettings, SettingsConfigDict

            cli = FlextCliCli()


            class MyConfig(BaseSettings):
                model_config = SettingsConfigDict(
                    env_prefix="MY_APP_",
                )
                input_dir: str = Field(default="data/input")
                count: int = Field(default=10)


            class MyParams(BaseModel):
                input_dir: str = Field(alias="input-dir", description="Input path")
                count: int = Field(default=10, description="Item count")
                sync: bool = Field(default=True, description="Enable sync")


            def handle(params: MyParams):
                # params is fully populated: CLI args OR config defaults
                # No fallback logic needed!
                print(f"Processing {params.input_dir}, count={params.count}")


            # Fully automatic - pass config reference
            config = MyConfig()  # Reads from MY_APP_INPUT_DIR, MY_APP_COUNT env vars
            command = cli.model_command(MyParams, handle, config=config)

            # CLI usage - ALL automatic:
            # my-command
            #   → Uses defaults: input_dir from config (from env or default)
            #   → Calls: handle(MyParams(input_dir=config.input_dir, count=10, sync=True))
            #   → Updates: config.input_dir if CLI value different
            #
            # my-command --input-dir /path
            #   → Overrides: input_dir from config with /path
            #   → Calls: handle(MyParams(input_dir=/path, count=10, sync=True))
            #   → Updates: config.input_dir = /path (different from original)
            #
            # my-command --input-dir /path --count 5
            #   → Overrides: input_dir and count
            #   → Calls: handle(MyParams(input_dir=/path, count=5, sync=True))
            #   → Updates: config with both values
            ```

        """
        # Auto-generate function with proper signature from model fields
        if not hasattr(model_class, "model_fields"):
            msg = f"{model_class.__name__} must be a Pydantic BaseModel"
            raise TypeError(msg)

        # Build parameter definitions and mapping
        params_def: list[str] = []
        params_call: list[str] = []
        field_mapping: dict[str, str] = {}  # param_name -> field_name

        def _format_type_annotation(field_type: type) -> str:
            """Format type annotation for dynamic function signature.

            Handles Pydantic v2 Annotated types by stripping metadata (PlainSerializer, etc.)
            and returning just the base type, which is sufficient for CLI function signatures.
            The actual validation and serialization is handled by Pydantic model instantiation.
            """
            # Get origin to check for Annotated
            origin = typing.get_origin(field_type)

            # Handle Annotated types - extract base type without metadata
            if origin is typing.Annotated:
                # Annotated[BaseType, metadata1, metadata2, ...]
                # We only need BaseType for the function signature
                args = typing.get_args(field_type)
                if args:
                    base_type = args[0]
                    # Recursively format the base type (might be Optional, etc.)
                    return _format_type_annotation(base_type)

            # Handle Literal types - convert to str for CLI signature
            # The actual validation is done by Pydantic model instantiation
            # Literal types with string values can't be properly evaluated in stringified annotations
            if origin is typing.Literal:
                return "str"

            # Handle Optional (Union[T, None])
            if origin is typing.Union:
                args = typing.get_args(field_type)
                # Check if this is Optional (Union with None)
                if type(None) in args:
                    # Filter out None to get the actual type
                    non_none_types = [t for t in args if t is not type(None)]
                    if len(non_none_types) == 1:
                        # This is Optional[T]
                        inner_type = non_none_types[0]
                        inner_str = _format_type_annotation(inner_type)
                        return f"Optional[{inner_str}]"
                    # Union with multiple non-None types
                    type_strs = [_format_type_annotation(t) for t in non_none_types]
                    return f"Union[{', '.join(type_strs)}]"

            # Handle List, Dict, etc.
            if origin is not None:
                # Generic type with origin (List, Dict, etc.)
                args = typing.get_args(field_type)
                origin_name = getattr(origin, "__name__", str(origin)).replace(
                    "typing.", ""
                )
                if args:
                    arg_strs = [_format_type_annotation(arg) for arg in args]
                    return f"{origin_name}[{', '.join(arg_strs)}]"
                return origin_name

            # Handle simple types
            if hasattr(field_type, "__name__"):
                return field_type.__name__

            # Fallback - clean up string representation
            # Remove problematic prefixes and syntax that can't be evaluated
            type_str = str(field_type)
            # Remove typing module prefix
            type_str = type_str.replace("typing.", "")
            # Remove types module prefix (for UnionType, etc.)
            type_str = type_str.replace("types.", "")
            # If we get a complex stringified type, just use 'str' as a safe fallback
            # This handles edge cases like <function PlainSerializer at 0x...>
            if "<" in type_str and ">" in type_str:
                return "str"
            return type_str

        def _get_config_value(field_name: str) -> typing.Any | None:
            """Get field value from config singleton if available."""
            if config is None:
                return None
            # Check if config has the field
            if not hasattr(config, field_name):
                return None
            # Get the field value
            try:
                return getattr(config, field_name)
            except (AttributeError, Exception):
                return None

        for field_name, field_info in model_class.model_fields.items():
            field_type = field_info.annotation
            has_default = field_info.default is not PydanticUndefined
            description = field_info.description or f"{field_name} parameter"

            # CRITICAL: Use Pydantic Field alias if present, else use field_name
            # This ensures CLI parameter matches Field(alias="...") definition
            cli_param_name = field_info.alias or field_name
            safe_param_name = cli_param_name.replace("-", "_")

            # Track mapping from CLI parameter to model field
            field_mapping[safe_param_name] = field_name
            params_call.append(f'"{field_name}": {safe_param_name}')

            # Format type annotation string
            type_str = _format_type_annotation(field_type)

            # ENHANCED: Get default value from field or config
            # Priority: field default (if not None) > config value > None
            cli_default = field_info.default
            # Check for both PydanticUndefined AND None (None means no real default, just optional)
            if cli_default is PydanticUndefined or cli_default is None:
                # No field default or default is None, try config
                config_value = _get_config_value(field_name)
                if config_value is not None:
                    cli_default = config_value
                    has_default = True
                # If no config value either, keep None as the default for optional fields
                elif cli_default is None:
                    has_default = (
                        True  # Still mark as having default (None is the default)
                    )

            # Generate parameter with Typer Option using alias for CLI flag
            if has_default and cli_default is not PydanticUndefined:
                default_value = repr(cli_default)
                if field_type is bool:
                    # Boolean flags need --flag/--no-flag format
                    flag_name = f"--{cli_param_name}"
                    no_flag_name = f"--no-{cli_param_name}"
                    params_def.append(
                        f"{safe_param_name}: {type_str} = typer.Option({default_value}, '{flag_name}', '{no_flag_name}', help={description!r})"
                    )
                else:
                    # Optional parameter with default - truly optional in CLI
                    cli_option_name = f"--{cli_param_name}"
                    params_def.append(
                        f"{safe_param_name}: {type_str} = typer.Option({default_value}, '{cli_option_name}', help={description!r})"
                    )
            else:
                # Required parameter - must be specified in CLI
                cli_option_name = f"--{cli_param_name}"
                params_def.append(
                    f"{safe_param_name}: {type_str} = typer.Option(..., '{cli_option_name}', help={description!r})"
                )

        # Create function dynamically with proper signature for Typer introspection
        # This is required because Typer needs to inspect function parameters
        params_signature = ", ".join(params_def)
        kwargs_dict = "{" + ", ".join(params_call) + "}"

        # Build function code with proper signature
        # Config defaults are read when building CLI parameters above
        func_code = f"""
def generated_command({params_signature}) -> None:
    '''Auto-generated command from {model_class.__name__} model.'''
    try:
        # Build kwargs dict mapping field names to values
        kwargs = {kwargs_dict}
        # Validate and instantiate model (fully populated from CLI args OR config defaults)
        params = model_class(**kwargs)
    except ValidationError as e:
        typer.echo(f"Invalid parameters: {{e}}", err=True)
        raise typer.Exit(code=1) from e
    try:
        handler(params)
    except Exception as e:
        typer.echo(f"Command failed: {{e}}", err=True)
        raise typer.Exit(code=1) from e
"""

        # Clean up generated code - remove any UnionType references that can't be evaluated
        # This can happen with Python 3.10+ union syntax (str | None)
        if "UnionType" in func_code:
            # Replace UnionType[X, NoneType] with Optional[X] for proper evaluation
            # The regex captures the first type argument before any comma, excluding NoneType
            func_code = re.sub(
                r"UnionType\[([^,\]]+)(?:, NoneType)?\]",
                r"Optional[\1]",
                func_code,
            )

        # Execute function creation in controlled namespace
        # Using exec is required here for dynamic function signature creation
        # which is necessary for Typer to introspect CLI parameters
        namespace: dict[str, typing.Any] = {
            "typer": typer,
            "ValidationError": ValidationError,
            "model_class": model_class,
            "handler": handler,
            "config": config,
            # Include typing module components for type annotation resolution
            # These are essential for evaluating stringified type annotations
            "ForwardRef": typing.ForwardRef,
            "Union": typing.Union,
            "Optional": typing.Optional,
            "Annotated": typing.Annotated,
            "Literal": typing.Literal,
            "List": list,
            "Dict": dict,
            "Tuple": tuple,
            "Set": set,
            "Callable": collections.abc.Callable,
            "Iterable": collections.abc.Iterable,
            "get_args": typing.get_args,
            "get_origin": typing.get_origin,
            # Include NoneType for type annotations
            "NoneType": type(None),
            # Note: We intentionally exclude UnionType from the namespace because:
            # - Type annotations using | syntax (str | None) are parsed internally
            # - The typing.Union and Optional from above handle all necessary union cases
            # - Providing UnionType leads to "not subscriptable" errors when eval'd
            # Include pathlib for Typer annotation evaluation (Python 3.13+)
            # Typer uses inspect.signature(eval_str=True) which needs pathlib in globals
            "pathlib": pathlib,
            "Path": pathlib.Path,
            # Include builtins for basic types (str, int, bool, etc.)
            "__builtins__": __builtins__,
        }
        # Add model_class's module globals so type annotations can resolve
        # This allows field types from the model's module to be available
        if hasattr(model_class, "__module__"):
            model_module = sys.modules.get(model_class.__module__)
            if model_module and hasattr(model_module, "__dict__"):
                namespace.update(model_module.__dict__)

        exec(func_code, namespace)

        # Type assertion: we know generated_command is Callable[..., None]
        generated_command_func: Callable[..., None] = typing.cast(
            "Callable[..., None]", namespace["generated_command"]
        )

        # Update generated function's __globals__ to include typing constructs and pathlib
        # This ensures Typer can later introspect the function with eval_str=True
        # pathlib is needed for Python 3.13+ when Typer evaluates Path annotations
        if hasattr(generated_command_func, "__globals__"):
            generated_command_func.__globals__.update({
                "Literal": typing.Literal,
                "pathlib": pathlib,
                "Path": pathlib.Path,
            })

        # If config provided, wrap function to update config with CLI values
        if config is not None:
            # Use functools.wraps to properly copy metadata for Typer
            @functools.wraps(generated_command_func)
            def wrapped_command(**kwargs: dict[str, typing.Any]) -> None:
                """Wrapper that updates config singleton with CLI values.

                Uses Pydantic v2's __dict__ directly to bypass validation,
                allowing CLI values to override config values even if invalid.
                This ensures configuration hierarchy: Constants → .env → env vars → CLI args
                """
                # Update config with CLI parameter values by directly modifying __dict__
                # This bypasses Pydantic v2 validators and read-only properties
                for field_name, cli_value in kwargs.items():
                    if cli_value is not None:
                        # Use __dict__ directly to bypass validation
                        # Config update is advisory - continue silently if it fails
                        with contextlib.suppress(Exception):
                            config.__dict__[field_name] = cli_value

                # Call the original generated command
                generated_command_func(**kwargs)

            # Also update wrapper's __globals__ if possible
            # pathlib is needed for Python 3.13+ when Typer evaluates Path annotations
            if hasattr(wrapped_command, "__globals__"):
                wrapped_command.__globals__.update({
                    "Literal": typing.Literal,
                    "pathlib": pathlib,
                    "Path": pathlib.Path,
                })

            return wrapped_command

        return generated_command_func

    def execute(self) -> FlextResult[object]:
        """Execute Click abstraction layer operations.

        Returns:
            FlextResult[object]: Success with CLI status or failure with error

        """
        return FlextResult[object].ok({
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
        })


__all__ = [
    "FlextCliCli",
]
