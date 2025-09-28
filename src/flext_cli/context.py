"""CLI domain context.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.typings import FlextCliTypes
from flext_core import (
    FlextLogger,
    FlextModels,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)


class FlextCliContext(FlextModels.Entity):
    """CLI execution context using domain-specific types.

    Manages CLI execution context with enhanced type safety using FlextCliTypes
    instead of generic FlextTypes.Core types. Extends FlextModels.Entity for
    proper entity lifecycle management.
    """

    def __init__(
        self,
        command: str | None = None,
        arguments: list[str] | None = None,
        environment_variables: FlextCliTypes.Data.CliConfigData | None = None,
        working_directory: str | None = None,
        **data: object,
    ) -> None:
        """Initialize CLI context with enhanced type safety.

        Args:
            command: Command being executed
            arguments: Command line arguments
            environment_variables: Environment variables using CLI-specific config data types
            working_directory: Current working directory
            **data: Additional entity initialization data

        """
        super().__init__(**data)
        self._logger = FlextLogger(__name__)

        # CLI context initialization with domain-specific types
        self._command = command
        self._arguments = arguments or []
        self._environment_variables: FlextCliTypes.Data.CliConfigData = (
            environment_variables or {}
        )
        self._working_directory = working_directory
        self._context_metadata: FlextCliTypes.Data.CliDataDict = {}

        # Context state
        self._is_active = False
        self._created_at = FlextUtilities.Generators.generate_timestamp()

    @property
    def command(self) -> str | None:
        """Get current command being executed.

        Returns:
            str | None: Command name or None if not set

        """
        return self._command

    @command.setter
    def command(self, value: str | None) -> None:
        """Set current command being executed.

        Args:
            value: Command name to set

        """
        self._command = value

    @property
    def arguments(self) -> list[str]:
        """Get command line arguments.

        Returns:
            list[str]: List of command arguments

        """
        return self._arguments.copy()

    @arguments.setter
    def arguments(self, value: list[str]) -> None:
        """Set command line arguments.

        Args:
            value: List of command arguments

        """
        self._arguments = value or []

    @property
    def environment_variables(self) -> FlextCliTypes.Data.CliConfigData:
        """Get environment variables using CLI-specific config data types.

        Returns:
            FlextCliTypes.Data.CliConfigData: Environment variables dictionary

        """
        return self._environment_variables.copy()

    @environment_variables.setter
    def environment_variables(self, value: FlextCliTypes.Data.CliConfigData) -> None:
        """Set environment variables using CLI-specific types.

        Args:
            value: Environment variables dictionary

        """
        self._environment_variables = value or {}

    @property
    def working_directory(self) -> str | None:
        """Get current working directory.

        Returns:
            str | None: Working directory path or None if not set

        """
        return self._working_directory

    @working_directory.setter
    def working_directory(self, value: str | None) -> None:
        """Set current working directory.

        Args:
            value: Working directory path

        """
        self._working_directory = value

    @property
    def is_active(self) -> bool:
        """Check if context is currently active.

        Returns:
            bool: True if context is active

        """
        return self._is_active

    def activate(self) -> FlextResult[None]:
        """Activate CLI context for execution.

        Returns:
            FlextResult[None]: Activation result

        """
        try:
            if self._is_active:
                return FlextResult[None].fail("Context is already active")

            self._is_active = True
            self._logger.info(f"CLI context activated for command: {self._command}")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Context activation failed: {e}")

    def deactivate(self) -> FlextResult[None]:
        """Deactivate CLI context.

        Returns:
            FlextResult[None]: Deactivation result

        """
        try:
            if not self._is_active:
                return FlextResult[None].fail("Context is not currently active")

            self._is_active = False
            self._logger.info("CLI context deactivated")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Context deactivation failed: {e}")

    def get_environment_variable(self, name: str) -> FlextResult[str]:
        """Get specific environment variable value.

        Args:
            name: Environment variable name

        Returns:
            FlextResult[str]: Variable value or error

        """
        if not name or not isinstance(name, str):
            return FlextResult[str].fail("Variable name must be a non-empty string")

        try:
            if name in self._environment_variables:
                value = self._environment_variables[name]
                # Convert to string since environment variables are typically strings
                return FlextResult[str].ok(str(value))
            return FlextResult[str].fail(f"Environment variable '{name}' not found")

        except Exception as e:
            return FlextResult[str].fail(f"Environment variable retrieval failed: {e}")

    def set_environment_variable(self, name: str, value: str) -> FlextResult[None]:
        """Set environment variable value.

        Args:
            name: Environment variable name
            value: Environment variable value

        Returns:
            FlextResult[None]: Set operation result

        """
        if not name or not isinstance(name, str):
            return FlextResult[None].fail("Variable name must be a non-empty string")

        if not isinstance(value, str):
            return FlextResult[None].fail("Variable value must be a string")

        try:
            self._environment_variables[name] = value
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Environment variable setting failed: {e}")

    def add_argument(self, argument: str) -> FlextResult[None]:
        """Add command line argument.

        Args:
            argument: Argument to add

        Returns:
            FlextResult[None]: Add operation result

        """
        if not argument or not isinstance(argument, str):
            return FlextResult[None].fail("Argument must be a non-empty string")

        try:
            self._arguments.append(argument)
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Argument addition failed: {e}")

    def remove_argument(self, argument: str) -> FlextResult[None]:
        """Remove command line argument.

        Args:
            argument: Argument to remove

        Returns:
            FlextResult[None]: Remove operation result

        """
        if not argument or not isinstance(argument, str):
            return FlextResult[None].fail("Argument must be a non-empty string")

        try:
            if argument in self._arguments:
                self._arguments.remove(argument)
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(f"Argument '{argument}' not found")

        except Exception as e:
            return FlextResult[None].fail(f"Argument removal failed: {e}")

    def set_metadata(
        self, key: str, value: FlextTypes.Core.JsonValue
    ) -> FlextResult[None]:
        """Set context metadata using CLI-specific data types.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            FlextResult[None]: Set operation result

        """
        if not key or not isinstance(key, str):
            return FlextResult[None].fail("Metadata key must be a non-empty string")

        try:
            self._context_metadata[key] = value
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Metadata setting failed: {e}")

    def get_metadata(self, key: str) -> FlextResult[object]:
        """Get context metadata value.

        Args:
            key: Metadata key

        Returns:
            FlextResult[object]: Metadata value or error

        """
        if not key or not isinstance(key, str):
            return FlextResult[object].fail("Metadata key must be a non-empty string")

        try:
            if key in self._context_metadata:
                return FlextResult[object].ok(self._context_metadata[key])
            return FlextResult[object].fail(f"Metadata key '{key}' not found")

        except Exception as e:
            return FlextResult[object].fail(f"Metadata retrieval failed: {e}")

    def get_context_summary(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get comprehensive context summary using CLI-specific data types.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Context summary data

        """
        try:
            summary: FlextCliTypes.Data.CliDataDict = {
                "context_id": self.id,
                "command": self._command or "none",
                "arguments_count": len(self._arguments),
                "arguments": list(
                    self._arguments
                ),  # Convert to list[object] for JsonValue compatibility
                "environment_variables_count": len(self._environment_variables),
                "working_directory": self._working_directory or "not_set",
                "is_active": self._is_active,
                "created_at": self._created_at,
                "metadata_keys": list(self._context_metadata.keys()),
                "metadata_count": len(self._context_metadata),
            }

            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(summary)

        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Context summary generation failed: {e}",
            )

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute the CLI context.

        Returns:
            FlextResult[dict[str, object]]: Execution result

        """
        try:
            return FlextResult[dict[str, object]].ok({
                "context_executed": True,
                "command": self._command,
                "arguments_count": len(self._arguments) if self._arguments else 0,
                "timestamp": FlextUtilities.Generators.generate_timestamp(),
            })
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Context execution failed: {e}")

    async def execute_async(self) -> FlextResult[dict[str, object]]:
        """Execute the CLI context asynchronously.

        Returns:
            FlextResult[dict[str, object]]: Execution result

        """
        try:
            return FlextResult[dict[str, object]].ok({
                "context_executed": True,
                "command": self._command,
                "arguments_count": len(self._arguments) if self._arguments else 0,
                "timestamp": FlextUtilities.Generators.generate_timestamp(),
                "async": True,
            })
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Async context execution failed: {e}"
            )

    @property
    def timeout_seconds(self) -> int:
        """Get the timeout in seconds.

        Returns:
            int: Timeout in seconds

        """
        return getattr(self, "_timeout_seconds", 30)

    @timeout_seconds.setter
    def timeout_seconds(self, value: int) -> None:
        """Set the timeout in seconds.

        Args:
            value: Timeout in seconds

        """
        self._timeout_seconds = value

    def to_dict(self) -> dict[str, object]:
        """Convert context to dictionary.

        Returns:
            dict[str, object]: Context as dictionary

        """
        return {
            "id": self.id,
            "command": self._command,
            "arguments": self._arguments or [],
            "environment_variables": self._environment_variables or {},
            "working_directory": self._working_directory,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "timeout_seconds": self.timeout_seconds,
        }

    def print_error(self, message: str) -> None:
        """Print error message to stderr.

        Args:
            message: Error message to print

        """

    def print_info(self, message: str) -> None:
        """Print info message to stdout.

        Args:
            message: Info message to print

        """

    def print_success(self, message: str) -> None:
        """Print success message to stdout.

        Args:
            message: Success message to print

        """

    def print_warning(self, message: str) -> None:
        """Print warning message to stderr.

        Args:
            message: Warning message to print

        """
