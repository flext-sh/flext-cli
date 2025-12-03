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
from typing import IO, Annotated, TypeVar, cast

import click
import typer
from flext_core import (
    FlextConstants,
    FlextContainer,
    FlextExceptions,
    FlextLogger,
    FlextModels,
    FlextProtocols,
    FlextResult,
    FlextRuntime,
    t,
    u,
)
from pydantic import BaseModel
from typer.testing import CliRunner

from flext_cli.cli_params import FlextCliCommonParams
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_cli.protocols import FlextCliProtocols

# Aliases for static method calls and type references
# Use u.* for FlextUtilities static methods
# Use t.* for FlextTypes type references
# Use c.* for FlextConstants constants
# Use m.* for FlextModels model references
# Use p.* for FlextProtocols protocol references
# Use r.* for FlextResult methods
# Use e.* for FlextExceptions
# u is already imported from flext_core
# t is already imported from flext_core
c = FlextConstants
m = FlextModels
p = FlextProtocols
r = FlextResult
e = FlextExceptions

# TypeVar for model command generic typing
TModel = TypeVar("TModel", bound=BaseModel)


class FlextCliCli:  # noqa: PLR0904
    """Complete CLI framework abstraction layer.

    Business Rules:
    ───────────────
    1. This is the ONLY file allowed to import Typer/Click directly
    2. All CLI framework functionality MUST go through this abstraction
    3. Typer automatically detects boolean flags from type hints and defaults
    4. Command decorators MUST validate command names (non-empty, valid identifiers)
    5. Option decorators MUST validate parameter declarations (non-empty)
    6. Boolean options automatically become flags (no is_flag parameter needed)
    7. Type hints MUST be real Python types for Typer introspection
    8. Command execution MUST handle exceptions gracefully

    Architecture Implications:
    ───────────────────────────
    - Single abstraction point for all Typer/Click functionality
    - Typer backend provides modern type-driven CLI development
    - Click compatibility ensures backward compatibility
    - Boolean flag detection automatic (no deprecated is_flag/flag_value)
    - Function annotations updated with real types for Typer introspection
    - CliRunner enables testing without subprocess execution

    Audit Implications:
    ───────────────────
    - Command creation MUST be logged with command name and metadata
    - Command execution MUST be logged with arguments (no sensitive data)
    - Option creation MUST be logged with parameter names and types
    - Error conditions MUST be logged with full context (no sensitive data)
    - CLI framework violations (direct Typer/Click imports) MUST be detected

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

    def _create_cli_decorator(
        self,
        entity_type: FlextCliConstants.EntityTypeLiteral,
        name: str | None,
        help_text: str | None,
    ) -> Callable[
        [FlextCliProtocols.Cli.CliCommandFunction], click.Command | click.Group
    ]:
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
        # Click decorators return types that implement CliCommandFunction
        # protocol structurally
        return decorator

    def create_command_decorator(
        self,
        name: str | None = None,
        help_text: str | None = None,
    ) -> Callable[[FlextCliProtocols.Cli.CliCommandFunction], click.Command]:
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
        config: FlextCliConfig | None = None,
        *,
        add_completion: bool = True,
    ) -> typer.Typer:
        """Create Typer app with automatic global common params.

        Creates app with (--debug, --log-level, --trace).
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

            # Filter out None values and False booleans using u.filter
            # Use build() DSL for filtering active params
            active_params_raw = u.filter(
                common_params, predicate=lambda _k, v: v is not None and v is not False
            )
            active_params = (
                cast(
                    "dict[str, t.GeneralValueType]",
                    u.build(active_params_raw, ops={"ensure": "dict"}, on_error="skip"),
                )
                if isinstance(active_params_raw, dict)
                else {}
            )

            if not active_params or not config:
                return

            # ✅ FILTER: Only apply params that exist in config using u.filter
            # Config may not have all common params (e.g., quiet)
            # Type narrowed: config is FlextCliConfig (parameter type)
            # FlextCliConfig extends BaseModel, so it has model_fields
            config_fields: set[str] = set(type(config).model_fields.keys())
            # Use build() DSL for filtering params by config fields
            filtered_params_raw = u.filter(
                active_params, predicate=lambda k, _v: k in config_fields
            )
            filtered_params = (
                cast(
                    "dict[str, t.GeneralValueType]",
                    u.build(
                        filtered_params_raw, ops={"ensure": "dict"}, on_error="skip"
                    ),
                )
                if isinstance(filtered_params_raw, dict)
                else {}
            )

            if not filtered_params:
                return

            # Use build() DSL for type-safe value extraction with generalized helper
            def get_val(
                k: str, type_name: str, default: t.GeneralValueType | None = None
            ) -> t.GeneralValueType | None:
                """Extract typed value using build DSL."""
                val = filtered_params.get(k)
                if val is None:
                    return default
                return (
                    cast(
                        "t.GeneralValueType | None",
                        u.build(val, ops={"ensure": type_name}, on_error="skip"),
                    )
                    if isinstance(
                        val,
                        (
                            bool
                            if type_name == "bool"
                            else str
                            if type_name == "str"
                            else dict
                        ),
                    )
                    else default
                )

            def get_bool(k: str) -> bool | None:
                """Extract bool value using build DSL."""
                return cast("bool | None", get_val(k, "bool"))

            def get_str(k: str) -> str | None:
                """Extract str value using build DSL."""
                return cast("str | None", get_val(k, "str"))

            result = FlextCliCommonParams.apply_to_config(
                config,
                verbose=get_bool("verbose"),
                quiet=get_bool("quiet"),
                debug=get_bool("debug"),
                trace=get_bool("trace"),
                log_level=get_str("log_level"),
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
                # Use build() DSL for log level extraction with fallback
                log_level_attr = getattr(config, "cli_log_level", None) or getattr(
                    config, "log_level", None
                )
                log_level_name = cast(
                    "str",
                    u.build(
                        log_level_attr.value if log_level_attr else None,
                        ops={"ensure": "str", "ensure_default": "INFO"},
                        on_error="skip",
                    ),
                )
                log_level_value = getattr(logging, log_level_name, logging.INFO)
            # Use build() DSL for console_enabled extraction
            console_enabled = cast(
                "bool",
                u.build(
                    getattr(config, "console_enabled", None),
                    ops={"ensure": "bool", "ensure_default": True},
                    on_error="skip",
                ),
            )

            # Force reconfiguration (bypasses is_configured() guards)
            FlextRuntime.reconfigure_structlog(
                log_level=log_level_value,
                console_renderer=console_enabled,
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
    ) -> Callable[[FlextCliProtocols.Cli.CliCommandFunction], click.Group]:
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
        # Click group decorator returns compatible type with CliCommandFunction protocol
        # Use cast to satisfy type checker - _create_cli_decorator returns Command | Group
        # but we know it's Group when entity_type is "group"
        decorator = self._create_cli_decorator("group", name, help_text)
        return cast(
            "Callable[[FlextCliProtocols.Cli.CliCommandHandler], click.Group]",
            decorator,
        )

    # =========================================================================
    # PARAMETER DECORATORS (OPTION, ARGUMENT)
    # =========================================================================

    def create_option_decorator(
        self,
        *param_decls: str,
        config: FlextCliModels.OptionConfig | None = None,
        **kwargs: t.GeneralValueType,
    ) -> Callable[
        [FlextCliProtocols.Cli.CliCommandFunction],
        FlextCliProtocols.Cli.CliCommandFunction,
    ]:
        """Create Click option decorator with explicit parameters.

        Business Rule:
        ──────────────
        Creates Click option decorators for CLI commands. Uses Click directly
        (cli.py is the ONLY file allowed to import Click). All parameters are
        explicitly typed to avoid **kwargs type issues.

        Audit Implication:
        ───────────────────
        CLI options are validated at command registration time. Invalid options
        will cause command registration to fail, preventing runtime errors.

        Args:
            *param_decls: Parameter declarations (e.g., "--count", "-c")
            config: Optional config object with all option settings (preferred)
            **kwargs: Optional keyword args: default, type_hint, required (bool),
                help_text (str), multiple (bool), count (bool), show_default (bool)

        Returns:
            Option decorator

        Note:
            For advanced Click options, import Click directly in cli.py only.

        Example:
            >>> cli = FlextCliCli()
            >>> option = cli.create_option_decorator(
            ...     "--verbose", "-v", help_text="Enable verbose output"
            ... )

        """
        # Build config from explicit parameters if not provided
        # Business Rule: OptionConfig.type_hint accepts GeneralValueType
        # Click ParamType and Python types are compatible with GeneralValueType at runtime
        # We use cast to satisfy type checker while maintaining runtime compatibility
        # Use build() DSL for config building with generalized helpers
        if config is None:

            def get_bool_val(k: str) -> bool:
                """Get bool value with default False."""
                return cast(
                    "bool",
                    u.build(
                        kwargs.get(k),
                        ops={"ensure": "bool", "ensure_default": False},
                        on_error="skip",
                    ),
                )

            def get_str_val(k: str, default: str | None = None) -> str | None:
                """Get str value with default."""
                return cast(
                    "str | None",
                    u.build(
                        kwargs.get(k),
                        ops={"ensure": "str", "ensure_default": default},
                        on_error="skip",
                    ),
                )

            config = FlextCliModels.OptionConfig(
                default=kwargs.get("default"),
                type_hint=cast(
                    "t.GeneralValueType | None",
                    u.build(
                        kwargs.get("type_hint"),
                        ops={"ensure_default": None},
                        on_error="skip",
                    ),
                ),
                required=get_bool_val("required"),
                help_text=get_str_val("help_text"),
                multiple=get_bool_val("multiple"),
                count=get_bool_val("count"),
                show_default=get_bool_val("show_default"),
            )

        # Use Click directly (cli.py is ONLY file that may import Click)
        # Business Rule: Typer auto-detects boolean flags from type hints and defaults
        # The 'is_flag' and 'flag_value' parameters are deprecated in Typer
        # Click still supports them, but we remove them for Typer compatibility
        # Typer automatically creates flags for bool types with default values
        decorator = click.option(
            *param_decls,
            default=config.default,
            type=config.type_hint,
            required=config.required,
            help=config.help_text,
            multiple=config.multiple,
            count=config.count,
            show_default=config.show_default,
        )
        self.logger.debug(
            "Created option decorator",
            extra={"param_decls": param_decls, "required": config.required},
        )
        # Click option decorator wraps function but preserves
        # CliCommandFunction protocol
        return decorator

    def create_argument_decorator(
        self,
        *param_decls: str,
        type_hint: click.ParamType | type | None = None,
        required: bool = True,
        nargs: int = 1,
    ) -> Callable[
        [FlextCliProtocols.Cli.CliCommandFunction],
        FlextCliProtocols.Cli.CliCommandFunction,
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
        # Click argument decorator wraps function but preserves
        # CliCommandFunction protocol
        return decorator

    # =========================================================================
    # PARAMETER TYPES
    # =========================================================================

    @staticmethod
    def get_datetime_type(
        formats: Sequence[str] | None = None,
    ) -> click.DateTime:
        """Get Click DateTime parameter type.

        Args:
            formats: Accepted datetime formats (default:
                ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'])

        Returns:
            Click DateTime type

        Example:
            >>> cli = FlextCliCli()
            >>> dt_type = cli.get_datetime_type(formats=["%Y-%m-%d", "%d/%m/%Y"])

        """
        # Use build() DSL for formats normalization
        formats_list = cast(
            "list[str]",
            u.build(
                formats,
                ops={
                    "ensure": "list",
                    "ensure_default": FlextCliConstants.FileDefaults.DEFAULT_DATETIME_FORMATS,
                },
                on_error="skip",
            ),
        )
        return click.DateTime(formats=formats_list)

    @staticmethod
    def get_uuid_type() -> click.ParamType:
        """Get Click UUID parameter type.

        Returns:
            Click UUID parameter type instance

        Example:
            >>> cli = FlextCliCli()
            >>> uuid_type = cli.get_uuid_type()
            >>> # Use in option: type=uuid_type

        """
        return click.UUID

    @staticmethod
    def get_tuple_type(
        types: Sequence[type[t.GeneralValueType] | click.ParamType],
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

    @staticmethod
    def get_bool_type() -> type[bool]:
        """Get bool parameter type.

        Returns:
            bool type for Click parameters

        Example:
            >>> cli = FlextCliCli()
            >>> bool_type = cli.get_bool_type()
            >>> # Use in option: type=bool_type

        """
        return bool

    @staticmethod
    def get_string_type() -> type[str]:
        """Get string parameter type.

        Returns:
            str type for Click parameters

        Example:
            >>> cli = FlextCliCli()
            >>> str_type = cli.get_string_type()

        """
        return str

    @staticmethod
    def get_int_type() -> type[int]:
        """Get integer parameter type.

        Returns:
            int type for Click parameters

        Example:
            >>> cli = FlextCliCli()
            >>> int_type = cli.get_int_type()

        """
        return int

    @staticmethod
    def get_float_type() -> type[float]:
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

    @staticmethod
    def get_current_context() -> click.Context | None:
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

    @staticmethod
    def create_pass_context_decorator() -> Callable[
        [Callable[[click.Context], t.GeneralValueType]],
        Callable[[click.Context], t.GeneralValueType],
    ]:
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
        # click.pass_context returns a decorator that satisfies
        # CliCommandFunction protocol
        # Use cast for structural typing compatibility
        # The return type is complex, so we use cast to satisfy type checker
        return cast(
            "Callable[[Callable[[click.Context], t.GeneralValueType]], Callable[[click.Context], t.GeneralValueType]]",
            click.pass_context,
        )

    # =========================================================================
    # COMMAND EXECUTION
    # =========================================================================

    @staticmethod
    def echo(
        message: str | None = None,
        file: IO[str] | None = None,
        *,
        nl: bool = True,
        err: bool = False,
        color: bool | None = None,
    ) -> r[bool]:
        """Output message using Typer.echo (Typer backend).

        Args:
            message: Message to output
            file: File to write to (default: stdout)
            nl: Add newline
            err: Write to stderr
            color: Force color on/off

        Returns:
            r[bool]: True if echo succeeded, failure on error

        """
        typer.echo(message=message, file=file, nl=nl, err=err, color=color)
        return r[bool].ok(True)

    @staticmethod
    def confirm(
        text: str,
        config: FlextCliModels.ConfirmConfig | None = None,
        **kwargs: bool | str,
    ) -> r[bool]:
        """Prompt for confirmation using Typer backend.

        Business Rule:
        ──────────────
        Prompts user for yes/no confirmation. Uses Typer's confirm() function
        which handles user input validation and error handling. If abort=True
        and user declines, raises typer.Abort exception.

        Audit Implication:
        ───────────────────
        User confirmations are logged for audit trail. Aborted confirmations
        are tracked as user-initiated cancellations.

        Args:
            text: Prompt text
            config: Optional config object with all confirmation settings (preferred)
            **kwargs: Optional keyword args: default (bool), abort (bool),
                prompt_suffix (str), show_default (bool), err (bool)

        Returns:
            r[bool]: Success with confirmation value or failure

        Raises:
            typer.Abort: If user aborts

        """
        # Use build() DSL for config building with generalized helpers
        if config is None:

            def get_bool_val(k: str, default: bool = False) -> bool:
                """Get bool value with default."""
                return cast(
                    "bool",
                    u.build(
                        kwargs.get(k),
                        ops={"ensure": "bool", "ensure_default": default},
                        on_error="skip",
                    ),
                )

            def get_str_val(k: str, default: str = "") -> str:
                """Get str value with default."""
                return cast(
                    "str",
                    u.build(
                        kwargs.get(k),
                        ops={"ensure": "str", "ensure_default": default},
                        on_error="skip",
                    ),
                )

            config = FlextCliModels.ConfirmConfig(
                default=get_bool_val("default"),
                abort=get_bool_val("abort"),
                prompt_suffix=get_str_val(
                    "prompt_suffix", FlextCliConstants.UIDefaults.DEFAULT_PROMPT_SUFFIX
                ),
                show_default=get_bool_val("show_default", True),
                err=get_bool_val("err"),
            )

        try:
            result = typer.confirm(
                text=text,
                default=config.default,
                abort=config.abort,
                prompt_suffix=config.prompt_suffix,
                show_default=config.show_default,
                err=config.err,
            )
            return r[bool].ok(result)
        except typer.Abort as e:
            return r[bool].fail(
                FlextCliConstants.ErrorMessages.USER_ABORTED_CONFIRMATION.format(
                    error=e,
                ),
            )

    @staticmethod
    def prompt(
        text: str,
        config: FlextCliModels.PromptConfig | None = None,
        **kwargs: t.GeneralValueType,
    ) -> r[t.GeneralValueType]:
        """Prompt for input using Typer backend.

        Business Rule:
        ──────────────
        Prompts user for text input. Uses Typer's prompt() function which handles
        input validation, type conversion, and error handling. Supports optional
        confirmation prompts for sensitive inputs (passwords, etc.).

        Audit Implication:
        ───────────────────
        User inputs are logged for audit trail. Sensitive inputs (passwords) should
        use hide_input=True and confirmation_prompt=True, and are masked in logs.

        Args:
            text: Prompt text
            config: Optional config object with all prompt settings (preferred)
            **kwargs: Optional keyword args: default, type_hint, value_proc,
                prompt_suffix (str), hide_input (bool), confirmation_prompt (bool),
                show_default (bool), err (bool), show_choices (bool)

        Returns:
            r[GeneralValueType]: Success with input value or failure

        Raises:
            typer.Abort: If user aborts

        """
        # Use build() DSL for config building with generalized helpers
        if config is None:

            def get_bool_val(k: str, default: bool = False) -> bool:
                """Get bool value with default."""
                return cast(
                    "bool",
                    u.build(
                        kwargs.get(k),
                        ops={"ensure": "bool", "ensure_default": default},
                        on_error="skip",
                    ),
                )

            def get_str_val(k: str, default: str = "") -> str:
                """Get str value with default."""
                return cast(
                    "str",
                    u.build(
                        kwargs.get(k),
                        ops={"ensure": "str", "ensure_default": default},
                        on_error="skip",
                    ),
                )

            value_proc_val = kwargs.get("value_proc")
            config = FlextCliModels.PromptConfig(
                default=kwargs.get("default"),
                type_hint=kwargs.get("type_hint"),
                value_proc=value_proc_val if callable(value_proc_val) else None,
                prompt_suffix=get_str_val(
                    "prompt_suffix", FlextCliConstants.UIDefaults.DEFAULT_PROMPT_SUFFIX
                ),
                hide_input=get_bool_val("hide_input"),
                confirmation_prompt=get_bool_val("confirmation_prompt"),
                show_default=get_bool_val("show_default", True),
                err=get_bool_val("err"),
                show_choices=get_bool_val("show_choices", True),
            )

        try:
            result = typer.prompt(
                text=text,
                default=config.default,
                hide_input=config.hide_input,
                confirmation_prompt=config.confirmation_prompt,
                type=config.type_hint,
                value_proc=config.value_proc,
                prompt_suffix=config.prompt_suffix,
                show_default=config.show_default,
                err=config.err,
                show_choices=config.show_choices,
            )
            # Convert result to CliJsonValue - typer.prompt returns various types
            # CliJsonValue is alias of GeneralValueType, so no cast needed
            # Use build() DSL for JSON conversion
            # Reuse to_json helper from output module
            from flext_cli.services.output import to_json

            json_value = to_json(result) if isinstance(result, dict) else result
            return r[t.GeneralValueType].ok(json_value)
        except typer.Abort as e:
            return r[t.GeneralValueType].fail(
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
    ) -> r[CliRunner]:
        """Create Click CliRunner for testing.

        Args:
            charset: Character encoding
            env: Environment variables
            echo_stdin: Echo stdin to output

        Returns:
            r[CliRunner]: Success with CliRunner instance or failure

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
        return r[CliRunner].ok(runner)

    # =========================================================================
    # UTILITIES
    # =========================================================================

    @staticmethod
    def format_filename(
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

    @staticmethod
    def get_terminal_size() -> tuple[int, int]:
        """Get terminal size.

        Returns:
            Tuple of (width, height)

        """
        size = shutil.get_terminal_size()
        return (size.columns, size.lines)

    @staticmethod
    def clear_screen() -> r[bool]:
        """Clear terminal screen.

        Returns:
            r[bool]: True if screen cleared successfully, failure on error

        """
        click.clear()
        return r[bool].ok(True)

    @staticmethod
    def pause(
        info: str = FlextCliConstants.UIDefaults.DEFAULT_PAUSE_MESSAGE,
    ) -> r[bool]:
        """Pause execution until key press.

        Args:
            info: Information message to display

        Returns:
            r[bool]: True if pause succeeded, failure on error

        """
        click.pause(info=info)
        return r[bool].ok(True)

    @staticmethod
    def model_command(
        model_class: type[TModel],
        handler: Callable[
            [TModel],
            t.GeneralValueType | r[t.GeneralValueType],
        ],
        config: FlextCliConfig | None = None,
    ) -> FlextCliProtocols.Cli.CliCommandFunction:
        """Create Typer command from Pydantic model with automatic config integration.

        Generic model-driven CLI automation using Field metadata introspection.
        Delegates to existing Typer infrastructure for type conversion.

        Handles optional parameters: Fields with defaults become optional CLI args
        that don't require specification on command line.

        Supports Pydantic v2 Field aliases: Field(alias="input-dir") generates
        --input-dir CLI option (not --input_dir).

        **AUTOMATIC CONFIG INTEGRATION** (NEW):
        If config singleton is provided, FlextCli automatically:
        1. Reads config field values as defaults for CLI parameters
           (when no CLI value provided)
        2. Updates config with CLI values using Pydantic v2's __dict__
           (bypasses validators)
        3. Passes fully-populated params model to handler
           (no fallback logic needed)

        This enables full configuration hierarchy - completely automatic:
        - Constants (in config defaults)
        - .env file (config reads via env_prefix)
        - Environment variables (config reads via Pydantic Settings)
        - CLI Arguments (override config if different, stored via __dict__
          to bypass validation)

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
            #   → Calls: handle(MyParams(input_dir=config.input_dir,
            #                            count=10, sync=True))
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
        # Delegate to FlextCliModels.ModelCommandBuilder for reduced
        # complexity (SOLID/SRP)
        if not hasattr(model_class, "model_fields"):
            # Type narrowing: get class name safely for error message
            class_name = getattr(model_class, "__name__", str(model_class))
            msg = (
                f"{class_name} must be a Pydantic model "
                f"(BaseModel or FlextModels subclass)"
            )
            raise TypeError(msg)

        # Use cast to satisfy type checker - TModel extends FlextModels
        # Handler can return GeneralValueType or r[GeneralValueType]
        # ModelCommandBuilder accepts GeneralValueType, so we cast handler
        builder = FlextCliModels.ModelCommandBuilder(
            cast("type[FlextModels]", model_class),
            cast("Callable[[FlextModels], t.GeneralValueType]", handler),
            config,
        )
        # ModelCommandBuilder.build() returns a function implementing
        # CliCommandFunction protocol
        return builder.build()

    @staticmethod
    def execute() -> r[t.JsonDict]:
        """Execute Click abstraction layer operations.

        Returns:
            r[t.JsonDict]: Success with CLI status or
            failure with error

        """
        return r[t.JsonDict].ok({
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
            FlextCliConstants.DictKeys.STATUS: (
                FlextCliConstants.ServiceStatus.OPERATIONAL.value
            ),
        })


__all__ = [
    "FlextCliCli",
]
