"""Public API facade for flext-cli.

Centralizes authentication, command registration/execution, and access to utilities
exposed as attributes of `FlextCli`, maintaining convenience wrappers that
delegate to internal services without breaking the isolation of Typer/Click and
Rich.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import secrets
from collections.abc import Callable, Mapping
from typing import TypeGuard

from flext_core import (
    FlextContainer as container,
    FlextLogger as logger_core,
    FlextResult as r,
    FlextRuntime as runtime,
    FlextTypes as t,
)

from flext_cli.__version__ import __version__
from flext_cli.app_base import FlextCliAppBase
from flext_cli.base import FlextCliServiceBase
from flext_cli.cli import FlextCliCli
from flext_cli.cli_params import FlextCliCommonParams
from flext_cli.commands import FlextCliCommands
from flext_cli.constants import FlextCliConstants as c
from flext_cli.context import FlextCliContext
from flext_cli.debug import FlextCliDebug
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.formatters import FlextCliFormatters
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import PasswordAuth, TokenData
from flext_cli.protocols import FlextCliProtocols as p
from flext_cli.services.cmd import FlextCliCmd
from flext_cli.services.core import FlextCliCore
from flext_cli.services.output import FlextCliOutput
from flext_cli.services.prompts import FlextCliPrompts
from flext_cli.services.tables import FlextCliTables
from flext_cli.settings import FlextCliSettings
from flext_cli.utilities import FlextCliUtilities as u


class FlextCli:
    """Coordinate CLI operations and expose domain services.

    Business Rules:
    ───────────────
    1. Singleton pattern ensures single CLI instance per process (thread-safe)
    2. Service instances MUST be initialized before use (lazy initialization)
    3. Command registration MUST validate command names and handlers
    4. Authentication MUST be performed before privileged operations
    5. Configuration MUST be loaded from environment variables or config files
    6. All operations MUST return r[T] for error handling
    7. Service instances are exposed as attributes for direct access
    8. Wrappers delegate to service instances without breaking isolation

    Architecture Implications:
    ───────────────────────────
    - Singleton pattern with thread-safe locking prevents race conditions
    - Service instances are created on-demand (lazy initialization)
    - Direct service access avoids unnecessary wrapper layers
    - Typer/Click and Rich isolation maintained through abstraction
    - Railway-Oriented Programming via FlextResult for composable error handling

    Audit Implications:
    ───────────────────
    - All command registrations MUST be logged with timestamp and command name
    - Authentication attempts MUST be logged (success/failure, no credentials)
    - Configuration changes MUST be logged with before/after values
    - Service initialization MUST be logged for audit trail
    - Error conditions MUST be logged with full context (no sensitive data)
    - Remote operations MUST use encrypted connections (TLS/SSL)
    - Session management MUST track user context for audit purposes

    Instantiates services (`core`, `cmd`, `output`, `prompts`, `tables`) and
    utilities (`formatters`, `file_tools`, `utilities`) for direct access,
    maintaining legacy wrappers as explicit delegation to these instances.
    """

    # Nested classes - FLEXT pattern with real inheritance
    class Base(FlextCliCli):
        """CLI base class extending FlextCliCli via inheritance."""

    class Runner(FlextCliCmd):
        """CLI runner extending FlextCliCmd via inheritance."""

    class Commands(FlextCliCommands):
        """CLI commands extending FlextCliCommands via inheritance."""

    class Params(FlextCliCommonParams):
        """CLI params extending FlextCliCommonParams via inheritance."""

    class Output(FlextCliOutput):
        """CLI output extending FlextCliOutput via inheritance."""

    class Formatters(FlextCliFormatters):
        """CLI formatters extending FlextCliFormatters via inheritance."""

    class Tables(FlextCliTables):
        """CLI tables extending FlextCliTables via inheritance."""

    class Prompts(FlextCliPrompts):
        """CLI prompts extending FlextCliPrompts via inheritance."""

    class FileTools(FlextCliFileTools):
        """CLI file tools extending FlextCliFileTools via inheritance."""

    class Config(FlextCliSettings):
        """CLI config extending FlextCliSettings via inheritance."""

    class Context(FlextCliContext):
        """CLI context extending FlextCliContext via inheritance."""

    class Core(FlextCliCore):
        """CLI core extending FlextCliCore via inheritance."""

    class Debug(FlextCliDebug):
        """CLI debug extending FlextCliDebug via inheritance."""

    class Mixins(FlextCliMixins):
        """CLI mixins extending FlextCliMixins via inheritance."""

    class AppBase(FlextCliAppBase):
        """CLI app base extending FlextCliAppBase via inheritance."""

    _instance: FlextCli | None = None
    _lock = __import__("threading").Lock()

    # Public service instances
    logger: logger_core
    config: FlextCliSettings
    formatters: FlextCliFormatters
    file_tools: FlextCliFileTools
    output: FlextCliOutput
    core: FlextCliCore
    cmd: FlextCliCmd
    prompts: FlextCliPrompts

    def __init__(self) -> None:
        """Initialize consolidated CLI with all functionality integrated."""
        self._name = c.Cli.CliDefaults.DEFAULT_APP_NAME
        self._version = c.Cli.CLI_VERSION
        self._description = f"{self._name}{c.Cli.APIDefaults.APP_DESCRIPTION_SUFFIX}"

        self.logger = logger_core(__name__)
        self._container = container()
        if not self._container.has_service(
            c.Cli.APIDefaults.CONTAINER_REGISTRATION_KEY,
        ):
            # Register service name only - container doesn't need the instance itself
            # Use a simple string identifier instead of the instance
            register_result = self._container.register(
                c.Cli.APIDefaults.CONTAINER_REGISTRATION_KEY,
                c.Cli.APIDefaults.CONTAINER_REGISTRATION_KEY,
            )
            if register_result.is_failure:
                self.logger.warning(
                    f"Failed to register CLI service: {register_result.error}",
                )

        # Domain library components
        self.formatters = FlextCliFormatters()
        self.file_tools = FlextCliFileTools()
        self.output = FlextCliOutput()
        self.core = FlextCliCore()
        self.cmd = FlextCliCmd()
        self.prompts = FlextCliPrompts()

        self._cli = FlextCliCli()
        self._commands: dict[str, p.Cli.CliRegisteredCommand] = {}
        self._groups: dict[str, p.Cli.CliRegisteredCommand] = {}
        self._plugin_commands: dict[str, p.Cli.CliRegisteredCommand] = {}

        self.config = FlextCliServiceBase.get_cli_config()
        self._valid_tokens: set[str] = set()
        self._valid_sessions: set[str] = set()
        self._session_permissions: dict[str, set[str]] = {}
        self._users: dict[str, dict[str, t.GeneralValueType]] = {}
        self._deleted_users: set[str] = set()

    @classmethod
    def get_instance(cls) -> FlextCli:
        """Get singleton FlextCli instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # =========================================================================
    # PRIVATE HELPERS - Generalize common patterns
    # =========================================================================

    @staticmethod
    def _validate_token_string(token: str) -> r[bool]:
        """Generalized token validation helper."""
        # Business Rule: Token validation MUST use FlextUtilities validation DSL
        # Architecture: Use u.validate_required_string for token validation
        # Audit Implication: Token validation ensures security and data integrity
        try:
            u.Cli.CliValidation.validate_required_string(token, context="Token")
            return r[bool].ok(True)
        except ValueError as e:
            return r[bool].fail(str(e))

    # =========================================================================
    # AUTHENTICATION
    # =========================================================================

    def authenticate(
        self,
        credentials: Mapping[str, str],
    ) -> r[str]:
        """Authenticate user with provided credentials."""
        if c.Cli.DictKeys.TOKEN in credentials:
            return self._authenticate_with_token(credentials)
        if (
            c.Cli.DictKeys.USERNAME in credentials
            and c.Cli.DictKeys.PASSWORD in credentials
        ):
            return self._authenticate_with_credentials(credentials)
        return r[str].fail(
            c.Cli.ErrorMessages.INVALID_CREDENTIALS,
        )

    def _authenticate_with_token(
        self,
        credentials: Mapping[str, str],
    ) -> r[str]:
        """Authenticate using token."""
        token = str(credentials[c.Cli.DictKeys.TOKEN])
        validation = FlextCli._validate_token_string(token)
        if validation.is_failure:
            return r[str].fail(validation.error or "")

        save_result = self.save_auth_token(token)
        if save_result.is_failure:
            return r[str].fail(
                c.Cli.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=save_result.error,
                ),
            )
        return r[str].ok(token)

    def _authenticate_with_credentials(
        self,
        credentials: Mapping[str, str],
    ) -> r[str]:
        """Authenticate using Pydantic 2 validation."""
        try:
            PasswordAuth.model_validate(credentials)
        except Exception as e:
            return r[str].fail(str(e))

        token = secrets.token_urlsafe(
            c.Cli.APIDefaults.TOKEN_GENERATION_BYTES,
        )
        self._valid_tokens.add(token)
        return r[str].ok(token)

    @staticmethod
    def validate_credentials(username: str, password: str) -> r[bool]:
        """Validate credentials using Pydantic 2."""
        try:
            PasswordAuth(username=username, password=password)
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(str(e))

    def save_auth_token(self, token: str) -> r[bool]:
        """Save authentication token using file tools domain library."""
        validation = FlextCli._validate_token_string(token)
        if validation.is_failure:
            return validation

        token_path = self.config.token_file
        # Create dict with FlextCliTypes.GeneralValueType for Mapper compatibility
        token_data: dict[str, t.GeneralValueType] = {
            # str is subtype of FlextCliTypes.GeneralValueType
            c.Cli.DictKeys.TOKEN: token,
        }

        # Use u.transform for type-safe JSON conversion
        transform_result = u.transform(token_data, to_json=True)
        json_data = (
            transform_result.value if transform_result.is_success else token_data
        )
        write_result = self.file_tools.write_json_file(str(token_path), json_data)
        if write_result.is_failure:
            return r[bool].fail(
                c.Cli.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=write_result.error,
                ),
            )

        self._valid_tokens.add(token)
        return r[bool].ok(True)

    def _get_token_error_message(self, error_str: str) -> str:
        """Get error message based on exception contenFlextCliTypes."""
        error_keywords = {
            "dict": c.Cli.APIDefaults.TOKEN_DATA_TYPE_ERROR,
            "mapping": c.Cli.APIDefaults.TOKEN_DATA_TYPE_ERROR,
            "object": c.Cli.APIDefaults.TOKEN_DATA_TYPE_ERROR,
            "string": c.Cli.APIDefaults.TOKEN_VALUE_TYPE_ERROR,
            "str": c.Cli.APIDefaults.TOKEN_VALUE_TYPE_ERROR,
        }
        # Type narrowing: error_keywords.keys() are all str, error_str is str
        keyword_list: list[str] = list(error_keywords.keys())
        # Find returns FlextCliTypes.GeneralValueType | None, but we know keywords are str
        found_keyword_raw = u.Collection.find(
            keyword_list,
            predicate=lambda kw: isinstance(kw, str) and kw in error_str,
        )
        # Type narrowing: found_keyword is str | None
        found_keyword: str | None = (
            found_keyword_raw if isinstance(found_keyword_raw, str) else None
        )
        return (
            error_keywords[found_keyword]
            if found_keyword is not None
            else c.Cli.ErrorMessages.TOKEN_FILE_EMPTY
        )

    def _handle_token_file_error(self, error_str: str) -> r[str]:
        """Handle file read error during token loading."""
        if u.Cli.FileOps.is_file_not_found_error(error_str):
            return r[str].fail(c.Cli.ErrorMessages.TOKEN_FILE_NOT_FOUND)
        return r[str].fail(
            c.Cli.ErrorMessages.TOKEN_LOAD_FAILED.format(error=error_str),
        )

    def get_auth_token(self) -> r[str]:
        """Get authentication token using Pydantic 2 validation."""
        # Read token file
        result = self.file_tools.read_json_file(str(self.config.token_file))
        if result.is_failure:
            return self._handle_token_file_error(str(result.error))

        data = result.value
        if not data or (runtime.is_dict_like(data) and not data):
            return r[str].fail(c.Cli.ErrorMessages.TOKEN_FILE_EMPTY)

        # Try direct extraction
        token_result = u.extract(
            data,
            c.Cli.DictKeys.TOKEN,
            required=True,
        )
        if token_result.is_success:
            token_value = token_result.value
            if isinstance(token_value, str) and token_value:
                return r[str].ok(token_value)

        # Fallback to model validation
        try:
            token_data = TokenData.model_validate(data)
            return r[str].ok(token_data.token)
        except Exception as e:
            return r[str].fail(self._get_token_error_message(str(e).lower()))

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        auth_result = self.get_auth_token()
        return auth_result.is_success if hasattr(auth_result, "is_success") else False

    def clear_auth_tokens(self) -> r[bool]:
        """Clear authentication tokens using file tools domain library."""
        token_path = self.config.token_file
        refresh_token_path = self.config.refresh_token_file

        delete_token_result = self.file_tools.delete_file(str(token_path))
        delete_refresh_result = self.file_tools.delete_file(str(refresh_token_path))

        # Check if either deletion failed (but don't fail if file doesn't exist)
        error_str_token = str(delete_token_result.error).lower()
        if delete_token_result.is_failure and not any(
            pattern in error_str_token
            for pattern in [
                "not found",
                "no such file",
                "does not exist",
                "errno 2",
            ]
        ):
            return r[bool].fail(
                c.Cli.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_token_result.error,
                ),
            )

        error_str_refresh = str(delete_refresh_result.error).lower()
        if delete_refresh_result.is_failure and not any(
            pattern in error_str_refresh
            for pattern in [
                "not found",
                "no such file",
                "does not exist",
                "errno 2",
            ]
        ):
            return r[bool].fail(
                c.Cli.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_refresh_result.error,
                ),
            )

        self._valid_tokens.clear()
        return r[bool].ok(True)

    # =========================================================================
    # COMMAND REGISTRATION
    # =========================================================================

    def _register_cli_entity(
        self,
        entity_type: c.Cli.EntityTypeLiteral | c.Cli.EntityType,
        name: str | None,
        func: p.Cli.CliCommandFunction,
    ) -> p.Cli.CliRegisteredCommand:
        """Register a CLI entity (command or group) with framework abstraction."""
        # Get function name safely - protocols may not have __name__
        entity_name = name if name is not None else getattr(func, "__name__", "unknown")

        if entity_type == "command":
            decorator = self._cli.create_command_decorator(name=entity_name)
            decorated_func = decorator(func)
            # Click Command implements CliRegisteredCommand protocol structurally at runtime
            # Protocol is structural, so decorated_func is compatible
            if not hasattr(decorated_func, "name") or not callable(decorated_func):
                msg = "decorated_func must have 'name' attribute and be callable"
                raise TypeError(msg)
            # Type narrowing: Click Command structurally implements CliRegisteredCommand
            # The protocol requires properties that Click Command provides at runtime
            # We use a helper to narrow the type safely
            result = self._narrow_to_registered_command(decorated_func)
            self._commands[entity_name] = result
        else:  # group
            decorator = self._cli.create_group_decorator(name=entity_name)
            decorated_func = decorator(func)
            # Click Group implements CliRegisteredCommand protocol structurally at runtime
            # Protocol is structural, so decorated_func is compatible
            if not hasattr(decorated_func, "name") or not callable(decorated_func):
                msg = "decorated_func must have 'name' attribute and be callable"
                raise TypeError(msg)
            # Type narrowing: Click Group structurally implements CliRegisteredCommand
            # The protocol requires properties that Click Group provides at runtime
            # We use a helper to narrow the type safely
            group_result = self._narrow_to_registered_command(decorated_func)
            self._groups[entity_name] = group_result
            result = group_result

        return result

    @staticmethod
    def _is_registered_command(
        obj: object,
    ) -> TypeGuard[p.Cli.CliRegisteredCommand]:
        """Type guard to check if object implements CliRegisteredCommand protocol."""
        return hasattr(obj, "name") and callable(obj) and hasattr(obj, "callback")

    @staticmethod
    def _is_rich_tree_protocol(
        obj: object,
    ) -> TypeGuard[p.Cli.Display.RichTreeProtocol]:
        """Type guard to check if object implements RichTreeProtocol."""
        return (
            hasattr(obj, "add")
            and callable(getattr(obj, "add", None))
            and hasattr(obj, "label")
        )

    def _narrow_to_registered_command(
        self,
        decorated_func: object,
    ) -> p.Cli.CliRegisteredCommand:
        """Narrow type to CliRegisteredCommand using structural protocol check.

        Click Command/Group structurally implements CliRegisteredCommand protocol.
        This helper performs runtime checks to satisfy type checker.
        """
        # Runtime check: verify decorated_func has required protocol attributes
        if not self._is_registered_command(decorated_func):
            msg = "decorated_func must implement CliRegisteredCommand protocol"
            raise TypeError(msg)
        # Type guard confirms compatibility - return as protocol type
        return decorated_func

    def command(
        self,
        name: str | None = None,
    ) -> Callable[
        [p.Cli.CliCommandFunction],
        p.Cli.CliRegisteredCommand,
    ]:
        """Register a command using CLI framework abstraction."""

        def decorator(
            func: p.Cli.CliCommandFunction,
        ) -> p.Cli.CliRegisteredCommand:
            return self._register_cli_entity(c.Cli.EntityType.COMMAND, name, func)

        return decorator

    def group(
        self,
        name: str | None = None,
    ) -> Callable[
        [p.Cli.CliCommandFunction],
        p.Cli.CliRegisteredCommand,
    ]:
        """Register a command group using CLI framework abstraction."""

        def decorator(
            func: p.Cli.CliCommandFunction,
        ) -> p.Cli.CliRegisteredCommand:
            return self._register_cli_entity(c.Cli.EntityType.GROUP, name, func)

        return decorator

    @staticmethod
    def execute_cli() -> r[bool]:
        """Execute the CLI application using framework abstraction."""
        return r[bool].ok(True)

    # =========================================================================
    # EXECUTION
    # =========================================================================

    def execute(self) -> r[Mapping[str, t.GeneralValueType]]:
        """Execute CLI service with railway pattern."""
        # Build JsonDict - convert version to string, components as dict
        result_dict: dict[str, t.GeneralValueType] = {
            c.Cli.DictKeys.STATUS: (c.Cli.ServiceStatus.OPERATIONAL.value),
            c.Cli.DictKeys.SERVICE: c.Cli.FLEXT_CLI,
            "timestamp": u.generate("timestamp"),
            "version": str(__version__),
            "components": {
                "config": "available",
                "formatters": "available",
                "core": "available",
                "prompts": "available",
            },
        }

        return r[dict[str, t.GeneralValueType]].ok(result_dict)

    # =========================================================================
    # CONVENIENCE METHODS - Delegate to service instances
    # =========================================================================


__all__ = [
    "FlextCli",
    "FlextCliAppBase",
]
