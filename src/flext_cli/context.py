"""FLEXT CLI Context - CLI execution context management.

Provides CLI execution context with type-safe operations and FlextResult patterns.
Follows FLEXT standards with single CliContext class per module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

import uuid

from flext_core import FlextResult, FlextService, FlextTypes, FlextUtilities
from pydantic import Field

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes


class FlextCliContext(FlextService[FlextCliTypes.Data.CliDataDict]):
    """CLI execution context model extending FlextService.

    Manages CLI execution context with enhanced type safety using FlextCliTypes
    instead of generic FlextTypes types. Provides CLI-specific context with domain types
    and uses FlextResult railway pattern for all operations.

    CRITICAL: Moved from models.py to follow FLEXT standards requiring
    service classes to be in appropriate modules, not mixed with data models.
    """

    # Direct attributes - no properties needed
    id: str = ""
    command: str | None = None
    arguments: list[str] = Field(default_factory=list)
    environment_variables: FlextTypes.JsonDict = Field(default_factory=dict)
    working_directory: str | None = None
    context_metadata: FlextTypes.JsonDict = Field(default_factory=dict)

    # Context state
    is_active: bool = False
    created_at: str = ""
    timeout_seconds: int = Field(default=30)

    def __init__(
        self,
        command: str | None = None,
        arguments: list[str] | None = None,
        environment_variables: FlextTypes.JsonDict | None = None,
        working_directory: str | None = None,
        **data: FlextTypes.JsonValue,
    ) -> None:
        """Initialize CLI context with enhanced type safety.

        Args:
            command: Command being executed
            arguments: Command line arguments
            environment_variables: Environment variables using CLI-specific config data types
            working_directory: Current working directory
            **data: Additional entity initialization data

        """
        # Generate id if not provided
        if "id" not in data:
            data["id"] = str(uuid.uuid4())

        # Initialize parent FlextService
        super().__init__(**data)

        # Set id from data or generated
        self.id = str(data.get("id", str(uuid.uuid4())))

        # Set CLI context attributes directly
        self.command = command
        self.arguments = arguments or []
        self.environment_variables = environment_variables or {}
        self.working_directory = working_directory
        self.context_metadata = {}

        # Context state
        self.is_active = False
        self.created_at = FlextUtilities.Generators.generate_iso_timestamp()
        self.timeout_seconds = int(FlextCliConfig.get_global_instance().timeout_seconds)

    def activate(self) -> FlextResult[None]:
        """Activate CLI context for execution."""
        try:
            if self.is_active:
                return FlextResult[None].fail(
                    FlextCliConstants.ContextErrorMessages.CONTEXT_ALREADY_ACTIVE
                )

            self.is_active = True
            return FlextResult[None].ok(None)
        except Exception as e:  # pragma: no cover
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.CONTEXT_ACTIVATION_FAILED.format(
                    error=e
                )
            )

    def deactivate(self) -> FlextResult[None]:
        """Deactivate CLI context."""
        try:
            if not self.is_active:
                return FlextResult[None].fail(
                    FlextCliConstants.ContextErrorMessages.CONTEXT_NOT_CURRENTLY_ACTIVE
                )

            self.is_active = False
            return FlextResult[None].ok(None)
        except Exception as e:  # pragma: no cover
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.CONTEXT_DEACTIVATION_FAILED.format(
                    error=e
                )
            )

    def get_environment_variable(self, name: str) -> FlextResult[str]:
        """Get specific environment variable value."""
        if not name or not isinstance(name, str):
            return FlextResult[str].fail(
                FlextCliConstants.ContextErrorMessages.VARIABLE_NAME_MUST_BE_STRING
            )

        try:
            if name in self.environment_variables:
                value = self.environment_variables[name]
                return FlextResult[str].ok(str(value))
            return FlextResult[str].fail(
                FlextCliConstants.ContextErrorMessages.ENV_VAR_NOT_FOUND.format(
                    name=name
                )
            )
        except Exception as e:  # pragma: no cover
            return FlextResult[str].fail(
                FlextCliConstants.ContextErrorMessages.ENV_VAR_RETRIEVAL_FAILED.format(
                    error=e
                )
            )

    def set_environment_variable(self, name: str, value: str) -> FlextResult[None]:
        """Set environment variable value."""
        if not name or not isinstance(name, str):
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.VARIABLE_NAME_MUST_BE_STRING
            )

        if not isinstance(value, str):
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.VARIABLE_VALUE_MUST_BE_STRING
            )

        try:
            self.environment_variables[name] = value
            return FlextResult[None].ok(None)
        except Exception as e:  # pragma: no cover
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.ENV_VAR_SETTING_FAILED.format(
                    error=e
                )
            )

    def add_argument(self, argument: str) -> FlextResult[None]:
        """Add command line argument."""
        if not argument or not isinstance(argument, str):
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.ARGUMENT_MUST_BE_STRING
            )

        try:
            self.arguments.append(argument)
            return FlextResult[None].ok(None)
        except Exception as e:  # pragma: no cover
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.ARGUMENT_ADDITION_FAILED.format(
                    error=e
                )
            )

    def remove_argument(self, argument: str) -> FlextResult[None]:
        """Remove command line argument."""
        if not argument or not isinstance(argument, str):
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.ARGUMENT_MUST_BE_STRING
            )

        try:
            if argument in self.arguments:
                self.arguments.remove(argument)
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.ARGUMENT_NOT_FOUND.format(
                    argument=argument
                )
            )
        except Exception as e:  # pragma: no cover
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.ARGUMENT_REMOVAL_FAILED.format(
                    error=e
                )
            )

    def set_metadata(self, key: str, value: FlextTypes.JsonValue) -> FlextResult[None]:
        """Set context metadata using CLI-specific data types."""
        if not key or not isinstance(key, str):
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.METADATA_KEY_MUST_BE_STRING
            )

        try:
            self.context_metadata[key] = value
            return FlextResult[None].ok(None)
        except Exception as e:  # pragma: no cover
            return FlextResult[None].fail(
                FlextCliConstants.ContextErrorMessages.METADATA_SETTING_FAILED.format(
                    error=e
                )
            )

    def get_metadata(self, key: str) -> FlextResult[FlextTypes.JsonValue]:
        """Get context metadata value."""
        if not key or not isinstance(key, str):
            return FlextResult[FlextTypes.JsonValue].fail(
                FlextCliConstants.ContextErrorMessages.METADATA_KEY_MUST_BE_STRING
            )

        try:
            if key in self.context_metadata:
                return FlextResult[FlextTypes.JsonValue].ok(self.context_metadata[key])
            return FlextResult[FlextTypes.JsonValue].fail(
                FlextCliConstants.ContextErrorMessages.METADATA_KEY_NOT_FOUND.format(
                    key=key
                )
            )
        except Exception as e:  # pragma: no cover
            return FlextResult[FlextTypes.JsonValue].fail(
                FlextCliConstants.ContextErrorMessages.METADATA_RETRIEVAL_FAILED.format(
                    error=e
                )
            )

    def get_context_summary(
        self,
    ) -> FlextResult[FlextTypes.JsonDict]:
        """Get comprehensive context summary using CLI-specific data types."""
        try:
            summary: FlextTypes.JsonDict = {
                FlextCliConstants.ContextDictKeys.CONTEXT_ID: self.id,
                FlextCliConstants.ContextDictKeys.COMMAND: self.command
                or FlextCliConstants.ContextDefaults.CONTEXT_NONE,
                FlextCliConstants.ContextDictKeys.ARGUMENTS_COUNT: len(self.arguments),
                FlextCliConstants.ContextDictKeys.ARGUMENTS: list(self.arguments),
                FlextCliConstants.ContextDictKeys.ENVIRONMENT_VARIABLES_COUNT: len(
                    self.environment_variables
                ),
                FlextCliConstants.ContextDictKeys.WORKING_DIRECTORY: self.working_directory
                or FlextCliConstants.ContextDefaults.CONTEXT_NOT_SET,
                FlextCliConstants.ContextDictKeys.IS_ACTIVE: self.is_active,
                FlextCliConstants.ContextDictKeys.CREATED_AT: self.created_at,
                FlextCliConstants.ContextDictKeys.METADATA_KEYS: list(
                    self.context_metadata.keys()
                ),
                FlextCliConstants.ContextDictKeys.METADATA_COUNT: len(
                    self.context_metadata
                ),
            }

            return FlextResult[FlextTypes.JsonDict].ok(summary)
        except Exception as e:  # pragma: no cover
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.ContextErrorMessages.CONTEXT_SUMMARY_GENERATION_FAILED.format(
                    error=e
                ),
            )

    def execute(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute the CLI context."""
        try:
            result: FlextCliTypes.Data.CliDataDict = {
                FlextCliConstants.ContextDictKeys.CONTEXT_EXECUTED: True,
                FlextCliConstants.ContextDictKeys.COMMAND: self.command,
                FlextCliConstants.ContextDictKeys.ARGUMENTS_COUNT: len(self.arguments)
                if self.arguments
                else 0,
                FlextCliConstants.DictKeys.TIMESTAMP: FlextUtilities.Generators.generate_iso_timestamp(),
            }
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(result)
        except Exception as e:  # pragma: no cover
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                FlextCliConstants.ContextErrorMessages.CONTEXT_EXECUTION_FAILED.format(
                    error=e
                )
            )

    def to_dict(self) -> dict[str, object]:
        """Convert context to dictionary."""
        # Return dict[str, object] for type compatibility with specific types
        return {
            FlextCliConstants.ContextDictKeys.ID: self.id,
            FlextCliConstants.ContextDictKeys.COMMAND: self.command,
            FlextCliConstants.ContextDictKeys.ARGUMENTS: self.arguments or [],
            FlextCliConstants.ContextDictKeys.ENVIRONMENT_VARIABLES: self.environment_variables
            or {},
            FlextCliConstants.ContextDictKeys.WORKING_DIRECTORY: self.working_directory,
            FlextCliConstants.ContextDictKeys.CREATED_AT: self.created_at,
            FlextCliConstants.ContextDictKeys.TIMEOUT_SECONDS: self.timeout_seconds,
        }


__all__ = [
    "FlextCliContext",
]
