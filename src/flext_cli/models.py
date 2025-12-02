"""FlextCli models module - Pydantic models with StrEnum."""

from __future__ import annotations

import types
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Literal,
    Self,
    TypeAlias,
    Union,
    cast,
    get_args,
    get_origin,
    override,
)

import typer
from flext_core import FlextModels, FlextResult, FlextTypes
from flext_core._models.entity import FlextModelsEntity
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.fields import FieldInfo

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants

# Type alias for Pydantic v2 include/exclude parameters
# Business Rule: Must match Pydantic's recursive IncEx type structure for override compatibility
# Pydantic uses a recursive type alias internally that mypy recognizes
# Audit Implication: Type compatibility ensures proper serialization behavior
# Using TYPE_CHECKING is necessary here because Pydantic's IncEx is not directly importable
# This is an exception to the "no TYPE_CHECKING" rule - required for type compatibility
if TYPE_CHECKING:
    from pydantic.types import IncEx  # type: ignore[import-untyped]
else:
    # Runtime fallback - simplified IncEx type alias that's structurally compatible
    # This matches the structure Pydantic expects at runtime
    # Note: Full recursion not needed at runtime - Pydantic accepts this structure
    IncEx: TypeAlias = (
        set[int]
        | set[str]
        | Mapping[int, int | str | set[int] | set[str] | bool]
        | Mapping[str, int | str | set[int] | set[str] | bool]
        | None
    )


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels.

    REGRAS:
    ───────
    1. Herdar de FlextModels, NUNCA BaseModel direto
    2. ConfigDict com frozen=True, extra="forbid"
    3. StrEnum de constants, NÃO criar novos
    4. field_validator para validação complexa
    5. Self para métodos de transformação
    """

    @staticmethod
    def execute() -> FlextResult[FlextTypes.JsonDict]:
        """Execute models operation - returns empty dict for compatibility."""
        return FlextResult[FlextTypes.JsonDict].ok({})

    class CliCommand(FlextModelsEntity.Core):
        """CLI command model."""

        model_config = ConfigDict(
            frozen=True,
            extra="forbid",
            use_enum_values=True,
            validate_default=True,
            str_strip_whitespace=True,
            # Override TimestampableMixin fields to use strings instead of datetime
            # This avoids frozen instance errors during initialization
        )

        # Note: CliCommand intentionally overrides TimestampableMixin datetime fields
        # with str fields for CLI serialization compatibility.
        # This is a known architectural trade-off: we lose type safety but gain
        # simpler CLI serialization. In Pydantic 2, field overrides with different
        # types are allowed at runtime but mypy flags them as errors.
        # Solution: Use datetime fields and serialize via field_serializer when needed.
        created_at: datetime = Field(
            default_factory=lambda: datetime.now(UTC),
            description="Creation timestamp",
        )
        updated_at: datetime | None = Field(
            default=None,
            description="Last update timestamp",
        )

        def model_post_init(self, __context: object, /) -> None:
            """Override to prevent frozen instance errors from TimestampableMixin.

            Uses standard Pydantic 2 signature for model_post_init.
            """
            # Do nothing - we use string timestamps instead of datetime

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

        result: FlextTypes.GeneralValueType | None = Field(
            default=None,
            description="Command result",
        )

        kwargs: FlextTypes.JsonDict = Field(
            default_factory=dict,
            description="Command keyword arguments",
        )

        def with_status(self, status: FlextCliConstants.Domain.Status) -> Self:
            """Return copy with new status."""
            return self.model_copy(update={"status": status})

        def with_args(self, args: Sequence[str]) -> Self:
            """Return copy with new arguments."""
            return self.model_copy(update={"args": list(args)})

        @property
        def command_summary(self) -> dict[str, str]:
            """Return command summary as dict."""
            return {"command": self.command_line or self.name}

        def start_execution(self) -> FlextResult[Self]:
            """Start command execution - update status to running."""
            try:
                updated = self.model_copy(update={"status": "running"})
                return FlextResult.ok(updated)
            except Exception as e:
                return FlextResult.fail(f"Failed to start execution: {e}")

        def complete_execution(self, exit_code: int) -> FlextResult[Self]:
            """Complete command execution with exit code."""
            try:
                updated = self.model_copy(
                    update={"status": "completed", "exit_code": exit_code}
                )
                return FlextResult.ok(updated)
            except Exception as e:
                return FlextResult.fail(f"Failed to complete execution: {e}")

        def update_status(self, status: str) -> Self:
            """Update command status."""
            return self.model_copy(update={"status": status})

        @classmethod
        def validate_command_input(
            cls, data: FlextTypes.GeneralValueType
        ) -> FlextResult[Self]:
            """Validate command input data."""
            try:
                if data is None:
                    return FlextResult.fail("Input must be a dictionary")
                if not isinstance(data, (dict, cls)):
                    return FlextResult.fail("Input must be a dictionary")
                if isinstance(data, dict):
                    # Cast dict to JsonDict for type compatibility with ** unpacking
                    # Type checker cannot verify ** unpacking compatibility, but runtime is safe
                    command = cls(**cast("FlextTypes.JsonDict", data))  # type: ignore[arg-type]
                    return FlextResult.ok(command)
                if isinstance(data, cls):
                    return FlextResult.ok(data)
                return FlextResult.fail(f"Invalid input type: {type(data)}")
            except Exception as e:
                return FlextResult.fail(f"Validation failed: {e}")

    class CliSession(FlextModelsEntity.Core):
        """CLI session model for tracking command execution sessions."""

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
        def validate_status(cls, value: FlextTypes.GeneralValueType) -> str:
            """Validate session status."""
            if not isinstance(value, str):
                msg = f"Status must be a string, got {type(value)}"
                raise TypeError(msg)
            # Check if status is valid (basic validation)
            valid_statuses = [
                FlextCliConstants.SessionStatus.ACTIVE.value,
                FlextCliConstants.SessionStatus.COMPLETED.value,
                FlextCliConstants.SessionStatus.TERMINATED.value,
            ]
            if value not in valid_statuses:
                msg = (
                    f"Invalid session status: {value}. Must be one of {valid_statuses}"
                )
                raise ValueError(msg)
            return value

        # Forward reference for CliCommand
        commands: Sequence[FlextCliModels.CliCommand] = Field(
            default_factory=list,
            description="Commands in session",
        )
        start_time: str | None = Field(default=None, description="Session start time")
        end_time: str | None = Field(default=None, description="Session end time")
        last_activity: str | None = Field(
            default=None, description="Last activity timestamp"
        )
        internal_duration_seconds: float = Field(
            default=0.0,
            description="Internal duration in seconds",
        )
        commands_executed: int = Field(
            default=0, description="Number of commands executed"
        )
        # Note: CliSession uses datetime fields from TimestampableMixin.
        # Serialization to strings happens via Pydantic's field_serializer.
        created_at: datetime = Field(
            default_factory=lambda: datetime.now(UTC),
            description="Session creation timestamp",
        )
        updated_at: datetime | None = Field(
            default=None,
            description="Session last update timestamp",
        )

        @override
        def model_post_init(self, __context: object, /) -> None:
            """Override Core.model_post_init to prevent frozen instance errors.

            Core.model_post_init tries to set updated_at, but frozen models
            cannot be modified after creation. We skip this for CliSession.
            """
            # Do nothing - updated_at is set via default or explicitly

        @property
        def session_summary(self) -> FlextCliModels.CliSessionData:
            """Return session summary as CliSessionData model."""
            return FlextCliModels.CliSessionData(
                session_id=self.session_id,
                status=self.status,
                commands_count=len(self.commands),
            )

        @property
        def commands_by_status(self) -> dict[str, list[FlextCliModels.CliCommand]]:
            """Group commands by status."""
            result: dict[str, list[FlextCliModels.CliCommand]] = {}
            for command in self.commands:
                status = command.status or ""
                if status not in result:
                    result[status] = []
                result[status].append(command)
            return result

        def add_command(self, command: FlextCliModels.CliCommand) -> FlextResult[Self]:
            """Add command to session."""
            try:
                updated_commands = list(self.commands) + [command]
                updated_session = self.model_copy(update={"commands": updated_commands})
                return FlextResult.ok(updated_session)
            except Exception as e:
                return FlextResult.fail(f"Failed to add command: {e}")

    class CliSessionData(FlextModelsEntity.Value):
        """CLI session summary data."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        session_id: str = Field(..., description="Session identifier")
        status: str = Field(..., description="Session status")
        commands_count: int = Field(default=0, description="Number of commands")

    class CliContext(FlextModelsEntity.Value):
        """CLI execution context model."""

        model_config = ConfigDict(
            frozen=True,
            extra="forbid",
            use_enum_values=True,
        )

        cwd: str = Field(
            ...,
            description="Current working directory",
        )

        env: Mapping[str, str] = Field(
            default_factory=dict,
            description="Environment variables",
        )

        args: Sequence[str] = Field(
            default_factory=list,
            description="Command line arguments",
        )

        output_format: FlextCliConstants.OutputFormats = Field(
            default=FlextCliConstants.OutputFormats.TABLE,
            description="Output format preference",
        )

    class CliOutput(FlextModelsEntity.Value):
        """CLI output configuration model."""

        model_config = ConfigDict(
            frozen=True,
            extra="forbid",
        )

        format: FlextCliConstants.OutputFormats = Field(
            default=FlextCliConstants.OutputFormats.TABLE,
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

    class CommandResult(FlextModelsEntity.Value):
        """Result of command execution."""

        model_config = ConfigDict(
            frozen=True,
            extra="forbid",
        )

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

        @property
        def success(self) -> bool:
            """Check if command succeeded."""
            return self.exit_code == 0

        @property
        def has_output(self) -> bool:
            """Check if command produced output."""
            return bool(self.stdout or self.stderr)

    class ServiceExecutionResult(FlextModelsEntity.Value):
        """Result of service execution for status reporting."""

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

    class CliConfig(FlextModelsEntity.Core):
        """CLI configuration model."""

        model_config = ConfigDict(
            frozen=True,
            extra="forbid",
            use_enum_values=True,
            validate_default=True,
        )

        server_type: FlextCliConstants.ServerType = Field(
            default=FlextCliConstants.ServerType.RFC,
            description="Server type",
        )

        output_format: FlextCliConstants.OutputFormats = Field(
            default=FlextCliConstants.OutputFormats.TABLE,
            description="Default output format",
        )

        verbosity: FlextCliConstants.LogVerbosity = Field(
            default=FlextCliConstants.LogVerbosity.COMPACT,
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

    class TableConfig(FlextModelsEntity.Value):
        """Table display configuration for tabulate.

        Fields map directly to tabulate() parameters.
        """

        model_config = ConfigDict(frozen=True, extra="forbid")

        # Headers configuration
        headers: str | Sequence[str] = Field(
            default="keys",
            description=(
                "Table headers (string like 'keys', 'firstrow' "
                "or sequence of header names)"
            ),
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

    class WorkflowResult(FlextModelsEntity.Value):
        """Workflow execution result with step-by-step tracking.

        Tracks overall workflow success and individual step results.
        """

        model_config = ConfigDict(frozen=True, extra="forbid")

        step_results: Sequence[FlextTypes.JsonDict] = Field(
            default_factory=list,
            description="Results for each workflow step",
        )
        total_steps: int = Field(default=0, description="Total number of steps")
        successful_steps: int = Field(
            default=0, description="Number of successful steps"
        )
        failed_steps: int = Field(default=0, description="Number of failed steps")
        overall_success: bool = Field(
            default=True, description="Whether workflow succeeded overall"
        )
        total_duration_seconds: float = Field(
            default=0.0, description="Total workflow duration"
        )

    class CliParamsConfig(FlextModelsEntity.Value):
        """CLI parameters configuration for command-line parsing.

        Maps directly to CLI flags: --verbose, --quiet, --debug, --trace, etc.
        All fields are optional (None) to allow partial updates.
        """

        model_config = ConfigDict(frozen=True, extra="forbid")

        verbose: bool | None = Field(default=None, description="Enable verbose output")
        quiet: bool | None = Field(
            default=None, description="Suppress non-essential output"
        )
        debug: bool | None = Field(default=None, description="Enable debug mode")
        trace: bool | None = Field(
            default=None, description="Enable trace logging (requires debug)"
        )
        log_level: str | None = Field(
            default=None, description="Log level (DEBUG, INFO, WARNING, ERROR)"
        )
        log_format: str | None = Field(
            default=None, description="Log format (compact, detailed, full)"
        )
        output_format: str | None = Field(
            default=None, description="Output format (table, json, yaml, csv)"
        )
        no_color: bool | None = Field(
            default=None, description="Disable colored output"
        )

    class OptionConfig(FlextModelsEntity.Value):
        """Configuration for CLI option decorators.

        Used with create_option_decorator to reduce argument count.
        """

        model_config = ConfigDict(frozen=True, extra="forbid")

        default: FlextTypes.GeneralValueType | None = Field(
            default=None, description="Default value"
        )
        type_hint: FlextTypes.GeneralValueType | None = Field(
            default=None, description="Parameter type (Click type or Python type)"
        )
        required: bool = Field(default=False, description="Whether option is required")
        help_text: str | None = Field(default=None, description="Help text for option")
        is_flag: bool = Field(
            default=False, description="Whether this is a boolean flag"
        )
        flag_value: FlextTypes.GeneralValueType | None = Field(
            default=None, description="Value when flag is set"
        )
        multiple: bool = Field(default=False, description="Allow multiple values")
        count: bool = Field(default=False, description="Count occurrences")
        show_default: bool = Field(default=False, description="Show default in help")

    class ConfirmConfig(FlextModelsEntity.Value):
        """Configuration for confirm prompts.

        Used with confirm() method to reduce argument count.
        """

        model_config = ConfigDict(frozen=True, extra="forbid")

        default: bool = Field(default=False, description="Default value")
        abort: bool = Field(default=False, description="Abort if not confirmed")
        prompt_suffix: str = Field(
            default=FlextCliConstants.UIDefaults.DEFAULT_PROMPT_SUFFIX,
            description="Suffix after prompt",
        )
        show_default: bool = Field(default=True, description="Show default in prompt")
        err: bool = Field(default=False, description="Write to stderr")

    class PromptConfig(FlextModelsEntity.Value):
        """Configuration for input prompts.

        Used with prompt() method to reduce argument count.
        """

        model_config = ConfigDict(frozen=True, extra="forbid")

        default: FlextTypes.GeneralValueType | None = Field(
            default=None, description="Default value"
        )
        type_hint: FlextTypes.GeneralValueType | None = Field(
            default=None, description="Value type"
        )
        value_proc: Callable[[str], FlextTypes.GeneralValueType] | None = Field(
            default=None, description="Value processor function"
        )
        prompt_suffix: str = Field(
            default=FlextCliConstants.UIDefaults.DEFAULT_PROMPT_SUFFIX,
            description="Suffix after prompt",
        )
        hide_input: bool = Field(default=False, description="Hide user input")
        confirmation_prompt: bool = Field(
            default=False, description="Ask for confirmation"
        )
        show_default: bool = Field(default=True, description="Show default in prompt")
        err: bool = Field(default=False, description="Write to stderr")
        show_choices: bool = Field(default=True, description="Show available choices")

    class PathInfo(FlextModelsEntity.Value):
        """Path information for debug output."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        index: int = Field(default=0, description="Path index in sys.path")
        path: str = Field(...)
        exists: bool = Field(default=False)
        is_file: bool = Field(default=False)
        is_dir: bool = Field(default=False)

    class EnvironmentInfo(FlextModelsEntity.Value):
        """Environment information for debug output."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        python_version: str = Field(default="")
        os_name: str = Field(default="")
        os_version: str = Field(default="")
        variables: Mapping[str, str] = Field(default_factory=dict)

    class SystemInfo(FlextModelsEntity.Value):
        """System information for debug output."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        python_version: str = Field(default="")
        platform: str = Field(default="")
        architecture: list[str] = Field(default_factory=list)
        processor: str = Field(default="")
        hostname: str = Field(default="")
        memory_total: int = Field(default=0)
        cpu_count: int = Field(default=0)

    class ContextExecutionResult(FlextModelsEntity.Value):
        """Context execution result."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        success: bool = Field(default=True)
        context_id: str = Field(default="")
        metadata: FlextTypes.JsonDict = Field(default_factory=dict)
        context_executed: bool = Field(
            default=False, description="Whether context was executed"
        )
        command: str = Field(default="", description="Command executed in context")
        arguments_count: int = Field(default=0, description="Number of arguments")
        timestamp: str = Field(default="", description="Execution timestamp")

    class DebugInfo(FlextModelsEntity.Value):
        """Debug information model with sensitive data masking."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        service: str = Field(..., description="Service name")
        level: str = Field(..., description="Debug level")
        message: str = Field(..., description="Debug message")
        system_info: FlextTypes.JsonDict = Field(
            default_factory=dict, description="System information"
        )
        config_info: FlextTypes.JsonDict = Field(
            default_factory=dict, description="Configuration information"
        )

        @field_validator("level", mode="before")
        @classmethod
        def normalize_level(cls, value: FlextTypes.GeneralValueType) -> str:
            """Normalize level to uppercase."""
            if isinstance(value, str):
                return value.upper()
            return str(value).upper()

        @property
        def debug_summary(self) -> FlextCliModels.CliDebugData:
            """Return debug summary as CliDebugData model."""
            return FlextCliModels.CliDebugData(
                service=self.service,
                level=self.level,
                message=self.message,
            )

        def model_dump(  # noqa: PLR0913
            self,
            *,
            mode: str = "python",
            include: IncEx | None = None,
            exclude: IncEx | None = None,
            context: FlextTypes.GeneralValueType | None = None,
            by_alias: bool | None = None,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            exclude_computed_fields: bool = False,
            round_trip: bool = False,
            warnings: Literal["none", "warn", "error"] | bool = True,
            fallback: Callable[
                [FlextTypes.GeneralValueType], FlextTypes.GeneralValueType
            ]
            | None = None,
            serialize_as_any: bool = False,
        ) -> dict[str, FlextTypes.GeneralValueType]:
            """Dump model with sensitive data masking.

            Business Rule:
            ──────────────
            Overrides BaseModel.model_dump() to mask sensitive fields before serialization.
            Uses Pydantic's IncEx type for include/exclude parameters (recursive type).
            The IncEx type alias matches Pydantic's internal type structure for compatibility.
            At runtime, our IncEx type is structurally compatible with Pydantic's IncEx.

            Audit Implication:
            ───────────────────
            Sensitive data (passwords, tokens, secrets) are masked in serialized output.
            This prevents accidental exposure of credentials in logs or API responses.
            """
            # Include/exclude are structurally compatible with Pydantic's IncEx at runtime
            # Business Rule: Our IncEx type alias matches Pydantic's structure
            # At runtime, Pydantic accepts our type structure without issues
            # The type checker sees different types, but they're structurally compatible
            # Solution: Call super().model_dump() directly - runtime accepts our types
            # The type checker sees different types, but runtime behavior is correct
            # This is a known limitation when overriding Pydantic methods with custom types
            # We use getattr to access the method dynamically to bypass type checking
            # Business Rule: Our IncEx type is structurally compatible with Pydantic's IncEx
            # Audit Implication: Type compatibility ensures proper serialization behavior
            model_dump_method = super().model_dump
            data = model_dump_method(
                mode=mode,
                include=include,  # Structurally compatible with Pydantic's IncEx
                exclude=exclude,  # Structurally compatible with Pydantic's IncEx
                context=context,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                exclude_computed_fields=exclude_computed_fields,
                round_trip=round_trip,
                warnings=warnings,
                fallback=fallback,
                serialize_as_any=serialize_as_any,
            )
            # Mask sensitive keys in system_info and config_info
            sensitive_keys = ["password", "token", "secret", "key", "credential"]
            system_info = data.get("system_info")
            if isinstance(system_info, dict):
                masked_system_info: dict[str, FlextTypes.GeneralValueType] = {}
                for key, value in system_info.items():
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        masked_system_info[key] = "***MASKED***"
                    else:
                        masked_system_info[key] = value
                data["system_info"] = masked_system_info
            config_info = data.get("config_info")
            if isinstance(config_info, dict):
                masked_config_info: dict[str, FlextTypes.GeneralValueType] = {}
                for key, value in config_info.items():
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        masked_config_info[key] = "***MASKED***"
                    else:
                        masked_config_info[key] = value
                data["config_info"] = masked_config_info
            return data

    class OptionBuilder:
        """Builder for Typer CLI options from field metadata.

        Constructs typer.Option instances from field_name and registry configuration.
        NOT a Pydantic model - this is a utility builder class.
        """

        def __init__(
            self,
            field_name: str,
            registry: Mapping[str, FlextTypes.JsonDict],
        ) -> None:
            """Initialize builder with field name and registry.

            Args:
                field_name: Name of field in FlextCliConfig
                registry: CLI parameter registry mapping field names to option metadata

            """
            self.field_name = field_name
            self.registry = registry

        def build(self) -> FlextTypes.GeneralValueType:
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
            field_meta = self.registry.get(self.field_name, {})

            # Extract option metadata from registry
            help_text = str(field_meta.get("help", ""))
            short_flag = str(field_meta.get("short", ""))
            default_value = field_meta.get("default")
            # Note: is_flag is deprecated in Typer - boolean defaults auto-enable flag behavior

            # Build option arguments
            option_args: list[str] = [f"--{self.field_name.replace('_', '-')}"]
            if short_flag:
                option_args.append(f"-{short_flag}")

            # typer.Option returns typer.Option which is compatible with GeneralValueType
            # Do NOT pass is_flag or flag_value - deprecated in Typer
            option: FlextTypes.GeneralValueType = typer.Option(
                default_value,
                *option_args,
                help=help_text,
            )
            return option

    class PasswordAuth(FlextModelsEntity.Value):
        """Password authentication data."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        username: str = Field(...)
        password: str = Field(...)
        realm: str = Field(default="")

    class CmdConfig(FlextModelsEntity.Value):
        """Command configuration."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        name: str = Field(...)
        description: str = Field(default="")
        hidden: bool = Field(default=False)
        deprecated: bool = Field(default=False)

    class TokenData(FlextModelsEntity.Value):
        """Authentication token data."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        token: str = Field(...)
        expires_at: str = Field(default="")
        token_type: str = Field(default="Bearer")

    class SessionStatistics(FlextModelsEntity.Value):
        """Statistics for CLI session tracking."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        commands_executed: int = Field(
            default=0, description="Number of commands executed"
        )
        errors_count: int = Field(default=0, description="Number of errors encountered")
        session_duration_seconds: float = Field(
            default=0.0, description="Session duration in seconds"
        )

    class PromptStatistics(FlextModelsEntity.Value):
        """Statistics for prompt service usage tracking."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        prompts_executed: int = Field(default=0, description="Total prompts executed")
        history_size: int = Field(default=0, description="Current history size")
        prompts_answered: int = Field(
            default=0, description="Prompts that received answers"
        )
        prompts_cancelled: int = Field(
            default=0, description="Prompts that were cancelled"
        )
        interactive_mode: bool = Field(
            default=False, description="Interactive mode flag"
        )
        default_timeout: int = Field(
            default=30, description="Default timeout in seconds"
        )
        timestamp: str = Field(
            default="", description="Timestamp of statistics collection"
        )

    class CommandStatistics(FlextModelsEntity.Value):
        """Command statistics."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        total_commands: int = Field(default=0)
        successful_commands: int = Field(default=0)
        failed_commands: int = Field(default=0)

    class CommandExecutionContextResult(FlextModelsEntity.Value):
        """Command execution context result."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        command_name: str = Field(...)
        exit_code: int = Field(default=0)
        output: str = Field(default="")
        context: FlextTypes.JsonDict = Field(default_factory=dict)

    class WorkflowStepResult(FlextModelsEntity.Value):
        """Workflow step result."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        step_name: str = Field(...)
        success: bool = Field(default=True)
        message: str = Field(default="")
        duration: float = Field(default=0.0)

    class WorkflowProgress(FlextModelsEntity.Value):
        """Workflow progress information."""

        model_config = ConfigDict(frozen=True, extra="forbid")

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
        - Type conversion MUST preserve type safety (no Any types)
        - Field validation MUST use Pydantic validators (not bypassed)
        - Sensitive fields (SecretStr) MUST be handled securely in CLI args
        - Command execution MUST log all parameters (except sensitive fields)
        - Model validation failures MUST return clear error messages

        Creates Typer command functions with automatic parameter extraction from model fields.
        NOT a Pydantic model - this is a utility builder class.
        """

        def __init__(
            self,
            model_class: type[FlextModels],
            handler: Callable[[FlextModels], FlextTypes.GeneralValueType],
            config: FlextCliConfig | None = None,
        ) -> None:
            """Initialize builder with model class, handler, and optional config.

            Args:
                model_class: Pydantic BaseModel subclass defining parameters
                handler: Function receiving validated model instance
                config: Optional config singleton for defaults

            """
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
            type_value = getattr(field_type, "__value__", None)
            if type_value is None:
                return field_type, None

            # Check if __value__ is a Literal type
            value_origin = get_origin(type_value)
            if value_origin is Literal:
                # Type alias to Literal - convert to str for Typer
                return str, Literal
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
        def get_builtin_name(t: type, builtin_types: set[str]) -> str:
            """Get builtin type name or 'str' as fallback."""
            if hasattr(t, "__name__") and t.__name__ in builtin_types:
                return t.__name__
            return "str"

        @staticmethod
        def handle_optional_type(
            args: tuple[type, ...],
            builtin_types: set[str],
        ) -> tuple[str, type]:
            """Handle Optional[T] pattern (Union with None)."""
            non_none_types = [arg for arg in args if arg is not type(None)]
            inner_type = non_none_types[0] if non_none_types else str

            if get_origin(inner_type) is Literal:
                return "Optional[str]", inner_type

            inner_name = FlextCliModels.ModelCommandBuilder.get_builtin_name(
                inner_type, builtin_types
            )
            return f"Optional[{inner_name}]", inner_type

        @staticmethod
        def handle_union_type(
            args: tuple[type, ...],
            builtin_types: set[str],
        ) -> tuple[str, type]:
            """Handle Union without None."""
            non_none_types = [arg for arg in args if arg is not type(None)]
            if not non_none_types:
                return "str", str

            first_type = non_none_types[0]
            if get_origin(first_type) is Literal:
                return "str", first_type

            type_name = FlextCliModels.ModelCommandBuilder.get_builtin_name(
                first_type, builtin_types
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
            builder = FlextCliModels.ModelCommandBuilder

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
            field_info: FlextTypes.GeneralValueType,
        ) -> tuple[type, FlextTypes.GeneralValueType, bool, bool]:
            """Process field metadata and return type info.

            Returns (field_type, default_value, is_required, has_factory).
            """
            default_value = getattr(field_info, "default", None)
            default_factory = getattr(field_info, "default_factory", None)
            has_factory = default_factory is not None
            is_required = (
                field_info.is_required()  # type: ignore[union-attr]
                if hasattr(field_info, "is_required")
                else True
            )

            # Get config default if available
            if self.config is not None and hasattr(self.config, field_name):
                config_value = getattr(self.config, field_name)
                if config_value is not None:
                    default_value = config_value

            # Get and resolve field type
            field_type = getattr(field_info, "annotation", None)
            if field_type is None or field_type is object:
                field_type = type(default_value) if default_value is not None else str
            else:
                field_type, origin = self._resolve_type_alias(field_type)
                if origin is not None and field_type is not str:
                    field_type, _ = self._extract_optional_inner_type(field_type)

            return field_type, default_value, is_required, has_factory

        @staticmethod
        def _format_bool_param(
            type_name: str, inner_type: type, default_val: FlextTypes.GeneralValueType
        ) -> tuple[str, FlextTypes.GeneralValueType]:
            """Format boolean parameter for Typer flag detection."""
            if hasattr(inner_type, "__name__") and inner_type.__name__ == "bool":
                return "bool", False if default_val is None else default_val
            return type_name, default_val

        def _build_param_signature(
            self,
            name: str,
            type_info: tuple[str, type, FlextTypes.GeneralValueType, bool, bool],
        ) -> tuple[str, bool]:
            """Build parameter signature string.

            Args:
                name: Parameter name
                type_info: Tuple of (type_name, inner_type, default_val, has_factory, has_default)

            Returns (param_str, is_no_default).

            """
            type_name, inner_type, default_val, has_factory, has_default = type_info
            type_name, default_val = self._format_bool_param(
                type_name, inner_type, default_val
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
            annotations: dict[str, type],
        ) -> dict[str, type]:
            """Create real type annotations for Typer flag detection."""
            real_annotations: dict[str, type] = {}
            for name, field_type in annotations.items():
                origin = get_origin(field_type)
                is_union = (
                    origin is Union
                    or origin is type(Union)
                    or origin is types.UnionType
                )
                if is_union:
                    args = get_args(field_type)
                    non_none = [a for a in args if a is not type(None)]
                    if non_none and non_none[0] is bool:
                        real_annotations[name] = cast("type", bool | None)
                    else:
                        real_annotations[name] = field_type
                else:
                    real_annotations[name] = field_type
            return real_annotations

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
            model_fields: dict[str, FlextTypes.GeneralValueType],
        ) -> tuple[dict[str, type], dict[str, FlextTypes.GeneralValueType], set[str]]:
            """Collect annotations, defaults and factory fields from model fields.

            Returns:
                Tuple of (annotations, defaults, fields_with_factory)

            """
            annotations: dict[str, type] = {}
            defaults: dict[str, FlextTypes.GeneralValueType] = {}
            fields_with_factory: set[str] = set()

            for field_name, field_info in model_fields.items():
                field_type, default_val, is_required, has_factory = (
                    self._process_field_metadata(field_name, field_info)
                )

                if has_factory:
                    fields_with_factory.add(field_name)

                # Store annotation
                if not is_required:
                    annotations[field_name] = cast("type", field_type | None)
                else:
                    annotations[field_name] = field_type

                # Store default
                if field_name not in fields_with_factory and (
                    not is_required or default_val is not None
                ):
                    defaults[field_name] = (
                        default_val if default_val is not None else None
                    )

            return annotations, defaults, fields_with_factory

        def _build_signature_parts(
            self,
            annotations: dict[str, type],
            defaults: dict[str, FlextTypes.GeneralValueType],
            fields_with_factory: set[str],
        ) -> str:
            """Build function signature string from field data.

            Returns:
                Comma-separated parameter signature string

            """
            params_no_default: list[str] = []
            params_with_default: list[str] = []

            for name, field_type in annotations.items():
                type_name, inner_type = self._get_type_name_for_signature(
                    field_type, self._BUILTIN_TYPES
                )
                type_info = (
                    type_name,
                    inner_type,
                    defaults.get(name),
                    name in fields_with_factory,
                    name in defaults,
                )
                param_str, is_no_default = self._build_param_signature(name, type_info)
                if is_no_default:
                    params_no_default.append(param_str)
                else:
                    params_with_default.append(param_str)

            return ", ".join(params_no_default + params_with_default)

        def _execute_command_wrapper(
            self,
            sig_parts: str,
            annotations: dict[str, type],
        ) -> Callable[..., FlextTypes.GeneralValueType]:
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
            if hasattr(builder_config, fn):
                object.__setattr__(builder_config, fn, v)
    if callable(builder_handler):
        return builder_handler(model_instance)
    return None
"""
            func_globals = {
                "builder_model_class": self.model_class,
                "builder_config": self.config,
                "builder_handler": self.handler,
                "__builtins__": __builtins__,
            }
            func_code = f"def command_wrapper({sig_parts}):{func_body}"
            exec(func_code, func_globals)  # noqa: S102
            command_wrapper = func_globals.get("command_wrapper")
            if command_wrapper is None:
                msg = "Failed to create command wrapper"
                raise RuntimeError(msg)

            # Type narrowing: _create_real_annotations returns dict[str, type]
            real_annotations = self._create_real_annotations(annotations)
            command_wrapper.__annotations__ = real_annotations

            if callable(command_wrapper):
                return cast(
                    "Callable[..., FlextTypes.GeneralValueType]", command_wrapper
                )
            msg = "command_wrapper is not callable"
            raise RuntimeError(msg)

        def build(self) -> Callable[..., FlextTypes.GeneralValueType]:
            """Build Typer command from Pydantic model.

            Business Rule:
            ──────────────
            Dynamically creates a Typer command function from Pydantic model fields.
            The generated function:
            1. Accepts CLI arguments matching model field names and types
            2. Validates arguments using Pydantic model_validate()
            3. Calls handler with validated model instance
            4. Returns handler result (typically FlextResult)

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
                model_fields
            )
            sig_parts = self._build_signature_parts(
                annotations, defaults, fields_with_factory
            )
            return self._execute_command_wrapper(sig_parts, annotations)

    class CliParameterSpec:
        """CLI parameter specification for model-to-CLI conversion."""

        def __init__(
            self,
            field_name: str,
            param_type: type,
            click_type: str,
            default: FlextTypes.GeneralValueType | None = None,
            help_text: str = "",
        ) -> None:
            """Initialize CLI parameter spec."""
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
        and Click options, following FLEXT patterns with FlextResult railway pattern.
        """

        @staticmethod
        def cli_args_to_model[M: type[BaseModel]](
            model_cls: type[M],
            cli_args: Mapping[str, FlextTypes.GeneralValueType],
        ) -> FlextResult[M]:
            """Convert CLI arguments dict to Pydantic model instance."""
            try:
                # Use direct model_validate instead of from_dict to avoid type variable issues
                # cli_args is already GeneralValueType compatible
                if issubclass(model_cls, BaseModel):
                    # Convert Mapping to dict for model_validate
                    cli_args_dict: dict[str, FlextTypes.GeneralValueType] = dict(
                        cli_args
                    )
                    # Type narrowing: model_cls is BaseModel subclass, model_validate exists
                    # Type cast: BaseModel.model_validate exists, but pyrefly needs type narrowing
                    # We know model_cls is BaseModel subclass from issubclass check above
                    # Use getattr to access model_validate to satisfy type checker
                    model_validate_method = getattr(model_cls, "model_validate", None)
                    if model_validate_method is not None:
                        validated: M = model_validate_method(
                            cli_args_dict, strict=False
                        )
                    else:
                        # Fallback: should not reach here due to issubclass check above
                        class_name = getattr(model_cls, "__name__", str(model_cls))
                        return FlextResult[M].fail(
                            f"{class_name} is not a Pydantic model"
                        )
                    return FlextResult.ok(validated)
                # Type narrowing: get class name safely for error message
                class_name = getattr(model_cls, "__name__", str(model_cls))
                return FlextResult[M].fail(f"{class_name} is not a Pydantic model")
            except Exception as e:
                return FlextResult[M].fail(f"Model creation failed: {e}")

        @staticmethod
        def model_to_cli_params(
            model_cls: type,
        ) -> FlextResult[list[FlextCliModels.CliParameterSpec]]:
            """Convert Pydantic model to list of CLI parameter specifications."""
            try:
                if not hasattr(model_cls, "model_fields"):
                    # Type narrowing: get class name safely for error message
                    class_name = getattr(model_cls, "__name__", str(model_cls))
                    return FlextResult[list[FlextCliModels.CliParameterSpec]].fail(
                        f"{class_name} is not a Pydantic model"
                    )
                params: list[FlextCliModels.CliParameterSpec] = []
                for field_name, field_info in model_cls.model_fields.items():
                    field_type = getattr(field_info, "annotation", str)
                    # Extract non-None type from Optional/Union
                    origin = get_origin(field_type)
                    if origin is not None:
                        args = get_args(field_type)
                        non_none_types = [arg for arg in args if arg is not type(None)]
                        if non_none_types:
                            field_type = non_none_types[0]
                    default = getattr(field_info, "default", None)
                    help_text = str(getattr(field_info, "description", ""))
                    click_type_str = (
                        FlextCliModels.CliModelConverter.python_type_to_click_type(
                            field_type
                        )
                    )
                    params.append(
                        FlextCliModels.CliParameterSpec(
                            field_name=field_name,
                            param_type=field_type,
                            click_type=click_type_str,
                            default=default,
                            help_text=help_text,
                        )
                    )
                return FlextResult[list[FlextCliModels.CliParameterSpec]].ok(params)
            except Exception as e:
                return FlextResult[list[FlextCliModels.CliParameterSpec]].fail(
                    f"Conversion failed: {e}"
                )

        @staticmethod
        def model_to_click_options(
            model_cls: type,
        ) -> FlextResult[list[FlextTypes.GeneralValueType]]:
            """Convert Pydantic model to list of Click options."""
            params_result = FlextCliModels.CliModelConverter.model_to_cli_params(
                model_cls
            )
            if params_result.is_failure:
                return FlextResult[list[FlextTypes.GeneralValueType]].fail(
                    params_result.error or "Conversion failed"
                )
            params = params_result.unwrap()
            # Create Click option-like objects with option_name and param_decls
            # Use simple object with attributes for compatibility with tests
            # Type cast: dynamically created objects are compatible with GeneralValueType
            options: list[FlextTypes.GeneralValueType] = []
            for param in params:
                # Create a simple object with option_name and param_decls attributes
                option_name = f"--{param.field_name.replace('_', '-')}"
                # Type cast: param_decls list is compatible with GeneralValueType (list is included)
                param_decls_list: FlextTypes.GeneralValueType = cast(
                    "FlextTypes.GeneralValueType", [option_name]
                )
                # Type cast: param_type (type) needs to be cast to GeneralValueType for dict
                param_type_value: FlextTypes.GeneralValueType = cast(
                    "FlextTypes.GeneralValueType", param.param_type
                )
                option_obj_dict: dict[str, FlextTypes.GeneralValueType] = {
                    "option_name": option_name,
                    "param_decls": param_decls_list,
                    "field_name": param.field_name,
                    "param_type": param_type_value,
                    "default": param.default,
                    "help": param.help,  # CliParameterSpec stores as .help, not .help_text
                }
                # Type cast: dynamically created object is compatible with GeneralValueType
                option_obj: FlextTypes.GeneralValueType = cast(
                    "FlextTypes.GeneralValueType",
                    type("ClickOption", (), option_obj_dict)(),
                )
                options.append(option_obj)
            return FlextResult[list[FlextTypes.GeneralValueType]].ok(options)

        @staticmethod
        def field_to_cli_param(
            field_name: str,
            field_info: FieldInfo | FlextTypes.GeneralValueType,
        ) -> FlextResult[FlextCliModels.CliParameterSpec]:
            """Convert Pydantic field to CLI parameter specification."""
            try:
                # Handle both FieldInfo and GeneralValueType
                if isinstance(field_info, FieldInfo):
                    annotation = field_info.annotation
                    default = (
                        field_info.default if hasattr(field_info, "default") else None
                    )
                    help_text = str(
                        field_info.description
                        if hasattr(field_info, "description")
                        else ""
                    )
                else:
                    annotation = getattr(field_info, "annotation", None)
                    default = getattr(field_info, "default", None)
                    help_text = str(getattr(field_info, "description", ""))
                if annotation is None:
                    return FlextResult[FlextCliModels.CliParameterSpec].fail(
                        f"Field {field_name} has no type annotation"
                    )
                field_type = annotation
                # Extract non-None type from Optional/Union
                origin = get_origin(field_type)
                if origin is not None:
                    args = get_args(field_type)
                    non_none_types = [arg for arg in args if arg is not type(None)]
                    if non_none_types:
                        field_type = non_none_types[0]
                click_type_str = (
                    FlextCliModels.CliModelConverter.python_type_to_click_type(
                        field_type
                    )
                )
                return FlextResult[FlextCliModels.CliParameterSpec].ok(
                    FlextCliModels.CliParameterSpec(
                        field_name=field_name,
                        param_type=field_type,
                        click_type=click_type_str,
                        default=default,
                        help_text=help_text,
                    )
                )
            except Exception as e:
                return FlextResult[FlextCliModels.CliParameterSpec].fail(
                    f"Field conversion failed: {e}"
                )

        @staticmethod
        def pydantic_type_to_python_type(pydantic_type: type | types.UnionType) -> type:
            """Convert Pydantic type annotation to Python type."""
            # Handle Optional/Union types - Python 3.10+ union types
            if isinstance(pydantic_type, types.UnionType):
                # For int | None, extract non-None type
                args = get_args(pydantic_type)
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    result_type = non_none_types[0]
                    if isinstance(result_type, type):
                        return result_type
                return str  # Fallback
            # Handle generic types like list[str], dict[str, str]
            origin = get_origin(pydantic_type)
            if origin is not None:
                # For generic types like list[str], dict[str, str], return the origin (list, dict)
                if origin in {list, dict}:
                    return origin
                args = get_args(pydantic_type)
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    return non_none_types[0]
            # Check if it's a known simple type
            if isinstance(pydantic_type, type) and pydantic_type in {
                str,
                int,
                float,
                bool,
                list,
                dict,
            }:
                return pydantic_type
            # Default to str for complex types
            return str

        @staticmethod
        def python_type_to_click_type(python_type: type) -> str:
            """Convert Python type to Click type string."""
            type_name = getattr(python_type, "__name__", str(python_type))
            click_type_map: dict[str, str] = {
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
            field_info: FieldInfo | FlextTypes.GeneralValueType,
        ) -> dict[str, FlextTypes.GeneralValueType]:
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
            props: dict[str, FlextTypes.GeneralValueType],
            types: Mapping[str, type | str],
        ) -> None:
            """Merge types mapping into properties dict."""
            if isinstance(types, dict):
                props.update({k: str(v) for k, v in types.items()})

        @staticmethod
        def merge_field_info_dict(
            props: dict[str, FlextTypes.GeneralValueType],
            field_info: FieldInfo | FlextTypes.GeneralValueType,
        ) -> None:
            """Merge field_info dict attributes into props."""
            if isinstance(field_info, dict):
                props.update({k: v for k, v in field_info.items() if k != "__dict__"})
            elif hasattr(field_info, "__dict__"):
                metadata_dict = getattr(field_info, "__dict__", {})
                if isinstance(metadata_dict, dict):
                    props.update(dict(metadata_dict.items()))

        @staticmethod
        def process_metadata_list(
            metadata_attr: list[object],
        ) -> dict[str, FlextTypes.GeneralValueType]:
            """Process metadata list into dict."""
            result: dict[str, FlextTypes.GeneralValueType] = {}
            for item in metadata_attr:
                if hasattr(item, "__dict__"):
                    item_dict = getattr(item, "__dict__", {})
                    if isinstance(item_dict, dict):
                        result.update(item_dict)
                elif isinstance(item, dict):
                    result.update(item)
            return result

        @staticmethod
        def merge_metadata_attr(
            props: dict[str, FlextTypes.GeneralValueType],
            field_info: FieldInfo | FlextTypes.GeneralValueType,
        ) -> None:
            """Merge metadata attribute into props."""
            if not hasattr(field_info, "metadata"):
                return
            metadata_attr = getattr(field_info, "metadata", None)
            if metadata_attr is None:
                return
            if isinstance(metadata_attr, list):
                props["metadata"] = (
                    FlextCliModels.CliModelConverter.process_metadata_list(
                        metadata_attr
                    )
                )
            elif isinstance(metadata_attr, dict):
                props["metadata"] = metadata_attr

        @staticmethod
        def merge_json_schema_extra(
            props: dict[str, FlextTypes.GeneralValueType],
            field_info: FieldInfo | FlextTypes.GeneralValueType,
        ) -> None:
            """Merge json_schema_extra into props metadata."""
            if not hasattr(field_info, "json_schema_extra"):
                return
            json_schema_extra = getattr(field_info, "json_schema_extra", None)
            if json_schema_extra is None:
                return
            if "metadata" not in props:
                props["metadata"] = {}
            if isinstance(props["metadata"], dict) and isinstance(
                json_schema_extra, dict
            ):
                props["metadata"].update(json_schema_extra)

        @staticmethod
        def extract_field_properties(
            field_name: str,
            field_info: FieldInfo | FlextTypes.GeneralValueType,
            types: Mapping[str, type | str] | None = None,
        ) -> FlextResult[dict[str, FlextTypes.GeneralValueType]]:
            """Extract properties from Pydantic field info."""
            try:
                props = FlextCliModels.CliModelConverter.extract_base_props(
                    field_name, field_info
                )
                if types is not None:
                    FlextCliModels.CliModelConverter.merge_types_into_props(
                        props, types
                    )
                    FlextCliModels.CliModelConverter.merge_field_info_dict(
                        props, field_info
                    )
                    FlextCliModels.CliModelConverter.merge_metadata_attr(
                        props, field_info
                    )
                    FlextCliModels.CliModelConverter.merge_json_schema_extra(
                        props, field_info
                    )
                return FlextResult[dict[str, FlextTypes.GeneralValueType]].ok(props)
            except Exception as e:
                return FlextResult[dict[str, FlextTypes.GeneralValueType]].fail(
                    f"Extraction failed: {e}"
                )

        # Field validation rules: (field_key, expected_type, type_check_func)
        FIELD_VALIDATION_RULES: ClassVar[
            list[tuple[str, str, Callable[[object], bool]]]
        ] = [
            ("python_type", "type", lambda v: isinstance(v, type)),
            ("click_type", "str", lambda v: isinstance(v, str)),
            ("is_required", "bool", lambda v: isinstance(v, bool)),
            ("description", "str", lambda v: isinstance(v, str)),
            ("validators", "list/tuple", lambda v: isinstance(v, (list, tuple))),
            ("metadata", "dict", lambda v: isinstance(v, dict)),
        ]

        @staticmethod
        def validate_field_schema(
            field_data: Mapping[str, object],
        ) -> FlextResult[bool]:
            """Validate field data schema against rules."""
            for (
                field_key,
                type_name,
                check_func,
            ) in FlextCliModels.CliModelConverter.FIELD_VALIDATION_RULES:
                if field_key in field_data:
                    value = field_data[field_key]
                    if not check_func(value):
                        return FlextResult[bool].fail(
                            f"Invalid {field_key}: {value} (expected {type_name})"
                        )
            return FlextResult[bool].ok(True)

        @staticmethod
        def convert_field_value(
            field_value: object,
        ) -> FlextResult[FlextTypes.GeneralValueType]:
            """Convert field value to GeneralValueType."""
            if field_value is None:
                return FlextResult[FlextTypes.GeneralValueType].ok(None)
            if isinstance(field_value, (str, int, float, bool, dict, list)):
                return FlextResult[FlextTypes.GeneralValueType].ok(field_value)
            return FlextResult[FlextTypes.GeneralValueType].ok(str(field_value))

        @staticmethod
        def validate_dict_field_data(
            field_name: str,
            field_data: Mapping[str, object],
        ) -> FlextResult[FlextTypes.GeneralValueType]:
            """Validate field data when field_info is a dict/Mapping."""
            schema_result = FlextCliModels.CliModelConverter.validate_field_schema(
                field_data
            )
            if schema_result.is_failure:
                return FlextResult[FlextTypes.GeneralValueType].fail(
                    schema_result.error or "Schema validation failed"
                )
            field_value = field_data.get(field_name, None)
            return FlextCliModels.CliModelConverter.convert_field_value(field_value)

        @staticmethod
        def _validate_field_data(
            field_name: str,
            field_info: FieldInfo
            | FlextTypes.GeneralValueType
            | Mapping[str, FlextTypes.GeneralValueType]
            | dict[str, object]
            | dict[str, type | str | bool | list[object] | dict[str, object]],
            data: Mapping[str, FlextTypes.GeneralValueType] | None = None,
        ) -> FlextResult[FlextTypes.GeneralValueType]:
            """Validate field data against field info."""
            try:
                if isinstance(field_info, (dict, Mapping)):
                    return FlextCliModels.CliModelConverter.validate_dict_field_data(
                        field_name, field_info
                    )
                if data is not None:
                    if field_name not in data:
                        return FlextResult[FlextTypes.GeneralValueType].fail(
                            f"Field {field_name} not found"
                        )
                    return FlextResult[FlextTypes.GeneralValueType].ok(data[field_name])
                return FlextResult[FlextTypes.GeneralValueType].fail(
                    "No data provided for validation"
                )
            except Exception as e:
                return FlextResult[FlextTypes.GeneralValueType].fail(
                    f"Validation failed: {e}"
                )

        @staticmethod
        def _process_validators(
            field_info: Sequence[
                Callable[[FlextTypes.GeneralValueType], FlextTypes.GeneralValueType]
            ]
            | Sequence[object]
            | FlextTypes.GeneralValueType,
        ) -> list[Callable[[FlextTypes.GeneralValueType], FlextTypes.GeneralValueType]]:
            """Process validators from field info, filtering only callable validators."""
            if not isinstance(field_info, (list, tuple, Sequence)):
                return []
            validators: list[
                Callable[[FlextTypes.GeneralValueType], FlextTypes.GeneralValueType]
            ] = []
            for item in field_info:
                if callable(item):
                    # Type narrowing: item is callable, cast to proper validator type
                    # Type cast: validators may have different signatures, cast for compatibility
                    validator: Callable[
                        [FlextTypes.GeneralValueType], FlextTypes.GeneralValueType
                    ] = cast(
                        "Callable[[FlextTypes.GeneralValueType], FlextTypes.GeneralValueType]",
                        item,
                    )
                    validators.append(validator)
            return validators

    class CliModelDecorators:
        """Decorators for creating CLI commands from Pydantic models."""

        @staticmethod
        def cli_from_model(
            model_class: type[BaseModel],
        ) -> Callable[
            [
                Callable[
                    [BaseModel],
                    FlextResult[FlextTypes.GeneralValueType]
                    | FlextResult[object]
                    | FlextTypes.GeneralValueType,
                ]
            ],
            Callable[..., FlextTypes.GeneralValueType],
        ]:
            """Create decorator that converts function to CLI command from model."""

            def decorator(
                func: Callable[
                    [BaseModel],
                    FlextResult[FlextTypes.GeneralValueType]
                    | FlextResult[object]
                    | FlextTypes.GeneralValueType,
                ],
            ) -> Callable[..., FlextTypes.GeneralValueType]:
                def wrapper(
                    *_args: FlextTypes.GeneralValueType,
                    **kwargs: FlextTypes.GeneralValueType,
                ) -> FlextTypes.GeneralValueType:
                    try:
                        # Create model instance from kwargs
                        model_instance = model_class(**kwargs)
                        # Call original function with model
                        result = func(model_instance)
                        # Convert result to GeneralValueType if needed
                        output: FlextTypes.GeneralValueType
                        if isinstance(result, FlextResult):
                            if result.is_success:
                                # Type narrowing: result.value is object, convert
                                value = result.value
                                if isinstance(
                                    value,
                                    (str, int, float, bool, type(None), dict, list),
                                ):
                                    output = value
                                else:
                                    output = str(value)
                            else:
                                output = str(result.error or "Unknown error")
                        elif isinstance(
                            result,
                            (str, int, float, bool, type(None), list, dict, tuple),
                        ):
                            output = result
                        else:
                            # Fallback: convert to string
                            output = str(result)
                    except Exception as e:
                        # Return error string on failure (decorator pattern)
                        output = f"Validation failed: {e}"
                    return output

                return wrapper

            return decorator

        @staticmethod
        def cli_from_multiple_models(
            *model_classes: type[BaseModel],
        ) -> Callable[
            [Callable[..., FlextTypes.GeneralValueType]],
            Callable[..., FlextTypes.GeneralValueType],
        ]:
            """Create decorator for multiple models."""

            def decorator(
                func: Callable[..., FlextTypes.GeneralValueType],
            ) -> Callable[..., FlextTypes.GeneralValueType]:
                def wrapper(
                    *_args: FlextTypes.GeneralValueType,
                    **kwargs: FlextTypes.GeneralValueType,
                ) -> FlextTypes.GeneralValueType:
                    try:
                        # Create model instances from kwargs (simplified)
                        models = [model_cls(**kwargs) for model_cls in model_classes]
                        return func(*models)
                    except Exception as e:
                        return f"Validation failed: {e}"

                return wrapper

            return decorator

    class LoggingConfig(FlextModelsEntity.Value):
        """Logging configuration model."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        log_level: str = Field(default="INFO", description="Log level")
        log_format: str = Field(default="", description="Log format string")
        console_output: bool = Field(default=True, description="Enable console output")
        log_file: str = Field(default="", description="Log file path")

        @property
        def logging_summary(self) -> FlextCliModels.CliLoggingData:
            """Return logging summary as CliLoggingData model."""
            return FlextCliModels.CliLoggingData(
                level=self.log_level,
                console_enabled=self.console_output,
            )

    class CliLoggingData(FlextModelsEntity.Value):
        """CLI logging summary data."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        level: str = Field(default="INFO", description="Log level")
        console_enabled: bool = Field(
            default=True, description="Console output enabled"
        )

    class CliDebugData(FlextModelsEntity.Value):
        """CLI debug summary data."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        service: str = Field(..., description="Service name")
        level: str = Field(..., description="Debug level")
        message: str = Field(..., description="Debug message")
