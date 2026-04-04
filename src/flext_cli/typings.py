"""FlextCli type definitions module - PEP 695 type aliases."""

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

from flext_core import FlextTypes


class FlextCliTypes(FlextTypes):
    """FlextCli type definitions extending FlextTypes via inheritance.

    RULES:
    ───────
    1. TypeVars outside the class (only case allowed)
    2. PEP 695 type aliases inside nested classes
    3. Complex types composed with Protocols
    4. ZERO simple aliases - use direct types
    5. Inheritance from FlextTypes, no duplication
    """

    class Cli:
        """CLI types namespace for cross-project access.

        Provides organized access to all CLI types for other FLEXT projects.
        Usage: Other projects can reference `FlextCliTypes.Cli.*` via short alias `FlextTypes.Cli.*`.
        This enables consistent namespace patterns for cross-project type access.
        """

        type Scalar = FlextTypes.Scalar
        type StrSequence = FlextTypes.StrSequence
        type RecursiveContainer = FlextTypes.RecursiveContainer
        type DefaultMapping = Mapping[str, Scalar | StrSequence]
        type ValueOrModel = FlextTypes.ValueOrModel
        type JsonValue = FlextTypes.JsonValue
        type JsonMapping = FlextTypes.JsonMapping
        type JsonList = FlextTypes.JsonList
        type JsonDict = FlextTypes.JsonMapping
        type TableMappingRow = FlextTypes.JsonMapping
        type TableSequenceRow = FlextTypes.JsonList
        type TableRow = TableMappingRow | TableSequenceRow
        type TableConfigValue = FlextTypes.ContainerValue
        type TabularData = TableMappingRow | Sequence[TableRow]
        type TableRows = Sequence[TableRow]
        type CliValue = Scalar | StrSequence | Mapping[str, Scalar | StrSequence] | None
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

        # YAML types (YAML parses to same Python types as JSON)
        type YamlDict = FlextTypes.JsonMapping
        type YamlValue = FlextTypes.JsonValue
        type YamlList = FlextTypes.JsonList
        type YamlDumpable = (
            FlextTypes.JsonMapping
            | Mapping[str, FlextTypes.NormalizedValue]
            | FlextTypes.JsonList
            | FlextTypes.JsonValue
        )

        PRIMITIVE_TYPES: ClassVar[
            tuple[type[str], type[int], type[float], type[bool]]
        ] = FlextTypes.PRIMITIVES_TYPES
        SCALAR_TYPES: ClassVar[tuple[type, ...]] = FlextTypes.SCALAR_TYPES

        # JSON adapters — SSOT para todos os projetos
        JSON_VALUE_ADAPTER: ClassVar[TypeAdapter[FlextTypes.JsonValue]] = TypeAdapter(
            FlextTypes.JsonValue
        )
        JSON_MAPPING_ADAPTER: ClassVar[TypeAdapter[FlextTypes.JsonMapping]] = (
            TypeAdapter(FlextTypes.JsonMapping)
        )
        JSON_LIST_ADAPTER: ClassVar[TypeAdapter[FlextTypes.JsonList]] = TypeAdapter(
            FlextTypes.JsonList
        )

        # YAML adapters — delegates to same underlying types as JSON
        YAML_DICT_ADAPTER: ClassVar[TypeAdapter[FlextTypes.JsonMapping]] = TypeAdapter(
            FlextTypes.JsonMapping
        )
        YAML_SEQ_ADAPTER: ClassVar[TypeAdapter[FlextTypes.JsonList]] = TypeAdapter(
            FlextTypes.JsonList
        )

        # ContainerValue adapters (NOT JSON — includes Path/datetime)
        CONTAINER_VALUE_ADAPTER: TypeAdapter[FlextTypes.ContainerValue] = TypeAdapter(
            FlextTypes.ContainerValue
        )
        CONTAINER_NORMALIZE_ADAPTER: ClassVar[
            TypeAdapter[FlextTypes.ContainerValue]
        ] = TypeAdapter(FlextTypes.ContainerValue)


t = FlextCliTypes

__all__ = ["FlextCliTypes", "t"]
