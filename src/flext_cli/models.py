"""FlextCli models module - Pydantic domain models."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import (
    Annotated,
    ClassVar,
    Self,
    override,
)

from flext_core import FlextModels, r
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
)
from rich.errors import ConsoleError, LiveError, StyleError

from flext_cli import FlextCliModelsSystemContext, c, t


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

    class Cli(FlextCliModelsSystemContext):
        """CLI project namespace - PADRAO HIERARQUICO.

        Este namespace contem todos os modelos CLI especificos do flext-cli.
        Acesso via: FlextCliModels.Cli.Entity, FlextCliModels.Cli.Value, FlextCliModels.Cli.CliCommand, etc.

        PADRAO: Namespace hierarquico completo, sem duplicacao.
        """

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

        # CRÍTICO: NÃO redeclarar classes base de flext-core (Entity, Value, AggregateRoot, etc.)
        # Elas vêm automaticamente via herança: FlextCliModels(FlextModels)
        # APENAS declarar modelos CLI-ESPECÍFICOS que estendem as bases

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

            Used with create_option_decorator to reduce argument counts.
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

            Used with confirm() method to reduce argument counts.
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

            Used with prompt() method to reduce argument counts.
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


__all__ = [
    "FlextCliModels",
    "m",
]

m = FlextCliModels
