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

import logging
import shutil
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import IO, Annotated, Literal, overload

import click
import typer
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextRuntime,
)
from pydantic import BaseModel
from typer.testing import CliRunner

from flext_cli.cli_params import FlextCliCommonParams
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_cli.protocols import FlextCliProtocols
from flext_cli.typings import CliJsonValue

# Type alias for command functions to avoid Callable[..., T]
CliCommandFunc = FlextCliProtocols.Cli.CliCommandFunction
# Type alias for model-based command handlers (used by model_command)
ModelCommandFunc = FlextCliProtocols.Cli.ModelCommandHandler


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

    @overload
    def _create_cli_decorator(
        self,
        entity_type: Literal["command"],
        name: str | None,
        help_text: str | None,
    ) -> Callable[[CliCommandFunc], click.Command]: ...

    @overload
    def _create_cli_decorator(
        self,
        entity_type: Literal["group"],
        name: str | None,
        help_text: str | None,
    ) -> Callable[[CliCommandFunc], click.Group]: ...

    def _create_cli_decorator(
        self,
        entity_type: FlextCliConstants.EntityTypeLiteral,
        name: str | None,
        help_text: str | None,
    ) -> Callable[[CliCommandFunc], click.Command | click.Group]:
        """Create Click decorator (command or group) - DRY helper.

        Args:
            entity_type: Type of decorator to create
            name: Entity name (optional, uses function name if None)
            help_text: Help text

        Returns:
            Decorator function

        """
        # Use Click directly (cli.py is ONLY file that may import Click)
        if entity_type == "command":
            decorator = click.command(name=name, help=help_text)
            log_msg = "Created command decorator"
            extra_key = "command_name"
        else:  # group
            decorator = click.group(name=name, help=help_text)
            log_msg = "Created group decorator"
            extra_key = "group_name"

        self.logger.debug(log_msg, extra={extra_key: name, "help": help_text})
        return decorator

    def create_command_decorator(
        self,
        name: str | None = None,
        help_text: str | None = None,
    ) -> Callable[[CliCommandFunc], click.Command]:
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
        return self._create_cli_decorator("command", name, help_text)

    def create_app_with_common_params(
        self,
        name: str,
        help_text: str,
        config: object | None = None,
        *,
        add_completion: bool = True,
    ) -> typer.Typer:
        """Create Typer app with automatic global common params (--debug, --log-level, --trace).

        This method creates a Typer app and automatically registers a global callback
        with FlextCliCommonParams (--debug, --trace, --verbose, --quiet, --log-level).
        These params are available at the app level (before subcommands) and will
        reconfigure the logger automatically when provided.

        Args:
            name: Application name
            help_text: Application help text
            config: Optional FlextConfig instance for logger reconfiguration
            add_completion: Whether to add shell completion support

        Returns:
            Configured Typer app with global common params

        Example:
            >>> cli = FlextCliCli()
            >>> app = cli.create_app_with_common_params(
            ...     name="my-app", help_text="My application", config=my_config
            ... )
            >>> # Now app has --debug, --log-level, etc. at global level
            >>> # Usage: my-app --debug subcommand

        """
        # Create Typer app
        app = typer.Typer(
            name=name,
            help=help_text,
            add_completion=add_completion,
        )

        # Define global callback with common params
        @app.callback()
        def global_callback(
            *,
            debug: Annotated[
                bool,
                typer.Option(
                    "--debug/--no-debug",
                    help="Enable debug mode",
                ),
            ] = False,
            trace: Annotated[
                bool,
                typer.Option(
                    "--trace/--no-trace",
                    help="Enable trace mode",
                ),
            ] = False,
            verbose: Annotated[
                bool,
                typer.Option(
                    "--verbose/--no-verbose",
                    help="Enable verbose mode",
                ),
            ] = False,
            quiet: Annotated[
                bool,
                typer.Option(
                    "--quiet/--no-quiet",
                    help="Enable quiet mode",
                ),
            ] = False,
            log_level: Annotated[
                str | None,
                typer.Option(
                    "--log-level",
                    "-L",
                    help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
                    case_sensitive=False,
                ),
            ] = None,
        ) -> None:
            """Global options available for all commands."""
            # Extract common params
            common_params = {
                "debug": debug,
                "trace": trace,
                "verbose": verbose,
                "quiet": quiet,
                "log_level": log_level,
            }

            # Filter out None values and False booleans
            active_params = {
                k: v
                for k, v in common_params.items()
                if v is not None and v is not False
            }

            if not active_params or not config:
                return

            # ✅ FILTER: Only apply params that exist in config
            # Config may not have all common params (e.g., quiet)
            # Type narrowing: check if config has model_fields (Pydantic BaseModel)

            config_fields: set[str] = set()
            if isinstance(config, BaseModel):
                config_fields = set(type(config).model_fields.keys())
            filtered_params = {
                k: v for k, v in active_params.items() if k in config_fields
            }

            if not filtered_params:
                return

            # Apply to config and reconfigure logger
            # Type guard: config is FlextCliConfig if we reached this point
            if not isinstance(config, FlextCliConfig):
                return

            # Unpack filtered_params as keyword arguments
            # Type safety: filtered_params contains only valid config field names
            # Use type guards for safe conversion instead of cast
            def get_bool_value(key: str) -> bool | None:
                value = filtered_params.get(key)
                return value if isinstance(value, bool) else None

            def get_str_value(key: str) -> str | None:
                value = filtered_params.get(key)
                return value if isinstance(value, str) else None

            result = FlextCliCommonParams.apply_to_config(
                config,
                verbose=get_bool_value("verbose"),
                quiet=get_bool_value("quiet"),
                debug=get_bool_value("debug"),
                trace=get_bool_value("trace"),
                log_level=get_str_value("log_level"),
            )

            if result.is_failure:
                FlextLogger.get_logger().warning(
                    f"Failed to apply CLI params: {result.error}",
                )
                return

            # ✅ RECONFIGURE: Logger with new config values
            # Use reconfigure_structlog() to bypass guards and force CLI override
            # Convert LogLevel enum (string) to logging int constant
            if config.debug or config.trace:
                log_level_value = logging.DEBUG  # 10
            else:
                # Convert LogLevel enum string to logging int
                log_level_name = config.cli_log_level.value  # "INFO", "DEBUG", etc.
                log_level_value = getattr(logging, log_level_name, logging.INFO)

            # Force reconfiguration (bypasses is_configured() guards)
            FlextRuntime.reconfigure_structlog(
                log_level=log_level_value,
                console_renderer=config.console_enabled,
            )

        self.logger.debug(
            "Created Typer app with global common params",
            extra={"app_name": name, "has_config": config is not None},
        )

        return app

    def create_group_decorator(
        self,
        name: str | None = None,
        help_text: str | None = None,
    ) -> Callable[[CliCommandFunc], click.Group]:
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
        # Type checker resolves overload based on Literal["group"] parameter
        return self._create_cli_decorator("group", name, help_text)

    # =========================================================================
    # PARAMETER DECORATORS (OPTION, ARGUMENT)
    # =========================================================================

    def create_option_decorator(
        self,
        *param_decls: str,
        default: CliJsonValue | None = None,
        type_hint: click.ParamType | type | None = None,
        required: bool = False,
        help_text: str | None = None,
        is_flag: bool = False,
        flag_value: CliJsonValue | None = None,
        multiple: bool = False,
        count: bool = False,
        show_default: bool = False,
    ) -> Callable[[CliCommandFunc], CliCommandFunc]:
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
    ) -> Callable[[CliCommandFunc], CliCommandFunc]:
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
            >>> import click
            >>> cli = FlextCliCli()
            >>> argument = cli.create_argument_decorator(
            ...     "filename", type_hint=click.Path(exists=True)
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
        types: Sequence[type[CliJsonValue] | click.ParamType],
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
    ) -> object:
        """Create pass_context decorator.

        Returns:
            pass_context decorator (click.pass_context)

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
    ) -> FlextResult[bool]:
        """Output message using Typer.echo (Typer backend).

        Args:
            message: Message to output
            file: File to write to (default: stdout)
            nl: Add newline
            err: Write to stderr
            color: Force color on/off

        Returns:
            FlextResult[bool]: True if echo succeeded, failure on error

        """
        typer.echo(message=message, file=file, nl=nl, err=err, color=color)
        return FlextResult[bool].ok(True)

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
                    error=e,
                ),
            )

    def prompt(
        self,
        text: str,
        default: CliJsonValue | None = None,
        type_hint: CliJsonValue | None = None,
        value_proc: Callable[[str], CliJsonValue] | None = None,
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
                FlextCliConstants.ErrorMessages.USER_ABORTED_PROMPT.format(error=e),
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

    def clear_screen(self) -> FlextResult[bool]:
        """Clear terminal screen.

        Returns:
            FlextResult[bool]: True if screen cleared successfully, failure on error

        """
        click.clear()
        return FlextResult[bool].ok(True)

    def pause(
        self,
        info: str = FlextCliConstants.UIDefaults.DEFAULT_PAUSE_MESSAGE,
    ) -> FlextResult[bool]:
        """Pause execution until key press.

        Args:
            info: Information message to display

        Returns:
            FlextResult[bool]: True if pause succeeded, failure on error

        """
        click.pause(info=info)
        return FlextResult[bool].ok(True)

    def model_command(
        self,
        model_class: type[BaseModel],
        handler: Callable[..., None],
        config: FlextCliConfig | None = None,
    ) -> CliCommandFunc:
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
        # Delegate to FlextCliModels.ModelCommandBuilder for reduced complexity (SOLID/SRP)
        if not hasattr(model_class, "model_fields"):
            msg = f"{model_class.__name__} must be a Pydantic model (BaseModel or FlextModels subclass)"
            raise TypeError(msg)

        builder = FlextCliModels.ModelCommandBuilder(model_class, handler, config)
        return builder.build()

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
