"""CLI base type aliases and adapters."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from types import GenericAlias
from typing import ClassVar

from pydantic import TypeAdapter
from pydantic.fields import FieldInfo
from rich.console import Console as RichConsole
from rich.tree import Tree as RichTree
from tomlkit.container import Container
from tomlkit.items import AoT, Array, Item, Table
from tomlkit.toml_document import TOMLDocument
from typer import Typer
from typer.models import OptionInfo
from typer.testing import CliRunner

from flext_core import t


class FlextCliTypesBase:
    """Base CLI aliases shared across services and models."""

    type Scalar = t.Scalar
    type StrSequence = t.StrSequence
    type RecursiveContainer = t.RecursiveContainer
    type DefaultMapping = Mapping[str, Scalar | StrSequence | None]
    type ValueOrModel = t.ValueOrModel
    type JsonValue = t.JsonValue
    type JsonMapping = t.JsonMapping
    type JsonList = t.JsonList
    type JsonDict = JsonMapping
    type TableMappingRow = JsonMapping
    type TableSequenceRow = JsonList
    type TableRow = TableMappingRow | TableSequenceRow
    type TableConfigValue = t.ContainerValue
    type TabularData = TableMappingRow | Sequence[TableRow]
    type TableRows = Sequence[TableRow]
    type TableShowIndex = bool | str | Sequence[str | int]
    type TableDisableNumparse = bool | Sequence[int]
    type CliValue = Scalar | StrSequence | DefaultMapping | None
    type FieldInfoMapping = Mapping[str, FieldInfo]
    type TyperAnnotations = MutableMapping[str, type | GenericAlias]
    type TyperApp = Typer
    type TyperOptionInfo = OptionInfo
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

    type YamlDict = t.JsonMapping
    type YamlValue = t.JsonValue
    type YamlList = t.JsonList
    type YamlDumpable = (
        t.JsonMapping | Mapping[str, t.NormalizedValue] | t.JsonList | t.JsonValue
    )

    PRIMITIVE_TYPES: ClassVar[tuple[type[str], type[int], type[float], type[bool]]] = (
        t.PRIMITIVES_TYPES
    )
    SCALAR_TYPES: ClassVar[tuple[type, ...]] = t.SCALAR_TYPES

    JSON_VALUE_ADAPTER: ClassVar[TypeAdapter[t.JsonValue]] = TypeAdapter(t.JsonValue)
    JSON_MAPPING_ADAPTER: ClassVar[TypeAdapter[t.JsonMapping]] = TypeAdapter(
        t.JsonMapping
    )
    JSON_LIST_ADAPTER: ClassVar[TypeAdapter[t.JsonList]] = TypeAdapter(t.JsonList)
    YAML_DICT_ADAPTER: ClassVar[TypeAdapter[t.JsonMapping]] = TypeAdapter(t.JsonMapping)
    YAML_SEQ_ADAPTER: ClassVar[TypeAdapter[t.JsonList]] = TypeAdapter(t.JsonList)
    CONTAINER_VALUE_ADAPTER: TypeAdapter[t.ContainerValue] = TypeAdapter(
        t.ContainerValue
    )
    CONTAINER_NORMALIZE_ADAPTER: ClassVar[TypeAdapter[t.ContainerValue]] = TypeAdapter(
        t.ContainerValue
    )


__all__ = ["FlextCliTypesBase"]
