"""CLI protocol-backed composite aliases."""

from __future__ import annotations

from collections.abc import (
    Callable,
    Mapping,
    MutableMapping,
    Sequence,
)
from pathlib import Path

from tomlkit.container import Container
from tomlkit.items import AoT, Array, Item, Table
from tomlkit.toml_document import TOMLDocument

from flext_cli import p
from flext_cli._constants.enums import FlextCliConstantsEnums
from flext_cli._protocols.base import FlextCliProtocolsBase
from flext_cli._typings.base import FlextCliTypesBase
from flext_core import m, t


class FlextCliTypesDomain:
    """Composite CLI aliases built from canonical protocols and core types."""

    type ResultValue = t.JsonPayload | Sequence[t.JsonPayload]
    type RuleDefinitions = Sequence[t.JsonMapping]
    type RuleMatcher = tuple[
        frozenset[str],
        frozenset[str],
        frozenset[str],
        frozenset[str],
    ]
    type RuleMatchers = Sequence[RuleMatcher]
    type RuleCatalog[TKind] = Mapping[
        TKind,
        Sequence[tuple[frozenset[str], frozenset[str], frozenset[str], frozenset[str]]],
    ]
    type MatchedRuleDefinition[TKind] = tuple[TKind, t.JsonMapping]
    type MatchedRuleDefinitions[TKind] = Sequence[tuple[TKind, t.JsonMapping]]
    type RuleLoadResult[TRuleKind, TFileRuleKind] = tuple[
        Sequence[tuple[TRuleKind, t.JsonMapping]],
        Sequence[tuple[TFileRuleKind, t.JsonMapping]],
    ]
    type MutableDefaultMapping = MutableMapping[
        str,
        t.Scalar | t.StrSequence,
    ]
    type CliParamValue = bool | str
    type CliParamKwargs = Mapping[str, CliParamValue]
    type DefaultAtom = t.Scalar | t.StrSequence
    type ProjectNamesValue = str | t.StrSequence
    type TableHeaders = str | t.StrSequence
    type IntTextValue = int | str
    type ModelSource = m.BaseModel | t.ScalarMapping
    type OptionRegistry = Mapping[
        str,
        Mapping[str, t.Scalar | t.StrSequence],
    ]
    type NullaryOperation[T] = Callable[[], T]
    type PromptTextReader = Callable[[str], str]
    type CliCommand = Callable[..., t.JsonPayload]
    type JsonCommandFn = Callable[..., p.Result[t.JsonPayload]]
    type ResultRouteHandler = Callable[..., FlextCliProtocolsBase.ErasedCommandResult]
    type MappingProcessor[T, U] = Callable[[str, T], U]
    type TomlMappingSource = (
        t.JsonPayload | t.JsonMapping | t.ScalarMapping | Item | TOMLDocument
    )
    type TomlUnwrappedSource = t.JsonPayload | t.JsonMapping | Item
    type TomlStringListSource = (
        TomlUnwrappedSource | Sequence[t.JsonPayload] | Sequence[t.Primitives]
    )
    type TomlRuntimeSource = (
        TOMLDocument
        | Table
        | Item
        | Array
        | AoT
        | Container
        | t.JsonMapping
        | t.JsonPayload
    )
    type TypeKind = FlextCliConstantsEnums.TypeKind
    type TypedExtractValue = str | bool | t.JsonMapping
    type TableDataSource = FlextCliTypesBase.TabularData | Sequence[t.JsonMapping]
    type TextPath = str | Path
    type JsonWriteData = t.JsonPayload | p.Cli.DisplayData


__all__: list[str] = ["FlextCliTypesDomain"]
