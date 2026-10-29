"""FLEXT CLI Common Parameters - Auto-generated from FlextSettings properties.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence

from flext_cli import c, p, r, s, t, u


class FlextCliCommonParams(s[p.Cli.RuntimeStatus]):
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
    def apply_to_config(
        cls,
        settings: p.Cli.Settings,
        params: p.Cli.CliParamsConfig | None = None,
        **kwargs: t.Cli.CliParamValue,
    ) -> p.Result[p.Cli.Settings]:
        """Apply CLI parameter values to FlextSettings using Pydantic validation.

        Business Rule: Applies CLI parameter values with Pydantic validation.
        Core owns severity and diagnostic-detail policy. Parameter values the
        ``CliParamsConfig`` model rejects are the declared failure outcome and
        the result carries the ``ValidationError``; every other exception
        escapes.

        Args:
            settings: Settings instance that receives the parameter values.
            params: Optional resolved parameter model; defaults apply when omitted.
            kwargs: Individual parameter values keyed by parameter name.

        Returns:
            The resulting ``p.Result[p.Cli.Settings]``.

        """
        try:
            params_to_use = u.Cli.params_resolve(params, kwargs)
        except c.ValidationError as exc:
            return r[p.Cli.Settings].fail(
                c.Cli.CLI_PARAM_ERR_APPLY_FAILED_FMT.format(error=exc),
                exception=exc,
            )
        return u.Cli.params_apply(settings, params_to_use)


__all__: MutableSequence[str] = ["FlextCliCommonParams"]
