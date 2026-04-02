"""FLEXT CLI Common Parameters - Auto-generated from FlextSettings properties."""

from __future__ import annotations

from collections.abc import Mapping

from typer.models import OptionInfo

from flext_cli import (
    FlextCliServiceBase,
    FlextCliSettings,
    c,
    m,
    p,
    t,
    u,
)
from flext_core import r


class FlextCliCommonParams(FlextCliServiceBase):
    """Common CLI parameters auto-generated from FlextSettings field metadata.

    Business Rules:
    ───────────────
    1. Parameters MUST be auto-generated from FlextCliSettings Pydantic fields
    2. Parameters MUST be enabled by default (cannot be disabled without error)
    3. Parameter types MUST match FlextCliSettings field types
    4. Choices MUST be validated against allowed values
    5. Boolean parameters automatically become Typer flags
    """

    @classmethod
    def _apply_param_setters(
        cls,
        config: FlextCliSettings,
        params: p.Cli.CliParamsConfig,
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
    def _build_params_from_kwargs(
        cls,
        kwargs: Mapping[str, bool | str | None],
    ) -> m.Cli.CliParamsConfig:
        """Build CLI params from keyword arguments (Pydantic model)."""
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
        params: p.Cli.CliParamsConfig | None,
        kwargs: Mapping[str, bool | str | None],
    ) -> m.Cli.CliParamsConfig:
        """Resolve explicit params or build from kwargs (returns Pydantic model)."""
        if params is not None:
            return (
                params
                if isinstance(params, m.Cli.CliParamsConfig)
                else cls._build_params_from_kwargs(kwargs)
            )
        return cls._build_params_from_kwargs(kwargs)

    @classmethod
    def _set_bool_params(
        cls,
        config: FlextCliSettings,
        params: p.Cli.CliParamsConfig,
    ) -> r[bool]:
        """Set boolean parameters with validation via model_copy."""
        if params.trace is not None and params.trace:
            will_be_debug = params.debug if params.debug is not None else config.debug
            if not will_be_debug:
                return r[bool].fail("Trace mode requires debug mode to be enabled")
        update_data: t.MutableBoolMapping = {}
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
    def _set_format_params(
        cls,
        config: FlextCliSettings,
        params: p.Cli.CliParamsConfig,
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
                valid = ", ".join(c.Cli.ValidationLists.OUTPUT_FORMATS)
                return r[FlextCliSettings].fail(
                    f"invalid output format: {params.output_format}. valid: {valid}",
                )
            config = config.model_copy(update={"output_format": validated_result.value})
        return r[FlextCliSettings].ok(config)

    @classmethod
    def _set_log_level(
        cls,
        config: FlextCliSettings,
        params: p.Cli.CliParamsConfig,
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
    def apply_to_config(
        cls,
        config: FlextCliSettings,
        params: p.Cli.CliParamsConfig | None = None,
        **kwargs: bool | str | None,
    ) -> r[FlextCliSettings]:
        """Apply CLI parameter values to FlextSettings using Pydantic validation.

        Business Rule: Applies CLI parameter values with Pydantic validation.
        Trace mode requires debug mode to be enabled.
        """
        try:
            params_to_use = cls._resolve_params(params, kwargs)
            return cls._apply_param_setters(config, params_to_use)
        except c.Cli.CLI_SAFE_EXCEPTIONS as e:
            return r[FlextCliSettings].fail(f"Failed to apply CLI parameters: {e}")

    @classmethod
    def create_option(cls, field_name: str) -> OptionInfo:
        """Create typer.Option() from FlextCliSettings field metadata."""
        if field_name not in c.Cli.CLI_PARAM_REGISTRY:
            msg = f"Field '{field_name}' not found in CLI parameter registry"
            raise ValueError(msg)
        return u.Cli.OptionBuilder(field_name, c.Cli.CLI_PARAM_REGISTRY).build()

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


__all__ = ["FlextCliCommonParams"]
