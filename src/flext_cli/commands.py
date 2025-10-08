"""FLEXT CLI Commands - Single unified class following FLEXT standards.

Command creation and management using flext-core patterns.
Single FlextCliCommands class with nested helpers following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import override

from flext_core import FlextCore

from flext_cli.constants import FlextCliConstants


class FlextCliCommands(FlextCore.Service[FlextCore.Types.Dict]):
    """Single unified CLI commands class following FLEXT standards.

    Provides CLI command registration and management using flext-core patterns.
    Follows FLEXT pattern: one class per module with nested helpers.
    """

    class _CliGroup:
        """Nested helper for CLI group operations."""

        def __init__(
            self, name: str, description: str, commands: FlextCore.Types.Dict
        ) -> None:
            """Initialize CLI group."""
            self.name = name
            self.description = description
            self.commands = commands

    @override
    def __init__(
        self, name: str = "flext", description: str = "", **data: object
    ) -> None:
        """Initialize CLI commands manager with Phase 1 context enrichment."""
        super().__init__(**data)
        # Initialize logger (inherited from FlextCore.Service)
        self.logger = FlextCore.Logger(__name__)
        self._name = name
        self._description = description
        self._commands: FlextCore.Types.NestedDict = {}
        self._cli_group = self._CliGroup(
            name=name,
            description=description,
            commands={},
        )

    @override
    def execute(self) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Execute the main domain service operation - required by FlextCore.Service."""
        return FlextCore.Result[FlextCore.Types.Dict].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": FlextCliConstants.FLEXT_CLI,
            "commands": list(self._commands.keys()),
        })

    def register_command(
        self,
        name: str,
        handler: Callable[[], object] | Callable[[FlextCore.Types.StringList], object],
        description: str = "",
    ) -> FlextCore.Result[None]:
        """Register a command.

        Args:
            name: Command name
            handler: Command handler function
            description: Command description

        Returns:
            FlextCore.Result[None]: Success or error

        """
        try:
            self._commands[name] = {
                "name": name,
                "handler": handler,
                "description": description,
            }
            self._cli_group.commands[name] = self._commands[name]
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.COMMAND_REGISTRATION_FAILED.format(
                    error=e
                )
            )

    def unregister_command(self, name: str) -> FlextCore.Result[None]:
        """Unregister a command.

        Args:
            name: Command name

        Returns:
            FlextCore.Result[None]: Success or error

        """
        try:
            if name in self._commands:
                del self._commands[name]
                if name in self._cli_group.commands:
                    del self._cli_group.commands[name]
                return FlextCore.Result[None].ok(None)
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(name=name)
            )
        except Exception as e:
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.COMMAND_UNREGISTRATION_FAILED.format(
                    error=e
                )
            )

    def create_command_group(
        self,
        name: str,
        description: str = "",
        commands: FlextCore.Types.Dict | None = None,
    ) -> FlextCore.Result[object]:
        """Create a command group.

        Args:
            name: Group name
            description: Group description
            commands: Dictionary of command names and objects in group

        Returns:
            FlextCore.Result[object]: Group object or error

        """
        try:
            group = self._CliGroup(
                name=name,
                description=description,
                commands=commands or {},
            )
            return FlextCore.Result[object].ok(group)
        except Exception as e:
            return FlextCore.Result[object].fail(
                FlextCliConstants.ErrorMessages.GROUP_CREATION_FAILED.format(error=e)
            )

    def run_cli(
        self,
        args: FlextCore.Types.StringList | None = None,
        *,
        standalone_mode: bool = True,
    ) -> FlextCore.Result[None]:
        """Run the CLI interface.

        Args:
            args: Command line arguments
            standalone_mode: Whether to run in standalone mode

        Returns:
            FlextCore.Result[None]: Success or error

        """
        try:
            # Check if args contain invalid commands
            if args:
                for arg in args:
                    if arg.startswith("--"):
                        continue  # Skip options
                    if arg not in self._commands:
                        return FlextCore.Result[None].fail(
                            FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(
                                name=arg
                            )
                        )

            # Log CLI execution mode for debugging
            self.logger.debug(
                f"CLI execution mode: standalone={standalone_mode}, args={args}"
            )

            # For now, just execute the service
            result = self.execute()
            if result.is_success:
                return FlextCore.Result[None].ok(None)
            return FlextCore.Result[None].fail(
                result.error or FlextCliConstants.ErrorMessages.CLI_EXECUTION_FAILED
            )
        except Exception as e:
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e)
            )

    def get_click_group(self) -> object:
        """Get the Click group object.

        Returns:
            Click group object

        """
        return self._cli_group

    def execute_command(
        self,
        command_name: str,
        args: FlextCore.Types.StringList | None = None,
        timeout: int = 30,
    ) -> FlextCore.Result[object]:
        """Execute a specific command.

        Args:
            command_name: Name of the command to execute
            args: Command arguments
            timeout: Command timeout in seconds

        Returns:
            FlextCore.Result[object]: Command result

        """
        try:
            # Log timeout parameter for future use
            self.logger.debug(
                f"Executing command {command_name} with timeout {timeout}s"
            )

            if command_name not in self._commands:
                return FlextCore.Result[object].fail(
                    f"Command not found: {command_name}"
                )

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
                    return FlextCore.Result[object].ok(result)
                return FlextCore.Result[object].fail(
                    f"Handler is not callable: {command_name}"
                )
            return FlextCore.Result[object].fail(
                f"Invalid command structure: {command_name}"
            )
        except Exception as e:
            return FlextCore.Result[object].fail(
                FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(error=e)
            )

    def get_commands(self) -> FlextCore.Types.NestedDict:
        """Get all registered commands.

        Returns:
            FlextCore.Types.NestedDict: Dictionary of registered commands

        """
        return self._commands.copy()

    def clear_commands(self) -> FlextCore.Result[int]:
        """Clear all registered commands.

        Returns:
            FlextCore.Result[int]: Number of commands cleared

        """
        try:
            count = len(self._commands)
            self._commands.clear()
            self._cli_group.commands.clear()
            return FlextCore.Result[int].ok(count)
        except Exception as e:
            return FlextCore.Result[int].fail(
                FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(error=e)
            )

    def list_commands(self) -> FlextCore.Result[FlextCore.Types.StringList]:
        """List all registered commands.

        Returns:
            FlextCore.Result[FlextCore.Types.StringList]: List of command names

        """
        try:
            command_names = list(self._commands.keys())
            return FlextCore.Result[FlextCore.Types.StringList].ok(command_names)
        except Exception as e:
            return FlextCore.Result[FlextCore.Types.StringList].fail(
                f"Failed to list commands: {e}"
            )

    def create_main_cli(self) -> FlextCliCommands:
        """Create the main CLI instance.

        Returns:
            FlextCliCommands: Main CLI instance

        """
        return FlextCliCommands(name=self._name, description=self._description)


__all__ = ["FlextCliCommands"]
