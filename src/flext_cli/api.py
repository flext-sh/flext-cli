"""FLEXT CLI API - Consolidated single-class implementation.

Single FlextCli class with EXACTLY ONE main class per module pattern.
Consolidates ALL CLI functionality (auth, formatting, commands, etc.).
Uses FlextResult railway pattern with zero async operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

import secrets
from collections.abc import Callable
from typing import Any, cast

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
from flext_cli.output import FlextCliOutput
from flext_cli.prompts import FlextCliPrompts
from flext_cli.typings import FlextCliTypes


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

    _instance: "FlextCli | None" = None
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
        self._container.register(
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
    def get_instance(cls) -> "FlextCli":
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
        """Authenticate using username/password."""
        username = str(credentials[FlextCliConstants.DictKeys.USERNAME])
        password = str(credentials[FlextCliConstants.DictKeys.PASSWORD])

        # Simple validation (in real implementation, check against user store)
        if not username or not password:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.USERNAME_PASSWORD_REQUIRED
            )

        if len(username) < FlextCliConstants.Auth.MIN_USERNAME_LENGTH:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.USERNAME_TOO_SHORT
            )

        if len(password) < FlextCliConstants.Auth.MIN_PASSWORD_LENGTH:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.PASSWORD_TOO_SHORT
            )

        # Generate token
        token = secrets.token_urlsafe(
            FlextCliConstants.APIDefaults.TOKEN_GENERATION_BYTES
        )
        self._valid_tokens.add(token)

        return FlextResult[str].ok(token)

    def validate_credentials(self, username: str, password: str) -> FlextResult[None]:
        """Validate credentials."""
        if not username or not password:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.USERNAME_PASSWORD_REQUIRED
            )
        return FlextResult[None].ok(None)

    def save_auth_token(self, token: str) -> FlextResult[None]:
        """Save authentication token using file tools domain library."""
        if not token.strip():
            return FlextResult[None].fail(FlextCliConstants.ErrorMessages.TOKEN_EMPTY)

        token_path = self.config.token_file
        token_data: FlextCliTypes.Auth.CredentialsData = {
            FlextCliConstants.DictKeys.TOKEN: token
        }

        # Use file tools domain library for JSON writing
        # Cast to JsonValue to satisfy invariant dict typing
        json_data: FlextTypes.JsonValue = cast("FlextTypes.JsonValue", token_data)
        write_result = self.file_tools.write_json_file(str(token_path), json_data)
        if write_result.is_failure:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=write_result.error
                )
            )

        self._valid_tokens.add(token)
        return FlextResult[None].ok(None)

    def get_auth_token(self) -> FlextResult[str]:
        """Get authentication token using file tools domain library."""
        token_path = self.config.token_file

        # Use file tools domain library for JSON reading
        read_result = self.file_tools.read_json_file(str(token_path))
        if read_result.is_failure:
            if (
                FlextCliConstants.APIDefaults.FILE_ERROR_INDICATOR
                in str(read_result.error).lower()
            ):
                return FlextResult[str].fail(
                    FlextCliConstants.ErrorMessages.TOKEN_FILE_NOT_FOUND
                )
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_LOAD_FAILED.format(
                    error=read_result.error
                )
            )

        # Type guard: validate data is dict with token key
        data = read_result.unwrap()
        if not isinstance(data, dict):
            return FlextResult[str].fail(
                FlextCliConstants.APIDefaults.TOKEN_DATA_TYPE_ERROR
            )

        token = data.get(FlextCliConstants.DictKeys.TOKEN)
        if not token:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY
            )

        if not isinstance(token, str):
            return FlextResult[str].fail(
                FlextCliConstants.APIDefaults.TOKEN_VALUE_TYPE_ERROR
            )

        return FlextResult[str].ok(token)

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        token_result = self.get_auth_token()
        return token_result.is_success

    def clear_auth_tokens(self) -> FlextResult[None]:
        """Clear authentication tokens using file tools domain library."""
        token_path = self.config.token_file
        refresh_token_path = self.config.refresh_token_file

        # Use file tools domain library for file deletion
        delete_token_result = self.file_tools.delete_file(str(token_path))
        delete_refresh_result = self.file_tools.delete_file(str(refresh_token_path))

        # Check if either deletion failed (but don't fail if file doesn't exist)
        if (
            delete_token_result.is_failure
            and FlextCliConstants.APIDefaults.FILE_ERROR_INDICATOR
            not in str(delete_token_result.error).lower()
        ):
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_token_result.error
                )
            )

        if (
            delete_refresh_result.is_failure
            and FlextCliConstants.APIDefaults.FILE_ERROR_INDICATOR
            not in str(delete_refresh_result.error).lower()
        ):
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_refresh_result.error
                )
            )

        self._valid_tokens.clear()
        return FlextResult[None].ok(None)

    # =========================================================================
    # COMMAND REGISTRATION - CLI framework abstraction (domain library pattern)
    # =========================================================================

    def command(
        self, name: str | None = None
    ) -> Callable[
        [Callable[..., FlextTypes.JsonValue]], Callable[..., FlextTypes.JsonValue]
    ]:
        """Register a command using CLI framework abstraction."""

        def decorator(
            func: Callable[..., FlextTypes.JsonValue],
        ) -> Callable[..., FlextTypes.JsonValue]:
            cmd_name = name or func.__name__
            self._commands[cmd_name] = func

            # Register with CLI framework abstraction
            command_decorator = self._cli.create_command_decorator(name=cmd_name)
            return command_decorator(func)

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
            group_name = name or func.__name__
            self._groups[group_name] = func

            # Register with CLI framework abstraction
            group_decorator = self._cli.create_group_decorator(name=group_name)
            return group_decorator(func)

        return decorator

    def execute_cli(self) -> FlextResult[None]:
        """Execute the CLI application using framework abstraction."""
        # FlextCliCli doesn't have run_app - CLI execution handled elsewhere
        return FlextResult[None].ok(None)

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
    ) -> FlextResult[None]:
        """Print formatted message (convenience method for formatters.print)."""
        return self.formatters.print(message, style)

    def create_table(
        self,
        data: FlextTypes.JsonValue | None = None,
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
        # Handle None case - use empty dict as default
        table_data: FlextTypes.JsonValue = data if data is not None else {}
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
    ) -> FlextResult[None]:
        """Print table string (convenience method)."""
        return self.formatters.print(table)

    def create_tree(
        self,
        label: str,
    ) -> FlextResult[Any]:
        """Create tree visualization (convenience method for formatters.create_tree)."""
        return self.formatters.create_tree(label)


__all__ = [
    "FlextCli",
]
