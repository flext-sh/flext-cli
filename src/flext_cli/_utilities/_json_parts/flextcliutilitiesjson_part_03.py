"""Generic JSON helpers shared through ``u.Cli.json_*``.

Follows the same pattern as ``_utilities/toml.py`` for TOML helpers.
All methods use the ``json_`` prefix for namespace consistency.
"""

from __future__ import annotations

from collections.abc import (
    Mapping,
)

from flext_cli import c, p, r, t


class FlextCliUtilitiesJson:
    """Implementation part for FlextCliUtilitiesJson."""

    @staticmethod
    def json_dumps(
        value: t.JsonValue,
        *,
        sort_keys: bool = False,
        indent: int | None = None,
    ) -> p.Result[str]:
        """Serialize a JSON-compatible value to a string via canonical adapters."""
        try:
            normalized = (
                FlextCliUtilitiesJson.json_sort_keys(value) if sort_keys else value
            )
            payload = t.Cli.JSON_VALUE_ADAPTER.dump_json(
                normalized,
                indent=indent,
            )
        except (c.ValidationError, ValueError, TypeError) as exc:
            return r[str].fail(f"json_dumps: {exc}")
        return r[str].ok(payload.decode(c.Cli.ENCODING_DEFAULT))

    @staticmethod
    def json_loads(raw: str | bytes) -> p.Result[t.JsonValue]:
        """Parse a JSON-encoded string/bytes into a JSON-compatible value."""
        try:
            data: t.JsonValue = t.Cli.JSON_VALUE_ADAPTER.validate_json(raw)
        except (c.ValidationError, ValueError) as exc:
            return r[t.JsonValue].fail(f"json_loads: {exc}")
        return r[t.JsonValue].ok(data)

    @staticmethod
    def json_sort_keys(data: t.JsonValue) -> t.JsonValue:
        """Recursively sort dictionary keys in a JSON structure."""
        if isinstance(data, Mapping):
            validated = t.Cli.JSON_MAPPING_ADAPTER.validate_python(data)
            return {
                key: FlextCliUtilitiesJson.json_sort_keys(
                    t.Cli.JSON_VALUE_ADAPTER.validate_python(value)
                )
                for key, value in sorted(validated.items())
            }
        if isinstance(data, list):
            items = t.Cli.JSON_LIST_ADAPTER.validate_python(data)
            return [
                FlextCliUtilitiesJson.json_sort_keys(
                    t.Cli.JSON_VALUE_ADAPTER.validate_python(item)
                )
                for item in items
            ]
        return data


__all__: list[str] = ["FlextCliUtilitiesJson"]
