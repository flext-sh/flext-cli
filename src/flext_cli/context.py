"""FLEXT CLI Context - CLI execution context management.

Provides CLI execution context with type-safe operations and FlextResult patterns.
Follows FLEXT standards with single FlextCliContext class per module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)

from flext_cli.models import FlextCliModels
from flext_cli.typings import FlextCliTypes


class FlextCliContext(FlextService[FlextCliTypes.Data.CliDataDict]):
    """CLI execution context management service.

    Provides type-safe CLI context operations with FlextResult railway patterns.
    Wraps CliContext model from FlextCliModels for service-level operations.
    """

    def __init__(self, **data: object) -> None:
        """Initialize CLI context service."""
        super().__init__(**data)
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer()
        self._model_class = FlextCliModels.CliContext

    def create_context(
        self,
        command: str | None = None,
        arguments: FlextTypes.StringList | None = None,
        environment_variables: FlextCliTypes.Data.CliConfigData | None = None,
        working_directory: str | None = None,
        **data: object,
    ) -> FlextResult[FlextCliModels.CliContext]:
        """Create a new CLI context instance.

        Args:
            command: CLI command to execute
            arguments: Command arguments
            environment_variables: Environment variables
            working_directory: Working directory
            **data: Additional context data

        Returns:
            FlextResult[FlextCliModels.CliContext]: Created context instance

        """
        try:
            context = self._model_class(
                command=command,
                arguments=arguments,
                environment_variables=environment_variables,
                working_directory=working_directory,
                **data,
            )
            return FlextResult[FlextCliModels.CliContext].ok(context)
        except Exception as e:
            return FlextResult[FlextCliModels.CliContext].fail(
                f"Failed to create context: {e}"
            )

    def validate_context(
        self,
        context: FlextCliModels.CliContext,
    ) -> FlextResult[None]:
        """Validate CLI context instance.

        Args:
            context: Context to validate

        Returns:
            FlextResult[None]: Validation result

        """
        try:
            # Validation is automatic via Pydantic in the model
            # This method provides explicit validation interface
            if not context.command and not context.arguments:
                return FlextResult[None].fail(
                    "Context must have either command or arguments"
                )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Context validation failed: {e}")

    def execute(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute context service operations.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Service execution result

        """
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok({
            "service": "FlextCliContext",
            "status": "operational",
        })


__all__ = [
    "FlextCliContext",
]
