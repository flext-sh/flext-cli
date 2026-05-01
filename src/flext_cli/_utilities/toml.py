"""Generic TOML helpers shared through ``u.Cli.toml_*``."""

from __future__ import annotations

import tomllib
from collections.abc import (
    Mapping,
    MutableMapping,
    Sequence,
)
from pathlib import Path
from typing import ClassVar, TypeIs

import tomlkit
from tomlkit.items import AoT, Array, Item, Table
from tomlkit.toml_document import TOMLDocument

from flext_cli import FlextCliUtilitiesRuntime as ur, c, p, r, t
from flext_core import u


class FlextCliUtilitiesToml:
    """Generic TOML read/write and table-manipulation helpers."""

    _module_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)

    @staticmethod
    def toml_as_mapping(
        value: t.Cli.TomlMappingSource | None,
    ) -> t.JsonMapping | None:
        """Normalize a TOML mapping into a typed plain mapping."""
        normalized = FlextCliUtilitiesToml.toml_unwrap_item(value)
        if normalized is None or not u.mapping(normalized):
            return None
        try:
            return t.Cli.JSON_MAPPING_ADAPTER.validate_python(normalized)
        except c.ValidationError:
            return None

    @staticmethod
    def toml_unwrap_item(
        value: t.Cli.TomlMappingSource | t.JsonValue | None,
    ) -> t.JsonValue | None:
        """Unwrap TOML items and documents to plain Python values."""
        if value is None:
            return None
        if isinstance(value, Mapping) and not isinstance(value, TOMLDocument | Item):
            return u.normalize_to_json_value(value)
        normalized = value.unwrap() if isinstance(value, TOMLDocument | Item) else value
        if isinstance(normalized, Item):
            return None
        return u.normalize_to_json_value(normalized)

    @staticmethod
    def toml_as_string_list(
        value: t.Cli.TomlStringListSource | None,
    ) -> t.StrSequence:
        """Normalize a TOML array into a string sequence."""
        normalized: t.Cli.TomlStringListSource | None = (
            value.unwrap() if isinstance(value, TOMLDocument | Item) else value
        )
        if normalized is None or isinstance(normalized, str | bytes):
            return []
        if not isinstance(normalized, Sequence):
            return []
        return [str(item) for item in normalized]

    @staticmethod
    def toml_array(items: t.StrSequence) -> Array:
        """Create a multiline TOML array."""
        array = tomlkit.array()
        for item in items:
            array.add_line(item)
        return array.multiline(True)

    @staticmethod
    def toml_document() -> TOMLDocument:
        """Create a new TOML document."""
        return tomlkit.document()

    @staticmethod
    def toml_table() -> Table:
        """Create a new explicit TOML table."""
        return tomlkit.table()

    @staticmethod
    def toml_aot() -> AoT:
        """Create a new TOML array-of-tables."""
        return tomlkit.aot()

    @staticmethod
    def toml_parse_text(text: str) -> TOMLDocument | None:
        """Parse TOML text, returning ``None`` on invalid input."""
        try:
            return tomlkit.parse(text)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def toml_mapping_from_text(text: str) -> t.JsonMapping | None:
        """Parse TOML text into one validated plain mapping."""
        try:
            loaded = tomllib.loads(text)
        except tomllib.TOMLDecodeError:
            return None
        try:
            return t.Cli.JSON_MAPPING_ADAPTER.validate_python(loaded)
        except c.ValidationError:
            return None

    @staticmethod
    def toml_document_from_mapping(mapping: t.JsonMapping) -> TOMLDocument:
        """Build one TOML document from a validated plain mapping."""
        document = FlextCliUtilitiesToml.toml_document()
        for key, value in mapping.items():
            document[key] = FlextCliUtilitiesToml._toml_item_from_json_value(value)
        return document

    @staticmethod
    def _toml_item_from_json_value(
        value: t.JsonValue,
    ) -> Item | t.JsonValue:
        """Convert one JSON-compatible value into one TOML runtime value."""
        if value is None:
            msg = "TOML does not support null values"
            raise TypeError(msg)
        if isinstance(value, bool | int | float | str):
            return tomlkit.item(value)
        if isinstance(value, list):
            return tomlkit.item(value)
        return tomlkit.item(value)

    @staticmethod
    def toml_is_document(
        value: t.Cli.TomlRuntimeSource,
    ) -> TypeIs[TOMLDocument]:
        """Return True when the value is a TOML document."""
        return isinstance(value, TOMLDocument)

    @staticmethod
    def toml_is_table(
        value: t.Cli.TomlRuntimeSource,
    ) -> TypeIs[Table]:
        """Return True when the value is a TOML table."""
        return isinstance(value, Table)

    @staticmethod
    def toml_is_item(
        value: t.Cli.TomlRuntimeSource,
    ) -> TypeIs[Item]:
        """Return True when the value is a TOML item."""
        return isinstance(value, Item)

    @staticmethod
    def toml_is_aot(
        value: t.Cli.TomlRuntimeSource,
    ) -> TypeIs[AoT]:
        """Return True when the value is a TOML array-of-tables."""
        return isinstance(value, AoT)

    @staticmethod
    def toml_table_child(
        container: TOMLDocument | Table,
        key: str,
    ) -> Table | None:
        """Return a table child from a TOML container."""
        if key not in container:
            return None
        value = container[key]
        return value if FlextCliUtilitiesToml.toml_is_table(value) else None

    @staticmethod
    def toml_item_child(
        container: TOMLDocument | Table,
        key: str,
    ) -> Item | None:
        """Return a raw TOML item from a container."""
        if key not in container:
            return None
        value = container[key]
        return value if FlextCliUtilitiesToml.toml_is_item(value) else None

    @staticmethod
    def toml_ensure_table(
        parent: TOMLDocument | Table,
        key: str,
    ) -> Table:
        """Return an explicit table child, promoting implicit super-tables when needed."""
        existing: t.Cli.TomlRuntimeSource | None = None
        if key in parent:
            existing = parent[key]
        if existing is not None and isinstance(existing, Table):
            table: Table = existing
            if not table.is_super_table():
                return table
            del parent[key]
            table = FlextCliUtilitiesToml.toml_table()
            for entry_key in list(existing):
                table[entry_key] = existing[entry_key]
            parent[key] = table
            return table
        table = FlextCliUtilitiesToml.toml_table()
        parent[key] = table
        return table

    @staticmethod
    def toml_ensure_path(
        parent: TOMLDocument | Table,
        path: t.StrSequence,
    ) -> Table:
        """Return a nested table path, creating intermediate tables as needed."""
        current: TOMLDocument | Table = parent
        for segment in path:
            current = FlextCliUtilitiesToml.toml_ensure_table(current, segment)
        if FlextCliUtilitiesToml.toml_is_table(current):
            return current
        msg = "toml_ensure_path must return a TOML table"
        raise TypeError(msg)

    @staticmethod
    def toml_table_path(
        parent: TOMLDocument | Table,
        path: t.StrSequence,
    ) -> Table | None:
        """Return a nested table path without creating missing tables."""
        current: TOMLDocument | Table = parent
        for segment in path:
            table = FlextCliUtilitiesToml.toml_table_child(current, segment)
            if table is None:
                return None
            current = table
        return current if FlextCliUtilitiesToml.toml_is_table(current) else None

    @staticmethod
    def toml_ensure_tool_table(doc: TOMLDocument) -> Table:
        """Return the top-level ``[tool]`` table."""
        return FlextCliUtilitiesToml.toml_ensure_table(doc, "tool")

    @staticmethod
    def toml_value(
        container: TOMLDocument | Table,
        key: str,
    ) -> t.JsonValue | None:
        """Return a normalized TOML value from a container."""
        if key not in container:
            return None
        raw_value = FlextCliUtilitiesToml.toml_unwrap_item(container[key])
        if raw_value is None:
            return None
        return raw_value

    @staticmethod
    def toml_mapping_child(
        container: t.MappingKV[str, t.JsonValue],
        key: str,
    ) -> t.JsonMapping | None:
        """Return a plain mapping child from one normalized TOML mapping."""
        value = container.get(key, None)
        if not u.mapping(value):
            return None
        try:
            return t.Cli.JSON_MAPPING_ADAPTER.validate_python(value)
        except c.ValidationError:
            return None

    @staticmethod
    def toml_mapping_ensure_table(
        parent: MutableMapping[str, t.JsonValue],
        key: str,
    ) -> dict[str, t.JsonValue]:
        """Return one mutable plain mapping child, creating it when missing."""
        existing = parent.get(key, None)
        if isinstance(existing, dict):
            return existing
        if u.mapping(existing):
            normalized_table: dict[str, t.JsonValue]
            try:
                normalized_table = dict(
                    t.Cli.JSON_MAPPING_ADAPTER.validate_python(existing)
                )
            except c.ValidationError:
                normalized_table = {}
            parent[key] = normalized_table
            return normalized_table
        table: dict[str, t.JsonValue] = {}
        parent[key] = table
        return table

    @staticmethod
    def toml_mapping_ensure_path(
        parent: MutableMapping[str, t.JsonValue],
        path: t.StrSequence,
    ) -> MutableMapping[str, t.JsonValue]:
        """Return one nested mutable mapping path, creating tables as needed."""
        current = parent
        for segment in path:
            current = FlextCliUtilitiesToml.toml_mapping_ensure_table(
                current,
                segment,
            )
        return current

    @staticmethod
    def toml_mapping_path(
        parent: t.MappingKV[str, t.JsonValue],
        path: t.StrSequence,
    ) -> MutableMapping[str, t.JsonValue] | None:
        """Return one nested mutable mapping path without creating missing tables."""
        current: t.MappingKV[str, t.JsonValue] = parent
        for segment in path:
            value = current.get(segment, None)
            if not isinstance(value, dict):
                return None
            current = value
        return current if isinstance(current, dict) else None

    @staticmethod
    def toml_remove_key_if_present(
        container: TOMLDocument | Table,
        key: str,
    ) -> bool:
        """Remove a TOML key when it exists; return True if removed."""
        if key not in container:
            return False
        del container[key]
        return True

    @staticmethod
    def toml_sync_value(
        container: TOMLDocument | Table,
        key: str,
        expected: t.JsonValue,
    ) -> bool:
        """Synchronize a scalar TOML value; return True if mutated."""
        current = FlextCliUtilitiesToml.toml_value(container, key)
        if current == expected:
            return False
        container[key] = expected
        return True

    @staticmethod
    def toml_sync_string_list(
        container: TOMLDocument | Table,
        key: str,
        expected: t.StrSequence,
        *,
        sort_values: bool = False,
    ) -> bool:
        """Synchronize a TOML string-array value; return True if mutated."""
        current = FlextCliUtilitiesToml.toml_as_string_list(
            FlextCliUtilitiesToml.toml_value(container, key),
        )
        normalized_expected = sorted(expected) if sort_values else [*expected]
        normalized_current = sorted(current) if sort_values else [*current]
        if normalized_current == normalized_expected:
            return False
        container[key] = FlextCliUtilitiesToml.toml_array(normalized_expected)
        return True

    @staticmethod
    def toml_merge_string_list(
        container: TOMLDocument | Table,
        key: str,
        required: t.StrSequence,
    ) -> bool:
        """Merge required values into a TOML string-array; return True if mutated."""
        current = FlextCliUtilitiesToml.toml_as_string_list(
            FlextCliUtilitiesToml.toml_value(container, key),
        )
        merged = sorted({*current, *required})
        if current == merged:
            return False
        container[key] = FlextCliUtilitiesToml.toml_array(merged)
        return True

    @staticmethod
    def toml_mapping_remove_key_if_present(
        container: MutableMapping[str, t.JsonValue],
        key: str,
    ) -> bool:
        """Remove one plain mapping key when it exists; return True if removed."""
        if key not in container:
            return False
        del container[key]
        return True

    @staticmethod
    def toml_mapping_sync_value(
        container: MutableMapping[str, t.JsonValue],
        key: str,
        expected: t.JsonValue,
    ) -> bool:
        """Synchronize a scalar/structured plain TOML value; return True if mutated."""
        current: t.JsonValue = u.normalize_to_json_value(container.get(key, None))
        normalized_expected: t.JsonValue = u.normalize_to_json_value(expected)
        if current == normalized_expected:
            return False
        container[key] = normalized_expected
        return True

    @staticmethod
    def toml_mapping_merge_string_list(
        container: MutableMapping[str, t.JsonValue],
        key: str,
        required: t.StrSequence,
    ) -> bool:
        """Merge required values into a plain string-list; return True if mutated."""
        current = FlextCliUtilitiesToml.toml_as_string_list(container.get(key, None))
        merged = sorted({*current, *required})
        if current == merged:
            return False
        normalized_list: list[t.JsonValue] = list(merged)
        container[key] = normalized_list
        return True

    @staticmethod
    def toml_sync_mapping_table(
        container: TOMLDocument | Table,
        key: str,
        expected: t.MappingKV[str, t.JsonValue],
        *,
        sort_keys: bool = False,
    ) -> bool:
        """Synchronize a TOML table mapping in place; return True if mutated."""
        existing = container.get(key, None)
        current = FlextCliUtilitiesToml.toml_as_mapping(
            existing
            if existing is not None
            and (u.mapping(existing) or isinstance(existing, TOMLDocument | Item))
            else None,
        )
        normalized_expected = {
            item_key: expected[item_key]
            for item_key in (sorted(expected) if sort_keys else tuple(expected))
        }
        if current == normalized_expected:
            return False
        table = FlextCliUtilitiesToml.toml_ensure_table(container, key)
        for existing_key in list(table):
            if existing_key not in normalized_expected:
                del table[existing_key]
        for item_key, item_value in normalized_expected.items():
            table[item_key] = item_value
        return True

    @staticmethod
    def toml_mapping_sync_string_list(
        container: MutableMapping[str, t.JsonValue],
        key: str,
        expected: t.StrSequence,
        *,
        sort_values: bool = False,
    ) -> bool:
        """Synchronize a plain string-list field; return True if mutated."""
        current = FlextCliUtilitiesToml.toml_as_string_list(container.get(key, None))
        normalized_expected = sorted(expected) if sort_values else [*expected]
        normalized_current = sorted(current) if sort_values else [*current]
        if normalized_current == normalized_expected:
            return False
        normalized_list: list[t.JsonValue] = list(normalized_expected)
        container[key] = normalized_list
        return True

    @staticmethod
    def toml_mapping_sync_mapping_table(
        container: MutableMapping[str, t.JsonValue],
        key: str,
        expected: t.MappingKV[str, t.JsonValue],
        *,
        sort_keys: bool = False,
    ) -> bool:
        """Synchronize a plain mapping-table field; return True if mutated."""
        existing = container.get(key, None)
        current = FlextCliUtilitiesToml.toml_as_mapping(
            existing if isinstance(existing, Mapping) else None,
        )
        normalized_expected = {
            item_key: expected[item_key]
            for item_key in (sorted(expected) if sort_keys else tuple(expected))
        }
        if current == normalized_expected:
            return False
        table = FlextCliUtilitiesToml.toml_mapping_ensure_table(container, key)
        stale_keys = [
            existing_key
            for existing_key in table
            if existing_key not in normalized_expected
        ]
        for existing_key in stale_keys:
            del table[existing_key]
        for item_key, item_value in normalized_expected.items():
            table[item_key] = item_value
        return True

    @staticmethod
    def toml_navigate_path(
        doc: TOMLDocument,
        path: t.StrSequence,
    ) -> Table:
        """Navigate to a nested TOML table by path segments.

        Always roots at [tool]. Skips "tool" in path if present.
        Creates intermediate tables as needed.
        """
        return FlextCliUtilitiesToml.toml_ensure_path(
            FlextCliUtilitiesToml.toml_ensure_tool_table(doc),
            [segment for segment in path if segment != "tool"],
        )

    @staticmethod
    def toml_dot_path(*parts: str) -> str:
        """Build one dotted TOML path from non-empty segments."""
        return ".".join(part for part in parts if part)

    @staticmethod
    def toml_table_prefix(path: t.StrSequence) -> str:
        """Build a dotted prefix string from table path (e.g. "tool.ruff.lint")."""
        return FlextCliUtilitiesToml.toml_dot_path(
            "tool",
            *(segment for segment in path if segment != "tool"),
        )

    @staticmethod
    def toml_read(path: Path) -> TOMLDocument | None:
        """Read a TOML document, returning ``None`` on missing or invalid files."""
        if not path.exists():
            return None
        try:
            return tomlkit.parse(path.read_text(encoding=c.Cli.ENCODING_DEFAULT))
        except (OSError, ValueError) as exc:
            FlextCliUtilitiesToml._module_logger.warning(
                "Failed to read or parse TOML document",
                path=str(path),
                error=str(exc),
                error_type=type(exc).__name__,
            )
            return None

    @staticmethod
    def toml_read_document(path: Path) -> p.Result[TOMLDocument]:
        """Read a TOML document with ``r`` semantics."""
        if not path.exists():
            return r[TOMLDocument].fail(f"failed to read TOML: {path}")
        doc = FlextCliUtilitiesToml.toml_read(path)
        if doc is None:
            return r[TOMLDocument].fail(f"TOML parse failed: {path}")
        return r[TOMLDocument].ok(doc)

    @staticmethod
    def toml_read_json(path: Path) -> p.Result[t.JsonMapping]:
        """Read TOML and return the unwrapped root table as ``JsonMapping``."""
        if not path.exists():
            return r[t.JsonMapping].fail(f"failed to read TOML: {path}")
        try:
            original_rendered = path.read_text(encoding=c.Cli.ENCODING_DEFAULT)
        except OSError as exc:
            return r[t.JsonMapping].fail(f"failed to read TOML: {exc}")
        mapping = FlextCliUtilitiesToml.toml_mapping_from_text(original_rendered)
        if mapping is None:
            return r[t.JsonMapping].fail(f"TOML parse failed: {path}")
        return r[t.JsonMapping].ok(mapping)

    @staticmethod
    def _resolve_taplo_config(path: Path) -> Path | None:
        """Resolve the nearest ``.taplo.toml`` for a pyproject file."""
        resolved = path.resolve()
        for candidate in (resolved.parent, *resolved.parents):
            config_path = candidate / ".taplo.toml"
            if config_path.is_file():
                return config_path
        return None

    @staticmethod
    def _format_pyproject(path: Path) -> p.Result[bool]:
        """Format managed ``pyproject.toml`` files with taplo when available."""
        if path.name != "pyproject.toml":
            return r[bool].ok(False)
        command = ["taplo", "format"]
        config_path = FlextCliUtilitiesToml._resolve_taplo_config(path)
        if config_path is not None:
            command.extend(["--config", str(config_path)])
        command.append(str(path))
        result = ur.run_raw(command, cwd=path.parent)
        if result.failure:
            return r[bool].fail(result.error or f"taplo format failed: {path}")
        output = result.value
        if output.exit_code != 0:
            message = (output.stderr or output.stdout).strip()
            return r[bool].fail(message or f"taplo format failed: {path}")
        return r[bool].ok(True)

    @staticmethod
    def toml_write_document(path: Path, doc: TOMLDocument) -> p.Result[bool]:
        """Write a TOML document and format managed pyproject files."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            u.write_file(
                path,
                doc.as_string(),
                encoding=c.Cli.ENCODING_DEFAULT,
            )
        except OSError as exc:
            return r[bool].fail(f"TOML write error: {exc}")
        format_result = FlextCliUtilitiesToml._format_pyproject(path)
        if format_result.failure:
            return r[bool].fail(format_result.error or f"taplo format failed: {path}")
        return r[bool].ok(True)

    @staticmethod
    def toml_write_mapping(path: Path, mapping: t.JsonMapping) -> p.Result[bool]:
        """Write one validated plain mapping as TOML through the canonical writer."""
        try:
            document = FlextCliUtilitiesToml.toml_document_from_mapping(mapping)
        except (TypeError, ValueError) as exc:
            return r[bool].fail(f"TOML build error: {exc}")
        return FlextCliUtilitiesToml.toml_write_document(path, document)


__all__: list[str] = ["FlextCliUtilitiesToml"]
