"""CLI protocol-backed composite aliases."""

from __future__ import annotations

from collections.abc import (
    Callable,
    MutableMapping,
)
from pathlib import Path

from tomlkit.container import Container
from tomlkit.items import AoT, Array, Item, Table
from tomlkit.toml_document import TOMLDocument

from flext_cli import FlextCliProtocolsBase as pb, FlextCliTypesBase as tb
from flext_cli._constants.enums import FlextCliConstantsEnums
from flext_cli._protocols.domain import FlextCliProtocolsDomain
from flext_core import m, p, t


class FlextCliTypesDomain:
    """Composite CLI aliases built from canonical protocols and core types."""

    type ResultValue = t.JsonPayload | t.SequenceOf[t.JsonPayload]
    type RuleDefinitions = t.SequenceOf[t.JsonMapping]
    type RuleMatcher = tuple[
        frozenset[str],
        frozenset[str],
        frozenset[str],
        frozenset[str],
    ]
    type RuleMatchers = t.SequenceOf[RuleMatcher]
    type RuleCatalog[TKind] = t.MappingKV[
        TKind,
        t.SequenceOf[
            tuple[frozenset[str], frozenset[str], frozenset[str], frozenset[str]]
        ],
    ]
    type MatchedRuleDefinition[TKind] = tuple[TKind, t.JsonMapping]
    type MatchedRuleDefinitions[TKind] = t.SequenceOf[tuple[TKind, t.JsonMapping]]
    type RuleLoadResult[TRuleKind, TFileRuleKind] = tuple[
        t.SequenceOf[tuple[TRuleKind, t.JsonMapping]],
        t.SequenceOf[tuple[TFileRuleKind, t.JsonMapping]],
    ]
    type MutableDefaultMapping = MutableMapping[
        str,
        t.Scalar | t.StrSequence,
    ]
    type CliParamValue = bool | str
    type CliParamKwargs = t.MappingKV[str, CliParamValue]
    type DefaultAtom = t.Scalar | t.StrSequence
    type ProjectNamesValue = str | t.StrSequence
    type TableHeaders = str | t.StrSequence
    type IntTextValue = int | str
    type ModelSource = m.BaseModel | t.ScalarMapping
    type OptionRegistry = t.MappingKV[
        str,
        t.MappingKV[str, t.Scalar | t.StrSequence],
    ]
    type NullaryOperation[T] = Callable[[], T]
    type PromptTextReader = Callable[[str], str]
    type CliCommand = Callable[..., t.JsonPayload]
    type JsonCommandFn = Callable[..., p.Result[t.JsonPayload]]
    type ResultRouteHandler = Callable[..., pb.ErasedCommandResult]
    type MappingProcessor[T, U] = Callable[[str, T], U]
    type TomlMappingSource = (
        t.JsonPayload | t.JsonMapping | t.ScalarMapping | Item | TOMLDocument
    )
    type TomlUnwrappedSource = t.JsonPayload | t.JsonMapping | Item
    type TomlStringListSource = (
        TomlUnwrappedSource | t.SequenceOf[t.JsonPayload] | t.SequenceOf[t.Primitives]
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
    type TableDataSource = tb.TabularData | t.SequenceOf[t.JsonMapping]
    type TextPath = str | Path
    type JsonWriteData = t.JsonPayload | FlextCliProtocolsDomain.DisplayData


__all__: list[str] = ["FlextCliTypesDomain"]
