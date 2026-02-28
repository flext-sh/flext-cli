"""FLEXT CLI Common Parameters - Auto-generated from FlextSettings properties."""

from __future__ import annotations

import sys
from collections.abc import Callable, Mapping
from typing import ClassVar

from flext_core import r
from rich.errors import ConsoleError, LiveError, StyleError
from typer.models import OptionInfo

from flext_cli import FlextCliSettings, c, m, p, u


class FlextCliCommonParams:
    """Common CLI parameters auto-generated from FlextSettings field metadata.

    Business Rules:
    ───────────────
    1. Parameters MUST be auto-generated from FlextCliSettings Pydantic fields
    2. Parameters MUST be enabled by default (cannot be disabled without error)
    3. Parameter types MUST match FlextCliSettings field types
    4. Choices MUST be validated against allowed values
    5. Boolean parameters automatically become Typer flags
    """

    CLI_PARAM_REGISTRY: ClassVar[
        Mapping[str, Mapping[str, str | int | bool | list[str]]]
    ] = {
        "verbose": {
            c.Cli.CliParamsRegistry.KEY_SHORT: c.Cli.CliParamsRegistry.SHORT_FLAG_VERBOSE,
            c.Cli.CliParamsRegistry.KEY_PRIORITY: c.Cli.CliParamsRegistry.PRIORITY_VERBOSE,
        },
        "quiet": {
            c.Cli.CliParamsRegistry.KEY_SHORT: c.Cli.CliParamsRegistry.SHORT_FLAG_QUIET,
            c.Cli.CliParamsRegistry.KEY_PRIORITY: c.Cli.CliParamsRegistry.PRIORITY_QUIET,
        },
        "debug": {
            c.Cli.CliParamsRegistry.KEY_SHORT: c.Cli.CliParamsRegistry.SHORT_FLAG_DEBUG,
            c.Cli.CliParamsRegistry.KEY_PRIORITY: c.Cli.CliParamsRegistry.PRIORITY_DEBUG,
        },
        "trace": {
            c.Cli.CliParamsRegistry.KEY_SHORT: c.Cli.CliParamsRegistry.SHORT_FLAG_TRACE,
            c.Cli.CliParamsRegistry.KEY_PRIORITY: c.Cli.CliParamsRegistry.PRIORITY_TRACE,
        },
        "cli_log_level": {
            c.Cli.CliParamsRegistry.KEY_SHORT: c.Cli.CliParamsRegistry.SHORT_FLAG_LOG_LEVEL,
            c.Cli.CliParamsRegistry.KEY_PRIORITY: c.Cli.CliParamsRegistry.PRIORITY_LOG_LEVEL,
            c.Cli.CliParamsRegistry.KEY_CHOICES: c.Cli.Lists.LOG_LEVELS_LIST,
            c.Cli.CliParamsRegistry.KEY_CASE_SENSITIVE: c.Cli.CliParamsRegistry.CASE_INSENSITIVE,
            # CLI param name is --log-level, maps to cli_log_level field
            c.Cli.CliParamsRegistry.KEY_FIELD_NAME_OVERRIDE: "log_level",
        },
        "log_verbosity": {
            c.Cli.CliParamsRegistry.KEY_PRIORITY: c.Cli.CliParamsRegistry.PRIORITY_LOG_FORMAT,
            c.Cli.CliParamsRegistry.KEY_CHOICES: c.Cli.Lists.LOG_LEVELS_LIST,
            c.Cli.CliParamsRegistry.KEY_CASE_SENSITIVE: c.Cli.CliParamsRegistry.CASE_INSENSITIVE,
            c.Cli.CliParamsRegistry.KEY_FIELD_NAME_OVERRIDE: c.Cli.CliParamsRegistry.LOG_FORMAT_OVERRIDE,
        },
        "output_format": {
            c.Cli.CliParamsRegistry.KEY_SHORT: c.Cli.CliParamsRegistry.SHORT_FLAG_OUTPUT_FORMAT,
            c.Cli.CliParamsRegistry.KEY_PRIORITY: c.Cli.CliParamsRegistry.PRIORITY_OUTPUT_FORMAT,
            c.Cli.CliParamsRegistry.KEY_CHOICES: list(
                c.Cli.ValidationLists.OUTPUT_FORMATS,
            ),
            c.Cli.CliParamsRegistry.KEY_CASE_SENSITIVE: c.Cli.CliParamsRegistry.CASE_INSENSITIVE,
        },
        "no_color": {
            c.Cli.CliParamsRegistry.KEY_PRIORITY: c.Cli.CliParamsRegistry.PRIORITY_NO_COLOR,
        },
        "config_file": {
            c.Cli.CliParamsRegistry.KEY_SHORT: c.Cli.CliParamsRegistry.SHORT_FLAG_CONFIG_FILE,
            c.Cli.CliParamsRegistry.KEY_PRIORITY: c.Cli.CliParamsRegistry.PRIORITY_CONFIG_FILE,
        },
    }

    _params_enabled: bool = True
    _enforcement_mode: bool = True

    @classmethod
    def disable_enforcement(cls) -> None:
        """Disable enforcement mode (for testing only)."""
        cls._enforcement_mode = False

    @classmethod
    def enable_enforcement(cls) -> None:
        """Enable enforcement mode (default)."""
        cls._enforcement_mode = True

    @classmethod
    def validate_enabled(cls) -> r[bool]:
        """Validate that common parameters are enabled."""
        if not cls._params_enabled and cls._enforcement_mode:
            return r[bool].fail(c.Cli.CliParamsErrorMessages.PARAMS_MANDATORY)
        return r[bool].ok(value=True)

    @classmethod
    def create_option(cls, field_name: str) -> OptionInfo:
        """Create typer.Option() from FlextCliSettings field metadata."""
        if field_name not in cls.CLI_PARAM_REGISTRY:
            msg = f"Field '{field_name}' not found in CLI parameter registry"
            raise ValueError(msg)
        return m.Cli.OptionBuilder(field_name, cls.CLI_PARAM_REGISTRY).build()

    @classmethod
    def get_all_common_params(cls) -> Mapping[str, OptionInfo]:
        """Get all common CLI parameters sorted by priority."""
        default_priority = c.Cli.CliDefaults.DEFAULT_PRIORITY
        param_fields = sorted(
            cls.CLI_PARAM_REGISTRY.items(),
            key=lambda x: int(
                str(x[1].get(c.Cli.CliParamsRegistry.KEY_PRIORITY, default_priority)),
            ),
        )
        return {name: cls.create_option(name) for name, _ in param_fields}

    @staticmethod
    def _opt_bool(kwargs: Mapping[str, bool | str | None], key: str) -> bool | None:
        """Extract optional bool from kwargs."""
        v = kwargs.get(key)
        return bool(v) if v is not None else None

    @staticmethod
    def _opt_str(kwargs: Mapping[str, bool | str | None], key: str) -> str | None:
        """Extract optional str from kwargs."""
        v = kwargs.get(key)
        return str(v) if v is not None else None

    @classmethod
    def _build_params_from_kwargs(
        cls,
        kwargs: Mapping[str, bool | str | None],
    ) -> p.Cli.CliParamsConfigProtocol:
        """Build CLI params protocol instance from keyword arguments."""
        return m.Cli.CliParamsConfig(
            verbose=cls._opt_bool(kwargs, "verbose"),
            quiet=cls._opt_bool(kwargs, "quiet"),
            debug=cls._opt_bool(kwargs, "debug"),
            trace=cls._opt_bool(kwargs, "trace"),
            log_level=cls._opt_str(kwargs, "log_level"),
            log_format=cls._opt_str(kwargs, "log_format"),
            output_format=cls._opt_str(kwargs, "output_format"),
            no_color=cls._opt_bool(kwargs, "no_color"),
        )

    @classmethod
    def _resolve_params(
        cls,
        params: p.Cli.CliParamsConfigProtocol | None,
        kwargs: Mapping[str, bool | str | None],
    ) -> p.Cli.CliParamsConfigProtocol:
        """Resolve explicit params or build from kwargs."""
        if params is not None:
            return params
        return cls._build_params_from_kwargs(kwargs)

    @classmethod
    def _apply_param_setters(
        cls,
        config: FlextCliSettings,
        params: p.Cli.CliParamsConfigProtocol,
    ) -> r[FlextCliSettings]:
        """Apply all parameter setter stages to config."""
        bool_result = cls._set_bool_params(config, params)
        if bool_result.is_failure:
            return r[FlextCliSettings].fail(
                bool_result.error or "Boolean parameter setting failed",
            )

        log_level_result = cls._set_log_level(config, params)
        if log_level_result.is_failure:
            return log_level_result

        format_result = cls._set_format_params(config, params)
        if format_result.is_failure:
            return format_result

        return r[FlextCliSettings].ok(config)

    @classmethod
    def apply_to_config(
        cls,
        config: FlextCliSettings,
        params: p.Cli.CliParamsConfigProtocol | None = None,
        **kwargs: bool | str | None,
    ) -> r[FlextCliSettings]:
        """Apply CLI parameter values to FlextSettings using Pydantic validation.

        Business Rule: Applies CLI parameter values with Pydantic validation.
        Trace mode requires debug mode to be enabled.
        """
        try:
            params_to_use = cls._resolve_params(params, kwargs)
            return cls._apply_param_setters(config, params_to_use)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[FlextCliSettings].fail(f"Failed to apply CLI parameters: {e}")

    @classmethod
    def _set_bool_params(
        cls,
        config: FlextCliSettings,
        params: p.Cli.CliParamsConfigProtocol,
    ) -> r[bool]:
        """Set boolean parameters with validation via model_copy."""
        if params.trace is not None and params.trace:
            will_be_debug = params.debug if params.debug is not None else config.debug
            if not will_be_debug:
                return r[bool].fail("Trace mode requires debug mode to be enabled")
        update_data: dict[str, bool] = {}
        for field in ("verbose", "quiet", "debug", "trace", "no_color"):
            val = getattr(params, field, None)
            if val is not None:
                update_data[field] = val
        if update_data:
            validated_config = config.model_copy(update=update_data)
            for key in update_data:
                setattr(config, key, getattr(validated_config, key))
        return r[bool].ok(value=True)

    @classmethod
    def _set_log_level(
        cls,
        config: FlextCliSettings,
        params: p.Cli.CliParamsConfigProtocol,
    ) -> r[FlextCliSettings]:
        """Set cli_log_level with enum conversion."""
        if params.log_level is None:
            return r[FlextCliSettings].ok(config)
        try:
            config.cli_log_level = c.Cli.Settings.LogLevel(params.log_level.upper())
            return r[FlextCliSettings].ok(config)
        except ValueError:
            valid = ", ".join(c.Cli.Lists.LOG_LEVELS_LIST)
            return r[FlextCliSettings].fail(
                f"invalid log level: {params.log_level}. valid options: {valid}",
            )

    @classmethod
    def _set_format_params(
        cls,
        config: FlextCliSettings,
        params: p.Cli.CliParamsConfigProtocol,
    ) -> r[FlextCliSettings]:
        """Set log_format and output_format with validation."""
        if params.log_format is not None:
            if params.log_format not in c.Cli.CliParamsDefaults.VALID_LOG_FORMATS:
                valid = ", ".join(c.Cli.CliParamsDefaults.VALID_LOG_FORMATS)
                return r[FlextCliSettings].fail(
                    f"invalid log format: {params.log_format}. valid: {valid}",
                )
            config.log_verbosity = params.log_format
        if params.output_format is not None:
            validated_result = u.Cli.CliValidation.v_format(params.output_format)
            if validated_result.is_failure:
                valid = ", ".join(c.Cli.CliParamsDefaults.VALID_OUTPUT_FORMATS)
                return r[FlextCliSettings].fail(
                    f"invalid output format: {params.output_format}. valid: {valid}",
                )
            config = config.model_copy(update={"output_format": validated_result.value})
        return r[FlextCliSettings].ok(config)

    @classmethod
    def configure_logger(
        cls,
        config: FlextCliSettings,
    ) -> r[bool]:
        """Configure FlextLogger based on config parameters.

        NOTE: FlextLogger uses structlog which configures logging globally.
        The log_level from FlextCliSettings is used during logger initialization.
        This method validates the configuration but doesn't modify the logger directly.

        Args:
            config: FlextCliSettings with logging configuration

        Returns:
            r[bool]: True if logger configured successfully, failure on error

        """
        try:
            # config.cli_log_level is str with default, never None
            log_level_upper = config.cli_log_level.upper()

            if log_level_upper not in c.Cli.Lists.LOG_LEVELS_LIST:
                valid = ", ".join(c.Cli.Lists.LOG_LEVELS_LIST)
                return r[bool].fail(
                    c.Cli.CliParamsErrorMessages.INVALID_LOG_LEVEL.format(
                        log_level=log_level_upper,
                        valid=valid,
                    ),
                )

            # FlextLogger configuration is done via FlextSettings at initialization
            return r[bool].ok(value=True)

        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[bool].fail(
                c.Cli.CliParamsErrorMessages.CONFIGURE_LOGGER_FAILED.format(error=e),
            )

    @classmethod
    def create_decorator(
        cls,
    ) -> Callable[
        [p.Cli.CliCommandFunction],
        p.Cli.CliCommandFunction,
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

        def decorator(
            func: p.Cli.CliCommandFunction,
        ) -> p.Cli.CliCommandFunction:
            # Validate enforcement
            validation = cls.validate_enabled()
            if validation.is_failure and cls._enforcement_mode:
                # In enforcement mode, any attempt to disable params is an error
                sys.exit(c.Cli.ExitCodes.FAILURE)

            # For Typer, parameters are defined in function signature
            # This decorator validates enforcement only
            return func

        return decorator


__all__ = [
    "FlextCliCommonParams",
]
