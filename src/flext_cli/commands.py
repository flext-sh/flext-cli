"""FLEXT CLI Commands - Single unified class following FLEXT standards.

Command creation and management using flext-core patterns.
Single FlextCliCommands class with nested helpers following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import override

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)

from flext_cli.constants import FlextCliConstants


class FlextCliCommands(FlextService[FlextTypes.Dict]):
    """Single unified CLI commands class following FLEXT standards.

    Provides CLI command registration and management using flext-core patterns.
    Follows FLEXT pattern: one class per module with nested helpers.
    """

    class _CliGroup:
        """Nested helper for CLI group operations."""

        def __init__(
            self, name: str, description: str, commands: FlextTypes.Dict
        ) -> None:
            """Initialize CLI group."""
            self.name = name
            self.description = description
            self.commands = commands

    # Attribute declarations - override FlextService optional types
    # These are guaranteed initialized in __init__
    _logger: FlextLogger | None
    _container: FlextContainer | None

    @override
    def __init__(
        self, name: str = "flext", description: str = "", **data: object
    ) -> None:
        """Initialize CLI commands manager with Phase 1 context enrichment."""
        super().__init__(**data)
        # Logger and container inherited from FlextService via FlextMixins
        self._name = name
        self._description = description
        self._commands: FlextTypes.NestedDict = {}
        self._cli_group = self._CliGroup(
            name=name,
            description=description,
            commands={},
        )

    @override
    def execute(self) -> FlextResult[FlextTypes.Dict]:
        """Execute the main domain service operation - required by FlextService."""
        return FlextResult[FlextTypes.Dict].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": FlextCliConstants.FLEXT_CLI,
            "commands": list(self._commands.keys()),
        })

    def register_command(
        self,
        name: str,
        handler: Callable[[], object] | Callable[[FlextTypes.StringList], object],
        description: str = "",
    ) -> FlextResult[None]:
        """Register a command.

        Args:
            name: Command name
            handler: Command handler function
            description: Command description

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            self._commands[name] = {
                "name": name,
                "handler": handler,
                "description": description,
            }
            self._cli_group.commands[name] = self._commands[name]
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Command registration failed: {e}")

    def unregister_command(self, name: str) -> FlextResult[None]:
        """Unregister a command.

        Args:
            name: Command name

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            if name in self._commands:
                del self._commands[name]
                if name in self._cli_group.commands:
                    del self._cli_group.commands[name]
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(f"Command not found: {name}")
        except Exception as e:
            return FlextResult[None].fail(f"Command unregistration failed: {e}")

    def create_command_group(
        self,
        name: str,
        description: str = "",
        commands: FlextTypes.Dict | None = None,
    ) -> FlextResult[object]:
        """Create a command group.

        Args:
            name: Group name
            description: Group description
            commands: Dictionary of command names and objects in group

        Returns:
            FlextResult[object]: Group object or error

        """
        try:
            group = self._CliGroup(
                name=name,
                description=description,
                commands=commands or {},
            )
            return FlextResult[object].ok(group)
        except Exception as e:
            return FlextResult[object].fail(f"Group creation failed: {e}")

    def run_cli(
        self,
        args: FlextTypes.StringList | None = None,
        *,
        standalone_mode: bool = True,
    ) -> FlextResult[None]:
        """Run the CLI interface.

        Args:
            args: Command line arguments
            standalone_mode: Whether to run in standalone mode

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            # Check if args contain invalid commands
            if args:
                for arg in args:
                    if arg.startswith("--"):
                        continue  # Skip options
                    if arg not in self._commands:
                        return FlextResult[None].fail(f"Command not found: {arg}")

            # Log CLI execution mode for debugging
            self._logger.debug(
                f"CLI execution mode: standalone={standalone_mode}, args={args}"
            )

            # For now, just execute the service
            result = self.execute()
            if result.is_success:
                return FlextResult[None].ok(None)
            return FlextResult[None].fail(result.error or "CLI execution failed")
        except Exception as e:
            return FlextResult[None].fail(f"CLI execution failed: {e}")

    def get_click_group(self) -> object:
        """Get the Click group object.

        Returns:
            Click group object

        """
        return self._cli_group

    def execute_command(
        self,
        command_name: str,
        args: FlextTypes.StringList | None = None,
        timeout: int = 30,
    ) -> FlextResult[object]:
        """Execute a specific command.

        Args:
            command_name: Name of the command to execute
            args: Command arguments
            timeout: Command timeout in seconds

        Returns:
            FlextResult[object]: Command result

        """
        try:
            # Log timeout parameter for future use
            self._logger.debug(
                f"Executing command {command_name} with timeout {timeout}s"
            )

            if command_name not in self._commands:
                return FlextResult[object].fail(f"Command not found: {command_name}")

            command_info = self._commands[command_name]
            if isinstance(command_info, dict) and "handler" in command_info:
                handler: object = command_info.get("handler")
                if handler is not None and callable(handler):
                    # Pass args to handler if it accepts them
                    if args:
                        try:
                            result = handler(args)
                        except TypeError:
                            # Handler doesn't accept args, call without them
                            result = handler()
                    else:
                        result = handler()
                    return FlextResult[object].ok(result)
                return FlextResult[object].fail(
                    f"Handler is not callable: {command_name}"
                )
            return FlextResult[object].fail(
                f"Invalid command structure: {command_name}"
            )
        except Exception as e:
            return FlextResult[object].fail(f"Command execution failed: {e}")

    def get_commands(self) -> FlextTypes.NestedDict:
        """Get all registered commands.

        Returns:
            FlextTypes.NestedDict: Dictionary of registered commands

        """
        return self._commands.copy()

    def clear_commands(self) -> FlextResult[int]:
        """Clear all registered commands.

        Returns:
            FlextResult[int]: Number of commands cleared

        """
        try:
            count = len(self._commands)
            self._commands.clear()
            self._cli_group.commands.clear()
            return FlextResult[int].ok(count)
        except Exception as e:
            return FlextResult[int].fail(f"Failed to clear commands: {e}")

    def list_commands(self) -> FlextResult[FlextTypes.StringList]:
        """List all registered commands.

        Returns:
            FlextResult[FlextTypes.StringList]: List of command names

        """
        try:
            command_names = list(self._commands.keys())
            return FlextResult[FlextTypes.StringList].ok(command_names)
        except Exception as e:
            return FlextResult[FlextTypes.StringList].fail(
                f"Failed to list commands: {e}"
            )

    def create_main_cli(self) -> FlextCliCommands:
        """Create the main CLI instance.

        Returns:
            FlextCliCommands: Main CLI instance

        """
        return FlextCliCommands(name=self._name, description=self._description)


__all__ = ["FlextCliCommands"]
