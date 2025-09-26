"""FLEXT CLI Processors - Single unified class following FLEXT standards.

Provides CLI-specific processor implementations using flext-core patterns.
Single FlextCliProcessors class with nested processor subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class FlextCliProcessors:
    """Single unified CLI processors class following FLEXT standards.

    Contains all processor implementations for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Inherits from FlextProcessors to avoid duplication
    - Uses centralized processor patterns from FlextProcessors
    - Implements CLI-specific extensions while reusing core functionality
    """

    class CommandProcessor:
        """CLI command processor for processing command operations."""

        @override
        def __init__(self) -> None:
            """Initialize command processor."""
            self._processed_commands: list[FlextCliModels.CliCommand] = []

        def process_command(
            self, command: FlextCliModels.CliCommand
        ) -> FlextResult[FlextCliModels.CliCommand]:
            """Process a CLI command.

            Args:
                command: Command to process

            Returns:
                FlextResult[FlextCliModels.CliCommand]: Processed command or error

            """
            try:
                # Validate command business rules
                validation_result = command.validate_business_rules()
                if not validation_result.is_success:
                    return FlextResult[FlextCliModels.CliCommand].fail(
                        validation_result.error or "Command validation failed"
                    )

                # Process the command
                command.update_timestamp()
                self._processed_commands.append(command)

                return FlextResult[FlextCliModels.CliCommand].ok(command)
            except Exception as e:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Command processing failed: {e}"
                )

        def get_processed_commands(
            self,
        ) -> FlextResult[list[FlextCliModels.CliCommand]]:
            """Get all processed commands.

            Returns:
                FlextResult[list[FlextCliModels.CliCommand]]: List of processed commands or error

            """
            try:
                return FlextResult[list[FlextCliModels.CliCommand]].ok(
                    self._processed_commands.copy()
                )
            except Exception as e:
                return FlextResult[list[FlextCliModels.CliCommand]].fail(
                    f"Failed to get processed commands: {e}"
                )

        def clear_processed_commands(self) -> FlextResult[int]:
            """Clear all processed commands.

            Returns:
                FlextResult[int]: Number of commands cleared or error

            """
            try:
                count = len(self._processed_commands)
                self._processed_commands.clear()
                return FlextResult[int].ok(count)
            except Exception as e:
                return FlextResult[int].fail(f"Failed to clear processed commands: {e}")

    class SessionProcessor:
        """CLI session processor for processing session operations."""

        @override
        def __init__(self) -> None:
            """Initialize session processor."""
            self._processed_sessions: list[FlextCliModels.CliSession] = []

        def process_session(
            self, session: FlextCliModels.CliSession
        ) -> FlextResult[FlextCliModels.CliSession]:
            """Process a CLI session.

            Args:
                session: Session to process

            Returns:
                FlextResult[FlextCliModels.CliSession]: Processed session or error

            """
            try:
                # Validate session business rules
                validation_result = session.validate_business_rules()
                if not validation_result.is_success:
                    return FlextResult[FlextCliModels.CliSession].fail(
                        validation_result.error or "Session validation failed"
                    )

                # Process the session
                session.update_timestamp()
                self._processed_sessions.append(session)

                return FlextResult[FlextCliModels.CliSession].ok(session)
            except Exception as e:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Session processing failed: {e}"
                )

        def get_processed_sessions(
            self,
        ) -> FlextResult[list[FlextCliModels.CliSession]]:
            """Get all processed sessions.

            Returns:
                FlextResult[list[FlextCliModels.CliSession]]: List of processed sessions or error

            """
            try:
                return FlextResult[list[FlextCliModels.CliSession]].ok(
                    self._processed_sessions.copy()
                )
            except Exception as e:
                return FlextResult[list[FlextCliModels.CliSession]].fail(
                    f"Failed to get processed sessions: {e}"
                )

        def clear_processed_sessions(self) -> FlextResult[int]:
            """Clear all processed sessions.

            Returns:
                FlextResult[int]: Number of sessions cleared or error

            """
            try:
                count = len(self._processed_sessions)
                self._processed_sessions.clear()
                return FlextResult[int].ok(count)
            except Exception as e:
                return FlextResult[int].fail(f"Failed to clear processed sessions: {e}")

    class DataProcessor:
        """CLI data processor for processing data operations."""

        @override
        def __init__(self) -> None:
            """Initialize data processor."""
            self._processed_data: list[object] = []

        def _transform_data(self, data: object) -> object:
            """Transform data for processing.

            Args:
                data: Raw data to transform

            Returns:
                object: Transformed data

            """
            # Basic transformation - could be extended with more complex logic
            if isinstance(data, dict):
                # Add processing metadata to dictionary data
                transformed_data = data.copy()
                if isinstance(transformed_data, dict):
                    transformed_data["_processed"] = True
                return transformed_data
            if isinstance(data, (list, tuple)):
                # Process list/tuple data
                return list(data) if not isinstance(data, list) else data
            # Return data as-is for other types
            return data

        def process_data(self, data: object) -> FlextResult[object]:
            """Process data.

            Args:
                data: Data to process

            Returns:
                FlextResult[object]: Processed data or error

            """
            try:
                # Basic data processing
                if data is None:
                    return FlextResult[object].fail("Data cannot be None")

                # Process the data with proper transformation
                processed = self._transform_data(data)
                self._processed_data.append(processed)

                return FlextResult[object].ok(processed)
            except Exception as e:
                return FlextResult[object].fail(f"Data processing failed: {e}")

        def get_processed_data(self) -> FlextResult[list[object]]:
            """Get all processed data.

            Returns:
                FlextResult[list[object]]: List of processed data or error

            """
            try:
                return FlextResult[list[object]].ok(self._processed_data.copy())
            except Exception as e:
                return FlextResult[list[object]].fail(
                    f"Failed to get processed data: {e}"
                )

        def clear_processed_data(self) -> FlextResult[int]:
            """Clear all processed data.

            Returns:
                FlextResult[int]: Number of data items cleared or error

            """
            try:
                count = len(self._processed_data)
                self._processed_data.clear()
                return FlextResult[int].ok(count)
            except Exception as e:
                return FlextResult[int].fail(f"Failed to clear processed data: {e}")


__all__ = [
    "FlextCliProcessors",
]
