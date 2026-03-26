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

        @staticmethod
        def is_mapping_like(
            obj: t.Cli.JsonValue | Mapping[str, t.Cli.JsonValue],
        ) -> TypeIs[Mapping[str, t.Cli.JsonValue]]:
            """Narrow value to Mapping for metadata processing."""
            return isinstance(obj, Mapping)

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
            def is_running(self) -> bool:
                """Check if command is running."""
                return self.status == c.Cli.CommandStatus.RUNNING.value

            def complete_execution(
                self,
                exit_code: int,
            ) -> r[FlextCliModels.Cli.CliCommand]:
                """Complete command execution with exit code."""
                try:
                    updated = self.model_copy(
                        update={"status": "completed", "exit_code": exit_code},
                    )
                    return r[FlextCliModels.Cli.CliCommand].ok(updated)
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
                return r[Mapping[str, t.Cli.JsonValue]].ok({})

            def start_execution(self) -> r[FlextCliModels.Cli.CliCommand]:
                """Start command execution - update status to running."""
                try:
                    updated = self.model_copy(update={"status": "running"})
                    return r[FlextCliModels.Cli.CliCommand].ok(updated)
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
                        .fail(f"Failed to start execution: {e}")
                        .map(lambda _unused: self)
                    )

            def update_status(self, status: str) -> Self:
                """Update command status."""
                return self.model_copy(update={"status": status})

            def with_args(self, args: t.StrSequence) -> Self:
                """Return copy with new arguments."""
                return self.model_copy(update={"args": list(args)})

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

            def add_command(
                self,
                command: FlextCliModels.Cli.CliCommand,
            ) -> r[FlextCliModels.Cli.CliSession]:
                """Add command to session."""
                try:
                    updated_commands = list(self.commands) + [command]
                    updated_session = self.model_copy(
                        update={"commands": tuple(updated_commands)},
                    )
                    return r[FlextCliModels.Cli.CliSession].ok(updated_session)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    ConsoleError,
                    StyleError,
                    LiveError,
                ) as e:
                    return (
                        r[FlextCliModels.Cli.CliSession]
                        .fail(f"Failed to add command: {e}")
                        .map(lambda _unused: self)
                    )

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
            ] = Field(default_factory=lambda: list[Mapping[str, t.Cli.JsonValue]]())
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
                required_parameters: list[inspect.Parameter] = []
                defaulted_parameters: list[inspect.Parameter] = []
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

                setattr(typed_wrapper, "__signature__", command_signature)
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

            JSON_VALUE_ADAPTER: ClassVar[TypeAdapter[t.Cli.JsonValue]] = TypeAdapter(
                t.Cli.JsonValue,
            )

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
                    cli_args_dict: Mapping[str, t.Cli.JsonValue] = dict(
                        cli_args,
                    )
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
            def _is_mapping_value(value: t.Cli.JsonValue) -> bool:
                return isinstance(value, Mapping)

            @staticmethod
            def convert_field_value(
                field_value: t.Cli.JsonValue,
            ) -> r[t.Cli.JsonValue]:
                """Convert field value to JSON-compatible value.

                models.py cannot use utilities - use direct conversion instead.
                Uses lower-layer JSON contracts for strict type safety.
                """
                if field_value is None:
                    return r[t.Cli.JsonValue].ok("")
                try:
                    json_value = FlextCliModels.Cli.CliModelConverter.JSON_VALUE_ADAPTER.validate_python(
                        field_value,
                    )
                    return r[t.Cli.JsonValue].ok(json_value)
                except ValidationError as exc:
                    _logger.debug(
                        "convert_field_value validation fallback",
                        error=exc,
                        exc_info=False,
                    )
                    return r[t.Cli.JsonValue].ok(str(field_value))

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
