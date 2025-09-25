"""FLEXT CLI Commands - Single unified class following FLEXT standards.

Command creation and management using flext-core patterns.
Single FlextCliCommands class with nested helpers following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
)


class FlextCliCommands(FlextService[dict[str, object]]):
    """Single unified CLI commands class following FLEXT standards.

    Provides CLI command registration and management using flext-core patterns.
    Follows FLEXT pattern: one class per module with nested helpers.
    """

    class _CliGroup:
        """Nested helper for CLI group operations."""

        def __init__(
            self, name: str, description: str, commands: dict[str, object]
        ) -> None:
            """Initialize CLI group."""
            self.name = name
            self.description = description
            self.commands = commands

    def __init__(
        self, name: str = "flext", description: str = "", **data: object
    ) -> None:
        """Initialize CLI commands manager."""
        super().__init__(**data)
        self._name = name
        self._description = description
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()
        self._commands: dict[str, object] = {}
        self._cli_group = self._CliGroup(
            name=name,
            description=description,
            commands={},
        )

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute the main domain service operation - required by FlextService."""
        return FlextResult[dict[str, object]].ok({
            "status": "operational",
            "service": "flext-cli",
            "commands": list(self._commands.keys()),
        })

    async def execute_async(self) -> FlextResult[dict[str, object]]:
        """Execute the main domain service operation asynchronously."""
        return FlextResult[dict[str, object]].ok({
            "status": "operational",
            "service": "flext-cli",
            "commands": list(self._commands.keys()),
        })

    def register_command(
        self,
        name: str,
        handler: object,
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
        commands: dict[str, object] | None = None,
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
        args: list[str] | None = None,
        *,
        standalone_mode: bool = True,  # noqa: ARG002
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
        args: list[str] | None = None,  # noqa: ARG002
    ) -> FlextResult[object]:
        """Execute a specific command.

        Args:
            command_name: Name of the command to execute
            args: Command arguments

        Returns:
            FlextResult[object]: Command result

        """
        try:
            if command_name not in self._commands:
                return FlextResult[object].fail(f"Command not found: {command_name}")

            command_info = self._commands[command_name]
            if isinstance(command_info, dict) and "handler" in command_info:
                handler: object | None = command_info.get("handler")
                if handler is not None and callable(handler):
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

    def list_commands(self) -> FlextResult[list[str]]:
        """List all registered commands.

        Returns:
            FlextResult[list[str]]: List of command names

        """
        try:
            command_names = list(self._commands.keys())
            return FlextResult[list[str]].ok(command_names)
        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to list commands: {e}")

    def create_main_cli(self) -> FlextCliCommands:
        """Create the main CLI instance.

        Returns:
            FlextCliCommands: Main CLI instance

        """
        return FlextCliCommands(name=self._name, description=self._description)


__all__ = ["FlextCliCommands"]
