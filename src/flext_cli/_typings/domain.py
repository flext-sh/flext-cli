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

from flext_cli import FlextCliConstantsEnums, FlextCliTypesBase, p


class FlextCliTypesDomain:
    """Composite CLI aliases built from canonical protocols and core types."""

    type ResultValue = t.RuntimeData | Sequence[t.RuntimeData]
    type RuleDefinition = FlextCliTypesBase.JsonMapping
    type RuleDefinitions = Sequence[RuleDefinition]
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
    type MatchedRuleDefinition[TKind] = tuple[TKind, FlextCliTypesBase.JsonMapping]
    type MatchedRuleDefinitions[TKind] = Sequence[
        tuple[TKind, FlextCliTypesBase.JsonMapping]
    ]
    type RuleLoadResult[TRuleKind, TFileRuleKind] = tuple[
        Sequence[tuple[TRuleKind, FlextCliTypesBase.JsonMapping]],
        Sequence[tuple[TFileRuleKind, FlextCliTypesBase.JsonMapping]],
    ]
    type ScalarMapping = Mapping[str, t.Scalar]
    type MutableScalarMapping = MutableMapping[str, t.Scalar]
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
    type ModelSource = m.BaseModel | ScalarMapping
    type OptionRegistry = Mapping[
        str,
        Mapping[str, t.Scalar | t.StrSequence],
    ]
    type JsonDefaults = Mapping[str, FlextCliTypesBase.JsonValue]
    type MutableJsonDefaults = MutableMapping[str, FlextCliTypesBase.JsonValue]
    type NullaryOperation[T] = Callable[[], T]
    type PromptTextReader = Callable[[str], str]
    type TextStreamWriter = Callable[[TextIO], None]
    type CliCommand = Callable[..., FlextCliTypesBase.RuntimeValue]
    type JsonCommandFn = Callable[..., p.Result[FlextCliTypesBase.JsonValue]]
    type ResultRouteHandler = Callable[..., p.Cli.ErasedCommandResult]
    type MappingProcessor[T, U] = Callable[[str, T], U]
    type JsonModelHandler[M: m.BaseModel] = Callable[[M], FlextCliTypesBase.JsonValue]
    type MappingSource = t.Container | Mapping[str, t.Container]
    type JsonPayload = (
        FlextCliTypesBase.JsonValue
        | FlextCliTypesBase.JsonLikeMapping
        | Sequence[FlextCliTypesBase.JsonValue]
        | t.Container
        | t.FlatContainerMapping
        | t.FlatContainerList
        | m.BaseModel
    )
    type JsonRuntimeData = FlextCliTypesBase.JsonValue | m.BaseModel
    type TomlMappingSource = (
        t.Container
        | FlextCliTypesBase.JsonLikeMapping
        | FlextCliTypesBase.TomlItem
        | FlextCliTypesBase.TomlDocument
    )
    type TomlUnwrappedSource = t.Container | FlextCliTypesBase.TomlItem
    type TomlStringListSource = TomlUnwrappedSource | Sequence[t.Primitives]
    type TomlRuntimeSource = FlextCliTypesBase.TomlValue | t.Container
    type TypeKind = FlextCliConstantsEnums.TypeKind
    type TypedExtractValue = str | bool | FlextCliTypesBase.JsonMapping
    type ResultCommandRoutes = Sequence[p.Cli.ResultCommandRoute]
    type TableDataSource = (
        FlextCliTypesBase.TabularData | Sequence[Mapping[str, t.Container]]
    )
    type TextPath = str | Path
    type PathLike = str | Path
    type JsonWriteData = JsonPayload | p.Cli.DisplayData


__all__: list[str] = ["FlextCliTypesDomain"]
