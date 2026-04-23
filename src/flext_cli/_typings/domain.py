"""CLI protocol-backed composite aliases."""

from __future__ import annotations

from collections.abc import (
    Callable,
    Mapping,
    MutableMapping,
    Sequence,
)
from pathlib import Path
from typing import TextIO

from flext_core import m, t
from flext_core._typings.services import FlextTypesServices as ts

from flext_cli import FlextCliConstantsEnums, FlextCliTypesBase, p
from flext_cli._protocols.base import FlextCliProtocolsBase


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
    type TextStreamWriter = Callable[[TextIO], None]
    type CliCommand = Callable[..., ts.JsonPayload]
    type JsonCommandFn = Callable[..., p.Result[ts.JsonPayload]]
    type ResultRouteHandler = Callable[..., FlextCliProtocolsBase.ErasedCommandResult]
    type MappingProcessor[T, U] = Callable[[str, T], U]
    type JsonModelHandler[M: m.BaseModel] = Callable[[M], ts.JsonPayload]
    type MappingSource = ts.JsonPayload
    type TomlMappingSource = (
        ts.JsonPayload
        | t.JsonMapping
        | t.ScalarMapping
        | FlextCliTypesBase.TomlItem
        | FlextCliTypesBase.TomlDocument
    )
    type TomlUnwrappedSource = (
        ts.JsonPayload | t.JsonMapping | FlextCliTypesBase.TomlItem
    )
    type TomlStringListSource = (
        TomlUnwrappedSource | Sequence[ts.JsonPayload] | Sequence[t.Primitives]
    )
    type TomlRuntimeSource = (
        FlextCliTypesBase.TomlValue | t.JsonMapping | ts.JsonPayload
    )
    type TypeKind = FlextCliConstantsEnums.TypeKind
    type TypedExtractValue = str | bool | t.JsonMapping
    type ResultCommandRoutes = Sequence[p.Cli.ResultCommandRoute]
    type TableDataSource = FlextCliTypesBase.TabularData | Sequence[t.JsonMapping]
    type TextPath = str | Path
    type JsonWriteData = ts.JsonPayload | p.Cli.DisplayData


__all__: list[str] = ["FlextCliTypesDomain"]
