"""Generic JSON helpers shared through ``u.Cli.json_*``.

Follows the same pattern as ``_utilities/toml.py`` for TOML helpers.
All methods use the ``json_`` prefix for namespace consistency.
"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    Sequence,
)
from typing import TYPE_CHECKING, ClassVar

from flext_cli import c, m, p, r, t
from flext_cli._utilities._json_parts.flextcliutilitiesjson_part_03 import (
    FlextCliUtilitiesJson as FlextCliUtilitiesJsonPart03,
)
from flext_core import u

if TYPE_CHECKING:
    from pathlib import Path


class FlextCliUtilitiesJson(FlextCliUtilitiesJsonPart03):
    """Implementation part for FlextCliUtilitiesJson."""

    _module_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)

    @staticmethod
    def normalize_json_value(item: t.JsonPayload) -> t.JsonValue:
        """Normalize any runtime value to JSON-compatible output (Pydantic-native)."""
        return u.normalize_to_json_value(item)

    @staticmethod
    def _json_write_content(
        payload: t.JsonPayload,
        options: m.Cli.JsonWriteOptions,
    ) -> str:
        """Serialize a JSON payload using canonical write options."""
        validated = FlextCliUtilitiesJson.normalize_json_value(payload)
        normalized = (
            FlextCliUtilitiesJson.json_sort_keys(validated)
            if options.sort_keys
            else validated
        )
        payload_bytes: bytes = t.Cli.JSON_VALUE_ADAPTER.dump_json(
            normalized,
            indent=options.indent,
            ensure_ascii=options.ensure_ascii,
        )
        return payload_bytes.decode(c.Cli.ENCODING_DEFAULT) + "\n"

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
            content = FlextCliUtilitiesJson._json_write_content(payload, opts)
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
        return t.Cli.JSON_MAPPING_ADAPTER.validate_python(normalized)

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
        return t.Cli.JSON_LIST_ADAPTER.validate_python(normalized)


__all__: list[str] = ["FlextCliUtilitiesJson"]
