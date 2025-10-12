"""FLEXT CLI Common Parameters - Auto-generated from FlextCore.Config properties.

Provides standardized CLI parameters that MUST be available in all CLI commands.
Parameters are auto-generated from FlextCliConfig Pydantic field metadata.

These parameters are ENABLED BY DEFAULT and cannot be disabled without error.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar, TypeVar, cast, get_args, get_origin

import typer
from flext_core import FlextCore

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants

# Type variable for create_option method return type
T = TypeVar("T")


class FlextCliCommonParams:
    """Common CLI parameters auto-generated from FlextCore.Config field metadata.

    Provides standardized parameter group integrated with FlextCore.Config and FlextCore.Logger.
    These parameters are enabled by default and enforced across all CLI commands.

    All parameter definitions are automatically extracted from FlextCliConfig Pydantic fields:
    - Descriptions from Field(description=...)
    - Defaults from Field(default=...)
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

    # CLI Parameter Metadata Registry
    # Maps field names to CLI-specific metadata (short flags, choices, priority)
    CLI_PARAM_REGISTRY: ClassVar[dict[str, dict[str, Any]]] = {
        "verbose": {"short": "v", "priority": 1},
        "quiet": {"short": "q", "priority": 2},
        "debug": {"short": "d", "priority": 3},
        "trace": {"short": "t", "priority": 4},
        "log_level": {
            "short": "L",
            "priority": 5,
            "choices": FlextCliConstants.LOG_LEVELS_LIST,
            "case_sensitive": False,
        },
        "log_verbosity": {
            "priority": 6,
            "choices": ["compact", "detailed", "full"],
            "case_sensitive": False,
            "field_name_override": "log-format",  # CLI uses --log-format
        },
        "output_format": {
            "short": "o",
            "priority": 7,
            "choices": ["table", "json", "yaml", "csv", "plain"],
            "case_sensitive": False,
        },
        "no_color": {"priority": 8},
        "config_file": {"short": "c", "priority": 9},
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
    def validate_enabled(cls) -> FlextCore.Result[None]:
        """Validate that common parameters are enabled.

        Returns:
            FlextCore.Result[None]: Success if enabled, failure if disabled in enforcement mode.

        """
        if not cls._params_enabled and cls._enforcement_mode:
            return FlextCore.Result[None].fail(
                "Common CLI parameters are mandatory and cannot be disabled. "
                "All CLI commands must support --verbose, --quiet, --debug, --log-level, etc."
            )
        return FlextCore.Result[None].ok(None)

    @classmethod
    def create_option(cls, field_name: str) -> object:
        """Create typer.Option() from FlextCliConfig field metadata.

        Auto-generates typer.Option() with all metadata from Pydantic Field:
        - Default value from field default
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
        # Get Pydantic field metadata
        fields = FlextCliConfig.model_fields
        schema = FlextCliConfig.model_json_schema()

        if field_name not in fields:
            msg = f"Field '{field_name}' not found in FlextCliConfig"
            raise ValueError(msg)

        field_info = fields[field_name]
        field_schema = schema["properties"].get(field_name, {})
        param_meta = cls.CLI_PARAM_REGISTRY.get(field_name, {})

        # Get base type (handle Optional/Union types)
        field_type = field_info.annotation
        origin = get_origin(field_type)

        if origin is type(None) or (
            hasattr(field_type, "__args__") and type(None) in get_args(field_type)
        ):
            # Extract non-None type from Optional
            args = [a for a in get_args(field_type) if a is not type(None)]
            field_type = args[0] if args else str

        # Build parameter declarations (--param-name, -short)
        cli_name = param_meta.get("field_name_override", field_name)
        option_name = f"--{cli_name.replace('_', '-')}"
        param_decls = [option_name]

        if "short" in param_meta:
            param_decls.insert(0, f"-{param_meta['short']}")

        # Get default value
        default_value = field_info.default
        if default_value is None:
            # For Optional fields, default to None
            pass
        elif (
            hasattr(default_value, "__class__")
            and default_value.__class__.__name__ == "PydanticUndefinedType"
        ):
            default_value = None

        # Build help text from field description
        help_text = field_info.description or f"Set {field_name}"

        # Enhance help text with choices
        if "choices" in param_meta:
            choices_str = ", ".join(str(c) for c in param_meta["choices"])
            help_text += f" (choices: {choices_str})"

        # Enhance help text with constraints
        if "minimum" in field_schema and "maximum" in field_schema:
            help_text += (
                f" [range: {field_schema['minimum']}-{field_schema['maximum']}]"
            )

        # Build typer.Option kwargs
        option_kwargs: dict[str, Any] = {
            "help": help_text,
        }

        # Add case sensitivity
        if "case_sensitive" in param_meta:
            option_kwargs["case_sensitive"] = param_meta["case_sensitive"]

        # Add numeric constraints
        if "minimum" in field_schema:
            option_kwargs["min"] = field_schema["minimum"]
        if "maximum" in field_schema:
            option_kwargs["max"] = field_schema["maximum"]

        # Add show_default for non-None defaults
        if default_value is not None:
            option_kwargs["show_default"] = True

        # Create and return typer.Option with param_decls and default
        return typer.Option(default_value, *param_decls, **option_kwargs)

    @classmethod
    def verbose_option(cls) -> bool:
        """Create --verbose/-v option from FlextCore.Config.verbose field metadata."""
        return cast("bool", cls.create_option("verbose"))

    @classmethod
    def quiet_option(cls) -> bool:
        """Create --quiet/-q option from FlextCore.Config.quiet field metadata."""
        return cast("bool", cls.create_option("quiet"))

    @classmethod
    def debug_option(cls) -> bool:
        """Create --debug/-d option from FlextCore.Config.debug field metadata."""
        return cast("bool", cls.create_option("debug"))

    @classmethod
    def trace_option(cls) -> bool:
        """Create --trace/-t option from FlextCore.Config.trace field metadata."""
        return cast("bool", cls.create_option("trace"))

    @classmethod
    def log_level_option(cls) -> str:
        """Create --log-level/-L option from FlextCore.Config.log_level field metadata."""
        return cast("str", cls.create_option("log_level"))

    @classmethod
    def log_format_option(cls) -> str:
        """Create --log-format option from FlextCore.Config.log_verbosity field metadata."""
        return cast("str", cls.create_option("log_verbosity"))

    @classmethod
    def output_format_option(cls) -> str:
        """Create --output-format/-o option from FlextCore.Config.output_format field metadata."""
        return cast("str", cls.create_option("output_format"))

    @classmethod
    def no_color_option(cls) -> bool:
        """Create --no-color option from FlextCore.Config.no_color field metadata."""
        return cast("bool", cls.create_option("no_color"))

    @classmethod
    def config_file_option(cls) -> Path | None:
        """Create --config-file/-c option from FlextCore.Config.config_file field metadata."""
        return cast("Path | None", cls.create_option("config_file"))

    @classmethod
    def get_all_common_params(cls) -> dict[str, Any]:
        """Get all common CLI parameters as typer.Option objects.

        Returns dict mapping parameter names to typer.Option objects auto-generated
        from FlextCliConfig field metadata. Sorted by priority from CLI_PARAM_REGISTRY.

        Returns:
            Dict of parameter name -> typer.Option(...)

        Example:
            >>> params = FlextCliCommonParams.get_all_common_params()
            >>> params["verbose"]  # typer.Option(False, "--verbose", "-v", help="...")

        """
        param_fields = sorted(
            cls.CLI_PARAM_REGISTRY.items(), key=lambda x: x[1].get("priority", 999)
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
    ) -> FlextCore.Result[FlextCliConfig]:
        """Apply CLI parameter values to FlextCore.Config instance.

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
            FlextCore.Result[FlextCliConfig]: Updated config or error

        """
        try:
            # Apply parameters only if explicitly provided (not None)
            if verbose is not None:
                config.verbose = verbose
            if quiet is not None:
                config.quiet = quiet
            if debug is not None:
                config.debug = debug
            if trace is not None:
                # Validate trace requires debug
                if trace and not config.debug:
                    return FlextCore.Result[FlextCliConfig].fail(
                        "Trace mode requires debug mode to be enabled. Use --debug --trace together."
                    )
                config.trace = trace
            if log_level is not None:
                # Validate log level
                if log_level.upper() not in FlextCliConstants.LOG_LEVELS_LIST:
                    valid = ", ".join(FlextCliConstants.LOG_LEVELS_LIST)
                    return FlextCore.Result[FlextCliConfig].fail(
                        f"Invalid log level: {log_level}. Must be one of: {valid}"
                    )
                config.log_level = log_level.upper()
            if log_format is not None:
                # Validate log format
                valid_formats = ["compact", "detailed", "full"]
                if log_format.lower() not in valid_formats:
                    valid = ", ".join(valid_formats)
                    return FlextCore.Result[FlextCliConfig].fail(
                        f"Invalid log format: {log_format}. Must be one of: {valid}"
                    )
                config.log_verbosity = log_format.lower()
            if output_format is not None:
                # Validate output format
                valid_formats = ["table", "json", "yaml", "csv", "plain"]
                if output_format.lower() not in valid_formats:
                    valid = ", ".join(valid_formats)
                    return FlextCore.Result[FlextCliConfig].fail(
                        f"Invalid output format: {output_format}. Must be one of: {valid}"
                    )
                config.output_format = output_format.lower()
            if no_color is not None:
                config.no_color = no_color

            return FlextCore.Result[FlextCliConfig].ok(config)

        except Exception as e:
            return FlextCore.Result[FlextCliConfig].fail(
                f"Failed to apply CLI parameters to config: {e}"
            )

    @classmethod
    def configure_logger(
        cls,
        config: FlextCliConfig,
    ) -> FlextCore.Result[None]:
        """Configure FlextCore.Logger based on config parameters.

        NOTE: FlextCore.Logger uses structlog which configures logging globally.
        The log_level from FlextCliConfig is used during logger initialization.
        This method validates the configuration but doesn't modify the logger directly.

        Args:
            config: FlextCliConfig with logging configuration

        Returns:
            FlextCore.Result[None]: Success or error

        """
        try:
            # Validate log level is valid
            log_level = config.log_level.upper()

            if log_level not in FlextCliConstants.LOG_LEVELS_LIST:
                valid = ", ".join(FlextCliConstants.LOG_LEVELS_LIST)
                return FlextCore.Result[None].fail(
                    f"Invalid log level: {log_level}. Must be one of: {valid}"
                )

            # FlextCore.Logger configuration is done via FlextCore.Config at initialization
            # No runtime modification needed for structlog-based logger
            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(f"Failed to configure logger: {e}")

    @classmethod
    def create_decorator(
        cls,
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
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

        def decorator(func: Callable[..., object]) -> Callable[..., object]:
            # Validate enforcement
            validation = cls.validate_enabled()
            if validation.is_failure and cls._enforcement_mode:
                # In enforcement mode, any attempt to disable params is an error
                sys.exit(1)

            # For Typer, parameters are defined in function signature
            # This decorator validates enforcement only
            return func

        return decorator


__all__ = [
    "FlextCliCommonParams",
]
