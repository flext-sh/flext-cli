"""FLEXT CLI Models - CLI domain models leveraging flext_core models.

Keep this thin; prefer using flext_core.FlextModels directly when possible.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, ClassVar
from uuid import uuid4

from flext_core import FlextModels, FlextResult
from pydantic import Field, computed_field, field_validator

from flext_cli.constants import FlextCliConstants


class FlextCliModels:
    """CLI-specific models extending flext_core FlextModels."""

    Core: ClassVar[type[FlextModels]] = FlextModels

    class CliCommand(FlextModels.Entity):
        """CLI command model."""

        if TYPE_CHECKING:
            # Typing-only constructor for static analyzers
            def __init__(self, *, command_line: str, **kwargs: object) -> None: ...

        id: str = Field(default_factory=lambda: str(uuid4()))
        command_line: str = Field(...)
        execution_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
        status: str = Field(default=FlextCliConstants.STATUS_PENDING)
        exit_code: int | None = None
        output: str = ""
        error_output: str = ""

        @computed_field
        def is_successful(self) -> bool:
            return self.status == FlextCliConstants.STATUS_COMPLETED and (
                self.exit_code is None or self.exit_code == 0
            )

        @field_validator("status")
        @classmethod
        def validate_status(cls, v: str) -> str:
            if v not in FlextCliConstants.VALID_COMMAND_STATUSES:
                msg = (
                    f"Status must be one of: {FlextCliConstants.VALID_COMMAND_STATUSES}"
                )
                raise ValueError(msg)
            return v

        def start_execution(self) -> FlextResult[None]:
            """Start the execution of the command."""
            self.status = FlextCliConstants.STATUS_RUNNING
            self.execution_time = datetime.now(UTC)
            return FlextResult[None].ok(None)

        def complete_execution(
            self, exit_code: int, output: str = "", error_output: str = ""
        ) -> FlextResult[None]:
            self.status = (
                FlextCliConstants.STATUS_COMPLETED
                if exit_code == 0
                else FlextCliConstants.STATUS_FAILED
            )
            self.exit_code = exit_code
            self.output = output
            self.error_output = error_output
            return FlextResult[None].ok(None)

        def validate_business_rules(self) -> FlextResult[None]:
            if not self.command_line.strip():
                return FlextResult[None].fail("Command line cannot be empty")
            if self.status not in FlextCliConstants.VALID_COMMAND_STATUSES:
                return FlextResult[None].fail(f"Invalid status: {self.status}")
            if (
                self.status
                in {FlextCliConstants.STATUS_COMPLETED, FlextCliConstants.STATUS_FAILED}
                and self.exit_code is None
            ):
                return FlextResult[None].fail(
                    "Exit code required for completed/failed commands"
                )
            return FlextResult[None].ok(None)

    class CliSession(FlextModels):
        """CLI session model."""

        if TYPE_CHECKING:
            # Typing-only constructor for static analyzers
            def __init__(
                self, *, user_id: str | None = None, **kwargs: object
            ) -> None: ...

        id: str = Field(default_factory=lambda: str(uuid4()))
        session_id: str = Field(default_factory=lambda: str(uuid4()))
        start_time: datetime = Field(default_factory=datetime.now)
        end_time: datetime | None = None
        commands: list[FlextCliModels.CliCommand] = Field(default_factory=list)
        user_id: str | None = None

        @computed_field
        def duration_seconds(self) -> float | None:
            if self.end_time is None:
                return None
            return (self.end_time - self.start_time).total_seconds()

        def add_command(self, command: FlextCliModels.CliCommand) -> FlextResult[None]:
            """Add a command to the session."""
            self.commands.append(command)
            return FlextResult[None].ok(None)

        def end_session(self) -> FlextResult[None]:
            """End the session."""
            self.end_time = datetime.now(UTC)
            return FlextResult[None].ok(None)

        def validate_business_rules(self) -> FlextResult[None]:
            if self.end_time is not None and self.end_time < self.start_time:
                return FlextResult[None].fail("End time cannot be before start time")
            if len(self.commands) > FlextCliConstants.MAX_COMMANDS_PER_SESSION:
                return FlextResult[None].fail(
                    f"Session has too many commands (limit: {FlextCliConstants.MAX_COMMANDS_PER_SESSION})"
                )
            for cmd in self.commands:
                validation_result = cmd.validate_business_rules()
                if validation_result.is_failure:
                    return FlextResult[None].fail(
                        f"Invalid command in session: {validation_result.error}"
                    )
            return FlextResult[None].ok(None)

    class CliConfig(FlextModels.Value):
        """CLI configuration model."""

        profile: str = Field(default=FlextCliConstants.DEFAULT_PROFILE)
        output_format: str = Field(default=FlextCliConstants.DEFAULT_OUTPUT_FORMAT)
        debug_mode: bool = Field(default=False)
        timeout_seconds: int = Field(default=FlextCliConstants.DEFAULT_COMMAND_TIMEOUT)

        @field_validator("output_format")
        @classmethod
        def validate_output_format(cls, v: str) -> str:
            if v not in FlextCliConstants.VALID_OUTPUT_FORMATS:
                msg = f"Output format must be one of: {FlextCliConstants.VALID_OUTPUT_FORMATS}"
                raise ValueError(msg)
            return v

        @field_validator("timeout_seconds")
        @classmethod
        def validate_timeout(cls, v: int) -> int:
            if v <= 0 or v > FlextCliConstants.MAX_TIMEOUT_SECONDS:
                msg = f"Timeout must be between 1 and {FlextCliConstants.MAX_TIMEOUT_SECONDS} seconds"
                raise ValueError(msg)
            return v


__all__ = ["FlextCliModels"]
