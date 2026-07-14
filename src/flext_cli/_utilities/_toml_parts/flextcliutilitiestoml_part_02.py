"""Generic TOML helpers shared through ``u.Cli.toml_*``."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeIs

import tomlkit
from tomlkit.items import AoT, Item, Table
from tomlkit.toml_document import TOMLDocument

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliUtilitiesToml:
    """Implementation part for FlextCliUtilitiesToml."""

    @staticmethod
    def toml_item_from_json_value(value: t.JsonValue) -> Item | t.JsonValue:
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
    def toml_is_document(value: t.Cli.TomlRuntimeSource) -> TypeIs[TOMLDocument]:
        """Return True when the value is a TOML document."""
        return isinstance(value, TOMLDocument)

    @staticmethod
    def toml_is_table(value: t.Cli.TomlRuntimeSource) -> TypeIs[Table]:
        """Return True when the value is a TOML table."""
        return isinstance(value, Table)

    @staticmethod
    def toml_is_item(value: t.Cli.TomlRuntimeSource) -> TypeIs[Item]:
        """Return True when the value is a TOML item."""
        return isinstance(value, Item)

    @staticmethod
    def toml_is_aot(value: t.Cli.TomlRuntimeSource) -> TypeIs[AoT]:
        """Return True when the value is a TOML array-of-tables."""
        return isinstance(value, AoT)

    @staticmethod
    def toml_table_child(container: TOMLDocument | Table, key: str) -> Table | None:
        """Return a table child from a TOML container."""
        if key not in container:
            return None
        value = container[key]
        return value if FlextCliUtilitiesToml.toml_is_table(value) else None

    @staticmethod
    def toml_item_child(container: TOMLDocument | Table, key: str) -> Item | None:
        """Return a raw TOML item from a container."""
        if key not in container:
            return None
        value = container[key]
        return value if FlextCliUtilitiesToml.toml_is_item(value) else None

    @staticmethod
    def toml_ensure_table(parent: TOMLDocument | Table, key: str) -> Table:
        """Return a table child without replacing TOMLKit super-tables."""
        existing: t.Cli.TomlRuntimeSource | None = None
        if key in parent:
            existing = parent[key]
        if isinstance(existing, Table):
            # NOTE(mro-wkii.17.26, agent codex): replacing a super-table copies
            # TOMLKit trivia and adds blank lines on every conform pass. A super
            # table is mutable and materializes its explicit header when needed.
            return existing
        table = tomlkit.table()
        parent[key] = table
        return table

    @staticmethod
    def toml_ensure_path(parent: TOMLDocument | Table, path: t.StrSequence) -> Table:
        """Return a nested table path, creating intermediate tables as needed."""
        current: TOMLDocument | Table = parent
        for segment in path:
            current = FlextCliUtilitiesToml.toml_ensure_table(current, segment)
        if FlextCliUtilitiesToml.toml_is_table(current):
            return current
        msg = "toml_ensure_path must return a TOML table"
        raise TypeError(msg)


__all__: list[str] = ["FlextCliUtilitiesToml"]
