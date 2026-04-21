"""CLI conversion helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import (
    Mapping,
)

from flext_core import m

from flext_cli import FlextCliUtilitiesJson as uj, c, p, r, t


class FlextCliUtilitiesConversion:
    """Conversion methods exposed directly on ``u.Cli``."""

    @staticmethod
    def default_for_type_kind(
        type_kind: t.Cli.TypeKind,
        default: t.Cli.JsonValue | None,
    ) -> t.Cli.TypedExtractValue:
        """Return a canonical default for one type kind."""
        if type_kind == c.Cli.TypeKind.STR:
            return default if isinstance(default, str) else ""
        if type_kind == c.Cli.TypeKind.BOOL:
            return default if isinstance(default, bool) else False
        if isinstance(default, Mapping):
            return {
                str(key): uj.normalize_json_value(value)
                for key, value in default.items()
            }
        return {}

    @staticmethod
    def cli_args_to_model[M: m.BaseModel](
        model_class: type[M],
        cli_args: t.Cli.JsonMapping,
    ) -> p.Result[M]:
        """Convert a CLI args mapping into a validated Pydantic model."""
        try:
            instance: M = model_class.model_validate(cli_args)
            return r[M].ok(instance)
        except c.ValidationError as exc:
            return r[M].fail(f"Validation error for {model_class.__name__}: {exc}")

    @staticmethod
    def convert_field_value(
        field_value: t.Cli.JsonValue | None,
    ) -> p.Result[t.Cli.JsonValue]:
        """Convert one field value to a JSON-compatible value."""
        if field_value is None:
            empty_value: t.Cli.JsonValue = ""
            return r[t.Cli.JsonValue].ok(empty_value)
        return r[t.Cli.JsonValue].ok(field_value)


__all__: list[str] = ["FlextCliUtilitiesConversion"]
