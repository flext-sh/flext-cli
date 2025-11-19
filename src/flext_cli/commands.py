"""FLEXT CLI Commands - Single unified class following FLEXT standards.

Command creation and management using flext-core patterns.
Single FlextCliCommands class with nested helpers following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable
from typing import override

from flext_core import FlextResult, FlextService, FlextTypes

from flext_cli.constants import FlextCliConstants


class FlextCliCommands(FlextService[FlextTypes.JsonDict]):
    """Single unified CLI commands class following FLEXT standards.

    Provides CLI command registration and management using flext-core patterns.
    Follows FLEXT pattern: one class per module with nested helpers.
    """

    # Logger is provided by FlextMixins mixin

    class _CliGroup:
        """Nested helper for CLI group operations."""

        def __init__(
            self, name: str, description: str, commands: dict[str, dict[str, object]]
        ) -> None:
            """Initialize CLI group."""
            self.name = name
            self.description = description
            self.commands = commands

    @override
    def __init__(
        self,
        name: str = FlextCliConstants.CommandsDefaults.DEFAULT_CLI_NAME,
        description: str = FlextCliConstants.CommandsDefaults.DEFAULT_DESCRIPTION,
        **data: FlextTypes.JsonValue,
    ) -> None:
        """Initialize CLI commands manager with Phase 1 context enrichment."""
        super().__init__(**data)
        # Logger is automatically provided by FlextMixins mixin
        self._name = name
        self._description = description
        # Commands store handler callables, use dict[str, dict[str, object]]
        self._commands: dict[str, dict[str, object]] = {}
        # Type hint for empty dict to match _CliGroup signature
        empty_commands: dict[str, dict[str, object]] = {}
        self._cli_group = self._CliGroup(
            name=name,
            description=description,
            commands=empty_commands,
        )

    def execute(self, **_kwargs: object) -> FlextResult[FlextTypes.JsonDict]:
        """Execute the main domain service operation - required by FlextService.

        Args:
            **_kwargs: Additional execution parameters (unused, for FlextService compatibility)

        """
        return FlextResult[FlextTypes.JsonDict].ok({
            FlextCliConstants.CommandsDictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.CommandsDictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
            FlextCliConstants.CommandsDictKeys.COMMANDS: list(self._commands.keys()),
        })

    def register_command(
        self,
        name: str,
        handler: Callable[[], FlextTypes.JsonValue]
        | Callable[[list[str]], FlextTypes.JsonValue],
        description: str = FlextCliConstants.CommandsDefaults.DEFAULT_DESCRIPTION,
    ) -> FlextResult[bool]:
        """Register a command.

        Args:
            name: Command name
            handler: Command handler function
            description: Command description

        Returns:
            FlextResult[bool]: True if registered successfully, or error

        """
        try:
            self._commands[name] = {
                FlextCliConstants.CommandsDictKeys.NAME: name,
                FlextCliConstants.CommandsDictKeys.HANDLER: handler,
                FlextCliConstants.CommandsDictKeys.DESCRIPTION: description,
            }
            self._cli_group.commands[name] = self._commands[name]
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.COMMAND_REGISTRATION_FAILED.format(
                    error=e
                )
            )

    def unregister_command(self, name: str) -> FlextResult[bool]:
        """Unregister a command.

        Args:
            name: Command name

        Returns:
            FlextResult[bool]: True if unregistered successfully, False if not found, or error

        """
        try:
            if name in self._commands:
                del self._commands[name]
                if name in self._cli_group.commands:
                    del self._cli_group.commands[name]
                return FlextResult[bool].ok(True)
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(name=name)
            )
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.COMMAND_UNREGISTRATION_FAILED.format(
                    error=e
                )
            )

    def create_command_group(
        self,
        name: str,
        description: str = "",
        commands: dict[str, dict[str, object]] | None = None,
    ) -> FlextResult[object]:
        """Create a command group.

        Args:
            name: Group name
            description: Group description
            commands: Dictionary of command names and handler objects in group

        Returns:
            FlextResult[object]: Group object or error

        """
        try:
            # Fast-fail if commands is None - no fallback
            if commands is None:
                return FlextResult[object].fail(
                    FlextCliConstants.ErrorMessages.COMMANDS_REQUIRED
                )
            validated_commands: dict[str, dict[str, object]] = commands
            group = self._CliGroup(
                name=name,
                description=description,
                commands=validated_commands,
            )
            return FlextResult[object].ok(group)
        except Exception as e:
            return FlextResult[object].fail(
                FlextCliConstants.ErrorMessages.GROUP_CREATION_FAILED.format(error=e)
            )

    def _validate_cli_args(self, args: list[str] | None) -> FlextResult[bool]:
        """Validate CLI arguments.

        Args:
            args: Command line arguments to validate

        Returns:
            FlextResult[bool]: True if all args are valid, or error

        """
        if not args:
            return FlextResult[bool].ok(True)

        for arg in args:
            if arg.startswith(FlextCliConstants.CommandsDefaults.OPTION_PREFIX):
                continue  # Skip options
            if arg not in self._commands:
                return FlextResult[bool].fail(
                    FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(name=arg)
                )

        return FlextResult[bool].ok(True)

    def run_cli(
        self,
        args: list[str] | None = None,
        *,
        standalone_mode: bool = True,
    ) -> FlextResult[bool]:
        """Run the CLI interface.

        Args:
            args: Command line arguments
            standalone_mode: Whether to run in standalone mode

        Returns:
            FlextResult[bool]: True if executed successfully, or error

        """
        try:
            # Validate arguments
            validation_result = self._validate_cli_args(args)
            if validation_result.is_failure:
                return validation_result

            # Log CLI execution mode for debugging
            self.logger.debug(
                FlextCliConstants.CommandsLogMessages.CLI_EXECUTION_MODE.format(
                    standalone_mode=standalone_mode, args=args
                )
            )

            # For now, just execute the service
            result = self.execute()
            if result.is_success:
                return FlextResult[bool].ok(True)
            # Fast-fail: error is always present in failure case
            return FlextResult[bool].fail(result.error or "Unknown error")
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e)
            )

    def get_click_group(self) -> FlextCliCommands._CliGroup:
        """Get the Click group object.

        Returns:
            Click group object

        """
        return self._cli_group

    def _execute_handler(
        self, handler: Callable[..., object], args: list[str] | None
    ) -> object:
        """Execute command handler with appropriate arguments.

        Args:
            handler: Handler callable to execute
            args: Optional command arguments

        Returns:
            Handler execution result

        """
        if args:
            try:
                return handler(args)
            except TypeError:
                # Handler doesn't accept args, call without them
                return handler()
        return handler()

    def execute_command(
        self,
        command_name: str,
        args: list[str] | None = None,
        timeout: int = FlextCliConstants.TIMEOUTS.DEFAULT,
    ) -> FlextResult[FlextTypes.JsonValue]:
        """Execute a specific command.

        Args:
            command_name: Name of the command to execute
            args: Command arguments
            timeout: Command timeout in seconds

        Returns:
            FlextResult[FlextTypes.JsonValue]: Command result

        """
        try:
            # Log timeout parameter for future use
            self.logger.debug(
                FlextCliConstants.CommandsLogMessages.EXECUTING_COMMAND.format(
                    command_name=command_name, timeout=timeout
                )
            )

            if command_name not in self._commands:
                return FlextResult[FlextTypes.JsonValue].fail(
                    FlextCliConstants.CommandsErrorMessages.COMMAND_NOT_FOUND_DETAIL.format(
                        command_name=command_name
                    )
                )

            command_info = self._commands[command_name]
            if not (
                isinstance(command_info, dict)
                and FlextCliConstants.CommandsDictKeys.HANDLER in command_info
            ):
                return FlextResult[FlextTypes.JsonValue].fail(
                    FlextCliConstants.CommandsErrorMessages.INVALID_COMMAND_STRUCTURE.format(
                        command_name=command_name
                    )
                )

            # Handler is guaranteed to exist from previous validation
            handler = command_info[FlextCliConstants.CommandsDictKeys.HANDLER]
            if not callable(handler):
                return FlextResult[FlextTypes.JsonValue].fail(
                    FlextCliConstants.CommandsErrorMessages.HANDLER_NOT_CALLABLE.format(
                        command_name=command_name
                    )
                )

            result = self._execute_handler(handler, args)
            # Result from handler should be JsonValue compatible
            # Validate type at runtime if needed, but avoid unnecessary cast
            if not isinstance(result, (str, int, float, bool, list, dict, type(None))):
                return FlextResult[FlextTypes.JsonValue].fail(
                    f"Handler returned invalid type: {type(result).__name__}"
                )

            return FlextResult[FlextTypes.JsonValue].ok(result)
        except Exception as e:
            return FlextResult[FlextTypes.JsonValue].fail(
                FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(error=e)
            )

    def get_commands(self) -> dict[str, dict[str, object]]:
        """Get all registered commands.

        Returns:
            dict[str, dict[str, object]]: Dictionary of registered commands

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
            return FlextResult[int].fail(
                FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(error=e)
            )

    def list_commands(self) -> FlextResult[list[str]]:
        """List all registered commands.

        Returns:
            FlextResult[list[str]]: List of command names

        """
        try:
            command_names = list(self._commands.keys())
            return FlextResult[list[str]].ok(command_names)
        except Exception as e:
            return FlextResult[list[str]].fail(
                FlextCliConstants.CommandsErrorMessages.FAILED_LIST_COMMANDS.format(
                    error=e
                )
            )

    def create_main_cli(self) -> FlextCliCommands:
        """Create the main CLI instance.

        Returns:
            FlextCliCommands: Main CLI instance

        """
        return FlextCliCommands(name=self._name, description=self._description)


__all__ = ["FlextCliCommands"]
