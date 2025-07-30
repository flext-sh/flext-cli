"""CLI domain services for business logic operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import logging

from flext_core import ValidatedModel
from flext_core.result import FlextResult
from pydantic import Field

# Real imports at top level for better performance and clarity
from flext_cli.domain.entities import CLICommand, CLISession, CommandType

logger = logging.getLogger(__name__)


class CLIServiceContainer(ValidatedModel):
    """Service container for CLI dependency injection."""

    name: str = Field(..., description="Service container name")
    version: str = Field(..., description="Service container version")


class CLICommandService:
    """Service for handling CLI command operations."""

    def __init__(self) -> None:
        """Initialize the CLI command service."""
        self._logger = logger

    def create_command(
        self,
        name: str,
        command_line: str,
        command_type: str = "cli",
    ) -> FlextResult[CLICommand]:
        """Create a new CLI command.

        Args:
            name: Command name
            command_line: Command line string
            command_type: Type of command

        Returns:
            FlextResult containing the created command or error.

        """
        try:
            # Convert string to CommandType enum
            if command_type == "cli":
                cmd_type = CommandType.CLI
            elif command_type == "system":
                cmd_type = CommandType.SYSTEM
            else:
                cmd_type = CommandType.CLI

            command = CLICommand(
                name=name,
                command_line=command_line,
                command_type=cmd_type,
            )

            return FlextResult.ok(command)
        except Exception as e:
            return FlextResult.fail(f"Failed to create command: {e}")

    def validate_command(self, command: CLICommand) -> FlextResult[None]:
        """Validate a CLI command.

        Args:
            command: Command to validate

        Returns:
            FlextResult indicating validation success or failure.

        """
        return command.validate_domain_rules()


class CLISessionService:
    """Service for handling CLI session operations."""

    def __init__(self) -> None:
        """Initialize the CLI session service."""
        self._logger = logger

    def create_session(self, session_id: str) -> FlextResult[CLISession]:
        """Create a new CLI session.

        Args:
            session_id: Session identifier

        Returns:
            FlextResult containing the created session or error.

        """
        try:
            session = CLISession(session_id=session_id)
            return FlextResult.ok(session)
        except Exception as e:
            return FlextResult.fail(f"Failed to create session: {e}")

    def validate_session(self, session: CLISession) -> FlextResult[None]:
        """Validate a CLI session.

        Args:
            session: Session to validate

        Returns:
            FlextResult indicating validation success or failure.

        """
        return session.validate_domain_rules()
