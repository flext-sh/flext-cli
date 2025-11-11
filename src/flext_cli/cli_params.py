"""FLEXT CLI Common Parameters - Auto-generated from FlextConfig properties.

Provides standardized CLI parameters that MUST be available in all CLI commands.
Parameters are auto-generated from FlextCliConfig pydantic field metadata.

These parameters are ENABLED BY DEFAULT and cannot be disabled without error.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

import sys
from collections.abc import Callable
from typing import ClassVar, TypeVar

from flext_core import FlextConstants, FlextResult
from typer.models import OptionInfo

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels

# Type variable for generic decorator
F = TypeVar("F", bound=Callable[..., object])


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

        Delegate to OptionBuilder for reduced complexity (SOLID/SRP).

        Args:
            field_name: Name of field in FlextCliConfig

        Returns:
            typer.Option instance

        """
        builder = FlextCliModels.OptionBuilder(field_name, cls.CLI_PARAM_REGISTRY)
        return builder.build()

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
        """Apply CLI parameter values to FlextConfig instance.

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
            # Build params model from kwargs if not provided (backwards compatibility)
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

            # Railway pattern: apply bool → log level → log format → output format
            return (
                cls._apply_bool_params(config, params)
                .flat_map(lambda cfg: cls._apply_log_level(cfg, params))
                .flat_map(lambda cfg: cls._apply_log_format(cfg, params))
                .flat_map(lambda cfg: cls._apply_output_format(cfg, params))
            )
        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to apply CLI parameters: {e}"
            )

    @classmethod
    def _apply_bool_params(
        cls, config: FlextCliConfig, params: FlextCliModels.CliParamsConfig
    ) -> FlextResult[FlextCliConfig]:
        """Apply boolean CLI parameters to config."""
        bool_params = {
            "verbose": params.verbose,
            "quiet": params.quiet,
            "debug": params.debug,
            "trace": params.trace,
            "no_color": params.no_color,
        }
        for attr, value in bool_params.items():
            if value is not None:
                setattr(config, attr, value)
        return FlextResult[FlextCliConfig].ok(config)

    @classmethod
    def _apply_log_level(
        cls, config: FlextCliConfig, params: FlextCliModels.CliParamsConfig
    ) -> FlextResult[FlextCliConfig]:
        """Apply and validate log_level parameter."""
        if params.log_level is None:
            return FlextResult[FlextCliConfig].ok(config)

        normalized = params.log_level.upper()
        try:
            config.log_level = FlextConstants.Settings.LogLevel(normalized)
        except ValueError:
            valid_levels = FlextCliConstants.LOG_LEVELS_LIST
            return FlextResult[FlextCliConfig].fail(
                f"invalid log level: {params.log_level}. valid options: {', '.join(valid_levels)}"
            )
        return FlextResult[FlextCliConfig].ok(config)

    @classmethod
    def _apply_validated_param(
        cls,
        config: FlextCliConfig,
        param_value: str | None,
        valid_values: list[str],
        config_attr: str,
        param_name: str,
    ) -> FlextResult[FlextCliConfig]:
        """Generic method to validate and apply a parameter to config.

        Args:
            config: Configuration object to update
            param_value: Parameter value to validate (None means skip)
            valid_values: List of valid values for validation
            config_attr: Config attribute name to set
            param_name: Parameter name for error messages

        Returns:
            FlextResult with updated config or error

        """
        if param_value is None:
            return FlextResult[FlextCliConfig].ok(config)

        if param_value not in valid_values:
            return FlextResult[FlextCliConfig].fail(
                f"invalid {param_name}: {param_value}. valid options: {', '.join(valid_values)}"
            )

        setattr(config, config_attr, param_value)
        return FlextResult[FlextCliConfig].ok(config)

    @classmethod
    def _apply_log_format(
        cls, config: FlextCliConfig, params: FlextCliModels.CliParamsConfig
    ) -> FlextResult[FlextCliConfig]:
        """Apply and validate log_format parameter."""
        return cls._apply_validated_param(
            config=config,
            param_value=params.log_format,
            valid_values=FlextCliConstants.CliParamsDefaults.VALID_LOG_FORMATS,
            config_attr="log_verbosity",
            param_name="log format",
        )

    @classmethod
    def _apply_output_format(
        cls, config: FlextCliConfig, params: FlextCliModels.CliParamsConfig
    ) -> FlextResult[FlextCliConfig]:
        """Apply and validate output_format parameter."""
        return cls._apply_validated_param(
            config=config,
            param_value=params.output_format,
            valid_values=FlextCliConstants.CliParamsDefaults.VALID_OUTPUT_FORMATS,
            config_attr="output_format",
            param_name="output format",
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
    ) -> Callable[[F], F]:
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
                log_level: str = FlextCliCommonParams.create_option("log_level"),
                output_format: str = FlextCliCommonParams.create_option(
                    "output_format"
                ),
                # ... other common params using create_option() method
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

        def decorator(func: F) -> F:
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
