"""Generic JSON helpers shared through ``u.Cli.json_*``.

Follows the same pattern as ``_utilities/toml.py`` for TOML helpers.
All methods use the ``json_`` prefix for namespace consistency.
"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    Sequence,
)
from pathlib import Path
from typing import ClassVar

from flext_cli import c, m, p, r, t
from flext_core import u


class FlextCliUtilitiesJson:
    """Generic JSON read/write and manipulation helpers."""

    _module_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)

    @staticmethod
    def normalize_json_value(item: t.JsonPayload) -> t.JsonValue:
        """Normalize any runtime value to JSON-compatible output (Pydantic-native)."""
        return u.normalize_to_json_value(item)

    @staticmethod
    def json_read(path: Path) -> p.Result[t.JsonMapping]:
        """Read and parse a JSON file.

        Returns empty mapping if file does not exist.
        """
        if not path.exists():
            return r[t.JsonMapping].ok({})
        try:
            raw = path.read_text(encoding=c.Cli.ENCODING_DEFAULT)
            loaded: t.JsonValue = t.Cli.JSON_VALUE_ADAPTER.validate_json(raw)
        except (c.ValidationError, OSError) as exc:
            return r[t.JsonMapping].fail(f"json_read: {exc}")
        if not isinstance(loaded, Mapping):
            return r[t.JsonMapping].fail("json_read: root must be an object")
        return r[t.JsonMapping].ok(t.Cli.JSON_MAPPING_ADAPTER.validate_python(loaded))

    @staticmethod
    def json_write(
        path: Path,
        payload: t.JsonPayload,
        options: m.Cli.JsonWriteOptions | None = None,
    ) -> p.Result[bool]:
        """Write any Pydantic-serializable payload to a JSON file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            opts = options or m.Cli.JsonWriteOptions()
            validated = FlextCliUtilitiesJson.normalize_json_value(payload)
            normalized = (
                FlextCliUtilitiesJson._json_sort_keys(validated)
                if opts.sort_keys
                else validated
            )
            content = (
                t.Cli.JSON_VALUE_ADAPTER.dump_json(
                    normalized,
                    indent=opts.indent,
                    ensure_ascii=opts.ensure_ascii,
                ).decode(
                    c.Cli.ENCODING_DEFAULT,
                )
                + "\n"
            )
            _ = path.write_text(content, encoding=c.Cli.ENCODING_DEFAULT)
        except c.EXC_OS_VALIDATION as exc:
            FlextCliUtilitiesJson._module_logger.debug(
                "json_write failed",
                error=str(exc),
                exc_info=False,
            )
            return r[bool].fail(f"json_write: {exc}")
        return r[bool].ok(True)

    @staticmethod
    def json_parse(text: str) -> p.Result[t.JsonValue]:
        """Parse a JSON string into a validated JsonValue."""
        try:
            return r[t.JsonValue].ok(
                t.Cli.JSON_VALUE_ADAPTER.validate_json(text),
            )
        except c.EXC_VALIDATION_VALUE as exc:
            return r[t.JsonValue].fail(f"json_parse: {exc}")

    @staticmethod
    def json_as_mapping(
        value: t.JsonPayload | None,
    ) -> t.JsonMapping:
        """Normalize any JSON-compatible value into a mapping."""
        if value is None:
            return {}
        normalized: t.JsonValue = u.normalize_to_json_value(value)
        if not isinstance(normalized, Mapping):
            return {}
        try:
            return t.Cli.JSON_MAPPING_ADAPTER.validate_python(normalized)
        except c.ValidationError:
            return {}

    @staticmethod
    def json_as_sequence(
        value: t.JsonPayload | None,
    ) -> t.SequenceOf[t.JsonValue]:
        """Normalize any JSON-compatible value into a JSON sequence."""
        if value is None:
            return []
        normalized: t.JsonValue = u.normalize_to_json_value(value)
        if not isinstance(normalized, Sequence) or isinstance(normalized, str | bytes):
            return []
        try:
            validated: t.SequenceOf[t.JsonValue] = (
                t.Cli.JSON_LIST_ADAPTER.validate_python(normalized)
            )
        except c.ValidationError:
            return []
        return validated

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
    def json_walk_path(
        data: t.JsonMapping,
        keys: tuple[str, ...],
    ) -> t.JsonValue | None:
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
    def json_deep_mapping(
        data: t.JsonMapping,
        *keys: str,
    ) -> t.JsonMapping:
        """Navigate nested mappings and normalize the final node as mapping."""
        if not keys:
            return FlextCliUtilitiesJson.json_as_mapping(data)
        raw = FlextCliUtilitiesJson.json_walk_path(data, keys)
        return FlextCliUtilitiesJson.json_as_mapping(raw)

    @staticmethod
    def json_deep_mapping_list(
        data: t.JsonMapping,
        *keys: str,
    ) -> t.SequenceOf[t.JsonMapping]:
        """Navigate nested mappings and normalize the final node as mapping list."""
        raw = FlextCliUtilitiesJson.json_walk_path(data, keys)
        return FlextCliUtilitiesJson.json_as_mapping_list(raw)

    @staticmethod
    def json_pick_str(
        data: t.JsonMapping,
        key: str,
        default: str = "",
    ) -> str:
        """Extract a string value from mapping with safe coercion."""
        return u.norm_str(data.get(key, default), default=default).strip()

    @staticmethod
    def json_pick_int(
        data: t.JsonMapping,
        key: str,
        default: int = 0,
    ) -> int:
        """Extract an integer value from mapping with safe coercion."""
        parsed = u.parse(data.get(key, default), int, default=default).unwrap_or(
            default
        )
        return int(parsed) if isinstance(parsed, bool) else parsed

    @staticmethod
    def json_pick_bool(
        data: t.JsonMapping,
        key: str,
        *,
        default: bool = False,
    ) -> bool:
        """Extract a boolean value from mapping with string/int coercion."""
        return u.parse(data.get(key, None), bool, default=default).unwrap_or(default)

    @staticmethod
    def json_nested_int(
        data: t.JsonMapping,
        *keys: str,
        default: int = 0,
    ) -> int:
        """Extract an integer from a nested mapping path."""
        parsed = u.parse(
            FlextCliUtilitiesJson.json_walk_path(data, keys),
            int,
            default=default,
        ).unwrap_or(default)
        return int(parsed) if isinstance(parsed, bool) else parsed

    @staticmethod
    def json_get_str_key(
        mapping: t.JsonMapping,
        key: str,
        *,
        default: str = "",
        case: str | None = None,
    ) -> str:
        """Extract and normalize a string key from a mapping."""
        raw = FlextCliUtilitiesJson.json_pick_str(mapping, key, default)
        return u.normalize(raw, case=case)

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
                FlextCliUtilitiesJson._json_sort_keys(value) if sort_keys else value
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
    def _json_sort_keys(data: t.JsonValue) -> t.JsonValue:
        """Recursively sort dictionary keys in a JSON structure."""
        if isinstance(data, Mapping):
            validated = t.Cli.JSON_MAPPING_ADAPTER.validate_python(data)
            return {
                key: FlextCliUtilitiesJson._json_sort_keys(
                    t.Cli.JSON_VALUE_ADAPTER.validate_python(value)
                )
                for key, value in sorted(validated.items())
            }
        if isinstance(data, list):
            items = t.Cli.JSON_LIST_ADAPTER.validate_python(data)
            return [
                FlextCliUtilitiesJson._json_sort_keys(
                    t.Cli.JSON_VALUE_ADAPTER.validate_python(item)
                )
                for item in items
            ]
        return data


__all__: list[str] = ["FlextCliUtilitiesJson"]
