"""FlextCli models module - Pydantic models with StrEnuFlextCliModels."""

from __future__ import annotations

import inspect
import operator
import types
from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence
from typing import (
    Annotated,
    ClassVar,
    Literal,
    Self,
    TypeIs,
    Union,
    get_args,
    get_origin,
    override,
)

import typer
from flext_core import FlextLogger, FlextModels, r
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    TypeAdapter,
    ValidationError,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic.fields import FieldInfo
from rich.errors import ConsoleError, LiveError, StyleError
from typer.models import OptionInfo

from flext_cli import FlextCliModelsStatistics, FlextCliModelsSystemContext, c, p, t

_logger = FlextLogger(__name__)


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels.

    NAMESPACE HIERARCHY PADRAO:
    ───────────────────────────
    1. Heranca real de FlextModels, SEM BaseModel direto
    2. Namespace hierarquico: FlextCliModels.Cli.Entity, FlextCliModels.Cli.Value, etc.
    3. SEM duplicacao de declaracoes ou aliases de raiz
    4. ConfigDict frozen=True, extra="forbid"
    5. StrEnum de constants, nao criar novos
    6. field_validator para validacao complexa
    7. Self para metodos de transformacao
    """

    class Cli(FlextCliModelsStatistics, FlextCliModelsSystemContext):
        """CLI project namespace - PADRAO HIERARQUICO.

        Este namespace contem todos os modelos CLI especificos do flext-cli.
        Acesso via: FlextCliModels.Cli.Entity, FlextCliModels.Cli.Value, FlextCliModels.Cli.CliCommand, etc.

        PADRAO: Namespace hierarquico completo, sem duplicacao.
        """

        JSON_NORMALIZE_ADAPTER: ClassVar[TypeAdapter[t.Cli.JsonValue]] = TypeAdapter(
            t.Cli.JsonValue,
        )
        DICT_STR_OBJECT_ADAPTER: ClassVar[
            TypeAdapter[Mapping[str, t.Cli.JsonValue]]
        ] = TypeAdapter(
            Mapping[str, t.Cli.JsonValue],
        )
        LIST_OBJECT_ADAPTER: ClassVar[TypeAdapter[Sequence[t.Cli.JsonValue]]] = (
            TypeAdapter(
                Sequence[t.Cli.JsonValue],
            )
        )

        @staticmethod
        def _default_json_list() -> Sequence[t.Cli.JsonValue]:
            return []

        @staticmethod
        def _default_step_results() -> Sequence[Mapping[str, t.Cli.JsonValue]]:
            return []

        @staticmethod
        def is_mapping_like(
            obj: t.Cli.JsonValue | Mapping[str, t.Cli.JsonValue],
        ) -> TypeIs[Mapping[str, t.Cli.JsonValue]]:
            """Narrow value to Mapping for metadata processing."""
            return isinstance(obj, Mapping)

        @staticmethod
        def is_sequence_like(
            obj: t.Cli.JsonValue | Sequence[t.Cli.JsonValue],
        ) -> TypeIs[Sequence[t.Cli.JsonValue]]:
            """Narrow value to non-string Sequence for JSON normalization."""
            return isinstance(obj, Sequence) and not isinstance(obj, (str, bytes))

        @staticmethod
        def unwrap_root_value(
            value: t.Cli.JsonValue,
        ) -> t.Cli.JsonValue:
            """Unwrap RootModel .root value if present, otherwise return as-is."""
            if hasattr(value, "__dict__"):
                model_dict = value.__dict__
                if "root" in model_dict:
                    root_value = model_dict["root"]
                    if root_value is not None:
                        return root_value
            return value

        class DisplayData(BaseModel):
            """Key-value data for table/display — Pydantic v2 contract. Use m.Cli.DisplayData."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            data: Annotated[
                t.Cli.JsonValue,
                Field(
                    description="Field-value pairs for display",
                ),
            ] = Field(default_factory=dict)

        class LoadedConfig(BaseModel):
            """Loaded configuration content — Pydantic v2 contract. Use m.Cli.LoadedConfig."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )
            content: Annotated[
                t.Cli.JsonValue,
                Field(
                    description="Configuration key-value content",
                ),
            ] = Field(default_factory=dict)

        class SuccessSummaryDetails(RootModel[t.StrMapping]):
            """Key-value details for success summary — Pydantic v2 only. Use m.Cli.SuccessSummaryDetails."""

        type CommandEntry = Mapping[
            str,
            str | Callable[..., r[t.Cli.JsonValue]],
        ]

        class CommandEntryModel(BaseModel):
            """Single command entry: name + handler. Use m.Cli.CommandEntryModel."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                arbitrary_types_allowed=True,
                extra="forbid",
            )
            name: Annotated[t.NonEmptyStr, Field(..., description="Command name")]
            handler: Annotated[
                Callable[..., r[t.Cli.JsonValue]],
                Field(..., description="Command handler callable"),
            ]

        class CliCommandGroup(BaseModel):
            """Command group with name, description, and command entries. Use m.Cli.CliCommandGroup."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                arbitrary_types_allowed=True,
                extra="forbid",
            )
            name: Annotated[t.NonEmptyStr, Field(..., description="Group name")]
            description: Annotated[
                str,
                Field(default="", description="Group description"),
            ]
            commands: Annotated[
                Mapping[str, FlextCliModels.Cli.CommandEntryModel],
                Field(
                    description="Command name to entry mapping",
                ),
            ] = Field(default_factory=dict)

        class CliNormalizedJson(RootModel[t.Cli.JsonValue]):
            """Single contract: any value normalized to JSON-compatible value."""

            @model_validator(mode="wrap")
            @classmethod
            def _normalize(
                cls,
                data: t.Cli.JsonValue,
                handler: Callable[..., FlextCliModels.Cli.CliNormalizedJson],
            ) -> FlextCliModels.Cli.CliNormalizedJson:
                normalized = FlextCliModels.Cli.JSON_NORMALIZE_ADAPTER.dump_python(
                    data,
                    mode="json",
                    warnings=False,
                )
                return handler(normalized)

        class _JsonNormalizeInput(BaseModel):
            """Single contract for norm_json: value -> normalized JSON value."""

            model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
            value: Annotated[t.Cli.JsonValue, Field(description="Value to normalize")]

            @computed_field
            @property
            def normalized(self) -> t.Cli.JsonValue:
                return FlextCliModels.Cli.CliNormalizedJson(self.value).root

        class _EnsureTypeRequest(BaseModel):
            """Single contract for ensure_str/ensure_bool. Delegates to TypedExtract."""

            model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
            kind: Annotated[Literal["str", "bool"], Field(description="Requested type")]
            value: Annotated[t.Cli.JsonValue | None, Field(default=None)]
            default: Annotated[str | bool, Field(description="Default value")]

            def result(self) -> str | bool:
                out = FlextCliModels.Cli.TypedExtract(
                    type_kind=self.kind,
                    value=self.value,
                    default=self.default,
                ).resolve()
                if self.kind == "bool":
                    return bool(out) if out is not None else bool(self.default)
                return str(out) if out is not None else str(self.default)

        class _MapGetValue(BaseModel):
            """Single contract for get_map_val: map + key + default -> value (normalized)."""

            model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
            map_: Annotated[
                Mapping[str, t.Cli.JsonValue],
                Field(alias="map", description="Source mapping"),
            ]
            key: Annotated[str, Field(description="Key to look up")]
            default: Annotated[
                t.Cli.JsonValue,
                Field(description="Default if key missing"),
            ]

            def result(self) -> t.Cli.JsonValue:
                val = self.map_.get(self.key, self.default)
                if isinstance(val, (*t.PRIMITIVES_TYPES, list)):
                    return val
                if FlextCliModels.Cli.is_mapping_like(val):
                    return {
                        str(k): FlextCliModels.Cli.JSON_NORMALIZE_ADAPTER.dump_python(
                            vv,
                            mode="json",
                            warnings=False,
                        )
                        for k, vv in val.items()
                    }
                return FlextCliModels.Cli.JSON_NORMALIZE_ADAPTER.dump_python(
                    val,
                    mode="json",
                    warnings=False,
                )

        class _DictKeysExtract(BaseModel):
            """Single contract for get_keys: input -> list of keys (empty if not dict)."""

            model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
            input_: Annotated[
                t.Cli.JsonValue | Mapping[str, t.Cli.JsonValue],
                Field(
                    alias="input",
                    description="Value to extract keys from",
                ),
            ]

            @computed_field
            @property
            def resolved(self) -> t.StrSequence:
                if isinstance(self.input_, Mapping):
                    return list(self.input_.keys())
                root = FlextCliModels.Cli.unwrap_root_value(self.input_)
                if isinstance(root, Mapping):
                    return list(root.keys())
                return []

        class _EnsureDictInput(BaseModel):
            """Single contract for ensure_dict: value + default -> Mapping[str, t.Cli.JsonValue]."""

            model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
            value: Annotated[t.Cli.JsonValue | None, Field(default=None)]
            default: Annotated[
                Mapping[str, t.Cli.JsonValue],
                Field(default_factory=dict),
            ]

            @computed_field
            @property
            def resolved(self) -> Mapping[str, t.Cli.JsonValue]:
                if self.value is None:
                    return self.default
                source = FlextCliModels.Cli.unwrap_root_value(self.value)
                if FlextCliModels.Cli.is_mapping_like(source):
                    return {
                        str(k): FlextCliModels.Cli.JSON_NORMALIZE_ADAPTER.dump_python(
                            vv,
                            mode="json",
                            warnings=False,
                        )
                        for k, vv in source.items()
                    }
                try:
                    parsed = FlextCliModels.Cli.DICT_STR_OBJECT_ADAPTER.validate_python(
                        source,
                    )
                    return {
                        str(k): FlextCliModels.Cli.JSON_NORMALIZE_ADAPTER.dump_python(
                            vv,
                            mode="json",
                            warnings=False,
                        )
                        for k, vv in parsed.items()
                    }
                except ValidationError:
                    return self.default

        class _EnsureListInput(BaseModel):
            """Single contract for ensure_list: value + default -> Sequence[t.Cli.JsonValue]."""

            model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
            value: Annotated[t.Cli.JsonValue | None, Field(default=None)]
            default: Sequence[t.Cli.JsonValue] = Field(default_factory=list)

            @computed_field
            @property
            def resolved(self) -> Sequence[t.Cli.JsonValue]:
                if self.value is None:
                    return list(self.default)
                source = FlextCliModels.Cli.unwrap_root_value(self.value)
                try:
                    seq = FlextCliModels.Cli.LIST_OBJECT_ADAPTER.validate_python(
                        source,
                    )
                    return [
                        FlextCliModels.Cli.JSON_NORMALIZE_ADAPTER.dump_python(
                            x,
                            mode="json",
                            warnings=False,
                        )
                        for x in seq
                    ]
                except ValidationError:
                    return list(self.default)

        class _PromptTimeoutResolved(BaseModel):
            """Single contract: raw (int | str | None) + default → int. Replaces isinstance(timeout_raw, int/str) branching."""

            model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
            raw: Annotated[int | str | None, Field(default=None)]
            default: Annotated[
                int,
                Field(default=30, description="Default timeout in seconds"),
            ]

            @computed_field
            @property
            def resolved(self) -> int:
                return self.resolve()

            def resolve(self) -> int:
                """Type-safe accessor (bypasses pyrefly computed_field limitation)."""
                if self.raw is None:
                    return self.default
                if isinstance(self.raw, int):
                    return self.raw
                if self.raw.isdigit():
                    return int(self.raw)
                return self.default

        class _ExecutionContextInput(
            RootModel[t.StrSequence | Mapping[str, t.Cli.JsonValue] | None],
        ):
            """Execution context: None, list of args, or mapping. Single Pydantic contract. Use model_validate(context) then .to_mapping() or .root."""

            def to_mapping(
                self,
                list_processor: Callable[[t.StrSequence], Sequence[t.Cli.JsonValue]]
                | None = None,
            ) -> Mapping[str, t.Cli.JsonValue]:
                raw = self.root
                if raw is None:
                    return {}
                if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
                    lst = list(raw)
                    processed = list_processor(lst) if list_processor else lst
                    return {
                        c.Cli.DictKeys.ARGS: [
                            FlextCliModels.Cli.normalize_json_value(item)
                            for item in processed
                        ],
                    }
                if isinstance(raw, Mapping):
                    return dict(raw)
                return {}

        @staticmethod
        def normalize_json_value(
            item: t.Cli.JsonValue,
        ) -> t.Cli.JsonValue:
            """Normalize a value to a JSON-serializable value."""
            if isinstance(item, t.PRIMITIVES_TYPES):
                return item
            if item is None:
                return ""
            source = FlextCliModels.Cli.unwrap_root_value(item)
            if FlextCliModels.Cli.is_mapping_like(source):
                return {
                    str(k): FlextCliModels.Cli.normalize_json_value(v)
                    for k, v in source.items()
                }
            if isinstance(source, Sequence) and not isinstance(source, (str, bytes)):
                return [FlextCliModels.Cli.normalize_json_value(i) for i in source]
            return str(item)

        class _NormalizedJsonList(BaseModel):
            """Single contract: ensure value is list with default. Replaces ensure_list branching."""

            model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
            value: Annotated[
                t.Cli.JsonValue | None,
                Field(default=None, description="Value to coerce"),
            ]
            default: Annotated[
                Sequence[t.Cli.JsonValue],
                Field(
                    description="Default when value is None or invalid",
                ),
            ] = Field(default_factory=list)

            @computed_field
            @property
            def resolved(self) -> Sequence[t.Cli.JsonValue]:
                return self.resolve()

            def resolve(self) -> Sequence[t.Cli.JsonValue]:
                """Type-safe accessor (bypasses pyrefly computed_field limitation)."""
                if self.value is None:
                    return list(self.default)
                source = FlextCliModels.Cli.unwrap_root_value(self.value)
                try:
                    raw_list = FlextCliModels.Cli.LIST_OBJECT_ADAPTER.validate_python(
                        source,
                    )
                    return [
                        FlextCliModels.Cli.normalize_json_value(i) for i in raw_list
                    ]
                except ValidationError:
                    return list(self.default)

        class NormalizedJsonDict(BaseModel):
            """Single contract: ensure value is Mapping[str, t.Cli.JsonValue] with default. Replaces ensure_dict branching."""

            model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
            value: Annotated[
                t.Cli.JsonValue | None,
                Field(default=None, description="Value to coerce"),
            ]
            default: Annotated[
                Mapping[str, t.Cli.JsonValue],
                Field(
                    description="Default when value is None or invalid",
                ),
            ] = Field(default_factory=dict)

            @computed_field
            @property
            def resolved(self) -> Mapping[str, t.Cli.JsonValue]:
                """Normalized Mapping[str, t.Cli.JsonValue]; uses resolve() for pyrefly."""
                return self.resolve()

            def resolve(self) -> Mapping[str, t.Cli.JsonValue]:
                """Type-safe accessor (bypasses pyrefly computed_field limitation)."""
                if self.value is None:
                    return dict(self.default)
                source = FlextCliModels.Cli.unwrap_root_value(self.value)
                try:
                    raw_dict = (
                        FlextCliModels.Cli.DICT_STR_OBJECT_ADAPTER.validate_python(
                            source,
                        )
                    )
                    return {
                        str(k): FlextCliModels.Cli.normalize_json_value(v)
                        for k, v in raw_dict.items()
                    }
                except ValidationError:
                    return dict(self.default)

        class TypedExtract(BaseModel):
            """Single contract for typed value extraction (str | bool | dict). Replaces polymorphic _extract_typed_value."""

            model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
            type_kind: Annotated[
                Literal["str", "bool", "dict"],
                Field(description="Requested type"),
            ]
            value: Annotated[t.Cli.JsonValue | None, Field(default=None)]
            default: Annotated[t.Cli.JsonValue | None, Field(default=None)]

            @computed_field
            @property
            def resolved(
                self,
            ) -> str | bool | Mapping[str, t.Cli.JsonValue] | None:
                """Value coerced to type_kind, or default. Single Pydantic contract (no polymorphic methods)."""
                return self.resolve()

            def resolve(
                self,
            ) -> str | bool | Mapping[str, t.Cli.JsonValue] | None:
                """Type-safe accessor (bypasses pyrefly computed_field limitation)."""
                if self.value is None:
                    return FlextCliModels.Cli.default_for_type_kind(
                        self.type_kind,
                        self.default,
                    )
                if self.type_kind == "str":
                    s = str(self.value).strip() if self.value else ""
                    return s or (
                        self.default if isinstance(self.default, str) else None
                    )
                if self.type_kind == "bool":
                    return bool(self.value)
                if self.type_kind == "dict":
                    if FlextCliModels.Cli.is_mapping_like(self.value):
                        return {
                            str(
                                k,
                            ): FlextCliModels.Cli.JSON_NORMALIZE_ADAPTER.dump_python(
                                vv,
                                mode="json",
                                warnings=False,
                            )
                            for k, vv in self.value.items()
                        }
                    if FlextCliModels.Cli.is_mapping_like(self.default):
                        return {
                            str(
                                k,
                            ): FlextCliModels.Cli.JSON_NORMALIZE_ADAPTER.dump_python(
                                vv,
                                mode="json",
                                warnings=False,
                            )
                            for k, vv in self.default.items()
                        }
                    return {}
                return FlextCliModels.Cli.default_for_type_kind(
                    self.type_kind,
                    self.default,
                )

        @staticmethod
        def default_for_type_kind(
            type_kind: Literal["str", "bool", "dict"],
            default: t.Cli.JsonValue | None,
        ) -> str | bool | Mapping[str, t.Cli.JsonValue] | None:
            """Default value for type_kind. Centralized (no polymorphic branches at call sites)."""
            if type_kind == "str":
                return default if isinstance(default, str) else None
            if type_kind == "bool":
                return default if isinstance(default, bool) else False
            if FlextCliModels.Cli.is_mapping_like(default):
                return {
                    str(k): FlextCliModels.Cli.JSON_NORMALIZE_ADAPTER.dump_python(
                        v,
                        mode="json",
                        warnings=False,
                    )
                    for k, v in default.items()
                }
            return {}

        class _LogLevelResolved(BaseModel):
            """Single contract for log level string (replaces u.convert for log level)."""

            model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
            raw: Annotated[str | None, Field(default=None)]
            default: Annotated[str, Field(default="INFO")]

            @computed_field
            @property
            def resolved(self) -> str:
                return self.resolve()

            def resolve(self) -> str:
                """Type-safe accessor (bypasses pyrefly computed_field limitation)."""
                s = (self.raw or self.default).strip().upper()
                return s or self.default

        class CliLoggingData(BaseModel):
            """CLI logging data model - defined at module level to avoid Pydantic field inheritance issues.

            CRITICAL: Defined OUTSIDE nested classes to prevent Pydantic from merging fields.
            Pydantic nested classes can share field definitions if defined in sequence,
            so this is at module level and then aliased into Cli namespace.
            """

            model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

            level: Annotated[
                str,
                Field(
                    default="INFO",
                    description="Logging level",
                ),
            ]
            format: Annotated[
                str,
                Field(
                    default="%(asctime)s - %(message)s",
                    description="Logging format",
                ),
            ]

        ExecutionContextInput = _ExecutionContextInput
        LogLevelResolved = _LogLevelResolved
        PromptTimeoutResolved = _PromptTimeoutResolved
        JsonNormalizeInput = _JsonNormalizeInput
        NormalizedJsonList = _NormalizedJsonList
        EnsureTypeRequest = _EnsureTypeRequest
        MapGetValue = _MapGetValue

        class CliExecutionMetadata(FlextModels.Value):
            """CLI execution metadata model."""

            command_name: str | None = None
            session_id: str | None = None
            start_time: float | None = None
            pid: int | None = None
            environment: str | None = None

        class CliValidationResult(FlextModels.Value):
            """CLI validation result model."""

            field_name: str | None = None
            rule_name: str | None = None
            is_valid: bool | None = None
            error_message: str | None = None

        # CRÍTICO: NÃO redeclarar classes base de flext-core (Entity, Value, AggregateRoot, etc.)
        # Elas vêm automaticamente via herança: FlextCliModels(FlextModels)
        # APENAS declarar modelos CLI-ESPECÍFICOS que estendem as bases

        @staticmethod
        def execute() -> r[Mapping[str, t.Cli.JsonValue]]:
            """Execute a no-op command returning an empty result."""
            return r[Mapping[str, t.Cli.JsonValue]].ok({})

        class TableConfig(FlextModels.Value):
            """Table display configuration for tabulate extending Value via inheritance.

            Fields map directly to tabulate() parameters.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            # Headers configuration
            headers: Annotated[
                str | t.StrSequence,
                Field(
                    description=(
                        "Table headers (string like 'keys', 'firstrow' "
                        "or sequence of header names)"
                    ),
                ),
            ] = "keys"
            show_header: Annotated[
                bool,
                Field(description="Whether to show table header"),
            ] = True

            # Format configuration
            table_format: Annotated[
                str,
                Field(
                    description="Table format (simple, grid, fancy_grid, pipe, orgtbl, etc.)",
                ),
            ] = "simple"

            # Number formatting
            floatfmt: Annotated[
                str,
                Field(description="Float format string"),
            ] = ".4g"
            numalign: Annotated[
                str,
                Field(description="Number alignment (right, center, left, decimal)"),
            ] = "decimal"

            # String formatting
            stralign: Annotated[
                str,
                Field(description="String alignment (left, center, right)"),
            ] = "left"

            align: Annotated[
                str,
                Field(description="General alignment (left, center, right, decimal)"),
            ] = "left"

            # Missing values
            missingval: Annotated[
                str,
                Field(description="String to use for missing values"),
            ] = ""

            # Index display
            showindex: Annotated[
                bool | str | Sequence[str | int],
                Field(description="Whether to show row indices"),
            ] = False

            # Column alignment
            colalign: Annotated[
                t.StrSequence | None,
                Field(
                    description="Per-column alignment (left, center, right, decimal)",
                ),
            ] = None

            # Number parsing
            disable_numparse: Annotated[
                bool | Sequence[int],
                Field(
                    description="Disable number parsing (bool or list of column indices)",
                ),
            ] = False

            def get_effective_colalign(self) -> t.StrSequence | None:
                """Get effective column alignment, resolving None to default."""
                return self.colalign

        class LoggingConfig(FlextModels.Value):
            """Logging configuration model extending Value via inheritance.

            Manages logging behavior for CLI applications with level, format, and output settings.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            log_level: Annotated[
                str,
                Field(
                    default="INFO",
                    description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
                ),
            ]
            log_format: Annotated[
                str,
                Field(
                    default="%(asctime)s - %(levelname)s - %(message)s",
                    description="Log message format string",
                ),
            ]
            console_output: Annotated[
                bool,
                Field(
                    default=True,
                    description="Whether to output logs to console",
                ),
            ]
            log_file: Annotated[
                str,
                Field(
                    default="",
                    description="Log file path (empty string means no file logging)",
                ),
            ]

            @computed_field
            def logging_summary(self) -> FlextCliModels.Cli.CliLoggingData:
                """Return logging summary as structured data."""
                # Use model_construct with module-level CliLoggingData
                return FlextCliModels.Cli.CliLoggingData.model_construct(
                    level=self.log_level,
                    format=self.log_format,
                )

        class CliCommand(FlextModels.Entity):
            """CLI command model extending Entity via inheritance."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                frozen=True,
                extra="forbid",
                use_enum_values=True,
                validate_default=True,
                str_strip_whitespace=True,
                # Override TimestampableMixin fields to use strings instead of datetime
                # This avoids frozen instance errors during initialization
            )

            @override
            def model_post_init(
                self,
                __context: t.ConfigurationMapping | None = None,
                /,
            ) -> None:
                """Finalize initialization without post-processing side effects."""
                return

            def _copy_with_update(self, **updates: t.Scalar) -> Self:
                """Helper method for model_copy with updates - reduces repetition.

                Composition pattern: centralizes model_copy logic for reuse.
                Uses broad value contracts to accept protocol implementations.
                """
                return self.model_copy(update=updates)

            name: Annotated[
                t.NonEmptyStr,
                Field(
                    ...,
                    description="Command name",
                ),
            ]

            command_line: Annotated[
                str,
                Field(description="Full command line"),
            ] = ""

            description: Annotated[
                str,
                Field(description="Command description"),
            ] = ""

            usage: Annotated[
                str,
                Field(description="Command usage information"),
            ] = ""

            entry_point: Annotated[
                str,
                Field(description="Command entry point"),
            ] = ""

            plugin_version: Annotated[
                str,
                Field(description="Plugin version"),
            ] = "default"

            args: Annotated[
                t.StrSequence,
                Field(description="Command arguments"),
            ] = ()

            status: Annotated[
                str,
                Field(description="Command execution status"),
            ] = "pending"

            exit_code: Annotated[
                int | None,
                Field(description="Command exit code"),
            ] = None

            output: Annotated[
                str,
                Field(description="Command output"),
            ] = ""

            error_output: Annotated[
                str,
                Field(description="Command error output"),
            ] = ""

            execution_time: Annotated[
                float | None,
                Field(description="Command execution time"),
            ] = None

            result: Annotated[
                t.Cli.JsonValue | None,
                Field(description="Command result"),
            ] = None

            kwargs: Annotated[
                Mapping[str, t.Cli.JsonValue],
                Field(description="Command keyword arguments"),
            ] = Field(default_factory=dict)

            @property
            def command_summary(self) -> t.StrMapping:
                """Return command summary as dict."""
                return {"command": self.command_line or self.name}

            @property
            def is_completed(self) -> bool:
                """Check if command is completed."""
                return self.status == c.Cli.CommandStatus.COMPLETED.value

            @property
            def is_failed(self) -> bool:
                """Check if command failed."""
                return self.status == c.Cli.CommandStatus.FAILED.value

            @property
            def is_pending(self) -> bool:
                """Check if command is pending."""
                return self.status == c.Cli.CommandStatus.PENDING.value

            @property
            def is_running(self) -> bool:
                """Check if command is running."""
                return self.status == c.Cli.CommandStatus.RUNNING.value

            @classmethod
            def validate_command_input(
                cls,
                data: Mapping[str, t.Cli.JsonValue] | FlextCliModels.Cli.CliCommand,
            ) -> r[FlextCliModels.Cli.CliCommand]:
                """Validate command input data."""
                if not isinstance(data, Mapping) and not isinstance(data, cls):
                    return (
                        r[FlextCliModels.Cli.CliCommand]
                        .fail("Input must be a dictionary")
                        .map(lambda _unused: cls.model_construct(name="invalid"))
                    )
                try:
                    command = cls.model_validate(data)
                    return r[FlextCliModels.Cli.CliCommand].ok(command)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return (
                        r[FlextCliModels.Cli.CliCommand]
                        .fail(f"Validation failed: {e}")
                        .map(lambda _unused: cls.model_construct(name="invalid"))
                    )

            def complete_execution(self, exit_code: int) -> r[Self]:
                """Complete command execution with exit code."""
                try:
                    updated = self.model_copy(
                        update={"status": "completed", "exit_code": exit_code},
                    )
                    return r[Self].ok(updated)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return (
                        r[Self]
                        .fail(f"Failed to complete execution: {e}")
                        .map(lambda _unused: self)
                    )

            def execute(
                self,
                _args: t.StrSequence,
            ) -> r[Mapping[str, t.Cli.JsonValue]]:
                """Execute command with arguments - required by Command.

                Args:
                    _args: Command arguments (unused in default implementation)

                Returns:
                    r: Command execution result

                """
                # Default implementation - returns empty result
                # Real implementations should override this method
                return r.ok({})

            def start_execution(self) -> r[Self]:
                """Start command execution - update status to running."""
                try:
                    updated = self.model_copy(update={"status": "running"})
                    return r[Self].ok(updated)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return (
                        r[Self]
                        .fail(f"Failed to start execution: {e}")
                        .map(lambda _unused: self)
                    )

            def update_status(self, status: str) -> Self:
                """Update command status."""
                return self.model_copy(update={"status": status})

            def with_args(self, args: t.StrSequence) -> Self:
                """Return copy with new arguments."""
                return self.model_copy(update={"args": list(args)})

            def with_status(self, status: str) -> Self:
                """Return copy with new status.

                Accepts both str and CommandStatus" for protocol compatibility.
                """
                return self._copy_with_update(status=str(status))

        class CliSession(FlextModels.Entity):
            """CLI session model for tracking command execution sessions extending Entity via inheritance."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                frozen=True,
                extra="forbid",
                use_enum_values=True,
                validate_default=True,
            )

            @override
            def model_post_init(
                self,
                __context: t.ConfigurationMapping | None = None,
                /,
            ) -> None:
                """Finalize initialization without post-processing side effects."""
                return

            session_id: Annotated[
                t.NonEmptyStr,
                Field(..., description="Session identifier"),
            ]
            user_id: Annotated[str, Field(default="", description="User identifier")]
            status: Annotated[
                str,
                Field(
                    ...,
                    description="Session status",
                ),
            ]

            @field_validator("status")
            @classmethod
            def validate_status(cls, value: t.Cli.JsonValue) -> str:
                """Validate session status."""
                if not isinstance(value, str):
                    msg = "session_status must be a string"
                    raise TypeError(msg)
                # Validate value is in allowed statuses
                valid_statuses = c.Cli.ValidationLists.SESSION_STATUSES
                if value not in valid_statuses:
                    msg = (
                        f"session_status must be one of {valid_statuses}, got '{value}'"
                    )
                    raise ValueError(msg)
                return value

            # Use concrete type to avoid protocol typing issues
            commands: Annotated[
                tuple[FlextCliModels.Cli.CliCommand, ...],
                Field(
                    description="Commands in session",
                ),
            ] = Field(default_factory=tuple)
            start_time: Annotated[
                str | None,
                Field(
                    default=None,
                    description="Session start time",
                ),
            ]
            end_time: Annotated[
                str | None,
                Field(default=None, description="Session end time"),
            ]
            last_activity: Annotated[
                str | None,
                Field(
                    default=None,
                    description="Last activity timestamp",
                ),
            ]
            internal_duration_seconds: Annotated[
                float,
                Field(
                    default=0.0,
                    description="Internal duration in seconds",
                ),
            ]
            commands_executed: Annotated[
                int,
                Field(
                    default=0,
                    description="Number of commands executed",
                ),
            ]

            @property
            def session_summary(self) -> FlextCliModels.Cli.CliSessionData:
                """Return session summary as CliSessionData model."""
                # Return concrete model instance (not protocol)
                return FlextCliModels.Cli.CliSessionData(
                    session_id=self.session_id,
                    status=self.status,
                    commands_count=len(self.commands),
                )

            def add_command(self, command: FlextCliModels.Cli.CliCommand) -> r[Self]:
                """Add command to session."""
                try:
                    updated_commands = list(self.commands) + [command]
                    updated_session = self.model_copy(
                        update={"commands": tuple(updated_commands)},
                    )
                    return r[Self].ok(updated_session)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return (
                        r[Self]
                        .fail(f"Failed to add command: {e}")
                        .map(lambda _unused: self)
                    )

            def commands_by_status(
                self,
                status: str | None = None,
            ) -> (
                Sequence[FlextCliModels.Cli.CliCommand]
                | Mapping[str, Sequence[FlextCliModels.Cli.CliCommand]]
            ):
                """Get commands filtered by status or grouped by all statuses.

                Args:
                    status: Optional status to filter by. If None, returns all grouped.

                Returns:
                    If status provided: List of commands matching that status
                    If status is None: Mapping of status -> commands

                """
                cli_commands: Sequence[FlextCliModels.Cli.CliCommand] = list(
                    self.commands,
                )
                result: MutableMapping[
                    str, MutableSequence[FlextCliModels.Cli.CliCommand]
                ] = {}
                for command in cli_commands:
                    cmd_status = command.status or ""
                    result.setdefault(cmd_status, []).append(command)

                if status is not None:
                    return result.get(status, [])
                return result

            def _copy_with_update(self, **updates: t.Scalar) -> Self:
                """Helper method for model_copy with updates - reduces repetition.

                Composition pattern: centralizes model_copy logic for reuse.
                Uses broad value contracts to accept protocol implementations.
                """
                return self.model_copy(update=updates)

        class CliSessionData(FlextModels.Value):
            """CLI session summary data extending FlextModels.Value via inheritance.

            Inherits frozen=True and extra="forbid" from FlextModels.Value
            (via FrozenStrictModel), no need to redefine.
            """

            session_id: Annotated[str, Field(..., description="Session identifier")]
            status: Annotated[str, Field(..., description="Session status")]
            commands_count: Annotated[
                int,
                Field(default=0, description="Number of commands"),
            ]

        class CliContext(FlextModels.Value):
            """CLI execution context model extending Value via inheritance."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                frozen=True,
                extra="forbid",
                use_enum_values=True,
            )

            cwd: Annotated[
                str,
                Field(
                    ...,
                    description="Current working directory",
                ),
            ]

            env: Annotated[
                t.StrMapping,
                Field(
                    description="Environment variables",
                ),
            ] = Field(default_factory=dict)

            args: Annotated[
                t.StrSequence,
                Field(
                    description="Command line arguments",
                ),
            ] = Field(default_factory=list)

            output_format: Annotated[
                c.Cli.OutputFormats,
                Field(
                    default=c.Cli.OutputFormats.TABLE,
                    description="Output format preference",
                ),
            ]

        class CliOutput(FlextModels.Value):
            """CLI output configuration model extending Value via inheritance."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                frozen=True,
                extra="forbid",
            )

            format: Annotated[
                c.Cli.OutputFormats,
                Field(
                    default=c.Cli.OutputFormats.TABLE,
                    description="Output format",
                ),
            ]

            headers: Annotated[
                t.StrSequence,
                Field(
                    description="Table headers",
                ),
            ] = Field(default_factory=list)

            show_headers: Annotated[
                bool,
                Field(
                    default=True,
                    description="Whether to show headers",
                ),
            ]

            color: Annotated[
                bool,
                Field(
                    default=True,
                    description="Whether to use colors",
                ),
            ]

        class CommandResult(FlextModels.Value):
            """Result of command execution extending Value via inheritance.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            command: Annotated[
                str,
                Field(
                    ...,
                    description="Executed command",
                ),
            ]

            exit_code: Annotated[
                t.NonNegativeInt,
                Field(
                    default=0,
                    description="Exit code",
                ),
            ]

            stdout: Annotated[
                str,
                Field(
                    default="",
                    description="Standard output",
                ),
            ]

            stderr: Annotated[
                str,
                Field(
                    default="",
                    description="Standard error",
                ),
            ]

            duration: Annotated[
                t.NonNegativeFloat,
                Field(
                    default=0.0,
                    description="Execution duration in seconds",
                ),
            ]

            @computed_field
            def has_output(self) -> bool:
                """Check if command produced output.

                Computed field included in serialization.
                """
                return bool(self.stdout or self.stderr)

            @computed_field
            def success(self) -> bool:
                """Check if command succeeded.

                Computed field included in serialization.
                """
                return self.exit_code == 0

        class ServiceExecutionResult(FlextModels.Value):
            """Result of service execution for status reporting extending Value via inheritance."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                frozen=True,
                extra="forbid",
            )

            service_executed: Annotated[
                bool,
                Field(
                    default=False,
                    description="Whether service was executed",
                ),
            ]

            commands_count: Annotated[
                t.NonNegativeInt,
                Field(
                    default=0,
                    description="Number of registered commands",
                ),
            ]

            session_active: Annotated[
                bool,
                Field(
                    default=False,
                    description="Whether session is active",
                ),
            ]

            execution_timestamp: Annotated[
                str,
                Field(
                    default="",
                    description="ISO timestamp of execution",
                ),
            ]

            service_ready: Annotated[
                bool,
                Field(
                    default=False,
                    description="Whether service is ready",
                ),
            ]

        class CliStatus(FlextModels.Value):
            """CLI application status."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                frozen=True,
                extra="forbid",
            )

            app_name: Annotated[
                str,
                Field(
                    default="",
                    description="Application name",
                ),
            ]

            version: Annotated[
                str,
                Field(
                    default="",
                    description="Application version",
                ),
            ]

            is_initialized: Annotated[
                bool,
                Field(
                    default=False,
                    description="Whether CLI is initialized",
                ),
            ]

            commands_count: Annotated[
                t.NonNegativeInt,
                Field(
                    default=0,
                    description="Number of registered commands",
                ),
            ]

            plugins_count: Annotated[
                t.NonNegativeInt,
                Field(
                    default=0,
                    description="Number of loaded plugins",
                ),
            ]

        class ConfigSnapshot(FlextModels.Value):
            """Snapshot of current CLI configuration information."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                frozen=True,
                extra="forbid",
            )

            config_dir: Annotated[
                str,
                Field(
                    default="",
                    description="Configuration directory path",
                ),
            ]

            config_exists: Annotated[
                bool,
                Field(
                    default=False,
                    description="Whether config directory exists",
                ),
            ]

            config_readable: Annotated[
                bool,
                Field(
                    default=False,
                    description="Whether config directory is readable",
                ),
            ]

            config_writable: Annotated[
                bool,
                Field(
                    default=False,
                    description="Whether config directory is writable",
                ),
            ]

            timestamp: Annotated[
                str,
                Field(
                    default="",
                    description="Timestamp of snapshot",
                ),
            ]

        class ServiceStatus(FlextModels.Value):
            """Generic service status response."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                frozen=True,
                extra="forbid",
            )

            status: Annotated[
                str,
                Field(
                    default="",
                    description="Status message",
                ),
            ]

            service: Annotated[
                str,
                Field(
                    default="",
                    description="Service name",
                ),
            ]

            timestamp: Annotated[
                str,
                Field(
                    default="",
                    description="Status timestamp",
                ),
            ]

            version: Annotated[
                str,
                Field(
                    default="",
                    description="Service version",
                ),
            ]

        class CliConfig(FlextModels.Entity):
            """CLI configuration model extending Entity via inheritance."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                frozen=True,
                extra="forbid",
                use_enum_values=True,
                validate_default=True,
            )

            server_type: Annotated[
                c.Cli.ServerType,
                Field(
                    default=c.Cli.ServerType.RFC,
                    description="Server type",
                ),
            ]

            output_format: Annotated[
                c.Cli.OutputFormats,
                Field(
                    default=c.Cli.OutputFormats.TABLE,
                    description="Default output format",
                ),
            ]

            verbosity: Annotated[
                c.Cli.LogVerbosity,
                Field(
                    default=c.Cli.LogVerbosity.COMPACT,
                    description="Log verbosity level",
                ),
            ]

            timeout: Annotated[
                t.PositiveInt,
                Field(
                    default=30,
                    description="Default timeout in seconds",
                ),
            ]

            color: Annotated[
                bool,
                Field(
                    default=True,
                    description="Enable colored output",
                ),
            ]

            confirm_actions: Annotated[
                bool,
                Field(
                    default=True,
                    description="Require confirmation for destructive actions",
                ),
            ]

            # =========================================================================
            # ADDITIONAL MODELS - Required by flext-cli modules
            # =========================================================================

        class WorkflowResult(FlextModels.Value):
            """Workflow execution result with step-by-step tracking.

            Tracks overall workflow success and individual step results.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            step_results: Annotated[
                Sequence[Mapping[str, t.Cli.JsonValue]],
                Field(
                    description="Results for each workflow step",
                ),
            ] = Field(default_factory=list)
            total_steps: Annotated[
                int,
                Field(default=0, description="Total number of steps"),
            ]
            successful_steps: Annotated[
                int,
                Field(
                    default=0,
                    description="Number of successful steps",
                ),
            ]
            failed_steps: Annotated[
                int,
                Field(default=0, description="Number of failed steps"),
            ]
            overall_success: Annotated[
                bool,
                Field(
                    default=True,
                    description="Whether workflow succeeded overall",
                ),
            ]
            total_duration_seconds: Annotated[
                float,
                Field(
                    default=0.0,
                    description="Total workflow duration",
                ),
            ]

        class CliParamsConfig(FlextModels.Value):
            """CLI parameters configuration for command-line parsing.

            Maps directly to CLI flags: --verbose, --quiet, --debug, --trace, etc.
            All fields are optional (None) to allow partial updates.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            verbose: Annotated[
                bool | None,
                Field(
                    default=None,
                    description="Enable verbose output",
                ),
            ]
            quiet: Annotated[
                bool | None,
                Field(
                    default=None,
                    description="Suppress non-essential output",
                ),
            ]
            debug: Annotated[
                bool | None,
                Field(default=None, description="Enable debug mode"),
            ]
            trace: Annotated[
                bool | None,
                Field(
                    default=None,
                    description="Enable trace logging (requires debug)",
                ),
            ]
            log_level: Annotated[
                str | None,
                Field(
                    default=None,
                    description="Log level (DEBUG, INFO, WARNING, ERROR)",
                ),
            ]
            log_format: Annotated[
                str | None,
                Field(
                    default=None,
                    description="Log format (compact, detailed, full)",
                ),
            ]
            output_format: Annotated[
                str | None,
                Field(
                    default=None,
                    description="Output format (table, json, yaml, csv)",
                ),
            ]
            no_color: Annotated[
                bool | None,
                Field(
                    default=None,
                    description="Disable colored output",
                ),
            ]

            @property
            def params(self) -> Mapping[str, t.Cli.JsonValue]:
                """Parameters mapping - required by CliParamsConfig."""
                return {
                    "verbose": bool(self.verbose)
                    if self.verbose is not None
                    else False,
                    "quiet": bool(self.quiet) if self.quiet is not None else False,
                    "debug": bool(self.debug) if self.debug is not None else False,
                    "trace": bool(self.trace) if self.trace is not None else False,
                    "log_level": self.log_level or "",
                    "log_format": self.log_format or "",
                    "output_format": self.output_format or "",
                    "no_color": (
                        bool(self.no_color) if self.no_color is not None else False
                    ),
                }

        class OptionConfig(FlextModels.Value):
            """Configuration for CLI option decorators.

            Used with create_option_decorator to reduce argument counFlextCliTypes.
            """

            model_config: ClassVar[ConfigDict] = ConfigDict(
                frozen=True,
                extra="forbid",
                arbitrary_types_allowed=True,
            )

            default: Annotated[
                t.Cli.JsonValue | None,
                Field(
                    default=None,
                    description="Default value",
                ),
            ]
            type_hint: Annotated[
                t.Cli.JsonValue | None,
                Field(
                    default=None,
                    description="Parameter type (Click type or Python type)",
                ),
            ]
            required: Annotated[
                bool,
                Field(
                    default=False,
                    description="Whether option is required",
                ),
            ]
            help_text: Annotated[
                str | None,
                Field(
                    default=None,
                    description="Help text for option",
                ),
            ]
            is_flag: Annotated[
                bool,
                Field(
                    default=False,
                    description="Whether this is a boolean flag",
                ),
            ]
            flag_value: Annotated[
                t.Cli.JsonValue | None,
                Field(
                    default=None,
                    description="Value when flag is set",
                ),
            ]
            multiple: Annotated[
                bool,
                Field(default=False, description="Allow multiple values"),
            ]
            count: Annotated[
                bool,
                Field(default=False, description="Count occurrences"),
            ]
            show_default: Annotated[
                bool,
                Field(
                    default=False,
                    description="Show default in help",
                ),
            ]

        class ConfirmConfig(FlextModels.Value):
            """Configuration for confirm prompts.

            Used with confirm() method to reduce argument counFlextCliTypes.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            default: Annotated[bool, Field(default=False, description="Default value")]
            abort: Annotated[
                bool,
                Field(default=False, description="Abort if not confirmed"),
            ]
            prompt_suffix: Annotated[
                str,
                Field(
                    default=c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX,
                    description="Suffix after prompt",
                ),
            ]
            show_default: Annotated[
                bool,
                Field(
                    default=True,
                    description="Show default in prompt",
                ),
            ]
            err: Annotated[bool, Field(default=False, description="Write to stderr")]

        class PromptConfig(FlextModels.Value):
            """Configuration for input prompts.

            Used with prompt() method to reduce argument counFlextCliTypes.
            """

            model_config: ClassVar[ConfigDict] = ConfigDict(
                frozen=True,
                extra="forbid",
                arbitrary_types_allowed=True,
            )

            default: Annotated[
                t.Cli.JsonValue | None,
                Field(
                    default=None,
                    description="Default value",
                ),
            ]
            type_hint: Annotated[
                t.Cli.JsonValue | None,
                Field(
                    default=None,
                    description="Value type",
                ),
            ]
            value_proc: Annotated[
                Callable[[t.Cli.JsonValue], t.Cli.JsonValue] | None,
                Field(
                    default=None,
                    description="Value processor function",
                ),
            ]
            prompt_suffix: Annotated[
                str,
                Field(
                    default=c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX,
                    description="Suffix after prompt",
                ),
            ]
            hide_input: Annotated[
                bool,
                Field(default=False, description="Hide user input"),
            ]
            confirmation_prompt: Annotated[
                bool,
                Field(
                    default=False,
                    description="Ask for confirmation",
                ),
            ]
            show_default: Annotated[
                bool,
                Field(
                    default=True,
                    description="Show default in prompt",
                ),
            ]
            err: Annotated[bool, Field(default=False, description="Write to stderr")]
            show_choices: Annotated[
                bool,
                Field(
                    default=True,
                    description="Show available choices",
                ),
            ]

        class DebugInfo(FlextModels.Value):
            """Debug information model with sensitive data masking.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            service: Annotated[str, Field(..., description="Service name")]
            level: Annotated[str, Field(..., description="Debug level")]
            message: Annotated[str, Field(..., description="Debug message")]
            system_info: Annotated[
                Mapping[str, t.Cli.JsonValue],
                Field(
                    description="System information",
                ),
            ] = Field(default_factory=dict)
            config_info: Annotated[
                Mapping[str, t.Cli.JsonValue],
                Field(
                    description="Configuration information",
                ),
            ] = Field(default_factory=dict)

            @property
            def debug_summary(self) -> FlextCliModels.Cli.CliDebugData:
                """Return debug summary as CliDebugData model."""
                return FlextCliModels.Cli.CliDebugData(
                    service=self.service,
                    level=self.level,
                    message=self.message,
                )

            @field_validator("level", mode="before")
            @classmethod
            def normalize_level(cls, value: str) -> str:
                """Normalize level to uppercase."""
                return str(value).upper()

            def dump_masked(self) -> Mapping[str, t.Cli.JsonValue]:
                """Dump model with sensitive data masking.

                Business Rule:
                ──────────────
                Returns model_dump() with sensitive fields masked before serialization.
                This is a separate method to avoid Pydantic method override type issues.

                Audit Implication:
                ───────────────────
                Sensitive data (passwords, tokens, secrets) are masked in serialized outpuFlextCliTypes.
                This prevents accidental exposure of credentials in logs or API responses.

                Returns:
                    Dict with sensitive values masked as "***MASKED***".

                """
                sensitive_keys = c.Cli.SENSITIVE_KEYS
                data: MutableMapping[str, t.Cli.JsonValue] = {
                    "service": self.service,
                    "level": self.level,
                    "message": self.message,
                }

                system_dict: Mapping[str, t.Cli.JsonValue] = {}
                try:
                    system_dict = (
                        FlextCliModels.Cli.DICT_STR_OBJECT_ADAPTER.validate_python(
                            self.system_info,
                        )
                    )
                except ValidationError as e:
                    _logger.debug("system_info mask failed", error=e)

                # Apply masking to system_dict
                masked_system_dict: Mapping[str, t.Cli.JsonValue] = {
                    k: (
                        "***MASKED***"
                        if any(sensitive in k.lower() for sensitive in sensitive_keys)
                        else v
                    )
                    for k, v in system_dict.items()
                }
                data["system_info"] = masked_system_dict

                config_dict: Mapping[str, t.Cli.JsonValue] = {}
                try:
                    config_dict = (
                        FlextCliModels.Cli.DICT_STR_OBJECT_ADAPTER.validate_python(
                            self.config_info,
                        )
                    )
                except ValidationError as e:
                    _logger.debug("config_info not valid as dict, using empty", error=e)

                # Apply masking to config_dict
                masked_config_dict: Mapping[str, t.Cli.JsonValue] = {
                    k: (
                        "***MASKED***"
                        if any(sensitive in k.lower() for sensitive in sensitive_keys)
                        else v
                    )
                    for k, v in config_dict.items()
                }
                data["config_info"] = masked_config_dict

                return data

        class OptionBuilder:
            """Builder for Typer CLI options from field metadata.

            Constructs typer.Option instances from field_name and registry configuration.
            NOT a Pydantic model - this is a utility builder class.
            """

            def __init__(
                self,
                field_name: str,
                registry: Mapping[str, Mapping[str, t.Cli.JsonValue]],
            ) -> None:
                """Initialize builder with field name and registry.

                Args:
                    field_name: Name of field in "FlextCliSettings"
                    registry: CLI parameter registry mapping field names to option metadata

                """
                super().__init__()
                self.field_name = field_name
                self.registry = registry

            def build(self) -> typer.models.OptionInfo:
                """Build typer.Option from field metadata.

                Business Rule:
                ──────────────
                Typer automatically treats boolean options as flags when default is bool.
                The 'is_flag' parameter was deprecated in Typer and removed in
                recent versions.
                Boolean defaults (True/False) automatically enable flag behavior.

                Audit Implications:
                ───────────────────
                - Boolean options with False default become --flag (enables feature)
                - Boolean options with True default become --no-flag (disables feature)
                - Non-boolean options require explicit value: --option=value

                Returns:
                    typer.Option instance configured from registry metadata

                """
                # models.py cannot use utilities - use direct dict access instead
                # Extract field metadata from registry using direct dict access
                field_meta = self.registry.get(self.field_name, {})
                if not field_meta:
                    msg = "Option registry metadata must support key lookup"
                    raise TypeError(msg)
                # Extract option metadata from registry using direct dict access
                help_text = str(field_meta.get("help", ""))
                short_flag = str(field_meta.get("short", ""))
                default_value = field_meta.get("default", ...)

                # Use field_name_override if available, otherwise use field_name
                # Registry uses KEY_FIELD_NAME_OVERRIDE to map CLI param name to field name
                field_name_override = field_meta.get(
                    c.Cli.CliParamsRegistry.KEY_FIELD_NAME_OVERRIDE,
                )
                cli_param_name: str = (
                    field_name_override
                    if isinstance(field_name_override, str)
                    else self.field_name
                )

                # Build option arguments
                option_args: MutableSequence[str] = [
                    f"--{cli_param_name.replace('_', '-')}"
                ]
                if short_flag:
                    option_args.append(f"-{short_flag}")

                # typer.Option returns OptionInfo for type safety
                option: OptionInfo = OptionInfo(
                    default=default_value,
                    param_decls=option_args,
                    help=help_text,
                )
                return option

        class PasswordAuth(FlextModels.Value):
            """Password authentication data.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            username: Annotated[t.BoundedStr, Field(...)]
            password: Annotated[t.BoundedStr, Field(...)]
            realm: Annotated[str, Field(default="")]

        class CmdConfig(FlextModels.Value):
            """Command configuration.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            name: Annotated[str, Field(...)]
            description: Annotated[str, Field(default="")]
            hidden: Annotated[bool, Field(default=False)]
            deprecated: Annotated[bool, Field(default=False)]

        class TokenData(FlextModels.Value):
            """Authentication token data.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            token: Annotated[str, Field(...)]
            expires_at: Annotated[str, Field(default="")]
            token_type: Annotated[str, Field(default="Bearer")]

        class FormatInputData(FlextModels.Value):
            """Single contract for format input: BaseModel or JSON-like value."""

            data: Annotated[
                BaseModel | t.Cli.JsonValue,
                Field(
                    ...,
                    description="Data to format (model or raw JSON)",
                ),
            ]

            @computed_field
            @property
            def normalized(self) -> t.Cli.JsonValue:
                """JSON-compatible value for formatting."""
                if isinstance(self.data, BaseModel):
                    return self.data.model_dump()
                return self.data

        class ModelCommandBuilder:
            """Builder for Typer commands from Pydantic models.

            Business Rules:
            ───────────────
            1. Automatically extracts CLI parameters from Pydantic model fields
            2. Converts Pydantic field types to Typer-compatible types
            3. Boolean fields automatically become Typer flags (no is_flag needed)
            4. Literal types are converted to str for Typer compatibility
            5. Optional fields become optional CLI parameters with defaults
            6. Field descriptions become CLI help text automatically
            7. Command wrapper generation uses inspect.Signature for runtime binding
            8. Function annotations MUST be updated with real Python types for Typer introspection

            Architecture Implications:
            ───────────────────────────
            - Uses dynamic function creation to generate Typer command functions
            - Type conversion handles Pydantic types (Literal, Optional, Union) to Typer types
            - Boolean defaults determine flag behavior (False=--flag, True=--no-flag)
            - Function __annotations__ updated with real types for Typer flag detection
            - Model validation happens after CLI argument parsing (Pydantic handles validation)

            Audit Implications:
            ───────────────────
            - Dynamic code generation MUST validate model_class is BaseModel subclass
            - Wrapper creation MUST avoid dynamic code execution
            - Type conversion MUST preserve strict type safety - See type-system-architecture.md
            - Field validation MUST use Pydantic validators (not bypassed)
            - Sensitive fields (SecretStr) MUST be handled securely in CLI args
            - Command execution MUST log all parameters (except sensitive fields)
            - Model validation failures MUST return clear error messages

            Creates Typer command functions with automatic parameter extraction from model fields.
            NOT a Pydantic model - this is a utility builder class.
            """

            def __init__(
                self,
                model_class: type[BaseModel],
                handler: Callable[[BaseModel], t.Cli.JsonValue],
                config: t.Cli.JsonValue | None = None,
            ) -> None:
                """Initialize builder with model class, handler, and optional config.

                Args:
                    model_class: Pydantic BaseModel subclass defining parameters
                    handler: Function receiving validated model instance
                    config: Optional config singleton for defaults

                """
                super().__init__()
                self.model_class = model_class
                self.handler = handler
                self.config = config

            @staticmethod
            def _create_real_annotations(
                annotations: Mapping[str, type],
            ) -> Mapping[str, type]:
                """Create real type annotations for Typer flag detection."""

                # models.py cannot use utilities - use direct iteration instead
                def process_annotation(_name: str, field_type: type) -> type:
                    origin = get_origin(field_type)
                    is_union = (
                        origin is Union
                        or origin is type(Union)
                        or origin is types.UnionType
                    )
                    if is_union:
                        args = get_args(field_type)
                        # models.py cannot use utilities - use list comprehension instead
                        # models.py cannot use utilities - use list comprehension instead
                        non_none = [a for a in args if a is not type(None)]
                        if non_none and non_none[0] is bool:
                            # Type narrowing: bool | None is a UnionType, not a type
                            # Return bool as the base type (None is handled separately)
                            return bool
                        return field_type
                    return field_type

                # Process annotations using dict comprehension for type safety
                # models.py cannot use utilities - use direct iteration instead
                processed_annotations: Mapping[str, type] = {
                    name: process_annotation(name, field_type)
                    for name, field_type in annotations.items()
                }
                return processed_annotations

            @staticmethod
            def _extract_optional_inner_type(
                field_type: type,
            ) -> tuple[type, bool]:
                """Extract inner type from Optional/Union types.

                Returns (inner_type, is_optional) tuple.
                Handles Literal types inside Optional.
                """
                result_type: type = field_type
                is_optional = False

                origin = get_origin(field_type)
                if origin is None:
                    pass  # Keep defaults (field_type, False)
                elif origin is Literal:
                    result_type = str
                elif type(None) not in get_args(field_type):
                    # Union without None - check if first type is Literal
                    non_none_types = [
                        arg for arg in get_args(field_type) if arg is not type(None)
                    ]
                    if non_none_types:
                        first_type = non_none_types[0]
                        if get_origin(first_type) is Literal:
                            result_type = str
                        else:
                            result_type = first_type
                    else:
                        result_type = str
                else:
                    # Optional/Union with None
                    is_optional = True
                    non_none_types = [
                        arg for arg in get_args(field_type) if arg is not type(None)
                    ]
                    if not non_none_types or get_origin(non_none_types[0]) is Literal:
                        result_type = str
                    else:
                        result_type = non_none_types[0]

                return result_type, is_optional

            @staticmethod
            def _format_bool_param(
                type_name: str,
                inner_type: type,
                default_val: t.Cli.JsonValue | None,
            ) -> tuple[str, t.Cli.JsonValue | None]:
                """Format boolean parameter for Typer flag detection."""
                # Python 3.13: Direct type comparison - more elegant
                if inner_type is bool:
                    return "bool", False if default_val is None else default_val
                return type_name, default_val

            @staticmethod
            def _get_type_name_for_signature(
                field_type: type,
                builtin_types: set[str],
            ) -> tuple[str, type]:
                """Get type name string for Typer function signature.

                Returns (type_name_str, inner_type) for use in signature generation.
                Handles Literal, Union, Optional, and boolean types.
                """
                origin = get_origin(field_type)
                builder = FlextCliModels.Cli.ModelCommandBuilder

                # Handle direct Literal type
                if origin is Literal:
                    return "str", field_type

                # Handle Union/Optional types
                if origin is not None and (origin is Union or origin is type(Union)):
                    args = get_args(field_type)
                    if type(None) in args:
                        return builder.handle_optional_type(args, builtin_types)
                    return builder.handle_union_type(args, builtin_types)

                # Handle regular types (no origin)
                type_name = builder.get_builtin_name(field_type, builtin_types)
                return type_name, field_type

            @staticmethod
            def _resolve_type_alias(field_type: type) -> tuple[type, str | None]:
                """Resolve type aliases to Literal and return (resolved_type, origin).

                Handles PEP 695 type aliases like `type X = Literal[...]`.
                Returns the resolved type and its origin for further processing.
                """
                origin = get_origin(field_type)
                if origin is not None:
                    return field_type, str(origin)

                # Check if type has __value__ (type alias characteristic)
                # Use getattr for type access - field_type is a type, not a Mapping
                type_value_candidate = getattr(field_type, "__value__", None)
                type_value: str | None = (
                    str(type_value_candidate)
                    if type_value_candidate is not None
                    else None
                )
                if type_value is not None and "Literal" in type_value:
                    # Check if __value__ is a Literal type
                    return str, "Literal"
                    # Not Literal - continue to return field_type with origin
                # Return field_type with its origin (None if not a generic)
                # This handles both cases: type_value is None or not Literal
                resolved_origin = get_origin(field_type)
                return field_type, str(
                    resolved_origin,
                ) if resolved_origin is not None else None

            @staticmethod
            def get_builtin_name(_t: type, builtin_types: set[str]) -> str:
                """Get configured alias name or 'str' fallback."""
                if len(builtin_types) == 1:
                    custom_name = next(iter(builtin_types))
                    if custom_name not in {
                        "str",
                        "int",
                        "float",
                        "bool",
                        "list",
                        "dict",
                        "tuple",
                        "set",
                        "bytes",
                    }:
                        return custom_name
                return "str"

            @staticmethod
            def handle_optional_type(
                args: tuple[type, ...],
                builtin_types: set[str],
            ) -> tuple[str, type]:
                """Handle T | None pattern (Union with None)."""
                # Filter non-None types from args
                non_none_types: Sequence[type] = [
                    item for item in args if item is not type(None)
                ]
                inner_type = non_none_types[0] if non_none_types else str

                if get_origin(inner_type) is Literal:
                    return "str | None", inner_type

                inner_name = FlextCliModels.Cli.ModelCommandBuilder.get_builtin_name(
                    inner_type,
                    builtin_types,
                )
                return f"{inner_name} | None", inner_type

            @staticmethod
            def handle_union_type(
                args: tuple[type, ...],
                builtin_types: set[str],
            ) -> tuple[str, type]:
                """Handle Union without None."""
                # Filter non-None types from args
                non_none_types: Sequence[type] = [
                    item
                    for item in args
                    if item is not type(None)  # Exclude None type from Union
                ]
                if not non_none_types:
                    return "str", str

                first_type = non_none_types[0]
                if get_origin(first_type) is Literal:
                    return "str", first_type

                type_name = FlextCliModels.Cli.ModelCommandBuilder.get_builtin_name(
                    first_type,
                    builtin_types,
                )
                return type_name, first_type

            def _build_param_signature(
                self,
                name: str,
                type_info: tuple[str, type, t.Cli.JsonValue | None, bool, bool],
            ) -> tuple[str, bool]:
                """Build parameter signature string.

                Args:
                    name: Parameter name
                    type_info: Tuple of (type_name, inner_type, default_val, has_factory, has_default)

                Returns (param_str, is_no_default).

                """
                type_name, inner_type, default_val, has_factory, has_default = type_info
                type_name, default_val = self._format_bool_param(
                    type_name,
                    inner_type,
                    default_val,
                )

                if has_factory:
                    return f"{name}: {type_name} | None", True

                if has_default:
                    default_repr = repr(default_val)
                    if "PydanticUndefined" in default_repr:
                        return f"{name}: {type_name} | None", True
                    return f"{name}: {type_name} = {default_repr}", False

                return f"{name}: {type_name}", True

            def _process_field_metadata(
                self,
                field_name: str,
                field_info: FieldInfo | Mapping[str, t.Cli.JsonValue] | t.Cli.JsonValue,
            ) -> tuple[type, t.Cli.JsonValue | None, bool, bool]:
                """Process field metadata and return type info.

                Returns (field_type, default_value, is_required, has_factory).
                """
                default_value: t.Cli.JsonValue | None = None
                is_required = True
                has_factory = False

                default_attr = (
                    field_info.default if isinstance(field_info, FieldInfo) else None
                )
                if default_attr is not None:
                    default_value = default_attr
                factory_attr = (
                    field_info.default_factory
                    if isinstance(field_info, FieldInfo)
                    else None
                )
                has_factory = callable(factory_attr)
                is_required_fn = (
                    field_info.is_required
                    if isinstance(field_info, FieldInfo)
                    else None
                )
                if callable(is_required_fn):
                    is_required = bool(is_required_fn())

                # Get config default if available
                if self.config is not None:
                    config_value = (
                        getattr(self.config, field_name)
                        if hasattr(self.config, field_name)
                        else None
                    )
                    if config_value is not None:
                        default_value = config_value

                # Get and resolve field type
                # Use getattr for FieldInfo access in mixed input payloads
                field_type_raw = (
                    field_info.annotation if isinstance(field_info, FieldInfo) else None
                )
                if field_type_raw is None:
                    # No annotation - infer from default value or use str
                    field_type = (
                        type(default_value) if default_value is not None else str
                    )
                else:
                    # Has annotation - resolve type alias
                    field_type, origin = self._resolve_type_alias(field_type_raw)
                    if origin is not None and field_type is not str:
                        field_type, _ = self._extract_optional_inner_type(field_type)

                # Type narrowing: ensure field_type is a type
                field_type_typed: type = field_type
                return field_type_typed, default_value, is_required, has_factory

            _BUILTIN_TYPES: ClassVar[set[str]] = {
                "str",
                "int",
                "float",
                "bool",
                "list",
                "dict",
                "tuple",
                "set",
                "bytes",
            }

            def build(self) -> p.Cli.CliCommandWrapper:
                """Build Typer command from Pydantic model.

                Business Rule:
                ──────────────
                Dynamically creates a Typer command function from Pydantic model fields.
                The generated function:
                1. Accepts CLI arguments matching model field names and types
                2. Validates arguments using Pydantic model_validate()
                3. Calls handler with validated model instance
                4. Returns handler result (typically r)

                Architecture Implications:
                ───────────────────────────
                - Function signature built from model field annotations and defaults
                - Boolean fields automatically detected for Typer flag generation
                - Literal types converted to str for Typer compatibility
                - Function __annotations__ updated with real Python types for introspection
                - Model validation ensures type safety and business rule enforcement

                Audit Implications:
                ───────────────────
                - Model class MUST be validated as BaseModel subclass before use
                - Function creation MUST validate all field types are supported
                - Handler execution MUST catch and log all exceptions
                - Model validation failures MUST return clear error messages
                - Sensitive fields MUST NOT be logged in command execution logs

                Returns:
                    Typer command function with auto-generated parameters

                """
                narrowed_fields: Mapping[str, FieldInfo] = dict(
                    self.model_class.model_fields,
                )
                annotations, defaults, fields_with_factory = self._collect_field_data(
                    narrowed_fields,
                )
                return self._execute_command_wrapper(
                    annotations,
                    defaults,
                    fields_with_factory,
                )

            def _build_signature_parts(
                self,
                annotations: Mapping[str, type],
                defaults: Mapping[str, t.Cli.JsonValue],
                fields_with_factory: set[str],
            ) -> str:
                """Build function signature string from field data.

                Returns:
                    Comma-separated parameter signature string

                """

                # models.py cannot use utilities - use direct iteration instead
                def process_signature(name: str, field_type: type) -> tuple[str, bool]:
                    type_name, inner_type = self._get_type_name_for_signature(
                        field_type,
                        self._BUILTIN_TYPES,
                    )
                    type_info = (
                        type_name,
                        inner_type,
                        defaults.get(name),
                        name in fields_with_factory,
                        name in defaults,
                    )
                    param_str, is_no_default = self._build_param_signature(
                        name,
                        type_info,
                    )
                    return param_str, is_no_default

                # Process annotations using dict comprehension for type safety
                # models.py cannot use utilities - use direct iteration instead
                signatures_dict: Mapping[str, tuple[str, bool]] = {
                    name: process_signature(name, field_type)
                    for name, field_type in annotations.items()
                }
                # models.py cannot use utilities - use list comprehension instead
                # Use operator.itemgetter(1) to get boolean flag, then check truthiness
                get_bool_flag = operator.itemgetter(1)
                signatures_values = list(signatures_dict.values())
                # models.py cannot use utilities - use list comprehension instead
                # Type narrowing: signatures_values is Sequence[tuple[str, bool]]
                signatures_values_typed: Sequence[tuple[str, bool]] = signatures_values

                def has_no_default(item: tuple[str, bool]) -> bool:
                    """Check if item has no default (is_no_default is True)."""
                    return bool(get_bool_flag(item))

                def has_default(item: tuple[str, bool]) -> bool:
                    """Check if item has default (is_no_default is False)."""
                    return not bool(get_bool_flag(item))

                # models.py cannot use utilities - use list comprehension instead
                params_no_default_list = [
                    item for item in signatures_values_typed if has_no_default(item)
                ]
                params_with_default_list = [
                    item for item in signatures_values_typed if has_default(item)
                ]
                params_no_default = list(params_no_default_list)
                params_with_default = list(params_with_default_list)
                # models.py cannot use utilities - use list comprehension instead
                # Extract param strings using list comprehension with operator.itemgetter
                params_no_default_strs = [
                    operator.itemgetter(0)(item) for item in params_no_default
                ]
                params_with_default_strs = [
                    operator.itemgetter(0)(item) for item in params_with_default
                ]

                return ", ".join(params_no_default_strs + params_with_default_strs)

            def _collect_field_data(
                self,
                model_fields: Mapping[str, FieldInfo],
            ) -> tuple[
                Mapping[str, type],
                Mapping[str, t.Cli.JsonValue],
                set[str],
            ]:
                """Collect annotations, defaults and factory fields from model fields.

                Returns:
                    Tuple of (annotations, defaults, fields_with_factory)

                """

                # models.py cannot use utilities - use direct iteration instead
                def process_field(
                    field_name: str,
                    field_info: FieldInfo
                    | Mapping[str, t.Cli.JsonValue]
                    | t.Cli.JsonValue,
                ) -> tuple[type, t.Cli.JsonValue | None, bool]:
                    """Process single field and return (type, default, has_factory)."""
                    field_type, default_val, _is_required, has_factory = (
                        self._process_field_metadata(field_name, field_info)
                    )
                    # Return field_type (not Union type) - None handling is separate
                    return (
                        field_type,
                        default_val if default_val is not None else None,
                        has_factory,
                    )

                # Process model fields using dict comprehension for type safety
                # models.py cannot use utilities - use direct iteration instead
                processed_dict: Mapping[
                    str,
                    tuple[type, t.Cli.JsonValue | None, bool],
                ] = {
                    field_name: process_field(field_name, field_info)
                    for field_name, field_info in model_fields.items()
                }
                # Build annotations, defaults, and fields_with_factory from processed results
                annotations: MutableMapping[str, type] = {}
                defaults: MutableMapping[str, t.Cli.JsonValue] = {}
                fields_with_factory: set[str] = set()

                for field_name, (
                    field_type,
                    default_val,
                    has_factory,
                ) in processed_dict.items():
                    annotations[field_name] = field_type
                    if has_factory:
                        fields_with_factory.add(field_name)
                    # Store default if not factory field and (not required or has default)
                    if (
                        field_name not in fields_with_factory
                        and default_val is not None
                    ):
                        defaults[field_name] = default_val

                return annotations, defaults, fields_with_factory

            def _execute_command_wrapper(
                self,
                annotations: Mapping[str, type],
                defaults: Mapping[str, t.Cli.JsonValue],
                fields_with_factory: set[str],
            ) -> p.Cli.CliCommandWrapper:
                required_parameters: MutableSequence[inspect.Parameter] = []
                defaulted_parameters: MutableSequence[inspect.Parameter] = []
                for field_name, field_type in annotations.items():
                    has_default = (
                        field_name in defaults and field_name not in fields_with_factory
                    )
                    default_value = (
                        defaults[field_name] if has_default else inspect.Parameter.empty
                    )
                    parameter = inspect.Parameter(
                        name=field_name,
                        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=default_value,
                        annotation=field_type,
                    )
                    if has_default:
                        defaulted_parameters.append(parameter)
                    else:
                        required_parameters.append(parameter)
                signature_parameters = required_parameters + defaulted_parameters
                command_signature = inspect.Signature(parameters=signature_parameters)

                def command_wrapper(
                    *args: t.Cli.JsonValue,
                    **kwargs: t.Scalar,
                ) -> t.Cli.JsonValue:
                    try:
                        bound_arguments = command_signature.bind(*args, **kwargs)
                    except TypeError as ex:
                        msg = f"Invalid command arguments: {ex}"
                        raise RuntimeError(msg) from ex

                    model_instance = self.model_class.model_validate(
                        dict(bound_arguments.arguments),
                    )
                    if self.config is not None:
                        for fn, value in bound_arguments.arguments.items():
                            try:
                                setattr(self.config, fn, value)
                            except (AttributeError, TypeError) as ex:
                                _logger.debug(
                                    "Could not set builder_config.%s",
                                    fn,
                                    error=ex,
                                )
                    if callable(self.handler):
                        return self.handler(model_instance)
                    msg = "builder_handler is not callable"
                    raise RuntimeError(msg)

                # Type narrowing: _create_real_annotations returns Mapping[str, type]
                real_annotations = self._create_real_annotations(annotations)
                command_wrapper.__annotations__ = dict(real_annotations)

                def typed_wrapper(
                    *args: t.Cli.JsonValue,
                    **kwargs: t.Scalar,
                ) -> t.Cli.JsonValue:
                    raw_result = command_wrapper(*args, **kwargs)
                    normalized = (
                        FlextCliModels.Cli.CliModelConverter.convert_field_value(
                            raw_result,
                        )
                    )
                    if normalized.is_success:
                        return normalized.value
                    return str(raw_result)

                typed_wrapper.__signature__ = command_signature
                typed_wrapper.__annotations__ = dict(real_annotations)
                return typed_wrapper

        class CliParameterSpec:
            """CLI parameter specification for model-to-CLI conversion."""

            def __init__(
                self,
                field_name: str,
                param_type: type,
                click_type: str,
                default: t.Cli.JsonValue | None = None,
                help_text: str = "",
            ) -> None:
                """Initialize CLI parameter spec."""
                super().__init__()
                self.field_name = field_name
                self.param_type = param_type
                self.click_type = click_type
                self.default = default
                self.help = help_text

            @property
            def name(self) -> str:
                """Alias for field_name for compatibility."""
                return self.field_name

        class CliModelConverter:
            """Converter for Pydantic models to CLI parameters.

            Provides methods to convert Pydantic models to CLI parameter specifications
            and Click options, following FLEXT patterns with r railway pattern.
            """

            @staticmethod
            def cli_args_to_model(
                model_cls: type[BaseModel],
                cli_args: Mapping[str, t.Cli.JsonValue],
            ) -> r[BaseModel]:
                """Convert CLI arguments dict to Pydantic model instance.

                Accepts type[BaseModel] directly to work around pyright limitations
                with PEP 695 generics and local classes in tests. All BaseModel
                subclasses are compatible with type[BaseModel].
                """
                try:
                    # Use direct model_validate instead of from_dict to avoid type variable issues
                    # Type narrowing: model_cls is BaseModel subclass (checked by caller)
                    # Convert Mapping to dict for model_validate
                    cli_args_dict: Mapping[str, t.Cli.JsonValue] = dict(
                        cli_args,
                    )
                    # Type narrowing: model_cls is BaseModel subclass, model_validate exists
                    # Use getattr to access model_validate to satisfy type checker
                    # BaseModel.model_validate exists but mypy needs explicit access
                    model_validate_method = model_cls.model_validate
                    model_instance = model_validate_method(cli_args_dict)
                    return r[BaseModel].ok(model_instance)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return r[BaseModel].fail(f"Failed to create model instance: {e}")

            @staticmethod
            def extract_base_props(
                field_name: str,
                field_info: FieldInfo | Mapping[str, t.Cli.JsonValue] | t.Cli.JsonValue,
            ) -> MutableMapping[str, t.Cli.JsonValue]:
                """Extract base properties from field info."""
                annotation = (
                    field_info.annotation if isinstance(field_info, FieldInfo) else None
                )
                default_val: t.Cli.JsonValue = (
                    field_info.default
                    if isinstance(field_info, FieldInfo)
                    and getattr(field_info, "default", None) is not None
                    else ""
                )
                return {
                    "field_name": field_name,
                    "annotation": str(annotation) if annotation is not None else "str",
                    "default": default_val,
                    "description": (
                        str(field_info.description)
                        if isinstance(field_info, FieldInfo)
                        else ""
                    ),
                }

            @staticmethod
            def extract_field_properties(
                field_name: str,
                field_info: FieldInfo | Mapping[str, t.Cli.JsonValue] | t.Cli.JsonValue,
                types: Mapping[str, type | str] | None = None,
            ) -> r[Mapping[str, t.Cli.JsonValue]]:
                """Extract properties from Pydantic field info."""
                try:
                    props = FlextCliModels.Cli.CliModelConverter.extract_base_props(
                        field_name,
                        field_info,
                    )
                    if types is not None:
                        FlextCliModels.Cli.CliModelConverter.merge_types_into_props(
                            props,
                            types,
                        )
                        FlextCliModels.Cli.CliModelConverter.merge_field_info_dict(
                            props,
                            field_info,
                        )
                        FlextCliModels.Cli.CliModelConverter.merge_metadata_attr(
                            props,
                            field_info,
                        )
                        FlextCliModels.Cli.CliModelConverter.merge_json_schema_extra(
                            props,
                            field_info,
                        )
                    return r[Mapping[str, t.Cli.JsonValue]].ok(props)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return r[Mapping[str, t.Cli.JsonValue]].fail(
                        f"Extraction failed: {e}",
                    )

            @staticmethod
            def field_to_cli_param(
                field_name: str,
                field_info: FieldInfo | Mapping[str, t.Cli.JsonValue] | t.Cli.JsonValue,
            ) -> r[p.Cli.CliParameterSpec]:
                """Convert Pydantic field to CLI parameter specification."""
                try:
                    annotation = (
                        field_info.annotation
                        if isinstance(field_info, FieldInfo)
                        else None
                    )
                    default = (
                        field_info.default
                        if isinstance(field_info, FieldInfo)
                        else None
                    )
                    help_text = (
                        str(field_info.description)
                        if isinstance(field_info, FieldInfo)
                        else ""
                    )
                    if annotation is None:
                        return r[p.Cli.CliParameterSpec].fail(
                            f"Field {field_name} has no type annotation",
                        )
                    field_type = annotation
                    # Extract non-None type from Optional/Union
                    origin = get_origin(field_type)
                    if origin is not None:
                        args = get_args(field_type)
                        # models.py cannot use utilities - use list comprehension instead
                        non_none_types = [
                            arg for arg in list(args) if arg is not type(None)
                        ]
                        if non_none_types:
                            field_type = non_none_types[0]
                    click_type_str = (
                        FlextCliModels.Cli.CliModelConverter.python_type_to_click_type(
                            field_type,
                        )
                    )
                    # Return concrete instance
                    spec = FlextCliModels.Cli.CliParameterSpec(
                        field_name=field_name,
                        param_type=field_type,
                        click_type=click_type_str,
                        default=default,
                        help_text=help_text,
                    )
                    return r[p.Cli.CliParameterSpec].ok(spec)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return r[p.Cli.CliParameterSpec].fail(
                        f"Field conversion failed: {e}",
                    )

            @staticmethod
            def handle_generic_type(
                pydantic_type: type | types.UnionType,
            ) -> type | None:
                """Handle generic types like list of str, dict of str to str. Returns None if not handled."""
                origin = get_origin(pydantic_type)
                if origin is None:
                    return None
                # For generic types like t.StrSequence, t.StrMapping, return the origin
                if origin is list:
                    return list
                if origin is dict:
                    return dict
                # Extract first type argument
                args = get_args(pydantic_type)
                # models.py cannot use utilities - use list comprehension instead
                non_none_types = [arg for arg in list(args) if arg is not type(None)]
                if non_none_types:
                    first_type = non_none_types[0]
                    if isinstance(first_type, type):
                        return first_type
                return None

            @staticmethod
            def handle_union_type(pydantic_type: type | types.UnionType) -> type:
                """Handle UnionType (e.g., int | None) and extract non-None type."""
                args = get_args(pydantic_type)
                # models.py cannot use utilities - use list comprehension instead
                non_none_types = [arg for arg in list(args) if arg is not type(None)]
                if non_none_types:
                    first_type = non_none_types[0]
                    if isinstance(first_type, type):
                        return first_type
                return str  # Fallback

            @staticmethod
            def is_simple_type(pydantic_type: type) -> bool:
                """Check if it's a known simple type."""
                return pydantic_type in {
                    str,
                    int,
                    float,
                    bool,
                    list,
                    dict,
                }

            @staticmethod
            def merge_field_info_dict(
                props: MutableMapping[str, t.Cli.JsonValue],
                field_info: (
                    FieldInfo | Mapping[str, t.Cli.JsonValue] | t.Cli.JsonValue
                ),
            ) -> None:
                """Merge field_info dict attributes into props."""
                if isinstance(field_info, Mapping):
                    filtered: MutableMapping[str, t.Cli.JsonValue] = {}
                    for k, v in field_info.items():
                        key_str = str(k)
                        if key_str == "__dict__":
                            continue
                        filtered[key_str] = (
                            FlextCliModels.Cli.JSON_NORMALIZE_ADAPTER.dump_python(
                                v,
                                mode="json",
                                warnings=False,
                            )
                        )
                    props.update(filtered)
                    return
                metadata_dict = (
                    field_info.__dict__ if hasattr(field_info, "__dict__") else None
                )
                if metadata_dict is not None:
                    dict_metadata: Mapping[str, t.Cli.JsonValue] = {
                        str(k): FlextCliModels.Cli.CliModelConverter.to_json_value(v)
                        for k, v in metadata_dict.items()
                    }
                    props.update(dict_metadata)

            @staticmethod
            def merge_json_schema_extra(
                props: MutableMapping[str, t.Cli.JsonValue],
                field_info: (
                    FieldInfo | Mapping[str, t.Cli.JsonValue] | t.Cli.JsonValue
                ),
            ) -> None:
                """Merge json_schema_extra into props metadata."""
                json_schema_extra = (
                    field_info.json_schema_extra
                    if isinstance(field_info, FieldInfo)
                    else None
                )
                if json_schema_extra is None:
                    return
                # Use dict.get() for safe metadata access
                metadata_raw = props.get("metadata", {})

                try:
                    metadata_dict = (
                        FlextCliModels.Cli.DICT_STR_OBJECT_ADAPTER.validate_python(
                            metadata_raw,
                            strict=True,
                        )
                    )
                except ValidationError as exc:
                    msg = "metadata must be Mapping"
                    raise TypeError(msg) from exc

                try:
                    schema_dict = (
                        FlextCliModels.Cli.DICT_STR_OBJECT_ADAPTER.validate_python(
                            json_schema_extra,
                            strict=True,
                        )
                    )
                except ValidationError as exc:
                    msg = "json_schema_extra must be Mapping"
                    raise TypeError(msg) from exc

                dict_metadata: MutableMapping[str, t.Cli.JsonValue] = {
                    str(k): FlextCliModels.Cli.CliModelConverter.to_json_value(v)
                    for k, v in metadata_dict.items()
                }
                dict_schema: Mapping[str, t.Cli.JsonValue] = {
                    str(k): FlextCliModels.Cli.CliModelConverter.to_json_value(v)
                    for k, v in schema_dict.items()
                }
                dict_metadata.update(dict_schema)
                props["metadata"] = dict_metadata

            @staticmethod
            def merge_metadata_attr(
                props: MutableMapping[str, t.Cli.JsonValue],
                field_info: FieldInfo | Mapping[str, t.Cli.JsonValue] | t.Cli.JsonValue,
            ) -> None:
                """Merge metadata attribute into props."""
                metadata_attr = (
                    field_info.metadata if isinstance(field_info, FieldInfo) else None
                )
                if metadata_attr is None:
                    return
                if FlextCliModels.Cli.is_mapping_like(metadata_attr):
                    props["metadata"] = {
                        str(k): FlextCliModels.Cli.CliModelConverter.to_json_value(v)
                        for k, v in metadata_attr.items()
                    }
                    return
                metadata_values = list(metadata_attr)
                props["metadata"] = (
                    FlextCliModels.Cli.CliModelConverter.process_metadata_list(
                        metadata_values,
                    )
                )

            @staticmethod
            def merge_types_into_props(
                props: MutableMapping[str, t.Cli.JsonValue],
                types: Mapping[str, type | str],
            ) -> None:
                """Merge types mapping into properties dict."""
                transformed: Mapping[str, t.Cli.JsonValue] = {
                    k: str(v) for k, v in types.items()
                }
                props.update(transformed)

            @staticmethod
            def model_to_cli_params(
                model_cls: type[BaseModel],
            ) -> r[Sequence[p.Cli.CliParameterSpec]]:
                """Convert Pydantic model to list of CLI parameter specifications."""
                try:

                    def convert_field(
                        field_name: str,
                        field_info: FieldInfo,
                    ) -> p.Cli.CliParameterSpec:
                        """Convert single field to CliParameterSpec."""
                        field_type = field_info.annotation
                        # Extract non-None type from Optional/Union
                        origin = get_origin(field_type)
                        if origin is not None:
                            args = get_args(field_type)
                            # models.py cannot use utilities - use list comprehension instead
                            non_none_types_result = [
                                arg for arg in list(args) if arg is not type(None)
                            ]
                            non_none_types: Sequence[type] = non_none_types_result
                            if non_none_types:
                                field_type = non_none_types[0]
                        default = field_info.default
                        help_text = str(field_info.description or "")
                        if field_type is None:
                            param_type: type = str
                        else:
                            param_type = field_type
                        click_type_str = FlextCliModels.Cli.CliModelConverter.python_type_to_click_type(
                            param_type,
                        )
                        return FlextCliModels.Cli.CliParameterSpec(
                            field_name=field_name,
                            param_type=param_type,
                            click_type=click_type_str,
                            default=default,
                            help_text=help_text,
                        )

                    # Process model fields using dict comprehension for type safety
                    # models.py cannot use utilities - use direct iteration instead
                    try:
                        params_dict: Mapping[
                            str,
                            p.Cli.CliParameterSpec,
                        ] = {
                            field_name: convert_field(field_name, field_info)
                            for field_name, field_info in model_cls.model_fields.items()
                        }
                        params_list = list(params_dict.values())
                        return r[Sequence[p.Cli.CliParameterSpec]].ok(params_list)
                    except (
                        ValueError,
                        TypeError,
                        KeyError,
                        ConsoleError,
                        StyleError,
                        LiveError,
                    ) as e:
                        return r[Sequence[p.Cli.CliParameterSpec]].fail(
                            f"Conversion failed: {e}",
                        )
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return r[Sequence[p.Cli.CliParameterSpec]].fail(
                        f"Conversion failed: {e}",
                    )

            @staticmethod
            def model_to_click_options(
                model_cls: type[BaseModel],
            ) -> r[Sequence[t.Cli.JsonValue]]:
                """Convert Pydantic model to list of Click options."""
                params_result = (
                    FlextCliModels.Cli.CliModelConverter.model_to_cli_params(
                        model_cls,
                    )
                )
                if params_result.is_failure:
                    return r[Sequence[t.Cli.JsonValue]].fail(
                        params_result.error or "Conversion failed",
                    )
                # After is_failure check, params_result.value is guaranteed to be the value
                params: Sequence[p.Cli.CliParameterSpec] = params_result.value
                # Create Click option-like objects with option_name and param_decls
                options: MutableSequence[t.Cli.JsonValue] = []
                for param in params:
                    # Type narrowing: param is CliParameterSpec
                    # Create a simple record with option_name and param_decls attributes
                    option_name = f"--{param.field_name.replace('_', '-')}"
                    param_decls_list: t.Cli.JsonValue = [option_name]
                    # type attribute may be absent, so we use string representation
                    param_type_name: str = (
                        param.param_type.__name__
                        if hasattr(param.param_type, "__name__")
                        else "str"
                    )
                    option_obj_dict: Mapping[str, t.Cli.JsonValue] = {
                        "option_name": option_name,
                        "param_decls": param_decls_list,
                        "field_name": param.field_name,
                        "param_type": param_type_name,
                        "default": param.default if param.default is not None else "",
                        "help": param.help,  # CliParameterSpec stores as .help, not .help_text
                    }
                    options.append(option_obj_dict)
                return r[Sequence[t.Cli.JsonValue]].ok(options)

            @staticmethod
            def process_metadata_list(
                metadata_attr: Sequence[t.Cli.JsonValue],
            ) -> Mapping[str, t.Cli.JsonValue]:
                """Process metadata list into dict."""
                result: MutableMapping[str, t.Cli.JsonValue] = {}
                for item in metadata_attr:
                    if FlextCliModels.Cli.is_mapping_like(item):
                        dict_item = {
                            str(k): FlextCliModels.Cli.CliModelConverter.to_json_value(
                                v,
                            )
                            for k, v in item.items()
                        }
                        result.update(dict_item)
                    elif hasattr(item, "__dict__"):
                        item_dict = item.__dict__
                        if FlextCliModels.Cli.is_mapping_like(item_dict):
                            dict_item = {
                                str(
                                    k,
                                ): FlextCliModels.Cli.CliModelConverter.to_json_value(v)
                                for k, v in item_dict.items()
                            }
                            result.update(dict_item)
                return result

            @staticmethod
            def pydantic_type_to_python_type(
                pydantic_type: type | types.UnionType,
            ) -> type:
                """Convert Pydantic type annotation to Python type."""
                # Handle Optional/Union types - Python 3.10+ union types
                if get_origin(pydantic_type) is types.UnionType:
                    return FlextCliModels.Cli.CliModelConverter.handle_union_type(
                        pydantic_type,
                    )
                # Handle generic types like t.StrSequence, t.StrMapping
                generic_result = (
                    FlextCliModels.Cli.CliModelConverter.handle_generic_type(
                        pydantic_type,
                    )
                )
                if generic_result is not None:
                    return generic_result
                # Check if it's a known simple type
                if isinstance(
                    pydantic_type,
                    type,
                ) and FlextCliModels.Cli.CliModelConverter.is_simple_type(
                    pydantic_type,
                ):
                    return pydantic_type
                # Default to str for complex types
                return str

            @staticmethod
            def python_type_to_click_type(python_type: type) -> str:
                """Convert Python type to Click type string."""
                type_name = (
                    python_type.__name__
                    if hasattr(python_type, "__name__")
                    else str(python_type)
                )
                click_type_map = {
                    "str": "STRING",
                    "int": "INT",
                    "float": "FLOAT",
                    "bool": "BOOL",
                    "list": "STRING",  # Click handles lists as strings
                    "dict": "STRING",  # Click handles dicts as strings
                }
                return click_type_map.get(type_name, "STRING")

            @staticmethod
            def to_json_value(
                value: t.Cli.JsonValue,
            ) -> t.Cli.JsonValue:
                """Convert arbitrary value into JSON-compatible value."""
                converted = FlextCliModels.Cli.CliModelConverter.convert_field_value(
                    value,
                )
                if converted.is_success:
                    return converted.value
                return str(value)

            @staticmethod
            def _is_python_type_value(value: t.Cli.JsonValue) -> bool:
                return isinstance(value, type)

            @staticmethod
            def _is_string_value(value: t.Cli.JsonValue) -> bool:
                return isinstance(value, str)

            @staticmethod
            def _is_boolean_value(value: t.Cli.JsonValue) -> bool:
                return value in {True, False}

            @staticmethod
            def _is_validators_value(value: t.Cli.JsonValue) -> bool:
                return isinstance(value, (list, tuple)) and not isinstance(
                    value,
                    (Mapping, bytes),
                )

            @staticmethod
            def _is_mapping_value(value: t.Cli.JsonValue) -> bool:
                return isinstance(value, Mapping)

            # Field validation rules: (field_key, expected_type, type_check_func)
            FIELD_VALIDATION_RULES: ClassVar[
                Sequence[tuple[str, str, Callable[..., bool]]]
            ] = [
                (
                    "python_type",
                    "type",
                    _is_python_type_value,
                ),
                (
                    "click_type",
                    "str",
                    _is_string_value,
                ),
                (
                    "is_required",
                    "bool",
                    _is_boolean_value,
                ),
                (
                    "description",
                    "str",
                    _is_string_value,
                ),
                (
                    "validators",
                    "list/tuple",
                    _is_validators_value,
                ),
                (
                    "metadata",
                    "dict",
                    _is_mapping_value,
                ),
            ]

            JSON_VALUE_ADAPTER: ClassVar[TypeAdapter[t.Cli.JsonValue]] = TypeAdapter(
                t.Cli.JsonValue,
            )

            @staticmethod
            def _process_validators(
                field_info: (
                    Sequence[Callable[..., t.Cli.JsonValue]]
                    | Sequence[t.Cli.JsonValue]
                    | t.Cli.JsonValue
                ),
            ) -> Sequence[Callable[..., t.Cli.JsonValue]]:
                """Process validators from field info, filtering only callable validators."""
                if not isinstance(field_info, (list, tuple, range)):
                    return []
                return [
                    item
                    for item in field_info
                    if callable(item) and not isinstance(item, type)
                ]

            @staticmethod
            def _validate_field_data(
                field_name: str,
                field_info: (
                    FieldInfo | Mapping[str, t.Cli.JsonValue] | t.Cli.JsonValue
                ),
                data: Mapping[str, t.Cli.JsonValue] | None = None,
            ) -> r[t.Cli.JsonValue]:
                """Validate field data against field info."""
                try:
                    if isinstance(field_info, Mapping):
                        field_data: Mapping[str, t.Cli.JsonValue] = {
                            str(k): v for k, v in field_info.items()
                        }
                        return FlextCliModels.Cli.CliModelConverter.validate_dict_field_data(
                            field_name,
                            field_data,
                        )
                    if data is not None:
                        if field_name not in data:
                            return r[t.Cli.JsonValue].fail(
                                f"Field {field_name} not found",
                            )
                        return r.ok(data[field_name])
                    return r[t.Cli.JsonValue].fail(
                        "No data provided for validation",
                    )
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return r[t.Cli.JsonValue].fail(
                        f"Validation failed: {e}",
                    )

            @staticmethod
            def convert_field_value(
                field_value: t.Cli.JsonValue,
            ) -> r[t.Cli.JsonValue]:
                """Convert field value to JSON-compatible value.

                models.py cannot use utilities - use direct conversion instead.
                Uses lower-layer JSON contracts for strict type safety.
                """
                if field_value is None:
                    return r.ok("")
                try:
                    json_value = FlextCliModels.Cli.CliModelConverter.JSON_VALUE_ADAPTER.validate_python(
                        field_value,
                    )
                    return r.ok(json_value)
                except ValidationError as exc:
                    _logger.debug(
                        "convert_field_value validation fallback",
                        error=exc,
                        exc_info=False,
                    )
                    return r.ok(str(field_value))

            @staticmethod
            def validate_dict_field_data(
                field_name: str,
                field_data: Mapping[str, t.Cli.JsonValue],
            ) -> r[t.Cli.JsonValue]:
                """Validate field data when field_info is a dict/Mapping."""
                schema_result = (
                    FlextCliModels.Cli.CliModelConverter.validate_field_schema(
                        field_data,
                    )
                )
                if schema_result.is_failure:
                    return r[t.Cli.JsonValue].fail(
                        schema_result.error or "Schema validation failed",
                    )
                field_value = field_data.get(field_name, None)
                return FlextCliModels.Cli.CliModelConverter.convert_field_value(
                    field_value,
                )

            @staticmethod
            def validate_field_schema(
                field_data: Mapping[str, t.Cli.JsonValue],
            ) -> r[bool]:
                """Validate field data schema against rules."""
                for (
                    field_key,
                    type_name,
                    check_func,
                ) in FlextCliModels.Cli.CliModelConverter.FIELD_VALIDATION_RULES:
                    if field_key in field_data:
                        value = field_data[field_key]
                        if not check_func(value):
                            return r[bool].fail(
                                f"Invalid {field_key}: {value} (expected {type_name})",
                            )
                return r[bool].ok(True)

        class CliModelDecorators:
            """Decorators for creating CLI commands from Pydantic models."""

            @staticmethod
            def cli_from_model(
                model_class: type[BaseModel],
            ) -> Callable[
                [
                    Callable[
                        [BaseModel],
                        r[t.Cli.JsonValue] | t.Cli.JsonValue,
                    ],
                ],
                p.Cli.CliCommandWrapper,
            ]:
                """Create decorator that converts function to CLI command from model."""

                def decorator(
                    func: Callable[
                        [BaseModel],
                        r[t.Cli.JsonValue] | t.Cli.JsonValue,
                    ],
                ) -> p.Cli.CliCommandWrapper:
                    def wrapper(
                        *_args: t.Cli.JsonValue,
                        **kwargs: t.Scalar,
                    ) -> t.Cli.JsonValue:
                        try:
                            # Create model instance from kwargs
                            model_instance = model_class(**kwargs)
                            # Call original function with model
                            result = func(model_instance)
                            # Convert result to JSON-compatible value if needed
                            output: t.Cli.JsonValue
                            if isinstance(result, r):
                                if result.is_success:
                                    output = FlextCliModels.Cli.CliModelDecorators.normalize_output(
                                        result.value,
                                    )
                                else:
                                    output = str(result.error or "Unknown error")
                            else:
                                output = FlextCliModels.Cli.CliModelDecorators.normalize_output(
                                    result,
                                )
                        except (
                            ValueError,
                            TypeError,
                            KeyError,
                            ConsoleError,
                            StyleError,
                            LiveError,
                        ) as e:
                            # Return error string on failure (decorator pattern)
                            output = f"Validation failed: {e}"
                        return output

                    return wrapper

                return decorator

            @staticmethod
            def cli_from_multiple_models(
                *model_classes: type[BaseModel],
            ) -> Callable[
                [p.Cli.CliCommandWrapper],
                p.Cli.CliCommandWrapper,
            ]:
                """Create decorator for multiple models."""

                def decorator(
                    func: p.Cli.CliCommandWrapper,
                ) -> p.Cli.CliCommandWrapper:
                    def wrapper(
                        *_args: t.Cli.JsonValue,
                        **kwargs: t.Scalar,
                    ) -> t.Cli.JsonValue:
                        try:
                            model_instances: Sequence[BaseModel] = [
                                model_cls(**kwargs) for model_cls in model_classes
                            ]
                            result: t.Cli.JsonValue = func(
                                *(inst.model_dump() for inst in model_instances),
                            )
                            return result
                        except (
                            ValueError,
                            TypeError,
                            KeyError,
                            ConsoleError,
                            StyleError,
                            LiveError,
                        ) as e:
                            return f"Validation failed: {e}"

                    return wrapper

                return decorator

            @staticmethod
            def normalize_output(
                value: t.Cli.JsonValue,
            ) -> t.Cli.JsonValue:
                """Normalize any value to JSON-compatible value."""
                normalized: r[t.Cli.JsonValue] = (
                    FlextCliModels.Cli.CliModelConverter.convert_field_value(value)
                )
                if normalized.is_success:
                    return normalized.value
                return str(value)

        class CliDebugData(FlextModels.Value):
            """CLI debug summary data.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            service: Annotated[str, Field(..., description="Service name")]
            level: Annotated[str, Field(..., description="Debug level")]
            message: Annotated[str, Field(..., description="Debug message")]

        class Display:
            """Rich display type aliases using Protocols.

            These type aliases reference protocol types from flext_cli.protocols.
            Located in Tier 1 (models.py) to allow protocol imports.
            """

            # Reference protocol types (FlextCliModels.Cli.Display.*)
            type RichTable = p.Cli.RichTable
            type RichTree = p.Cli.RichTree
            type Console = p.Cli.RichConsole

        class Interactive:
            """Interactive display type aliases using Protocols.

            These type aliases reference protocol types from flext_cli.protocols.
            Located in Tier 1 (models.py) to allow protocol imports.
            """

            # Reference protocol types (FlextCliModels.Cli.Interactive.*)
            type Progress = p.Cli.RichProgress


__all__ = [
    "FlextCliModels",
    "m",
]

m = FlextCliModels
