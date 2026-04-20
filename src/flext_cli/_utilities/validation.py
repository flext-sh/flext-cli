"""CLI validation helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableMapping,
    MutableSequence,
)
from typing import ClassVar

from flext_cli import c, p, r, t
from flext_core import u


class FlextCliUtilitiesValidation:
    """Validation methods exposed directly on ``u.Cli``."""

    _module_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)

    @staticmethod
    def process_mapping[T, U](
        items: Mapping[str, T],
        processor: t.Cli.MappingProcessor[T, U],
        on_error: str = "fail",
    ) -> p.Result[Mapping[str, U]]:
        """Process a mapping of items with canonical error handling."""
        errors: MutableSequence[str] = []
        values: MutableMapping[str, U] = {}
        for key, value in items.items():
            try:
                values[key] = processor(key, value)
            except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
                if on_error == "fail":
                    return r[Mapping[str, U]].fail(f"Error processing {key}: {exc}")
                if on_error == "collect":
                    errors.append(f"{key}: {exc}")
                else:
                    FlextCliUtilitiesValidation._module_logger.debug(
                        f"process_mapping skip key {key}: {exc}",
                        exc_info=False,
                    )
        return (
            r[Mapping[str, U]].fail("; ".join(errors))
            if errors
            else r[Mapping[str, U]].ok(values)
        )

    @staticmethod
    def to_str(value: t.Cli.CliValue) -> str:
        """Convert a value to a safe string representation."""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return str(value)

    @staticmethod
    def _validate_cli_value(
        val: t.Cli.CliValue,
        *,
        name: str = "field",
        empty: bool = True,
        in_list: t.StrSequence | None = None,
        eq: str | None = None,
        msg: str = "",
    ) -> p.Result[bool]:
        """Validate a value against emptiness, enumerations, or equality constraints."""
        if not empty:
            check = FlextCliUtilitiesValidation.validate_not_empty(val, name=name)
            if check.failure:
                return r[bool].fail(msg or check.error or "")
        if in_list is not None:
            val_str = FlextCliUtilitiesValidation.to_str(val)
            if val_str not in set(in_list):
                err = (
                    c.Cli.VALIDATION_MSG_SESSION_STATUS_INVALID.format(
                        current_status=val_str,
                        valid_states=in_list,
                    )
                    if name == "session_status"
                    else c.Cli.VALIDATION_MSG_INVALID_ENUM_VALUE.format(
                        field_name=name,
                        valid_values=in_list,
                    )
                )
                return r[bool].fail(msg or err)
        if eq is not None:
            val_str = FlextCliUtilitiesValidation.to_str(val)
            if val_str != eq:
                err = c.Cli.VALIDATION_MSG_COMMAND_STATE_INVALID.format(
                    operation=name,
                    current_status=val_str,
                    required_status=eq,
                )
                return r[bool].fail(msg or err)
            return r[bool].ok(True)
        return r[bool].ok(True)

    @staticmethod
    def validate_not_empty(
        val: t.Cli.CliValue | None,
        *,
        name: str = "field",
    ) -> p.Result[bool]:
        """Validate that a value is not empty."""
        if val is None:
            return r[bool].fail(
                c.Cli.VALIDATION_MSG_FIELD_CANNOT_BE_EMPTY.format(
                    field_name=name,
                ),
            )
        if isinstance(val, str) and not u.string_non_empty(val):
            return r[bool].fail(
                c.Cli.VALIDATION_MSG_FIELD_CANNOT_BE_EMPTY.format(
                    field_name=name,
                ),
            )
        return r[bool].ok(True)

    @staticmethod
    def validate_format(format_type: str) -> p.Result[str]:
        """Validate one CLI output format."""
        fmt = str(format_type).lower()
        valid = FlextCliUtilitiesValidation._validate_cli_value(
            fmt,
            name="format",
            empty=False,
            in_list=c.Cli.OUTPUT_FORMATS,
        )
        if valid.success:
            return r[str].ok(fmt)
        return r[str].fail(
            c.Cli.ERR_INVALID_OUTPUT_FORMAT.format(format=format_type),
        )


__all__: list[str] = [
    "FlextCliUtilitiesValidation",
]
