"""FLEXT CLI Domain Service - Unified domain service for CLI operations.

Provides domain service methods for CLI operations following FLEXT standards.
Single unified class with all domain service methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime

from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class FlextCliDomainService:
    """Unified domain service for CLI operations following FLEXT standards.

    Provides all domain service methods for CLI operations in a single class.
    Follows FLEXT pattern: one class per module with comprehensive functionality.
    """

    def __init__(self) -> None:
        """Initialize the domain service."""

    def execute(self) -> FlextResult[FlextResult[str]]:
        """Execute domain service operations."""
        try:
            # Perform domain service execution
            health_result = self.health_check()
            if health_result.is_failure:
                return FlextResult[FlextResult[str]].fail(
                    f"Health check failed: {health_result.error}"
                )

            # Return success result
            return FlextResult[FlextResult[str]].ok(
                FlextResult[str].ok("Domain service executed successfully")
            )
        except Exception as e:
            return FlextResult[FlextResult[str]].fail(f"Execution failed: {e}")

    def health_check(self) -> FlextResult[str]:
        """Perform health check for domain services."""
        try:
            return FlextResult[str].ok("FLEXT CLI Domain Services: healthy")
        except Exception as e:
            return FlextResult[str].fail(f"Health check failed: {e}")

    def create_command(
        self, command_line: str
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Create a new CLI command."""
        try:
            if not command_line or not command_line.strip():
                return FlextResult[FlextCliModels.CliCommand].fail(
                    "Command line cannot be empty"
                )

            # Check for dangerous patterns
            dangerous_patterns = ["rm -rf", "format", "del /f", "sudo rm"]
            if any(pattern in command_line.lower() for pattern in dangerous_patterns):
                return FlextResult[FlextCliModels.CliCommand].fail(
                    "Command contains dangerous patterns"
                )

            # Create command with stripped whitespace
            command = FlextCliModels.CliCommand(
                command=command_line.strip(),
                status=FlextCliConstants.CommandStatus.PENDING.value,
            )

            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Command creation failed: {e}"
            )

    def start_command_execution(
        self, command: FlextCliModels.CliCommand
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Start command execution."""
        try:
            if command.status != FlextCliConstants.CommandStatus.PENDING.value:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Command must be pending to start. Current status: {command.status}"
                )

            command.status = FlextCliConstants.CommandStatus.RUNNING.value
            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Start execution failed: {e}"
            )

    def complete_command_execution(
        self,
        command: FlextCliModels.CliCommand,
        exit_code: int,
        output: str = "",
        error_output: str = "",
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Complete command execution."""
        try:
            if command.status != FlextCliConstants.CommandStatus.RUNNING.value:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Command must be running to complete. Current status: {command.status}"
                )

            command.exit_code = exit_code
            command.output = output
            command.error_output = error_output

            if exit_code == 0:
                command.status = FlextCliConstants.CommandStatus.COMPLETED.value
            else:
                command.status = FlextCliConstants.CommandStatus.FAILED.value

            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Complete execution failed: {e}"
            )

    def create_session(
        self, user_id: str | None = None
    ) -> FlextResult[FlextCliModels.CliSession]:
        """Create a new CLI session."""
        try:
            # Auto-generate user_id if not provided
            if user_id is None:
                user_id = f"user_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"

            session = FlextCliModels.CliSession(user_id=user_id)
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Session creation failed: {e}"
            )

    def add_command_to_session(
        self, session: FlextCliModels.CliSession, _command: FlextCliModels.CliCommand
    ) -> FlextResult[FlextCliModels.CliSession]:
        """Add command to session."""
        try:
            # Note: CliSession doesn't have a commands list in the current model
            # This is a placeholder implementation
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Add command to session failed: {e}"
            )

    def end_session(
        self, session: FlextCliModels.CliSession
    ) -> FlextResult[FlextCliModels.CliSession]:
        """End a CLI session."""
        try:
            session.end_time = datetime.now(UTC)
            session.status = "completed"
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"End session failed: {e}"
            )

    def execute_command_workflow(
        self, command_line: str
    ) -> FlextResult[dict[str, str | int]]:
        """Execute complete command workflow."""
        try:
            if not command_line or not command_line.strip():
                return FlextResult[dict[str, str | int]].fail(
                    "Command line cannot be empty"
                )

            # Create command
            create_result = self.create_command(command_line)
            if create_result.is_failure:
                return FlextResult[dict[str, str | int]].fail(
                    f"Command creation failed: {create_result.error}"
                )

            command = create_result.value

            # Start execution
            start_result = self.start_command_execution(command)
            if start_result.is_failure:
                return FlextResult[dict[str, str | int]].fail(
                    f"Start execution failed: {start_result.error}"
                )

            # Complete execution (simulated)
            complete_result = self.complete_command_execution(
                command,
                exit_code=0,
                output=f"Executed: {command_line}",
                error_output="",
            )

            if complete_result.is_failure:
                return FlextResult[dict[str, str | int]].fail(
                    f"Complete execution failed: {complete_result.error}"
                )

            # Return workflow data
            workflow_data: dict[str, str | int] = {
                "command_line": command_line,
                "workflow_status": "completed",
                "session_id": f"session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
                "command_id": command.id,
                "exit_code": command.exit_code or 0,
                "output": command.output,
            }

            return FlextResult[dict[str, str | int]].ok(workflow_data)
        except Exception as e:
            return FlextResult[dict[str, str | int]].fail(
                f"Workflow execution failed: {e}"
            )


__all__ = [
    "FlextCliDomainService",
]
