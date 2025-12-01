"""FlextCli models module - Pydantic models with StrEnum."""

from __future__ import annotations

import types
from collections.abc import Callable, Mapping, Sequence
from typing import Literal, Self, get_args, get_origin

import typer
from flext_core import FlextModels, FlextResult, FlextTypes
from flext_core._models.entity import FlextModelsEntity
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.fields import FieldInfo

# Type alias for Pydantic v2 include/exclude parameters (IncEx was removed in v2)
IncEx = set[str] | dict[str, int | str | set[str]] | None

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.utilities import FlextCliUtilities


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

    def execute(self) -> FlextResult[FlextTypes.JsonDict]:
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

        # Override TimestampableMixin fields to use strings instead of datetime
        # This is intentional to avoid datetime serialization issues in CLI context
        updated_at: str | None = Field(  # type: ignore[assignment]
            default=None,
            description="Last update timestamp",
        )
        created_at: str | None = Field(  # type: ignore[assignment]
            default=None,
            description="Creation timestamp",
        )

        def model_post_init(self, __context: object, /) -> None:  # type: ignore[override]
            """Override to prevent frozen instance errors from TimestampableMixin."""
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
            ...,
            min_length=1,
            description="Command description",
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
                    command = cls(**data)
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
                raise ValueError(msg)
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
        # Note: created_at/updated_at conflict with TimestampableMixin.
        # Using strings instead of datetime.
        created_at: str = Field(  # type: ignore[assignment]
            default="", description="Session creation timestamp"
        )
        updated_at: str = Field(  # type: ignore[assignment]
            default="",
            description="Session last update timestamp",
        )

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
            default=FlextCliConstants.ServerType.OUD,
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

        def model_dump(
            self,
            *,
            mode: Literal["json", "python"] | str = "python",
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
        ) -> FlextTypes.JsonDict:
            """Dump model with sensitive data masking."""
            # Include/exclude are already correct types for super().model_dump()
            data = super().model_dump(
                mode=mode,
                include=include,
                exclude=exclude,
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

            Returns:
                typer.Option instance configured from registry metadata

            """
            field_meta = self.registry.get(self.field_name, {})

            # Extract option metadata from registry
            help_text = str(field_meta.get("help", ""))
            short_flag = str(field_meta.get("short", ""))
            default_value = field_meta.get("default")
            is_flag = bool(field_meta.get("is_flag", False))

            # Build option arguments
            option_args: list[str] = [f"--{self.field_name.replace('_', '-')}"]
            if short_flag:
                option_args.append(f"-{short_flag}")

            return typer.Option(
                default_value,
                *option_args,
                help=help_text,
                is_flag=is_flag,
            )

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

        def build(self) -> Callable[..., FlextTypes.GeneralValueType]:
            """Build Typer command from Pydantic model.

            Returns:
                Typer command function with auto-generated parameters

            """
            # Get model fields for parameter generation
            model_fields = getattr(self.model_class, "model_fields", {})

            # Build annotations dict first before creating function
            annotations: dict[str, type] = {}
            defaults: dict[str, FlextTypes.GeneralValueType] = {}

            # Generate Typer parameters from model fields
            for field_name, field_info in model_fields.items():
                # Extract field metadata
                default_value = getattr(field_info, "default", None)

                # Get config default if available
                if self.config is not None and hasattr(self.config, field_name):
                    config_value = getattr(self.config, field_name)
                    if config_value is not None:
                        default_value = config_value

                # Get field type from Pydantic field_info annotation
                field_type = getattr(field_info, "annotation", None)
                if field_type is None or field_type is object:
                    # Fallback: infer from default value type
                    if default_value is not None:
                        field_type = type(default_value)
                    else:
                        # Default to str for Typer compatibility
                        field_type = str
                else:
                    # Handle Optional types (Union[SomeType, None])
                    origin = get_origin(field_type)
                    if origin is not None:
                        args = get_args(field_type)
                        # Extract non-None type from Optional/Union
                        non_none_types = [arg for arg in args if arg is not type(None)]
                        if non_none_types:
                            field_type = non_none_types[0]

                # Store annotation
                annotations[field_name] = field_type

                # Store default if available
                if default_value is not None:
                    defaults[field_name] = default_value

            # Build function signature parts - separate params with and without defaults
            param_parts_no_default = []
            param_parts_with_default = []

            # Typer-compatible built-in types
            builtin_types = {
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

            for name, field_type in annotations.items():
                # Get type name - handle both built-in types and custom types
                if hasattr(field_type, "__name__"):
                    type_name = field_type.__name__
                    # Check if it's a built-in type that Typer supports
                    if type_name in builtin_types:
                        pass  # Use as-is
                    else:
                        # For all other types (Literal, nested types, custom types), use str
                        # Typer will accept string input, and Pydantic will validate the actual type
                        type_name = "str"
                else:
                    # Unknown type - use str as fallback
                    type_name = "str"

                if name in defaults:
                    default_repr = repr(defaults[name])
                    param_parts_with_default.append(
                        f"{name}: {type_name} = {default_repr}"
                    )
                else:
                    param_parts_no_default.append(f"{name}: {type_name}")

            # Combine: params without defaults first, then params with defaults
            param_parts = param_parts_no_default + param_parts_with_default

            # Create closure variables to capture self attributes
            builder_model_class = self.model_class
            builder_config = self.config
            builder_handler = self.handler

            # Build function signature string
            sig_parts = ", ".join(param_parts)

            # Create function dynamically using types.FunctionType to properly capture closure

            # Create function code with proper closure capture
            func_body = f"""
    kwargs = {{{", ".join(f'"{name}": {name}' for name in annotations)}}}
    # Create model instance from kwargs
    model_instance = builder_model_class(**kwargs)

    # Update config if provided
    if builder_config is not None:
        for field_name, value in kwargs.items():
            if hasattr(builder_config, field_name):
                # Use __dict__ to bypass Pydantic validators
                object.__setattr__(builder_config, field_name, value)

    # Call handler with model instance
    handler_func = builder_handler
    if callable(handler_func):
        return handler_func(model_instance)
    return None
"""

            # Create function object with proper signature
            func_globals = {
                "builder_model_class": builder_model_class,
                "builder_config": builder_config,
                "builder_handler": builder_handler,
                "__builtins__": __builtins__,
            }

            # Build function signature dynamically
            func_code = f"def command_wrapper({sig_parts}):{func_body}"

            # Execute in namespace with captured variables
            exec(func_code, func_globals)  # noqa: S102
            return func_globals["command_wrapper"]

    class CliParameterSpec:
        """CLI parameter specification for model-to-CLI conversion."""

        def __init__(
            self,
            field_name: str,
            param_type: type,
            click_type: str,
            default: FlextTypes.GeneralValueType | None = None,
            help: str = "",
        ) -> None:
            """Initialize CLI parameter spec."""
            self.field_name = field_name
            self.param_type = param_type
            self.click_type = click_type
            self.default = default
            self.help = help

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
                # Use FlextCliUtilities.Model.from_dict for model creation
                # cli_args is already GeneralValueType compatible
                cli_args_dict: dict[str, FlextTypes.GeneralValueType] = dict(cli_args)
                return FlextCliUtilities.Model.from_dict(model_cls, cli_args_dict)
            except Exception as e:
                return FlextResult[M].fail(f"Model creation failed: {e}")

        @staticmethod
        def model_to_cli_params(
            model_cls: type,
        ) -> FlextResult[list[FlextCliModels.CliParameterSpec]]:
            """Convert Pydantic model to list of CLI parameter specifications."""
            try:
                if not hasattr(model_cls, "model_fields"):
                    return FlextResult[list["FlextCliModels.CliParameterSpec"]].fail(
                        f"{model_cls.__name__} is not a Pydantic model"
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
                            help=help_text,
                        )
                    )
                return FlextResult[list["FlextCliModels.CliParameterSpec"]].ok(params)
            except Exception as e:
                return FlextResult[list["FlextCliModels.CliParameterSpec"]].fail(
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
            options: list[FlextTypes.GeneralValueType] = []
            for param in params:
                # Create a simple object with option_name and param_decls attributes
                option_name = f"--{param.field_name.replace('_', '-')}"
                option_obj = type(
                    "ClickOption",
                    (),
                    {
                        "option_name": option_name,
                        "param_decls": [option_name],
                        "field_name": param.field_name,
                        "param_type": param.param_type,
                        "default": param.default,
                        "help": param.help,
                    },
                )()
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
                    return FlextResult["FlextCliModels.CliParameterSpec"].fail(
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
                return FlextResult["FlextCliModels.CliParameterSpec"].ok(
                    FlextCliModels.CliParameterSpec(
                        field_name=field_name,
                        param_type=field_type,
                        click_type=click_type_str,
                        default=default,
                        help=help_text,
                    )
                )
            except Exception as e:
                return FlextResult["FlextCliModels.CliParameterSpec"].fail(
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
                    return non_none_types[0]
                return str  # Fallback
            # Handle generic types like list[str], dict[str, str]
            origin = get_origin(pydantic_type)
            if origin is not None:
                # For generic types like list[str], dict[str, str], return the origin (list, dict)
                if origin in (list, dict):
                    return origin
                args = get_args(pydantic_type)
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    return non_none_types[0]
            # Check if it's a known simple type
            if isinstance(pydantic_type, type) and pydantic_type in (
                str,
                int,
                float,
                bool,
                list,
                dict,
            ):
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
        def extract_field_properties(
            field_name: str,
            field_info: FieldInfo | FlextTypes.GeneralValueType,
            types: Mapping[str, type | str] | None = None,
        ) -> FlextResult[dict[str, FlextTypes.GeneralValueType]]:
            """Extract properties from Pydantic field info."""
            try:
                annotation = getattr(field_info, "annotation", None)
                props: dict[str, FlextTypes.GeneralValueType] = {
                    "field_name": field_name,
                    "annotation": str(annotation) if annotation is not None else "str",
                    "default": getattr(field_info, "default", None),
                    "description": str(getattr(field_info, "description", "")),
                }
                # Add types if provided
                if types is not None:
                    if isinstance(types, dict):
                        props.update({k: str(v) for k, v in types.items()})
                    # Also check if field_info has metadata dict
                    if isinstance(field_info, dict):
                        props.update({
                            k: v for k, v in field_info.items() if k != "__dict__"
                        })
                    elif hasattr(field_info, "__dict__"):
                        metadata_dict_from_attr = getattr(field_info, "__dict__", {})
                        if isinstance(metadata_dict_from_attr, dict):
                            props.update({
                                k: v for k, v in metadata_dict_from_attr.items()
                            })
                    # Check for metadata attribute
                    if hasattr(field_info, "metadata"):
                        metadata_attr = getattr(field_info, "metadata", None)
                        if metadata_attr is not None:
                            if isinstance(metadata_attr, list):
                                # Convert list of metadata objects to dict
                                metadata_dict_from_list: dict[
                                    str, FlextTypes.GeneralValueType
                                ] = {}
                                for item in metadata_attr:
                                    if hasattr(item, "__dict__"):
                                        item_dict = getattr(item, "__dict__", {})
                                        if isinstance(item_dict, dict):
                                            metadata_dict_from_list.update(item_dict)
                                    elif isinstance(item, dict):
                                        metadata_dict_from_list.update(item)
                                props["metadata"] = metadata_dict_from_list
                            elif isinstance(metadata_attr, dict):
                                props["metadata"] = metadata_attr
                    # Check for json_schema_extra
                    if hasattr(field_info, "json_schema_extra"):
                        json_schema_extra = getattr(
                            field_info, "json_schema_extra", None
                        )
                        if json_schema_extra is not None:
                            if "metadata" not in props:
                                props["metadata"] = {}
                            if isinstance(props["metadata"], dict) and isinstance(
                                json_schema_extra, dict
                            ):
                                props["metadata"].update(json_schema_extra)
                return FlextResult[dict[str, FlextTypes.GeneralValueType]].ok(props)
            except Exception as e:
                return FlextResult[dict[str, FlextTypes.GeneralValueType]].fail(
                    f"Extraction failed: {e}"
                )

        @staticmethod
        def _validate_field_data(
            field_name: str,
            field_info: FieldInfo
            | FlextTypes.GeneralValueType
            | Mapping[str, FlextTypes.GeneralValueType]
            | dict[str, object]
            | dict[str, type | str | bool | list | dict],
            data: Mapping[str, FlextTypes.GeneralValueType] | None = None,
        ) -> FlextResult[FlextTypes.GeneralValueType]:
            """Validate field data against field info."""
            try:
                # If field_info is a dict, treat it as the data to validate
                if isinstance(field_info, (dict, Mapping)):
                    field_data = field_info
                    # Validate python_type
                    if "python_type" in field_data:
                        python_type = field_data["python_type"]
                        if not isinstance(python_type, type):
                            return FlextResult[FlextTypes.GeneralValueType].fail(
                                f"Invalid python_type: {python_type}"
                            )
                    # Validate click_type
                    if "click_type" in field_data:
                        click_type = field_data["click_type"]
                        if not isinstance(click_type, str):
                            return FlextResult[FlextTypes.GeneralValueType].fail(
                                f"Invalid click_type: {click_type}"
                            )
                    # Validate is_required
                    if "is_required" in field_data:
                        is_required = field_data["is_required"]
                        if not isinstance(is_required, bool):
                            return FlextResult[FlextTypes.GeneralValueType].fail(
                                f"Invalid is_required: {is_required}"
                            )
                    # Validate description
                    if "description" in field_data:
                        description = field_data["description"]
                        if not isinstance(description, str):
                            return FlextResult[FlextTypes.GeneralValueType].fail(
                                f"Invalid description: {description}"
                            )
                    # Validate validators
                    if "validators" in field_data:
                        validators = field_data["validators"]
                        if not isinstance(validators, (list, tuple)):
                            return FlextResult[FlextTypes.GeneralValueType].fail(
                                f"Invalid validators: {validators}"
                            )
                    # Validate metadata
                    if "metadata" in field_data:
                        metadata = field_data["metadata"]
                        if not isinstance(metadata, dict):
                            return FlextResult[FlextTypes.GeneralValueType].fail(
                                f"Invalid metadata: {metadata}"
                            )
                    return FlextResult[FlextTypes.GeneralValueType].ok(
                        field_data.get(field_name, None)
                    )
                # If data is provided, use it
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
                    # Type narrowing: item is callable, cast to correct type
                    validator = item  # type: ignore[assignment]
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
                    *args: FlextTypes.GeneralValueType,
                    **kwargs: FlextTypes.GeneralValueType,
                ) -> FlextTypes.GeneralValueType:
                    try:
                        # Create model instance from kwargs
                        model_instance = model_class(**kwargs)
                        # Call original function with model
                        return func(model_instance)
                    except Exception as e:
                        # Return error string on failure (decorator pattern)
                        return f"Validation failed: {e}"

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
                    *args: FlextTypes.GeneralValueType,
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
