"""CLI protocol-backed composite aliases."""

from __future__ import annotations

from collections.abc import (
    Callable,
    Mapping,
    MutableMapping,
    Sequence,
)
from pathlib import Path
from typing import Literal, TextIO

from pydantic.fields import FieldInfo

from flext_cli import FlextCliConstantsEnums, p
from flext_cli._typings.base import FlextCliTypesBase
from flext_core import m, t


class FlextCliTypesDomain:
    """Composite CLI aliases built from canonical protocols and core types."""

    type ResultValue = t.ValueOrModel | Sequence[t.ValueOrModel]
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
    type FieldMetadataSource = (
        FieldInfo | FlextCliTypesBase.JsonMapping | FlextCliTypesBase.JsonValue
    )
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
        | Sequence[FlextCliTypesBase.JsonLikeValue]
        | t.Container
        | t.FlatContainerMapping
        | t.FlatContainerList
        | m.BaseModel
    )
    type JsonValueOrModel = FlextCliTypesBase.JsonValue | m.BaseModel
    type TomlMappingSource = (
        t.Container | FlextCliTypesBase.TomlItem | FlextCliTypesBase.TomlDocument
    )
    type TomlUnwrappedSource = t.Container | FlextCliTypesBase.TomlItem
    type TomlRuntimeSource = FlextCliTypesBase.TomlValue | t.Container
    type TypeKind = Literal[
        FlextCliConstantsEnums.TypeKind.STR,
        FlextCliConstantsEnums.TypeKind.BOOL,
        FlextCliConstantsEnums.TypeKind.DICT,
    ]
    type TypedExtractValue = str | bool | FlextCliTypesBase.JsonMapping
    type ResultCommandRoutes = Sequence[p.Cli.ResultCommandRoute]
    type TableDataSource = (
        FlextCliTypesBase.TabularData | Sequence[Mapping[str, t.Container]]
    )
    type TextPath = str | Path
    type PathLike = str | Path
    type JsonWriteData = (
        t.Container | Sequence[Mapping[str, t.Container]] | p.Cli.DisplayData
    )


__all__: list[str] = ["FlextCliTypesDomain"]
