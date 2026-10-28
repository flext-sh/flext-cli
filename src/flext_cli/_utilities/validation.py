"""CLI validation helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence

from flext_cli import c, p, r, t


class FlextCliUtilitiesValidation:
    """Validation methods exposed directly on ``u.Cli``."""

    @staticmethod
    def validate_not_empty(
        val: t.Cli.CliValue | None,
        *,
        name: str = "field",
    ) -> p.Result[bool]:
        """Validate that a value is not empty.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        if val is None:
            return r[bool].fail(
                c.Cli.VALIDATION_MSG_FIELD_CANNOT_BE_EMPTY.format(field_name=name),
            )
        if isinstance(val, str):
            stripped = val.strip()
            if not stripped:
                return r[bool].fail(
                    c.Cli.VALIDATION_MSG_FIELD_CANNOT_BE_EMPTY.format(field_name=name),
                )
        return r[bool].ok(value=True)

    @staticmethod
    def validate_format(format_type: str) -> p.Result[str]:
        """Validate one CLI output format.

        Returns:
            The resulting ``p.Result[str]``.

        """
        fmt = format_type.lower()
        valid = FlextCliUtilitiesValidation.validate_not_empty(fmt, name="format")
        if valid.failure or fmt not in set(c.Cli.OUTPUT_FORMATS):
            return r[str].fail(
                c.Cli.ERR_INVALID_OUTPUT_FORMAT.format(format=format_type),
            )
        return r[str].ok(fmt)


__all__: MutableSequence[str] = ["FlextCliUtilitiesValidation"]
