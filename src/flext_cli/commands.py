"""FLEXT CLI Commands - Command registration and execution service.

Command creation and management using flext-core patterns.
Provides command registration, execution, grouping, and lifecycle management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import Protocol, Self, runtime_checkable

from flext_core import r
from pydantic import BaseModel, ConfigDict, Field
from rich.errors import ConsoleError, LiveError, StyleError

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import c
from flext_cli.typings import t


@runtime_checkable
class FlextCliCommandHandler(Protocol):
    """Protocol for command handler callables."""

    def __call__(
        self,
        *args: t.JsonValue,
        **kwargs: t.JsonValue,
    ) -> r[t.JsonValue]:
        """Execute command with variable arguments."""
        ...


# Type alias for command entry dict
FlextCliCommandEntry = Mapping[str, str | FlextCliCommandHandler]


class FlextCliCommandGroup(BaseModel):
    """Represents a command group with name, description, and commands."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    name: str = Field(..., description="Command group name")
    description: str = Field(default="", description="Command group description")
    commands: Mapping[str, FlextCliCommandEntry] = Field(
        default_factory=dict,
        description="Mapping of command names to command entries",
    )


class FlextCliCommands(FlextCliServiceBase):
    """CLI commands service for command registration and execution.

    Provides:
    - Command registration and unregistration
    - Command execution with arguments
    - Command groups creation
    - Command listing and discovery

    Business Rules:
    ───────────────
    1. Command names MUST be non-empty strings
    2. Command handlers MUST be callable
    3. Commands MUST be registered before execution
    4. Command groups MUST have at least one command

    """

    def __init__(
        self,
        name: str = "flext",
        description: str = "FLEXT CLI",
    ) -> None:
        """Initialize commands service.

        Args:
            name: CLI application name.
            description: CLI application description.

        """
        super().__init__()
        self._name = name
        self._description = description
        self._commands: dict[str, FlextCliCommandEntry] = {}
        self._groups: dict[str, FlextCliCommandGroup] = {}

    @property
    def name(self) -> str:
        """Return CLI name."""
        return self._name

    @property
    def description(self) -> str:
        """Return CLI description."""
        return self._description

    def execute(self) -> r[Mapping[str, t.JsonValue]]:
        """Execute commands service - returns service status.

        Business Rule:
        ──────────────
        Returns status information about the commands service including
        registered commands count.

        Returns:
            r[dict]: Service status with commands count.

        """
        return r[Mapping[str, t.JsonValue]].ok({
            "app_name": c.Cli.FLEXT_CLI,
            "is_initialized": True,
            "commands_count": len(self._commands),
        })

    def register_command(
        self,
        name: str,
        handler: FlextCliCommandHandler,
    ) -> r[bool]:
        """Register a CLI command.

        Args:
            name: Command name.
            handler: Command handler callable.

        Returns:
            r[bool]: Success if registered, failure otherwise.

        """
        if not name.strip():
            return r[bool].fail("Command name must be non-empty string")
        # Type system ensures handler is callable via CommandHandler Protocol

        self._commands[name] = {
            "handler": handler,
            "name": name,
        }
        return r[bool].ok(value=True)

    def unregister_command(self, name: str) -> r[bool]:
        """Unregister a CLI command.

        Args:
            name: Command name to unregister.

        Returns:
            r[bool]: Success if unregistered, failure if not found.

        """
        if name not in self._commands:
            return r[bool].fail(f"Command not found: {name}")

        del self._commands[name]
        return r[bool].ok(value=True)

    def execute_command(
        self,
        name: str,
        args: Sequence[str] | None = None,
        **kwargs: t.JsonValue,
    ) -> r[t.JsonValue]:
        """Execute a registered CLI command.

        Args:
            name: Command name to execute.
            args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            r[t.JsonValue]: Command execution result.

        """
        if not name.strip():
            return r[t.JsonValue].fail("Invalid command name")

        if name not in self._commands:
            return r[t.JsonValue].fail(f"Command not found: {name}")

        cmd_info = self._commands[name]
        handler = cmd_info.get("handler")

        if not callable(handler):
            return r[t.JsonValue].fail(f"Handler not callable for: {name}")

        try:
            # Try to execute handler with provided arguments
            result: r[t.JsonValue] | None = None

            # Attempt execution with various argument combinations
            execution_attempted = False

            # Try with both args and kwargs
            if args or kwargs:
                try:
                    result = handler(*args, **kwargs) if args else handler(**kwargs)
                    execution_attempted = True
                except TypeError as exc:
                    logging.getLogger(__name__).debug(
                        "Handler signature mismatch for %s, trying no-args: %s",
                        name,
                        exc,
                        exc_info=False,
                    )

            # If no args/kwargs or execution failed, try with no arguments
            if not execution_attempted:
                result = handler()

            return self._normalize_handler_result(result, name)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[t.JsonValue].fail(f"Command execution failed: {e}")

    @staticmethod
    def _normalize_handler_result(
        result: r[t.JsonValue] | None,
        command_name: str,
    ) -> r[t.JsonValue]:
        """Normalize handler output to FlextResult."""
        if result is None:
            return r[t.JsonValue].ok({"status": "success", "command": command_name})
        if result.is_success:
            return r[t.JsonValue].ok(result.value)
        error_value = result.error
        return r[t.JsonValue].fail(
            str(error_value) if error_value else "Command failed"
        )

    def get_commands(self) -> Mapping[str, FlextCliCommandEntry]:
        """Get all registered commands.

        Returns:
            Dict mapping command names to command info.

        """
        return dict(self._commands)

    def list_commands(self) -> r[list[str]]:
        """List all registered command names.

        Returns:
            r[list[str]]: List of command names.

        """
        return r[list[str]].ok(list(self._commands.keys()))

    def clear_commands(self) -> r[int]:
        """Clear all registered commands.

        Returns:
            r[int]: Number of commands cleared.

        """
        count = len(self._commands)
        self._commands.clear()
        self._groups.clear()
        return r[int].ok(count)

    def run_cli(
        self,
        args: Sequence[str] | None = None,
    ) -> r[t.JsonValue]:
        """Run CLI with given arguments.

        Args:
            args: CLI arguments to process.

        Returns:
            r[t.JsonValue]: Execution result.

        """
        if not args:
            return r[t.JsonValue].ok({"status": "success", "message": "No args"})

        cmd_name = args[0] if args else ""
        cmd_args = list(args[1:]) if len(args) > 1 else []

        # Handle special options
        if cmd_name in {"--help", "-h"}:
            return r[t.JsonValue].ok({
                "status": "help",
                "commands": list(self._commands.keys()),
            })

        if cmd_name in {"--version", "-v"}:
            return r[t.JsonValue].ok({"status": "version", "name": self._name})

        if cmd_name not in self._commands:
            return r[t.JsonValue].fail(f"Command not found: {cmd_name}")

        return self.execute_command(cmd_name, args=cmd_args)

    def create_command_group(
        self,
        name: str,
        description: str = "",
        commands: Mapping[str, FlextCliCommandEntry] | None = None,
    ) -> r[FlextCliCommandGroup]:
        """Create a command group.

        Args:
            name: Group name.
            description: Group description.
            commands: Dict of command name to handler info.

        Returns:
            r[FlextCliCommandGroup]: Command group, or failure.

        """
        if not name.strip():
            return r[FlextCliCommandGroup].fail("Group name must be non-empty string")

        if commands is None:
            return r[FlextCliCommandGroup].fail(
                "Commands are required for group creation"
            )

        # Type system ensures commands is Mapping after None check
        group = FlextCliCommandGroup(
            name=name,
            description=description,
            commands=dict(commands),
        )
        self._groups[name] = group
        return r[FlextCliCommandGroup].ok(group)

    def get_click_group(self) -> FlextCliCommandGroup:
        """Get Click group representation.

        Returns:
            FlextCliCommandGroup: Click group info with name and commands.

        Note:
            This returns a FlextCliCommandGroup object, not actual Click objects.
            Use FlextCliCli for actual Click integration.

        """
        return FlextCliCommandGroup(
            name=self._name,
            description=self._description,
            commands=dict(self._commands.items()),
        )

    def create_main_cli(self) -> Self:
        """Create the main CLI instance.

        Returns:
            Self: This commands instance configured as main CLI.

        """
        return self
