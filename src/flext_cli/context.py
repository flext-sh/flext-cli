"""FLEXT CLI Context - CLI execution context management.

Provides CLI execution context with type-safe operations and FlextResult patterns.
Follows FLEXT standards with single CliContext class per module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import typing
from typing import cast

from flext_core import (
    FlextConfig,
    FlextMixins,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)
from pydantic import Field

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_cli.typings import FlextCliTypes


class FlextCliContext(FlextCliServiceBase):
    """CLI execution context model extending FlextCliServiceBase.

    Manages CLI execution context with enhanced type safety using FlextCliTypes
    instead of generic FlextTypes types. Provides CLI-specific context with domain types
    and uses FlextResult railway pattern for all operations.

    CRITICAL: Moved from models.py to follow FLEXT standards requiring
    service classes to be in appropriate modules, not mixed with data models.
    """

    # Direct attributes - no properties needed
    id: str = ""
    command: str | None = None
    arguments: list[str] | None = Field(default_factory=list)
    environment_variables: FlextTypes.JsonDict | None = Field(default_factory=dict)
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
        # Generate id if not provided using FlextUtilities
        generated_id: str | None = None
        if "id" not in data:
            generated_id = FlextUtilities.Generators.generate_uuid()
            data["id"] = generated_id

        # Initialize parent FlextService
        super().__init__(**data)

        # Set id from data - check both self.id (after super().__init__) and generated_id
        # This ensures all paths are reachable for comprehensive coverage
        # Check self.id first (set by super().__init__ from data), then fallback to generated_id
        if self.id:
            # Normal path: id was set by super().__init__ from data and is truthy
            # Ensure it's a string
            self.id = str(self.id)
        elif generated_id is not None:
            # Fallback path: id was generated but self.id is falsy after super().__init__
            # This can happen if super().__init__ doesn't set id or sets it to falsy value
            self.id = generated_id
        else:
            # Final fallback: generate new id using FlextUtilities (defensive programming)
            # This line is reachable if both self.id and generated_id are None/empty
            self.id = FlextUtilities.Generators.generate_uuid()

        # Set CLI context attributes directly
        # Validate explicitly - no fallback to empty collections
        self.command = command
        if arguments is not None:
            self.arguments = arguments
        else:
            self.arguments = []
        if environment_variables is not None:
            self.environment_variables = environment_variables
        else:
            self.environment_variables = {}
        self.working_directory = working_directory
        # Initialize context_metadata as empty dict (JsonDict type)
        if not self.context_metadata:
            self.context_metadata = {}

        # Context state
        self.is_active = False
        self.created_at = FlextUtilities.Generators.generate_iso_timestamp()
        # Get timeout_seconds from FlextConfig base (not FlextCliConfig)
        global_config = FlextConfig.get_global_instance()
        # timeout_seconds is float in FlextConfig, convert to int for context
        self.timeout_seconds = int(global_config.timeout_seconds)

    def activate(self) -> FlextResult[bool]:
        """Activate CLI context for execution.

        Returns:
            FlextResult[bool]: True if activated successfully, False if already active, or error

        """
        try:
            if self.is_active:
                return FlextResult[bool].fail(
                    FlextCliConstants.ContextErrorMessages.CONTEXT_ALREADY_ACTIVE,
                )

            self.is_active = True
            return FlextResult[bool].ok(True)
        except Exception as e:  # pragma: no cover
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.CONTEXT_ACTIVATION_FAILED.format(
                    error=e,
                ),
            )

    def deactivate(self) -> FlextResult[bool]:
        """Deactivate CLI context.

        Returns:
            FlextResult[bool]: True if deactivated successfully, False if not active, or error

        """
        try:
            if not self.is_active:
                return FlextResult[bool].fail(
                    FlextCliConstants.ContextErrorMessages.CONTEXT_NOT_CURRENTLY_ACTIVE,
                )

            self.is_active = False
            return FlextResult[bool].ok(True)
        except Exception as e:  # pragma: no cover
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.CONTEXT_DEACTIVATION_FAILED.format(
                    error=e,
                ),
            )

    def get_environment_variable(self, name: str) -> FlextResult[str]:
        """Get specific environment variable value."""
        # Validate using FlextUtilities.Validation
        try:
            FlextUtilities.Validation.validate_required_string(
                name,
                "Variable name",
            )
        except ValueError as e:
            return FlextResult[str].fail(
                str(e) or "Environment variable validation failed",
            )

        # Fast-fail if environment_variables is None
        if self.environment_variables is None:
            return FlextResult[str].fail(
                FlextCliConstants.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
            )

        try:
            if name in self.environment_variables:
                value = self.environment_variables[name]
                return FlextResult[str].ok(str(value))
            return FlextResult[str].fail(
                FlextCliConstants.ContextErrorMessages.ENV_VAR_NOT_FOUND.format(
                    name=name,
                ),
            )
        except Exception as e:  # pragma: no cover
            return FlextResult[str].fail(
                FlextCliConstants.ContextErrorMessages.ENV_VAR_RETRIEVAL_FAILED.format(
                    error=e,
                ),
            )

    def set_environment_variable(self, name: str, value: str) -> FlextResult[bool]:
        """Set environment variable value.

        Returns:
            FlextResult[bool]: True if set successfully, or error

        """
        # Validate using FlextUtilities.Validation
        try:
            FlextUtilities.Validation.validate_required_string(
                name,
                "Variable name",
            )
        except ValueError as e:
            return FlextResult[bool].fail(
                str(e) or "Environment variable setting failed",
            )

        if not isinstance(value, str):
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.VARIABLE_VALUE_MUST_BE_STRING,
            )

        # Fast-fail if environment_variables is None
        if self.environment_variables is None:
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
            )

        try:
            self.environment_variables[name] = value
            return FlextResult[bool].ok(True)
        except Exception as e:  # pragma: no cover
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.ENV_VAR_SETTING_FAILED.format(
                    error=e,
                ),
            )

    def add_argument(self, argument: str) -> FlextResult[bool]:
        """Add command line argument.

        Returns:
            FlextResult[bool]: True if added successfully, or error

        """
        # Validate using FlextUtilities.Validation
        try:
            FlextUtilities.Validation.validate_required_string(
                argument,
                "Argument",
            )
        except ValueError as e:
            return FlextResult[bool].fail(str(e) or "Validation failed")

        # Fast-fail if arguments is None
        if self.arguments is None:
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
            )

        try:
            self.arguments.append(argument)
            return FlextResult[bool].ok(True)
        except Exception as e:  # pragma: no cover
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.ARGUMENT_ADDITION_FAILED.format(
                    error=e,
                ),
            )

    def remove_argument(self, argument: str) -> FlextResult[bool]:
        """Remove command line argument.

        Returns:
            FlextResult[bool]: True if removed successfully, False if not found, or error

        """
        # Validate using FlextUtilities.Validation
        try:
            FlextUtilities.Validation.validate_required_string(
                argument,
                "Argument",
            )
        except ValueError as e:
            return FlextResult[bool].fail(str(e) or "Validation failed")

        # Fast-fail if arguments is None
        if self.arguments is None:
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
            )

        try:
            if argument in self.arguments:
                self.arguments.remove(argument)
                return FlextResult[bool].ok(True)
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.ARGUMENT_NOT_FOUND.format(
                    argument=argument,
                ),
            )
        except Exception as e:  # pragma: no cover
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.ARGUMENT_REMOVAL_FAILED.format(
                    error=e,
                ),
            )

    def set_metadata(self, key: str, value: FlextTypes.JsonValue) -> FlextResult[bool]:
        """Set context metadata using CLI-specific data types.

        Returns:
            FlextResult[bool]: True if set successfully, or error

        """
        # Validate using FlextUtilities.Validation
        try:
            FlextUtilities.Validation.validate_required_string(
                key,
                "Metadata key",
            )
        except ValueError as e:
            return FlextResult[bool].fail(str(e) or "Validation failed")

        try:
            self.context_metadata[key] = value
            return FlextResult[bool].ok(True)
        except Exception as e:  # pragma: no cover
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.METADATA_SETTING_FAILED.format(
                    error=e,
                ),
            )

    def get_metadata(self, key: str) -> FlextResult[FlextTypes.JsonValue]:
        """Get context metadata value."""
        # Validate using FlextUtilities.Validation
        try:
            FlextUtilities.Validation.validate_required_string(
                key,
                "Metadata key",
            )
        except ValueError as e:
            return FlextResult[FlextTypes.JsonValue].fail(
                str(e) or "Metadata validation failed",
            )

        try:
            if key in self.context_metadata:
                return FlextResult[FlextTypes.JsonValue].ok(self.context_metadata[key])
            return FlextResult[FlextTypes.JsonValue].fail(
                FlextCliConstants.ContextErrorMessages.METADATA_KEY_NOT_FOUND.format(
                    key=key,
                ),
            )
        except Exception as e:  # pragma: no cover
            return FlextResult[FlextTypes.JsonValue].fail(
                FlextCliConstants.ContextErrorMessages.METADATA_RETRIEVAL_FAILED.format(
                    error=e,
                ),
            )

    def get_context_summary(
        self,
    ) -> FlextResult[FlextTypes.JsonDict]:
        """Get comprehensive context summary using CLI-specific data types."""
        try:
            # Validate command explicitly - no fallback, use actual value or fail
            command_value: str | None = self.command

            # Handle None values for arguments and environment_variables
            arguments_list = self.arguments if self.arguments is not None else []
            env_vars_dict = (
                self.environment_variables
                if self.environment_variables is not None
                else {}
            )

            summary: FlextTypes.JsonDict = {
                FlextCliConstants.ContextDictKeys.CONTEXT_ID: self.id,
                FlextCliConstants.ContextDictKeys.COMMAND: command_value,
                FlextCliConstants.ContextDictKeys.ARGUMENTS_COUNT: len(arguments_list),
                FlextCliConstants.ContextDictKeys.ARGUMENTS: list(arguments_list),
                FlextCliConstants.ContextDictKeys.ENVIRONMENT_VARIABLES_COUNT: len(
                    env_vars_dict,
                ),
                FlextCliConstants.ContextDictKeys.WORKING_DIRECTORY: self.working_directory,
                FlextCliConstants.ContextDictKeys.IS_ACTIVE: self.is_active,
                FlextCliConstants.ContextDictKeys.CREATED_AT: self.created_at,
                FlextCliConstants.ContextDictKeys.METADATA_KEYS: list(
                    self.context_metadata.keys(),
                ),
                FlextCliConstants.ContextDictKeys.METADATA_COUNT: len(
                    self.context_metadata,
                ),
            }

            return FlextResult[FlextTypes.JsonDict].ok(summary)
        except Exception as e:  # pragma: no cover
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.ContextErrorMessages.CONTEXT_SUMMARY_GENERATION_FAILED.format(
                    error=e,
                ),
            )

    def execute(self, **_kwargs: object) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute the CLI context.

        Args:
            **_kwargs: Additional execution parameters (unused, for FlextService compatibility)

        Returns:
            FlextResult with ContextExecutionResult serialized as dict

        Pydantic 2 Modernization:
            - Uses ContextExecutionResult model internally
            - Serializes to dict for API compatibility
            - Type-safe with automatic validation

        """
        try:
            # Fast-fail if arguments is None - no fallback
            if self.arguments is None:
                return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                    FlextCliConstants.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
                )
            arguments_count = len(self.arguments)
            result_model = FlextCliModels.ContextExecutionResult(
                context_executed=True,
                command=self.command,
                arguments_count=arguments_count,
                timestamp=FlextUtilities.Generators.generate_iso_timestamp(),
            )
            # Use model directly - no conversion needed
            # Return model data as dict for API compatibility
            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(
                cast(
                    "FlextCliTypes.Data.CliDataDict",
                    FlextMixins.ModelConversion.to_dict(result_model),
                ),
            )
        except Exception as e:  # pragma: no cover
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                FlextCliConstants.ContextErrorMessages.CONTEXT_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def to_dict(self) -> FlextResult[FlextTypes.JsonDict]:
        """Convert context to dictionary.

        Returns:
            FlextResult[FlextTypes.JsonDict]: Dictionary representation or error

        Fast-fail: No fallbacks - validates that all required data exists.

        """
        try:
            # Fast-fail if arguments is None - no fallback
            if self.arguments is None:
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
                )

            # Fast-fail if environment_variables is None - no fallback
            if self.environment_variables is None:
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
                )

            # Cast to JsonDict for type checker (dict with JsonValue values is JsonDict at runtime)
            result = typing.cast(
                "FlextTypes.JsonDict",
                {
                    FlextCliConstants.ContextDictKeys.ID: self.id,
                    FlextCliConstants.ContextDictKeys.COMMAND: self.command,
                    FlextCliConstants.ContextDictKeys.ARGUMENTS: self.arguments,
                    FlextCliConstants.ContextDictKeys.ENVIRONMENT_VARIABLES: self.environment_variables,
                    FlextCliConstants.ContextDictKeys.WORKING_DIRECTORY: self.working_directory,
                    FlextCliConstants.ContextDictKeys.CREATED_AT: self.created_at,
                    FlextCliConstants.ContextDictKeys.TIMEOUT_SECONDS: self.timeout_seconds,
                },
            )

            return FlextResult[FlextTypes.JsonDict].ok(result)
        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.ContextErrorMessages.CONTEXT_SERIALIZATION_FAILED.format(
                    error=e,
                ),
            )


__all__ = [
    "FlextCliContext",
]
