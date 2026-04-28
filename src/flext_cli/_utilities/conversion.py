"""CLI conversion helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import (
    Mapping,
)
from pathlib import Path

from flext_cli import c, p, r, t
from flext_core import m, u


class FlextCliUtilitiesConversion:
    """Conversion methods exposed directly on ``u.Cli``."""

    @staticmethod
    def default_for_type_kind(
        type_kind: t.Cli.TypeKind,
        default: t.JsonValue | None,
    ) -> t.Cli.TypedExtractValue:
        """Return a canonical default for one type kind."""
        if type_kind == c.Cli.TypeKind.STR:
            return default if isinstance(default, str) else ""
        if type_kind == c.Cli.TypeKind.BOOL:
            return default if isinstance(default, bool) else False
        if isinstance(default, Mapping):
            return {
                key: u.normalize_to_json_value(value) for key, value in default.items()
            }
        return {}

    @staticmethod
    def cli_args_to_model[M: m.BaseModel](
        model_class: type[M],
        cli_args: t.JsonMapping,
    ) -> p.Result[M]:
        """Convert a CLI args mapping into a validated Pydantic model."""
        try:
            instance: M = model_class.model_validate(cli_args)
            return r[M].ok(instance)
        except c.ValidationError as exc:
            return r[M].fail(f"Validation error for {model_class.__name__}: {exc}")

    @staticmethod
    def convert_field_value(
        field_value: t.JsonValue | None,
    ) -> p.Result[t.JsonValue]:
        """Convert one field value to a JSON-compatible value."""
        if field_value is None:
            empty_value: t.JsonValue = ""
            return r[t.JsonValue].ok(empty_value)
        return r[t.JsonValue].ok(field_value)

    @staticmethod
    def resolve_optional_path(
        value: t.Cli.TextPath | None,
        *,
        default: Path,
    ) -> Path:
        """Resolve an optional text/path value while preserving a default path."""
        if isinstance(value, Path):
            return value
        if isinstance(value, str):
            normalized = value.strip()
            if normalized:
                return Path(normalized)
        return default

    @staticmethod
    def normalize_optional_text(value: t.JsonValue | Path) -> str | None:
        """Normalize optional text-like values, preserving ``None`` for empties."""
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value if value is None else str(value)

    @staticmethod
    def normalize_required_text(
        value: t.JsonValue | Path,
        *,
        default: str,
    ) -> str:
        """Normalize required text-like values, falling back to ``default``."""
        normalized = FlextCliUtilitiesConversion.normalize_optional_text(value)
        return normalized if normalized is not None else default


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesConversion"]
