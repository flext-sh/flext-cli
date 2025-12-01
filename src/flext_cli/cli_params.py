"""FLEXT CLI Common Parameters - Auto-generated from FlextConfig properties.

Provides standardized CLI parameters that MUST be available in all CLI commands.
Parameters are auto-generated from FlextCliConfig pydantic field metadata.

These parameters are ENABLED BY DEFAULT and cannot be disabled without error.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import ClassVar

from flext_core import FlextConstants, FlextResult, FlextTypes
from typer.models import OptionInfo

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_cli.protocols import FlextCliProtocols
from flext_cli.utilities import FlextCliUtilities

# Direct type references - use FlextCliProtocols.Cli.CliCommandFunction directly


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

    # Registry allows list[str] for choices
    CLI_PARAM_REGISTRY: ClassVar[dict[str, dict[str, str | int | bool | list[str]]]] = {
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
        "cli_log_level": {
            _reg.KEY_SHORT: _reg.SHORT_FLAG_LOG_LEVEL,
            _reg.KEY_PRIORITY: _reg.PRIORITY_LOG_LEVEL,
            _reg.KEY_CHOICES: FlextCliConstants.Lists.LOG_LEVELS_LIST,
            _reg.KEY_CASE_SENSITIVE: _reg.CASE_INSENSITIVE,
            _reg.KEY_FIELD_NAME_OVERRIDE: "log_level",  # CLI param name is --log-level, maps to cli_log_level field
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
    def validate_enabled(cls) -> FlextResult[bool]:
        """Validate that common parameters are enabled.

        Returns:
            FlextResult[bool]: True if enabled, failure if disabled in enforcement mode.

        """
        err = FlextCliConstants.CliParamsErrorMessages
        if not cls._params_enabled and cls._enforcement_mode:
            return FlextResult[bool].fail(err.PARAMS_MANDATORY)
        return FlextResult[bool].ok(True)

    @classmethod
    def create_option(cls, field_name: str) -> OptionInfo:
        """Create typer.Option() from FlextCliConfig field metadata.

        Delegate to OptionBuilder for reduced complexity (SOLID/SRP).

        Args:
            field_name: Name of field in FlextCliConfig

        Returns:
            typer.Option instance

        Raises:
            ValueError: If field_name is not in CLI parameter registry

        """
        if field_name not in cls.CLI_PARAM_REGISTRY:
            raise ValueError(f"Field '{field_name}' not found in CLI parameter registry")

        builder = FlextCliModels.OptionBuilder(field_name, cls.CLI_PARAM_REGISTRY)
        built_option = builder.build()
        # OptionBuilder.build() returns object, cast to OptionInfo for type checker
        if isinstance(built_option, OptionInfo):
            return built_option
        # Fallback: create OptionInfo if builder returns something else
        return OptionInfo(default=None)

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
        default_priority = FlextCliConstants.DEFAULT_PRIORITY
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
        params: FlextCliModels.CliParamsConfig | None = None,
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
        """Apply CLI parameter values to FlextConfig using Pydantic validation.

        Args:
            config: FlextCliConfig instance to update
            params: CliParamsConfig model (preferred) or None to use keyword args
            verbose: Verbose flag (deprecated - use params)
            quiet: Quiet flag (deprecated - use params)
            debug: Debug flag (deprecated - use params)
            trace: Trace flag (deprecated - use params)
            log_level: Log level (deprecated - use params)
            log_format: Log format (deprecated - use params)
            output_format: Output format (deprecated - use params)
            no_color: No color flag (deprecated - use params)

        Returns:
            FlextResult[FlextCliConfig]: Updated config or error

        """
        try:
            # Build params model from kwargs if not provided (Pydantic validates automatically)
            if params is None:
                params = FlextCliModels.CliParamsConfig(
                    verbose=verbose,
                    quiet=quiet,
                    debug=debug,
                    trace=trace,
                    log_level=log_level,
                    log_format=log_format,
                    output_format=output_format,
                    no_color=no_color,
                )

            # Apply all parameters - extracted helpers to reduce complexity
            bool_result = cls._set_bool_params(config, params)
            if bool_result.is_failure:
                return FlextResult[FlextCliConfig].fail(
                    bool_result.error or "Boolean parameter setting failed",
                )

            log_level_result = cls._set_log_level(config, params)
            if log_level_result.is_failure:
                return log_level_result

            format_result = cls._set_format_params(config, params)
            if format_result.is_failure:
                return format_result

            return FlextResult[FlextCliConfig].ok(config)

        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to apply CLI parameters: {e}",
            )

    @classmethod
    def _set_bool_params(
        cls,
        config: FlextCliConfig,
        params: FlextCliModels.CliParamsConfig,
    ) -> FlextResult[bool]:
        """Set boolean parameters with validation.

        Uses model_copy to validate all updates together, then applies them to the
        original config object. This ensures validators see the final state rather
        than intermediate states during individual field assignments.

        Returns:
            FlextResult[bool]: True if successful, error if trace=True without debug=True

        """
        # VALIDATION: trace mode requires debug mode (from FlextConfig)
        # Check BEFORE applying to avoid invalid state
        # If trace is being set, check if debug will be enabled
        if params.trace is not None and params.trace:
            # Trace requires debug - check if debug is being set or already enabled
            will_be_debug = params.debug if params.debug is not None else config.debug
            if not will_be_debug:
                return FlextResult[bool].fail(
                    "Trace mode requires debug mode to be enabled",
                )

        # Update all attributes at once using model_copy to avoid triggering
        # validate_assignment for each individual field (which would see intermediate states)
        # Then update the original config object's attributes
        # Use mutable dict for building updates
        update_data: dict[str, FlextTypes.GeneralValueType] = {}
        if params.verbose is not None:
            update_data["verbose"] = params.verbose
        if params.quiet is not None:
            update_data["quiet"] = params.quiet
        if params.debug is not None:
            update_data["debug"] = params.debug
        if params.trace is not None:
            update_data["trace"] = params.trace
        if params.no_color is not None:
            update_data["no_color"] = params.no_color

        if update_data:
            # Validate all updates together using model_copy, then apply to original
            # This ensures validators see the final state, not intermediate states
            validated_config = config.model_copy(update=update_data)
            # Update original config object's attributes from validated instance
            for key in update_data:
                setattr(config, key, getattr(validated_config, key))

        return FlextResult[bool].ok(True)

    @classmethod
    def _set_log_level(
        cls,
        config: FlextCliConfig,
        params: FlextCliModels.CliParamsConfig,
    ) -> FlextResult[FlextCliConfig]:
        """Set cli_log_level with enum conversion."""
        if params.log_level is None:
            return FlextResult[FlextCliConfig].ok(config)

        normalized = params.log_level.upper()
        try:
            config.cli_log_level = FlextConstants.Settings.LogLevel(normalized)
            return FlextResult[FlextCliConfig].ok(config)
        except ValueError:
            valid = FlextCliConstants.LOG_LEVELS_LIST
            return FlextResult[FlextCliConfig].fail(
                f"invalid log level: {params.log_level}. valid options: {', '.join(valid)}",
            )

    @classmethod
    def _set_format_params(
        cls,
        config: FlextCliConfig,
        params: FlextCliModels.CliParamsConfig,
    ) -> FlextResult[FlextCliConfig]:
        """Set log_format and output_format with validation."""
        # log_format maps to log_verbosity
        if params.log_format is not None:
            if (
                params.log_format
                not in FlextCliConstants.CliParamsDefaults.VALID_LOG_FORMATS
            ):
                valid = FlextCliConstants.CliParamsDefaults.VALID_LOG_FORMATS
                return FlextResult[FlextCliConfig].fail(
                    f"invalid log format: {params.log_format}. valid options: {', '.join(valid)}",
                )
            config.log_verbosity = params.log_format

        # output_format - use validator that returns proper Literal type
        if params.output_format is not None:
            validated_result = FlextCliUtilities.CliValidation.validate_output_format(
                params.output_format
            )
            if validated_result.is_failure:
                valid = FlextCliConstants.CliParamsDefaults.VALID_OUTPUT_FORMATS
                return FlextResult[FlextCliConfig].fail(
                    f"invalid output format: {params.output_format}. valid options: {', '.join(valid)}",
                )
            # Update config using model_copy to handle Literal type correctly
            validated_format = validated_result.unwrap()
            config = config.model_copy(update={"output_format": validated_format})

        return FlextResult[FlextCliConfig].ok(config)

    @classmethod
    def configure_logger(
        cls,
        config: FlextCliConfig,
    ) -> FlextResult[bool]:
        """Configure FlextLogger based on config parameters.

        NOTE: FlextLogger uses structlog which configures logging globally.
        The log_level from FlextCliConfig is used during logger initialization.
        This method validates the configuration but doesn't modify the logger directly.

        Args:
            config: FlextCliConfig with logging configuration

        Returns:
            FlextResult[bool]: True if logger configured successfully, failure on error

        """
        err = FlextCliConstants.CliParamsErrorMessages
        try:
            log_level_upper = config.cli_log_level.value.upper()

            if log_level_upper not in FlextCliConstants.LOG_LEVELS_LIST:
                valid = ", ".join(FlextCliConstants.LOG_LEVELS_LIST)
                return FlextResult[bool].fail(
                    err.INVALID_LOG_LEVEL.format(
                        log_level=log_level_upper,
                        valid=valid,
                    ),
                )

            # FlextLogger configuration is done via FlextConfig at initialization
            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(err.CONFIGURE_LOGGER_FAILED.format(error=e))

    @classmethod
    def create_decorator(
        cls,
    ) -> Callable[[FlextCliProtocols.Cli.CliCommandFunction], FlextCliProtocols.Cli.CliCommandFunction]:
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
                verbose: bool = FlextCliCommonParams.create_option("verbose"),
                debug: bool = FlextCliCommonParams.create_option("debug"),
                log_level: str = FlextCliCommonParams.create_option("cli_log_level"),
                output_format: str = FlextCliCommonParams.create_option(
                    "output_format"
                ),
                # ... other common params using create_option() method
            ) -> None:
                # Common parameters automatically available with full metadata
                config = FlextCliServiceBase.get_cli_config()
                FlextCliCommonParams.apply_to_config(
                    config,
                    verbose=verbose,
                    debug=debug,
                    log_level=log_level,
                    output_format=output_format,
                )
            ```

        """

        def decorator(func: FlextCliProtocols.Cli.CliCommandFunction) -> FlextCliProtocols.Cli.CliCommandFunction:
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
