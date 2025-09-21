"""CLI Command Service - Single responsibility for command management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from flext_cli.models import FlextCliModels
from flext_core import FlextDomainService, FlextLogger, FlextResult, FlextTypes


class FlextCliCommandService(FlextDomainService[FlextTypes.Core.List]):
    """Unified command service using single responsibility principle.

    Handles ALL command management operations for CLI ecosystem.
    ARCHITECTURAL COMPLIANCE: One class per module, nested helpers pattern.
    """

    def __init__(self) -> None:
        """Initialize command service with flext-core integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._command_history: list[FlextCliModels.CliCommand] = []
        self._command_history_enabled = True

    class _CommandValidationHelper:
        """Nested helper for command validation - no loose functions."""

        @staticmethod
        def validate_command_line(command_line: object) -> FlextResult[str]:
            """Validate command line parameter.

            Returns:
            FlextResult[str]: Description of return value.

            """
            if not isinstance(command_line, str) or not command_line.strip():
                return FlextResult[str].fail("Command line must be a non-empty string")

            return FlextResult[str].ok(command_line.strip())

        @staticmethod
        def validate_command_object(
            command: object,
        ) -> FlextResult[FlextCliModels.CliCommand]:
            """Validate command object parameter.

            Returns:
            FlextResult[FlextCliModels.CliCommand]: Description of return value.

            """
            if not isinstance(command, FlextCliModels.CliCommand):
                return FlextResult[FlextCliModels.CliCommand].fail(
                    "Invalid command object"
                )

            return FlextResult[FlextCliModels.CliCommand].ok(command)

    class _CommandBuilderHelper:
        """Nested helper for command construction - no loose functions."""

        @staticmethod
        def create_command_metadata(command_line: str) -> FlextCliModels.CliCommand:
            """Create command with proper metadata.

            Returns:
            FlextCliModels.CliCommand: Description of return value.

            """
            return FlextCliModels.CliCommand(
                id=str(uuid4()),
                command_line=command_line,
                execution_time=datetime.now(UTC),
            )

        @staticmethod
        def create_command_with_options(
            name: str,
            description: str,
            handler: object,
            **options: object,
        ) -> dict[str, object]:
            """Create command with options for CLI frameworks.

            Returns:
            dict[str, object]: Description of return value.

            """
            return {
                "name": name,
                "description": description,
                "handler": handler,
                "arguments": options.get("arguments", []),
                "output_format": options.get("output_format", "table"),
                "options": options,
            }

    def execute(self) -> FlextResult[FlextTypes.Core.List]:
        """Execute command operation - FlextDomainService interface.

        Returns:
            FlextResult[FlextTypes.Core.List]: Description of return value.

        """
        self._logger.info("Executing command service operation")
        return FlextResult[FlextTypes.Core.List].ok(list(self._command_history))

    def create_command(
        self,
        command_line: str,
        **_options: object,
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Create CLI command with validation - single responsibility.

        Returns:
            FlextResult[FlextCliModels.CliCommand]: Description of return value.

        """
        # Input validation using nested helper
        validation_result = self._CommandValidationHelper.validate_command_line(
            command_line
        )
        if validation_result.is_failure:
            return FlextResult[FlextCliModels.CliCommand].fail(
                validation_result.error or "Command validation failed"
            )

        validated_command_line = validation_result.unwrap()

        try:
            # Create command using nested helper
            command = self._CommandBuilderHelper.create_command_metadata(
                validated_command_line
            )

            # Add to command history if enabled
            if self._command_history_enabled:
                self._command_history.append(command)

            self._logger.info(f"Created command: {command.id}")
            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Command creation failed: {e}"
            )

    def execute_command(self, command: FlextCliModels.CliCommand) -> FlextResult[str]:
        """Execute CLI command with validation - single responsibility.

        Returns:
            FlextResult[str]: Description of return value.

        """
        # Validate command object using nested helper
        validation_result = self._CommandValidationHelper.validate_command_object(
            command
        )
        if validation_result.is_failure:
            return FlextResult[str].fail(
                validation_result.error or "Command object validation failed"
            )

        validated_command = validation_result.unwrap()

        try:
            # Execute command (placeholder implementation)
            execution_result = f"Executed: {validated_command.command_line}"

            # Update execution time
            validated_command.execution_time = datetime.now(UTC)

            self._logger.info(f"Executed command: {validated_command.id}")
            return FlextResult[str].ok(execution_result)
        except Exception as e:
            return FlextResult[str].fail(f"Command execution failed: {e}")

    def create_command_definition(
        self,
        name: str,
        description: str,
        handler: object,
        **options: object,
    ) -> FlextResult[dict[str, object]]:
        """Create command definition for CLI frameworks - single responsibility.

        Returns:
            FlextResult[dict[str, object]]: Description of return value.

        """
        if not name.strip():
            return FlextResult[dict[str, object]].fail(
                "Command name must be a non-empty string"
            )

        if not description.strip():
            return FlextResult[dict[str, object]].fail(
                "Command description must be a non-empty string"
            )

        if handler is None:
            return FlextResult[dict[str, object]].fail("Command handler cannot be None")

        try:
            # Create command definition using nested helper
            command_def = self._CommandBuilderHelper.create_command_with_options(
                name.strip(),
                description.strip(),
                handler,
                **options,
            )

            return FlextResult[dict[str, object]].ok(command_def)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Command definition creation failed: {e}"
            )

    def get_command_history(self) -> FlextResult[list[FlextCliModels.CliCommand]]:
        """Get command history - single responsibility.

        Returns:
            FlextResult[list[FlextCliModels.CliCommand]]: Description of return value.

        """
        if not self._command_history_enabled:
            return FlextResult[list[FlextCliModels.CliCommand]].fail(
                "Command history is disabled"
            )

        return FlextResult[list[FlextCliModels.CliCommand]].ok(
            self._command_history.copy()
        )

    def clear_command_history(self) -> FlextResult[int]:
        """Clear command history - single responsibility.

        Returns:
            FlextResult[int]: Description of return value.

        """
        if not self._command_history_enabled:
            return FlextResult[int].fail("Command history is disabled")

        try:
            command_count = len(self._command_history)
            self._command_history.clear()

            self._logger.info(f"Cleared {command_count} commands from history")
            return FlextResult[int].ok(command_count)
        except Exception as e:
            return FlextResult[int].fail(f"History clearing failed: {e}")

    def get_command_statistics(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get command statistics - single responsibility.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        if not self._command_history_enabled:
            return FlextResult[FlextTypes.Core.Dict].fail("Command history is disabled")

        try:
            total_commands = len(self._command_history)
            command_lines = [cmd.command_line for cmd in self._command_history]

            # Calculate basic statistics
            unique_commands = len(set(command_lines))
            most_common_command = (
                max(set(command_lines), key=command_lines.count)
                if command_lines
                else None
            )

            statistics = {
                "total_commands": total_commands,
                "unique_commands": unique_commands,
                "most_common_command": most_common_command,
                "history_enabled": self._command_history_enabled,
                "recent_commands": command_lines[-10:] if command_lines else [],
            }

            return FlextResult[FlextTypes.Core.Dict].ok(dict(statistics))
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Statistics calculation failed: {e}"
            )

    def find_commands_by_pattern(
        self, pattern: str
    ) -> FlextResult[list[FlextCliModels.CliCommand]]:
        """Find commands matching pattern - single responsibility.

        Returns:
            FlextResult[list[FlextCliModels.CliCommand]]: Description of return value.

        """
        if not self._command_history_enabled:
            return FlextResult[list[FlextCliModels.CliCommand]].fail(
                "Command history is disabled"
            )

        if not pattern.strip():
            return FlextResult[list[FlextCliModels.CliCommand]].fail(
                "Pattern must be a non-empty string"
            )

        try:
            pattern_lower = pattern.lower().strip()
            matching_commands = [
                cmd
                for cmd in self._command_history
                if cmd.command_line and pattern_lower in cmd.command_line.lower()
            ]

            return FlextResult[list[FlextCliModels.CliCommand]].ok(matching_commands)
        except Exception as e:
            return FlextResult[list[FlextCliModels.CliCommand]].fail(
                f"Pattern search failed: {e}"
            )

    def configure_command_history(self, *, enabled: bool) -> FlextResult[None]:
        """Configure command history tracking - single responsibility.

        Returns:
            FlextResult[None]: Description of return value.

        """
        try:
            self._command_history_enabled = bool(enabled)

            if not enabled:
                # Clear history when disabling tracking
                self._command_history.clear()
                self._logger.info("Command history disabled, history cleared")
            else:
                self._logger.info("Command history enabled")

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Configuration failed: {e}")

    def get_recent_commands(
        self, limit: int = 10
    ) -> FlextResult[list[FlextCliModels.CliCommand]]:
        """Get recent commands with limit - single responsibility.

        Returns:
            FlextResult[list[FlextCliModels.CliCommand]]: Description of return value.

        """
        if not self._command_history_enabled:
            return FlextResult[list[FlextCliModels.CliCommand]].fail(
                "Command history is disabled"
            )

        if limit <= 0:
            return FlextResult[list[FlextCliModels.CliCommand]].fail(
                "Limit must be a positive integer"
            )

        try:
            recent_commands = (
                self._command_history[-limit:] if self._command_history else []
            )
            return FlextResult[list[FlextCliModels.CliCommand]].ok(recent_commands)
        except Exception as e:
            return FlextResult[list[FlextCliModels.CliCommand]].fail(
                f"Recent commands retrieval failed: {e}"
            )


__all__ = ["FlextCliCommandService"]
