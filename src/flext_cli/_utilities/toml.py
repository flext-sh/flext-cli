"""Generic TOML helpers shared through ``u.Cli.toml_*``."""

from __future__ import annotations

import tomllib
from collections.abc import (
    Mapping,
    MutableMapping,
    MutableSequence,
)
from pathlib import Path
from typing import ClassVar, TypeIs

import tomlkit
from tomlkit import TOMLDocument
from tomlkit.items import AoT, Item as TomlItem, Table as TomlTable

from flext_cli import FlextCliUtilitiesJson, FlextCliUtilitiesRuntime, c, p, r, t
from flext_core import m, u


class FlextCliUtilitiesToml:
    """Generic TOML read/write and table-manipulation helpers."""

    _module_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)
    _STR_SEQUENCE_ADAPTER: m.TypeAdapter[t.StrSequence] = m.TypeAdapter(t.StrSequence)

    @staticmethod
    def toml_as_mapping(
        value: t.Cli.TomlMappingSource,
    ) -> t.Cli.JsonMapping | None:
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
        value: t.Cli.TomlMappingSource,
    ) -> t.Container | None:
        """Unwrap TOML items and documents to plain Python values."""
        normalized: t.Cli.TomlUnwrappedSource = value
        if FlextCliUtilitiesToml.toml_is_document(
            value,
        ) or FlextCliUtilitiesToml.toml_is_item(value):
            normalized = value.unwrap()
        if FlextCliUtilitiesToml.toml_is_item(normalized):
            return None
        return normalized

    @staticmethod
    def toml_as_string_list(
        value: t.Cli.TomlUnwrappedSource,
    ) -> t.StrSequence:
        """Normalize a TOML array into a string sequence."""
        normalized = FlextCliUtilitiesToml.toml_unwrap_item(value)
        if normalized is None or isinstance(normalized, str):
            return []
        try:
            items = FlextCliUtilitiesToml._STR_SEQUENCE_ADAPTER.validate_python(
                normalized,
            )
        except c.ValidationError:
            return []
        return [str(item) for item in items]

    @staticmethod
    def toml_array(items: t.StrSequence) -> t.Cli.TomlArray:
        """Create a multiline TOML array."""
        array = tomlkit.array()
        for item in items:
            array.add_line(item)
        return array.multiline(True)

    @staticmethod
    def toml_document() -> t.Cli.TomlDocument:
        """Create a new TOML document."""
        return tomlkit.document()

    @staticmethod
    def toml_table() -> t.Cli.TomlTable:
        """Create a new explicit TOML table."""
        return tomlkit.table()

    @staticmethod
    def toml_aot() -> t.Cli.TomlAoT:
        """Create a new TOML array-of-tables."""
        return tomlkit.aot()

    @staticmethod
    def toml_parse_text(text: str) -> t.Cli.TomlDocument | None:
        """Parse TOML text, returning ``None`` on invalid input."""
        try:
            return tomlkit.parse(text)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def toml_mapping_from_text(text: str) -> t.Cli.JsonMapping | None:
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
    def toml_document_from_mapping(mapping: t.Cli.JsonMapping) -> t.Cli.TomlDocument:
        """Build one TOML document from a validated plain mapping."""
        document = FlextCliUtilitiesToml.toml_document()
        for key, value in mapping.items():
            document[key] = FlextCliUtilitiesToml._toml_item_from_json_value(value)
        return document

    @staticmethod
    def _toml_item_from_json_value(
        value: t.Cli.JsonValue,
    ) -> t.Cli.TomlItem | t.Container:
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
    ) -> TypeIs[t.Cli.TomlDocument]:
        """Return True when the value is a TOML document."""
        return isinstance(value, TOMLDocument)

    @staticmethod
    def toml_is_table(
        value: t.Cli.TomlRuntimeSource,
    ) -> TypeIs[t.Cli.TomlTable]:
        """Return True when the value is a TOML table."""
        return isinstance(value, TomlTable)

    @staticmethod
    def toml_is_item(
        value: t.Cli.TomlRuntimeSource,
    ) -> TypeIs[t.Cli.TomlItem]:
        """Return True when the value is a TOML item."""
        return isinstance(value, TomlItem)

    @staticmethod
    def toml_is_aot(
        value: t.Cli.TomlRuntimeSource,
    ) -> TypeIs[t.Cli.TomlAoT]:
        """Return True when the value is a TOML array-of-tables."""
        return isinstance(value, AoT)

    @staticmethod
    def toml_table_child(
        container: t.Cli.TomlParent,
        key: str,
    ) -> t.Cli.TomlTable | None:
        """Return a table child from a TOML container."""
        if key not in container:
            return None
        value = container[key]
        return value if FlextCliUtilitiesToml.toml_is_table(value) else None

    @staticmethod
    def toml_item_child(
        container: t.Cli.TomlParent,
        key: str,
    ) -> t.Cli.TomlItem | None:
        """Return a raw TOML item from a container."""
        if key not in container:
            return None
        value = container[key]
        return value if FlextCliUtilitiesToml.toml_is_item(value) else None

    @staticmethod
    def toml_ensure_table(
        parent: t.Cli.TomlParent,
        key: str,
    ) -> t.Cli.TomlTable:
        """Return an explicit table child, promoting implicit super-tables when needed."""
        existing: t.Cli.TomlItem | t.Container | None = None
        if key in parent:
            existing = parent[key]
        if FlextCliUtilitiesToml.toml_is_table(existing):
            if not existing.is_super_table():
                return existing
            del parent[key]
            table = FlextCliUtilitiesToml.toml_table()
            for entry_key in FlextCliUtilitiesToml.toml_table_string_keys(existing):
                table[entry_key] = existing[entry_key]
            parent[key] = table
            return table
        table = FlextCliUtilitiesToml.toml_table()
        parent[key] = table
        return table

    @staticmethod
    def toml_ensure_path(
        parent: t.Cli.TomlParent,
        path: t.StrSequence,
    ) -> t.Cli.TomlTable:
        """Return a nested table path, creating intermediate tables as needed."""
        current: t.Cli.TomlParent = parent
        for segment in path:
            current = FlextCliUtilitiesToml.toml_ensure_table(current, segment)
        if FlextCliUtilitiesToml.toml_is_table(current):
            return current
        msg = "toml_ensure_path must return a TOML table"
        raise TypeError(msg)

    @staticmethod
    def toml_table_path(
        parent: t.Cli.TomlParent,
        path: t.StrSequence,
    ) -> t.Cli.TomlTable | None:
        """Return a nested table path without creating missing tables."""
        current: t.Cli.TomlParent = parent
        for segment in path:
            table = FlextCliUtilitiesToml.toml_table_child(current, segment)
            if table is None:
                return None
            current = table
        return current if FlextCliUtilitiesToml.toml_is_table(current) else None

    @staticmethod
    def toml_ensure_tool_table(doc: t.Cli.TomlDocument) -> t.Cli.TomlTable:
        """Return the top-level ``[tool]`` table."""
        return FlextCliUtilitiesToml.toml_ensure_table(doc, "tool")

    @staticmethod
    def toml_value(
        container: t.Cli.TomlParent,
        key: str,
    ) -> t.Cli.JsonValue | None:
        """Return a normalized TOML value from a container."""
        if key not in container:
            return None
        raw_value = FlextCliUtilitiesToml.toml_unwrap_item(container[key])
        if raw_value is None:
            return None
        return FlextCliUtilitiesJson.normalize_json_value(raw_value)

    @staticmethod
    def toml_table_string_keys(table: t.Cli.TomlTable) -> t.StrSequence:
        """Return string keys for a TOML table."""
        return list(table)

    @staticmethod
    def toml_mapping_child(
        container: Mapping[str, t.Cli.JsonValue],
        key: str,
    ) -> t.Cli.JsonMapping | None:
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
        parent: MutableMapping[str, t.Cli.JsonValue],
        key: str,
    ) -> dict[str, t.Cli.JsonValue]:
        """Return one mutable plain mapping child, creating it when missing."""
        existing = parent.get(key, None)
        if isinstance(existing, dict):
            return existing
        if u.mapping(existing):
            try:
                normalized = dict(t.Cli.JSON_MAPPING_ADAPTER.validate_python(existing))
            except c.ValidationError:
                normalized: dict[str, t.Cli.JsonValue] = {}
            parent[key] = normalized
            return normalized
        table: dict[str, t.Cli.JsonValue] = {}
        parent[key] = table
        return table

    @staticmethod
    def toml_mapping_ensure_path(
        parent: MutableMapping[str, t.Cli.JsonValue],
        path: t.StrSequence,
    ) -> MutableMapping[str, t.Cli.JsonValue]:
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
        parent: Mapping[str, t.Cli.JsonValue],
        path: t.StrSequence,
    ) -> MutableMapping[str, t.Cli.JsonValue] | None:
        """Return one nested mutable mapping path without creating missing tables."""
        current: Mapping[str, t.Cli.JsonValue] = parent
        for segment in path:
            value = current.get(segment, None)
            if not isinstance(value, dict):
                return None
            current = value
        return current if isinstance(current, dict) else None

    @staticmethod
    def toml_remove_key_if_present(
        container: t.Cli.TomlParent,
        key: str,
        changes: MutableSequence[str],
        change_message: str,
    ) -> bool:
        """Remove a TOML key when it exists and record the change."""
        if key not in container:
            return False
        del container[key]
        changes.append(change_message)
        return True

    @staticmethod
    def toml_sync_value(
        container: t.Cli.TomlParent,
        key: str,
        expected: t.Cli.JsonValue,
        changes: MutableSequence[str],
        change_message: str,
    ) -> bool:
        """Synchronize a scalar TOML value."""
        current = FlextCliUtilitiesToml.toml_value(container, key)
        if current == expected:
            return False
        container[key] = expected
        changes.append(change_message)
        return True

    @staticmethod
    def toml_sync_string_list(
        container: t.Cli.TomlParent,
        key: str,
        expected: t.StrSequence,
        changes: MutableSequence[str],
        change_message: str,
        *,
        sort_values: bool = False,
    ) -> bool:
        """Synchronize a TOML string-array value."""
        current = FlextCliUtilitiesToml.toml_as_string_list(
            FlextCliUtilitiesToml.toml_value(container, key),
        )
        normalized_expected = sorted(expected) if sort_values else [*expected]
        normalized_current = sorted(current) if sort_values else [*current]
        if normalized_current == normalized_expected:
            return False
        container[key] = FlextCliUtilitiesToml.toml_array(normalized_expected)
        changes.append(change_message)
        return True

    @staticmethod
    def toml_merge_string_list(
        container: t.Cli.TomlParent,
        key: str,
        required: t.StrSequence,
        changes: MutableSequence[str],
        change_message: str,
    ) -> bool:
        """Merge required values into a TOML string-array field."""
        current = FlextCliUtilitiesToml.toml_as_string_list(
            FlextCliUtilitiesToml.toml_value(container, key),
        )
        merged = sorted({*current, *required})
        if current == merged:
            return False
        container[key] = FlextCliUtilitiesToml.toml_array(merged)
        changes.append(change_message)
        return True

    @staticmethod
    def toml_mapping_remove_key_if_present(
        container: MutableMapping[str, t.Cli.JsonValue],
        key: str,
        changes: MutableSequence[str],
        change_message: str,
    ) -> bool:
        """Remove one plain mapping key when it exists and record the change."""
        if key not in container:
            return False
        del container[key]
        changes.append(change_message)
        return True

    @staticmethod
    def toml_mapping_sync_value(
        container: MutableMapping[str, t.Cli.JsonValue],
        key: str,
        expected: t.Cli.JsonValue,
        changes: MutableSequence[str],
        change_message: str,
    ) -> bool:
        """Synchronize one scalar or structured plain TOML value."""
        current = FlextCliUtilitiesJson.normalize_json_value(container.get(key, None))
        normalized_expected = FlextCliUtilitiesJson.normalize_json_value(expected)
        if current == normalized_expected:
            return False
        container[key] = normalized_expected
        changes.append(change_message)
        return True

    @staticmethod
    def toml_mapping_merge_string_list(
        container: MutableMapping[str, t.Cli.JsonValue],
        key: str,
        required: t.StrSequence,
        changes: MutableSequence[str],
        change_message: str,
    ) -> bool:
        """Merge required values into one plain string-list field."""
        current = FlextCliUtilitiesToml.toml_as_string_list(container.get(key, None))
        merged = sorted({*current, *required})
        if current == merged:
            return False
        normalized_list: list[t.Cli.JsonValue] = list(merged)
        container[key] = normalized_list
        changes.append(change_message)
        return True

    @staticmethod
    def toml_sync_mapping_table(
        container: t.Cli.TomlParent,
        key: str,
        expected: Mapping[str, t.Cli.JsonValue],
        changes: MutableSequence[str],
        change_message: str,
        *,
        sort_keys: bool = False,
    ) -> bool:
        """Synchronize a TOML table mapping in place."""
        existing = container.get(key, None)
        current = FlextCliUtilitiesToml.toml_as_mapping(existing)
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
        changes.append(change_message)
        return True

    @staticmethod
    def toml_mapping_sync_string_list(
        container: MutableMapping[str, t.Cli.JsonValue],
        key: str,
        expected: t.StrSequence,
        changes: MutableSequence[str],
        change_message: str,
        *,
        sort_values: bool = False,
    ) -> bool:
        """Synchronize one plain string-list field in a normalized TOML mapping."""
        current = FlextCliUtilitiesToml.toml_as_string_list(container.get(key, None))
        normalized_expected = sorted(expected) if sort_values else [*expected]
        normalized_current = sorted(current) if sort_values else [*current]
        if normalized_current == normalized_expected:
            return False
        normalized_list: list[t.Cli.JsonValue] = list(normalized_expected)
        container[key] = normalized_list
        changes.append(change_message)
        return True

    @staticmethod
    def toml_mapping_sync_mapping_table(
        container: MutableMapping[str, t.Cli.JsonValue],
        key: str,
        expected: Mapping[str, t.Cli.JsonValue],
        changes: MutableSequence[str],
        change_message: str,
        *,
        sort_keys: bool = False,
    ) -> bool:
        """Synchronize one plain mapping-table field in a normalized TOML mapping."""
        current = FlextCliUtilitiesToml.toml_as_mapping(container.get(key, None))
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
        changes.append(change_message)
        return True

    @staticmethod
    def toml_navigate_path(
        doc: t.Cli.TomlDocument,
        path: t.StrSequence,
    ) -> t.Cli.TomlTable:
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
    def toml_read(path: Path) -> t.Cli.TomlDocument | None:
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
    def toml_read_document(path: Path) -> p.Result[t.Cli.TomlDocument]:
        """Read a TOML document with ``r`` semantics."""
        if not path.exists():
            return r[t.Cli.TomlDocument].fail(f"failed to read TOML: {path}")
        doc = FlextCliUtilitiesToml.toml_read(path)
        if doc is None:
            return r[t.Cli.TomlDocument].fail(f"TOML parse failed: {path}")
        return r[t.Cli.TomlDocument].ok(doc)

    @staticmethod
    def toml_read_json(path: Path) -> p.Result[t.Cli.JsonMapping]:
        """Read TOML and return the unwrapped root table as ``JsonMapping``."""
        if not path.exists():
            return r[t.Cli.JsonMapping].fail(f"failed to read TOML: {path}")
        try:
            original_rendered = path.read_text(encoding=c.Cli.ENCODING_DEFAULT)
        except OSError as exc:
            return r[t.Cli.JsonMapping].fail(f"failed to read TOML: {exc}")
        mapping = FlextCliUtilitiesToml.toml_mapping_from_text(original_rendered)
        if mapping is None:
            return r[t.Cli.JsonMapping].fail(f"TOML parse failed: {path}")
        return r[t.Cli.JsonMapping].ok(mapping)

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
        result = FlextCliUtilitiesRuntime.run_raw(command, cwd=path.parent)
        if result.failure:
            return r[bool].fail(result.error or f"taplo format failed: {path}")
        output = result.value
        if output.exit_code != 0:
            message = (output.stderr or output.stdout).strip()
            return r[bool].fail(message or f"taplo format failed: {path}")
        return r[bool].ok(True)

    @staticmethod
    def toml_write_document(path: Path, doc: t.Cli.TomlDocument) -> p.Result[bool]:
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
    def toml_write_mapping(path: Path, mapping: t.Cli.JsonMapping) -> p.Result[bool]:
        """Write one validated plain mapping as TOML through the canonical writer."""
        try:
            document = FlextCliUtilitiesToml.toml_document_from_mapping(mapping)
        except (TypeError, ValueError) as exc:
            return r[bool].fail(f"TOML build error: {exc}")
        return FlextCliUtilitiesToml.toml_write_document(path, document)


__all__: list[str] = ["FlextCliUtilitiesToml"]
