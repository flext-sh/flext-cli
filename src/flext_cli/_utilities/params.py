"""CLI params helpers shared through ``u.Cli``."""

from __future__ import annotations

from flext_cli import FlextCliUtilitiesValidation as uv, c, m, p, t
from flext_core import r


class FlextCliUtilitiesParams:
    """Parameter resolution and application helpers for CLI settings."""

    @staticmethod
    def params_resolve(
        params: p.Cli.CliParamsConfig | None,
        kwargs: t.Cli.CliParamKwargs,
    ) -> m.Cli.CliParamsConfig:
        """Resolve explicit params and kwargs into one validated model."""
        kwargs_model = m.Cli.CliParamsConfig.model_validate(kwargs)
        if params is None:
            return kwargs_model
        if not isinstance(params, m.Cli.CliParamsConfig):
            return kwargs_model
        return params.model_copy(
            update=kwargs_model.model_dump(exclude_none=True),
        )

    @staticmethod
    def params_set_bool(
        settings: p.Cli.Settings,
        params: p.Cli.CliParamsConfig,
    ) -> p.Result[p.Cli.Settings]:
        """Set boolean parameters through validated model_copy updates."""
        if params.trace is not None and params.trace:
            will_be_debug = params.debug if params.debug is not None else settings.debug
            if not will_be_debug:
                return r[p.Cli.Settings].fail(c.Cli.CLI_PARAM_ERR_TRACE_REQUIRES_DEBUG)
        root_update: t.MutableBoolMapping = {}
        for field in ("debug", "trace"):
            value = getattr(params, field, None)
            if value is not None:
                root_update[field] = value
        cli_update: t.MutableBoolMapping = {}
        for field in ("verbose", "quiet", "no_color"):
            value = getattr(params, field, None)
            if value is not None:
                cli_update[field] = value
        if not root_update and not cli_update:
            return r[p.Cli.Settings].ok(settings)
        next_settings = settings.clone(**root_update) if root_update else settings
        if not cli_update:
            return r[p.Cli.Settings].ok(next_settings)
        next_cli = next_settings.Cli.model_copy(update=cli_update)
        return r[p.Cli.Settings].ok(
            next_settings.clone(Cli=next_cli),
        )

    @staticmethod
    def params_set_log_level(
        settings: p.Cli.Settings,
        params: p.Cli.CliParamsConfig,
    ) -> p.Result[p.Cli.Settings]:
        """Set CLI log level with enum conversion/validation."""
        if params.log_level is None:
            return r[p.Cli.Settings].ok(settings)
        try:
            resolved_level = m.Cli.LogLevelResolved(
                raw=params.log_level,
                default=c.LogLevel.INFO,
            ).resolved
            next_level = type(c.LogLevel.INFO)(resolved_level)
            next_cli = settings.Cli.model_copy(
                update={"cli_log_level": str(next_level)},
            )
            return r[p.Cli.Settings].ok(
                settings.clone(Cli=next_cli),
            )
        except ValueError:
            valid = ", ".join(c.Cli.LOG_LEVELS)
            return r[p.Cli.Settings].fail(
                c.Cli.CLI_PARAM_ERR_INVALID_WITH_OPTIONS_FMT.format(
                    field_label="log level",
                    field_value=params.log_level,
                    valid_values=valid,
                ),
            )

    @staticmethod
    def params_set_format(
        settings: p.Cli.Settings,
        params: p.Cli.CliParamsConfig,
    ) -> p.Result[p.Cli.Settings]:
        """Set output/log format values with canonical validation helpers."""
        next_config = settings
        if params.log_format is not None:
            try:
                log_verbosity = c.Cli.LogVerbosity(params.log_format.lower())
            except ValueError:
                valid = ", ".join(c.Cli.CLI_VALID_LOG_FORMATS)
                return r[p.Cli.Settings].fail(
                    c.Cli.CLI_PARAM_ERR_INVALID_WITH_VALID_FMT.format(
                        field_label="log format",
                        field_value=params.log_format,
                        valid_values=valid,
                    ),
                )
            next_cli = next_config.Cli.model_copy(
                update={"log_verbosity": str(log_verbosity)},
            )
            next_config = next_config.clone(Cli=next_cli)
        if params.output_format is not None:
            validated_result = uv.validate_format(params.output_format)
            if validated_result.failure or validated_result.value is None:
                valid = ", ".join(c.Cli.OUTPUT_FORMATS)
                return r[p.Cli.Settings].fail(
                    c.Cli.CLI_PARAM_ERR_INVALID_WITH_VALID_FMT.format(
                        field_label="output format",
                        field_value=params.output_format,
                        valid_values=valid,
                    ),
                )
            next_cli = next_config.Cli.model_copy(
                update={"output_format": validated_result.value},
            )
            next_config = next_config.clone(Cli=next_cli)
        return r[p.Cli.Settings].ok(next_config)

    @staticmethod
    def params_apply(
        settings: p.Cli.Settings,
        params: p.Cli.CliParamsConfig,
    ) -> p.Result[p.Cli.Settings]:
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


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesParams"]
