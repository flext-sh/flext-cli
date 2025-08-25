"""CLI domain entities."""

from __future__ import annotations

from flext_core import FlextEntityId, FlextResult

from flext_cli.constants import FlextCliConstants
from flext_cli.models import (
    FlextCliCommand as CLICommand,
    FlextCliCommandType,
    FlextCliPlugin,
    FlextCliSession,
)

# CommandType moved to models.py - import from there


class FlextCliEntityFactory:
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
            entity = CLICommand(id=FlextEntityId(name), command_line=command_line)
            # best-effort: tentar atribuir campos adicionais se existirem
            try:
                if command_type is not None and hasattr(entity, "command_type"):
                    # Convert local CommandType to FlextCliCommandType using value
                    entity.command_type = FlextCliCommandType(command_type.value)
                if hasattr(entity, "name"):
                    entity.name = name
            except Exception:
                ...
            return FlextResult[CLICommand].ok(entity)
        except Exception as e:
            return FlextResult[CLICommand].fail(
                f"{FlextCliConstants.CliErrors.COMMAND_EXECUTION_FAILED}: {e!s}",
            )

    @staticmethod
    def create_plugin(
        *,
        name: str,
        entry_point: str,
        commands: list[str] | None = None,
        plugin_version: str | None = None,
    ) -> FlextResult[FlextCliPlugin]:
        """Create a `FlextCliPlugin` instance for tests.

        Args:
            name: Plugin identifier and display name.
            entry_point: Import path for the plugin entry point.
            commands: Optional list of supported command names.
            plugin_version: Optional plugin version string.

        Returns:
            FlextResult with the created `FlextCliPlugin` or a failure message.

        """
        try:
            # Use individual arguments instead of **kwargs to avoid type issues
            entity = FlextCliPlugin(
                name=name,
                entry_point=entry_point,
                commands=commands or [],
                plugin_version=plugin_version or "0.1.0",
            )
            return FlextResult[FlextCliPlugin].ok(entity)
        except Exception as e:
            return FlextResult[FlextCliPlugin].fail(
                f"{FlextCliConstants.CliErrors.PLUGIN_ENTRY_POINT_EMPTY}: {e!s}",
            )

    @staticmethod
    def create_session(*, session_id: str) -> FlextResult[FlextCliSession]:
        """Create a `FlextCliSession` instance for tests.

        Args:
            session_id: Identifier used for both the session `id` and `user_id`.

        Returns:
            FlextResult with the created `FlextCliSession` or a failure message.

        """
        try:
            # FlextCliSession requires a non-empty user_id; map session_id to user_id for tests
            if not session_id:
                return FlextResult[FlextCliSession].fail(
                    FlextCliConstants.CliErrors.SESSION_VALIDATION_FAILED,
                )
            entity = FlextCliSession(id=FlextEntityId(session_id), user_id=session_id)
            return FlextResult[FlextCliSession].ok(entity)
        except Exception as e:
            return FlextResult[FlextCliSession].fail(
                f"{FlextCliConstants.CliErrors.SESSION_VALIDATION_FAILED}: {e!s}",
            )


__all__ = [
    # "CommandType",  # Moved to models.py
    "FlextCliEntityFactory",
]
