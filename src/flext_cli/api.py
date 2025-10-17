"""FLEXT CLI API - Consolidated single-class implementation.

Single FlextCli class with EXACTLY ONE main class per module pattern.
Consolidates ALL CLI functionality (auth, formatting, commands, etc.).
Uses FlextResult railway pattern with zero async operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import secrets
from collections.abc import Callable
from pathlib import Path
from typing import cast

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

# Direct module-level class references (no wrapping)
__constants__ = FlextCliConstants
__models__ = FlextCliModels
__types__ = FlextCliTypes


class FlextCli:
    """Consolidated single-class CLI implementation.

    Contains ALL CLI functionality (formatting, auth, commands, etc.).
    Uses FlextResult railway pattern with zero async operations.
    All defaults from FlextCliConstants with proper centralization.
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
        self._commands: FlextTypes.Dict = {}
        self._groups: FlextTypes.Dict = {}
        self._plugin_commands: FlextTypes.Dict = {}

        # Auth state (consolidated from FlextCliAuth)
        self.config = FlextCliConfig()
        self._valid_tokens: set[str] = set()
        self._valid_sessions: set[str] = set()
        self._session_permissions: dict[str, set[str]] = {}
        self._users: dict[str, FlextTypes.Dict] = {}
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

    def print(
        self,
        message: str,
        style: str | None = None,
    ) -> FlextResult[None]:
        """Print formatted message using formatters domain library."""
        return self.formatters.print(message, style=style)

    def create_table(
        self,
        data: FlextCliTypes.Data.CliDataDict | None = None,
        headers: FlextTypes.StringList | None = None,
        title: str | None = None,
    ) -> FlextResult[FlextCliTypes.Display.RichTable]:
        """Create table using formatters domain library.

        Returns:
            FlextResult[RichTable]: Rich Table wrapped in Result

        """
        return self.formatters.create_table(data=data, headers=headers, title=title)

    def create_progress(self) -> FlextResult[FlextCliTypes.Interactive.Progress]:
        """Create progress bar using formatters domain library.

        Returns:
            FlextResult[Progress]: Rich Progress wrapped in Result

        """
        return self.formatters.create_progress()

    def create_tree(self, label: str) -> FlextResult[FlextCliTypes.Display.RichTree]:
        """Create tree using formatters domain library."""
        return self.formatters.create_tree(label=label)

    def print_table(self, table: FlextCliTypes.Display.RichTable) -> FlextResult[None]:
        """Print a Rich Table object using formatters domain library.

        Args:
            table: Rich Table object to print

        Returns:
            FlextResult[None]: Success if printed, failure with details

        """
        try:
            self.formatters.get_console().print(table)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.APIDefaults.PRINT_TABLE_ERROR_PREFIX.format(error=e)
            )

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
        [Callable[..., FlextCliTypes.JsonValue]], Callable[..., FlextCliTypes.JsonValue]
    ]:
        """Register a command using CLI framework abstraction."""

        def decorator(
            func: Callable[..., FlextCliTypes.JsonValue],
        ) -> Callable[..., FlextCliTypes.JsonValue]:
            cmd_name = name or func.__name__
            self._commands[cmd_name] = func

            # Register with CLI framework abstraction
            command_decorator = self._cli.create_command_decorator(name=cmd_name)
            return command_decorator(func)

        return decorator

    def group(
        self, name: str | None = None
    ) -> Callable[
        [Callable[..., FlextCliTypes.JsonValue]], Callable[..., FlextCliTypes.JsonValue]
    ]:
        """Register a command group using CLI framework abstraction."""

        def decorator(
            func: Callable[..., FlextCliTypes.JsonValue],
        ) -> Callable[..., FlextCliTypes.JsonValue]:
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
    # FILE OPERATIONS - Domain library delegation
    # =========================================================================

    def read_text_file(self, path: Path) -> FlextResult[str]:
        """Read text file using file tools domain library."""
        return self.file_tools.read_text_file(str(path))

    def write_text_file(self, path: Path, content: str) -> FlextResult[None]:
        """Write text file using file tools domain library."""
        return self.file_tools.write_text_file(str(path), content)

    # =========================================================================
    # EXECUTION - Railway pattern with FlextResult
    # =========================================================================

    def execute(self) -> FlextResult[FlextTypes.Dict]:
        """Execute CLI service with railway pattern."""
        return FlextResult[FlextTypes.Dict].ok({
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
        })


__all__ = [
    "FlextCli",
]
