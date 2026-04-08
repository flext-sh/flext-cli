"""Generic TOML helpers shared through ``u.Cli.toml_*``."""

from __future__ import annotations

from collections.abc import MutableSequence, Sequence
from pathlib import Path
from typing import ClassVar, TypeIs

import tomlkit
from pydantic import TypeAdapter, ValidationError
from tomlkit import TOMLDocument
from tomlkit.items import AoT, Item as TomlItem, Table as TomlTable

from flext_cli import FlextCliUtilitiesBase, FlextCliUtilitiesJson, c, r, t
from flext_core import FlextLogger, u


class FlextCliUtilitiesToml:
    """Generic TOML read/write and table-manipulation helpers."""

    _module_logger: ClassVar[FlextLogger] = FlextLogger(__name__)
    _STR_SEQUENCE_ADAPTER: TypeAdapter[Sequence[str]] = TypeAdapter(Sequence[str])

    @staticmethod
    def toml_as_mapping(
        value: t.Cli.TomlMappingSource,
    ) -> t.Cli.JsonMapping | None:
        """Normalize a TOML mapping into a typed plain mapping."""
        normalized = FlextCliUtilitiesToml.toml_unwrap_item(value)
        if normalized is None or not u.is_mapping(normalized):
            return None
        try:
            return t.Cli.JSON_MAPPING_ADAPTER.validate_python(normalized)
        except ValidationError:
            return None

    @staticmethod
    def toml_unwrap_item(
        value: t.Cli.TomlMappingSource,
    ) -> t.RecursiveContainer | None:
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
        except ValidationError:
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
    def toml_get_table(
        container: t.Cli.TomlParent,
        key: str,
    ) -> t.Cli.TomlTable | None:
        """Get a table child from a TOML container."""
        if key not in container:
            return None
        value = container[key]
        return value if FlextCliUtilitiesToml.toml_is_table(value) else None

    @staticmethod
    def toml_get_item(
        container: t.Cli.TomlParent,
        key: str,
    ) -> t.Cli.TomlItem | None:
        """Get a raw TOML item from a container."""
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
        existing: t.Cli.TomlItem | t.RecursiveContainer | None = None
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
    def toml_get_table_path(
        parent: t.Cli.TomlParent,
        path: t.StrSequence,
    ) -> t.Cli.TomlTable | None:
        """Return a nested table path without creating missing tables."""
        current: t.Cli.TomlParent = parent
        for segment in path:
            table = FlextCliUtilitiesToml.toml_get_table(current, segment)
            if table is None:
                return None
            current = table
        return current if FlextCliUtilitiesToml.toml_is_table(current) else None

    @staticmethod
    def toml_ensure_tool_table(doc: t.Cli.TomlDocument) -> t.Cli.TomlTable:
        """Return the top-level ``[tool]`` table."""
        return FlextCliUtilitiesToml.toml_ensure_table(doc, "tool")

    @staticmethod
    def toml_get(
        container: t.Cli.TomlParent,
        key: str,
    ) -> t.Cli.JsonValue | None:
        """Get a normalized TOML value from a container."""
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
        current = FlextCliUtilitiesToml.toml_get(container, key)
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
            FlextCliUtilitiesToml.toml_get(container, key),
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
            FlextCliUtilitiesToml.toml_get(container, key),
        )
        merged = sorted({*current, *required})
        if current == merged:
            return False
        container[key] = FlextCliUtilitiesToml.toml_array(merged)
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
            return tomlkit.parse(path.read_text(encoding=c.Cli.Encoding.DEFAULT))
        except (OSError, ValueError) as exc:
            FlextCliUtilitiesToml._module_logger.warning(
                "Failed to read or parse TOML document",
                path=str(path),
                error=str(exc),
                error_type=type(exc).__name__,
            )
            return None

    @staticmethod
    def toml_read_document(path: Path) -> r[t.Cli.TomlDocument]:
        """Read a TOML document with ``r`` semantics."""
        if not path.exists():
            return r[t.Cli.TomlDocument].fail(f"failed to read TOML: {path}")
        doc = FlextCliUtilitiesToml.toml_read(path)
        if doc is None:
            return r[t.Cli.TomlDocument].fail(f"TOML parse failed: {path}")
        return r[t.Cli.TomlDocument].ok(doc)

    @staticmethod
    def toml_read_json(path: Path) -> r[t.Cli.JsonMapping]:
        """Read TOML and return the unwrapped root table as ``JsonMapping``."""
        document_result = FlextCliUtilitiesToml.toml_read_document(path)
        if document_result.is_failure:
            return r[t.Cli.JsonMapping].fail(
                document_result.error or f"TOML parse failed: {path}",
            )
        mapping = FlextCliUtilitiesToml.toml_as_mapping(document_result.value)
        if mapping is None:
            return r[t.Cli.JsonMapping].fail(f"TOML root must be a table: {path}")
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
    def _format_pyproject(path: Path) -> r[bool]:
        """Format managed ``pyproject.toml`` files with taplo when available."""
        if path.name != "pyproject.toml":
            return r[bool].ok(False)
        command = ["taplo", "format"]
        config_path = FlextCliUtilitiesToml._resolve_taplo_config(path)
        if config_path is not None:
            command.extend(["--config", str(config_path)])
        command.append(str(path))
        result = FlextCliUtilitiesBase.run_raw(command, cwd=path.parent)
        if result.is_failure:
            return r[bool].fail(result.error or f"taplo format failed: {path}")
        output = result.value
        if output.exit_code != 0:
            message = (output.stderr or output.stdout).strip()
            return r[bool].fail(message or f"taplo format failed: {path}")
        return r[bool].ok(True)

    @staticmethod
    def toml_write_document(path: Path, doc: t.Cli.TomlDocument) -> r[bool]:
        """Write a TOML document and format managed pyproject files."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            u.write_file(
                path,
                doc.as_string(),
                encoding=c.Cli.Encoding.DEFAULT,
            )
        except OSError as exc:
            return r[bool].fail(f"TOML write error: {exc}")
        format_result = FlextCliUtilitiesToml._format_pyproject(path)
        if format_result.is_failure:
            return r[bool].fail(format_result.error or f"taplo format failed: {path}")
        return r[bool].ok(True)


__all__ = ["FlextCliUtilitiesToml"]
