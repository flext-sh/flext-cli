"""CLI base type aliases and adapters."""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableMapping,
    Sequence,
)
from pathlib import Path
from types import GenericAlias, UnionType
from typing import ClassVar, TypeAliasType

from flext_core import m, t
from tomlkit.container import Container
from tomlkit.items import AoT, Array, Item, Table
from tomlkit.toml_document import TOMLDocument

from rich.console import Console as RichConsole
from rich.tree import Tree as RichTree
from typer import Typer
from typer.models import OptionInfo
from typer.testing import CliRunner


class FlextCliTypesBase:
    """Base CLI aliases shared across services and models."""

    type Scalar = t.Scalar
    type StrSequence = t.StrSequence
    type JsonScalar = (
        t.Container
        | Mapping[str, t.Container]
        | Sequence[t.Container]
        | Sequence[Mapping[str, t.Container]]
    )
    type JsonValue = t.JsonValue
    type JsonMapping = Mapping[str, JsonValue]
    type JsonLikeMapping = Mapping[str, JsonValue]
    type JsonList = Sequence[JsonValue]
    type JsonContainer = JsonValue
    type DefaultMapping = Mapping[str, Scalar | StrSequence]
    type ValueOrModel = t.ValueOrModel
    type JsonDict = JsonMapping
    type TableMappingRow = JsonMapping
    type TableSequenceRow = JsonList
    type TableRow = TableMappingRow | TableSequenceRow
    type TableConfigValue = (
        t.Container | Sequence[str] | Sequence[int] | Sequence[str | int] | None
    )
    type TabularData = TableMappingRow | Sequence[TableRow]
    type TableRows = Sequence[TableRow]
    type TableShowIndex = bool | str | Sequence[str | int]
    type TableDisableNumparse = bool | Sequence[int]
    type TableColAlign = Sequence[str] | None
    type CliValue = Scalar | StrSequence | DefaultMapping
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
    type RuntimeValue = t.Container

    type YamlDict = JsonMapping
    type YamlValue = JsonValue
    type YamlList = JsonList
    type YamlDumpable = (
        JsonValue
        | JsonMapping
        | JsonList
        | t.Container
        | t.FlatContainerMapping
        | t.FlatContainerList
    )

    PRIMITIVE_TYPES: ClassVar[tuple[type[str], type[int], type[float], type[bool]]] = (
        t.PRIMITIVES_TYPES
    )
    SCALAR_TYPES: ClassVar[tuple[type, ...]] = t.SCALAR_TYPES

    STR_SEQUENCE_ADAPTER: ClassVar[t.ValueAdapter[StrSequence]] = (
        t.str_sequence_adapter()
    )
    JSON_VALUE_ADAPTER: ClassVar[t.ValueAdapter[JsonValue]] = t.json_value_adapter()
    JSON_MAPPING_ADAPTER: ClassVar[t.ValueAdapter[JsonMapping]] = (
        t.json_mapping_adapter()
    )
    JSON_LIST_ADAPTER: ClassVar[t.ValueAdapter[JsonList]] = t.json_list_adapter()
    YAML_DICT_ADAPTER: ClassVar[t.ValueAdapter[JsonMapping]] = t.json_mapping_adapter()
    YAML_SEQ_ADAPTER: ClassVar[t.ValueAdapter[JsonList]] = t.json_list_adapter()
    CLI_DEFAULT_SOURCE_ADAPTER: ClassVar[t.ValueAdapter[CliDefaultSource]] = (
        m.TypeAdapter(CliDefaultSource)
    )


__all__: list[str] = ["FlextCliTypesBase"]
