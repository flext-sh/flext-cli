"""CLI protocol-backed composite aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Literal, TextIO

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from flext_cli import FlextCliTypesBase, p
from flext_core import t


class FlextCliTypesDomain:
    """Composite CLI aliases built from canonical protocols and core types."""

    type JsonValueResult = p.Result[t.JsonValue]
    type JsonMappingResult = p.Result[t.JsonMapping]
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
    type StrEnvMapping = Mapping[str, str]
    type ConfigModel = BaseModel | None
    type ModelSource = BaseModel | ScalarMapping | None
    type OptionRegistry = Mapping[
        str,
        Mapping[str, t.Scalar | t.StrSequence],
    ]
    type FieldMetadataSource = FieldInfo | t.JsonMapping | t.JsonValue
    type JsonDefaults = Mapping[str, t.JsonValue]
    type MutableJsonDefaults = MutableMapping[str, t.JsonValue]
    type NullaryOperation[T] = Callable[[], T]
    type TextStreamWriter = Callable[[TextIO], None]
    type MappingProcessor[T, U] = Callable[[str, T], U]
    type JsonModelHandler[M: BaseModel] = Callable[[M], t.JsonValue]
    type RecursiveMapping = Mapping[str, t.RecursiveContainer]
    type RecursiveMappingSource = t.RecursiveContainer | RecursiveMapping | None
    type JsonPayload = t.JsonValue | BaseModel | t.JsonMapping | t.JsonList
    type JsonValueOrModel = t.JsonValue | BaseModel | None
    type TomlMappingSource = (
        t.RecursiveContainer
        | FlextCliTypesBase.TomlItem
        | FlextCliTypesBase.TomlDocument
        | None
    )
    type TomlUnwrappedSource = t.RecursiveContainer | FlextCliTypesBase.TomlItem | None
    type TomlRuntimeSource = FlextCliTypesBase.TomlValue | t.RecursiveContainer | None
    type TypeKind = Literal["str", "bool", "dict"]
    type ReturnChildLiteral = Literal[True]
    type TypedExtractValue = str | bool | t.JsonMapping | None
    type ResultCommandRoutes = Sequence[p.Cli.ResultCommandRoute]
    type TableDataSource = FlextCliTypesBase.TabularData | Sequence[t.ContainerMapping]
    type TextPath = str | Path
    type JsonWriteData = (
        t.RecursiveContainer | Sequence[t.ContainerMapping] | p.Cli.DisplayData
    )


__all__ = ["FlextCliTypesDomain"]
