"""FLEXT CLI Context - CLI execution context management.

**MODULE**: FlextCliContext - Single primary class for CLI execution context
**SCOPE**: Context management, environment variables, arguments, metadata with type-safe operations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import (
    FlextConfig,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)
from pydantic import Field

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels


class FlextCliContext(FlextCliServiceBase):
    """CLI execution context with type-safe operations and FlextResult patterns.

    Manages CLI execution context using FlextCliTypes for domain-specific type safety.
    All operations use FlextResult railway pattern for error handling.
    """

    # Direct attributes - no properties needed
    id: str = ""
    command: str | None = None
    arguments: list[str] | None = Field(default_factory=list)
    environment_variables: dict[str, FlextTypes.GeneralValueType] | None = Field(
        default_factory=dict
    )
    working_directory: str | None = None
    context_metadata: dict[str, FlextTypes.GeneralValueType] = Field(
        default_factory=dict
    )

    # Context state
    is_active: bool = False
    created_at: str = ""
    timeout_seconds: int = Field(default=30)

    def __init__(
        self,
        command: str | None = None,
        arguments: list[str] | None = None,
        environment_variables: dict[str, FlextTypes.GeneralValueType] | None = None,
        working_directory: str | None = None,
        **data: FlextTypes.GeneralValueType,
    ) -> None:
        """Initialize CLI context with enhanced type safety.

        Args:
            command: Command being executed
            arguments: Command line arguments
            environment_variables: Environment variables using CLI-specific types
            working_directory: Current working directory
            **data: Additional entity initialization data

        """
        # Generate id if not provided or empty
        if not data.get("id"):
            data["id"] = FlextUtilities.Generators.generate_id()

        # Set all fields in data BEFORE calling super().__init__()
        # This avoids frozen model violations
        if command is not None:
            data["command"] = command
        if arguments is not None:
            data["arguments"] = arguments
        if environment_variables is not None:
            data["environment_variables"] = environment_variables
        if working_directory is not None:
            data["working_directory"] = working_directory

        # Set default values for optional fields
        if "created_at" not in data:
            data["created_at"] = FlextUtilities.Generators.generate_iso_timestamp()
        if "is_active" not in data:
            data["is_active"] = False

        # Set timeout from global config if not provided
        if "timeout_seconds" not in data:
            global_config = FlextConfig.get_global_instance()
            data["timeout_seconds"] = int(global_config.timeout_seconds)

        super().__init__(**data)

    # ==========================================================================
    # PRIVATE HELPERS - Generalize common patterns
    # ==========================================================================

    def _validate_string(
        self, value: str, field_name: str, error_template: str
    ) -> FlextResult[bool]:
        """Generalized string validation helper."""
        try:
            FlextUtilities.Validation.validate_required_string(value, field_name)
            return FlextResult[bool].ok(True)
        except ValueError as e:
            return FlextResult[bool].fail(str(e) or error_template)

    def _ensure_initialized(
        self,
        value: FlextTypes.GeneralValueType | None,
        error_message: str,
    ) -> FlextResult[bool]:
        """Generalized initialization check helper."""
        if value is None:
            return FlextResult[bool].fail(error_message)
        return FlextResult[bool].ok(True)

    def _safe_dict_operation(
        self,
        operation: str,
        dict_obj: dict[str, FlextTypes.GeneralValueType] | None,
        key: str,
        value: FlextTypes.GeneralValueType | None = None,
        error_messages: dict[str, str] | None = None,
    ) -> FlextResult[FlextTypes.GeneralValueType | bool]:
        """Generalized dict operation helper (get/set/check)."""
        default_errors = {
            "not_initialized": FlextCliConstants.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
            "not_found": FlextCliConstants.ContextErrorMessages.ENV_VAR_NOT_FOUND.format(
                name=key
            ),
            "failed": FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(
                error="Operation failed"
            ),
        }
        # Merge error_messages with default_errors, preserving defaults
        errors = {**default_errors, **(error_messages or {})}

        init_check = self._ensure_initialized(dict_obj, errors["not_initialized"])
        if init_check.is_failure:
            return FlextResult[FlextTypes.GeneralValueType | bool].fail(
                init_check.error or ""
            )

        # Type narrowing: dict_obj is not None after _ensure_initialized check
        if dict_obj is None:
            return FlextResult[FlextTypes.GeneralValueType | bool].fail(
                errors["not_initialized"]
            )

        try:
            if operation == "get":
                if key in dict_obj:
                    return FlextResult[FlextTypes.GeneralValueType | bool].ok(
                        dict_obj[key]
                    )
                return FlextResult[FlextTypes.GeneralValueType | bool].fail(
                    errors["not_found"]
                )
            if operation == "set" and value is not None:
                dict_obj[key] = value
                return FlextResult[FlextTypes.GeneralValueType | bool].ok(True)
            return FlextResult[FlextTypes.GeneralValueType | bool].fail(
                errors["failed"]
            )
        except Exception as e:
            return FlextResult[FlextTypes.GeneralValueType | bool].fail(
                errors.get("exception", str(e)) or errors["failed"]
            )

    def _safe_list_operation(
        self,
        operation: str,
        list_obj: list[str] | None,
        value: str,
        error_messages: dict[str, str] | None = None,
    ) -> FlextResult[bool]:
        """Generalized list operation helper (add/remove/check)."""
        default_errors = {
            "not_initialized": FlextCliConstants.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
            "not_found": FlextCliConstants.ContextErrorMessages.ARGUMENT_NOT_FOUND.format(
                argument=value
            ),
            "failed": FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(
                error="Operation failed"
            ),
        }
        # Merge error_messages with default_errors, preserving defaults
        errors = {**default_errors, **(error_messages or {})}

        init_check = self._ensure_initialized(list_obj, errors["not_initialized"])
        if init_check.is_failure:
            return FlextResult[bool].fail(init_check.error or "")

        # Type narrowing: list_obj is not None after _ensure_initialized check
        if list_obj is None:
            return FlextResult[bool].fail(errors["not_initialized"])

        try:
            if operation == "add":
                list_obj.append(value)
                return FlextResult[bool].ok(True)
            if operation == "remove":
                if value in list_obj:
                    list_obj.remove(value)
                    return FlextResult[bool].ok(True)
                return FlextResult[bool].fail(errors["not_found"])
            return FlextResult[bool].fail(errors["failed"])
        except Exception as e:
            # Format exception message if template provided
            exception_template = errors.get("exception", "")
            if exception_template and "{error}" in exception_template:
                exception_msg = exception_template.format(error=str(e))
            else:
                exception_msg = str(e) if exception_template else errors["failed"]
            return FlextResult[bool].fail(exception_msg)

    # ==========================================================================
    # CONTEXT STATE MANAGEMENT
    # ==========================================================================

    def activate(self) -> FlextResult[bool]:
        """Activate CLI context for execution."""
        if self.is_active:
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.CONTEXT_ALREADY_ACTIVE
            )
        # Use object.__setattr__ for frozen model
        object.__setattr__(self, "is_active", True)
        return FlextResult[bool].ok(True)

    def deactivate(self) -> FlextResult[bool]:
        """Deactivate CLI context."""
        if not self.is_active:
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.CONTEXT_NOT_CURRENTLY_ACTIVE
            )
        # Use object.__setattr__ for frozen model
        object.__setattr__(self, "is_active", False)
        return FlextResult[bool].ok(True)

    # ==========================================================================
    # ENVIRONMENT VARIABLES
    # ==========================================================================

    def get_environment_variable(self, name: str) -> FlextResult[str]:
        """Get specific environment variable value."""
        validation = self._validate_string(
            name, "Variable name", "Environment variable validation failed"
        )
        if validation.is_failure:
            return FlextResult[str].fail(validation.error or "")

        result = self._safe_dict_operation(
            "get",
            self.environment_variables,
            name,
            error_messages={
                "not_initialized": FlextCliConstants.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
                "not_found": FlextCliConstants.ContextErrorMessages.ENV_VAR_NOT_FOUND.format(
                    name=name
                ),
                "exception": FlextCliConstants.ContextErrorMessages.ENV_VAR_RETRIEVAL_FAILED.format(
                    error="{error}"
                ),
            },
        )
        if result.is_success:
            return FlextResult[str].ok(str(result.unwrap()))
        return FlextResult[str].fail(result.error or "")

    def set_environment_variable(self, name: str, value: str) -> FlextResult[bool]:
        """Set environment variable value."""
        validation = self._validate_string(
            name, "Variable name", "Environment variable setting failed"
        )
        if validation.is_failure:
            return FlextResult[bool].fail(validation.error or "")

        if not isinstance(value, str):
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.VARIABLE_VALUE_MUST_BE_STRING
            )

        result = self._safe_dict_operation(
            "set",
            self.environment_variables,
            name,
            value,
            error_messages={
                "not_initialized": FlextCliConstants.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
                "exception": FlextCliConstants.ContextErrorMessages.ENV_VAR_SETTING_FAILED.format(
                    error="{error}"
                ),
            },
        )
        if result.is_success:
            return FlextResult[bool].ok(True)
        return FlextResult[bool].fail(result.error or "")

    # ==========================================================================
    # ARGUMENTS MANAGEMENT
    # ==========================================================================

    def add_argument(self, argument: str) -> FlextResult[bool]:
        """Add command line argument."""
        validation = self._validate_string(argument, "Argument", "Validation failed")
        if validation.is_failure:
            return FlextResult[bool].fail(validation.error or "")

        return self._safe_list_operation(
            "add",
            self.arguments,
            argument,
            error_messages={
                "not_initialized": FlextCliConstants.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
                "exception": FlextCliConstants.ContextErrorMessages.ARGUMENT_ADDITION_FAILED.format(
                    error="{error}"
                ),
            },
        )

    def remove_argument(self, argument: str) -> FlextResult[bool]:
        """Remove command line argument."""
        validation = self._validate_string(argument, "Argument", "Validation failed")
        if validation.is_failure:
            return FlextResult[bool].fail(validation.error or "")

        return self._safe_list_operation(
            "remove",
            self.arguments,
            argument,
            error_messages={
                "not_initialized": FlextCliConstants.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
                "exception": FlextCliConstants.ContextErrorMessages.ARGUMENT_REMOVAL_FAILED.format(
                    error="{error}"
                ),
            },
        )

    # ==========================================================================
    # METADATA MANAGEMENT
    # ==========================================================================

    def set_metadata(
        self, key: str, value: FlextTypes.GeneralValueType
    ) -> FlextResult[bool]:
        """Set context metadata using CLI-specific data types."""
        validation = self._validate_string(key, "Metadata key", "Validation failed")
        if validation.is_failure:
            return FlextResult[bool].fail(validation.error or "")

        try:
            self.context_metadata[key] = value
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ContextErrorMessages.METADATA_SETTING_FAILED.format(
                    error=e
                )
            )

    def get_metadata(self, key: str) -> FlextResult[FlextTypes.GeneralValueType]:
        """Get context metadata value."""
        validation = self._validate_string(
            key, "Metadata key", "Metadata validation failed"
        )
        if validation.is_failure:
            return FlextResult[FlextTypes.GeneralValueType].fail(validation.error or "")

        if key in self.context_metadata:
            return FlextResult[FlextTypes.GeneralValueType].ok(
                self.context_metadata[key]
            )
        return FlextResult[FlextTypes.GeneralValueType].fail(
            FlextCliConstants.ContextErrorMessages.METADATA_KEY_NOT_FOUND.format(
                key=key
            )
        )

    # ==========================================================================
    # CONTEXT INFORMATION
    # ==========================================================================

    def get_context_summary(
        self,
    ) -> FlextResult[dict[str, FlextTypes.JsonValue]]:
        """Get comprehensive context summary."""
        arguments_list = self.arguments if self.arguments is not None else []
        env_vars_dict = (
            self.environment_variables if self.environment_variables is not None else {}
        )

        summary: dict[str, FlextTypes.JsonValue] = {
            FlextCliConstants.ContextDictKeys.CONTEXT_ID: self.id,
            FlextCliConstants.ContextDictKeys.COMMAND: self.command,
            FlextCliConstants.ContextDictKeys.ARGUMENTS_COUNT: len(arguments_list),
            FlextCliConstants.ContextDictKeys.ARGUMENTS: list(arguments_list),
            FlextCliConstants.ContextDictKeys.ENVIRONMENT_VARIABLES_COUNT: len(
                env_vars_dict
            ),
            FlextCliConstants.ContextDictKeys.WORKING_DIRECTORY: self.working_directory,
            FlextCliConstants.ContextDictKeys.IS_ACTIVE: self.is_active,
            FlextCliConstants.ContextDictKeys.CREATED_AT: self.created_at,
            FlextCliConstants.ContextDictKeys.METADATA_KEYS: list(
                self.context_metadata.keys()
            ),
            FlextCliConstants.ContextDictKeys.METADATA_COUNT: len(
                self.context_metadata
            ),
        }

        return FlextResult[dict[str, FlextTypes.JsonValue]].ok(summary)

    def execute(
        self, **_kwargs: FlextTypes.JsonDict
    ) -> FlextResult[FlextTypes.JsonDict]:
        """Execute the CLI context.

        Returns:
            FlextResult with ContextExecutionResult serialized as dict

        """
        init_check = self._ensure_initialized(
            self.arguments,
            FlextCliConstants.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
        )
        if init_check.is_failure:
            return FlextResult[FlextTypes.JsonDict].fail(init_check.error or "")

        # Type narrowing: self.arguments is not None after _ensure_initialized check
        if self.arguments is None:
            return FlextResult[FlextTypes.JsonDict].fail(
                FlextCliConstants.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED
            )

        result_model = FlextCliModels.ContextExecutionResult(
            context_executed=True,
            command=self.command or "",
            arguments_count=len(self.arguments) if self.arguments is not None else 0,
            timestamp=FlextUtilities.Generators.generate_iso_timestamp(),
        )

        # Convert to CliDataDict using DataMapper
        result_dict = FlextUtilities.DataMapper.convert_dict_to_json(
            result_model.model_dump()
        )
        return FlextResult[FlextTypes.JsonDict].ok(result_dict)

    def to_dict(self) -> FlextResult[FlextTypes.JsonDict]:
        """Convert context to dictionary."""
        init_checks = [
            self._ensure_initialized(
                self.arguments,
                FlextCliConstants.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
            ),
            self._ensure_initialized(
                self.environment_variables,
                FlextCliConstants.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
            ),
        ]

        for check in init_checks:
            if check.is_failure:
                return FlextResult[FlextTypes.JsonDict].fail(check.error or "")

        # Convert all values to CliJsonValue for type safety
        result: dict[str, FlextTypes.GeneralValueType] = {
            FlextCliConstants.ContextDictKeys.ID: self.id,
            FlextCliConstants.ContextDictKeys.COMMAND: self.command,
            FlextCliConstants.ContextDictKeys.ARGUMENTS: list(self.arguments)
            if self.arguments
            else [],
            FlextCliConstants.ContextDictKeys.ENVIRONMENT_VARIABLES: dict(
                self.environment_variables
            )
            if self.environment_variables
            else {},
            FlextCliConstants.ContextDictKeys.WORKING_DIRECTORY: self.working_directory,
            FlextCliConstants.ContextDictKeys.CREATED_AT: self.created_at,
            FlextCliConstants.ContextDictKeys.TIMEOUT_SECONDS: self.timeout_seconds,
        }

        return FlextResult[FlextTypes.JsonDict].ok(result)


__all__ = ["FlextCliContext"]
