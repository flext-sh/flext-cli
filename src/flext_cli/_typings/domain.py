"""CLI protocol-backed composite aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Literal, TextIO

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from flext_cli import FlextCliProtocols as p, FlextCliTypesBase as cli_t
from flext_core import r, t


class FlextCliTypesDomain:
    """Composite CLI aliases built from canonical protocols and core types."""

    type ResultValue = t.ValueOrModel | Sequence[t.ValueOrModel]
    type JsonValueResult = p.Result[cli_t.JsonValue]
    type JsonMappingResult = p.Result[cli_t.JsonMapping]
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
    type FieldMetadataSource = FieldInfo | cli_t.JsonMapping | cli_t.JsonValue
    type JsonDefaults = Mapping[str, cli_t.JsonValue]
    type MutableJsonDefaults = MutableMapping[str, cli_t.JsonValue]
    type NullaryOperation[T] = Callable[[], T]
    type TextStreamWriter = Callable[[TextIO], None]
    type CliCommand = Callable[..., cli_t.RuntimeValue]
    type JsonCommandFn = Callable[..., r[t.RecursiveValue] | None]
    type ResultRouteHandler = Callable[..., p.Cli.ErasedCommandResult]
    type MappingProcessor[T, U] = Callable[[str, T], U]
    type JsonModelHandler[M: BaseModel] = Callable[[M], t.RecursiveValue]
    type RecursiveMapping = Mapping[str, t.RecursiveContainer]
    type RecursiveMappingSource = t.RecursiveContainer | RecursiveMapping | None
    type JsonPayload = (
        cli_t.JsonValue
        | BaseModel
        | cli_t.JsonMapping
        | cli_t.JsonList
        | Mapping[str, t.NormalizedValue]
    )
    type JsonValueOrModel = cli_t.JsonValue | BaseModel | None
    type TomlMappingSource = (
        t.RecursiveContainer | cli_t.TomlItem | cli_t.TomlDocument | None
    )
    type TomlUnwrappedSource = t.RecursiveContainer | cli_t.TomlItem | None
    type TomlRuntimeSource = cli_t.TomlValue | t.RecursiveContainer | None
    type TypeKind = Literal["str", "bool", "dict"]
    type ReturnChildLiteral = Literal[True]
    type TypedExtractValue = str | bool | cli_t.JsonMapping | None
    type ResultCommandRoutes = Sequence[p.Cli.ResultCommandRoute]
    type TableDataSource = cli_t.TabularData | Sequence[t.ContainerMapping]
    type TextPath = str | Path
    type JsonWriteData = (
        t.RecursiveContainer | Sequence[t.ContainerMapping] | p.Cli.DisplayData
    )


__all__ = ["FlextCliTypesDomain"]
