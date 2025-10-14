"""FLEXT CLI API - Consolidated single-class implementation.

Single FlextCli class with EXACTLY ONE main class per module pattern.
Consolidates ALL CLI functionality (auth, formatting, commands, etc.).
Uses FlextCore.Result railway pattern with zero async operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import secrets
from collections.abc import Callable
from pathlib import Path

from flext_core import FlextCore
from rich.progress import Progress
from rich.table import Table
from rich.tree import Tree

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


class FlextCli:
    """Consolidated single-class CLI implementation.

    Contains ALL CLI functionality (formatting, auth, commands, etc.).
    Uses FlextCore.Result railway pattern with zero async operations.
    All defaults from FlextCliConstants with proper centralization.
    """

    _instance: FlextCli | None = None
    _lock = __import__("threading").Lock()

    def __init__(self) -> None:
        """Initialize consolidated CLI with all functionality integrated."""
        # CLI metadata - MUST be first for Typer app creation
        self._name = FlextCliConstants.CliDefaults.DEFAULT_APP_NAME
        self._version = FlextCliConstants.CLI_VERSION
        self._description = f"{self._name} CLI"

        # Core initialization
        self._logger = FlextCore.Logger(__name__)
        self._container = FlextCore.Container.get_global()
        self._container.register("flext_cli", self)

        # Domain library components (domain library pattern)
        self._formatters = FlextCliFormatters()
        self._file_tools = FlextCliFileTools()
        self._output = FlextCliOutput()
        self._core = FlextCliCore()
        self._cmd = FlextCliCmd()
        self._prompts = FlextCliPrompts()

        # CLI framework abstraction (domain library pattern)
        self._cli = FlextCliCli()
        self._commands: FlextCore.Types.Dict = {}
        self._groups: FlextCore.Types.Dict = {}
        self._plugin_commands: FlextCore.Types.Dict = {}

        # Auth state (consolidated from FlextCliAuth)
        self._config = FlextCliConfig()
        self._valid_tokens: set[str] = set()
        self._valid_sessions: set[str] = set()
        self._session_permissions: dict[str, set[str]] = {}
        self._users: dict[str, FlextCore.Types.Dict] = {}
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
    ) -> FlextCore.Result[None]:
        """Print formatted message using formatters domain library."""
        return self._formatters.print(message, style=style)

    def create_table(
        self,
        data: FlextCliTypes.Data.CliDataDict | None = None,
        headers: FlextCore.Types.StringList | None = None,
        title: str | None = None,
    ) -> FlextCore.Result[Table]:
        """Create table using formatters domain library.

        Returns:
            FlextCore.Result[Table]: Rich Table wrapped in Result

        """
        return self._formatters.create_table(data=data, headers=headers, title=title)

    def create_progress(self) -> FlextCore.Result[Progress]:
        """Create progress bar using formatters domain library.

        Returns:
            FlextCore.Result[Progress]: Rich Progress wrapped in Result

        """
        return self._formatters.create_progress()

    def create_tree(self, label: str) -> FlextCore.Result[Tree]:
        """Create tree using formatters domain library."""
        return self._formatters.create_tree(label=label)

    @property
    def config(self) -> FlextCliConfig:
        """Get CLI configuration instance."""
        return self._config

    @property
    def output(self) -> FlextCliOutput:
        """Get CLI output service instance."""
        return self._output

    @property
    def formatters(self) -> FlextCliFormatters:
        """Get CLI formatters instance."""
        return self._formatters

    @property
    def file_tools(self) -> FlextCliFileTools:
        """Get CLI file tools instance."""
        return self._file_tools

    @property
    def core(self) -> FlextCliCore:
        """Get CLI core service instance."""
        return self._core

    @property
    def constants(self) -> type[FlextCliConstants]:
        """Get CLI constants class."""
        return FlextCliConstants

    @property
    def models(self) -> type[FlextCliModels]:
        """Get CLI models class."""
        return FlextCliModels

    @property
    def types(self) -> type[FlextCliTypes]:
        """Get CLI types class."""
        return FlextCliTypes

    @property
    def logger(self) -> FlextCore.Logger:
        """Get CLI logger instance."""
        return self._logger

    @property
    def cmd(self) -> FlextCliCmd:
        """Get CLI command service instance."""
        return self._cmd

    @property
    def prompts(self) -> FlextCliPrompts:
        """Get prompts instance - direct access."""
        return self._prompts

    @property
    def utilities(self) -> object:
        """Get CLI utilities instance."""
        # For now, return self as utilities - this might need to be expanded later
        return self

    def print_table(self, table: Table) -> FlextCore.Result[None]:
        """Print a Rich Table object using formatters domain library.

        Args:
            table: Rich Table object to print

        Returns:
            FlextCore.Result[None]: Success if printed, failure with details

        """
        try:
            self._formatters.get_console().print(table)
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(f"Failed to print table: {e}")

    # =========================================================================
    # AUTHENTICATION - Direct implementation (consolidated from auth.py)
    # =========================================================================

    def authenticate(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextCore.Result[str]:
        """Authenticate user with provided credentials."""
        if FlextCliConstants.DictKeys.TOKEN in credentials:
            return self._authenticate_with_token(credentials)
        if (
            FlextCliConstants.DictKeys.USERNAME in credentials
            and FlextCliConstants.DictKeys.PASSWORD in credentials
        ):
            return self._authenticate_with_credentials(credentials)
        return FlextCore.Result[str].fail(
            FlextCliConstants.ErrorMessages.INVALID_CREDENTIALS
        )

    def _authenticate_with_token(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextCore.Result[str]:
        """Authenticate using token."""
        token = str(credentials[FlextCliConstants.DictKeys.TOKEN])
        save_result = self.save_auth_token(token)
        if save_result.is_failure:
            return FlextCore.Result[str].fail(
                f"Failed to save token: {save_result.error}"
            )
        if not token.strip():
            return FlextCore.Result[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_EMPTY
            )
        return FlextCore.Result[str].ok(token)

    def _authenticate_with_credentials(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextCore.Result[str]:
        """Authenticate using username/password."""
        username = str(credentials[FlextCliConstants.DictKeys.USERNAME])
        password = str(credentials[FlextCliConstants.DictKeys.PASSWORD])

        # Simple validation (in real implementation, check against user store)
        if not username or not password:
            return FlextCore.Result[str].fail(
                FlextCliConstants.ErrorMessages.USERNAME_PASSWORD_REQUIRED
            )

        if len(username) < FlextCliConstants.Auth.MIN_USERNAME_LENGTH:
            return FlextCore.Result[str].fail(
                FlextCliConstants.ErrorMessages.USERNAME_TOO_SHORT
            )

        if len(password) < FlextCliConstants.Auth.MIN_PASSWORD_LENGTH:
            return FlextCore.Result[str].fail(
                FlextCliConstants.ErrorMessages.PASSWORD_TOO_SHORT
            )

        # Generate token
        token = secrets.token_urlsafe(32)
        self._valid_tokens.add(token)

        return FlextCore.Result[str].ok(token)

    def validate_credentials(
        self, username: str, password: str
    ) -> FlextCore.Result[None]:
        """Validate credentials."""
        if not username or not password:
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.USERNAME_PASSWORD_REQUIRED
            )
        return FlextCore.Result[None].ok(None)

    def save_auth_token(self, token: str) -> FlextCore.Result[None]:
        """Save authentication token using file tools domain library."""
        if not token.strip():
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.TOKEN_EMPTY
            )

        token_path = self._config.token_file
        token_data = {"token": token}

        # Use file tools domain library for JSON writing
        write_result = self._file_tools.write_json_file(str(token_path), token_data)
        if write_result.is_failure:
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=write_result.error
                )
            )

        self._valid_tokens.add(token)
        return FlextCore.Result[None].ok(None)

    def get_auth_token(self) -> FlextCore.Result[str]:
        """Get authentication token using file tools domain library."""
        token_path = self._config.token_file

        # Use file tools domain library for JSON reading
        read_result = self._file_tools.read_json_file(str(token_path))
        if read_result.is_failure:
            if "not found" in str(read_result.error).lower():
                return FlextCore.Result[str].fail(
                    FlextCliConstants.ErrorMessages.TOKEN_FILE_NOT_FOUND
                )
            return FlextCore.Result[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_LOAD_FAILED.format(
                    error=read_result.error
                )
            )

        # Type guard: validate data is dict with "token" key
        data = read_result.unwrap()
        if not isinstance(data, dict):
            return FlextCore.Result[str].fail("Token file must contain a JSON object")

        token = data.get("token")
        if not token:
            return FlextCore.Result[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY
            )

        if not isinstance(token, str):
            return FlextCore.Result[str].fail("Token must be a string")

        return FlextCore.Result[str].ok(token)

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        token_result = self.get_auth_token()
        return token_result.is_success

    def clear_auth_tokens(self) -> FlextCore.Result[None]:
        """Clear authentication tokens using file tools domain library."""
        token_path = self._config.token_file
        refresh_token_path = self._config.refresh_token_file

        # Use file tools domain library for file deletion
        delete_token_result = self._file_tools.delete_file(str(token_path))
        delete_refresh_result = self._file_tools.delete_file(str(refresh_token_path))

        # Check if either deletion failed (but don't fail if file doesn't exist)
        if (
            delete_token_result.is_failure
            and "not found" not in str(delete_token_result.error).lower()
        ):
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_token_result.error
                )
            )

        if (
            delete_refresh_result.is_failure
            and "not found" not in str(delete_refresh_result.error).lower()
        ):
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_refresh_result.error
                )
            )

        self._valid_tokens.clear()
        return FlextCore.Result[None].ok(None)

    # =========================================================================
    # COMMAND REGISTRATION - CLI framework abstraction (domain library pattern)
    # =========================================================================

    def command(
        self, name: str | None = None
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Register a command using CLI framework abstraction."""

        def decorator(func: Callable[..., object]) -> Callable[..., object]:
            cmd_name = name or func.__name__
            self._commands[cmd_name] = func

            # Register with CLI framework abstraction
            command_decorator = self._cli.create_command_decorator(name=cmd_name)
            return command_decorator(func)

        return decorator

    def group(
        self, name: str | None = None
    ) -> Callable[[Callable[..., object]], Callable[..., object]]:
        """Register a command group using CLI framework abstraction."""

        def decorator(func: Callable[..., object]) -> Callable[..., object]:
            group_name = name or func.__name__
            self._groups[group_name] = func

            # Register with CLI framework abstraction
            group_decorator = self._cli.create_group_decorator(name=group_name)
            return group_decorator(func)

        return decorator

    def execute_cli(self) -> FlextCore.Result[None]:
        """Execute the CLI application using framework abstraction."""
        # FlextCliCli doesn't have run_app - CLI execution handled elsewhere
        return FlextCore.Result[None].ok(None)

    # =========================================================================
    # FILE OPERATIONS - Domain library delegation
    # =========================================================================

    def read_text_file(self, path: Path) -> FlextCore.Result[str]:
        """Read text file using file tools domain library."""
        return self._file_tools.read_text_file(str(path))

    def write_text_file(self, path: Path, content: str) -> FlextCore.Result[None]:
        """Write text file using file tools domain library."""
        return self._file_tools.write_text_file(str(path), content)

    # =========================================================================
    # EXECUTION - Railway pattern with FlextCore.Result
    # =========================================================================

    def execute(self) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Execute CLI service with railway pattern."""
        return FlextCore.Result[FlextCore.Types.Dict].ok({
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.OPERATIONAL,
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
        })


__all__ = [
    "FlextCli",
]
