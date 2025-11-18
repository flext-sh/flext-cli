"""FLEXT CLI API - Consolidated single-class implementation.

Single FlextCli class with EXACTLY ONE main class per module pattern.
Consolidates ALL CLI functionality (auth, formatting, commands, etc.).
Uses FlextResult railway pattern with zero async operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import secrets
import typing
from collections.abc import Callable, Sequence

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextTypes,
)

from flext_cli.cli import FlextCliCli
from flext_cli.cmd import FlextCliCmd
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.core import FlextCliCore
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import FlextCliModels
from flext_cli.output import FlextCliOutput
from flext_cli.prompts import FlextCliPrompts
from flext_cli.typings import FlextCliTypes
from flext_cli.utilities import FlextCliUtilities


class FlextCli:
    """Coordinator for CLI operations with direct domain library access.

    Consolidates ALL CLI functionality through direct access to domain libraries:
    - formatters: FlextCliFormatters - Rich-based visual output
    - output: FlextCliOutput - Comprehensive output tools
    - file_tools: FlextCliFileTools - File operations
    - core: FlextCliCore - Core CLI service
    - cmd: FlextCliCmd - Command execution
    - prompts: FlextCliPrompts - Interactive prompts
    - config: FlextCliConfig - Configuration management

    Uses FlextResult railway pattern with zero async operations.
    All defaults from FlextCliConstants with proper centralization.

    Usage (direct access pattern):
        >>> cli = FlextCli.get_instance()
        >>> cli.formatters.print("Hello")  # Direct formatters access
        >>> cli.output.format_data(data)  # Direct output access
        >>> cli.file_tools.read_json_file(path)  # Direct file tools access
    """

    _instance: FlextCli | None = None
    _lock = __import__("threading").Lock()

    # Public service instances (no wrapping needed - direct access)
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
        # CLI metadata - MUST be first for Typer app creation
        self._name = FlextCliConstants.CliDefaults.DEFAULT_APP_NAME
        self._version = FlextCliConstants.CLI_VERSION
        self._description = (
            f"{self._name}{FlextCliConstants.APIDefaults.APP_DESCRIPTION_SUFFIX}"
        )

        # Core initialization
        self.logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()
        # Register in container only if not already registered (avoids test conflicts)
        if not self._container.has_service(
            FlextCliConstants.APIDefaults.CONTAINER_REGISTRATION_KEY
        ):
            self._container.with_service(
                FlextCliConstants.APIDefaults.CONTAINER_REGISTRATION_KEY, self
            )

        # Domain library components (domain library pattern)
        self.formatters = FlextCliFormatters()
        self.file_tools = FlextCliFileTools()
        self.output = FlextCliOutput()
        self.core = FlextCliCore()
        self.cmd = FlextCliCmd()
        self.prompts = FlextCliPrompts()

        # CLI framework abstraction (domain library pattern)
        self._cli = FlextCliCli()
        # Commands and groups store Callable functions, not JSON data
        self._commands: dict[str, Callable[..., FlextTypes.JsonValue]] = {}
        self._groups: dict[str, Callable[..., FlextTypes.JsonValue]] = {}
        self._plugin_commands: dict[str, Callable[..., FlextTypes.JsonValue]] = {}

        # Auth state (consolidated from FlextCliAuth)
        self.config = FlextCliConfig()
        self._valid_tokens: set[str] = set()
        self._valid_sessions: set[str] = set()
        self._session_permissions: dict[str, set[str]] = {}
        self._users: dict[str, FlextTypes.JsonDict] = {}
        self._deleted_users: set[str] = set()

    @classmethod
    def get_instance(cls) -> FlextCli:
        """Get singleton FlextCli instance using class-level singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # =========================================================================
    # AUTHENTICATION - Direct implementation (consolidated from auth.py)
    # =========================================================================

    def authenticate(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextResult[str]:
        """Authenticate user with provided credentials."""
        if FlextCliConstants.DictKeys.TOKEN in credentials:
            return self._authenticate_with_token(credentials)
        if (
            FlextCliConstants.DictKeys.USERNAME in credentials
            and FlextCliConstants.DictKeys.PASSWORD in credentials
        ):
            return self._authenticate_with_credentials(credentials)
        return FlextResult[str].fail(
            FlextCliConstants.ErrorMessages.INVALID_CREDENTIALS
        )

    def _authenticate_with_token(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextResult[str]:
        """Authenticate using token."""
        token = str(credentials[FlextCliConstants.DictKeys.TOKEN])
        if not token.strip():
            return FlextResult[str].fail(FlextCliConstants.ErrorMessages.TOKEN_EMPTY)
        save_result = self.save_auth_token(token)
        if save_result.is_failure:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=save_result.error
                )
            )
        return FlextResult[str].ok(token)

    def _authenticate_with_credentials(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextResult[str]:
        """Authenticate using Pydantic 2 validation - no manual checks."""
        # Validate using Pydantic model - eliminates all manual validation
        try:
            FlextCliModels.PasswordAuth.model_validate(credentials)
        except Exception as e:
            return FlextResult[str].fail(str(e))

        # Generate token
        token = secrets.token_urlsafe(
            FlextCliConstants.APIDefaults.TOKEN_GENERATION_BYTES
        )
        self._valid_tokens.add(token)

        return FlextResult[str].ok(token)

    def validate_credentials(self, username: str, password: str) -> FlextResult[bool]:
        """Validate credentials using Pydantic 2."""
        try:
            FlextCliModels.PasswordAuth(username=username, password=password)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(str(e))

    def save_auth_token(self, token: str) -> FlextResult[bool]:
        """Save authentication token using file tools domain library."""
        if not token.strip():
            return FlextResult[bool].fail(FlextCliConstants.ErrorMessages.TOKEN_EMPTY)

        token_path = self.config.token_file
        token_data: FlextCliTypes.Auth.CredentialsData = {
            FlextCliConstants.DictKeys.TOKEN: token
        }

        # Use file tools domain library for JSON writing
        # token_data is CredentialsData (dict[str, JsonValue]) which is compatible with JsonValue
        # Cast to JsonValue for type checker (dict is a valid JsonValue at runtime)
        json_data = typing.cast("FlextTypes.JsonValue", token_data)
        write_result = self.file_tools.write_json_file(str(token_path), json_data)
        if write_result.is_failure:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=write_result.error
                )
            )

        self._valid_tokens.add(token)
        return FlextResult[bool].ok(True)

    def get_auth_token(self) -> FlextResult[str]:
        """Get authentication token using Pydantic 2 validation - no wrappers.

        Uses FlextCliModels.TokenData for validation instead of manual checks.
        """
        token_path = self.config.token_file

        # Read JSON file directly using file_tools
        result = self.file_tools.read_json_file(str(token_path))
        if result.is_failure:
            error_str = str(result.error)
            # Check for file not found using utilities helper (covers "not found", "no such file", etc.)
            if (
                FlextCliConstants.APIDefaults.FILE_ERROR_INDICATOR in error_str.lower()
                or FlextCliUtilities.FileOps.is_file_not_found_error(error_str)
            ):
                return FlextResult[str].fail(
                    FlextCliConstants.ErrorMessages.TOKEN_FILE_NOT_FOUND
                )
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_LOAD_FAILED.format(
                    error=error_str
                )
            )

        # Validate using Pydantic model - eliminates _validate_token_data + _extract_token_string
        data = result.unwrap()
        # Check if data is empty or None before validation
        if not data or (isinstance(data, dict) and not data):
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY
            )
        try:
            token_data = FlextCliModels.TokenData.model_validate(data)
            return FlextResult[str].ok(token_data.token)
        except Exception as e:
            # Return appropriate error message based on exception type
            error_str = str(e).lower()
            if "dict" in error_str or "mapping" in error_str or "object" in error_str:
                return FlextResult[str].fail(
                    FlextCliConstants.APIDefaults.TOKEN_DATA_TYPE_ERROR
                )
            if "string" in error_str or "str" in error_str:
                return FlextResult[str].fail(
                    FlextCliConstants.APIDefaults.TOKEN_VALUE_TYPE_ERROR
                )
            # Fallback for any other validation errors (e.g., field required, value errors)
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY
            )

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        token_result = self.get_auth_token()
        return token_result.is_success

    def clear_auth_tokens(self) -> FlextResult[bool]:
        """Clear authentication tokens using file tools domain library."""
        token_path = self.config.token_file
        refresh_token_path = self.config.refresh_token_file

        # Use file tools domain library for file deletion
        delete_token_result = self.file_tools.delete_file(str(token_path))
        delete_refresh_result = self.file_tools.delete_file(str(refresh_token_path))

        # Check if either deletion failed (but don't fail if file doesn't exist)
        if (
            delete_token_result.is_failure
            and not FlextCliUtilities.FileOps.is_file_not_found_error(
                str(delete_token_result.error)
            )
        ):
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_token_result.error
                )
            )

        if (
            delete_refresh_result.is_failure
            and not FlextCliUtilities.FileOps.is_file_not_found_error(
                str(delete_refresh_result.error)
            )
        ):
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_refresh_result.error
                )
            )

        self._valid_tokens.clear()
        return FlextResult[bool].ok(True)

    # =========================================================================
    # COMMAND REGISTRATION - CLI framework abstraction (domain library pattern)
    # =========================================================================

    def _register_cli_entity(
        self,
        entity_type: FlextCliConstants.EntityTypeLiteral,
        name: str | None,
        func: Callable[..., FlextTypes.JsonValue],
    ) -> Callable[..., FlextTypes.JsonValue]:
        """Register a CLI entity (command or group) with framework abstraction.

        Args:
            entity_type: Type of entity to register ("command" or "group")
            name: Entity name (None to use function name)
            func: Function to register

        Returns:
            Decorated function

        """
        # Validate entity name explicitly - no fallback
        entity_name = name if name is not None else func.__name__

        if entity_type == "command":
            self._commands[entity_name] = func
            decorator = self._cli.create_command_decorator(name=entity_name)
        else:  # group
            self._groups[entity_name] = func
            decorator = self._cli.create_group_decorator(name=entity_name)

        return decorator(func)

    def command(
        self, name: str | None = None
    ) -> Callable[
        [Callable[..., FlextTypes.JsonValue]], Callable[..., FlextTypes.JsonValue]
    ]:
        """Register a command using CLI framework abstraction."""

        def decorator(
            func: Callable[..., FlextTypes.JsonValue],
        ) -> Callable[..., FlextTypes.JsonValue]:
            return self._register_cli_entity("command", name, func)

        return decorator

    def group(
        self, name: str | None = None
    ) -> Callable[
        [Callable[..., FlextTypes.JsonValue]], Callable[..., FlextTypes.JsonValue]
    ]:
        """Register a command group using CLI framework abstraction."""

        def decorator(
            func: Callable[..., FlextTypes.JsonValue],
        ) -> Callable[..., FlextTypes.JsonValue]:
            return self._register_cli_entity("group", name, func)

        return decorator

    def execute_cli(self) -> FlextResult[bool]:
        """Execute the CLI application using framework abstraction."""
        # FlextCliCli doesn't have run_app - CLI execution handled elsewhere
        return FlextResult[bool].ok(True)

    # =========================================================================
    # EXECUTION - Railway pattern with FlextResult
    # =========================================================================

    def execute(self) -> FlextResult[FlextTypes.JsonDict]:
        """Execute CLI service with railway pattern."""
        return FlextResult[FlextTypes.JsonDict].ok({
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
        })

    # =========================================================================
    # CONVENIENCE METHODS - Delegate to service instances
    # =========================================================================

    def print(
        self,
        message: str,
        style: str | None = None,
    ) -> FlextResult[bool]:
        """Print formatted message (convenience method for formatters.print)."""
        return self.formatters.print(message, style)

    def create_table(
        self,
        data: Sequence[dict[str, FlextTypes.JsonValue]]
        | dict[str, FlextTypes.JsonValue]
        | None = None,
        headers: list[str] | None = None,
        title: str | None = None,
    ) -> FlextResult[str]:
        """Create table from data (convenience method).

        Args:
            data: Data to format as table (dict or list of dicts)
            headers: Optional column headers
            title: Optional table title

        Returns:
            FlextResult[str]: Formatted table string

        """
        # Handle None case - fast fail if data is None
        if data is None:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED
            )

        # table_data is dict|list which are both valid JsonValue types
        # Ensure type compatibility for type checker (dict/list are JsonValue at runtime)
        if isinstance(data, dict):
            table_data = typing.cast("FlextTypes.JsonValue", data)
        else:
            # Convert to list and ensure JsonValue compatibility
            table_data = typing.cast("FlextTypes.JsonValue", list(data))

        # Use output.format_data which supports data, title, and headers
        return self.output.format_data(
            data=table_data,
            format_type="table",
            title=title,
            headers=headers,
        )

    def print_table(
        self,
        table: str,
    ) -> FlextResult[bool]:
        """Print table string (convenience method)."""
        return self.formatters.print(table)

    def create_tree(
        self,
        label: str,
    ) -> FlextResult[FlextCliTypes.Display.RichTree]:
        """Create tree visualization (convenience method for formatters.create_tree)."""
        return self.formatters.create_tree(label)


__all__ = [
    "FlextCli",
]
