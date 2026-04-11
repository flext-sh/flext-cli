"""CLI params helpers shared through ``u.Cli``."""

from __future__ import annotations

from flext_cli import FlextCliSettings, c, m, p, r, t
from flext_cli._utilities.validation import FlextCliUtilitiesValidation


class FlextCliUtilitiesParams:
    """Parameter resolution and application helpers for CLI settings."""

    @staticmethod
    def params_build_from_kwargs(
        kwargs: t.Cli.CliParamKwargs,
    ) -> m.Cli.CliParamsConfig:
        """Build CLI params model from kwargs via canonical Pydantic validation."""
        return m.Cli.CliParamsConfig.model_validate(kwargs)

    @staticmethod
    def params_resolve(
        params: p.Cli.CliParamsConfig | None,
        kwargs: t.Cli.CliParamKwargs,
    ) -> m.Cli.CliParamsConfig:
        """Resolve explicit params and kwargs into one validated model."""
        kwargs_model = FlextCliUtilitiesParams.params_build_from_kwargs(kwargs)
        if params is None:
            return kwargs_model
        if not isinstance(params, m.Cli.CliParamsConfig):
            return kwargs_model
        merged_data: t.Cli.JsonMapping = {
            **params.model_dump(exclude_none=True),
            **kwargs_model.model_dump(exclude_none=True),
        }
        return m.Cli.CliParamsConfig.model_validate(merged_data)

    @staticmethod
    def params_set_bool(
        settings: FlextCliSettings,
        params: p.Cli.CliParamsConfig,
    ) -> r[FlextCliSettings]:
        """Set boolean parameters through validated model_copy updates."""
        if params.trace is not None and params.trace:
            will_be_debug = params.debug if params.debug is not None else settings.debug
            if not will_be_debug:
                return r[FlextCliSettings].fail(
                    c.Cli.CLI_PARAM_ERR_TRACE_REQUIRES_DEBUG
                )
        update_data: t.MutableBoolMapping = {}
        for field in ("verbose", "quiet", "debug", "trace", "no_color"):
            value = getattr(params, field, None)
            if value is not None:
                update_data[field] = value
        if not update_data:
            return r[FlextCliSettings].ok(settings)
        return r[FlextCliSettings].ok(settings.model_copy(update=update_data))

    @staticmethod
    def params_set_log_level(
        settings: FlextCliSettings,
        params: p.Cli.CliParamsConfig,
    ) -> r[FlextCliSettings]:
        """Set CLI log level with enum conversion/validation."""
        if params.log_level is None:
            return r[FlextCliSettings].ok(settings)
        try:
            resolved_level = m.Cli.LogLevelResolved(
                raw=params.log_level,
                default=c.LogLevel.INFO,
            ).resolved
            next_level = type(c.LogLevel.INFO)(resolved_level)
            return r[FlextCliSettings].ok(
                settings.model_copy(update={"cli_log_level": next_level}),
            )
        except ValueError:
            valid = ", ".join(c.Cli.LOG_LEVELS_LIST)
            return r[FlextCliSettings].fail(
                c.Cli.CLI_PARAM_ERR_INVALID_WITH_OPTIONS_FMT.format(
                    field_label="log level",
                    field_value=params.log_level,
                    valid_values=valid,
                ),
            )

    @staticmethod
    def params_set_format(
        settings: FlextCliSettings,
        params: p.Cli.CliParamsConfig,
    ) -> r[FlextCliSettings]:
        """Set output/log format values with canonical validation helpers."""
        next_config = settings
        if params.log_format is not None:
            try:
                log_verbosity = c.Cli.LogVerbosity(params.log_format.lower())
            except ValueError:
                valid = ", ".join(c.Cli.CLI_VALID_LOG_FORMATS)
                return r[FlextCliSettings].fail(
                    c.Cli.CLI_PARAM_ERR_INVALID_WITH_VALID_FMT.format(
                        field_label="log format",
                        field_value=params.log_format,
                        valid_values=valid,
                    ),
                )
            next_config = next_config.model_copy(
                update={"log_verbosity": str(log_verbosity)},
            )
        if params.output_format is not None:
            validated_result = FlextCliUtilitiesValidation.validate_format(
                params.output_format
            )
            if validated_result.failure or validated_result.value is None:
                valid = ", ".join(c.Cli.OUTPUT_FORMATS)
                return r[FlextCliSettings].fail(
                    c.Cli.CLI_PARAM_ERR_INVALID_WITH_VALID_FMT.format(
                        field_label="output format",
                        field_value=params.output_format,
                        valid_values=valid,
                    ),
                )
            next_config = next_config.model_copy(
                update={"output_format": validated_result.value},
            )
        return r[FlextCliSettings].ok(next_config)

    @staticmethod
    def params_apply(
        settings: FlextCliSettings,
        params: p.Cli.CliParamsConfig,
    ) -> r[FlextCliSettings]:
        """Apply all parameter-setting stages to one settings model."""
        return (
            FlextCliUtilitiesParams
            .params_set_bool(settings, params)
            .map_error(lambda error: error or "Boolean parameter setting failed")
            .flat_map(
                lambda updated_config: FlextCliUtilitiesParams.params_set_log_level(
                    updated_config,
                    params,
                ),
            )
            .flat_map(
                lambda updated_config: FlextCliUtilitiesParams.params_set_format(
                    updated_config,
                    params,
                ),
            )
        )


__all__ = ["FlextCliUtilitiesParams"]
