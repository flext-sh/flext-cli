"""CLI base type aliases and adapters."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from pathlib import Path
from types import GenericAlias, UnionType
from typing import ClassVar, Literal, TypeAliasType

from pydantic.fields import FieldInfo
from rich.console import Console as RichConsole
from rich.tree import Tree as RichTree
from tomlkit.container import Container
from tomlkit.items import AoT, Array, Item, Table
from tomlkit.toml_document import TOMLDocument
from typer import Typer
from typer.models import OptionInfo
from typer.testing import CliRunner

from flext_cli import c
from flext_core import m, t


class FlextCliTypesBase:
    """Base CLI aliases shared across services and models."""

    type Scalar = t.Scalar
    type StrSequence = t.StrSequence
    type RecursiveContainer = t.Container
    type DefaultMapping = Mapping[str, Scalar | StrSequence | None]
    type ValueOrModel = t.ValueOrModel
    type JsonValue = t.JsonValue
    type JsonMapping = Mapping[str, JsonValue]
    type JsonList = Sequence[JsonValue]
    type JsonDict = JsonMapping
    type TableMappingRow = JsonMapping
    type TableSequenceRow = JsonList
    type TableRow = TableMappingRow | TableSequenceRow
    type TableConfigValue = t.ContainerValue
    type TabularData = TableMappingRow | Sequence[TableRow]
    type TableRows = Sequence[TableRow]
    type TableShowIndex = bool | str | Sequence[str | int]
    type TableDisableNumparse = bool | Sequence[int]
    type TableColAlign = Sequence[str | None] | None
    type CliValue = Scalar | StrSequence | DefaultMapping | None
    type CliDefaultSource = CliValue | Path
    type FieldInfoMapping = Mapping[str, FieldInfo]
    type CliAnnotations = MutableMapping[str, type | GenericAlias]
    type CliApp = Typer
    type CliOptionInfo = OptionInfo

    # Literal types derived from nested StrEnum authorities
    type OutputFormatLiteral = Literal[
        c.Cli.OutputFormats.JSON,
        c.Cli.OutputFormats.YAML,
        c.Cli.OutputFormats.CSV,
        c.Cli.OutputFormats.TABLE,
        c.Cli.OutputFormats.PLAIN,
    ]
    type MessageTypeLiteral = Literal[
        c.Cli.MessageTypes.INFO,
        c.Cli.MessageTypes.ERROR,
        c.Cli.MessageTypes.WARNING,
        c.Cli.MessageTypes.SUCCESS,
        c.Cli.MessageTypes.DEBUG,
    ]
    type CommandStatusLiteral = Literal[
        c.Cli.CommandStatus.PENDING,
        c.Cli.CommandStatus.RUNNING,
        c.Cli.CommandStatus.COMPLETED,
        c.Cli.CommandStatus.FAILED,
        c.Cli.CommandStatus.CANCELLED,
    ]
    type LogLevelLiteral = Literal[
        c.LogLevel.DEBUG,
        c.LogLevel.INFO,
        c.LogLevel.WARNING,
        c.LogLevel.ERROR,
        c.LogLevel.CRITICAL,
    ]
    type LogVerbosityLiteral = Literal[
        c.Cli.LogVerbosity.COMPACT,
        c.Cli.LogVerbosity.DETAILED,
        c.Cli.LogVerbosity.FULL,
    ]
    type PipelineStageStatusLiteral = Literal[
        c.Cli.PipelineStageStatus.OK,
        c.Cli.PipelineStageStatus.SKIPPED,
        c.Cli.PipelineStageStatus.FAILED,
    ]
    type TabularFormatLiteral = Literal[
        c.Cli.TabularFormat.PLAIN,
        c.Cli.TabularFormat.SIMPLE,
        c.Cli.TabularFormat.GRID,
        c.Cli.TabularFormat.FANCY_GRID,
        c.Cli.TabularFormat.PIPE,
        c.Cli.TabularFormat.ORGTBL,
        c.Cli.TabularFormat.JIRA,
        c.Cli.TabularFormat.PRESTO,
        c.Cli.TabularFormat.PRETTY,
        c.Cli.TabularFormat.PSQL,
        c.Cli.TabularFormat.RST,
        c.Cli.TabularFormat.MEDIAWIKI,
        c.Cli.TabularFormat.MOINMOIN,
        c.Cli.TabularFormat.YOUTRACK,
        c.Cli.TabularFormat.HTML,
        c.Cli.TabularFormat.UNSAFEHTML,
        c.Cli.TabularFormat.LATEX,
        c.Cli.TabularFormat.LATEX_RAW,
        c.Cli.TabularFormat.LATEX_BOOKTABS,
        c.Cli.TabularFormat.LATEX_LONGTABLE,
        c.Cli.TabularFormat.TEXTILE,
        c.Cli.TabularFormat.TSV,
        c.Cli.TabularFormat.TABLE,
    ]
    type StyleLiteral = Literal[
        c.Cli.MessageStyles.BLUE,
        c.Cli.MessageStyles.GREEN,
        c.Cli.MessageStyles.RED,
        c.Cli.MessageStyles.YELLOW,
        c.Cli.MessageStyles.CYAN,
        c.Cli.MessageStyles.WHITE,
        c.Cli.MessageStyles.DIM,
        c.Cli.MessageStyles.BOLD,
        c.Cli.MessageStyles.BOLD_BLUE,
        c.Cli.MessageStyles.BOLD_GREEN,
        c.Cli.MessageStyles.BOLD_RED,
        c.Cli.MessageStyles.BOLD_YELLOW,
        c.Cli.MessageStyles.BOLD_CYAN,
        c.Cli.MessageStyles.BOLD_WHITE,
        c.Cli.MessageStyles.BOLD_MAGENTA,
    ]

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

    type RuntimeAnnotation = type | GenericAlias | UnionType | TypeAliasType | None
    type RuntimeValue = t.Container

    type YamlDict = t.JsonMapping
    type YamlValue = t.RecursiveValue
    type YamlList = t.JsonList
    type YamlDumpable = (
        t.JsonMapping | Mapping[str, t.Container] | t.JsonList | t.RecursiveValue
    )

    PRIMITIVE_TYPES: ClassVar[tuple[type[str], type[int], type[float], type[bool]]] = (
        t.PRIMITIVES_TYPES
    )
    SCALAR_TYPES: ClassVar[tuple[type, ...]] = t.SCALAR_TYPES

    JSON_VALUE_ADAPTER: ClassVar[m.TypeAdapter[JsonValue]] = m.TypeAdapter(JsonValue)
    JSON_MAPPING_ADAPTER: ClassVar[m.TypeAdapter[JsonMapping]] = m.TypeAdapter(
        JsonMapping
    )
    JSON_LIST_ADAPTER: ClassVar[m.TypeAdapter[JsonList]] = m.TypeAdapter(JsonList)
    YAML_DICT_ADAPTER: ClassVar[m.TypeAdapter[t.JsonMapping]] = m.TypeAdapter(
        t.JsonMapping
    )
    YAML_SEQ_ADAPTER: ClassVar[m.TypeAdapter[t.JsonList]] = m.TypeAdapter(t.JsonList)
    CONTAINER_VALUE_ADAPTER: m.TypeAdapter[t.ContainerValue] = m.TypeAdapter(
        t.ContainerValue
    )
    CONTAINER_NORMALIZE_ADAPTER: ClassVar[m.TypeAdapter[t.ContainerValue]] = (
        m.TypeAdapter(t.ContainerValue)
    )
    CLI_DEFAULT_SOURCE_ADAPTER: ClassVar[m.TypeAdapter[CliDefaultSource]] = (
        m.TypeAdapter(CliDefaultSource)
    )


__all__: list[str] = ["FlextCliTypesBase"]
