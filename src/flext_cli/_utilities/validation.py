"""CLI validation helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

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

    @staticmethod
    def format_validation_errors(
        exc: t.ValidationError,
        *,
        command: str,
        model: str,
    ) -> str:
        """Render pydantic errors as located command/model/field lines.

        Returns:
            The resulting ``str``.

        """
        lines: list[str] = []
        for error in exc.errors():
            loc = ".".join(str(part) for part in error.get("loc", ()) if part != "body")
            field = loc or "<input>"
            message = error.get("msg", "invalid value")
            lines.append(
                c.Cli.ERR_CLI_DEFINITION_FIELD.format(
                    command=command,
                    model=model,
                    field=field,
                    reason=message,
                ),
            )
        if lines:
            return "\n".join(lines)
        return c.Cli.ERR_CLI_DEFINITION_INVALID_MODEL.format(
            command=command,
            model=model,
            reason="validation failed",
        )


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesValidation"]
