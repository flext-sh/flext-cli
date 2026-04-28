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
        if isinstance(val, str):
            stripped = val.strip()
            if not stripped:
                return r[bool].fail(
                    c.Cli.VALIDATION_MSG_FIELD_CANNOT_BE_EMPTY.format(
                        field_name=name,
                    ),
                )
        return r[bool].ok(True)

    @staticmethod
    def validate_format(format_type: str) -> p.Result[str]:
        """Validate one CLI output format."""
        fmt = format_type.lower()
        valid = FlextCliUtilitiesValidation.validate_not_empty(fmt, name="format")
        if valid.failure or fmt not in set(c.Cli.OUTPUT_FORMATS):
            return r[str].fail(
                c.Cli.ERR_INVALID_OUTPUT_FORMAT.format(format=format_type),
            )
        return r[str].ok(fmt)


__all__: t.MutableSequenceOf[str] = [
    "FlextCliUtilitiesValidation",
]
