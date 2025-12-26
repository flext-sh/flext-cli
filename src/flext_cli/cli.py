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
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import IO, Annotated, TypeGuard

import click
import typer
from click.exceptions import UsageError
from flext_core import FlextContainer, FlextLogger, FlextRuntime, r
from pydantic import BaseModel
from typer.testing import CliRunner

from flext_cli.cli_params import FlextCliCommonParams
from flext_cli.constants import FlextCliConstants as c
from flext_cli.models import ConfirmConfig, OptionConfig, m
from flext_cli.protocols import p
from flext_cli.settings import FlextCliSettings
from flext_cli.typings import t
from flext_cli.utilities import FlextCliUtilities as u


class FlextCliCli:
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
    - Parameter types (Choice, Path, File, IntRange, etc.Cli.)
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

    @staticmethod
    def _is_option_config_protocol(
        obj: object,
    ) -> bool:
        """Type guard to check if object implements OptionConfigProtocol."""
        return (
            hasattr(obj, "default")
            and hasattr(obj, "type_hint")
            and hasattr(obj, "required")
            and hasattr(obj, "help_text")
        )

    @staticmethod
    def _is_prompt_config_protocol(
        obj: object,
    ) -> TypeGuard[p.Cli.PromptConfigProtocol]:
        """Type guard to check if object implements PromptConfigProtocol."""
        return (
            hasattr(obj, "default")
            and hasattr(obj, "type_hint")
            and hasattr(obj, "prompt_suffix")
        )

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
        entity_type: c.Cli.EntityTypeLiteral | c.Cli.EntityType,
        name: str | None,
        help_text: str | None,
    ) -> Callable[[p.Cli.CliCommandFunction], click.Command | click.Group]:
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
    ) -> Callable[[p.Cli.CliCommandFunction], click.Command]:
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
        return self._create_cli_decorator(c.Cli.EntityType.COMMAND, name, help_text)

    def _extract_typed_value(
        self,
        val: t.GeneralValueType | None,
        type_name: str,
        default: t.GeneralValueType | None = None,
    ) -> t.GeneralValueType | None:
        """Extract typed value using build DSL."""
        if val is None:
            return default
        # Handle conversion based on type_name with proper type safety
        if type_name == "str":
            str_default = "" if not isinstance(default, str) else default
            built_val: t.GeneralValueType = u.Cli.convert(val, str, str_default)
        elif type_name == "bool":
            bool_default = False if not isinstance(default, bool) else default
            built_val = u.Cli.convert(val, bool, bool_default)
        else:  # dict
            dict_default = {} if not isinstance(default, dict) else default
            built_val = u.Cli.convert(val, dict, dict_default)
        result = (
            built_val
            if isinstance(
                val,
                (bool if type_name == "bool" else str if type_name == "str" else dict),
            )
            else default
        )
        if result is None:
            return None
        if isinstance(result, (str, int, float, bool, list)):
            return result
        if isinstance(result, dict):
            # Ensure dict keys are strings for GeneralValueType compatibility
            return {
                str(k): v
                for k, v in result.items()
                if isinstance(v, (str, int, float, bool, list, dict, type(None)))
            }
        return str(result)

    def _get_log_level_value(self, config: FlextCliSettings) -> int:
        """Get log level value from config."""
        if config.debug or config.trace:
            return logging.DEBUG
        log_level_attr = getattr(config, "cli_log_level", None) or getattr(
            config,
            "log_level",
            None,
        )
        log_level_built = u.Cli.convert(
            log_level_attr.value if log_level_attr else None,
            str,
            "INFO",
        )
        log_level_name: str = (
            str(log_level_built) if log_level_built is not None else "INFO"
        )
        return getattr(logging, log_level_name, logging.INFO)

    def _get_console_enabled(self, config: FlextCliSettings) -> bool:
        """Get console enabled value from config."""
        console_enabled_val = getattr(config, "console_enabled", None)
        if console_enabled_val is None:
            return True
        return bool(console_enabled_val)

    def _apply_common_params_to_config(
        self,
        config: FlextCliSettings,
        *,
        debug: bool = False,
        trace: bool = False,
        verbose: bool = False,
        quiet: bool = False,
        log_level: str | None = None,
    ) -> None:
        """Apply common params to config and reconfigure logger."""
        common_params = {
            "debug": debug,
            "trace": trace,
            "verbose": verbose,
            "quiet": quiet,
            "log_level": log_level,
        }

        # Use mapper to filter out None and False values
        # Type narrowing: bool | str | None are compatible with t.GeneralValueType (ScalarValue)
        # No  needed - values are already compatible with t.GeneralValueType
        common_params_typed: dict[str, t.GeneralValueType] = dict(common_params.items())
        active_params: dict[str, t.GeneralValueType] = u.mapper().filter_dict(
            common_params_typed,
            lambda _k, v: v is not None and v is not False,
        )

        if not active_params:
            return

        config_fields: set[str] = set(type(config).model_fields.keys())
        # Use mapper to filter params by config fields
        filtered_params: dict[str, t.GeneralValueType] = u.mapper().filter_dict(
            active_params,
            lambda k, _v: k in config_fields,
        )

        if not filtered_params:
            return

        def get_bool(k: str) -> bool | None:
            """Extract bool value from filtered params."""
            value = u.mapper().get(filtered_params, k)
            result = self._extract_typed_value(value, "bool")
            return result if isinstance(result, (bool, type(None))) else None

        def get_str(k: str) -> str | None:
            """Extract str value from filtered params."""
            value = u.mapper().get(filtered_params, k)
            result = self._extract_typed_value(value, "str")
            return result if isinstance(result, (str, type(None))) else None

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

        log_level_value = self._get_log_level_value(config)
        console_enabled = self._get_console_enabled(config)

        # FlextRuntime.reconfigure_structlog may not be available in all contexts
        # Use getattr to avoid pyright error about unknown attribute
        reconfigure_method = getattr(FlextRuntime, "reconfigure_structlog", None)
        if reconfigure_method is not None and callable(reconfigure_method):
            reconfigure_method(
                log_level=log_level_value,
                console_renderer=console_enabled,
            )

    def create_app_with_common_params(
        self,
        name: str,
        help_text: str,
        config: FlextCliSettings | None = None,
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
            config: Optional FlextSettings instance for logger reconfiguration
            add_completion: Whether to add shell completion support

        Returns:
            Configured Typer app with global common params

        Example:
            >>> cli = FlextCliCli()
            >>> app = cli.create_app_with_common_params(
            ...     name="my-app", help_text="My application", config=my_config
            ... )
            >>> # Now app has --debug, --log-level, etc.Cli. at global level
            >>> # Usage: my-app --debug subcommand

        """
        app = typer.Typer(
            name=name,
            help=help_text,
            add_completion=add_completion,
        )

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
            if config:
                self._apply_common_params_to_config(
                    config,
                    debug=debug,
                    trace=trace,
                    verbose=verbose,
                    quiet=quiet,
                    log_level=log_level,
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
    ) -> Callable[[p.Cli.CliCommandFunction], click.Group]:
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
        # _create_cli_decorator returns Command | Group, but we know it's Group when entity_type is "group"
        decorator = self._create_cli_decorator("group", name, help_text)
        # Type narrowing: decorator is Callable compatible with click.Group
        if not callable(decorator):
            msg = "decorator must be callable"
            raise TypeError(msg)
        # Type narrowing: when entity_type is "group", decorator returns click.Group
        # Create wrapper that ensures return type is click.Group

        def group_decorator(func: p.Cli.CliCommandFunction) -> click.Group:
            result = decorator(func)
            # Runtime validation: result should be click.Group when entity_type is "group"
            if not isinstance(result, click.Group):
                msg = "decorator must return click.Group for group entity type"
                raise TypeError(msg)
            return result

        return group_decorator

    # =========================================================================
    # PARAMETER DECORATORS (OPTION, ARGUMENT)
    # =========================================================================

    def _build_bool_value(
        self,
        kwargs: dict[str, t.GeneralValueType],
        key: str,
        *,
        default: bool = False,
    ) -> bool:
        """Extract and build bool value from kwargs."""
        val = u.get(kwargs, key)
        if val is None:
            return default
        return u.Cli.convert(val, bool, default)

    def _build_str_value(
        self,
        kwargs: dict[str, t.GeneralValueType],
        key: str,
        default: str = "",
    ) -> str:
        """Extract and build str value from kwargs."""
        val = u.mapper().get(kwargs, key)
        if val is None:
            return default
        build_result = u.build(
            val,
            ops={"ensure": "str", "ensure_default": default},
        )
        if not isinstance(build_result, str):
            msg = "build_result must be str"
            raise TypeError(msg)
        return build_result

    def _normalize_type_hint(
        self,
        type_hint_val: t.GeneralValueType | None,
    ) -> t.GeneralValueType | None:
        """Normalize and validate type hint value."""
        type_hint_build = u.build(
            type_hint_val,
            ops={"ensure_default": None},
        )
        # Type narrowing: build returns t.GeneralValueType | None
        if type_hint_build is None:
            return None
        # Check for t.GeneralValueType compatible types
        if isinstance(type_hint_build, str):
            return type_hint_build
        if isinstance(type_hint_build, int):
            return type_hint_build
        if isinstance(type_hint_build, float):
            return type_hint_build
        if isinstance(type_hint_build, bool):
            return type_hint_build
        if isinstance(type_hint_build, list):
            return type_hint_build
        if isinstance(type_hint_build, tuple):
            return type_hint_build
        if isinstance(type_hint_build, dict):
            return type_hint_build
        # Convert other types (including type objects) to string
        return str(type_hint_build)

    def _build_option_config_from_kwargs(
        self,
        kwargs: dict[str, t.GeneralValueType],
    ) -> OptionConfig:
        """Build OptionConfig from kwargs dict."""
        return OptionConfig(
            default=u.mapper().get(kwargs, "default"),
            type_hint=self._normalize_type_hint(u.mapper().get(kwargs, "type_hint")),
            required=self._build_bool_value(kwargs, "required"),
            help_text=self._build_str_value(kwargs, "help_text"),
            multiple=self._build_bool_value(kwargs, "multiple"),
            count=self._build_bool_value(kwargs, "count"),
            show_default=self._build_bool_value(kwargs, "show_default"),
        )

    def create_option_decorator(
        self,
        *param_decls: str,
        config: object | None = None,
        **kwargs: t.GeneralValueType,
    ) -> Callable[
        [p.Cli.CliCommandFunction],
        p.Cli.CliCommandFunction,
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
        if config is None:
            config_instance = self._build_option_config_from_kwargs(kwargs)
            # Type narrowing: config_instance implements OptionConfigProtocol
            if not self._is_option_config_protocol(config_instance):
                msg = "config_instance must implement OptionConfigProtocol"
                raise TypeError(msg)
            config = config_instance  # Type checked by _is_option_config_protocol above

        # Type narrowing: config is not None after assignment
        if config is None:
            msg = "config cannot be None"
            raise ValueError(msg)

        # Use Click directly (cli.py is ONLY file that may import Click)
        # Use safe attribute access since config may not have all attributes
        decorator = click.option(
            *param_decls,
            default=getattr(config, "default", None),
            type=getattr(config, "type_hint", None),
            required=getattr(config, "required", False),
            help=getattr(config, "help_text", ""),
            multiple=getattr(config, "multiple", False),
            count=getattr(config, "count", False),
            show_default=getattr(config, "show_default", True),
        )
        self.logger.debug(
            "Created option decorator",
            extra={
                "param_decls": param_decls,
                "required": getattr(config, "required", False),
            },
        )
        return decorator

    def create_argument_decorator(
        self,
        *param_decls: str,
        type_hint: click.ParamType | type | None = None,
        required: bool = True,
        nargs: int = 1,
    ) -> Callable[
        [p.Cli.CliCommandFunction],
        p.Cli.CliCommandFunction,
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
        formats_build = u.build(
            formats,
            ops={
                "ensure": "list",
                "ensure_default": c.Cli.FileDefaults.DEFAULT_DATETIME_FORMATS,
            },
        )
        if not isinstance(formats_build, list):
            msg = "formats_build must be list"
            raise TypeError(msg)
        # Convert t.GeneralValueType to str for datetime formats
        formats_list: list[str] = [str(fmt) for fmt in formats_build]
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
        # Type narrowing: click.pass_context is a decorator function
        if not callable(click.pass_context):
            msg = "click.pass_context must be callable"
            raise TypeError(msg)
        # Create wrapper to ensure return type matches signature

        def pass_context_wrapper(
            func: Callable[[click.Context], t.GeneralValueType],
        ) -> Callable[[click.Context], t.GeneralValueType]:
            # click.pass_context wraps function to pass context as first argument
            decorated = click.pass_context(func)
            # Runtime validation: decorated function should accept context
            if not callable(decorated):
                msg = "decorated function must be callable"
                raise TypeError(msg)
            # Type narrowing: decorated function matches signature
            # click.pass_context returns a function that matches our signature
            # Runtime validation confirms compatibility
            # Type narrowing: decorated is Callable[[click.Context], t.GeneralValueType]
            # Create wrapper that ensures type safety

            def typed_decorated(_ctx: click.Context) -> t.GeneralValueType:
                # click.pass_context returns a function that injects context automatically
                # The decorated function signature is: (*args, **kwargs) -> result
                # Context is injected by click, so we call decorated() without ctx
                # click handles context injection internally
                return decorated()  # click.pass_context handles context injection

            return typed_decorated

        return pass_context_wrapper

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
    def _build_confirm_config_from_kwargs(
        kwargs: Mapping[str, t.GeneralValueType],
    ) -> ConfirmConfig:
        """Build ConfirmConfig from kwargs dict."""

        def get_bool_val(k: str, *, default: bool = False) -> bool:
            """Get bool value with default."""
            val = u.mapper().get(kwargs, k)
            if val is None:
                return default
            build_result = u.build(
                val,
                ops={"ensure": "bool", "ensure_default": default},
            )
            if not isinstance(build_result, bool):
                msg = "build_result must be bool"
                raise TypeError(msg)
            return build_result

        def get_str_val(k: str, default: str = "") -> str:
            """Get str value with default."""
            val = u.mapper().get(kwargs, k)
            if val is None:
                return default
            build_result = u.build(
                val,
                ops={"ensure": "str", "ensure_default": default},
            )
            if not isinstance(build_result, str):
                msg = "build_result must be str"
                raise TypeError(msg)
            return build_result

        return ConfirmConfig(
            default=get_bool_val("default", default=False),
            abort=get_bool_val("abort", default=False),
            prompt_suffix=get_str_val(
                "prompt_suffix",
                default=c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX,
            ),
            show_default=get_bool_val("show_default", default=True),
            err=get_bool_val("err", default=False),
        )

    @staticmethod
    def confirm(
        text: str,
        config: p.Cli.ConfirmConfigProtocol | None = None,
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
        # Build config from explicit parameters if not provided
        if config is None:
            # Type narrowing: kwargs values are bool | str, which are t.GeneralValueType compatible
            config_instance = FlextCliCli._build_confirm_config_from_kwargs(kwargs)
            # Type narrowing: config_instance implements ConfirmConfigProtocol
            if not hasattr(config_instance, "default") or not hasattr(
                config_instance,
                "abort",
            ):
                msg = "config_instance must have 'default' and 'abort' attributes"
                raise TypeError(msg)
            config = config_instance

        # Type narrowing: config is not None after assignment
        if config is None:
            msg = "config cannot be None"
            raise ValueError(msg)

        try:
            result = typer.confirm(
                text=text,
                default=getattr(config, "default", None),
                abort=getattr(config, "abort", False),
                prompt_suffix=getattr(config, "prompt_suffix", ""),
                show_default=getattr(config, "show_default", True),
                err=getattr(config, "err", False),
            )
            return r[bool].ok(result)
        except typer.Abort as e:
            return r[bool].fail(
                c.Cli.ErrorMessages.USER_ABORTED_CONFIRMATION.format(
                    error=e,
                ),
            )

    @staticmethod
    def _build_prompt_config_from_kwargs(
        kwargs: Mapping[str, t.GeneralValueType],
    ) -> m.Cli.PromptConfig:
        """Build PromptConfig from kwargs dict."""

        def get_bool_val(k: str, *, default: bool = False) -> bool:
            """Get bool value with default."""
            val = u.mapper().get(kwargs, k)
            if val is None:
                return default
            build_result = u.build(
                val,
                ops={"ensure": "bool", "ensure_default": default},
            )
            if not isinstance(build_result, bool):
                msg = "build_result must be bool"
                raise TypeError(msg)
            return build_result

        def get_str_val(k: str, default: str = "") -> str:
            """Get str value with default."""
            val = u.mapper().get(kwargs, k)
            if val is None:
                return default
            build_result = u.build(
                val,
                ops={"ensure": "str", "ensure_default": default},
            )
            if not isinstance(build_result, str):
                msg = "build_result must be str"
                raise TypeError(msg)
            return build_result

        value_proc_val = u.mapper().get(kwargs, "value_proc")
        return m.Cli.PromptConfig(
            default=u.mapper().get(kwargs, "default"),
            type_hint=u.mapper().get(kwargs, "type_hint"),
            value_proc=value_proc_val if callable(value_proc_val) else None,
            prompt_suffix=get_str_val(
                "prompt_suffix",
                c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX,
            ),
            hide_input=get_bool_val("hide_input", default=False),
            confirmation_prompt=get_bool_val("confirmation_prompt", default=False),
            show_default=get_bool_val("show_default", default=True),
            err=get_bool_val("err", default=False),
            show_choices=get_bool_val("show_choices", default=True),
        )

    @staticmethod
    def prompt(
        text: str,
        config: p.Cli.PromptConfigProtocol | None = None,
        **kwargs: t.GeneralValueType,
    ) -> r[t.GeneralValueType]:
        """Prompt for input using Typer backend.

        Business Rule:
        ──────────────
        Prompts user for text input. Uses Typer's prompt() function which handles
        input validation, type conversion, and error handling. Supports optional
        confirmation prompts for sensitive inputs (passwords, etc.Cli.).

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
            r[t.GeneralValueType]: Success with input value or failure

        Raises:
            typer.Abort: If user aborts

        """
        # Build config from explicit parameters if not provided
        if config is None:
            config_instance = FlextCliCli._build_prompt_config_from_kwargs(kwargs)
            # Type narrowing: config_instance implements PromptConfigProtocol
            if not FlextCliCli._is_prompt_config_protocol(config_instance):
                msg = "config_instance must implement PromptConfigProtocol"
                raise TypeError(msg)
            config = config_instance

        # Type narrowing: config is not None after assignment
        if config is None:
            msg = "config cannot be None"
            raise ValueError(msg)

        # Note: config is already properly typed via _build_prompt_config_from_kwargs
        # and validated via _is_prompt_config_protocol above

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
            # Convert result to t.GeneralValueType - typer.prompt returns various types
            # Use u.build with JSON transformation for dict conversion
            json_value: t.GeneralValueType = (
                u.build(
                    result,
                    ops={"ensure": "dict", "transform": {"to_json": True}},
                )
                if isinstance(result, dict)
                else result
            )
            return r[t.GeneralValueType].ok(json_value)
        except typer.Abort as e:
            return r[t.GeneralValueType].fail(
                c.Cli.ErrorMessages.USER_ABORTED_PROMPT.format(error=e),
            )

    # =========================================================================
    # TESTING SUPPORT
    # =========================================================================

    def create_cli_runner(
        self,
        charset: str = c.Cli.Utilities.DEFAULT_ENCODING,
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
            >>> runner = result.value
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
        info: str = c.Cli.CmdMessages.DEFAULT_PAUSE_MESSAGE,
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
        model_class: type[BaseModel],
        handler: Callable[
            [BaseModel],
            t.GeneralValueType | r[t.GeneralValueType],
        ],
        config: FlextCliSettings | None = None,
    ) -> p.Cli.CliCommandFunction:
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
        # Delegate to ModelCommandBuilder for reduced
        # complexity (SOLID/SRP)
        if not hasattr(model_class, "model_fields"):
            # Type narrowing: get class name safely for error message
            class_name = getattr(model_class, "__name__", str(model_class))
            msg = f"{class_name} must be a Pydantic model (BaseModel or m subclass)"
            raise TypeError(msg)

        # Handler can return t.GeneralValueType or r[t.GeneralValueType]
        # Validate model_class is a type and handler is callable
        if not isinstance(model_class, type):
            msg = "model_class must be a type"
            raise TypeError(msg)
        if not callable(handler):
            msg = "handler must be callable"
            raise TypeError(msg)
        # Create wrapper that normalizes return type
        # Handler accepts BaseModel, returns t.GeneralValueType or r[t.GeneralValueType]

        def normalized_handler(model: object) -> t.GeneralValueType:
            # Type narrowing: validate model is BaseModel instance
            if not isinstance(model, BaseModel):
                msg = "model must be a BaseModel instance"
                raise TypeError(msg)
            # Runtime validation: model must be instance of expected model_class
            if not isinstance(model, model_class):
                class_name = getattr(model_class, "__name__", "UnknownClass")
                msg = f"model must be instance of {class_name}"
                raise TypeError(msg)
            # Model is now validated to be an instance of model_class
            # Handler accepts BaseModel, which model satisfies
            result = handler(model)
            # Normalize return type: if result is r[t.GeneralValueType], unwrap it
            if isinstance(result, r):
                if result.is_success:
                    # Type narrowing: unwrapped is t.GeneralValueType
                    return result.value
                # On failure, raise error
                msg = f"Handler failed: {result.error}"
                raise ValueError(msg)
            # Result is already t.GeneralValueType
            # Type narrowing: result is t.GeneralValueType (not r[t.GeneralValueType])
            return result

        # Type narrowing: model_class is type[FlextCliModelT] which extends BaseModel
        # Runtime validation: ensure model_class extends BaseModel (required for ModelCommandBuilder)
        # FlextCliModelT is bound to BaseModel, so any BaseModel subclass is valid
        if not issubclass(model_class, BaseModel):
            msg = "model_class must be a BaseModel subclass"
            raise TypeError(msg)
        builder = m.Cli.ModelCommandBuilder(
            model_class,
            normalized_handler,
            config,
        )
        # ModelCommandBuilder.build() returns a function implementing
        # CliCommandFunction protocol
        return builder.build()

    @staticmethod
    def execute() -> r[Mapping[str, t.GeneralValueType]]:
        """Execute Click abstraction layer operations.

        Returns:
            r[dict[str, t.GeneralValueType]]: Success with CLI status or
            failure with error

        """
        return r[dict[str, t.GeneralValueType]].ok({
            c.Cli.DictKeys.SERVICE: c.Cli.FLEXT_CLI,
            c.Cli.DictKeys.STATUS: (c.Cli.ServiceStatus.OPERATIONAL.value),
        })


__all__ = [
    "FlextCliCli",
    "Typer",
    "UsageError",
]

# Re-export Typer for API compatibility
Typer = typer.Typer
