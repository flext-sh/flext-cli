"""FLEXT CLI Context - CLI execution context management."""

from __future__ import annotations

import uuid
from collections.abc import Mapping, MutableMapping
from datetime import UTC, datetime

from flext_core import r
from pydantic import BaseModel, ConfigDict, Field, field_validator

from flext_cli.constants import c
from flext_cli.models import m
from flext_cli.typings import t
from flext_cli.utilities import u


class FlextCliContext(BaseModel):
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
    """

    model_config = ConfigDict(frozen=False, validate_assignment=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    command: str | None = None
    arguments: list[str] | None = Field(default_factory=list)
    environment_variables: dict[str, t.JsonValue] | None = Field(default_factory=dict)
    working_directory: str | None = None
    context_metadata: dict[str, t.JsonValue] = Field(default_factory=dict)
    is_active: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    timeout_seconds: int = Field(default=30)

    @field_validator("id", mode="before")
    @classmethod
    def _ensure_id_generated(cls, v: str) -> str:
        """Generate UUID if id is empty."""
        return v or str(uuid.uuid4())

    def activate(self) -> r[bool]:
        """Activate the context for session management."""
        if self.is_active:
            return r[bool].fail("Context is already active")
        self.is_active = True
        return r[bool].ok(value=True)

    def deactivate(self) -> r[bool]:
        """Deactivate the context."""
        if not self.is_active:
            return r[bool].fail("Context is not active")
        self.is_active = False
        return r[bool].ok(value=True)

    @staticmethod
    def _validate_string(value: str, field_name: str, error_template: str) -> r[bool]:
        """Validate non-empty string using u."""
        try:
            result = u.Cli.CliValidation.v_empty(value, name=field_name)
            if result.is_failure:
                raise ValueError(result.error or f"{field_name} cannot be empty")
            return r[bool].ok(value=True)
        except ValueError as e:
            return r[bool].fail(str(e) or error_template)

    @staticmethod
    def _ensure_initialized(value: t.JsonValue | None, error_message: str) -> r[bool]:
        """Check that a value is not None."""
        if value is None:
            return r[bool].fail(error_message)
        return r[bool].ok(value=True)

    @staticmethod
    def _safe_dict_operation(
        operation: str,
        dict_obj: MutableMapping[str, t.JsonValue] | None,
        key: str,
        value: t.JsonValue | None = None,
        error_messages: Mapping[str, str] | None = None,
    ) -> r[t.JsonValue | bool]:
        """Perform dict get/set with consistent error handling."""
        errors = {
            "not_initialized": c.Cli.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
            "not_found": c.Cli.ContextErrorMessages.ENV_VAR_NOT_FOUND.format(name=key),
            "failed": c.Cli.ErrorMessages.CLI_EXECUTION_ERROR.format(
                error="Operation failed"
            ),
            **(error_messages or {}),
        }
        if dict_obj is None:
            return r[t.JsonValue | bool].fail(errors["not_initialized"])
        try:
            if operation == "get":
                if key in dict_obj:
                    return r[t.JsonValue | bool].ok(dict_obj[key])
                return r[t.JsonValue | bool].fail(errors["not_found"])
            if operation == "set" and value is not None:
                dict_obj[key] = value
                return r[t.JsonValue | bool].ok(True)
            return r[t.JsonValue | bool].fail(errors["failed"])
        except Exception as e:
            return r[t.JsonValue | bool].fail(
                errors.get("exception", str(e)) or errors["failed"]
            )

    @staticmethod
    def _safe_list_operation(
        operation: str,
        list_obj: list[str] | None,
        value: str,
        error_messages: Mapping[str, str] | None = None,
    ) -> r[bool]:
        """Perform list add/remove with consistent error handling."""
        errors = {
            "not_initialized": c.Cli.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
            "not_found": c.Cli.ContextErrorMessages.ARGUMENT_NOT_FOUND.format(
                argument=value
            ),
            "failed": c.Cli.ErrorMessages.CLI_EXECUTION_ERROR.format(
                error="Operation failed"
            ),
            **(error_messages or {}),
        }

        init_check = FlextCliContext._ensure_initialized(
            list_obj,
            errors["not_initialized"],
        )
        if init_check.is_failure:
            return r[bool].fail(init_check.error or errors["not_initialized"])

        if list_obj is None:
            return r[bool].fail(errors["not_initialized"])

        try:
            if operation == "add":
                return FlextCliContext._perform_add(list_obj, value)

            if operation == "remove":
                return FlextCliContext._perform_remove(
                    list_obj, value, errors["not_found"]
                )

            return r[bool].fail(errors["failed"])
        except Exception as e:
            tmpl = errors.get("exception", "")
            msg = (
                tmpl.format(error=str(e))
                if tmpl and "{error}" in tmpl
                else (str(e) if tmpl else errors["failed"])
            )
            return r[bool].fail(msg)

    @staticmethod
    def _perform_add(list_obj: list[str], value: str) -> r[bool]:
        """Perform add operation on initialized list."""
        list_obj.append(value)
        return r[bool].ok(value=True)

    @staticmethod
    def _perform_remove(
        list_obj: list[str],
        value: str,
        not_found_error: str,
    ) -> r[bool]:
        """Perform remove operation on initialized list."""
        if value in list_obj:
            list_obj.remove(value)
            return r[bool].ok(value=True)
        return r[bool].fail(not_found_error)

    def _validated_op(self, name: str, field: str, error: str) -> r[bool] | None:
        """Validate string and return failure or None to continue."""
        v = FlextCliContext._validate_string(name, field, error)
        return r[bool].fail(v.error or "") if v.is_failure else None

    def get_environment_variable(self, name: str) -> r[str]:
        """Get specific environment variable value."""
        if (
            fail := self._validated_op(
                name, "Variable name", "Environment variable validation failed"
            )
        ) is not None:
            return r[str].fail(fail.error or "")
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
                    error="{error}"
                ),
            },
        )
        return (
            r[str].ok(str(result.value))
            if result.is_success
            else r[str].fail(result.error or "")
        )

    def set_environment_variable(self, name: str, value: str) -> r[bool]:
        """Set environment variable value."""
        if (
            fail := self._validated_op(
                name, "Variable name", "Environment variable setting failed"
            )
        ) is not None:
            return fail
        result = self._safe_dict_operation(
            "set",
            self.environment_variables,
            name,
            value,
            error_messages={
                "not_initialized": c.Cli.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
                "exception": c.Cli.ContextErrorMessages.ENV_VAR_SETTING_FAILED.format(
                    error="{error}"
                ),
            },
        )
        return (
            r[bool].ok(value=True)
            if result.is_success
            else r[bool].fail(result.error or "")
        )

    def add_argument(self, argument: str) -> r[bool]:
        """Add command line argument."""
        if (
            fail := self._validated_op(argument, "Argument", "Validation failed")
        ) is not None:
            return fail
        return self._safe_list_operation(
            "add",
            self.arguments,
            argument,
            error_messages={
                "not_initialized": c.Cli.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
                "exception": c.Cli.ContextErrorMessages.ARGUMENT_ADDITION_FAILED.format(
                    error="{error}"
                ),
            },
        )

    def remove_argument(self, argument: str) -> r[bool]:
        """Remove command line argument."""
        if (
            fail := self._validated_op(argument, "Argument", "Validation failed")
        ) is not None:
            return fail
        return self._safe_list_operation(
            "remove",
            self.arguments,
            argument,
            error_messages={
                "not_initialized": c.Cli.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
                "exception": c.Cli.ContextErrorMessages.ARGUMENT_REMOVAL_FAILED.format(
                    error="{error}"
                ),
            },
        )

    def set_metadata(self, key: str, value: t.JsonValue) -> r[bool]:
        """Set context metadata using CLI-specific data types."""
        if (
            fail := self._validated_op(key, "Metadata key", "Validation failed")
        ) is not None:
            return fail
        try:
            self.context_metadata[key] = value
            return r[bool].ok(value=True)
        except Exception as e:
            return r[bool].fail(
                c.Cli.ContextErrorMessages.METADATA_SETTING_FAILED.format(error=e),
            )

    def get_metadata(self, key: str) -> r[t.JsonValue]:
        """Get context metadata value."""
        if (
            fail := self._validated_op(
                key, "Metadata key", "Metadata validation failed"
            )
        ) is not None:
            return r[t.JsonValue].fail(fail.error or "")
        if key in self.context_metadata:
            return r[t.JsonValue].ok(self.context_metadata[key])
        return r[t.JsonValue].fail(
            c.Cli.ContextErrorMessages.METADATA_KEY_NOT_FOUND.format(key=key),
        )

    def get_context_summary(self) -> r[Mapping[str, t.JsonValue]]:
        """Get comprehensive context summary."""
        args = self.arguments or []
        env = self.environment_variables or {}
        k = c.Cli.ContextDictKeys
        summary: dict[str, t.JsonValue] = {
            k.CONTEXT_ID: self.id,
            k.COMMAND: self.command,
            k.ARGUMENTS_COUNT: len(args),
            k.ARGUMENTS: list(args),
            k.ENVIRONMENT_VARIABLES_COUNT: len(env),
            k.WORKING_DIRECTORY: self.working_directory,
            k.IS_ACTIVE: self.is_active,
            k.CREATED_AT: self.created_at,
            k.METADATA_KEYS: list(self.context_metadata.keys()),
            k.METADATA_COUNT: len(self.context_metadata),
        }
        return r[Mapping[str, t.JsonValue]].ok(summary)

    def execute(self) -> r[m.Cli.ContextExecutionResult]:
        """Execute the CLI context."""
        init_check = FlextCliContext._ensure_initialized(
            self.arguments,
            c.Cli.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
        )
        if init_check.is_failure:
            return r[m.Cli.ContextExecutionResult].fail(init_check.error or "")
        return r[m.Cli.ContextExecutionResult].ok(
            m.Cli.ContextExecutionResult(
                context_executed=True,
                command=self.command or "",
                arguments_count=len(self.arguments)
                if self.arguments is not None
                else 0,
                timestamp=u.generate("timestamp"),
            )
        )

    def to_dict(self) -> r[Mapping[str, t.JsonValue]]:
        """Convert context to dictionary."""
        for field_val, err_msg in [
            (
                self.arguments,
                c.Cli.ContextErrorMessages.ARGUMENTS_NOT_INITIALIZED,
            ),
            (
                self.environment_variables,
                c.Cli.ContextErrorMessages.ENV_VARS_NOT_INITIALIZED,
            ),
        ]:
            check = FlextCliContext._ensure_initialized(field_val, err_msg)
            if check.is_failure:
                return r[Mapping[str, t.JsonValue]].fail(check.error or "")
        k = c.Cli.ContextDictKeys
        result: dict[str, t.JsonValue] = {
            k.ID: self.id,
            k.COMMAND: self.command,
            k.ARGUMENTS: list(self.arguments) if self.arguments else [],
            k.ENVIRONMENT_VARIABLES: dict(self.environment_variables)
            if self.environment_variables
            else {},
            k.WORKING_DIRECTORY: self.working_directory,
            k.CREATED_AT: self.created_at,
            k.TIMEOUT_SECONDS: self.timeout_seconds,
        }
        return r[Mapping[str, t.JsonValue]].ok(result)


__all__ = ["FlextCliContext"]
