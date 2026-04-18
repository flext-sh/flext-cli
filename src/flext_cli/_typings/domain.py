"""CLI protocol-backed composite aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Literal, TextIO

from pydantic.fields import FieldInfo

from flext_cli import FlextCliConstantsEnums, FlextCliTypesBase, p
from flext_core import m, t


class FlextCliTypesDomain:
    """Composite CLI aliases built from canonical protocols and core types."""

    type ResultValue = t.ValueOrModel | Sequence[t.ValueOrModel]
    type JsonValueResult = p.Result[FlextCliTypesBase.JsonValue]
    type JsonMappingResult = p.Result[FlextCliTypesBase.JsonMapping]
    type ScalarMapping = Mapping[str, t.Scalar]
    type MutableScalarMapping = MutableMapping[str, t.Scalar]
    type MutableDefaultMapping = MutableMapping[
        str,
        t.Scalar | t.StrSequence,
    ]
    type CliParamValue = bool | str | None
    type CliParamKwargs = Mapping[str, CliParamValue]
    type DefaultAtom = t.Scalar | t.StrSequence | None
    type ProjectNamesValue = str | t.StrSequence | None
    type TableHeaders = str | t.StrSequence | None
    type IntTextValue = int | str | None
    type StrEnvMapping = t.StrMapping
    type ConfigModel = m.BaseModel | None
    type ModelSource = m.BaseModel | ScalarMapping | None
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
    type JsonCommandFn = Callable[..., p.Result[t.RecursiveValue] | None]
    type ResultRouteHandler = Callable[..., p.Cli.ErasedCommandResult]
    type MappingProcessor[T, U] = Callable[[str, T], U]
    type JsonModelHandler[M: m.BaseModel] = Callable[[M], t.RecursiveValue]
    type RecursiveMapping = t.RecursiveContainerMapping
    type RecursiveMappingSource = t.RecursiveContainer | RecursiveMapping | None
    type JsonPayload = (
        FlextCliTypesBase.JsonValue
        | m.BaseModel
        | FlextCliTypesBase.JsonMapping
        | FlextCliTypesBase.JsonList
        | Mapping[str, t.RecursiveContainer]
    )
    type JsonValueOrModel = FlextCliTypesBase.JsonValue | m.BaseModel | None
    type TomlMappingSource = (
        t.RecursiveContainer
        | FlextCliTypesBase.TomlItem
        | FlextCliTypesBase.TomlDocument
        | None
    )
    type TomlUnwrappedSource = t.RecursiveContainer | FlextCliTypesBase.TomlItem | None
    type TomlRuntimeSource = FlextCliTypesBase.TomlValue | t.RecursiveContainer | None
    type TypeKind = Literal[
        FlextCliConstantsEnums.TypeKind.STR,
        FlextCliConstantsEnums.TypeKind.BOOL,
        FlextCliConstantsEnums.TypeKind.DICT,
    ]
    type ReturnChildLiteral = Literal[True]
    type TypedExtractValue = str | bool | FlextCliTypesBase.JsonMapping | None
    type ResultCommandRoutes = Sequence[p.Cli.ResultCommandRoute]
    type TableDataSource = (
        FlextCliTypesBase.TabularData | Sequence[t.RecursiveContainerMapping]
    )
    type TextPath = str | Path
    type PathLike = str | Path
    type JsonWriteData = (
        t.RecursiveContainer | Sequence[t.RecursiveContainerMapping] | p.Cli.DisplayData
    )


__all__: list[str] = ["FlextCliTypesDomain"]
