"""Generic JSON helpers shared through ``u.Cli.json_*``.

Follows the same pattern as ``_utilities/toml.py`` for TOML helpers.
All methods use the ``json_`` prefix for namespace consistency.
"""

from __future__ import annotations

import operator
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import ClassVar, TypeIs

from pydantic import BaseModel, ValidationError

from flext_cli import c, p, r, t
from flext_core import u


class FlextCliUtilitiesJson:
    """Generic JSON read/write and manipulation helpers."""

    _module_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)

    @staticmethod
    def mapping_like(
        value: t.Cli.RecursiveMappingSource,
    ) -> TypeIs[t.Cli.RecursiveMapping]:
        """Narrow values to mapping-like recursive containers."""
        return isinstance(value, Mapping)

    @staticmethod
    def unwrap_root_value(
        value: t.Cli.RecursiveContainer,
    ) -> t.Cli.RecursiveContainer:
        """Unwrap ``RootModel.root`` values without importing Pydantic internals."""
        if hasattr(value, "__dict__"):
            model_dict = value.__dict__
            if "root" in model_dict:
                root_value = model_dict["root"]
                if root_value is not None:
                    return root_value
        return value

    @staticmethod
    def normalize_json_value(
        item: t.Cli.RecursiveContainer,
    ) -> t.Cli.JsonValue:
        """Normalize recursive container values into JSON-compatible output."""
        if isinstance(item, t.Cli.PRIMITIVE_TYPES):
            return item
        if item is None:
            return ""
        source = FlextCliUtilitiesJson.unwrap_root_value(item)
        if FlextCliUtilitiesJson.mapping_like(source):
            return {
                str(key): FlextCliUtilitiesJson.normalize_json_value(value)
                for key, value in source.items()
            }
        if isinstance(source, Sequence) and not isinstance(source, (str, bytes)):
            return [
                FlextCliUtilitiesJson.normalize_json_value(value) for value in source
            ]
        return str(item)

    @staticmethod
    def json_read(path: Path) -> p.Result[t.Cli.JsonMapping]:
        """Read and parse a JSON file.

        Returns empty mapping if file does not exist.
        """
        if not path.exists():
            return r[t.Cli.JsonMapping].ok({})
        try:
            raw = path.read_text(encoding=c.Cli.ENCODING_DEFAULT)
            loaded: t.Cli.JsonValue = t.Cli.JSON_VALUE_ADAPTER.validate_json(raw)
        except (ValidationError, OSError) as exc:
            return r[t.Cli.JsonMapping].fail(f"json_read: {exc}")
        if not isinstance(loaded, Mapping):
            return r[t.Cli.JsonMapping].fail("json_read: root must be an object")
        try:
            return r[t.Cli.JsonMapping].ok(
                t.Cli.JSON_MAPPING_ADAPTER.validate_python(loaded),
            )
        except c.ValidationError as exc:
            return r[t.Cli.JsonMapping].fail(f"json_read validation: {exc}")

    @staticmethod
    def json_write(
        path: Path,
        payload: t.Cli.JsonPayload,
        *,
        sort_keys: bool = False,
        ensure_ascii: bool = False,
        indent: int = 2,
    ) -> p.Result[bool]:
        """Write a JSON payload to a file. Creates parent dirs as needed."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            materialized: t.Cli.JsonValue
            if isinstance(payload, BaseModel):
                materialized = payload.model_dump(mode="json")
            elif isinstance(payload, Mapping):
                materialized = {
                    str(key): FlextCliUtilitiesJson.normalize_json_value(value)
                    for key, value in payload.items()
                }
            elif isinstance(payload, Sequence) and not isinstance(
                payload, (str, bytes)
            ):
                materialized = [
                    FlextCliUtilitiesJson.normalize_json_value(value)
                    for value in payload
                ]
            else:
                materialized = t.Cli.JSON_VALUE_ADAPTER.validate_python(payload)
            validated: t.Cli.JsonValue = t.Cli.JSON_VALUE_ADAPTER.validate_python(
                materialized,
            )
            normalized = (
                FlextCliUtilitiesJson._json_sort_keys(validated)
                if sort_keys
                else validated
            )
            content = (
                t.Cli.JSON_VALUE_ADAPTER.dump_json(
                    normalized,
                    indent=indent,
                    ensure_ascii=ensure_ascii,
                ).decode(
                    c.Cli.ENCODING_DEFAULT,
                )
                + "\n"
            )
            _ = path.write_text(content, encoding=c.Cli.ENCODING_DEFAULT)
        except (TypeError, ValueError, ValidationError, OSError) as exc:
            FlextCliUtilitiesJson._module_logger.debug(
                "json_write failed",
                error=str(exc),
                exc_info=False,
            )
            return r[bool].fail(f"json_write: {exc}")
        return r[bool].ok(True)

    @staticmethod
    def json_parse(text: str) -> p.Result[t.Cli.JsonValue]:
        """Parse a JSON string into a validated JsonValue."""
        try:
            return r[t.Cli.JsonValue].ok(
                t.Cli.JSON_VALUE_ADAPTER.validate_json(text),
            )
        except (ValidationError, ValueError) as exc:
            return r[t.Cli.JsonValue].fail(f"json_parse: {exc}")

    @staticmethod
    def json_normalize(
        value: t.Cli.JsonValueOrModel,
    ) -> t.Cli.JsonValue:
        """Normalize a value to a JSON-serializable form."""
        if value is None:
            return None
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        return value

    @staticmethod
    def _json_sort_keys(data: t.Cli.JsonValue) -> t.Cli.JsonValue:
        """Recursively sort dictionary keys in a JSON structure."""
        if isinstance(data, Mapping):
            validated = t.Cli.JSON_MAPPING_ADAPTER.validate_python(data)
            return {
                k: FlextCliUtilitiesJson._json_sort_keys(v)
                for k, v in sorted(validated.items(), key=operator.itemgetter(0))
            }
        if isinstance(data, list):
            items = t.Cli.JSON_LIST_ADAPTER.validate_python(data)
            return [FlextCliUtilitiesJson._json_sort_keys(item) for item in items]
        return data


__all__: list[str] = ["FlextCliUtilitiesJson"]
