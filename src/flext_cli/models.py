"""FLEXT CLI Models - Advanced CLI domain models using FlextModels unified patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import ClassVar
from uuid import uuid4

from flext_core import FlextModels, FlextResult
from pydantic import Field, computed_field, field_validator


class FlextCliModels(FlextModels):
    """Advanced CLI-specific models using FlextModels unified patterns.

    Leverages FlextModels.Entity, FlextModels.AggregateRoot, and FlextModels.BaseConfig
    for enterprise-grade CLI domain modeling with Python 3.13+ features.
    """

    # Reference to flext-core models for strict inheritance
    Core: ClassVar = FlextModels

    class CliCommand(FlextModels.Entity):
        """CLI command entity using FlextModels.Entity pattern."""

        id: str = Field(default_factory=lambda: str(uuid4()), description="Unique command identifier")
        command_line: str = Field(..., description="Full command line string")
        execution_time: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Command execution timestamp")
        status: str = Field(default="PENDING", description="Command execution status")
        exit_code: int | None = Field(None, description="Command exit code")
        output: str = Field(default="", description="Command output")
        error_output: str = Field(default="", description="Command error output")

        @computed_field
        def is_successful(self) -> bool:
            """Computed field for command success status."""
            return self.status == "COMPLETED" and (self.exit_code is None or self.exit_code == 0)

        @field_validator("status")
        @classmethod
        def validate_status(cls, v: str) -> str:
            """Validate command status using Python 3.13+ patterns."""
            valid_statuses = {"PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"}
            if v not in valid_statuses:
                msg = f"Status must be one of: {valid_statuses}"
                raise ValueError(msg)
            return v

        def start_execution(self) -> FlextResult[None]:
            """Start command execution using FlextResult pattern."""
            self.status = "RUNNING"
            self.execution_time = datetime.now(UTC)
            return FlextResult[None].ok(None)

        def complete_execution(self, exit_code: int, output: str = "", error_output: str = "") -> FlextResult[None]:
            """Complete command execution with results."""
            self.status = "COMPLETED" if exit_code == 0 else "FAILED"
            self.exit_code = exit_code
            self.output = output
            self.error_output = error_output
            return FlextResult[None].ok(None)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate CLI command business rules."""
            if not self.command_line.strip():
                return FlextResult[None].fail("Command line cannot be empty")

            if self.status not in {"PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"}:
                return FlextResult[None].fail(f"Invalid status: {self.status}")

            if self.status in {"COMPLETED", "FAILED"} and self.exit_code is None:
                return FlextResult[None].fail("Exit code required for completed/failed commands")

            return FlextResult[None].ok(None)

    class CliSession(FlextModels.AggregateRoot):
        """CLI session aggregate using FlextModels.AggregateRoot pattern."""

        id: str = Field(default_factory=lambda: str(uuid4()), description="Unique session identifier")
        session_id: str = Field(default_factory=lambda: str(uuid4()), description="Session identifier (alias for compatibility)")
        start_time: datetime = Field(default_factory=datetime.now, description="Session start time")
        end_time: datetime | None = Field(None, description="Session end time")
        commands: list[FlextCliModels.CliCommand] = Field(default_factory=list, description="Commands executed in session")
        user_id: str | None = Field(None, description="Associated user ID")

        @computed_field
        def duration_seconds(self) -> float | None:
            """Computed session duration in seconds."""
            if self.end_time is None:
                return None
            return (self.end_time - self.start_time).total_seconds()

        def add_command(self, command: FlextCliModels.CliCommand) -> FlextResult[None]:
            """Add command to session using domain event pattern."""
            self.commands.append(command)
            self.add_domain_event({
                "event_type": "command_added",
                "session_id": str(self.session_id),
                "command_id": str(command.id),
                "timestamp": datetime.now(UTC).isoformat()
            })
            return FlextResult[None].ok(None)

        def end_session(self) -> FlextResult[None]:
            """End the CLI session."""
            self.end_time = datetime.now(UTC)
            self.add_domain_event({
                "event_type": "session_ended",
                "session_id": str(self.session_id),
                "duration": (
                    (self.end_time - self.start_time).total_seconds() if self.end_time is not None else None
                ),
                "commands_count": len(self.commands),
                "timestamp": self.end_time.isoformat()
            })
            return FlextResult[None].ok(None)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate CLI session business rules."""
            if self.end_time is not None and self.end_time < self.start_time:
                return FlextResult[None].fail("End time cannot be before start time")

            if len(self.commands) > 10000:  # Reasonable limit
                return FlextResult[None].fail("Session has too many commands (limit: 10000)")

            # Validate all commands in session
            for cmd in self.commands:
                validation_result = cmd.validate_business_rules()
                if validation_result.is_failure:
                    return FlextResult[None].fail(f"Invalid command in session: {validation_result.error}")

            return FlextResult[None].ok(None)

    class CliConfig(FlextModels.BaseConfig):
        """CLI configuration using FlextModels.BaseConfig pattern."""

        profile: str = Field(default="default", description="Configuration profile")
        output_format: str = Field(default="table", description="Default output format")
        debug_mode: bool = Field(default=False, description="Enable debug mode")
        timeout_seconds: int = Field(default=30, description="Command timeout in seconds")

        @field_validator("output_format")
        @classmethod
        def validate_output_format(cls, v: str) -> str:
            """Validate output format using Python 3.13+ patterns."""
            valid_formats = {"table", "json", "yaml", "csv"}
            if v not in valid_formats:
                msg = f"Output format must be one of: {valid_formats}"
                raise ValueError(msg)
            return v

        @field_validator("timeout_seconds")
        @classmethod
        def validate_timeout(cls, v: int) -> int:
            """Validate timeout value."""
            if v <= 0 or v > 3600:
                msg = "Timeout must be between 1 and 3600 seconds"
                raise ValueError(msg)
            return v


# =============================================================================
# EXPORTS - Single unique class following user requirements
# =============================================================================

__all__ = [
    "FlextCliModels",
]
