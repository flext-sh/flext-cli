"""FLEXT CLI Commands - Command registration and execution service.

Command creation and management using flext-core patterns.
Provides command registration, execution, grouping, and lifecycle management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol, Self, runtime_checkable

from flext_core import r

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import c
from flext_cli.typings import t


@runtime_checkable
class CommandHandler(Protocol):
    """Protocol for command handler callables."""

    def __call__(
        self,
        *args: t.GeneralValueType,
        **kwargs: t.GeneralValueType,
    ) -> t.GeneralValueType:
        """Execute command with variable arguments."""
        ...


# Type alias for command entry dict
CommandEntry = dict[str, str | CommandHandler]


@dataclass
class CommandGroup:
    """Represents a command group with name, description, and commands."""

    name: str
    description: str = ""
    commands: dict[str, CommandEntry] = field(default_factory=dict)


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
        self._commands: dict[str, CommandEntry] = {}
        self._groups: dict[str, CommandGroup] = {}

    @property
    def name(self) -> str:
        """Return CLI name."""
        return self._name

    @property
    def description(self) -> str:
        """Return CLI description."""
        return self._description

    def execute(self) -> r[dict[str, t.GeneralValueType]]:
        """Execute commands service - returns service status.

        Business Rule:
        ──────────────
        Returns status information about the commands service including
        registered commands count.

        Returns:
            r[dict]: Service status with commands count.

        """
        return r[dict[str, t.GeneralValueType]].ok({
            "app_name": c.Cli.FLEXT_CLI,
            "is_initialized": True,
            "commands_count": len(self._commands),
        })

    def register_command(
        self,
        name: str,
        handler: CommandHandler,
    ) -> r[bool]:
        """Register a CLI command.

        Args:
            name: Command name.
            handler: Command handler callable.

        Returns:
            r[bool]: Success if registered, failure otherwise.

        """
        if not isinstance(name, str) or not name.strip():
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
        **kwargs: t.GeneralValueType,
    ) -> r[t.GeneralValueType]:
        """Execute a registered CLI command.

        Args:
            name: Command name to execute.
            args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            r[t.GeneralValueType]: Command execution result.

        """
        if not name or not isinstance(name, str):
            return r[t.GeneralValueType].fail("Invalid command name")

        if name not in self._commands:
            return r[t.GeneralValueType].fail(f"Command not found: {name}")

        cmd_info = self._commands[name]
        handler = cmd_info.get("handler")

        if not callable(handler):
            return r[t.GeneralValueType].fail(f"Handler not callable for: {name}")

        try:
            # Try to execute handler with provided arguments
            result: t.GeneralValueType | None = None

            # Attempt execution with various argument combinations
            execution_attempted = False

            # Try with both args and kwargs
            if args or kwargs:
                try:
                    result = handler(*args, **kwargs) if args else handler(**kwargs)
                    execution_attempted = True
                except TypeError:
                    # Handler signature mismatch - try without arguments
                    pass

            # If no args/kwargs or execution failed, try with no arguments
            if not execution_attempted:
                result = handler()

            # Handle result: None means success with default response
            if result is None:
                return r[t.GeneralValueType].ok({"status": "success", "command": name})

            # If handler already returns FlextResult, extract and re-wrap
            if isinstance(result, r):
                if result.is_success:
                    return r[t.GeneralValueType].ok(result.value)
                return r[t.GeneralValueType].fail(result.error or "Command failed")

            # Return the handler's result wrapped in FlextResult
            return r[t.GeneralValueType].ok(result)
        except Exception as e:
            return r[t.GeneralValueType].fail(f"Command execution failed: {e}")

    def get_commands(self) -> dict[str, CommandEntry]:
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
    ) -> r[t.GeneralValueType]:
        """Run CLI with given arguments.

        Args:
            args: CLI arguments to process.

        Returns:
            r[t.GeneralValueType]: Execution result.

        """
        if not args:
            return r[t.GeneralValueType].ok({"status": "success", "message": "No args"})

        cmd_name = args[0] if args else ""
        cmd_args = list(args[1:]) if len(args) > 1 else []

        # Handle special options
        if cmd_name in {"--help", "-h"}:
            return r[t.GeneralValueType].ok({
                "status": "help",
                "commands": list(self._commands.keys()),
            })

        if cmd_name in {"--version", "-v"}:
            return r[t.GeneralValueType].ok({"status": "version", "name": self._name})

        if cmd_name not in self._commands:
            return r[t.GeneralValueType].fail(f"Command not found: {cmd_name}")

        return self.execute_command(cmd_name, args=cmd_args)

    def create_command_group(
        self,
        name: str,
        description: str = "",
        commands: dict[str, CommandEntry] | None = None,
    ) -> r[CommandGroup]:
        """Create a command group.

        Args:
            name: Group name.
            description: Group description.
            commands: Dict of command name to handler info.

        Returns:
            r[CommandGroup]: Command group, or failure.

        """
        if not isinstance(name, str) or not name.strip():
            return r[CommandGroup].fail("Group name must be non-empty string")

        if commands is None:
            return r[CommandGroup].fail("Commands are required for group creation")

        # Type system ensures commands is Mapping after None check
        group = CommandGroup(
            name=name,
            description=description,
            commands=dict(commands),
        )
        self._groups[name] = group
        return r[CommandGroup].ok(group)

    def get_click_group(self) -> CommandGroup:
        """Get Click group representation.

        Returns:
            CommandGroup: Click group info with name and commands.

        Note:
            This returns a CommandGroup object, not actual Click objects.
            Use FlextCliCli for actual Click integration.

        """
        return CommandGroup(
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
