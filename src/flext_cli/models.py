"""FlextCli models module - Pydantic models with StrEnum."""

from __future__ import annotations

import operator
import types
from collections.abc import Callable, Mapping, Sequence
from typing import (
    ClassVar,
    Literal,
    Self,
    Union,
    get_args,
    get_origin,
    override,
)

import typer
from flext_core import (
    FlextModels,
    FlextRuntime,
    r,
    u as flext_u,
)
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator
from pydantic.fields import FieldInfo

from flext_cli.config import FlextCliConfig
from flext_cli.constants import c
from flext_cli.protocols import p
from flext_cli.typings import t


class FlextCliModels(FlextModels):
    """FlextCli models extending FlextModels.

    RULES:
    ───────
    1. Inherit from FlextModels, NEVER BaseModel directly
    2. ConfigDict with frozen=True, extra="forbid"
    3. Use StrEnum from constants, do not create new ones
    4. field_validator for complex validation
    5. Self for transformation methods
    """

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Warn when FlextCliModels is subclassed directly."""
        super().__init_subclass__(**kwargs)
        flext_u.Deprecation.warn_once(
            f"subclass:{cls.__name__}",
            "Subclassing FlextCliModels is deprecated. Use FlextModels.Cli instead.",
        )

    class Cli:
        """CLI project namespace for cross-project access.

        This namespace contains all CLI-specific models from flext-cli.
        Access via: m.Cli.CliCommand, m.Cli.PromptConfig, etc.
        """

        @staticmethod
        def execute() -> r[t.Json.JsonDict]:
            """Execute models operation - returns empty dict for compatibility."""
            return r[t.Json.JsonDict].ok({})

        # Nested classes exposing Entity and Value via inheritance from parent
        class Entity(FlextModels.Entity):
            """Entity model base extending FlextModels.Entity via inheritance."""

        # Entry class for compatibility with flext-ldif and other projects
        # m.Entry is a class that can be inherited by FlextLdifModels.Entry
        # flext-cli does NOT depend on flext-ldif - this is a base class for other projects
        class Entry(Entity):
            """Entry model base extending Entity for compatibility with flext-ldif.

            This class extends Entity and can be inherited by FlextLdifModels.Entry
            when flext-ldif is used. flext-cli does not depend on flext-ldif.
            All methods returning self use Self for proper type inference.
            """

        class Value(FlextModels.Value):
            """Value model base extending FlextModels.Value via inheritance."""

        class CliCommand(Entity):
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
                Uses object instead of GeneralValueType to accept Protocol types.
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

            result: t.GeneralValueType | None = Field(
                default=None,
                description="Command result",
            )

            kwargs: t.Json.JsonDict = Field(
                default_factory=dict,
                description="Command keyword arguments",
            )

            def execute(self, _args: Sequence[str]) -> r[t.GeneralValueType]:
                """Execute command with arguments - required by Command.

                Args:
                    _args: Command arguments (unused in default implementation)

                Returns:
                    r[t.GeneralValueType]: Command execution result

                """
                # Default implementation - returns empty result
                # Real implementations should override this method
                return r[t.GeneralValueType].ok(None)

            def with_status(self, status: str | c.Cli.CommandStatus) -> Self:
                """Return copy with new status.

                Accepts both str and c.Cli.CommandStatus for protocol compatibility.
                """
                status_value = (
                    status.value if isinstance(status, c.Cli.CommandStatus) else status
                )
                return self._copy_with_update(status=status_value)

            def with_args(self, args: Sequence[str]) -> Self:
                """Return copy with new arguments."""
                return self._copy_with_update(args=list(args))

            @property
            def command_summary(self) -> dict[str, str]:
                """Return command summary as dict."""
                return {"command": self.command_line or self.name}

            def start_execution(self) -> r[Self]:
                """Start command execution - update status to running."""
                try:
                    updated = self.model_copy(update={"status": "running"})
                    return r.ok(updated)
                except Exception as e:
                    return r.fail(f"Failed to start execution: {e}")

            def complete_execution(self, exit_code: int) -> r[Self]:
                """Complete command execution with exit code."""
                try:
                    updated = self.model_copy(
                        update={"status": "completed", "exit_code": exit_code},
                    )
                    return r.ok(updated)
                except Exception as e:
                    return r.fail(f"Failed to complete execution: {e}")

            def update_status(self, status: str) -> Self:
                """Update command status."""
                return self.model_copy(update={"status": status})

            @classmethod
            def validate_command_input(cls, data: object) -> r[Self]:
                """Validate command input data."""
                try:
                    if data is None:
                        return r.fail("Input must be a dictionary")
                    # Check instance first - early return avoids unreachable code
                    if isinstance(data, cls):
                        return r.ok(data)
                    # Type narrowing: data is not cls instance
                    # Check if dict for model_validate
                    if not isinstance(data, dict):
                        return r.fail("Input must be a dictionary")
                    # Type narrowing: data is dict, use model_validate for type-safe creation
                    if not isinstance(data, dict):
                        msg = "data must be dict"
                        raise TypeError(msg)
                    # Type narrowing: data is confirmed to be dict[str, object]
                    data_dict: dict[str, object] = (
                        data if isinstance(data, dict) else {}
                    )
                    # Use model_validate for type-safe model creation from dict
                    command = cls.model_validate(data_dict)
                    return r.ok(command)
                except Exception as e:
                    return r.fail(f"Validation failed: {e}")

        class CliSession(Entity):
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
            def validate_status(cls, value: t.GeneralValueType) -> str:
                """Validate session status."""
                if not isinstance(value, str):
                    msg = f"Status must be a string, got {type(value)}"
                    raise TypeError(msg)
                # Validate value is in allowed statuses
                str_value: str = value
                valid_statuses = c.Cli.ValidationLists.SESSION_STATUSES
                if str_value not in valid_statuses:
                    msg = f"session_status must be one of {valid_statuses}, got '{str_value}'"
                    raise ValueError(msg)
                return str_value

            # Use protocol for type hint to enable structural typing
            commands: Sequence[p.Cli.Command] = Field(
                default_factory=list,
                description="Commands in session",
            )
            start_time: str | None = Field(
                default=None, description="Session start time"
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
            def session_summary(self) -> m.Cli.CliSessionData:
                """Return session summary as CliSessionData model."""
                # Return concrete model instance (not protocol)
                return m.Cli.CliSessionData(
                    session_id=self.session_id,
                    status=self.status,
                    commands_count=len(self.commands),
                )

            @property
            def commands_by_status(self) -> dict[str, list[m.Cli.CliCommand]]:
                """Group commands by status."""
                # Filter commands to only CliCommand instances

                cli_commands: list[m.Cli.CliCommand] = []
                for cmd in self.commands:
                    if isinstance(cmd, m.Cli.CliCommand):
                        cli_commands.append(cmd)  # noqa: PERF401
                # Group by status
                result: dict[str, list[m.Cli.CliCommand]] = {}
                for command in cli_commands:
                    status = command.status or ""
                    if status not in result:
                        result[status] = []
                    result[status].append(command)
                return result

            def add_command(self, command: p.Cli.Command) -> r[Self]:
                """Add command to session."""
                try:
                    updated_commands = list(self.commands) + [command]
                    updated_session = self._copy_with_update(commands=updated_commands)
                    return r.ok(updated_session)
                except Exception as e:
                    return r.fail(f"Failed to add command: {e}")

            def _copy_with_update(self, **updates: object) -> Self:
                """Helper method for model_copy with updates - reduces repetition.

                Composition pattern: centralizes model_copy logic for reuse.
                Uses object instead of GeneralValueType to accept Protocol types.
                """
                return self.model_copy(update=updates)

        class CliSessionData(Value):
            """CLI session summary data extending Value via inheritance.

            Inherits frozen=True and extra="forbid" from FlextModels.Value
            (via FrozenStrictModel), no need to redefine.
            """

            session_id: str = Field(..., description="Session identifier")
            status: str = Field(..., description="Session status")
            commands_count: int = Field(default=0, description="Number of commands")

        class CliContext(Value):
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

            env: Mapping[str, str] = Field(
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

        class CliOutput(Value):
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

        class CommandResult(Value):
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

            @property
            @computed_field
            def success(self) -> bool:
                """Check if command succeeded.

                Computed field included in serialization.
                """
                return self.exit_code == 0

            @property
            @computed_field
            def has_output(self) -> bool:
                """Check if command produced output.

                Computed field included in serialization.
                """
                return bool(self.stdout or self.stderr)

        class ServiceExecutionResult(Value):
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

        class CliConfig(Entity):
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

        class TableConfig(Value):
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

        class WorkflowResult(Value):
            """Workflow execution result with step-by-step tracking.

            Tracks overall workflow success and individual step results.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            step_results: Sequence[t.Json.JsonDict] = Field(
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

        class CliParamsConfig(Value):
            """CLI parameters configuration for command-line parsing.

            Maps directly to CLI flags: --verbose, --quiet, --debug, --trace, etc.
            All fields are optional (None) to allow partial updates.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            verbose: bool | None = Field(
                default=None, description="Enable verbose output"
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
            def params(self) -> Mapping[str, t.GeneralValueType]:
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

        class OptionConfig(Value):
            """Configuration for CLI option decorators.

            Used with create_option_decorator to reduce argument count.
            """

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
                arbitrary_types_allowed=True,
            )

            default: t.GeneralValueType | None = Field(
                default=None,
                description="Default value",
            )
            type_hint: object = Field(
                default=None,
                description="Parameter type (Click type or Python type)",
            )
            required: bool = Field(
                default=False, description="Whether option is required"
            )
            help_text: str | None = Field(
                default=None, description="Help text for option"
            )
            is_flag: bool = Field(
                default=False,
                description="Whether this is a boolean flag",
            )
            flag_value: t.GeneralValueType | None = Field(
                default=None,
                description="Value when flag is set",
            )
            multiple: bool = Field(default=False, description="Allow multiple values")
            count: bool = Field(default=False, description="Count occurrences")
            show_default: bool = Field(
                default=False, description="Show default in help"
            )

        class ConfirmConfig(Value):
            """Configuration for confirm prompts.

            Used with confirm() method to reduce argument count.
            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            default: bool = Field(default=False, description="Default value")
            abort: bool = Field(default=False, description="Abort if not confirmed")
            prompt_suffix: str = Field(
                default=c.Cli.UIDefaults.DEFAULT_PROMPT_SUFFIX,
                description="Suffix after prompt",
            )
            show_default: bool = Field(
                default=True, description="Show default in prompt"
            )
            err: bool = Field(default=False, description="Write to stderr")

        class PromptConfig(Value):
            """Configuration for input prompts.

            Used with prompt() method to reduce argument count.
            """

            model_config = ConfigDict(
                frozen=True,
                extra="forbid",
                arbitrary_types_allowed=True,
            )

            default: t.GeneralValueType | None = Field(
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
                default=True, description="Show default in prompt"
            )
            err: bool = Field(default=False, description="Write to stderr")
            show_choices: bool = Field(
                default=True, description="Show available choices"
            )

        class PathInfo(Value):
            """Path information for debug output.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            index: int = Field(default=0, description="Path index in sys.path")
            path: str = Field(...)
            exists: bool = Field(default=False)
            is_file: bool = Field(default=False)
            is_dir: bool = Field(default=False)

        class EnvironmentInfo(Value):
            """Environment information for debug output.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            python_version: str = Field(default="")
            os_name: str = Field(default="")
            os_version: str = Field(default="")
            variables: Mapping[str, str] = Field(default_factory=dict)

        class SystemInfo(Value):
            """System information for debug output.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            python_version: str = Field(default="")
            platform: str = Field(default="")
            architecture: list[str] = Field(default_factory=list)
            processor: str = Field(default="")
            hostname: str = Field(default="")
            memory_total: int = Field(default=0)
            cpu_count: int = Field(default=0)

        class ContextExecutionResult(Value):
            """Context execution result.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            success: bool = Field(default=True)
            context_id: str = Field(default="")
            metadata: t.Json.JsonDict = Field(default_factory=dict)
            context_executed: bool = Field(
                default=False,
                description="Whether context was executed",
            )
            command: str = Field(default="", description="Command executed in context")
            arguments_count: int = Field(default=0, description="Number of arguments")
            timestamp: str = Field(default="", description="Execution timestamp")

        class DebugInfo(Value):
            """Debug information model with sensitive data masking.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            service: str = Field(..., description="Service name")
            level: str = Field(..., description="Debug level")
            message: str = Field(..., description="Debug message")
            system_info: t.Json.JsonDict = Field(
                default_factory=dict,
                description="System information",
            )
            config_info: t.Json.JsonDict = Field(
                default_factory=dict,
                description="Configuration information",
            )

            @field_validator("level", mode="before")
            @classmethod
            def normalize_level(cls, value: t.GeneralValueType) -> str:
                """Normalize level to uppercase."""
                # Type narrowing: ensure value is str before calling .upper()
                if isinstance(value, str):
                    return value.upper()
                return str(value).upper()

            @property
            def debug_summary(self) -> m.Cli.CliDebugData:
                """Return debug summary as CliDebugData model."""
                return m.Cli.CliDebugData(
                    service=self.service,
                    level=self.level,
                    message=self.message,
                )

            def dump_masked(self) -> dict[str, t.GeneralValueType]:
                """Dump model with sensitive data masking.

                Business Rule:
                ──────────────
                Returns model_dump() with sensitive fields masked before serialization.
                This is a separate method to avoid Pydantic method override type issues.

                Audit Implication:
                ───────────────────
                Sensitive data (passwords, tokens, secrets) are masked in serialized output.
                This prevents accidental exposure of credentials in logs or API responses.

                Returns:
                    Dict with sensitive values masked as "***MASKED***".

                """
                data = self.model_dump()
                sensitive_keys = ["password", "token", "secret", "key", "credential"]

                # Mask sensitive keys in system_info using mapper
                system_info = u.mapper().get(data, "system_info")
                system_dict: dict[str, t.GeneralValueType]
                if system_info and FlextRuntime.is_dict_like(system_info):
                    # Type narrowing: system_info is dict-like, convert to dict
                    if isinstance(system_info, dict):
                        system_dict = system_info
                    # Use mapper to convert to dict
                    # Type narrowing: system_info is dict-like but not dict, convert
                    elif not isinstance(system_info, (dict, Mapping)):
                        system_dict = {}
                    else:
                        # system_info is Mapping, convert to dict
                        # Type narrowing: Mapping values are GeneralValueType compatible
                        if isinstance(system_info, Mapping):
                            # Convert Mapping to dict - values are GeneralValueType compatible
                            # Use dict comprehension to help type checker
                            system_dict_raw: dict[str, t.GeneralValueType] = {
                                str(k): v for k, v in system_info.items()
                            }
                        else:
                            system_dict_raw = {}
                        system_dict = system_dict_raw
                else:
                    system_dict = {}

                # Apply masking to system_dict (regardless of how it was obtained)
                masked_system_dict: dict[str, t.GeneralValueType] = {
                    k: (
                        "***MASKED***"
                        if any(sensitive in k.lower() for sensitive in sensitive_keys)
                        else v
                    )
                    for k, v in system_dict.items()
                }
                data["system_info"] = masked_system_dict

                # Mask sensitive keys in config_info using mapper
                config_info = u.mapper().get(data, "config_info")
                config_dict: dict[str, t.GeneralValueType]
                if config_info and FlextRuntime.is_dict_like(config_info):
                    # Type narrowing: config_info is dict-like, convert to dict
                    if isinstance(config_info, dict):
                        config_dict = config_info
                    # Use mapper to convert to dict
                    # Type narrowing: config_info is dict-like but not dict, convert
                    elif not isinstance(config_info, (dict, Mapping)):
                        config_dict = {}
                    else:
                        # config_info is Mapping, convert to dict
                        # Type narrowing: Mapping values are GeneralValueType compatible
                        if isinstance(config_info, Mapping):
                            # Convert Mapping to dict - values are GeneralValueType compatible
                            # Use dict comprehension to help type checker
                            config_dict_raw: dict[str, t.GeneralValueType] = {
                                str(k): v for k, v in config_info.items()
                            }
                        else:
                            config_dict_raw = {}
                        config_dict = config_dict_raw
                else:
                    config_dict = {}

                # Apply masking to config_dict (regardless of how it was obtained)
                masked_config_dict: dict[str, t.GeneralValueType] = {
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
                registry: Mapping[str, t.Json.JsonDict],
            ) -> None:
                """Initialize builder with field name and registry.

                Args:
                    field_name: Name of field in "FlextCliConfig"
                    registry: CLI parameter registry mapping field names to option metadata

                """
                self.field_name = field_name
                self.registry = registry

            def build(self) -> t.GeneralValueType:
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
                # Use u.mapper().get() for safe extraction with defaults
                # Extract field metadata from registry using u.mapper().get()
                field_meta_raw: object = u.mapper().get(
                    self.registry, self.field_name, default={}
                )
                if not u.Guards.is_type(field_meta_raw, dict):
                    msg = "field_meta_raw must be dict"
                    raise TypeError(msg)
                # Type narrowing: field_meta_raw is dict, cast to dict[str, GeneralValueType]
                field_meta: dict[str, t.GeneralValueType] = (
                    field_meta_raw if isinstance(field_meta_raw, dict) else {}
                )
                # Extract option metadata from registry
                help_text = str(u.mapper().get(field_meta, "help", default=""))
                short_flag = str(u.mapper().get(field_meta, "short", default=""))
                default_value = u.mapper().get(field_meta, "default")
                # Note: is_flag is deprecated in Typer - boolean defaults auto-enable flag behavior

                # Use field_name_override if available, otherwise use field_name
                # Registry uses KEY_FIELD_NAME_OVERRIDE to map CLI param name to field name
                field_name_override = u.mapper().get(
                    field_meta,
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

                # typer.Option returns typer.Option which is compatible with GeneralValueType
                # Do NOT pass is_flag or flag_value - deprecated in Typer
                option: t.GeneralValueType = typer.Option(
                    default_value,
                    *option_args,
                    help=help_text,
                )
                return option

        class PasswordAuth(Value):
            """Password authentication data.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            username: str = Field(...)
            password: str = Field(...)
            realm: str = Field(default="")

        class CmdConfig(Value):
            """Command configuration.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            name: str = Field(...)
            description: str = Field(default="")
            hidden: bool = Field(default=False)
            deprecated: bool = Field(default=False)

        class TokenData(Value):
            """Authentication token data.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            token: str = Field(...)
            expires_at: str = Field(default="")
            token_type: str = Field(default="Bearer")

        class SessionStatistics(Value):
            """Statistics for CLI session tracking.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            commands_executed: int = Field(
                default=0,
                description="Number of commands executed",
            )
            errors_count: int = Field(
                default=0, description="Number of errors encountered"
            )
            session_duration_seconds: float = Field(
                default=0.0,
                description="Session duration in seconds",
            )

        class PromptStatistics(Value):
            """Statistics for prompt service usage tracking.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            prompts_executed: int = Field(
                default=0, description="Total prompts executed"
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

        class CommandStatistics(Value):
            """Command statistics.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            total_commands: int = Field(default=0)
            successful_commands: int = Field(default=0)
            failed_commands: int = Field(default=0)

        class CommandExecutionContextResult(Value):
            """Command execution context result.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            command_name: str = Field(...)
            exit_code: int = Field(default=0)
            output: str = Field(default="")
            context: t.Json.JsonDict = Field(default_factory=dict)

        class WorkflowStepResult(Value):
            """Workflow step result.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            step_name: str = Field(...)
            success: bool = Field(default=True)
            message: str = Field(default="")
            duration: float = Field(default=0.0)

        class WorkflowProgress(Value):
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
                model_class: type[BaseModel],
                handler: Callable[[BaseModel], t.GeneralValueType],
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

                # u.filter for list accepts predicate(item) -> bool
                def is_not_none_type(arg: object) -> bool:
                    """Check if arg is not type(None)."""
                    return arg is not type(None)

                args_list: list[object] = list(args)
                non_none_types_list = u.Cli.filter(
                    args_list, predicate=is_not_none_type
                )
                if not u.Guards.is_type(non_none_types_list, list):
                    msg = "non_none_types_list must be list"
                    raise TypeError(msg)
                # Type narrowing: filter returns list[object], but we know items are types
                # Validate at runtime and narrow type
                non_none_types: list[type] = [
                    item for item in non_none_types_list if isinstance(item, type)
                ]
                inner_type = non_none_types[0] if non_none_types else str

                if get_origin(inner_type) is Literal:
                    return "Optional[str]", inner_type

                inner_name = m.Cli.ModelCommandBuilder.get_builtin_name(
                    inner_type,
                    builtin_types,
                )
                return f"Optional[{inner_name}]", inner_type

            @staticmethod
            def handle_union_type(
                args: tuple[type, ...],
                builtin_types: set[str],
            ) -> tuple[str, type]:
                """Handle Union without None."""

                # u.filter for list accepts predicate(item) -> bool
                def is_not_none_type(arg: object) -> bool:
                    """Check if arg is not type(None)."""
                    return arg is not type(None)

                args_list: list[object] = list(args)
                non_none_types_list = u.Cli.filter(
                    args_list, predicate=is_not_none_type
                )
                if not u.Guards.is_type(non_none_types_list, list):
                    msg = "non_none_types_list must be list"
                    raise TypeError(msg)
                # Type narrowing: filter returns list[object], but we know items are types
                # Validate at runtime and narrow type
                non_none_types: list[type] = [
                    item for item in non_none_types_list if isinstance(item, type)
                ]
                if not non_none_types:
                    return "str", str

                first_type = non_none_types[0]
                if get_origin(first_type) is Literal:
                    return "str", first_type

                type_name = m.Cli.ModelCommandBuilder.get_builtin_name(
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
                builder = m.Cli.ModelCommandBuilder

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
                field_info: t.GeneralValueType,
            ) -> tuple[type, t.GeneralValueType, bool, bool]:
                """Process field metadata and return type info.

                Returns (field_type, default_value, is_required, has_factory).
                """
                # Use getattr for FieldInfo access - field_info is an object, not always a Mapping
                default_value = (
                    getattr(field_info, "default", None)
                    if field_info is not None
                    else None
                )
                default_factory = (
                    getattr(field_info, "default_factory", None)
                    if field_info is not None
                    else None
                )
                has_factory = default_factory is not None
                # Business Rule: Field requirement MUST be checked only for Pydantic FieldInfo objects
                # Architecture: Use isinstance() to verify field_info is FieldInfo before accessing attributes
                # Audit Implication: Type safety prevents AttributeError on primitive types
                is_required = True
                # Type narrowing: Check if field_info is a Pydantic FieldInfo object
                # Business Rule: Only FieldInfo objects have is_required attribute
                # Architecture: isinstance() check ensures type safety before attribute access
                # Audit Implication: Prevents AttributeError when field_info is primitive type
                # Note: mypy incorrectly flags FieldInfo as subclass of primitives
                # Use getattr for safe access to avoid mypy false positives
                if field_info is not None and isinstance(field_info, FieldInfo):
                    # Type narrowing: field_info is FieldInfo, safe to access is_required
                    # Use getattr to avoid mypy unreachable false positive
                    is_required_attr = getattr(field_info, "is_required", True)
                    # is_required can be bool or callable, handle both cases
                    if callable(is_required_attr):
                        # is_required_attr is a callable - try to invoke it
                        try:
                            is_required = bool(is_required_attr())
                        except TypeError:
                            # If callable doesn't accept no args, treat as bool
                            is_required = bool(is_required_attr)
                    else:
                        # is_required_attr is bool at this point (after callable check)
                        is_required = bool(is_required_attr)

                # Get config default if available
                if self.config is not None and u.has(self.config, field_name):
                    # Use getattr for config access - config is an object, not a Mapping
                    config_value = getattr(self.config, field_name, None)
                    if config_value is not None:
                        default_value = config_value

                # Get and resolve field type
                # Use getattr for FieldInfo access - field_info is an object, not always a Mapping
                field_type_raw = (
                    getattr(field_info, "annotation", None)
                    if field_info is not None
                    else None
                )
                if field_type_raw is None:
                    # No annotation - infer from default value or use str
                    field_type = (
                        type(default_value) if default_value is not None else str
                    )
                elif field_type_raw is object:
                    # object type - infer from default value or use str
                    field_type = (
                        type(default_value) if default_value is not None else str
                    )
                else:
                    # Has annotation - resolve type alias
                    field_type, origin = self._resolve_type_alias(field_type_raw)
                    if origin is not None and field_type is not str:
                        field_type, _ = self._extract_optional_inner_type(field_type)

                # Type narrowing: ensure field_type is a type
                field_type_typed: type = (
                    field_type if isinstance(field_type, type) else str
                )
                return field_type_typed, default_value, is_required, has_factory

            @staticmethod
            def _format_bool_param(
                type_name: str,
                inner_type: type,
                default_val: t.GeneralValueType,
            ) -> tuple[str, t.GeneralValueType]:
                """Format boolean parameter for Typer flag detection."""
                if hasattr(inner_type, "__name__") and inner_type.__name__ == "bool":
                    return "bool", False if default_val is None else default_val
                return type_name, default_val

            def _build_param_signature(
                self,
                name: str,
                type_info: tuple[str, type, t.GeneralValueType, bool, bool],
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
                annotations: dict[str, type],
            ) -> dict[str, type]:
                """Create real type annotations for Typer flag detection."""

                # Use u.process to process annotations
                def process_annotation(_name: str, field_type: type) -> type:
                    origin = get_origin(field_type)
                    is_union = (
                        origin is Union
                        or origin is type(Union)
                        or origin is types.UnionType
                    )
                    if is_union:
                        args = get_args(field_type)
                        # Use u.filter for unified filtering - returns list automatically
                        non_none = list(
                            u.Cli.filter(args, lambda a: a is not type(None))
                        )
                        if non_none and non_none[0] is bool:
                            # Type narrowing: bool | None is a UnionType, not a type
                            # Return bool as the base type (None is handled separately)
                            return bool
                        return field_type
                    return field_type

                # Process annotations using dict comprehension for type safety
                # u.Cli.process() works on iterables, but for dicts we need to process items
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
                model_fields: dict[str, t.GeneralValueType],
            ) -> tuple[dict[str, type], dict[str, t.GeneralValueType], set[str]]:
                """Collect annotations, defaults and factory fields from model fields.

                Returns:
                    Tuple of (annotations, defaults, fields_with_factory)

                """

                # Use u.process_dict to process all fields
                def process_field(
                    field_name: str,
                    field_info: t.GeneralValueType,
                ) -> tuple[type, t.GeneralValueType | None, bool]:
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
                # u.Cli.process() works on iterables, but for dicts we need to process items
                processed_dict: dict[
                    str, tuple[type, t.GeneralValueType | None, bool]
                ] = {
                    field_name: process_field(field_name, field_info)
                    for field_name, field_info in model_fields.items()
                }
                # Build annotations, defaults, and fields_with_factory from processed results
                annotations: dict[str, type] = {}
                defaults: dict[str, t.GeneralValueType] = {}
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
                annotations: dict[str, type],
                defaults: dict[str, t.GeneralValueType],
                fields_with_factory: set[str],
            ) -> str:
                """Build function signature string from field data.

                Returns:
                    Comma-separated parameter signature string

                """

                # Use u.process_dict to process annotations and build signatures
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
                        name, type_info
                    )
                    return param_str, is_no_default

                # Process annotations using dict comprehension for type safety
                # u.Cli.process() works on iterables, but for dicts we need to process items
                signatures_dict: dict[str, tuple[str, bool]] = {
                    name: process_signature(name, field_type)
                    for name, field_type in annotations.items()
                }
                # Separate into two lists using u.filter
                # Use operator.itemgetter(1) to get boolean flag, then check truthiness
                get_bool_flag = operator.itemgetter(1)
                signatures_values = list(signatures_dict.values())
                # u.filter for list accepts predicate(item) -> bool
                # Type narrowing: signatures_values is list[tuple[str, bool]]
                signatures_values_typed: list[tuple[str, bool]] = signatures_values

                def has_no_default(item: tuple[str, bool]) -> bool:
                    """Check if item has no default (is_no_default is True)."""
                    return bool(get_bool_flag(item))

                def has_default(item: tuple[str, bool]) -> bool:
                    """Check if item has default (is_no_default is False)."""
                    return not bool(get_bool_flag(item))

                params_no_default_list = u.Cli.filter(
                    signatures_values_typed,
                    predicate=has_no_default,
                )
                params_with_default_list = u.Cli.filter(
                    signatures_values_typed,
                    predicate=has_default,
                )
                params_no_default = (
                    list(params_no_default_list)
                    if isinstance(params_no_default_list, list)
                    else []
                )
                params_with_default = (
                    list(params_with_default_list)
                    if isinstance(params_with_default_list, list)
                    else []
                )
                # Extract param strings using u.map with operator.itemgetter
                params_no_default_strs_result = u.Cli.map(
                    params_no_default, mapper=operator.itemgetter(0)
                )
                if not isinstance(params_no_default_strs_result, list):
                    msg = "params_no_default_strs_result must be list"
                    raise TypeError(msg)
                params_no_default_strs: list[str] = params_no_default_strs_result
                params_with_default_strs_result = u.Cli.map(
                    params_with_default, mapper=operator.itemgetter(0)
                )
                if not isinstance(params_with_default_strs_result, list):
                    msg = "params_with_default_strs_result must be list"
                    raise TypeError(msg)
                params_with_default_strs: list[str] = params_with_default_strs_result

                return ", ".join(params_no_default_strs + params_with_default_strs)

            def _execute_command_wrapper(
                self,
                sig_parts: str,
                annotations: dict[str, type],
            ) -> Callable[..., t.GeneralValueType]:
                # Callable[..., T] uses ... for variadic args (created dynamically via exec)
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
                exec(func_code, func_globals)  # nosec B102
                command_wrapper = func_globals.get("command_wrapper")
                if command_wrapper is None:
                    msg = "Failed to create command wrapper"
                    raise RuntimeError(msg)

                # Type narrowing: _create_real_annotations returns dict[str, type]
                real_annotations = self._create_real_annotations(annotations)
                command_wrapper.__annotations__ = real_annotations

                if callable(command_wrapper):
                    # command_wrapper is created dynamically via exec, so signature is variadic
                    # Callable[..., T] is necessary for variadic callables
                    # Type narrowing: command_wrapper is callable, return as Callable[..., GeneralValueType]
                    # Runtime validation ensures it matches expected signature
                    # command_wrapper is created dynamically and matches Callable[..., GeneralValueType]
                    if not isinstance(command_wrapper, type) and callable(
                        command_wrapper
                    ):
                        return command_wrapper
                    msg = "command_wrapper must be a callable function"
                    raise TypeError(msg)
                msg = "command_wrapper is not callable"
                raise RuntimeError(msg)

            def build(self) -> Callable[..., t.GeneralValueType]:
                # Callable[..., T] uses ... for variadic args (created dynamically)
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
                default: t.GeneralValueType | None = None,
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
            and Click options, following FLEXT patterns with r railway pattern.
            """

            @staticmethod
            def cli_args_to_model(
                model_cls: type[BaseModel],
                cli_args: Mapping[str, t.GeneralValueType],
            ) -> r[BaseModel]:
                """Convert CLI arguments dict to Pydantic model instance.

                Accepts type[BaseModel] directly to work around pyright limitations
                with PEP 695 generics and local classes in tests. All BaseModel
                subclasses are compatible with type[BaseModel].
                """
                try:
                    # Use direct model_validate instead of from_dict to avoid type variable issues
                    # cli_args is already GeneralValueType compatible
                    # Type narrowing: model_cls is BaseModel subclass (checked by caller)
                    # Convert Mapping to dict for model_validate
                    cli_args_dict: dict[str, t.GeneralValueType] = dict(cli_args)
                    # Type narrowing: model_cls is BaseModel subclass, model_validate exists
                    # Use getattr to access model_validate to satisfy type checker
                    # BaseModel.model_validate exists but mypy needs explicit access
                    if not hasattr(model_cls, "model_validate"):
                        return r.fail(f"{model_cls.__name__} is not a Pydantic model")
                    model_validate_method = model_cls.model_validate
                    model_instance = model_validate_method(cli_args_dict)
                    # model_instance is already BaseModel (or subclass) - no cast needed
                    return r.ok(model_instance)
                except Exception as e:
                    return r.fail(f"Failed to create model instance: {e}")

            @staticmethod
            def model_to_cli_params(
                model_cls: type,
            ) -> r[list[p.Cli.CliParameterSpecProtocol]]:
                """Convert Pydantic model to list of CLI parameter specifications."""
                try:
                    if not hasattr(model_cls, "model_fields"):
                        # Type narrowing: get class name safely for error message
                        class_name = getattr(model_cls, "__name__", str(model_cls))
                        return r[list[p.Cli.CliParameterSpecProtocol]].fail(
                            f"{class_name} is not a Pydantic model",
                        )
                    # Use u.process to convert all fields

                    def convert_field(
                        field_name: str,
                        field_info: t.GeneralValueType,
                    ) -> p.Cli.CliParameterSpecProtocol:
                        """Convert single field to CliParameterSpec."""
                        field_type = getattr(field_info, "annotation", str)
                        # Extract non-None type from Optional/Union
                        origin = get_origin(field_type)
                        if origin is not None:
                            args = get_args(field_type)
                            non_none_types_result = u.Cli.filter(
                                list(args), lambda arg: arg is not type(None)
                            )
                            if not isinstance(non_none_types_result, list):
                                msg = "non_none_types_result must be list"
                                raise TypeError(msg)
                            non_none_types: list[type] = non_none_types_result
                            if non_none_types:
                                field_type = non_none_types[0]
                        default = getattr(field_info, "default", None)
                        help_text = str(getattr(field_info, "description", ""))
                        click_type_str = (
                            m.Cli.CliModelConverter.python_type_to_click_type(
                                field_type,
                            )
                        )
                        return m.Cli.CliParameterSpec(
                            field_name=field_name,
                            param_type=field_type,
                            click_type=click_type_str,
                            default=default,
                            help_text=help_text,
                        )

                    # Process model fields using dict comprehension for type safety
                    # u.Cli.process() works on iterables, but for dicts we need to process items
                    try:
                        params_dict: dict[str, p.Cli.CliParameterSpecProtocol] = {
                            field_name: convert_field(field_name, field_info)
                            for field_name, field_info in model_cls.model_fields.items()
                        }
                        params_list = list(params_dict.values())
                        return r[list[p.Cli.CliParameterSpecProtocol]].ok(params_list)
                    except Exception as e:
                        return r[list[p.Cli.CliParameterSpecProtocol]].fail(
                            f"Conversion failed: {e}",
                        )
                except Exception as e:
                    return r[list[p.Cli.CliParameterSpecProtocol]].fail(
                        f"Conversion failed: {e}",
                    )

            @staticmethod
            def model_to_click_options(
                model_cls: type,
            ) -> r[list[t.GeneralValueType]]:
                """Convert Pydantic model to list of Click options."""
                params_result = m.Cli.CliModelConverter.model_to_cli_params(
                    model_cls,
                )
                if params_result.is_failure:
                    return r[list[t.GeneralValueType]].fail(
                        params_result.error or "Conversion failed",
                    )
                # Extract value from result with default
                params_raw = params_result.value if params_result.is_success else []
                # Type narrowing: params_result.value is list[p.Cli.CliParameterSpecProtocol]
                if not isinstance(params_raw, list):
                    params: list[p.Cli.CliParameterSpecProtocol] = []
                else:
                    # Type narrowing: params_raw is list, check items are CliParameterSpecProtocol
                    params = [
                        item
                        for item in params_raw
                        if isinstance(item, p.Cli.CliParameterSpecProtocol)
                    ]
                # Create Click option-like objects with option_name and param_decls
                # Use simple object with attributes for compatibility with tests
                # Type cast: dynamically created objects are compatible with GeneralValueType
                options: list[t.GeneralValueType] = []
                for param in params:
                    # Type narrowing: param is CliParameterSpecProtocol
                    # Create a simple object with option_name and param_decls attributes
                    option_name = f"--{param.field_name.replace('_', '-')}"
                    # Type narrowing: param_decls list is compatible with GeneralValueType (list is included)
                    param_decls_list: t.GeneralValueType = [option_name]
                    # Type narrowing: param_type (type) - store as string for dict compatibility
                    # type is not in GeneralValueType, so we use string representation
                    param_type_name: str = (
                        getattr(param.param_type, "__name__", "str")
                        if isinstance(param.param_type, type)
                        else "str"
                    )
                    option_obj_dict: dict[str, t.GeneralValueType] = {
                        "option_name": option_name,
                        "param_decls": param_decls_list,
                        "field_name": param.field_name,
                        "param_type": param_type_name,
                        "default": param.default,
                        "help": param.help,  # CliParameterSpec stores as .help, not .help_text
                    }
                    # Type narrowing: dynamically created object is compatible with GeneralValueType
                    option_obj: t.GeneralValueType = type(
                        "ClickOption", (), option_obj_dict
                    )()
                    options.append(option_obj)
                return r[list[t.GeneralValueType]].ok(options)

            @staticmethod
            def field_to_cli_param(
                field_name: str,
                field_info: FieldInfo | t.GeneralValueType,
            ) -> r[p.Cli.CliParameterSpecProtocol]:
                """Convert Pydantic field to CLI parameter specification."""
                try:
                    # Handle both FieldInfo and GeneralValueType
                    if isinstance(field_info, FieldInfo):
                        annotation = field_info.annotation
                        default = (
                            field_info.default
                            if hasattr(field_info, "default")
                            else None
                        )
                        help_text = str(
                            field_info.description
                            if hasattr(field_info, "description")
                            else "",
                        )
                    else:
                        annotation = getattr(field_info, "annotation", None)
                        default = getattr(field_info, "default", None)
                        help_text = str(getattr(field_info, "description", ""))
                    if annotation is None:
                        return r[p.Cli.CliParameterSpecProtocol].fail(
                            f"Field {field_name} has no type annotation",
                        )
                    field_type = annotation
                    # Extract non-None type from Optional/Union
                    origin = get_origin(field_type)
                    if origin is not None:
                        args = get_args(field_type)
                        non_none_types_result = u.Cli.filter(
                            list(args), lambda arg: arg is not type(None)
                        )
                        if not isinstance(non_none_types_result, list):
                            msg = "non_none_types_result must be list"
                            raise TypeError(msg)
                        non_none_types: list[type] = non_none_types_result
                        if non_none_types:
                            field_type = non_none_types[0]
                    click_type_str = m.Cli.CliModelConverter.python_type_to_click_type(
                        field_type,
                    )
                    # Return concrete instance
                    return r[p.Cli.CliParameterSpecProtocol].ok(
                        m.Cli.CliParameterSpec(
                            field_name=field_name,
                            param_type=field_type,
                            click_type=click_type_str,
                            default=default,
                            help_text=help_text,
                        ),
                    )
                except Exception as e:
                    return r[p.Cli.CliParameterSpecProtocol].fail(
                        f"Field conversion failed: {e}",
                    )

            @staticmethod
            def handle_union_type(pydantic_type: types.UnionType) -> type:
                """Handle UnionType (e.g., int | None) and extract non-None type."""
                args = get_args(pydantic_type)
                non_none_types_result = u.Cli.filter(
                    list(args), lambda arg: arg is not type(None)
                )
                if not isinstance(non_none_types_result, list):
                    msg = "non_none_types_result must be list"
                    raise TypeError(msg)
                non_none_types: list[type] = non_none_types_result
                if non_none_types:
                    result_type = non_none_types[0]
                    if isinstance(result_type, type):
                        return result_type
                return str  # Fallback

            @staticmethod
            def handle_generic_type(pydantic_type: object) -> type | None:
                """Handle generic types like list[str], dict[str, str]. Returns None if not handled."""
                origin = get_origin(pydantic_type)
                if origin is None:
                    return None
                # For generic types like list[str], dict[str, str], return the origin
                if isinstance(origin, type) and origin in {list, dict}:
                    return origin
                # Extract first type argument
                args = get_args(pydantic_type)
                non_none_types_result = u.Cli.filter(
                    list(args), lambda arg: arg is not type(None)
                )
                if not isinstance(non_none_types_result, list):
                    msg = "non_none_types_result must be list"
                    raise TypeError(msg)
                non_none_types: list[type] = non_none_types_result
                if non_none_types:
                    first_type = non_none_types[0]
                    if isinstance(first_type, type):
                        return first_type
                    return first_type
                return None

            @staticmethod
            def is_simple_type(pydantic_type: type | object) -> bool:
                """Check if it's a known simple type."""
                return isinstance(pydantic_type, type) and pydantic_type in {
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
                if isinstance(pydantic_type, types.UnionType):
                    return m.Cli.CliModelConverter.handle_union_type(pydantic_type)
                # Handle generic types like list[str], dict[str, str]
                generic_result = m.Cli.CliModelConverter.handle_generic_type(
                    pydantic_type
                )
                if generic_result is not None:
                    return generic_result
                # Check if it's a known simple type
                if m.Cli.CliModelConverter.is_simple_type(pydantic_type):
                    return pydantic_type  # type: ignore[return-value]
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
                field_info: FieldInfo | t.GeneralValueType,
            ) -> dict[str, t.GeneralValueType]:
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
                props: dict[str, t.GeneralValueType],
                types: Mapping[str, type | str],
            ) -> None:
                """Merge types mapping into properties dict."""
                if isinstance(types, dict):
                    # Use dict comprehension for type conversion - direct and type-safe
                    transformed: dict[str, t.GeneralValueType] = {
                        k: str(v) for k, v in types.items()
                    }
                    props.update(transformed)

            @staticmethod
            def merge_field_info_dict(
                props: dict[str, t.GeneralValueType],
                field_info: FieldInfo | t.GeneralValueType,
            ) -> None:
                """Merge field_info dict attributes into props."""
                if isinstance(field_info, dict):
                    # Use dict comprehension to exclude "__dict__" for type safety
                    filtered: dict[str, t.GeneralValueType] = {
                        k: v for k, v in dict(field_info).items() if k != "__dict__"
                    }
                    props.update(filtered)
                elif hasattr(field_info, "__dict__"):
                    metadata_dict = getattr(field_info, "__dict__", {})
                    if isinstance(metadata_dict, dict):
                        props.update(dict(metadata_dict.items()))

            @staticmethod
            def process_metadata_list(
                metadata_attr: list[object],
            ) -> dict[str, t.GeneralValueType]:
                """Process metadata list into dict."""
                result: dict[str, t.GeneralValueType] = {}
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
                props: dict[str, t.GeneralValueType],
                field_info: FieldInfo | t.GeneralValueType,
            ) -> None:
                """Merge metadata attribute into props."""
                if not hasattr(field_info, "metadata"):
                    return
                metadata_attr = getattr(field_info, "metadata", None)
                if metadata_attr is None:
                    return
                if isinstance(metadata_attr, list):
                    props["metadata"] = m.Cli.CliModelConverter.process_metadata_list(
                        metadata_attr,
                    )
                elif isinstance(metadata_attr, dict):
                    props["metadata"] = metadata_attr

            @staticmethod
            def merge_json_schema_extra(
                props: dict[str, t.GeneralValueType],
                field_info: FieldInfo | t.GeneralValueType,
            ) -> None:
                """Merge json_schema_extra into props metadata."""
                if not hasattr(field_info, "json_schema_extra"):
                    return
                json_schema_extra = getattr(field_info, "json_schema_extra", None)
                if json_schema_extra is None:
                    return
                # Use dict.get() for safe metadata access
                metadata_raw = props.get("metadata")
                if not metadata_raw:
                    props["metadata"] = {}
                # Use FlextRuntime.is_dict_like for type checking
                if FlextRuntime.is_dict_like(
                    metadata_raw
                ) and FlextRuntime.is_dict_like(
                    json_schema_extra,
                ):
                    # Type narrowing: both are dict-like, safe to update
                    if not isinstance(metadata_raw, dict):
                        msg = "metadata_raw must be dict"
                        raise TypeError(msg)
                    dict_metadata: dict[str, t.GeneralValueType] = metadata_raw
                    if not isinstance(json_schema_extra, dict):
                        msg = "json_schema_extra must be dict"
                        raise TypeError(msg)
                    dict_schema: dict[str, t.GeneralValueType] = json_schema_extra
                    dict_metadata.update(dict_schema)
                    props["metadata"] = dict_metadata

            @staticmethod
            def extract_field_properties(
                field_name: str,
                field_info: FieldInfo | t.GeneralValueType,
                types: Mapping[str, type | str] | None = None,
            ) -> r[dict[str, t.GeneralValueType]]:
                """Extract properties from Pydantic field info."""
                try:
                    props = m.Cli.CliModelConverter.extract_base_props(
                        field_name,
                        field_info,
                    )
                    if types is not None:
                        m.Cli.CliModelConverter.merge_types_into_props(
                            props,
                            types,
                        )
                        m.Cli.CliModelConverter.merge_field_info_dict(
                            props,
                            field_info,
                        )
                        m.Cli.CliModelConverter.merge_metadata_attr(
                            props,
                            field_info,
                        )
                        m.Cli.CliModelConverter.merge_json_schema_extra(
                            props,
                            field_info,
                        )
                    return r[dict[str, t.GeneralValueType]].ok(props)
                except Exception as e:
                    return r[dict[str, t.GeneralValueType]].fail(
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
            ) -> r[bool]:
                """Validate field data schema against rules."""
                for (
                    field_key,
                    type_name,
                    check_func,
                ) in m.Cli.CliModelConverter.FIELD_VALIDATION_RULES:
                    if field_key in field_data:
                        value = field_data[field_key]
                        if not check_func(value):
                            return r[bool].fail(
                                f"Invalid {field_key}: {value} (expected {type_name})",
                            )
                return r[bool].ok(True)

            @staticmethod
            def convert_field_value(
                field_value: object,
            ) -> r[t.GeneralValueType]:
                """Convert field value (delegates to utilities)."""
                return u.Cli.CliValidation.v_conv(field_value)

            @staticmethod
            def validate_dict_field_data(
                field_name: str,
                field_data: Mapping[str, object],
            ) -> r[t.GeneralValueType]:
                """Validate field data when field_info is a dict/Mapping."""
                schema_result = m.Cli.CliModelConverter.validate_field_schema(
                    field_data,
                )
                if schema_result.is_failure:
                    return r[t.GeneralValueType].fail(
                        schema_result.error or "Schema validation failed",
                    )
                field_value = field_data.get(field_name, None)
                return m.Cli.CliModelConverter.convert_field_value(field_value)

            @staticmethod
            def _validate_field_data(
                field_name: str,
                field_info: FieldInfo
                | t.GeneralValueType
                | Mapping[str, t.GeneralValueType]
                | dict[str, object]
                | dict[str, type | str | bool | list[object] | dict[str, object]],
                data: Mapping[str, t.GeneralValueType] | None = None,
            ) -> r[t.GeneralValueType]:
                """Validate field data against field info."""
                try:
                    if isinstance(field_info, (dict, Mapping)):
                        return m.Cli.CliModelConverter.validate_dict_field_data(
                            field_name,
                            field_info,
                        )
                    if data is not None:
                        if field_name not in data:
                            return r[t.GeneralValueType].fail(
                                f"Field {field_name} not found",
                            )
                        return r[t.GeneralValueType].ok(data[field_name])
                    return r[t.GeneralValueType].fail("No data provided for validation")
                except Exception as e:
                    return r[t.GeneralValueType].fail(f"Validation failed: {e}")

            @staticmethod
            def _process_validators(
                field_info: Sequence[Callable[[t.GeneralValueType], t.GeneralValueType]]
                | Sequence[object]
                | t.GeneralValueType,
            ) -> list[Callable[[t.GeneralValueType], t.GeneralValueType]]:
                """Process validators from field info, filtering only callable validators."""
                if not isinstance(field_info, (list, tuple, Sequence)):
                    return []
                validators: list[
                    Callable[[t.GeneralValueType], t.GeneralValueType]
                ] = []
                for item in field_info:
                    if callable(item):
                        # Type narrowing: item is callable, cast to proper validator type
                        # Type narrowing: validators may have different signatures
                        if not callable(item):
                            msg = "item must be callable"
                            raise TypeError(msg)
                        validator: Callable[
                            [t.GeneralValueType], t.GeneralValueType
                        ] = item
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
                        r[t.GeneralValueType] | r[object] | t.GeneralValueType,
                    ],
                ],
                Callable[..., t.GeneralValueType],
            ]:
                # Callable[..., T] uses ... for variadic args (CLI commands accept *args, **kwargs)
                """Create decorator that converts function to CLI command from model."""

                def decorator(
                    func: Callable[
                        [BaseModel],
                        r[t.GeneralValueType] | r[object] | t.GeneralValueType,
                    ],
                ) -> Callable[..., t.GeneralValueType]:
                    # Callable[..., T] uses ... for variadic args (CLI commands accept *args, **kwargs)
                    def wrapper(
                        *_args: t.GeneralValueType,
                        **kwargs: t.GeneralValueType,
                    ) -> t.GeneralValueType:
                        try:
                            # Create model instance from kwargs
                            model_instance = model_class(**kwargs)
                            # Call original function with model
                            result = func(model_instance)
                            # Convert result to GeneralValueType if needed
                            output: t.GeneralValueType
                            if isinstance(result, r):
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
                [Callable[..., t.GeneralValueType]],
                Callable[..., t.GeneralValueType],
            ]:
                # Callable[..., T] uses ... for variadic args (CLI commands accept *args, **kwargs)
                """Create decorator for multiple models."""

                def decorator(
                    func: Callable[..., t.GeneralValueType],
                ) -> Callable[..., t.GeneralValueType]:
                    # Callable[..., T] uses ... for variadic args (CLI commands accept *args, **kwargs)
                    def wrapper(
                        *_args: t.GeneralValueType,
                        **kwargs: t.GeneralValueType,
                    ) -> t.GeneralValueType:
                        try:
                            # Create model instances from kwargs (simplified)
                            models = [
                                model_cls(**kwargs) for model_cls in model_classes
                            ]
                            return func(*models)
                        except Exception as e:
                            return f"Validation failed: {e}"

                    return wrapper

                return decorator

        class LoggingConfig(Value):
            """Logging configuration model.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            log_level: str = Field(default="INFO", description="Log level")
            log_format: str = Field(default="", description="Log format string")
            console_output: bool = Field(
                default=True, description="Enable console output"
            )
            log_file: str = Field(default="", description="Log file path")

            @property
            def logging_summary(self) -> m.Cli.CliLoggingData:
                """Return logging summary as CliLoggingData model."""
                return m.Cli.CliLoggingData(
                    level=self.log_level,
                    console_enabled=self.console_output,
                )

        class CliLoggingData(Value):
            """CLI logging summary data.

            Inherits frozen=True and extra="forbid" from FlextModels.Value.
            """

            level: str = Field(default="INFO", description="Log level")
            console_enabled: bool = Field(
                default=True,
                description="Console output enabled",
            )

        class CliDebugData(Value):
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

            # Reference protocol types (p.Cli.Display.*)
            type RichTable = p.Cli.Display.RichTableProtocol
            type RichTree = p.Cli.Display.RichTreeProtocol
            type Console = p.Cli.Display.RichConsoleProtocol

        class Interactive:
            """Interactive display type aliases using Protocols.

            These type aliases reference protocol types from flext_cli.protocols.
            Located in Tier 1 (models.py) to allow protocol imports.
            """

            # Reference protocol types (p.Cli.Interactive.*)
            type Progress = p.Cli.Interactive.RichProgressProtocol


# Use namespace completo (m.Cli.*) para acesso explícito
# Use m.Cli.TableConfig for explicit namespace access
# Use m.Cli.TableConfig for explicit namespace access

m = FlextCliModels
m_cli = FlextCliModels

__all__ = [
    "FlextCliModels",
    "m",
    "m_cli",
]
