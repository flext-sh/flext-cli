"""Application commands for tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from flext_cli.entities import CommandType

# Type alias for command arguments and options
AnyPrimitive = str | int | float | bool | None


@dataclass
class ExecuteCommandCommand:
    """Execute a command with specified arguments and options."""

    name: str
    command_line: str
    command_type: CommandType = CommandType.SYSTEM
    timeout_seconds: float | None = None
    arguments: dict[str, AnyPrimitive] | None = None
    options: dict[str, AnyPrimitive] = field(default_factory=dict)
    user_id: UUID | None = None
    session_id: str | None = None
    working_directory: str | None = None
    environment: dict[str, str] | None = None


@dataclass
class CancelCommandCommand:
    """Cancel a running command."""

    command_id: UUID
    user_id: UUID | None = None


@dataclass
class CreateConfigCommand:
    """Create a new configuration."""

    name: str | None = None
    description: str | None = None
    config_data: dict[str, AnyPrimitive] | None = field(default=None)
    config_type: str | None = None
    version: str = "0.9.0"
    user_id: UUID | None = None
    is_global: bool = False


@dataclass
class UpdateConfigCommand:
    """Update an existing configuration."""

    config_id: UUID | None = None
    name: str | None = None
    description: str | None = None
    config_data: dict[str, AnyPrimitive] = field(default_factory=dict)
    version: str | None = None
    user_id: UUID | None = None


@dataclass
class DeleteConfigCommand:
    """Delete a configuration."""

    config_id: UUID | None = None
    user_id: UUID | None = None


@dataclass
class ValidateConfigCommand:
    """Validate a configuration."""

    config_id: UUID | None = None
    user_id: UUID | None = None


@dataclass
class StartSessionCommand:
    """Start a new session."""

    session_id: str | None = None
    user_id: UUID | None = None
    working_directory: str | None = None
    environment: dict[str, str] | None = None


@dataclass
class EndSessionCommand:
    """End a session."""

    session_id: UUID | None = None
    user_id: UUID | None = None


@dataclass
class InstallPluginCommand:
    """Install a new plugin."""

    name: str | None = None
    version: str | None = None
    entry_point: str | None = None
    commands: list[str] | None = None
    dependencies: list[str] | None = None
    author: str | None = None
    license: str | None = None
    repository_url: str | None = None
    user_id: UUID | None = None


@dataclass
class UninstallPluginCommand:
    """Uninstall a plugin."""

    plugin_id: UUID | None = None
    user_id: UUID | None = None


@dataclass
class EnablePluginCommand:
    """Enable a plugin."""

    plugin_id: UUID | None = None
    user_id: UUID | None = None


@dataclass
class DisablePluginCommand:
    """Disable a plugin."""

    plugin_id: UUID | None = None
    user_id: UUID | None = None


@dataclass
class ListCommandsCommand:
    """List available commands."""

    command_type: CommandType | None = None
    user_id: UUID | None = None
    session_id: str | None = None


@dataclass
class GetCommandHistoryCommand:
    """Get command history."""

    user_id: UUID | None = None
    session_id: str | None = None
    limit: int = 100
    command_type: CommandType | None = None


@dataclass
class GetCommandStatusCommand:
    """Get the status of a command."""

    command_id: UUID | None = None
    user_id: UUID | None = None


@dataclass
class ListConfigsCommand:
    """List configurations."""

    config_type: str | None = None
    user_id: UUID | None = None
    include_global: bool = True


@dataclass
class ListPluginsCommand:
    """List plugins."""

    enabled_only: bool = False
    installed_only: bool = False
    user_id: UUID | None = None


@dataclass
class GetSessionInfoCommand:
    """Get session information."""

    session_id: UUID | None = None
    user_id: UUID | None = None
