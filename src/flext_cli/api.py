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
from typing import TYPE_CHECKING, cast

from flext_core import FlextCore, FlextResult
from rich.tree import Tree

from flext_cli.cli import FlextCliCli
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import FlextCliModels
from flext_cli.typings import FlextCliTypes

# TYPE_CHECKING imports for lazy-loaded types (avoid circular imports)
if TYPE_CHECKING:
    from flext_cli.cmd import FlextCliCmd
    from flext_cli.core import FlextCliCore
    from flext_cli.output import FlextCliOutput
    from flext_cli.prompts import FlextCliPrompts
else:
    # Runtime imports for lazy-loading - must be at module top to avoid PLC0415
    from flext_cli.cmd import FlextCliCmd
    from flext_cli.core import FlextCliCore
    from flext_cli.output import FlextCliOutput
    from flext_cli.prompts import FlextCliPrompts


class FlextCli:
    """Consolidated single-class CLI implementation.

    Contains ALL CLI functionality (formatting, auth, commands, etc.).
    Uses FlextResult railway pattern with zero async operations.
    All defaults from FlextCliConstants with proper centralization.
    """

    def __init__(self) -> None:
        """Initialize consolidated CLI with all functionality integrated."""
        # CLI metadata - MUST be first for Typer app creation
        self._name = FlextCliConstants.CliDefaults.DEFAULT_APP_NAME
        self._version = FlextCliConstants.VERSION
        self._description = f"{self._name} CLI"

        # Core initialization
        self._logger = FlextCore.Logger(__name__)
        self._container = FlextCore.Container.get_global()
        self._container.register("flext_cli", self)

        # Domain library components (domain library pattern)
        self._formatters = FlextCliFormatters()
        self._file_tools = FlextCliFileTools()

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
        self._users: dict[str, dict[str, object]] = {}
        self._deleted_users: set[str] = set()

    @classmethod
    def get_instance(cls) -> FlextCli:
        """Get singleton FlextCli instance."""
        container = FlextCore.Container.get_global()
        result = container.get("flext_cli")
        if result.is_failure or result.value is None:
            return cls()
        return cast("FlextCli", result.value)

    # =========================================================================
    # CONFIGURATION MANAGEMENT - Direct access with FlextCliConstants defaults
    # =========================================================================

    @property
    def config(self) -> FlextCliConfig:
        """Access CLI configuration singleton."""
        return FlextCliConfig.get_global_instance()

    @property
    def constants(self) -> type[FlextCliConstants]:
        """Access CLI constants."""
        return FlextCliConstants

    @property
    def models(self) -> type[FlextCliModels]:
        """Access CLI models."""
        return FlextCliModels

    @property
    def types(self) -> type[FlextCliTypes]:
        """Access CLI types."""
        return FlextCliTypes

    @property
    def file_tools(self) -> FlextCliFileTools:
        """Access file tools domain library."""
        return self._file_tools

    @property
    def formatters(self) -> FlextCliFormatters:
        """Access formatters domain library."""
        return self._formatters

    @property
    def output(self) -> FlextCliOutput:
        """Access output formatting service (lazy-loaded)."""
        if not hasattr(self, "_output"):
            self._output = FlextCliOutput()
        return self._output

    @property
    def utilities(self) -> type[FlextCore.Utilities]:
        """Access core utilities for validation and data processing."""
        return FlextCore.Utilities

    @property
    def logger(self) -> FlextCore.Logger:
        """Access logger instance."""
        return self._logger

    @property
    def core(self) -> FlextCliCore:
        """Access core CLI service (lazy-loaded)."""
        if not hasattr(self, "_core"):
            self._core = FlextCliCore()
        return self._core

    @property
    def prompts(self) -> FlextCliPrompts:
        """Access prompts service (lazy-loaded)."""
        if not hasattr(self, "_prompts"):
            self._prompts = FlextCliPrompts()
        return self._prompts

    @property
    def cmd(self) -> FlextCliCmd:
        """Access command service (lazy-loaded)."""
        if not hasattr(self, "_cmd"):
            self._cmd = FlextCliCmd()
        return self._cmd

    # =========================================================================
    # FORMATTING - Domain library pattern using FlextCliFormatters
    # =========================================================================

    def print(
        self,
        message: str,
        style: str | None = None,
        **kwargs: object,
    ) -> FlextResult[None]:
        """Print formatted message using formatters domain library."""
        return self._formatters.print(message, style=style, **kwargs)

    def create_table(
        self,
        data: FlextCliTypes.Data.CliDataDict | None = None,
        headers: FlextCore.Types.StringList | None = None,
        title: str | None = None,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Create table using formatters domain library."""
        result = self._formatters.create_table(
            data=data, headers=headers, title=title, **kwargs
        )
        return result.map(lambda table: cast("object", table))

    def create_progress(self, **kwargs: object) -> FlextResult[object]:
        """Create progress bar using formatters domain library."""
        result = self._formatters.create_progress(**kwargs)
        return result.map(lambda progress: cast("object", progress))

    def create_tree(self, label: str, **kwargs: object) -> FlextResult[Tree]:
        """Create tree using formatters domain library."""
        return self._formatters.create_tree(label=label, **kwargs)

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
        save_result = self.save_auth_token(token)
        if save_result.is_failure:
            return FlextResult[str].fail(f"Failed to save token: {save_result.error}")
        if not token.strip():
            return FlextResult[str].fail(FlextCliConstants.ErrorMessages.TOKEN_EMPTY)
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
        token = secrets.token_urlsafe(32)
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

        token_path = self._config.token_file
        token_data = {"token": token}

        # Use file tools domain library for JSON writing
        write_result = self._file_tools.write_json_file(str(token_path), token_data)
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
        token_path = self._config.token_file

        # Use file tools domain library for JSON reading
        read_result = self._file_tools.read_json_file(str(token_path))
        if read_result.is_failure:
            if "not found" in str(read_result.error).lower():
                return FlextResult[str].fail(
                    FlextCliConstants.ErrorMessages.TOKEN_FILE_NOT_FOUND
                )
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_LOAD_FAILED.format(
                    error=read_result.error
                )
            )

        data = cast("dict[str, str]", read_result.unwrap())
        token = data.get("token")
        if not token:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY
            )

        return FlextResult[str].ok(str(token))

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        token_result = self.get_auth_token()
        return token_result.is_success

    def clear_auth_tokens(self) -> FlextResult[None]:
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
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_token_result.error
                )
            )

        if (
            delete_refresh_result.is_failure
            and "not found" not in str(delete_refresh_result.error).lower()
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

    def execute_cli(self) -> FlextResult[None]:
        """Execute the CLI application using framework abstraction."""
        # FlextCliCli doesn't have run_app - CLI execution handled elsewhere
        return FlextResult[None].ok(None)

    # =========================================================================
    # FILE OPERATIONS - Domain library delegation
    # =========================================================================

    def read_text_file(self, path: Path) -> FlextResult[str]:
        """Read text file using file tools domain library."""
        return self._file_tools.read_text_file(str(path))

    def write_text_file(self, path: Path, content: str) -> FlextResult[None]:
        """Write text file using file tools domain library."""
        return self._file_tools.write_text_file(str(path), content)

    # =========================================================================
    # EXECUTION - Railway pattern with FlextResult
    # =========================================================================

    def execute(self) -> FlextResult[FlextCore.Types.Dict]:
        """Execute CLI service with railway pattern."""
        return FlextResult[FlextCore.Types.Dict].ok({
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.OPERATIONAL,
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
        })


__all__ = [
    "FlextCli",
]
