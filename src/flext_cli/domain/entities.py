"""CLI domain entities."""

from __future__ import annotations

from enum import StrEnum

from flext_core import FlextResult

from flext_cli.constants import FlextCliConstants
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
      command_type: CommandType | None = None,
    ) -> FlextResult[CLICommand]:
      """Create a `CLICommand` instance for tests.

      Args:
          name: Identifier to assign to the command (mapped to `id`).
          command_line: Shell command line to execute.
          command_type: Optional command type to assign to the command.

      Returns:
          FlextResult with the created `CLICommand` or a failure message.

      """
      try:
          # CLICommand does not accept name/command_type fields directly in the new model
          entity = CLICommand(id=name, command_line=command_line)
          # best-effort: tentar atribuir campos adicionais se existirem
          try:
              if command_type is not None and hasattr(entity, "command_type"):
                  entity.command_type = command_type.value
              if hasattr(entity, "name"):
                  entity.name = name
          except Exception:
              ...
          return FlextResult.ok(entity)
      except Exception as e:  # noqa: BLE001
          return FlextResult.fail(
              f"{FlextCliConstants.CliErrors.COMMAND_EXECUTION_FAILED}: {e!s}",
          )

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
          return FlextResult.fail(
              f"{FlextCliConstants.CliErrors.PLUGIN_ENTRY_POINT_EMPTY}: {e!s}",
          )

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
              return FlextResult.fail(
                  FlextCliConstants.CliErrors.SESSION_VALIDATION_FAILED,
              )
          entity = CLISession(id=session_id, user_id=session_id)
          return FlextResult.ok(entity)
      except Exception as e:  # noqa: BLE001
          return FlextResult.fail(
              f"{FlextCliConstants.CliErrors.SESSION_VALIDATION_FAILED}: {e!s}",
          )


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
