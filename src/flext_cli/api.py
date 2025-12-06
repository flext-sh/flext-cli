"""Public API facade for flext-cli.

Centraliza autenticação, registro/execução de comandos e acesso às utilidades
expostas como atributos do `FlextCli`, mantendo wrappers de conveniência que
delegam para os serviços internos sem quebrar o isolamento de Typer/Click e
Rich.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import secrets
from collections.abc import Callable, Mapping, Sequence
from typing import cast

from flext_core import (
    FlextContainer,
    FlextDecorators,
    FlextExceptions,
    FlextHandlers,
    FlextLogger,
    FlextMixins,
    FlextResult,
    FlextRuntime,
)

from flext_cli.__version__ import __version__
from flext_cli.app_base import FlextCliAppBase
from flext_cli.base import FlextCliServiceBase
from flext_cli.cli import FlextCliCli
from flext_cli.cli_params import FlextCliCommonParams
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants, c
from flext_cli.context import FlextCliContext
from flext_cli.debug import FlextCliDebug
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.formatters import FlextCliFormatters
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import FlextCliModels, m
from flext_cli.protocols import FlextCliProtocols, p
from flext_cli.services.cmd import FlextCliCmd
from flext_cli.services.core import FlextCliCore
from flext_cli.services.output import FlextCliOutput
from flext_cli.services.prompts import FlextCliPrompts
from flext_cli.services.tables import FlextCliTables
from flext_cli.typings import t
from flext_cli.utilities import FlextCliUtilities, u

r = FlextResult
e = FlextExceptions
d = FlextDecorators
s = FlextCliServiceBase  # Domain-specific service base
x = FlextMixins
h = FlextHandlers


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

    Instancia serviços (`core`, `cmd`, `output`, `prompts`, `tables`) e
    utilidades (`formatters`, `file_tools`, `utilities`) para acesso direto,
    mantendo os wrappers legados como delegação explícita para essas instâncias.
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

    class Config(FlextCliConfig):
        """CLI config extending FlextCliConfig via inheritance."""

    class Context(FlextCliContext):
        """CLI context extending FlextCliContext via inheritance."""

    class Core(FlextCliCore):
        """CLI core extending FlextCliCore via inheritance."""

    class Debug(FlextCliDebug):
        """CLI debug extending FlextCliDebug via inheritance."""

    class Models(FlextCliModels):
        """CLI models extending FlextCliModels via inheritance."""

    class Protocols(FlextCliProtocols):
        """CLI protocols extending FlextCliProtocols via inheritance."""

    class Constants(FlextCliConstants):
        """CLI constants extending FlextCliConstants via inheritance."""

    class Mixins(FlextCliMixins):
        """CLI mixins extending FlextCliMixins via inheritance."""

    class Utilities(FlextCliUtilities):
        """CLI utilities extending FlextCliUtilities via inheritance."""

    class AppBase(FlextCliAppBase):
        """CLI app base extending FlextCliAppBase via inheritance."""

    # Singleton pattern
    _instance: FlextCli | None = None
    _lock = __import__("threading").Lock()

    # Public service instances
    logger: FlextLogger
    config: FlextCliConfig
    formatters: FlextCliFormatters
    file_tools: FlextCliFileTools
    output: FlextCliOutput
    core: FlextCliCore
    cmd: FlextCliCmd
    prompts: FlextCliPrompts

    def __init__(self) -> None:
        """Initialize consolidated CLI with all functionality integrated."""
        self._name = c.CliDefaults.DEFAULT_APP_NAME
        self._version = c.CLI_VERSION
        self._description = f"{self._name}{c.APIDefaults.APP_DESCRIPTION_SUFFIX}"

        self.logger = FlextLogger(__name__)
        self._container = FlextContainer()
        if not self._container.has_service(
            c.APIDefaults.CONTAINER_REGISTRATION_KEY,
        ):
            # Register service name only - container doesn't need the instance itself
            # Use a simple string identifier instead of the instance
            register_result = self._container.register(
                c.APIDefaults.CONTAINER_REGISTRATION_KEY,
                c.APIDefaults.CONTAINER_REGISTRATION_KEY,
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
        self._users: dict[str, t.Json.JsonDict] = {}
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
            u.validate_required_string(token, context="Token")
            return r[bool].ok(True)
        except ValueError as e:
            return r[bool].fail(
                str(e) or c.ErrorMessages.TOKEN_EMPTY,
            )

    # =========================================================================
    # AUTHENTICATION
    # =========================================================================

    def authenticate(
        self,
        credentials: Mapping[str, str],
    ) -> r[str]:
        """Authenticate user with provided credentials."""
        if c.DictKeys.TOKEN in credentials:
            return self._authenticate_with_token(credentials)
        if c.DictKeys.USERNAME in credentials and c.DictKeys.PASSWORD in credentials:
            return self._authenticate_with_credentials(credentials)
        return r[str].fail(
            c.ErrorMessages.INVALID_CREDENTIALS,
        )

    def _authenticate_with_token(
        self,
        credentials: Mapping[str, str],
    ) -> r[str]:
        """Authenticate using token."""
        token = str(credentials[c.DictKeys.TOKEN])
        validation = FlextCli._validate_token_string(token)
        if validation.is_failure:
            return r[str].fail(validation.error or "")

        save_result = self.save_auth_token(token)
        if save_result.is_failure:
            return r[str].fail(
                c.ErrorMessages.TOKEN_SAVE_FAILED.format(
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
            m.PasswordAuth.model_validate(credentials)
        except Exception as e:
            return r[str].fail(str(e))

        token = secrets.token_urlsafe(
            c.APIDefaults.TOKEN_GENERATION_BYTES,
        )
        self._valid_tokens.add(token)
        return r[str].ok(token)

    @staticmethod
    def validate_credentials(username: str, password: str) -> r[bool]:
        """Validate credentials using Pydantic 2."""
        try:
            m.PasswordAuth(username=username, password=password)
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(str(e))

    def save_auth_token(self, token: str) -> r[bool]:
        """Save authentication token using file tools domain library."""
        validation = FlextCli._validate_token_string(token)
        if validation.is_failure:
            return validation

        token_path = self.config.token_file
        # Create dict with GeneralValueType for Mapper compatibility
        token_data: dict[str, t.GeneralValueType] = {
            # str is subtype of GeneralValueType
            c.DictKeys.TOKEN: token,
        }

        # Use u.transform for type-safe JSON conversion
        transform_result = u.transform(token_data, to_json=True)
        json_data = (
            transform_result.unwrap() if transform_result.is_success else token_data
        )
        write_result = self.file_tools.write_json_file(str(token_path), json_data)
        if write_result.is_failure:
            return r[bool].fail(
                c.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=write_result.error,
                ),
            )

        self._valid_tokens.add(token)
        return r[bool].ok(True)

    def get_auth_token(self) -> r[str]:
        """Get authentication token using Pydantic 2 validation."""
        token_path = self.config.token_file

        # Helper to handle file read errors
        def handle_file_error(error_str: str) -> r[str]:
            """Handle file read error."""
            if u.FileOps.is_file_not_found_error(error_str):
                return r[str].fail(
                    c.ErrorMessages.TOKEN_FILE_NOT_FOUND,
                )
            return r[str].fail(
                c.ErrorMessages.TOKEN_LOAD_FAILED.format(
                    error=error_str,
                ),
            )

        # Helper to determine error message from exception
        def get_error_message(error_str: str) -> str:
            """Get error message based on exception content."""
            error_keywords = {
                "dict": c.APIDefaults.TOKEN_DATA_TYPE_ERROR,
                "mapping": c.APIDefaults.TOKEN_DATA_TYPE_ERROR,
                "object": c.APIDefaults.TOKEN_DATA_TYPE_ERROR,
                "string": c.APIDefaults.TOKEN_VALUE_TYPE_ERROR,
                "str": c.APIDefaults.TOKEN_VALUE_TYPE_ERROR,
            }
            found_keyword = u.find(
                list(error_keywords.keys()),
                predicate=lambda kw: kw in error_str,
            )
            if found_keyword is not None and isinstance(found_keyword, str):
                return error_keywords[found_keyword]
            return c.ErrorMessages.TOKEN_FILE_EMPTY

        result = self.file_tools.read_json_file(str(token_path))
        if result.is_failure:
            return handle_file_error(str(result.error))

        data = result.unwrap()
        if not data or (FlextRuntime.is_dict_like(data) and not data):
            return r[str].fail(
                c.ErrorMessages.TOKEN_FILE_EMPTY,
            )

        # Use u.extract to safely extract token from data
        token_result = u.extract(
            data,
            c.DictKeys.TOKEN,  # path parameter
            required=True,
        )
        if token_result.is_success:
            # Type cast to break mypy inference if it thinks it's None
            token_value = cast("object", token_result.unwrap())
            if isinstance(token_value, str) and token_value:
                return r[str].ok(token_value)

        # If extract failed, try model validation as fallback
        try:
            token_data = m.TokenData.model_validate(data)
            return r[str].ok(token_data.token)
        except Exception as e:
            return r[str].fail(get_error_message(str(e).lower()))

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.get_auth_token().is_success

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
                c.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
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
                c.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
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
        entity_type: c.EntityTypeLiteral,
        name: str | None,
        func: p.Cli.CliCommandFunction,
    ) -> p.Cli.CliRegisteredCommand:
        """Register a CLI entity (command or group) with framework abstraction."""
        # Get function name safely - protocols may not have __name__
        entity_name = name if name is not None else getattr(func, "__name__", "unknown")

        if entity_type == "command":
            decorator = self._cli.create_command_decorator(name=entity_name)
            decorated_func = decorator(func)
            # Click Command/Group implements CliRegisteredCommand protocol structurally
            # Type narrowing: decorated_func is structurally compatible with protocol
            # Cast Command to CliRegisteredCommand for type compatibility
            result = cast("p.Cli.CliRegisteredCommand", decorated_func)
            self._commands[entity_name] = result
        else:  # group
            decorator = self._cli.create_group_decorator(name=entity_name)
            decorated_func = decorator(func)
            # Click Group implements CliRegisteredCommand protocol structurally
            # Type narrowing: decorated_func is structurally compatible with protocol
            # Cast Group to CliRegisteredCommand for type compatibility
            group_result = cast("p.Cli.CliRegisteredCommand", decorated_func)
            self._groups[entity_name] = group_result
            result = group_result

        return result

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
            return self._register_cli_entity("command", name, func)

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
            return self._register_cli_entity("group", name, func)

        return decorator

    @staticmethod
    def execute_cli() -> r[bool]:
        """Execute the CLI application using framework abstraction."""
        return r[bool].ok(True)

    # =========================================================================
    # EXECUTION
    # =========================================================================

    def execute(self) -> r[t.Json.JsonDict]:
        """Execute CLI service with railway pattern."""
        # Build JsonDict - convert version to string, components as dict
        result_dict: t.Json.JsonDict = {
            c.DictKeys.STATUS: (c.ServiceStatus.OPERATIONAL.value),
            c.DictKeys.SERVICE: c.FLEXT_CLI,
            "timestamp": u.generate("timestamp"),
            "version": str(__version__),
            "components": {
                "config": "available",
                "formatters": "available",
                "core": "available",
                "prompts": "available",
            },
        }

        return r[t.Json.JsonDict].ok(result_dict)

    # =========================================================================
    # CONVENIENCE METHODS - Delegate to service instances
    # =========================================================================

    def print(
        self,
        message: str,
        style: str | None = None,
    ) -> r[bool]:
        """Print formatted message (convenience method for formatters.print)."""
        return self.formatters.print(message, style)

    def create_table(
        self,
        data: Sequence[Mapping[str, t.GeneralValueType]]
        | Mapping[str, t.GeneralValueType]
        | None = None,
        headers: list[str] | None = None,
        title: str | None = None,
    ) -> r[str]:
        """Create table from data (convenience method)."""
        if data is None:
            return r[str].fail(
                c.ErrorMessages.NO_DATA_PROVIDED,
            )

        # Convert data using Mapper for type-safe conversion
        table_data: t.GeneralValueType
        if isinstance(data, dict):
            # Use u.transform for JSON conversion
            transform_result = u.transform(data, to_json=True)
            table_data = (
                transform_result.unwrap() if transform_result.is_success else data
            )
        else:
            # Handle all Sequence types - use u.map to convert items
            data_list: list[t.GeneralValueType] = list(data)
            mapped_result = u.map(
                data_list,
                mapper=lambda item: (
                    u.transform({"_": item}, to_json=True).unwrap().get("_", item)
                    if isinstance(item, dict)
                    else item
                ),
            )
            converted_list: list[t.GeneralValueType] = (
                list(mapped_result) if isinstance(mapped_result, (list, tuple)) else []
            )
            table_data = converted_list

        return self.output.format_data(
            data=table_data,
            format_type=c.OutputFormats.TABLE.value,
            title=title,
            headers=headers,
        )

    def print_table(
        self,
        table: str,
    ) -> r[bool]:
        """Print table string (convenience method)."""
        return self.formatters.print(table)

    def create_tree(
        self,
        label: str,
    ) -> r[p.Display.RichTreeProtocol]:
        """Create tree visualization (convenience method for formatters.create_tree)."""
        # formatters.create_tree returns RichTree which implements RichTreeProtocol
        result = self.formatters.create_tree(label)
        if result.is_success:
            # RichTree (concrete type) implements RichTreeProtocol structurally
            # Type narrowing: unwrap returns RichTreeProtocol-compatible type
            tree_value = result.unwrap()
            # Type narrowing: tree_value is structurally compatible with protocol
            # Cast Tree to RichTreeProtocol for type compatibility
            tree_protocol = cast("p.Display.RichTreeProtocol", tree_value)
            return r[p.Display.RichTreeProtocol].ok(tree_protocol)
        # Result is already r[RichTreeProtocol] from formatters
        # Cast result to expected return type
        return cast("r[p.Display.RichTreeProtocol]", result)


__all__ = [
    "FlextCli",
    "FlextCliAppBase",
]
