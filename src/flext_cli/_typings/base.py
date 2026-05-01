"""CLI base type aliases and adapters."""

from __future__ import annotations

from collections.abc import (
    MutableMapping,
)
from pathlib import Path
from types import GenericAlias, UnionType
from typing import ClassVar, TypeAliasType

from rich.console import Console as RichConsole
from rich.tree import Tree as RichTree
from tomlkit.container import Container
from tomlkit.items import AoT, Array, Item, Table
from tomlkit.toml_document import TOMLDocument
from typer import Typer
from typer.models import OptionInfo
from typer.testing import CliRunner

from flext_core import m, t


class FlextCliTypesBase:
    """Base CLI aliases shared across services and models."""

    type TableMappingRow = t.MappingKV[str, t.JsonPayload]
    type TableSequenceRow = t.SequenceOf[t.JsonPayload]
    type DefaultMapping = t.MappingKV[str, t.Scalar | t.StrSequence]
    type TableRow = TableMappingRow | TableSequenceRow
    type TableConfigValue = (
        t.JsonValue | t.StrSequence | t.SequenceOf[int] | t.SequenceOf[str | int] | None
    )
    type TabularData = TableMappingRow | t.SequenceOf[TableRow]
    type TableRows = t.SequenceOf[TableRow]
    type TableIndexValue = str | int
    type TableIndexSelection = t.SequenceOf[TableIndexValue]
    type TableShowIndex = bool | TableIndexSelection
    type TableDisableNumparse = bool | t.SequenceOf[int]
    type TableColAlign = t.StrSequence | None
    type CliValue = t.Scalar | t.StrSequence | DefaultMapping
    type CliDefaultSource = CliValue | Path
    type CliAnnotations = MutableMapping[str, type | GenericAlias]
    type CliApp = Typer
    type CliOptionInfo = OptionInfo

    type TyperRunner = CliRunner
    type TomlDocument = TOMLDocument
    type TomlTable = Table
    type TomlItem = Item
    type TomlArray = Array
    type TomlAoT = AoT
    type TomlContainer = Container
    type TomlParent = TOMLDocument | Table
    type TomlValue = TOMLDocument | Table | Item | Array | AoT | Container
    type RichTreeType = RichTree
    type RichConsoleType = RichConsole

    type RuntimeAnnotation = type | GenericAlias | UnionType | TypeAliasType

    PRIMITIVE_TYPES: ClassVar[tuple[type[str], type[int], type[float], type[bool]]] = (
        t.PRIMITIVES_TYPES
    )
    SCALAR_TYPES: ClassVar[tuple[type, ...]] = t.SCALAR_TYPES

    STR_SEQUENCE_ADAPTER: ClassVar[t.ValueAdapter[t.StrSequence]] = (
        t.str_sequence_adapter()
    )
    JSON_VALUE_ADAPTER: ClassVar[t.ValueAdapter[t.JsonValue]] = t.json_value_adapter()
    JSON_MAPPING_ADAPTER: ClassVar[t.ValueAdapter[t.JsonMapping]] = (
        t.json_mapping_adapter()
    )
    JSON_LIST_ADAPTER: ClassVar[t.ValueAdapter[t.JsonList]] = t.json_list_adapter()
    type YamlDict = t.JsonMapping
    YAML_DICT_ADAPTER: ClassVar[t.ValueAdapter[t.JsonMapping]] = (
        t.json_mapping_adapter()
    )
    YAML_SEQ_ADAPTER: ClassVar[t.ValueAdapter[t.JsonList]] = t.json_list_adapter()
    CLI_DEFAULT_SOURCE_ADAPTER: ClassVar[t.ValueAdapter[CliDefaultSource]] = (
        m.TypeAdapter(CliDefaultSource)
    )


__all__: list[str] = ["FlextCliTypesBase"]
