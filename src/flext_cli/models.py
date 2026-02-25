"""FlextCli models module - Pydantic models with StrEnuFlextCliModels."""

from __future__ import annotations

import operator
import types
from collections.abc import Callable, Mapping, MutableMapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import (
    ClassVar,
    Literal,
    Self,
    TypeGuard,
    Union,
    get_args,
    get_origin,
    override,
)

import typer
from flext_core import FlextLogger, FlextModels, FlextResult, r
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

from flext_cli.constants import FlextCliConstants as c
from flext_cli.protocols import FlextCliProtocols as p
from flext_cli.typings import t

_logger = FlextLogger(__name__)


def _is_mapping_like(obj: object) -> TypeGuard[Mapping[str, object]]:
    """Narrow object to Mapping for metadata processing."""
    return isinstance(obj, Mapping)


def _normalize_to_json_value(item: object) -> t.JsonValue:
    """Recursively normalize any value to JSON-serializable (t.JsonValue)."""
    if item is None or isinstance(item, (str, int, float, bool)):
        return item
    if isinstance(item, BaseModel):
        raw = item.model_dump(mode="json")
        return _normalize_to_json_value(raw)
    if isinstance(item, Path):
        return str(item)
    if isinstance(item, datetime):
        return item.isoformat()
    if isinstance(item, Mapping):
        return {str(k): _normalize_to_json_value(vv) for k, vv in item.items()}
    if isinstance(item, Sequence) and not isinstance(item, str):
        return [_normalize_to_json_value(x) for x in item]
    return str(item)


class _CliNormalizedJson(RootModel[t.JsonValue]):
    """Single contract: any value normalized to JSON (t.JsonValue)."""

    @model_validator(mode="wrap")
    @classmethod
    def _normalize(
        cls, data: object, handler: Callable[[t.JsonValue], _CliNormalizedJson]
    ) -> _CliNormalizedJson:
        normalized = _normalize_to_json_value(data)
        return handler(normalized)


class _JsonNormalizeInput(BaseModel):
    """Single contract for norm_json: value -> normalized JsonValue."""

    model_config = ConfigDict(extra="forbid")
    value: t.ConfigMapValue = Field(description="Value to normalize")

    @computed_field
    @property
    def normalized(self) -> t.JsonValue:
        return _CliNormalizedJson.model_validate(self.value).root


class _EnsureTypeRequest(BaseModel):
    """Single contract for ensure_str/ensure_bool. Delegates to TypedExtract."""

    model_config = ConfigDict(extra="forbid")
    kind: Literal["str", "bool"] = Field(description="Requested type")
    value: t.JsonValue | None = Field(default=None)
    default: str | bool = Field(description="Default value")

    def result(self) -> str | bool:
        out = _TypedExtract(
            type_kind=self.kind,
            value=self.value,
            default=self.default,
        ).resolved
        if self.kind == "bool":
            return bool(out) if out is not None else bool(self.default)
        return str(out) if out is not None else str(self.default)


class _MapGetValue(BaseModel):
    """Single contract for get_map_val: map + key + default -> value (normalized)."""

    model_config = ConfigDict(extra="forbid")
    map_: Mapping[str, t.JsonValue] = Field(alias="map", description="Source mapping")
    key: str = Field(description="Key to look up")
    default: t.JsonValue = Field(description="Default if key missing")

    def result(self) -> t.JsonValue:
        val = self.map_.get(self.key, self.default)
        if val is None or isinstance(val, (str, int, float, bool, list)):
            return val
        if isinstance(val, dict):
            return {str(k): _normalize_to_json_value(vv) for k, vv in val.items()}
        return _normalize_to_json_value(val)


class _DictKeysExtract(BaseModel):
    """Single contract for get_keys: input -> list of keys (empty if not dict)."""

    model_config = ConfigDict(extra="forbid")
    input_: t.JsonValue | Mapping[str, t.JsonValue] = Field(
        alias="input", description="Value to extract keys from"
    )

    @computed_field
    @property
    def resolved(self) -> list[str]:
        if isinstance(self.input_, Mapping):
            return list(self.input_.keys())
        root = getattr(self.input_, "root", None)
        if isinstance(root, Mapping):
            return list(root.keys())
        return []


class _EnsureDictInput(BaseModel):
    """Single contract for ensure_dict: value + default -> Mapping[str, JsonValue]."""

    model_config = ConfigDict(extra="forbid")
    value: t.JsonValue | None = Field(default=None)
    default: dict[str, t.JsonValue] = Field(default_factory=dict)

    @computed_field
    @property
    def resolved(self) -> Mapping[str, t.JsonValue]:
        if self.value is None:
            return self.default
        root_val = getattr(self.value, "root", None)
        source = root_val if root_val is not None else self.value
        if isinstance(source, Mapping):
            return {str(k): _normalize_to_json_value(vv) for k, vv in source.items()}
        adapter: TypeAdapter[dict[str, t.JsonValue]] = TypeAdapter(
            dict[str, t.JsonValue]
        )
        try:
            parsed = adapter.validate_python(source)
            return {str(k): _normalize_to_json_value(vv) for k, vv in parsed.items()}
        except ValidationError:
            return self.default


class _EnsureListInput(BaseModel):
    """Single contract for ensure_list: value + default -> list[JsonValue]."""

    model_config = ConfigDict(extra="forbid")
    value: t.JsonValue | None = Field(default=None)
    default: list[t.JsonValue] = Field(default_factory=list)

    @computed_field
    @property
    def resolved(self) -> list[t.JsonValue]:
        if self.value is None:
            return list(self.default)
        root_val = getattr(self.value, "root", None)
        source = root_val if root_val is not None else self.value
        adapter: TypeAdapter[list[t.JsonValue]] = TypeAdapter(list[t.JsonValue])
        try:
            seq = adapter.validate_python(source)
            return [_normalize_to_json_value(x) for x in seq]
        except ValidationError:
            return list(self.default)


class _PromptTimeoutResolved(BaseModel):
    """Single contract: raw (int | str | None) + default → int. Replaces isinstance(timeout_raw, int/str) branching."""

    model_config = ConfigDict(extra="forbid")
    raw: int | str | None = Field(default=None)
    default: int = Field(default=30, description="Default timeout in seconds")

    @computed_field
    @property
    def resolved(self) -> int:
        if self.raw is None:
            return self.default
        if isinstance(self.raw, int):
            return self.raw
        if isinstance(self.raw, str) and self.raw.isdigit():
            return int(self.raw)
        return self.default


class _ExecutionContextInput(
    RootModel[Sequence[str] | Mapping[str, t.JsonValue] | None],
):
    """Execution context: None, list of args, or mapping. Single Pydantic contract. Use model_validate(context) then .to_mapping() or .root."""

    def to_mapping(
        self,
        list_processor: Callable[[Sequence[str]], list[t.JsonValue]] | None = None,
    ) -> dict[str, t.JsonValue]:
        raw = self.root
        if raw is None:
            return {}
        if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
            lst = list(raw)
            processed = list_processor(lst) if list_processor else lst
            return {c.Cli.DictKeys.ARGS: processed}
        if isinstance(raw, Mapping):
            return dict(raw)
        return {}


class _JsonNormalizeInput(BaseModel):
    """Single contract: normalize ConfigMapValue to JsonValue. Replaces norm_json branching."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    value: t.ConfigMapValue = Field(..., description="Value to normalize")

    @computed_field
    @property
    def normalized(self) -> t.JsonValue:
        return _normalize_json_value(self.value)


def _normalize_json_value(item: t.ConfigMapValue) -> t.JsonValue:
    if isinstance(item, (str, int, float, bool, type(None))):
        return item
    root = getattr(item, "root", None)
    source = root if root is not None else item
    if isinstance(source, Mapping):
        return {str(k): _normalize_json_value(v) for k, v in source.items()}
    if isinstance(source, Sequence) and not isinstance(source, (str, bytes)):
        return [_normalize_json_value(i) for i in source]
    return str(item)


class _EnsureTypeRequest(BaseModel):
    """Single contract: coerce value to str or bool with default. Replaces ensure_str/ensure_bool branching."""

    model_config = ConfigDict(extra="forbid")
    kind: Literal["str", "bool"] = Field(description="Target type")
    value: t.JsonValue | None = Field(default=None)
    default: str | bool = Field(default="")

    def result(self) -> str | bool:
        if self.kind == "str":
            default_str = self.default if isinstance(self.default, str) else ""
            if self.value is None:
                return default_str
            try:
                s = str(self.value)
                return s or default_str
            except (TypeError, ValueError):
                return default_str
        # bool
        default_bool = self.default if isinstance(self.default, bool) else False
        if self.value is None:
            return default_bool
        try:
            return bool(self.value)
        except (TypeError, ValueError):
            return default_bool


class _MapGetValue(BaseModel):
    """Single contract: get key from mapping and normalize value. Replaces get_map_val branching."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    map_: Mapping[str, t.JsonValue] = Field(..., alias="map_", description="Mapping")
    key: str = Field(..., description="Key")
    default: t.JsonValue = Field(default=None, description="Default")

    def result(self) -> t.JsonValue:
        value = self.map_.get(self.key, self.default)
        if value is None or isinstance(value, (str, int, float, bool, list)):
            return value
        if isinstance(value, dict):
            out: dict[str, t.JsonValue] = {}
            for kk, vv in value.items():
                if isinstance(
                    vv,
                    (str, int, float, bool, type(None), list, dict),
                ):
                    out[str(kk)] = vv
                else:
                    out[str(kk)] = str(vv)
            return out
        return str(value)


class _NormalizedJsonList(BaseModel):
    """Single contract: ensure value is list of JsonValue with default. Replaces ensure_list branching."""

    model_config = ConfigDict(extra="forbid")
    value: t.JsonValue | None = Field(default=None, description="Value to coerce")
    default: list[t.JsonValue] = Field(
        default_factory=list,
        description="Default when value is None or invalid",
    )

    @computed_field
    @property
    def resolved(self) -> list[t.JsonValue]:
        if self.value is None:
            return list(self.default)
        root = getattr(self.value, "root", None)
        source = root if root is not None else self.value
        try:
            adapter: TypeAdapter[list[t.JsonValue]] = TypeAdapter(list[t.JsonValue])
            raw_list = adapter.validate_python(source)
            return [_normalize_json_value(i) for i in raw_list]
        except ValidationError:
            return list(self.default)


class _NormalizedJsonDict(BaseModel):
    """Single contract: ensure value is dict[str, JsonValue] with default. Replaces ensure_dict branching."""

    model_config = ConfigDict(extra="forbid")
    value: t.JsonValue | None = Field(default=None, description="Value to coerce")
    default: dict[str, t.JsonValue] = Field(
        default_factory=dict,
        description="Default when value is None or invalid",
    )

    @computed_field
    @property
    def resolved(self) -> dict[str, t.JsonValue]:
        if self.value is None:
            return dict(self.default)
        root = getattr(self.value, "root", None)
        source = root if root is not None else self.value
        try:
            adapter: TypeAdapter[dict[str, t.JsonValue]] = TypeAdapter(
                dict[str, t.JsonValue]
            )
            raw_dict = adapter.validate_python(source)
            return {str(k): _normalize_json_value(v) for k, v in raw_dict.items()}
        except ValidationError:
            return dict(self.default)


class _TypedExtract(BaseModel):
    """Single contract for typed value extraction (str | bool | dict). Replaces polymorphic _extract_typed_value."""

    model_config = ConfigDict(extra="forbid")
    type_kind: Literal["str", "bool", "dict"] = Field(description="Requested type")
    value: t.JsonValue | None = Field(default=None)
    default: t.JsonValue | None = Field(default=None)

    @computed_field
    @property
    def resolved(self) -> str | bool | dict[str, t.JsonValue] | None:
        """Value coerced to type_kind, or default. Single Pydantic contract (no polymorphic methods)."""
        if self.value is None:
            return _default_for_type_kind(self.type_kind, self.default)
        if self.type_kind == "str":
            s = str(self.value).strip() if self.value else ""
            return s or (self.default if isinstance(self.default, str) else None)
        if self.type_kind == "bool":
            return (
                bool(self.value)
                if self.value is not None
                else (self.default if isinstance(self.default, bool) else False)
            )
        if self.type_kind == "dict":
            if isinstance(self.value, Mapping):
                return {
                    str(k): _normalize_to_json_value(vv) for k, vv in self.value.items()
                }
            if isinstance(self.default, Mapping):
                return {
                    str(k): _normalize_to_json_value(vv)
                    for k, vv in self.default.items()
                }
            return {}
        return _default_for_type_kind(self.type_kind, self.default)


def _default_for_type_kind(
    type_kind: Literal["str", "bool", "dict"],
    default: t.JsonValue | None,
) -> str | bool | dict[str, t.JsonValue] | None:
    """Default value for type_kind. Centralized (no polymorphic branches at call sites)."""
    if type_kind == "str":
        return default if isinstance(default, str) else None
    if type_kind == "bool":
        return default if isinstance(default, bool) else False
    if isinstance(default, Mapping):
        return dict(default)
    return {}


class _LogLevelResolved(BaseModel):
    """Single contract for log level string (replaces u.Parser.convert for log level)."""

    model_config = ConfigDict(extra="forbid")
    raw: str | None = Field(default=None)
    default: str = Field(default="INFO")

    @computed_field
    @property
    def resolved(self) -> str:
        s = (self.raw or self.default).strip().upper()
        return s or self.default


class _CliLoggingData(BaseModel):
    """CLI logging data model - defined at module level to avoid Pydantic field inheritance issues.

    CRITICAL: Defined OUTSIDE nested classes to prevent Pydantic from merging fields.
    Pydantic nested classes can share field definitions if defined in sequence,
    so this is at module level and then aliased into Cli namespace.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    level: str = Field(
        default="INFO",
        description="Logging level",
    )
    format: str = Field(
        default="%(asctime)s - %(message)s",
        description="Logging format",
    )


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

    class Cli:
        """CLI project namespace - PADRAO HIERARQUICO.

        Este namespace contem todos os modelos CLI especificos do flext-cli.
        Acesso via: FlextCliModels.Cli.Entity, FlextCliModels.Cli.Value, FlextCliModels.Cli.CliCommand, etc.

        PADRAO: Namespace hierarquico completo, sem duplicacao.
        """

        # Module-level Pydantic model aliased to avoid field inheritance issues
        CliLoggingData: ClassVar = _CliLoggingData
        ExecutionContextInput: ClassVar = _ExecutionContextInput
        TypedExtract: ClassVar = _TypedExtract
        LogLevelResolved: ClassVar = _LogLevelResolved
        PromptTimeoutResolved: ClassVar = _PromptTimeoutResolved
        JsonNormalizeInput: ClassVar = _JsonNormalizeInput
        NormalizedJsonList: ClassVar = _NormalizedJsonList
        NormalizedJsonDict: ClassVar = _NormalizedJsonDict
        EnsureTypeRequest: ClassVar = _EnsureTypeRequest
        MapGetValue: ClassVar = _MapGetValue

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
        def execute() -> r[Mapping[str, t.JsonValue]]:
            """Execute a no-op command returning an empty result."""
            return r[Mapping[str, t.JsonValue]].ok({})

        class TableConfig(FlextModels.Value):
            """Table display configuration for tabulate extending Value via inheritance.

            Fields map directly to tabulate() parameters.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            # Headers configuration
            headers: str | Sequence[str] = Field(
                default="keys",
                description=(
                    "Table headers (string like 'keys', 'firstrow' "
                    "or sequence of header names)"
                ),
            )
            show_header: bool = Field(
                default=True,
                description="Whether to show table header",
            )

            # Format configuration
            table_format: str = Field(
                default="simple",
                description="Table format (simple, grid, fancy_grid, pipe, orgtbl, etc.)",
            )

            # Number formatting
            floatfmt: str = Field(
                default=".4g",
                description="Float format string",
            )
            numalign: str = Field(
                default="decimal",
                description="Number alignment (right, center, left, decimal)",
            )

            # String formatting
            stralign: str = Field(
                default="left",
                description="String alignment (left, center, right)",
            )

            # General alignment (alias for stralign/numalign compatibility)
            align: str = Field(
                default="left",
                description="General alignment (left, center, right, decimal)",
            )

            # Missing values
            missingval: str = Field(
                default="",
                description="String to use for missing values",
            )

            # Index display
            showindex: bool | str | Sequence[str | int] = Field(
                default=False,
                description="Whether to show row indices",
            )

            # Column alignment
            colalign: Sequence[str] | None = Field(
                default=None,
                description="Per-column alignment (left, center, right, decimal)",
            )

            # Number parsing
            disable_numparse: bool | Sequence[int] = Field(
                default=False,
                description="Disable number parsing (bool or list of column indices)",
            )

            def get_effective_colalign(self) -> Sequence[str] | None:
                """Get effective column alignment, resolving None to default."""
                return self.colalign

        class LoggingConfig(FlextModels.Value):
            """Logging configuration model extending Value via inheritance.

            Manages logging behavior for CLI applications with level, format, and output settings.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            log_level: str = Field(
                default="INFO",
                description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            )
            log_format: str = Field(
                default="%(asctime)s - %(levelname)s - %(message)s",
                description="Log message format string",
            )
            console_output: bool = Field(
                default=True,
                description="Whether to output logs to console",
            )
            log_file: str = Field(
                default="",
                description="Log file path (empty string means no file logging)",
            )

            @computed_field
            def logging_summary(self) -> _CliLoggingData:
                """Return logging summary as structured data."""
                # Use model_construct with module-level _CliLoggingData
                return _CliLoggingData.model_construct(
                    level=self.log_level,
                    format=self.log_format,
                )

        class CliCommand(FlextModels.Entity):
            """CLI command model extending Entity via inheritance."""

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
                use_enum_values=True,
                validate_default=True,
                str_strip_whitespace=True,
                # Override TimestampableMixin fields to use strings instead of datetime
                # This avoids frozen instance errors during initialization
            )

            # Inherit created_at and updated_at from Entity - frozen=True makes them read-only
            # Entity provides these fields, and frozen models inherit them correctly
            def model_post_init(self, __context: object, /) -> None:
                """Post-initialization hook for frozen model compatibility.

                Uses standard Pydantic 2 signature for model_post_init.
                Entity's timestamp fields are inherited and work correctly with frozen=True.
                """
                # Entity handles timestamp initialization via its own model_post_init

            def _copy_with_update(self, **updates: object) -> Self:
                """Helper method for model_copy with updates - reduces repetition.

                Composition pattern: centralizes model_copy logic for reuse.
                Uses object instead of t.JsonValue to accept Protocol types.
                """
                return self.model_copy(update=updates)

            name: str = Field(
                ...,
                min_length=1,
                description="Command name",
            )

            command_line: str = Field(
                default="",
                description="Full command line",
            )

            description: str = Field(
                default="",
                description="Command description",
            )

            usage: str = Field(
                default="",
                description="Command usage information",
            )

            entry_point: str = Field(
                default="",
                description="Command entry point",
            )

            plugin_version: str = Field(
                default="default",
                description="Plugin version",
            )

            args: Sequence[str] = Field(
                default_factory=list,
                description="Command arguments",
            )

            status: str = Field(
                default="pending",
                description="Command execution status",
            )

            exit_code: int | None = Field(
                default=None,
                description="Command exit code",
            )

            output: str = Field(
                default="",
                description="Command output",
            )

            error_output: str = Field(
                default="",
                description="Command error output",
            )

            execution_time: float | None = Field(
                default=None,
                description="Command execution time",
            )

            result: t.JsonValue | None = Field(
                default=None,
                description="Command result",
            )

            kwargs: dict[str, t.JsonValue] = Field(
                default_factory=dict,
                description="Command keyword arguments",
            )

            def execute(
                self,
                _args: Sequence[str],
            ) -> r[t.JsonValue]:
                """Execute command with arguments - required by Command.

                Args:
                    _args: Command arguments (unused in default implementation)

                Returns:
                    r[t.JsonValue]: Command execution result

                """
                # Default implementation - returns empty result
                # Real implementations should override this method
                return r[t.JsonValue].ok(None)

            def with_status(self, status: str) -> Self:
                """Return copy with new status.

                Accepts both str and CommandStatus" for protocol compatibility.
                """
                return self._copy_with_update(status=str(status))

            def with_args(self, args: Sequence[str]) -> Self:
                """Return copy with new arguments."""
                return self._copy_with_update(args=list(args))

            @property
            def command_summary(self) -> Mapping[str, str]:
                """Return command summary as dict."""
                return {"command": self.command_line or self.name}

            @property
            def is_pending(self) -> bool:
                """Check if command is pending."""
                return self.status == c.Cli.CommandStatus.PENDING.value

            @property
            def is_running(self) -> bool:
                """Check if command is running."""
                return self.status == c.Cli.CommandStatus.RUNNING.value

            @property
            def is_completed(self) -> bool:
                """Check if command is completed."""
                return self.status == c.Cli.CommandStatus.COMPLETED.value

            @property
            def is_failed(self) -> bool:
                """Check if command failed."""
                return self.status == c.Cli.CommandStatus.FAILED.value

            def start_execution(self) -> r[Self]:
                """Start command execution - update status to running."""
                try:
                    updated = self.model_copy(update={"status": "running"})
                    return r.ok(updated)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return r.fail(f"Failed to start execution: {e}")

            def complete_execution(self, exit_code: int) -> r[Self]:
                """Complete command execution with exit code."""
                try:
                    updated = self.model_copy(
                        update={"status": "completed", "exit_code": exit_code},
                    )
                    return r.ok(updated)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return r.fail(f"Failed to complete execution: {e}")

            def update_status(self, status: str) -> Self:
                """Update command status."""
                return self.model_copy(update={"status": status})

            @classmethod
            def validate_command_input(
                cls,
                data: Mapping[str, t.JsonValue] | Self,
            ) -> r[Self]:
                """Validate command input data."""
                if not isinstance(data, Mapping) and not isinstance(data, cls):
                    return r.fail("Input must be a dictionary")
                try:
                    command = cls.model_validate(data)
                    return r.ok(command)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return r.fail(f"Validation failed: {e}")

        class CliSession(FlextModels.Entity):
            """CLI session model for tracking command execution sessions extending Entity via inheritance."""

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
                use_enum_values=True,
                validate_default=True,
            )

            session_id: str = Field(..., min_length=1, description="Session identifier")
            user_id: str = Field(default="", description="User identifier")
            status: str = Field(
                ...,
                description="Session status",
            )

            @field_validator("status")
            @classmethod
            def validate_status(cls, value: object) -> str:
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
            commands: Sequence[FlextCliModels.Cli.CliCommand] = Field(
                default_factory=list,
                description="Commands in session",
            )
            start_time: str | None = Field(
                default=None,
                description="Session start time",
            )
            end_time: str | None = Field(default=None, description="Session end time")
            last_activity: str | None = Field(
                default=None,
                description="Last activity timestamp",
            )
            internal_duration_seconds: float = Field(
                default=0.0,
                description="Internal duration in seconds",
            )
            commands_executed: int = Field(
                default=0,
                description="Number of commands executed",
            )

            # Inherit created_at and updated_at from Entity - frozen=True makes them read-only
            # Entity provides these fields, and frozen models inherit them correctly
            @override
            def model_post_init(self, __context: object, /) -> None:
                """Post-initialization hook for frozen model compatibility.

                Entity's timestamp fields are inherited and work correctly with frozen=True.
                """
                # Entity handles timestamp initialization via its own model_post_init

            @property
            def session_summary(self) -> FlextCliModels.Cli.CliSessionData:
                """Return session summary as CliSessionData model."""
                # Return concrete model instance (not protocol)
                return FlextCliModels.Cli.CliSessionData(
                    session_id=self.session_id,
                    status=self.status,
                    commands_count=len(self.commands),
                )

            def commands_by_status(
                self,
                status: str | None = None,
            ) -> (
                list[FlextCliModels.Cli.CliCommand]
                | Mapping[str, list[FlextCliModels.Cli.CliCommand]]
            ):
                """Get commands filtered by status or grouped by all statuses.

                Args:
                    status: Optional status to filter by. If None, returns all grouped.

                Returns:
                    If status provided: List of commands matching that status
                    If status is None: Mapping of status -> commands

                """
                cli_commands: list[FlextCliModels.Cli.CliCommand] = list(self.commands)
                result: dict[str, list[FlextCliModels.Cli.CliCommand]] = {}
                for command in cli_commands:
                    cmd_status = command.status or ""
                    if cmd_status not in result:
                        result[cmd_status] = []
                    result[cmd_status].append(command)

                if status is not None:
                    return result.get(status, [])
                return result

            def add_command(self, command: FlextCliModels.Cli.CliCommand) -> r[Self]:
                """Add command to session."""
                try:
                    updated_commands = list(self.commands) + [command]
                    updated_session = self._copy_with_update(commands=updated_commands)
                    return r.ok(updated_session)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return r.fail(f"Failed to add command: {e}")

            def _copy_with_update(self, **updates: object) -> Self:
                """Helper method for model_copy with updates - reduces repetition.

                Composition pattern: centralizes model_copy logic for reuse.
                Uses object instead of t.JsonValue to accept Protocol types.
                """
                return self.model_copy(update=updates)

        class CliSessionData(FlextModels.Value):
            """CLI session summary data extending FlextModels.Value via inheritance.

            Inherits frozen=True and extra="forbid" from FlextModels.Value
            (via FrozenStrictModel), no need to redefine.
            """

            session_id: str = Field(..., description="Session identifier")
            status: str = Field(..., description="Session status")
            commands_count: int = Field(default=0, description="Number of commands")

        class CliContext(FlextModels.Value):
            """CLI execution context model extending Value via inheritance."""

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
                use_enum_values=True,
            )

            cwd: str = Field(
                ...,
                description="Current working directory",
            )

            env: dict[str, str] = Field(
                default_factory=dict,
                description="Environment variables",
            )

            args: Sequence[str] = Field(
                default_factory=list,
                description="Command line arguments",
            )

            output_format: c.Cli.OutputFormats = Field(
                default=c.Cli.OutputFormats.TABLE,
                description="Output format preference",
            )

        class CliOutput(FlextModels.Value):
            """CLI output configuration model extending Value via inheritance."""

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
            )

            format: c.Cli.OutputFormats = Field(
                default=c.Cli.OutputFormats.TABLE,
                description="Output format",
            )

            headers: Sequence[str] = Field(
                default_factory=list,
                description="Table headers",
            )

            show_headers: bool = Field(
                default=True,
                description="Whether to show headers",
            )

            color: bool = Field(
                default=True,
                description="Whether to use colors",
            )

        class CommandResult(FlextModels.Value):
            """Result of command execution extending Value via inheritance.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            command: str = Field(
                ...,
                description="Executed command",
            )

            exit_code: int = Field(
                default=0,
                ge=0,
                description="Exit code",
            )

            stdout: str = Field(
                default="",
                description="Standard output",
            )

            stderr: str = Field(
                default="",
                description="Standard error",
            )

            duration: float = Field(
                default=0.0,
                ge=0.0,
                description="Execution duration in seconds",
            )

            @computed_field
            def success(self) -> bool:
                """Check if command succeeded.

                Computed field included in serialization.
                """
                return self.exit_code == 0

            @computed_field
            def has_output(self) -> bool:
                """Check if command produced output.

                Computed field included in serialization.
                """
                return bool(self.stdout or self.stderr)

        class ServiceExecutionResult(FlextModels.Value):
            """Result of service execution for status reporting extending Value via inheritance."""

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
            )

            service_executed: bool = Field(
                default=False,
                description="Whether service was executed",
            )

            commands_count: int = Field(
                default=0,
                ge=0,
                description="Number of registered commands",
            )

            session_active: bool = Field(
                default=False,
                description="Whether session is active",
            )

            execution_timestamp: str = Field(
                default="",
                description="ISO timestamp of execution",
            )

            service_ready: bool = Field(
                default=False,
                description="Whether service is ready",
            )

        class CliStatus(FlextModels.Value):
            """CLI application status."""

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
            )

            app_name: str = Field(
                default="",
                description="Application name",
            )

            version: str = Field(
                default="",
                description="Application version",
            )

            is_initialized: bool = Field(
                default=False,
                description="Whether CLI is initialized",
            )

            commands_count: int = Field(
                default=0,
                ge=0,
                description="Number of registered commands",
            )

            plugins_count: int = Field(
                default=0,
                ge=0,
                description="Number of loaded plugins",
            )

        class ConfigSnapshot(FlextModels.Value):
            """Snapshot of current CLI configuration information."""

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
            )

            config_dir: str = Field(
                default="",
                description="Configuration directory path",
            )

            config_exists: bool = Field(
                default=False,
                description="Whether config directory exists",
            )

            config_readable: bool = Field(
                default=False,
                description="Whether config directory is readable",
            )

            config_writable: bool = Field(
                default=False,
                description="Whether config directory is writable",
            )

            timestamp: str = Field(
                default="",
                description="Timestamp of snapshot",
            )

        class ServiceStatus(FlextModels.Value):
            """Generic service status response."""

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
            )

            status: str = Field(
                default="",
                description="Status message",
            )

            service: str = Field(
                default="",
                description="Service name",
            )

            timestamp: str = Field(
                default="",
                description="Status timestamp",
            )

            version: str = Field(
                default="",
                description="Service version",
            )

        class CliConfig(FlextModels.Entity):
            """CLI configuration model extending Entity via inheritance."""

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
                use_enum_values=True,
                validate_default=True,
            )

            server_type: c.Cli.ServerType = Field(
                default=c.Cli.ServerType.RFC,
                description="Server type",
            )

            output_format: c.Cli.OutputFormats = Field(
                default=c.Cli.OutputFormats.TABLE,
                description="Default output format",
            )

            verbosity: c.Cli.LogVerbosity = Field(
                default=c.Cli.LogVerbosity.COMPACT,
                description="Log verbosity level",
            )

            timeout: int = Field(
                default=30,
                ge=1,
                le=300,
                description="Default timeout in seconds",
            )

            color: bool = Field(
                default=True,
                description="Enable colored output",
            )

            confirm_actions: bool = Field(
                default=True,
                description="Require confirmation for destructive actions",
            )

            # =========================================================================
            # ADDITIONAL MODELS - Required by flext-cli modules
            # =========================================================================

        class WorkflowResult(FlextModels.Value):
            """Workflow execution result with step-by-step tracking.

            Tracks overall workflow success and individual step results.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            step_results: Sequence[dict[str, t.JsonValue]] = Field(
                default_factory=list,
                description="Results for each workflow step",
            )
            total_steps: int = Field(default=0, description="Total number of steps")
            successful_steps: int = Field(
                default=0,
                description="Number of successful steps",
            )
            failed_steps: int = Field(default=0, description="Number of failed steps")
            overall_success: bool = Field(
                default=True,
                description="Whether workflow succeeded overall",
            )
            total_duration_seconds: float = Field(
                default=0.0,
                description="Total workflow duration",
            )

        class CliParamsConfig(FlextModels.Value):
            """CLI parameters configuration for command-line parsing.

            Maps directly to CLI flags: --verbose, --quiet, --debug, --trace, etc.
            All fields are optional (None) to allow partial updates.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            verbose: bool | None = Field(
                default=None,
                description="Enable verbose output",
            )
            quiet: bool | None = Field(
                default=None,
                description="Suppress non-essential output",
            )
            debug: bool | None = Field(default=None, description="Enable debug mode")
            trace: bool | None = Field(
                default=None,
                description="Enable trace logging (requires debug)",
            )
            log_level: str | None = Field(
                default=None,
                description="Log level (DEBUG, INFO, WARNING, ERROR)",
            )
            log_format: str | None = Field(
                default=None,
                description="Log format (compact, detailed, full)",
            )
            output_format: str | None = Field(
                default=None,
                description="Output format (table, json, yaml, csv)",
            )
            no_color: bool | None = Field(
                default=None,
                description="Disable colored output",
            )

            @property
            def params(self) -> Mapping[str, t.JsonValue]:
                """Parameters mapping - required by CliParamsConfigProtocol."""
                return {
                    "verbose": self.verbose,
                    "quiet": self.quiet,
                    "debug": self.debug,
                    "trace": self.trace,
                    "log_level": self.log_level,
                    "log_format": self.log_format,
                    "output_format": self.output_format,
                    "no_color": self.no_color,
                }

        class OptionConfig(FlextModels.Value):
            """Configuration for CLI option decorators.

            Used with create_option_decorator to reduce argument counFlextCliTypes.
            """

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
                arbitrary_types_allowed=True,
            )

            default: t.JsonValue | None = Field(
                default=None,
                description="Default value",
            )
            type_hint: object = Field(
                default=None,
                description="Parameter type (Click type or Python type)",
            )
            required: bool = Field(
                default=False,
                description="Whether option is required",
            )
            help_text: str | None = Field(
                default=None,
                description="Help text for option",
            )
            is_flag: bool = Field(
                default=False,
                description="Whether this is a boolean flag",
            )
            flag_value: t.JsonValue | None = Field(
                default=None,
                description="Value when flag is set",
            )
            multiple: bool = Field(default=False, description="Allow multiple values")
            count: bool = Field(default=False, description="Count occurrences")
            show_default: bool = Field(
                default=False,
                description="Show default in help",
            )

        class ConfirmConfig(FlextModels.Value):
            """Configuration for confirm prompts.

            Used with confirm() method to reduce argument counFlextCliTypes.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            default: bool = Field(default=False, description="Default value")
            abort: bool = Field(default=False, description="Abort if not confirmed")
            prompt_suffix: str = Field(
                default=c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX,
                description="Suffix after prompt",
            )
            show_default: bool = Field(
                default=True,
                description="Show default in prompt",
            )
            err: bool = Field(default=False, description="Write to stderr")

        class PromptConfig(FlextModels.Value):
            """Configuration for input prompts.

            Used with prompt() method to reduce argument counFlextCliTypes.
            """

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
                arbitrary_types_allowed=True,
            )

            default: t.JsonValue | None = Field(
                default=None,
                description="Default value",
            )
            type_hint: object = Field(
                default=None,
                description="Value type",
            )
            value_proc: object = Field(
                default=None,
                description="Value processor function",
            )
            prompt_suffix: str = Field(
                default=c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX,
                description="Suffix after prompt",
            )
            hide_input: bool = Field(default=False, description="Hide user input")
            confirmation_prompt: bool = Field(
                default=False,
                description="Ask for confirmation",
            )
            show_default: bool = Field(
                default=True,
                description="Show default in prompt",
            )
            err: bool = Field(default=False, description="Write to stderr")
            show_choices: bool = Field(
                default=True,
                description="Show available choices",
            )

        class PathInfo(FlextModels.Value):
            """Path information for debug outpuFlextCliTypes.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            index: int = Field(default=0, description="Path index in sys.path")
            path: str = Field(...)
            exists: bool = Field(default=False)
            is_file: bool = Field(default=False)
            is_dir: bool = Field(default=False)

        class EnvironmentInfo(FlextModels.Value):
            """Environment information for debug outpuFlextCliTypes.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            python_version: str = Field(default="")
            os_name: str = Field(default="")
            os_version: str = Field(default="")
            variables: dict[str, str] = Field(default_factory=dict)

        class SystemInfo(FlextModels.Value):
            """System information for debug outpuFlextCliTypes.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            python_version: str = Field(default="")
            platform: str = Field(default="")
            architecture: list[str] = Field(default_factory=list)
            processor: str = Field(default="")
            hostname: str = Field(default="")
            memory_total: int = Field(default=0)
            cpu_count: int = Field(default=0)

        class ContextExecutionResult(FlextModels.Value):
            """Context execution result.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            success: bool = Field(default=True)
            context_id: str = Field(default="")
            metadata: dict[str, t.JsonValue] = Field(
                default_factory=dict,
            )
            context_executed: bool = Field(
                default=False,
                description="Whether context was executed",
            )
            command: str = Field(default="", description="Command executed in context")
            arguments_count: int = Field(default=0, description="Number of arguments")
            timestamp: str = Field(default="", description="Execution timestamp")

        class DebugInfo(FlextModels.Value):
            """Debug information model with sensitive data masking.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            service: str = Field(..., description="Service name")
            level: str = Field(..., description="Debug level")
            message: str = Field(..., description="Debug message")
            system_info: dict[str, t.JsonValue] = Field(
                default_factory=dict,
                description="System information",
            )
            config_info: dict[str, t.JsonValue] = Field(
                default_factory=dict,
                description="Configuration information",
            )

            @field_validator("level", mode="before")
            @classmethod
            def normalize_level(cls, value: str) -> str:
                """Normalize level to uppercase."""
                return str(value).upper()

            @property
            def debug_summary(self) -> FlextCliModels.Cli.CliDebugData:
                """Return debug summary as CliDebugData model."""
                return FlextCliModels.Cli.CliDebugData(
                    service=self.service,
                    level=self.level,
                    message=self.message,
                )

            def dump_masked(self) -> Mapping[str, t.JsonValue]:
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
                sensitive_keys = ["password", "token", "secret", "key", "credential"]
                data: dict[str, t.JsonValue] = {
                    "service": self.service,
                    "level": self.level,
                    "message": self.message,
                }

                system_dict: dict[str, t.JsonValue] = {}
                system_adapter: TypeAdapter[dict[str, t.JsonValue]] = TypeAdapter(
                    dict[str, t.JsonValue]
                )
                try:
                    system_dict = system_adapter.validate_python(self.system_info)
                except ValidationError as e:
                    _logger.debug("system_info not valid as dict, using empty: %s", e)

                # Apply masking to system_dict
                masked_system_dict: dict[str, t.JsonValue] = {
                    k: (
                        "***MASKED***"
                        if any(sensitive in k.lower() for sensitive in sensitive_keys)
                        else v
                    )
                    for k, v in system_dict.items()
                }
                data["system_info"] = masked_system_dict

                config_dict: dict[str, t.JsonValue] = {}
                config_adapter: TypeAdapter[dict[str, t.JsonValue]] = TypeAdapter(
                    dict[str, t.JsonValue]
                )
                try:
                    config_dict = config_adapter.validate_python(self.config_info)
                except ValidationError as e:
                    _logger.debug("config_info not valid as dict, using empty: %s", e)

                # Apply masking to config_dict
                masked_config_dict: dict[str, t.JsonValue] = {
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
                registry: Mapping[str, Mapping[str, t.JsonValue]],
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
                field_meta_getter = getattr(field_meta, "get", None)
                if not callable(field_meta_getter):
                    msg = "Option registry metadata must support key lookup"
                    raise TypeError(msg)
                # Extract option metadata from registry using direct dict access
                help_text = str(field_meta_getter("help", ""))
                short_flag = str(field_meta_getter("short", ""))
                default_value = field_meta_getter("default")
                # Note: is_flag is deprecated in Typer - boolean defaults auto-enable flag behavior

                # Use field_name_override if available, otherwise use field_name
                # Registry uses KEY_FIELD_NAME_OVERRIDE to map CLI param name to field name
                field_name_override = field_meta_getter(
                    c.Cli.CliParamsRegistry.KEY_FIELD_NAME_OVERRIDE,
                )
                cli_param_name: str = (
                    str(field_name_override)
                    if field_name_override is not None
                    else self.field_name
                )

                # Build option arguments
                option_args: list[str] = [f"--{cli_param_name.replace('_', '-')}"]
                if short_flag:
                    option_args.append(f"-{short_flag}")

                # typer.Option returns OptionInfo for type safety
                # Do NOT pass is_flag or flag_value - deprecated in Typer
                option: OptionInfo = typer.Option(
                    default_value,
                    *option_args,
                    help=help_text,
                )
                return option

        class PasswordAuth(FlextModels.Value):
            """Password authentication data.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            username: str = Field(..., min_length=3)
            password: str = Field(..., min_length=8)
            realm: str = Field(default="")

        class CmdConfig(FlextModels.Value):
            """Command configuration.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            name: str = Field(...)
            description: str = Field(default="")
            hidden: bool = Field(default=False)
            deprecated: bool = Field(default=False)

        class TokenData(FlextModels.Value):
            """Authentication token data.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            token: str = Field(...)
            expires_at: str = Field(default="")
            token_type: str = Field(default="Bearer")

        class FormatInputData(FlextModels.Value):
            """Single contract for format input: BaseModel or JsonValue. Normalizes to JsonValue."""

            data: BaseModel | t.JsonValue = Field(
                ...,
                description="Data to format (model or raw JSON)",
            )

            @computed_field
            @property
            def normalized(self) -> t.JsonValue:
                """JSON-compatible value for formatting."""
                if isinstance(self.data, BaseModel):
                    return self.data.model_dump()
                return self.data

        class SessionStatistics(FlextModels.Value):
            """Statistics for CLI session tracking.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            commands_executed: int = Field(
                default=0,
                description="Number of commands executed",
            )
            errors_count: int = Field(
                default=0,
                description="Number of errors encountered",
            )
            session_duration_seconds: float = Field(
                default=0.0,
                description="Session duration in seconds",
            )

        class PromptStatistics(FlextModels.Value):
            """Statistics for prompt service usage tracking.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            prompts_executed: int = Field(
                default=0,
                description="Total prompts executed",
            )
            history_size: int = Field(default=0, description="Current history size")
            prompts_answered: int = Field(
                default=0,
                description="Prompts that received answers",
            )
            prompts_cancelled: int = Field(
                default=0,
                description="Prompts that were cancelled",
            )
            interactive_mode: bool = Field(
                default=False,
                description="Interactive mode flag",
            )
            default_timeout: int = Field(
                default=30,
                description="Default timeout in seconds",
            )
            timestamp: str = Field(
                default="",
                description="Timestamp of statistics collection",
            )

        class CommandStatistics(FlextModels.Value):
            """Command statistics.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            total_commands: int = Field(default=0)
            successful_commands: int = Field(default=0)
            failed_commands: int = Field(default=0)

        class CommandExecutionContextResult(FlextModels.Value):
            """Command execution context result.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            command_name: str = Field(...)
            exit_code: int = Field(default=0)
            output: str = Field(default="")
            context: dict[str, t.JsonValue] = Field(
                default_factory=dict,
            )

        class WorkflowStepResult(FlextModels.Value):
            """Workflow step result.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            step_name: str = Field(...)
            success: bool = Field(default=True)
            message: str = Field(default="")
            duration: float = Field(default=0.0)

        class WorkflowProgress(FlextModels.Value):
            """Workflow progress information.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            current_step: int = Field(default=0)
            total_steps: int = Field(default=0)
            current_step_name: str = Field(default="")
            percentage: float = Field(default=0.0)

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
            7. Dynamic function creation uses exec() for runtime code generation
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
            - Function creation MUST use exec() safely (no user input in code string)
            - Type conversion MUST preserve type safety (no object types) - See type-system-architecture.md
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
                handler: Callable[[BaseModel], t.JsonValue],
                config: object | None = None,
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
            def _resolve_type_alias(field_type: type) -> tuple[type, object]:
                """Resolve type aliases to Literal and return (resolved_type, origin).

                Handles PEP 695 type aliases like `type X = Literal[...]`.
                Returns the resolved type and its origin for further processing.
                """
                origin = get_origin(field_type)
                if origin is not None:
                    return field_type, origin

                # Check if type has __value__ (type alias characteristic)
                # Use getattr for type object access - field_type is a type, not a Mapping
                type_value = getattr(field_type, "__value__", None)
                if type_value is not None:
                    # Check if __value__ is a Literal type
                    value_origin = get_origin(type_value)
                    if value_origin is Literal:
                        # Type alias to Literal - convert to str for Typer
                        return str, Literal
                    # Not Literal - continue to return field_type with origin
                # Return field_type with its origin (None if not a generic)
                # This handles both cases: type_value is None or not Literal
                return field_type, get_origin(field_type)

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
                non_none_types: list[type] = [
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
                non_none_types: list[type] = [
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

            def _process_field_metadata(
                self,
                field_name: str,
                field_info: FieldInfo | t.JsonValue,
            ) -> tuple[type, t.JsonValue, bool, bool]:
                """Process field metadata and return type info.

                Returns (field_type, default_value, is_required, has_factory).
                """
                default_value: t.JsonValue = None
                is_required = True
                has_factory = False

                default_attr = getattr(field_info, "default", None)
                if default_attr is not None:
                    default_value = default_attr
                factory_attr = getattr(field_info, "default_factory", None)
                has_factory = callable(factory_attr)
                is_required_fn = getattr(field_info, "is_required", None)
                if callable(is_required_fn):
                    is_required = bool(is_required_fn())

                # Get config default if available
                if self.config is not None:
                    config_value = getattr(self.config, field_name, None)
                    if config_value is not None:
                        default_value = config_value

                # Get and resolve field type
                # Use getattr for FieldInfo access - field_info is an object, not always a Mapping
                field_type_raw = getattr(field_info, "annotation", None)
                if field_type_raw is None:
                    # No annotation - infer from default value or use str
                    field_type = (
                        type(default_value) if default_value is not None else str
                    )
                elif field_type_raw is object:
                    # object annotations are converted to str for CLI compatibility
                    field_type = str
                else:
                    # Has annotation - resolve type alias
                    field_type, origin = self._resolve_type_alias(field_type_raw)
                    if origin is not None and field_type is not str:
                        field_type, _ = self._extract_optional_inner_type(field_type)

                # Type narrowing: ensure field_type is a type
                field_type_typed: type = field_type
                return field_type_typed, default_value, is_required, has_factory

            @staticmethod
            def _format_bool_param(
                type_name: str,
                inner_type: type,
                default_val: t.JsonValue,
            ) -> tuple[str, t.JsonValue]:
                """Format boolean parameter for Typer flag detection."""
                # Python 3.13: Direct type comparison - more elegant
                if inner_type is bool:
                    return "bool", False if default_val is None else default_val
                return type_name, default_val

            def _build_param_signature(
                self,
                name: str,
                type_info: tuple[str, type, t.JsonValue, bool, bool],
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
                processed_annotations: dict[str, type] = {
                    name: process_annotation(name, field_type)
                    for name, field_type in annotations.items()
                }
                return processed_annotations

            # Typer-compatible built-in types (class constant)
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

            def _collect_field_data(
                self,
                model_fields: Mapping[str, t.JsonValue],
            ) -> tuple[
                Mapping[str, type],
                Mapping[str, t.JsonValue],
                set[str],
            ]:
                """Collect annotations, defaults and factory fields from model fields.

                Returns:
                    Tuple of (annotations, defaults, fields_with_factory)

                """

                # models.py cannot use utilities - use direct iteration instead
                def process_field(
                    field_name: str,
                    field_info: t.JsonValue,
                ) -> tuple[type, t.JsonValue | None, bool]:
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
                processed_dict: dict[
                    str,
                    tuple[type, t.JsonValue | None, bool],
                ] = {
                    field_name: process_field(field_name, field_info)
                    for field_name, field_info in model_fields.items()
                }
                # Build annotations, defaults, and fields_with_factory from processed results
                annotations: dict[str, type] = {}
                defaults: dict[str, t.JsonValue] = {}
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

            def _build_signature_parts(
                self,
                annotations: Mapping[str, type],
                defaults: Mapping[str, t.JsonValue],
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
                signatures_dict: dict[str, tuple[str, bool]] = {
                    name: process_signature(name, field_type)
                    for name, field_type in annotations.items()
                }
                # models.py cannot use utilities - use list comprehension instead
                # Use operator.itemgetter(1) to get boolean flag, then check truthiness
                get_bool_flag = operator.itemgetter(1)
                signatures_values = list(signatures_dict.values())
                # models.py cannot use utilities - use list comprehension instead
                # Type narrowing: signatures_values is list[tuple[str, bool]]
                signatures_values_typed: list[tuple[str, bool]] = signatures_values

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

            def _execute_command_wrapper(
                self,
                sig_parts: str,
                annotations: Mapping[str, type],
            ) -> p.Cli.CliCommandWrapper:
                """Execute dynamic function creation and return command wrapper.

                Args:
                    sig_parts: Function signature parameters string
                    annotations: Type annotations dictionary

                Returns:
                    The created command wrapper function

                Raises:
                    RuntimeError: If wrapper creation fails

                """
                func_body = f"""
    kwargs = {{{", ".join(f'"{n}": {n}' for n in annotations)}}}
    model_instance = builder_model_class(**kwargs)
    if builder_config is not None:
        for fn, v in kwargs.items():
            try:
                object.__setattr__(builder_config, fn, v)
            except (AttributeError, TypeError) as e:
                _logger.debug(
                    "Could not set builder_config.%s: %s", fn, e
                )
    if callable(builder_handler):
        return builder_handler(model_instance)
    raise RuntimeError("builder_handler is not callable")
"""
                func_globals = {
                    "builder_model_class": self.model_class,
                    "builder_config": self.config,
                    "builder_handler": self.handler,
                    "__builtins__": __builtins__,
                }
                func_code = f"def command_wrapper({sig_parts}):{func_body}"
                exec(func_code, func_globals)  # nosec B102
                command_wrapper = func_globals.get("command_wrapper")
                if command_wrapper is None:
                    msg = "Failed to create command wrapper"
                    raise RuntimeError(msg)

                def _is_callable_object(
                    obj: object,
                ) -> TypeGuard[Callable[..., object]]:
                    return callable(obj)

                if not _is_callable_object(command_wrapper):
                    msg = "exec() failed to create valid function"
                    raise TypeError(msg)

                # Type narrowing: _create_real_annotations returns dict[str, type]
                real_annotations = self._create_real_annotations(annotations)
                command_wrapper.__annotations__ = dict(real_annotations)

                # TypeGuard narrows command_wrapper to Callable[..., object] for dynamic exec result
                def typed_wrapper(
                    *args: t.JsonValue,
                    **kwargs: t.JsonValue,
                ) -> t.JsonValue:
                    args_obj: tuple[object, ...] = args
                    kwargs_obj: dict[str, object] = dict(kwargs)
                    raw_result: object = command_wrapper(*args_obj, **kwargs_obj)
                    normalized = (
                        FlextCliModels.Cli.CliModelConverter.convert_field_value(
                            raw_result,
                        )
                    )
                    if normalized.is_success:
                        return normalized.value
                    return str(raw_result)

                typed_wrapper.__annotations__ = dict(real_annotations)
                return typed_wrapper

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
                model_fields = getattr(self.model_class, "model_fields", {})
                annotations, defaults, fields_with_factory = self._collect_field_data(
                    model_fields,
                )
                sig_parts = self._build_signature_parts(
                    annotations,
                    defaults,
                    fields_with_factory,
                )
                return self._execute_command_wrapper(sig_parts, annotations)

        class CliParameterSpec:
            """CLI parameter specification for model-to-CLI conversion."""

            def __init__(
                self,
                field_name: str,
                param_type: type,
                click_type: str,
                default: t.JsonValue | None = None,
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
                cli_args: Mapping[str, t.JsonValue],
            ) -> r[BaseModel]:
                """Convert CLI arguments dict to Pydantic model instance.

                Accepts type[BaseModel] directly to work around pyright limitations
                with PEP 695 generics and local classes in tests. All BaseModel
                subclasses are compatible with type[BaseModel].
                """
                try:
                    # Use direct model_validate instead of from_dict to avoid type variable issues
                    # cli_args is already t.JsonValue compatible
                    # Type narrowing: model_cls is BaseModel subclass (checked by caller)
                    # Convert Mapping to dict for model_validate
                    cli_args_dict: dict[str, t.JsonValue] = dict(
                        cli_args,
                    )
                    # Type narrowing: model_cls is BaseModel subclass, model_validate exists
                    # Use getattr to access model_validate to satisfy type checker
                    # BaseModel.model_validate exists but mypy needs explicit access
                    model_validate_method = model_cls.model_validate
                    model_instance = model_validate_method(cli_args_dict)
                    return FlextResult.ok(model_instance)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return FlextResult.fail(f"Failed to create model instance: {e}")

            @staticmethod
            def model_to_cli_params(
                model_cls: type[BaseModel],
            ) -> FlextResult[list[p.Cli.CliParameterSpecProtocol]]:
                """Convert Pydantic model to list of CLI parameter specifications."""
                try:

                    def convert_field(
                        field_name: str,
                        field_info: FieldInfo | t.JsonValue,
                    ) -> p.Cli.CliParameterSpecProtocol:
                        """Convert single field to CliParameterSpec."""
                        field_type = getattr(field_info, "annotation", str)
                        # Extract non-None type from Optional/Union
                        origin = get_origin(field_type)
                        if origin is not None:
                            args = get_args(field_type)
                            # models.py cannot use utilities - use list comprehension instead
                            non_none_types_result = [
                                arg for arg in list(args) if arg is not type(None)
                            ]
                            non_none_types: list[type] = non_none_types_result
                            if non_none_types:
                                field_type = non_none_types[0]
                        default = getattr(field_info, "default", None)
                        help_text = str(getattr(field_info, "description", ""))
                        click_type_str = FlextCliModels.Cli.CliModelConverter.python_type_to_click_type(
                            field_type,
                        )
                        return FlextCliModels.Cli.CliParameterSpec(
                            field_name=field_name,
                            param_type=field_type,
                            click_type=click_type_str,
                            default=default,
                            help_text=help_text,
                        )

                    # Process model fields using dict comprehension for type safety
                    # models.py cannot use utilities - use direct iteration instead
                    try:
                        params_dict: dict[
                            str,
                            p.Cli.CliParameterSpecProtocol,
                        ] = {
                            field_name: convert_field(field_name, field_info)
                            for field_name, field_info in model_cls.model_fields.items()
                        }
                        params_list = list(params_dict.values())
                        return FlextResult.ok(params_list)
                    except (
                        ValueError,
                        TypeError,
                        KeyError,
                        ConsoleError,
                        StyleError,
                        LiveError,
                    ) as e:
                        return FlextResult.fail(f"Conversion failed: {e}")
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return FlextResult.fail(f"Conversion failed: {e}")

            @staticmethod
            def model_to_click_options(
                model_cls: type[BaseModel],
            ) -> FlextResult[list[t.JsonValue]]:
                """Convert Pydantic model to list of Click options."""
                params_result = (
                    FlextCliModels.Cli.CliModelConverter.model_to_cli_params(
                        model_cls,
                    )
                )
                if params_result.is_failure:
                    return FlextResult.fail(params_result.error or "Conversion failed")
                # After is_failure check, params_result.value is guaranteed to be the value
                params: list[p.Cli.CliParameterSpecProtocol] = params_result.value
                # Create Click option-like objects with option_name and param_decls
                # Use simple object with attributes for compatibility with tests
                # Type cast: dynamically created objects are compatible with t.JsonValue
                options: list[t.JsonValue] = []
                for param in params:
                    # Type narrowing: param is CliParameterSpecProtocol
                    # Create a simple object with option_name and param_decls attributes
                    option_name = f"--{param.field_name.replace('_', '-')}"
                    # Type narrowing: param_decls list is compatible with t.JsonValue (list is included)
                    param_decls_list: t.JsonValue = [option_name]
                    # Type narrowing: param_type (type) - store as string for dict compatibility
                    # type is not in t.JsonValue, so we use string representation
                    param_type_name: str = getattr(param.param_type, "__name__", "str")
                    option_obj_dict: dict[str, t.JsonValue] = {
                        "option_name": option_name,
                        "param_decls": param_decls_list,
                        "field_name": param.field_name,
                        "param_type": param_type_name,
                        "default": param.default,
                        "help": param.help,  # CliParameterSpec stores as .help, not .help_text
                    }
                    # Append dict directly - it's already GeneralValueType compatible
                    options.append(option_obj_dict)
                return FlextResult.ok(options)

            @staticmethod
            def field_to_cli_param(
                field_name: str,
                field_info: FieldInfo | t.JsonValue,
            ) -> FlextResult[p.Cli.CliParameterSpecProtocol]:
                """Convert Pydantic field to CLI parameter specification."""
                try:
                    annotation = getattr(field_info, "annotation", None)
                    default = getattr(field_info, "default", None)
                    help_text = str(getattr(field_info, "description", ""))
                    if annotation is None:
                        return FlextResult.fail(
                            f"Field {field_name} has no type annotation"
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
                    return FlextResult.ok(spec)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return FlextResult.fail(f"Field conversion failed: {e}")

            @staticmethod
            def handle_union_type(pydantic_type: object) -> type:
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
            def handle_generic_type(pydantic_type: object) -> type | None:
                """Handle generic types like list of str, dict of str to str. Returns None if not handled."""
                origin = get_origin(pydantic_type)
                if origin is None:
                    return None
                # For generic types like list[str], dict[str, str], return the origin
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
            def pydantic_type_to_python_type(
                pydantic_type: type | object,
            ) -> type:
                """Convert Pydantic type annotation to Python type."""
                # Handle Optional/Union types - Python 3.10+ union types
                if get_origin(pydantic_type) is types.UnionType:
                    return FlextCliModels.Cli.CliModelConverter.handle_union_type(
                        pydantic_type,
                    )
                # Handle generic types like list[str], dict[str, str]
                generic_result = (
                    FlextCliModels.Cli.CliModelConverter.handle_generic_type(
                        pydantic_type,
                    )
                )
                if generic_result is not None:
                    return generic_result
                # Check if it's a known simple type
                if isinstance(
                    pydantic_type, type
                ) and FlextCliModels.Cli.CliModelConverter.is_simple_type(
                    pydantic_type,
                ):
                    return pydantic_type
                # Default to str for complex types
                return str

            @staticmethod
            def python_type_to_click_type(python_type: type) -> str:
                """Convert Python type to Click type string."""
                type_name = getattr(python_type, "__name__", str(python_type))
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
            def extract_base_props(
                field_name: str,
                field_info: FieldInfo | t.JsonValue,
            ) -> dict[str, t.JsonValue]:
                """Extract base properties from field info."""
                annotation = getattr(field_info, "annotation", None)
                return {
                    "field_name": field_name,
                    "annotation": str(annotation) if annotation is not None else "str",
                    "default": getattr(field_info, "default", None),
                    "description": str(getattr(field_info, "description", "")),
                }

            @staticmethod
            def merge_types_into_props(
                props: MutableMapping[str, t.JsonValue],
                types: Mapping[str, type | str],
            ) -> None:
                """Merge types mapping into properties dict."""
                transformed: dict[str, t.JsonValue] = {
                    k: str(v) for k, v in types.items()
                }
                props.update(transformed)

            @staticmethod
            def to_json_value(value: object) -> t.JsonValue:
                """Convert arbitrary value into JsonValue."""
                converted = FlextCliModels.Cli.CliModelConverter.convert_field_value(
                    value
                )
                if converted.is_success:
                    return converted.value
                return str(value)

            @staticmethod
            def merge_field_info_dict(
                props: MutableMapping[str, t.JsonValue],
                field_info: FieldInfo | t.JsonValue,
            ) -> None:
                """Merge field_info dict attributes into props."""
                if isinstance(field_info, Mapping):
                    filtered: dict[str, t.JsonValue] = {
                        str(k): FlextCliModels.Cli.CliModelConverter.to_json_value(v)
                        for k, v in field_info.items()
                        if str(k) != "__dict__"
                    }
                    props.update(filtered)
                    return
                metadata_dict = getattr(field_info, "__dict__", None)
                if metadata_dict is not None and isinstance(metadata_dict, Mapping):
                    dict_metadata: dict[str, t.JsonValue] = {
                        str(k): FlextCliModels.Cli.CliModelConverter.to_json_value(v)
                        for k, v in metadata_dict.items()
                    }
                    props.update(dict_metadata)

            @staticmethod
            def process_metadata_list(
                metadata_attr: Sequence[object],
            ) -> Mapping[str, t.JsonValue]:
                """Process metadata list into dict."""
                result: dict[str, t.JsonValue] = {}
                for item in metadata_attr:
                    if _is_mapping_like(item):
                        dict_item = {
                            str(k): FlextCliModels.Cli.CliModelConverter.to_json_value(
                                v
                            )
                            for k, v in item.items()
                        }
                        result.update(dict_item)
                    elif hasattr(item, "__dict__"):
                        item_dict = getattr(item, "__dict__")
                        if _is_mapping_like(item_dict):
                            dict_item = {
                                str(
                                    k
                                ): FlextCliModels.Cli.CliModelConverter.to_json_value(v)
                                for k, v in item_dict.items()
                            }
                            result.update(dict_item)
                return result

            @staticmethod
            def merge_metadata_attr(
                props: MutableMapping[str, t.JsonValue],
                field_info: FieldInfo | t.JsonValue,
            ) -> None:
                """Merge metadata attribute into props."""
                metadata_attr = getattr(field_info, "metadata", None)
                if metadata_attr is None:
                    return
                if isinstance(metadata_attr, Mapping):
                    props["metadata"] = {
                        str(k): FlextCliModels.Cli.CliModelConverter.to_json_value(v)
                        for k, v in metadata_attr.items()
                    }
                    return
                if isinstance(metadata_attr, (list, tuple, range)):
                    metadata_values = list(metadata_attr)
                    props["metadata"] = (
                        FlextCliModels.Cli.CliModelConverter.process_metadata_list(
                            metadata_values,
                        )
                    )

            @staticmethod
            def merge_json_schema_extra(
                props: MutableMapping[str, t.JsonValue],
                field_info: FieldInfo | t.JsonValue,
            ) -> None:
                """Merge json_schema_extra into props metadata."""
                json_schema_extra = getattr(field_info, "json_schema_extra", None)
                if json_schema_extra is None:
                    return
                # Use dict.get() for safe metadata access
                metadata_raw = props.get("metadata", {})
                dict_adapter: TypeAdapter[dict[str, t.JsonValue]] = TypeAdapter(
                    dict[str, t.JsonValue]
                )

                try:
                    metadata_dict = dict_adapter.validate_python(
                        metadata_raw, strict=True
                    )
                except ValidationError as exc:
                    msg = "metadata must be Mapping"
                    raise TypeError(msg) from exc

                try:
                    schema_dict = dict_adapter.validate_python(
                        json_schema_extra,
                        strict=True,
                    )
                except ValidationError as exc:
                    msg = "json_schema_extra must be Mapping"
                    raise TypeError(msg) from exc

                dict_metadata: dict[str, t.JsonValue] = {
                    str(k): FlextCliModels.Cli.CliModelConverter.to_json_value(v)
                    for k, v in metadata_dict.items()
                }
                dict_schema: dict[str, t.JsonValue] = {
                    str(k): FlextCliModels.Cli.CliModelConverter.to_json_value(v)
                    for k, v in schema_dict.items()
                }
                dict_metadata.update(dict_schema)
                props["metadata"] = dict_metadata

            @staticmethod
            def extract_field_properties(
                field_name: str,
                field_info: FieldInfo | t.JsonValue,
                types: Mapping[str, type | str] | None = None,
            ) -> FlextResult[Mapping[str, t.JsonValue]]:
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
                    return FlextResult.ok(props)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return FlextResult[Mapping[str, t.JsonValue]].fail(
                        f"Extraction failed: {e}",
                    )

            # Field validation rules: (field_key, expected_type, type_check_func)
            FIELD_VALIDATION_RULES: ClassVar[
                list[tuple[str, str, Callable[[object], bool]]]
            ] = [
                ("python_type", "type", lambda v: isinstance(v, type)),
                (
                    "click_type",
                    "str",
                    lambda v: isinstance(v, str),
                ),
                ("is_required", "bool", lambda v: v in {True, False}),
                (
                    "description",
                    "str",
                    lambda v: isinstance(v, str),
                ),
                (
                    "validators",
                    "list/tuple",
                    lambda v: (
                        isinstance(v, list | tuple)
                        and not isinstance(v, Mapping | bytes)
                    ),
                ),
                (
                    "metadata",
                    "dict",
                    lambda v: isinstance(v, Mapping),
                ),
            ]

            JSON_VALUE_ADAPTER: ClassVar[TypeAdapter[t.JsonValue]] = TypeAdapter(
                t.JsonValue,
            )

            @staticmethod
            def validate_field_schema(
                field_data: Mapping[str, object],
            ) -> FlextResult[bool]:
                """Validate field data schema against rules."""
                for (
                    field_key,
                    type_name,
                    check_func,
                ) in FlextCliModels.Cli.CliModelConverter.FIELD_VALIDATION_RULES:
                    if field_key in field_data:
                        value = field_data[field_key]
                        if not check_func(value):
                            return FlextResult.fail(
                                f"Invalid {field_key}: {value} (expected {type_name})"
                            )
                return FlextResult.ok(True)

            @staticmethod
            def convert_field_value(
                field_value: object,
            ) -> FlextResult[t.JsonValue]:
                """Convert field value to t.JsonValue.

                models.py cannot use utilities - use direct conversion instead.
                Uses t.JsonValue from lower layer for proper type safety.
                """
                if field_value is None:
                    return FlextResult.ok(None)
                try:
                    json_value = FlextCliModels.Cli.CliModelConverter.JSON_VALUE_ADAPTER.validate_python(
                        field_value,
                    )
                    return FlextResult.ok(json_value)
                except ValidationError as exc:
                    _logger.debug(
                        "convert_field_value validation fallback: %s",
                        exc,
                        exc_info=False,
                    )
                    return FlextResult.ok(str(field_value))

            @staticmethod
            def validate_dict_field_data(
                field_name: str,
                field_data: Mapping[str, object],
            ) -> FlextResult[t.JsonValue]:
                """Validate field data when field_info is a dict/Mapping."""
                schema_result = (
                    FlextCliModels.Cli.CliModelConverter.validate_field_schema(
                        field_data,
                    )
                )
                if schema_result.is_failure:
                    return FlextResult.fail(
                        schema_result.error or "Schema validation failed"
                    )
                field_value = field_data.get(field_name, None)
                return FlextCliModels.Cli.CliModelConverter.convert_field_value(
                    field_value,
                )

            @staticmethod
            def _validate_field_data(
                field_name: str,
                field_info: (
                    FieldInfo
                    | t.JsonValue
                    | Mapping[str, t.JsonValue]
                    | Mapping[
                        str,
                        type
                        | str
                        | bool
                        | list[t.JsonValue]
                        | Mapping[str, t.JsonValue],
                    ]
                ),
                data: Mapping[str, t.JsonValue] | None = None,
            ) -> FlextResult[t.JsonValue]:
                """Validate field data against field info."""
                try:
                    if isinstance(field_info, Mapping):
                        field_data: dict[str, object] = {
                            str(k): v for k, v in field_info.items()
                        }
                        return FlextCliModels.Cli.CliModelConverter.validate_dict_field_data(
                            field_name,
                            field_data,
                        )
                    if data is not None:
                        if field_name not in data:
                            return FlextResult.fail(f"Field {field_name} not found")
                        return FlextResult.ok(data[field_name])
                    return FlextResult[t.JsonValue].fail(
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
                    return FlextResult[t.JsonValue].fail(
                        f"Validation failed: {e}",
                    )

            @staticmethod
            def _process_validators(
                field_info: (
                    Sequence[Callable[..., object]] | Sequence[object] | t.JsonValue
                ),
            ) -> list[Callable[..., object]]:
                """Process validators from field info, filtering only callable validators."""
                if not isinstance(field_info, (list, tuple, range)):
                    return []
                return [
                    item
                    for item in field_info
                    if callable(item) and not isinstance(item, type)
                ]

        class CliModelDecorators:
            """Decorators for creating CLI commands from Pydantic models."""

            @staticmethod
            def normalize_output(value: object) -> t.JsonValue:
                """Normalize any value to JsonValue."""
                normalized: FlextResult[t.JsonValue] = (
                    FlextCliModels.Cli.CliModelConverter.convert_field_value(value)
                )
                if normalized.is_success:
                    return normalized.value
                return str(value)

            @staticmethod
            def cli_from_model(
                model_class: type[BaseModel],
            ) -> Callable[
                [
                    Callable[
                        [BaseModel],
                        r[t.JsonValue] | t.JsonValue,
                    ],
                ],
                p.Cli.CliCommandWrapper,
            ]:
                """Create decorator that converts function to CLI command from model."""

                def decorator(
                    func: Callable[
                        [BaseModel],
                        r[t.JsonValue] | t.JsonValue,
                    ],
                ) -> p.Cli.CliCommandWrapper:
                    def wrapper(
                        *_args: t.JsonValue,
                        **kwargs: t.JsonValue,
                    ) -> t.JsonValue:
                        try:
                            # Create model instance from kwargs
                            model_instance = model_class(**kwargs)
                            # Call original function with model
                            result = func(model_instance)
                            # Convert result to t.JsonValue if needed
                            output: t.JsonValue
                            if isinstance(result, FlextResult):
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
                        *_args: t.JsonValue,
                        **kwargs: t.JsonValue,
                    ) -> t.JsonValue:
                        try:
                            model_instances: list[BaseModel] = []
                            for model_cls in model_classes:
                                validated_model = model_cls(**kwargs)
                                model_instances.append(validated_model)
                            return func(
                                *(m_inst.model_dump() for m_inst in model_instances)
                            )
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

        class CliDebugData(FlextModels.Value):
            """CLI debug summary data.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            service: str = Field(..., description="Service name")
            level: str = Field(..., description="Debug level")
            message: str = Field(..., description="Debug message")

        class Display:
            """Rich display type aliases using Protocols.

            These type aliases reference protocol types from flext_cli.protocols.
            Located in Tier 1 (models.py) to allow protocol imports.
            """

            # Reference protocol types (FlextCliModels.Cli.Display.*)
            type RichTable = p.Cli.Display.RichTableProtocol
            type RichTree = p.Cli.Display.RichTreeProtocol
            type Console = p.Cli.Display.RichConsoleProtocol

        class Interactive:
            """Interactive display type aliases using Protocols.

            These type aliases reference protocol types from flext_cli.protocols.
            Located in Tier 1 (models.py) to allow protocol imports.
            """

            # Reference protocol types (FlextCliModels.Cli.Interactive.*)
            type Progress = p.Cli.Interactive.RichProgressProtocol

            # ═════════════════════════════════════════════════════════════════════
            # VALUE CLASS ALIASES - FORWARD COMPATIBILITY
            # ═════════════════════════════════════════════════════════════════════
            # These aliases allow FlextCliModels.SystemInfo instead of FlextCliModels.Cli.Value.SystemInfo
            # Maintains backward compatibility while supporting namespace hierarchy
            # ═════════════════════════════════════════════════════════════════════

            # Expose nested Value classes at Cli level for compatibility
            # Note: Some classes may not exist yet - commented out to avoid import errors
            # SystemInfo = Value.SystemInfo
            # EnvironmentInfo = Value.EnvironmentInfo
            # PathInfo = Value.PathInfo
            # CommandStatistics = Value.CommandStatistics
            # SessionStatistics = Value.SessionStatistics
            # ServiceExecutionResult = Value.ServiceExecutionResult
            # CommandExecutionContextResult = Value.CommandExecutionContextResult

        # End of Cli class

    # End of FlextCliModels class


m = FlextCliModels
CliExecutionMetadata = FlextCliModels.Cli.CliExecutionMetadata
CliValidationResult = FlextCliModels.Cli.CliValidationResult

# Pydantic forward reference resolution
# DomainEvent is available in current flext-core
# Ensure forward references can be resolved by making types available in module globals
# This is required because FlextModels.Entity has fields that reference DomainEvent
globals()["DomainEvent"] = FlextModels.DomainEvent

__all__ = [
    "CliExecutionMetadata",
    "CliValidationResult",
    "FlextCliModels",
    "m",
]
