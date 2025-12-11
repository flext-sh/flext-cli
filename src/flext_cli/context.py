"""FLEXT CLI Context - CLI execution context management.

**MODULE**: FlextCliContext - Single primary class for CLI execution context
**SCOPE**: Context management, environment variables, arguments, metadata with type-safe operations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextSettings, r, s
from pydantic import Field

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import c
from flext_cli.models import m
from flext_cli.typings import t
from flext_cli.utilities import u


class FlextCliContext(FlextCliServiceBase):
    """CLI execution context with type-safe operations and FlextResult patterns.

    Business Rules:
    ───────────────
    1. Context MUST be created for each CLI command execution
    2. Context ID MUST be unique (UUID-based generation)
    3. Context MUST track command, arguments, and environment variables
    4. Context timeout MUST be enforced (default 30 seconds, configurable)
    5. Context metadata MUST be immutable after creation (frozen model)
    6. Active context MUST be tracked for session management
    7. Context cleanup MUST happen after command completion
    8. Environment variables MUST be validated before use

    Architecture Implications:
    ───────────────────────────
    - Extends FlextCliServiceBase for consistent logging and container access
    - Uses FlextModelsEntity.Entry for timestamp tracking
    - Frozen model ensures immutability after creation
    - Type-safe operations using t for domain-specific types
    - Railway-Oriented Programming via FlextResult for error handling

    Audit Implications:
    ───────────────────
    - Context creation MUST be logged with context ID and command
    - Context termination MUST be logged with duration and exit code
    - Environment variable access MUST be logged (no sensitive values)
    - Context metadata MUST be preserved for audit trail
    - Timeout events MUST be logged for monitoring
    - Context cleanup MUST be logged for resource tracking

    Manages CLI execution context using FlextCliTypes for domain-specific type safety.
    All operations use FlextResult railway pattern for error handling.
    """

    # Direct attributes - no properties needed
    id: str = ""
    command: str | None = None
    arguments: list[str] | None = Field(default_factory=list)
    environment_variables: dict[str, t.GeneralValueType] | None = Field(
        default_factory=dict,
    )
    working_directory: str | None = None
    context_metadata: dict[str, t.GeneralValueType] = Field(default_factory=dict)

    # Context state
    is_active: bool = False
    created_at: str = ""
    timeout_seconds: int = Field(default=30)

    def __init__(
        self,
        command: str | None = None,
        arguments: list[str] | None = None,
        environment_variables: dict[str, t.GeneralValueType] | None = None,
        working_directory: str | None = None,
        **data: t.GeneralValueType,
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
            data["id"] = u.generate("uuid")

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
            data["created_at"] = u.generate("timestamp")
        if "is_active" not in data:
            data["is_active"] = False

        # Set timeout from global config if not provided
        if "timeout_seconds" not in data:
            global_config = FlextSettings.get_global_instance()
            data["timeout_seconds"] = int(global_config.timeout_seconds)

        # Convert data for super().__init__()
        # FlextService.__init__ accepts **data: t.GeneralValueType
        # Note: mypy has generic type inference issue with FlextService[JsonDict].__init__
        # but runtime accepts dict[str, t.GeneralValueType] as **kwargs: t.GeneralValueType
        if not isinstance(data, dict):
            msg = "data must be dict"
            raise TypeError(msg)
        # Pass data directly - FlextService base class accepts **kwargs: t.GeneralValueType
        # This works at runtime even if mypy complains about generic type inference
        s[dict[str, t.GeneralValueType]].__init__(self, **data)

    # ==========================================================================
    # PRIVATE HELPERS - Generalize common patterns
    # ==========================================================================

    @staticmethod
    def _validate_string(value: str, field_name: str, error_template: str) -> r[bool]:
        """Generalized string validation helper.

        Business Rule:
        ──────────────
        Validates that a string is non-empty using u
        Static method - no instance state needed.
        """
        try:
            # Use runtime alias u.Cli.CliValidation.v_empty for non-empty validation
            validation_result = u.Cli.CliValidation.v_empty(value, name=field_name)
            if validation_result.is_failure:
                raise ValueError(
                    validation_result.error or f"{field_name} cannot be empty",
                )
            return r[bool].ok(True)
        except ValueError as e:
            return r[bool].fail(str(e) or error_template)

    @staticmethod
    def _ensure_initialized(
        value: t.GeneralValueType | None,
        error_message: str,
    ) -> r[bool]:
        """Generalized initialization check helper.

        Business Rule:
        ──────────────
        Checks that a value is not None before proceeding with operations.
        Static method - no instance state needed.
        """
        if value is None:
            return r[bool].fail(error_message)
        return r[bool].ok(True)

    @staticmethod
    def _safe_dict_operation(
        operation: str,
        dict_obj: dict[str, t.GeneralValueType] | None,
        key: str,
        value: t.GeneralValueType | None = None,
        error_messages: dict[str, str] | None = None,
    ) -> r[t.GeneralValueType | bool]:
        """Generalized dict operation helper (get/set/check).

        Business Rule:
        ──────────────
        Performs dict operations (get/set) with consistent error handling.
        Uses early return pattern consolidated into result variable.

        Audit Implications:
        ───────────────────
        - Initialization check prevents null pointer operations
        - Operation type validation ensures only valid operations execute
        - Exception handling captures unexpected errors with context
        """
        default_errors = {
            "not_initialized": c.Cli.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
            "not_found": c.Cli.ContextErrorMessages.ENV_VAR_NOT_FOUND.format(name=key),
            "failed": c.Cli.ErrorMessages.CLI_EXECUTION_ERROR.format(
                error="Operation failed",
            ),
        }
        errors = {**default_errors, **(error_messages or {})}

        # Initialize result - will be overwritten by operation
        result: r[t.GeneralValueType | bool]

        # Check initialization
        init_check = FlextCliContext._ensure_initialized(
            dict_obj,
            errors["not_initialized"],
        )
        if init_check.is_failure or dict_obj is None:
            result = r[t.GeneralValueType | bool].fail(
                init_check.error or errors["not_initialized"],
            )
        else:
            try:
                if operation == "get":
                    result = (
                        r[t.GeneralValueType | bool].ok(dict_obj[key])
                        if key in dict_obj
                        else r[t.GeneralValueType | bool].fail(errors["not_found"])
                    )
                elif operation == "set" and value is not None:
                    dict_obj[key] = value
                    result = r[t.GeneralValueType | bool].ok(True)
                else:
                    result = r[t.GeneralValueType | bool].fail(errors["failed"])
            except Exception as e:
                result = r[t.GeneralValueType | bool].fail(
                    errors.get("exception", str(e)) or errors["failed"],
                )

        return result

    @staticmethod
    def _safe_list_operation(
        operation: str,
        list_obj: list[str] | None,
        value: str,
        error_messages: dict[str, str] | None = None,
    ) -> r[bool]:
        """Generalized list operation helper (add/remove/check).

        Business Rule:
        ──────────────
        Performs list operations (add/remove) with consistent error handling.
        Uses single return point pattern for reduced complexity.

        Audit Implications:
        ───────────────────
        - Initialization check prevents null pointer operations
        - Operation type validation ensures only valid operations execute
        - Exception handling captures unexpected errors with formatted context
        """
        default_errors = {
            "not_initialized": c.Cli.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
            "not_found": c.Cli.ContextErrorMessages.ARGUMENT_NOT_FOUND.format(
                argument=value,
            ),
            "failed": c.Cli.ErrorMessages.CLI_EXECUTION_ERROR.format(
                error="Operation failed",
            ),
        }
        errors = {**default_errors, **(error_messages or {})}

        # Initialize result
        result: r[bool]

        # Check initialization
        init_check = FlextCliContext._ensure_initialized(
            list_obj,
            errors["not_initialized"],
        )
        if init_check.is_failure or list_obj is None:
            result = r[bool].fail(init_check.error or errors["not_initialized"])
        else:
            try:
                if operation == "add":
                    list_obj.append(value)
                    result = r[bool].ok(True)
                elif operation == "remove":
                    if value in list_obj:
                        list_obj.remove(value)
                        result = r[bool].ok(True)
                    else:
                        result = r[bool].fail(errors["not_found"])
                else:
                    result = r[bool].fail(errors["failed"])
            except Exception as e:
                exception_template = errors.get("exception", "")
                exception_msg = (
                    exception_template.format(error=str(e))
                    if exception_template and "{error}" in exception_template
                    else (str(e) if exception_template else errors["failed"])
                )
                result = r[bool].fail(exception_msg)

        return result

    # ==========================================================================
    # CONTEXT STATE MANAGEMENT
    # ==========================================================================

    def activate(self) -> r[bool]:
        """Activate CLI context for execution."""
        if self.is_active:
            return r[bool].fail(c.Cli.ContextErrorMessages.CONTEXT_ALREADY_ACTIVE)
        # Business Rule: Model is frozen, must use object.__setattr__
        # Architecture: Frozen model prevents direct assignment
        # Audit Implication: Attribute changes are tracked and validated by Pydantic
        self.is_active = True
        return r[bool].ok(True)

    def deactivate(self) -> r[bool]:
        """Deactivate CLI context."""
        if not self.is_active:
            return r[bool].fail(c.Cli.ContextErrorMessages.CONTEXT_NOT_CURRENTLY_ACTIVE)
        # Business Rule: Model is frozen, must use setattr
        # Architecture: Frozen model prevents direct assignment
        # Audit Implication: Attribute changes are tracked and validated by Pydantic
        self.is_active = False
        return r[bool].ok(True)

    # ==========================================================================
    # ENVIRONMENT VARIABLES
    # ==========================================================================

    def get_environment_variable(self, name: str) -> r[str]:
        """Get specific environment variable value."""
        validation = FlextCliContext._validate_string(
            name,
            "Variable name",
            "Environment variable validation failed",
        )
        if validation.is_failure:
            return r[str].fail(validation.error or "")

        result = self._safe_dict_operation(
            "get",
            self.environment_variables,
            name,
            error_messages={
                "not_initialized": c.Cli.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
                "not_found": c.Cli.ContextErrorMessages.ENV_VAR_NOT_FOUND.format(
                    name=name
                ),
                "exception": c.Cli.ContextErrorMessages.ENV_VAR_RETRIEVAL_FAILED.format(
                    error="{error}",
                ),
            },
        )
        if result.is_success:
            # Use .value directly instead of deprecated .value
            return r[str].ok(str(result.value))
        return r[str].fail(result.error or "")

    def set_environment_variable(self, name: str, value: str) -> r[bool]:
        """Set environment variable value."""
        validation = FlextCliContext._validate_string(
            name,
            "Variable name",
            "Environment variable setting failed",
        )
        if validation.is_failure:
            return r[bool].fail(validation.error or "")

        # validation.is_success is True at this point (after failure check)
        # value is validated and guaranteed to be str via validation

        result = self._safe_dict_operation(
            "set",
            self.environment_variables,
            name,
            value,
            error_messages={
                "not_initialized": c.Cli.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
                "exception": c.Cli.ContextErrorMessages.ENV_VAR_SETTING_FAILED.format(
                    error="{error}",
                ),
            },
        )
        if result.is_success:
            return r[bool].ok(True)
        return r[bool].fail(result.error or "")

    # ==========================================================================
    # ARGUMENTS MANAGEMENT
    # ==========================================================================

    def add_argument(self, argument: str) -> r[bool]:
        """Add command line argument."""
        validation = FlextCliContext._validate_string(
            argument,
            "Argument",
            "Validation failed",
        )
        if validation.is_failure:
            return r[bool].fail(validation.error or "")

        return self._safe_list_operation(
            "add",
            self.arguments,
            argument,
            error_messages={
                "not_initialized": c.Cli.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
                "exception": c.Cli.ContextErrorMessages.ARGUMENT_ADDITION_FAILED.format(
                    error="{error}",
                ),
            },
        )

    def remove_argument(self, argument: str) -> r[bool]:
        """Remove command line argument."""
        validation = FlextCliContext._validate_string(
            argument,
            "Argument",
            "Validation failed",
        )
        if validation.is_failure:
            return r[bool].fail(validation.error or "")

        return self._safe_list_operation(
            "remove",
            self.arguments,
            argument,
            error_messages={
                "not_initialized": c.Cli.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
                "exception": c.Cli.ContextErrorMessages.ARGUMENT_REMOVAL_FAILED.format(
                    error="{error}",
                ),
            },
        )

    # ==========================================================================
    # METADATA MANAGEMENT
    # ==========================================================================

    def set_metadata(self, key: str, value: t.GeneralValueType) -> r[bool]:
        """Set context metadata using CLI-specific data types."""
        validation = FlextCliContext._validate_string(
            key,
            "Metadata key",
            "Validation failed",
        )
        if validation.is_failure:
            return r[bool].fail(validation.error or "")

        try:
            self.context_metadata[key] = value
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(
                c.Cli.ContextErrorMessages.METADATA_SETTING_FAILED.format(error=e),
            )

    def get_metadata(self, key: str) -> r[t.GeneralValueType]:
        """Get context metadata value."""
        validation = FlextCliContext._validate_string(
            key,
            "Metadata key",
            "Metadata validation failed",
        )
        if validation.is_failure:
            return r[t.GeneralValueType].fail(validation.error or "")

        if key in self.context_metadata:
            return r[t.GeneralValueType].ok(self.context_metadata[key])
        return r[t.GeneralValueType].fail(
            c.Cli.ContextErrorMessages.METADATA_KEY_NOT_FOUND.format(key=key),
        )

    # ==========================================================================
    # CONTEXT INFORMATION
    # ==========================================================================

    def get_context_summary(
        self,
    ) -> r[dict[str, t.JsonValue]]:
        """Get comprehensive context summary."""
        arguments_list = self.arguments if self.arguments is not None else []
        env_vars_dict = (
            self.environment_variables if self.environment_variables is not None else {}
        )

        summary: dict[str, t.JsonValue] = {
            c.Cli.ContextDictKeys.CONTEXT_ID: self.id,
            c.Cli.ContextDictKeys.COMMAND: self.command,
            c.Cli.ContextDictKeys.ARGUMENTS_COUNT: len(arguments_list),
            c.Cli.ContextDictKeys.ARGUMENTS: list(arguments_list),
            c.Cli.ContextDictKeys.ENVIRONMENT_VARIABLES_COUNT: len(env_vars_dict),
            c.Cli.ContextDictKeys.WORKING_DIRECTORY: self.working_directory,
            c.Cli.ContextDictKeys.IS_ACTIVE: self.is_active,
            c.Cli.ContextDictKeys.CREATED_AT: self.created_at,
            c.Cli.ContextDictKeys.METADATA_KEYS: list(self.context_metadata.keys()),
            c.Cli.ContextDictKeys.METADATA_COUNT: len(self.context_metadata),
        }

        return r[dict[str, t.JsonValue]].ok(summary)

    def execute(
        self, **_kwargs: dict[str, t.GeneralValueType]
    ) -> r[dict[str, t.GeneralValueType]]:
        """Execute the CLI context.

        Returns:
            FlextResult with ContextExecutionResult serialized as dict

        """
        init_check = FlextCliContext._ensure_initialized(
            self.arguments,
            c.Cli.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
        )
        if init_check.is_failure:
            return r[dict[str, t.GeneralValueType]].fail(init_check.error or "")

        # Type narrowing: self.arguments is not None after _ensure_initialized check
        # Arguments are guaranteed to be not None after successful initialization check
        # Extract arguments_count safely
        args_count = len(self.arguments) if self.arguments is not None else 0
        result_model = m.Cli.ContextExecutionResult(
            context_executed=True,
            command=self.command or "",
            arguments_count=args_count,
            timestamp=u.generate("timestamp"),
        )

        # Use u.transform for JSON conversion
        transform_result = u.transform(result_model.model_dump(), to_json=True)
        # Use .value directly instead of deprecated .value
        result_dict = (
            transform_result.value
            if transform_result.is_success
            else result_model.model_dump()
        )
        return r[dict[str, t.GeneralValueType]].ok(result_dict)

    def to_dict(self) -> r[dict[str, t.GeneralValueType]]:
        """Convert context to dictionary."""
        init_checks = [
            FlextCliContext._ensure_initialized(
                self.arguments,
                c.Cli.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
            ),
            FlextCliContext._ensure_initialized(
                self.environment_variables,
                c.Cli.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
            ),
        ]

        for check in init_checks:
            if check.is_failure:
                return r[dict[str, t.GeneralValueType]].fail(check.error or "")

        # Convert all values to t.GeneralValueType for type safety
        result: dict[str, t.GeneralValueType] = {
            c.Cli.ContextDictKeys.ID: self.id,
            c.Cli.ContextDictKeys.COMMAND: self.command,
            c.Cli.ContextDictKeys.ARGUMENTS: list(self.arguments)
            if self.arguments
            else [],
            c.Cli.ContextDictKeys.ENVIRONMENT_VARIABLES: dict(
                self.environment_variables
            )
            if self.environment_variables
            else {},
            c.Cli.ContextDictKeys.WORKING_DIRECTORY: self.working_directory,
            c.Cli.ContextDictKeys.CREATED_AT: self.created_at,
            c.Cli.ContextDictKeys.TIMEOUT_SECONDS: self.timeout_seconds,
        }

        return r[dict[str, t.GeneralValueType]].ok(result)


__all__ = ["FlextCliContext"]
