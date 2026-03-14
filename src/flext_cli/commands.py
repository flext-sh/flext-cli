"""FLEXT CLI Commands - Command registration and execution service.

Command creation and management using flext-core patterns.
Provides command registration, execution, grouping, and lifecycle management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping, Sequence
from typing import Self, override

from flext_core import r
from rich.errors import ConsoleError, LiveError, StyleError

from flext_cli import FlextCliServiceBase, c, m, t
from flext_cli.typings import FlextCliTypes

FlextCliCommandGroup = m.Cli.CliCommandGroup
FlextCliCommandEntryModel = m.Cli.CommandEntryModel


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

    def __init__(self, name: str = "flext", description: str = "FLEXT CLI") -> None:
        """Initialize commands service.

        Args:
            name: CLI application name.
            description: CLI application description.

        """
        super().__init__(
            config_type=None,
            config_overrides=None,
            initial_context=None,
        )
        self._name = name
        self._description = description
        self._commands: dict[str, FlextCliCommandEntryModel] = {}
        self._groups: dict[str, FlextCliCommandGroup] = {}

    @property
    def description(self) -> str:
        """Return CLI description."""
        return self._description

    @property
    def name(self) -> str:
        """Return CLI name."""
        return self._name

    @staticmethod
    def _normalize_handler_result(
        result: r | None, command_name: str
    ) -> r:
        """Normalize handler output to r."""
        if result is None:
            return r.ok({"status": "success", "command": command_name})
        if result.is_success:
            return r.ok(result.value)
        error_value = result.error
        return r.fail(str(error_value) if error_value else "Command failed")

    def clear_commands(self) -> r[int]:
        """Clear all registered commands.

        Returns:
            r[int]: Number of commands cleared.

        """
        count = len(self._commands)
        self._commands.clear()
        self._groups.clear()
        return r[int].ok(count)

    def create_command_group(
        self,
        name: str,
        description: str = "",
        commands: Mapping[str, FlextCliCommandEntryModel] | None = None,
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
        group_commands: dict[str, FlextCliTypes.Cli.JsonValue] = {
            key: value.model_dump(mode="json") for key, value in commands.items()
        }
        group = FlextCliCommandGroup.model_validate({
            "name": name,
            "description": description,
            "commands": group_commands,
        })
        self._groups[name] = group
        return r[FlextCliCommandGroup].ok(group)

    def create_main_cli(self) -> Self:
        """Create the main CLI instance.

        Returns:
            Self: This commands instance configured as main CLI.

        """
        return self

    @override
    def execute(self) -> r[Mapping[str, FlextCliTypes.Cli.JsonValue]]:
        """Execute commands service - returns service status.

        Business Rule:
        ──────────────
        Returns status information about the commands service including
        registered commands count.

        Returns:
            r[dict]: Service status with commands count.

        """
        return r[Mapping[str, FlextCliTypes.Cli.JsonValue]].ok({
            "app_name": c.Cli.FLEXT_CLI,
            "is_initialized": True,
            "commands_count": len(self._commands),
        })

    def execute_command(
        self, name: str, args: Sequence[str] | None = None, **kwargs: t.Scalar
    ) -> r:
        """Execute a registered CLI command.

        Args:
            name: Command name to execute.
            args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            r: Command execution result.

        """
        if not name.strip():
            return r.fail("Invalid command name")
        if name not in self._commands:
            return r.fail(f"Command not found: {name}")
        cmd_info = self._commands[name]
        handler = cmd_info.handler
        if not callable(handler):
            return r.fail(f"Handler not callable for: {name}")
        try:
            result: r | None = None
            execution_attempted = False
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
            return r.fail(f"Command execution failed: {e}")

    def get_click_group(self) -> FlextCliCommandGroup:
        """Get Click group representation.

        Returns:
            FlextCliCommandGroup: Click group info with name and commands.

        Note:
            This returns a FlextCliCommandGroup object, not actual Click objects.
            Use FlextCliCli for actual Click integration.

        """
        group_commands: dict[str, FlextCliTypes.Cli.JsonValue] = {
            key: value.model_dump(mode="json") for key, value in self._commands.items()
        }
        return FlextCliCommandGroup.model_validate({
            "name": self._name,
            "description": self._description,
            "commands": group_commands,
        })

    def get_commands(self) -> Mapping[str, FlextCliCommandEntryModel]:
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

    def register_command(self, name: str, handler: Callable[..., r]) -> r[bool]:
        """Register a CLI command.

        Args:
            name: Command name.
            handler: Command handler callable.

        Returns:
            r[bool]: Success if registered, failure otherwise.

        """
        if not name.strip():
            return r[bool].fail("Command name must be non-empty string")
        self._commands[name] = FlextCliCommandEntryModel(name=name, handler=handler)
        return r[bool].ok(value=True)

    def run_cli(self, args: Sequence[str] | None = None) -> r:
        """Run CLI with given arguments.

        Args:
            args: CLI arguments to process.

        Returns:
            r: Execution result.

        """
        if not args:
            return r.ok({"status": "success", "message": "No args"})
        cmd_name = args[0] if args else ""
        cmd_args = list(args[1:]) if len(args) > 1 else []
        if cmd_name in {"--help", "-h"}:
            return r.ok({
                "status": "help",
                "commands": list(self._commands.keys()),
            })
        if cmd_name in {"--version", "-v"}:
            return r.ok({"status": "version", "name": self._name})
        if cmd_name not in self._commands:
            return r.fail(f"Command not found: {cmd_name}")
        return self.execute_command(cmd_name, args=cmd_args)

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
