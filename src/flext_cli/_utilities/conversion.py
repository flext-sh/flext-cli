"""CLI conversion helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar

from pydantic import BaseModel, TypeAdapter

from flext_cli import FlextCliUtilitiesJson, c, p, r, t
from flext_core import m, u


class FlextCliUtilitiesCliModelConverter:
    """Convert CLI payloads into canonical Pydantic or JSON values."""

    _module_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)
    JSON_VALUE_ADAPTER: ClassVar[m.TypeAdapter[t.Cli.JsonValue]] = TypeAdapter(
        t.Cli.JsonValue,
    )

    @staticmethod
    def cli_args_to_model[M: BaseModel](
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
        try:
            json_value: t.Cli.JsonValue = (
                FlextCliUtilitiesCliModelConverter.JSON_VALUE_ADAPTER.validate_python(
                    field_value,
                )
            )
            return r[t.Cli.JsonValue].ok(json_value)
        except c.ValidationError as exc:
            FlextCliUtilitiesCliModelConverter._module_logger.debug(
                "convert_field_value validation fallback",
                error=str(exc),
                exc_info=False,
            )
            fallback_value: t.Cli.JsonValue = str(field_value)
            return r[t.Cli.JsonValue].ok(fallback_value)


class FlextCliUtilitiesConversion:
    """Conversion methods exposed directly on ``u.Cli``."""

    @staticmethod
    def default_for_type_kind(
        type_kind: t.Cli.TypeKind,
        default: t.Cli.JsonValue | None,
    ) -> t.Cli.TypedExtractValue:
        """Return a canonical default for one type kind."""
        if type_kind == c.Cli.TypeKind.STR:
            return default if isinstance(default, str) else None
        if type_kind == c.Cli.TypeKind.BOOL:
            return default if isinstance(default, bool) else False
        if isinstance(default, Mapping):
            return {
                str(key): FlextCliUtilitiesJson.normalize_json_value(value)
                for key, value in default.items()
            }
        return {}

    @staticmethod
    def cli_args_to_model[M: BaseModel](
        model_class: type[M],
        cli_args: t.Cli.JsonMapping,
    ) -> p.Result[M]:
        """Convert a CLI args mapping into a validated Pydantic model."""
        return FlextCliUtilitiesCliModelConverter.cli_args_to_model(
            model_class,
            cli_args,
        )

    @staticmethod
    def convert_field_value(
        field_value: t.Cli.JsonValue | None,
    ) -> p.Result[t.Cli.JsonValue]:
        """Convert one field value to a JSON-compatible value."""
        return FlextCliUtilitiesCliModelConverter.convert_field_value(field_value)


__all__: list[str] = [
    "FlextCliUtilitiesCliModelConverter",
    "FlextCliUtilitiesConversion",
]
