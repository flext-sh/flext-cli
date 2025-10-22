"""FLEXT CLI Common Parameters - Auto-generated from FlextConfig properties.

Provides standardized CLI parameters that MUST be available in all CLI commands.
Parameters are auto-generated from FlextCliConfig pydantic field metadata.

These parameters are ENABLED BY DEFAULT and cannot be disabled without error.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys
import types
from collections.abc import Callable
from typing import ClassVar, Literal, cast, get_args, get_origin

import typer
from flext_core import FlextConstants, FlextResult, FlextTypes
from typer.models import OptionInfo

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants


class FlextCliCommonParams:
    """Common CLI parameters auto-generated from FlextConfig field metadata.

    Provides standardized parameter group integrated with FlextConfig and FlextLogger.
    These parameters are enabled by default and enforced across all CLI commands.

    All parameter definitions are automatically extracted from FlextCliConfig pydantic fields:
    - Descriptions from Field(description=...)
    - defaults from Field(default=...)
    - Constraints from Field(ge=..., le=...)
    - Types from field annotations

    Standard Parameters (auto-generated):
        --verbose/-v: Enable verbose output
        --quiet/-q: Suppress non-error output
        --debug/-d: Enable debug mode
        --trace/-t: Enable trace mode (requires debug)
        --log-level/-L: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        --log-format: Set log format (compact, detailed, full)
        --output-format/-o: Set output format (table, json, yaml, csv, plain)
        --no-color: Disable colored output
        --config-file/-c: Path to configuration file
    """

    # CLI Parameter Metadata registry
    # Maps field names to CLI-specific metadata (short flags, choices, priority)
    # Type aliases to reduce line length
    _reg = FlextCliConstants.CliParamsRegistry
    _def = FlextCliConstants.CliParamDefaults  # Singular - for FIELD_NAME_SEPARATOR
    _defs = FlextCliConstants.CliParamsDefaults  # Plural - for VALID_LOG_FORMATS

    CLI_PARAM_REGISTRY: ClassVar[dict[str, dict[str, object]]] = {
        "verbose": {
            _reg.KEY_SHORT: _reg.SHORT_FLAG_VERBOSE,
            _reg.KEY_PRIORITY: _reg.PRIORITY_VERBOSE,
        },
        "quiet": {
            _reg.KEY_SHORT: _reg.SHORT_FLAG_QUIET,
            _reg.KEY_PRIORITY: _reg.PRIORITY_QUIET,
        },
        "debug": {
            _reg.KEY_SHORT: _reg.SHORT_FLAG_DEBUG,
            _reg.KEY_PRIORITY: _reg.PRIORITY_DEBUG,
        },
        "trace": {
            _reg.KEY_SHORT: _reg.SHORT_FLAG_TRACE,
            _reg.KEY_PRIORITY: _reg.PRIORITY_TRACE,
        },
        "log_level": {
            _reg.KEY_SHORT: _reg.SHORT_FLAG_LOG_LEVEL,
            _reg.KEY_PRIORITY: _reg.PRIORITY_LOG_LEVEL,
            _reg.KEY_CHOICES: FlextCliConstants.LOG_LEVELS_LIST,
            _reg.KEY_CASE_SENSITIVE: _reg.CASE_INSENSITIVE,
        },
        "log_verbosity": {
            _reg.KEY_PRIORITY: _reg.PRIORITY_LOG_FORMAT,
            _reg.KEY_CHOICES: _defs.VALID_LOG_FORMATS,
            _reg.KEY_CASE_SENSITIVE: _reg.CASE_INSENSITIVE,
            _reg.KEY_FIELD_NAME_OVERRIDE: _reg.LOG_FORMAT_OVERRIDE,
        },
        "output_format": {
            _reg.KEY_SHORT: _reg.SHORT_FLAG_OUTPUT_FORMAT,
            _reg.KEY_PRIORITY: _reg.PRIORITY_OUTPUT_FORMAT,
            _reg.KEY_CHOICES: _defs.VALID_OUTPUT_FORMATS,
            _reg.KEY_CASE_SENSITIVE: _reg.CASE_INSENSITIVE,
        },
        "no_color": {
            _reg.KEY_PRIORITY: _reg.PRIORITY_NO_COLOR,
        },
        "config_file": {
            _reg.KEY_SHORT: _reg.SHORT_FLAG_CONFIG_FILE,
            _reg.KEY_PRIORITY: _reg.PRIORITY_CONFIG_FILE,
        },
    }

    # Class-level flag to track if parameters are enabled
    _params_enabled: bool = True
    _enforcement_mode: bool = True  # If True, error on disable attempt

    @classmethod
    def disable_enforcement(cls) -> None:
        """Disable enforcement mode (for testing only).

        WARNING: This should only be used in test scenarios.
        Production code must always use common parameters.
        """
        cls._enforcement_mode = False

    @classmethod
    def enable_enforcement(cls) -> None:
        """Enable enforcement mode (default).

        Common parameters are mandatory and attempts to disable them will error.
        """
        cls._enforcement_mode = True

    @classmethod
    def validate_enabled(cls) -> FlextResult[None]:
        """Validate that common parameters are enabled.

        Returns:
            FlextResult[None]: Success if enabled, failure if disabled in enforcement mode.

        """
        err = FlextCliConstants.CliParamsErrorMessages
        if not cls._params_enabled and cls._enforcement_mode:
            return FlextResult[None].fail(err.PARAMS_MANDATORY)
        return FlextResult[None].ok(None)

    @classmethod
    def create_option(cls, field_name: str) -> OptionInfo:
        """Create typer.Option() from FlextCliConfig field metadata.

        Auto-generates typer.Option() with all metadata from pydantic Field:
        - default value from field default
        - Help text from field description
        - Constraints (min/max) from JSON schema
        - Short flags from CLI_PARAM_REGISTRY
        - Valid choices from CLI_PARAM_REGISTRY

        Args:
            field_name: Name of field in FlextCliConfig (e.g., 'verbose', 'log_level')

        Returns:
            typer.Option() object to use as parameter default value

        Example:
            >>> verbose_opt = FlextCliCommonParams.create_option("verbose")
            >>> # Use as: verbose: bool = FlextCliCommonParams.verbose_option()

        """
        # Local aliases for shorter lines
        reg = cls._reg
        def_sep = cls._def  # Singular - FIELD_NAME_SEPARATOR, PARAM_NAME_SEPARATOR
        defs = cls._defs  # Plural - VALID_LOG_FORMATS, CHOICES_HELP_SUFFIX
        err = FlextCliConstants.CliParamsErrorMessages
        json = FlextCliConstants.JsonSchemaKeys
        pyd = FlextCliConstants.PydanticTypeNames

        # Get pydantic field metadata
        fields = FlextCliConfig.model_fields
        schema = FlextCliConfig.model_json_schema()

        if field_name not in fields:
            msg = err.FIELD_NOT_FOUND.format(field_name=field_name)
            raise ValueError(msg)

        field_info = fields[field_name]
        field_schema = schema[json.PROPERTIES].get(field_name, {})
        param_meta = cls.CLI_PARAM_REGISTRY.get(field_name, {})

        # Get base type (handle Optional/Union types)
        field_type = field_info.annotation
        origin = get_origin(field_type)

        if origin is types.NoneType or (
            hasattr(field_type, "__args__") and types.NoneType in get_args(field_type)
        ):
            # Extract non-None type from Optional
            args = [a for a in get_args(field_type) if a is not types.NoneType]
            field_type = args[0] if args else str

        # Build parameter declarations (--param-name, -short)
        cli_name_raw = param_meta.get(reg.KEY_FIELD_NAME_OVERRIDE, field_name)
        cli_name = str(cli_name_raw) if cli_name_raw != field_name else field_name
        option_name = f"--{cli_name.replace(def_sep.FIELD_NAME_SEPARATOR, def_sep.PARAM_NAME_SEPARATOR)}"
        param_decls = [option_name]

        if reg.KEY_SHORT in param_meta:
            short_val = param_meta[reg.KEY_SHORT]
            if isinstance(short_val, str):
                param_decls.insert(0, f"-{short_val}")

        # Get default value
        default_value = field_info.default
        if default_value is None:
            pass
        elif (
            hasattr(default_value, "__class__")
            and default_value.__class__.__name__ == pyd.UNDEFINED_TYPE
        ):
            default_value = None

        # Build help text from field description
        help_text = field_info.description or defs.DEFAULT_HELP_TEXT_FORMAT.format(
            field_name=field_name
        )

        # Enhance help text with choices
        if reg.KEY_CHOICES in param_meta:
            choices_val = param_meta[reg.KEY_CHOICES]
            if isinstance(choices_val, (list, tuple)):
                choices_str = ", ".join(str(c) for c in choices_val)
                help_text += defs.CHOICES_HELP_SUFFIX.format(choices_str=choices_str)

        # Enhance help text with constraints
        if json.MINIMUM in field_schema and json.MAXIMUM in field_schema:
            help_text += defs.RANGE_HELP_SUFFIX.format(
                minimum=field_schema[json.MINIMUM], maximum=field_schema[json.MAXIMUM]
            )

        # Build typer.Option parameters (type-safe)
        case_sensitive_val: bool | None = None
        if reg.KEY_CASE_SENSITIVE in param_meta:
            cs_raw = param_meta[reg.KEY_CASE_SENSITIVE]
            case_sensitive_val = bool(cs_raw) if isinstance(cs_raw, bool) else None

        min_val: float | int | None = None
        max_val: float | int | None = None
        if json.MINIMUM in field_schema:
            min_raw = field_schema[json.MINIMUM]
            min_val = min_raw if isinstance(min_raw, (int, float)) else None
        if json.MAXIMUM in field_schema:
            max_raw = field_schema[json.MAXIMUM]
            max_val = max_raw if isinstance(max_raw, (int, float)) else None

        show_default_val = default_value is not None

        return cast(
            "OptionInfo",
            typer.Option(
                default_value,
                *param_decls,
                help=help_text,
                case_sensitive=case_sensitive_val
                if case_sensitive_val is not None
                else True,
                min=min_val,
                max=max_val,
                show_default=show_default_val,
            ),
        )

    @classmethod
    def verbose_option(cls) -> OptionInfo:
        """Create --verbose/-v option from FlextConfig.verbose field metadata."""
        return cls.create_option("verbose")

    @classmethod
    def quiet_option(cls) -> OptionInfo:
        """Create --quiet/-q option from FlextConfig.quiet field metadata."""
        return cls.create_option("quiet")

    @classmethod
    def debug_option(cls) -> OptionInfo:
        """Create --debug/-d option from FlextConfig.debug field metadata."""
        return cls.create_option("debug")

    @classmethod
    def trace_option(cls) -> OptionInfo:
        """Create --trace/-t option from FlextConfig.trace field metadata."""
        return cls.create_option("trace")

    @classmethod
    def log_level_option(cls) -> OptionInfo:
        """Create --log-level/-L option from FlextConfig.log_level field metadata."""
        return cls.create_option("log_level")

    @classmethod
    def log_format_option(cls) -> OptionInfo:
        """Create --log-format option from FlextConfig.log_verbosity field metadata."""
        return cls.create_option("log_verbosity")

    @classmethod
    def output_format_option(
        cls,
    ) -> OptionInfo:
        """Create --output-format/-o option from FlextConfig.output_format field metadata."""
        return cls.create_option("output_format")

    @classmethod
    def no_color_option(cls) -> OptionInfo:
        """Create --no-color option from FlextConfig.no_color field metadata."""
        return cls.create_option("no_color")

    @classmethod
    def config_file_option(cls) -> OptionInfo:
        """Create --config-file/-c option from FlextConfig.config_file field metadata."""
        return cls.create_option("config_file")

    @classmethod
    def get_all_common_params(cls) -> dict[str, OptionInfo]:
        """Get all common CLI parameters as typer.Option objects.

        Returns dict[str, OptionInfo] mapping parameter names to typer.Option objects auto-generated
        from FlextCliConfig field metadata. Sorted by priority from CLI_PARAM_REGISTRY.

        Returns:
            Dict of parameter name -> typer.Option(...)

        Example:
            >>> params = FlextCliCommonParams.get_all_common_params()
            >>> params["verbose"]  # typer.Option(False, "--verbose", "-v", help="...")

        """
        reg = cls._reg
        default_priority = FlextCliConstants.PriorityDefaults.DEFAULT_PRIORITY
        param_fields = sorted(
            cls.CLI_PARAM_REGISTRY.items(),
            key=lambda x: int(str(x[1].get(reg.KEY_PRIORITY, default_priority))),
        )

        return {
            field_name: cls.create_option(field_name) for field_name, _ in param_fields
        }

    @classmethod
    def apply_to_config(
        cls,
        config: FlextCliConfig,
        *,
        verbose: bool | None = None,
        quiet: bool | None = None,
        debug: bool | None = None,
        trace: bool | None = None,
        log_level: str | None = None,
        log_format: str | None = None,
        output_format: str | None = None,
        no_color: bool | None = None,
    ) -> FlextResult[FlextCliConfig]:
        """Apply CLI parameter values to FlextConfig instance.

        This method updates the config with CLI parameter values, following precedence:
        CLI parameters > ENV variables > .env file > defaults

        Args:
            config: FlextCliConfig instance to update
            verbose: Verbose flag from CLI
            quiet: Quiet flag from CLI
            debug: Debug flag from CLI
            trace: Trace flag from CLI
            log_level: Log level from CLI
            log_format: Log format from CLI
            output_format: Output format from CLI
            no_color: No color flag from CLI

        Returns:
            FlextResult[FlextCliConfig]: Updated config or error

        """
        err = FlextCliConstants.CliParamsErrorMessages
        defs = cls._defs
        try:
            # Apply parameters only if explicitly provided (not None)
            if verbose is not None:
                config.verbose = verbose
            if quiet is not None:
                config.quiet = quiet
            if debug is not None:
                config.debug = debug
            if trace is not None:
                if trace and not config.debug:
                    return FlextResult[FlextCliConfig].fail(err.TRACE_REQUIRES_DEBUG)
                config.trace = trace
            if log_level is not None:
                log_level_upper = log_level.upper()
                if log_level_upper not in FlextCliConstants.LOG_LEVELS_LIST:
                    valid = ", ".join(FlextCliConstants.LOG_LEVELS_LIST)
                    return FlextResult[FlextCliConfig].fail(
                        err.INVALID_LOG_LEVEL.format(log_level=log_level, valid=valid)
                    )
                # Cast to parent class type (FlextConstants.Settings.LogLevel)
                config.log_level = cast(
                    "FlextConstants.Settings.LogLevel", log_level_upper
                )
            if log_format is not None:
                log_format_lower = log_format.lower()
                if log_format_lower not in defs.VALID_LOG_FORMATS:
                    valid = ", ".join(defs.VALID_LOG_FORMATS)
                    return FlextResult[FlextCliConfig].fail(
                        err.INVALID_LOG_FORMAT.format(
                            log_format=log_format, valid=valid
                        )
                    )
                config.log_verbosity = cast(
                    "Literal['compact', 'detailed', 'full']", log_format_lower
                )
            if output_format is not None:
                output_format_lower = output_format.lower()
                if output_format_lower not in defs.VALID_OUTPUT_FORMATS:
                    valid = ", ".join(defs.VALID_OUTPUT_FORMATS)
                    return FlextResult[FlextCliConfig].fail(
                        err.INVALID_OUTPUT_FORMAT.format(
                            output_format=output_format, valid=valid
                        )
                    )
                # Cast to Literal type after validation
                config.output_format = cast(
                    "Literal['json', 'yaml', 'csv', 'table', 'plain']",
                    output_format_lower,
                )
            if no_color is not None:
                config.no_color = no_color

            return FlextResult[FlextCliConfig].ok(config)

        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                err.APPLY_PARAMS_FAILED.format(error=e)
            )

    @classmethod
    def configure_logger(
        cls,
        config: FlextCliConfig,
    ) -> FlextResult[None]:
        """Configure FlextLogger based on config parameters.

        NOTE: FlextLogger uses structlog which configures logging globally.
        The log_level from FlextCliConfig is used during logger initialization.
        This method validates the configuration but doesn't modify the logger directly.

        Args:
            config: FlextCliConfig with logging configuration

        Returns:
            FlextResult[None]: Success or error

        """
        err = FlextCliConstants.CliParamsErrorMessages
        try:
            log_level_upper = config.log_level.upper()

            if log_level_upper not in FlextCliConstants.LOG_LEVELS_LIST:
                valid = ", ".join(FlextCliConstants.LOG_LEVELS_LIST)
                return FlextResult[None].fail(
                    err.INVALID_LOG_LEVEL.format(log_level=log_level_upper, valid=valid)
                )

            # FlextLogger configuration is done via FlextConfig at initialization
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(err.CONFIGURE_LOGGER_FAILED.format(error=e))

    @classmethod
    def create_decorator(
        cls,
    ) -> Callable[
        [Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]],
        Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue],
    ]:
        """Create decorator to validate common CLI parameters are used.

        By default, ALL parameters are included and this is MANDATORY.
        Attempting to disable enforcement will raise an error unless explicitly allowed.

        NOTE: This decorator validates parameter enforcement.
        The decorated function MUST include common parameters in its signature using
        the *_option() methods:

        Returns:
            Callable: Decorator function

        Raises:
            SystemExit: If enforcement is enabled and parameters are disabled

        Example:
            ```python
            @app.command()
            @FlextCliCommonParams.create_decorator()
            def my_command(
                name: str,
                verbose: bool = FlextCliCommonParams.verbose_option(),
                debug: bool = FlextCliCommonParams.debug_option(),
                log_level: str = FlextCliCommonParams.log_level_option(),
                output_format: str = FlextCliCommonParams.output_format_option(),
                # ... other common params using *_option() methods
            ) -> None:
                # Common parameters automatically available with full metadata
                config = FlextCliConfig()
                FlextCliCommonParams.apply_to_config(
                    config,
                    verbose=verbose,
                    debug=debug,
                    log_level=log_level,
                    output_format=output_format,
                )
            ```

        """

        def decorator(
            func: Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue],
        ) -> Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]:
            # Validate enforcement
            validation = cls.validate_enabled()
            if validation.is_failure and cls._enforcement_mode:
                # In enforcement mode, any attempt to disable params is an error
                sys.exit(FlextCliConstants.ExitCodes.FAILURE)

            # For Typer, parameters are defined in function signature
            # This decorator validates enforcement only
            return func

        return decorator


__all__ = [
    "FlextCliCommonParams",
]
