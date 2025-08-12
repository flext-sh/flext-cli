"""Legacy-compatible CLI domain entities used in tests.

This module adapts the modern `flext_cli.models` API to legacy names and
provides small factory helpers to create valid instances for testing.
"""

from __future__ import annotations

from enum import StrEnum

from flext_core import FlextResult

from flext_cli.models import (
    CommandStatus,
    FlextCliCommand as CLICommand,
    FlextCliCommandStatus,
    FlextCliConfiguration as CLIConfig,
    FlextCliOutput,
    FlextCliOutputFormat,
    FlextCliPlugin as CLIPlugin,
    FlextCliSession as CLISession,
    PluginStatus,
    SessionStatus,
)


class CommandType(StrEnum):
    """Enumeration of supported CLI command categories."""

    SYSTEM = "system"
    PIPELINE = "pipeline"
    PLUGIN = "plugin"
    DATA = "data"
    CONFIG = "config"
    AUTH = "auth"
    MONITORING = "monitoring"
    CLI = "cli"
    SCRIPT = "script"
    SQL = "sql"


class CLIEntityFactory:
    """Factory helpers used by tests to create entities safely."""

    @staticmethod
    def create_command(
        *,
        name: str,
        command_line: str,
    ) -> FlextResult[CLICommand]:
        """Create a `CLICommand` instance for tests.

        Args:
            name: Identifier to assign to the command (mapped to `id`).
            command_line: Shell command line to execute.

        Returns:
            FlextResult with the created `CLICommand` or a failure message.

        """
        try:
            # CLICommand does not accept name/command_type fields in the new model
            entity = CLICommand(id=name, command_line=command_line)
            return FlextResult.ok(entity)
        except Exception as e:  # noqa: BLE001
            return FlextResult.fail(str(e))

    @staticmethod
    def create_plugin(
        *,
        name: str,
        entry_point: str,
        commands: list[str] | None = None,
        plugin_version: str | None = None,
    ) -> FlextResult[CLIPlugin]:
        """Create a `CLIPlugin` instance for tests.

        Args:
            name: Plugin identifier and display name.
            entry_point: Import path for the plugin entry point.
            commands: Optional list of supported command names.
            plugin_version: Optional plugin version string.

        Returns:
            FlextResult with the created `CLIPlugin` or a failure message.

        """
        try:
            kwargs: dict[str, object] = {
                "id": name,
                "name": name,
                "entry_point": entry_point,
                "commands": commands or [],
            }
            if plugin_version is not None:
                kwargs["plugin_version"] = plugin_version
            entity = CLIPlugin(**kwargs)  # type: ignore[arg-type]
            return FlextResult.ok(entity)
        except Exception as e:  # noqa: BLE001
            return FlextResult.fail(str(e))

    @staticmethod
    def create_session(*, session_id: str) -> FlextResult[CLISession]:
        """Create a `CLISession` instance for tests.

        Args:
            session_id: Identifier used for both the session `id` and `user_id`.

        Returns:
            FlextResult with the created `CLISession` or a failure message.

        """
        try:
            # CLISession requires a non-empty user_id; map session_id to user_id for tests
            if not session_id:
                msg = "String should have at least 1 character"
                raise ValueError(msg)
            entity = CLISession(id=session_id, user_id=session_id)
            return FlextResult.ok(entity)
        except Exception as e:  # noqa: BLE001
            return FlextResult.fail(str(e))


__all__ = [
    "CLICommand",
    "CLIConfig",
    "CLIEntityFactory",
    "CLIPlugin",
    "CLISession",
    "CommandStatus",
    "CommandType",
    "FlextCliCommandStatus",
    "FlextCliOutput",
    "FlextCliOutputFormat",
    "PluginStatus",
    "SessionStatus",
]
