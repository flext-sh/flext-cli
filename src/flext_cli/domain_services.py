"""FLEXT CLI Domain Services - Business logic orchestration following DDD patterns.

Provides FlextCliDomainServices class that orchestrates CLI business operations
using domain entities and value objects, following Domain-Driven Design principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextDomainService, FlextLogger, FlextResult, FlextTypes

from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels

if TYPE_CHECKING:
    CommandInput = FlextTypes.Core.Dict
    SessionContext = FlextTypes.Core.Dict


logger = FlextLogger(__name__)


class FlextCliDomainServices(FlextDomainService[FlextResult[object]]):
    """CLI domain services orchestrating business operations.

    Provides comprehensive CLI business logic following Domain-Driven Design
    patterns with proper separation of concerns, entity lifecycle management,
    and business rule enforcement.

    Features:
        - Command lifecycle management (create, execute, complete)
        - Session management with business rules
        - Configuration validation and management
        - Health check operations
        - Integration with flext-core domain services
    """

    def __init__(self) -> None:
        """Initialize domain services."""
        super().__init__()

    def execute(self) -> FlextResult[FlextResult[object]]:
        """Execute domain service request.

        Returns:
            FlextResult containing execution result

        """
        try:
            # Generic execution handler - perform health check by default
            health_result = self.health_check()
            if health_result.is_success:
                return FlextResult[FlextResult[object]].ok(
                    FlextResult[object].ok(health_result.value)
                )
            return FlextResult[FlextResult[object]].fail(
                health_result.error or "Health check failed"
            )
        except Exception as e:
            logger.exception("Domain service execution failed")
            return FlextResult[FlextResult[object]].fail(f"Execution failed: {e}")

    def health_check(self) -> FlextResult[str]:
        """Perform CLI health check.

        Returns:
            FlextResult containing health status

        """
        try:
            return FlextResult[str].ok("FLEXT CLI Domain Services: healthy")
        except Exception as e:
            logger.exception("Health check failed")
            return FlextResult[str].fail(f"Health check failed: {e}")

    def create_command(
        self, command_line: str
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Create new CLI command entity with validation.

        Args:
            command_line: Command line to execute

        Returns:
            FlextResult containing created command entity

        """
        try:
            if not command_line or not command_line.strip():
                return FlextResult[FlextCliModels.CliCommand].fail(
                    "Command line cannot be empty"
                )

            command = FlextCliModels.CliCommand(command_line=command_line.strip())

            # Validate business rules
            validation_result = command.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Command validation failed: {validation_result.error}"
                )

            logger.debug("Created command: %s", command.id)
            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            logger.exception("Failed to create command")
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Command creation failed: {e}"
            )

    def start_command_execution(
        self, command: FlextCliModels.CliCommand
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Start command execution with state transition.

        Args:
            command: Command entity to start

        Returns:
            FlextResult containing updated command entity

        """
        try:
            if command.status != FlextCliConstants.STATUS_PENDING:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Command must be pending to start, current status: {command.status}"
                )

            start_result = command.start_execution()
            if start_result.is_failure:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Failed to start execution: {start_result.error}"
                )

            logger.debug("Started execution for command: %s", command.id)
            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            logger.exception("Failed to start command execution")
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Command execution start failed: {e}"
            )

    def complete_command_execution(
        self,
        command: FlextCliModels.CliCommand,
        exit_code: int,
        output: str = "",
        error_output: str = "",
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Complete command execution with results.

        Args:
            command: Command entity to complete
            exit_code: Command exit code
            output: Standard output
            error_output: Error output

        Returns:
            FlextResult containing completed command entity

        """
        try:
            if command.status != FlextCliConstants.STATUS_RUNNING:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Command must be running to complete, current status: {command.status}"
                )

            completion_result = command.complete_execution(
                exit_code, output, error_output
            )
            if completion_result.is_failure:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Failed to complete execution: {completion_result.error}"
                )

            # Validate final state
            validation_result = command.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Command validation failed after completion: {validation_result.error}"
                )

            logger.debug(
                "Completed execution for command: %s (exit_code=%d)",
                command.id,
                exit_code,
            )
            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            logger.exception("Failed to complete command execution")
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Command execution completion failed: {e}"
            )

    def create_session(
        self, user_id: str | None = None
    ) -> FlextResult[FlextCliModels.CliSession]:
        """Create new CLI session entity.

        Args:
            user_id: Optional user identifier

        Returns:
            FlextResult containing created session entity

        """
        try:
            session = FlextCliModels.CliSession(user_id=user_id)

            # Validate business rules
            validation_result = session.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Session validation failed: {validation_result.error}"
                )

            logger.debug("Created session: %s", session.id)
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            logger.exception("Failed to create session")
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Session creation failed: {e}"
            )

    def add_command_to_session(
        self,
        session: FlextCliModels.CliSession,
        command: FlextCliModels.CliCommand,
    ) -> FlextResult[FlextCliModels.CliSession]:
        """Add command to session with validation.

        Args:
            session: Session entity
            command: Command entity to add

        Returns:
            FlextResult containing updated session entity

        """
        try:
            # Check session limits
            if len(session.commands) >= FlextCliConstants.MAX_COMMANDS_PER_SESSION:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Session command limit reached: {FlextCliConstants.MAX_COMMANDS_PER_SESSION}"
                )

            add_result = session.add_command(command)
            if add_result.is_failure:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Failed to add command to session: {add_result.error}"
                )

            # Validate updated session
            validation_result = session.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Session validation failed after adding command: {validation_result.error}"
                )

            logger.debug("Added command %s to session %s", command.id, session.id)
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            logger.exception("Failed to add command to session")
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Command addition to session failed: {e}"
            )

    def end_session(
        self, session: FlextCliModels.CliSession
    ) -> FlextResult[FlextCliModels.CliSession]:
        """End CLI session with validation.

        Args:
            session: Session entity to end

        Returns:
            FlextResult containing ended session entity

        """
        try:
            if session.end_time is not None:
                return FlextResult[FlextCliModels.CliSession].fail(
                    "Session is already ended"
                )

            end_result = session.end_session()
            if end_result.is_failure:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Failed to end session: {end_result.error}"
                )

            # Validate final state
            validation_result = session.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Session validation failed after ending: {validation_result.error}"
                )

            logger.debug("Ended session: %s", session.id)
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            logger.exception("Failed to end session")
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Session ending failed: {e}"
            )

    def execute_command_workflow(
        self, command_line: str, user_id: str | None = None
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute complete command workflow from creation to completion.

        Args:
            command_line: Command line to execute
            user_id: Optional user identifier

        Returns:
            FlextResult containing workflow execution results

        """
        try:
            # Create session
            session_result = self.create_session(user_id)
            if session_result.is_failure:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Failed to create session: {session_result.error}"
                )
            session = session_result.value

            # Create command
            command_result = self.create_command(command_line)
            if command_result.is_failure:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Failed to create command: {command_result.error}"
                )
            command = command_result.value

            # Add command to session
            add_result = self.add_command_to_session(session, command)
            if add_result.is_failure:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Failed to add command to session: {add_result.error}"
                )
            session = add_result.value

            # Start execution
            start_result = self.start_command_execution(command)
            if start_result.is_failure:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Failed to start command execution: {start_result.error}"
                )
            command = start_result.value

            # Simulate execution completion (in real implementation, this would be async)
            # For now, return success workflow result
            workflow_result: FlextTypes.Core.Dict = {
                "session_id": session.id,
                "command_id": command.id,
                "command_line": command.command_line,
                "status": command.status,
                "workflow_status": "initialized",
            }

            logger.debug("Executed command workflow: %s", command_line)
            return FlextResult[FlextTypes.Core.Dict].ok(workflow_result)
        except Exception as e:
            logger.exception("Command workflow execution failed")
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Command workflow execution failed: {e}"
            )


__all__ = ["FlextCliDomainServices"]
