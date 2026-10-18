"""CLI params helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import u

from flext_cli import c, m, p, r, t
from flext_cli._utilities.validation import FlextCliUtilitiesValidation


class FlextCliUtilitiesParams:
    """Parameter resolution and application helpers for CLI settings."""

    @staticmethod
    def params_resolve(
        params: p.Cli.CliParamsConfig | None,
        kwargs: t.Cli.CliParamKwargs,
    ) -> m.Cli.CliParamsConfig:
        """Resolve explicit params and kwargs into one validated model.

        Returns:
            The resulting ``m.Cli.CliParamsConfig``.

        """
        kwargs_model = m.Cli.CliParamsConfig.model_validate(kwargs)
        if params is None:
            return kwargs_model
        if not isinstance(params, m.Cli.CliParamsConfig):
            return kwargs_model
        return params.model_copy(update=kwargs_model.model_dump(exclude_none=True))

    @staticmethod
    def params_set_bool(
        settings: p.Cli.Settings,
        params: p.Cli.CliParamsConfig,
    ) -> p.Result[p.Cli.Settings]:
        """Apply Core policy and the independent CLI display booleans.

        Returns:
            The resulting ``p.Result[p.Cli.Settings]``.

        """
        cli_update: t.MutableBoolMapping = {}
        for field in ("verbose", "quiet", "no_color"):
            value = getattr(params, field, None)
            if value is not None:
                cli_update[f"cli_{field}"] = value
        return FlextCliUtilitiesParams.params_set_log_level(settings, params).map(
            lambda resolved: resolved.clone(**cli_update) if cli_update else resolved,
        )

    @staticmethod
    def params_set_log_level(
        settings: p.Cli.Settings,
        params: p.Cli.CliParamsConfig,
    ) -> p.Result[p.Cli.Settings]:
        """Resolve optional logging flags through the canonical Core policy.

        Returns:
            The resulting ``p.Result[p.Cli.Settings]``.

        Raises:
            TypeError: If the resolved settings break the CLI settings contract.

        """
        try:
            resolved = u.resolve_logging_settings(
                runtime_settings=settings,
                log_level=params.log_level,
                debug=params.debug,
                trace=params.trace,
            )
        except (c.ValidationError, ValueError) as exc:
            return r[p.Cli.Settings].fail(str(exc), exception=exc)
        if not isinstance(resolved, p.Cli.Settings):
            msg = "Resolved logging settings do not satisfy the CLI settings contract"
            raise TypeError(msg)
        return r[p.Cli.Settings].ok(resolved)

    @staticmethod
    def params_set_format(
        settings: p.Cli.Settings,
        params: p.Cli.CliParamsConfig,
    ) -> p.Result[p.Cli.Settings]:
        """Set output/log format values with canonical validation helpers.

        Returns:
            The resulting ``p.Result[p.Cli.Settings]``.

        """
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
            next_config = next_config.clone(cli_log_verbosity=str(log_verbosity))
        if params.output_format is not None:
            validated_result = FlextCliUtilitiesValidation.validate_format(
                params.output_format,
            )
            if validated_result.failure:
                valid = ", ".join(c.Cli.OUTPUT_FORMATS)
                return r[p.Cli.Settings].fail(
                    c.Cli.CLI_PARAM_ERR_INVALID_WITH_VALID_FMT.format(
                        field_label="output format",
                        field_value=params.output_format,
                        valid_values=valid,
                    ),
                )
            next_config = next_config.clone(cli_output_format=validated_result.value)
        return r[p.Cli.Settings].ok(next_config)

    @staticmethod
    def params_apply(
        settings: p.Cli.Settings,
        params: p.Cli.CliParamsConfig,
    ) -> p.Result[p.Cli.Settings]:
        """Apply all parameter-setting stages to one settings model.

        Returns:
            The resulting ``p.Result[p.Cli.Settings]``.

        """
        return FlextCliUtilitiesParams.params_set_bool(settings, params).flat_map(
            lambda updated_config: FlextCliUtilitiesParams.params_set_format(
                updated_config,
                params,
            ),
        )


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesParams"]
