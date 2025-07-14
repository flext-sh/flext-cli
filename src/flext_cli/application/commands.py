"""Application commands for FLEXT-CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from flext_cli.domain.entities import CommandType

if TYPE_CHECKING:
    from uuid import UUID


class ExecuteCommandCommand:
    """Command to execute a CLI command."""

    def __init__(
        self,
        name: str,
        command_line: str,
        *,
        arguments: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
        command_type: CommandType = CommandType.SYSTEM,
        user_id: UUID | None = None,
        session_id: str | None = None,
        working_directory: str | None = None,
        environment: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        """Initialize the command."""
        self.name = name
        self.command_line = command_line
        self.arguments = arguments
        self.options = options
        self.command_type = command_type
        self.user_id = user_id
        self.session_id = session_id
        self.working_directory = working_directory
        self.environment = environment
        self.timeout_seconds = timeout_seconds


class CancelCommandCommand:
    """Command to cancel a running CLI command."""

    def __init__(self, command_id: UUID, user_id: UUID | None = None) -> None:
        """Initialize cancel command.

        Args:
            command_id: ID of command to cancel
            user_id: User requesting cancellation

        """
        self.command_id = command_id
        self.user_id = user_id


class CreateConfigCommand:
    """Command to create a CLI configuration."""

    name: str
    description = None
    config_data: dict[str, Any]
    config_type: str
    version = "1.0.0"
    user_id: UUID | None = None
    is_global: bool = False


class UpdateConfigCommand:
    """Command to update a CLI configuration."""

    config_id: UUID
    name = None
    description: str | None = None
    config_data: dict[str, Any] | None = None
    version: str | None = None
    user_id: UUID | None = None


class DeleteConfigCommand:
    """Command to delete a CLI configuration."""

    config_id: UUID
    user_id = None


class ValidateConfigCommand:
    """Command to validate a CLI configuration."""

    config_id: UUID
    user_id = None


class StartSessionCommand:
    """Command to start a CLI session."""

    session_id: str
    user_id = None
    working_directory: str | None = None
    environment: dict[str, str] | None = None


class EndSessionCommand:
    """Command to end a CLI session."""

    session_id: UUID
    user_id = None


class InstallPluginCommand:
    """Command to install a CLI plugin."""

    name: str
    version = None
    entry_point: str
    commands: list[str] | None = None
    dependencies: list[str] | None = None
    author: str | None = None
    license: str | None = None
    repository_url: str | None = None
    user_id: UUID | None = None


class UninstallPluginCommand:
    """Command to uninstall a CLI plugin."""

    plugin_id: UUID
    user_id = None


class EnablePluginCommand:
    """Command to enable a CLI plugin."""

    plugin_id: UUID
    user_id = None


class DisablePluginCommand:
    """Command to disable a CLI plugin."""

    plugin_id: UUID
    user_id = None


class ListCommandsCommand:
    """Command to list available CLI commands."""

    command_type: CommandType | None = None
    user_id: UUID | None = None
    session_id: str | None = None


class GetCommandHistoryCommand:
    """Command to get command execution history."""

    user_id: UUID | None = None
    session_id: str | None = None
    limit: int = 100
    command_type: CommandType | None = None


class GetCommandStatusCommand:
    """Command to get command execution status."""

    command_id: UUID
    user_id = None


class ListConfigsCommand:
    """Command to list CLI configurations."""

    config_type: str | None = None
    user_id: UUID | None = None
    include_global: bool = True


class ListPluginsCommand:
    """Command to list CLI plugins."""

    enabled_only: bool = False
    installed_only: bool = False
    user_id: UUID | None = None


class GetSessionInfoCommand:
    """Command to get CLI session information."""

    session_id: UUID
    user_id = None
