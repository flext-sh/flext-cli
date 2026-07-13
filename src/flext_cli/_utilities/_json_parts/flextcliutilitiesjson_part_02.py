"""Generic JSON helpers shared through ``u.Cli.json_*``.

Follows the same pattern as ``_utilities/toml.py`` for TOML helpers.
All methods use the ``json_`` prefix for namespace consistency.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli._utilities._json_parts.flextcliutilitiesjson_part_01 import (
    FlextCliUtilitiesJson as FlextCliUtilitiesJsonPart01,
)
from flext_core import u

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliUtilitiesJson(FlextCliUtilitiesJsonPart01):
    """Implementation part for FlextCliUtilitiesJson."""

    @staticmethod
    def json_as_mapping_list(
        value: t.JsonPayload | None,
    ) -> t.SequenceOf[t.JsonMapping]:
        """Normalize any JSON-compatible value into a list of mappings."""
        return [
            mapping
            for item in FlextCliUtilitiesJson.json_as_sequence(value)
            if (mapping := FlextCliUtilitiesJson.json_as_mapping(item))
        ]

    @staticmethod
    def json_walk_path(data: t.JsonMapping, keys: t.StrSequence) -> t.JsonValue | None:
        """Walk a path over nested mappings and return the leaf value."""
        current: t.JsonMapping = data
        for key in keys[:-1]:
            raw = current.get(key, None)
            if raw is None:
                return None
            nested = FlextCliUtilitiesJson.json_as_mapping(raw)
            if not nested:
                return None
            current = nested
        if not keys:
            return None
        leaf = current.get(keys[-1], None)
        if leaf is None:
            return None
        return u.normalize_to_json_value(leaf)

    @staticmethod
    def json_deep_mapping(data: t.JsonMapping, *keys: str) -> t.JsonMapping:
        """Navigate nested mappings and normalize the final node as mapping."""
        if not keys:
            return FlextCliUtilitiesJson.json_as_mapping(data)
        raw = FlextCliUtilitiesJson.json_walk_path(data, keys)
        return FlextCliUtilitiesJson.json_as_mapping(raw)

    @staticmethod
    def json_deep_mapping_list(
        data: t.JsonMapping, *keys: str
    ) -> t.SequenceOf[t.JsonMapping]:
        """Navigate nested mappings and normalize the final node as mapping list."""
        raw = FlextCliUtilitiesJson.json_walk_path(data, keys)
        return FlextCliUtilitiesJson.json_as_mapping_list(raw)

    @staticmethod
    def json_pick_str(data: t.JsonMapping, key: str, default: str = "") -> str:
        """Extract a string value from mapping with safe coercion."""
        return u.norm_str(data.get(key, default), default=default).strip()

    @staticmethod
    def json_pick_int(data: t.JsonMapping, key: str, default: int = 0) -> int:
        """Extract an integer value from mapping with safe coercion."""
        parsed = u.parse(data.get(key, default), int, default=default).unwrap_or(
            default
        )
        return int(parsed) if isinstance(parsed, bool) else parsed

    @staticmethod
    def json_pick_bool(data: t.JsonMapping, key: str, *, default: bool = False) -> bool:
        """Extract a boolean value from mapping with string/int coercion."""
        return u.parse(data.get(key, None), bool, default=default).unwrap_or(default)

    @staticmethod
    def json_nested_int(data: t.JsonMapping, *keys: str, default: int = 0) -> int:
        """Extract an integer from a nested mapping path."""
        parsed = u.parse(
            FlextCliUtilitiesJson.json_walk_path(data, keys), int, default=default
        ).unwrap_or(default)
        return int(parsed) if isinstance(parsed, bool) else parsed

    @staticmethod
    def json_get_str_key(
        mapping: t.JsonMapping, key: str, *, default: str = "", case: str | None = None
    ) -> str:
        """Extract and normalize a string key from a mapping."""
        raw = FlextCliUtilitiesJson.json_pick_str(mapping, key, default)
        return u.normalize(raw, case=case)


__all__: list[str] = ["FlextCliUtilitiesJson"]
