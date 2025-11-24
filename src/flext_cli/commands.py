"""FLEXT CLI Commands - Single unified class following FLEXT standards.

Command creation and management using flext-core patterns.
Single FlextCliCommands class with nested helpers following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable
from typing import override

from flext_core import FlextResult, FlextRuntime, FlextTypes

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants


class FlextCliCommands(FlextCliServiceBase):
    """Single unified CLI commands class following FLEXT standards.

    Provides CLI command registration and management using flext-core patterns.
    Follows FLEXT pattern: one class per module with nested helpers.
    """

    # Logger is provided by FlextMixins mixin

    class _CliGroup:
        """Nested helper for CLI group operations."""

        def __init__(
            self,
            name: str,
            description: str,
            commands: dict[str, dict[str, object]],
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

        self.logger.debug(
            "Initialized CLI commands manager",
            operation="__init__",
            cli_name=name,
            description=description,
            commands_count=0,
            source="flext-cli/src/flext_cli/commands.py",
        )

    def execute(self, **_kwargs: object) -> FlextResult[FlextTypes.JsonDict]:
        """Execute the main domain service operation - required by FlextService.

        Args:
            **_kwargs: Additional execution parameters (unused, for FlextService compatibility)

        """
        self.logger.info(
            "Executing CLI commands service",
            operation="execute",
            commands_count=len(self._commands),
            cli_name=self._name,
            source="flext-cli/src/flext_cli/commands.py",
        )

        self.logger.debug(
            "Building service status response",
            operation="execute",
            registered_commands=list(self._commands.keys()),
            source="flext-cli/src/flext_cli/commands.py",
        )

        result = FlextResult[FlextTypes.JsonDict].ok({
            FlextCliConstants.CommandsDictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.CommandsDictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
            FlextCliConstants.CommandsDictKeys.COMMANDS: list(self._commands.keys()),
        })

        self.logger.debug(
            "Service execution completed successfully",
            operation="execute",
            result_status="operational",
            source="flext-cli/src/flext_cli/commands.py",
        )

        return result

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
        self.logger.debug(
            "Registering CLI command",
            operation="register_command",
            command_name=name,
            description=description,
            handler_type=type(handler).__name__,
            source="flext-cli/src/flext_cli/commands.py",
        )

        try:
            self._commands[name] = {
                FlextCliConstants.CommandsDictKeys.NAME: name,
                FlextCliConstants.CommandsDictKeys.HANDLER: handler,
                FlextCliConstants.CommandsDictKeys.DESCRIPTION: description,
            }
            self._cli_group.commands[name] = self._commands[name]

            self.logger.debug(
                "Command registered successfully",
                operation="register_command",
                command_name=name,
                total_commands=len(self._commands),
                source="flext-cli/src/flext_cli/commands.py",
            )

            return FlextResult[bool].ok(True)
        except Exception as e:  # pragma: no cover
            self.logger.exception(  # pragma: no cover
                "FAILED to register command - registration aborted",  # pragma: no cover
                operation="register_command",  # pragma: no cover
                command_name=name,  # pragma: no cover
                error=str(e),  # pragma: no cover
                error_type=type(e).__name__,  # pragma: no cover
                consequence="Command will not be available for execution",  # pragma: no cover
                source="flext-cli/src/flext_cli/commands.py",  # pragma: no cover
            )  # pragma: no cover
            return FlextResult[bool].fail(  # pragma: no cover
                FlextCliConstants.ErrorMessages.COMMAND_REGISTRATION_FAILED.format(
                    error=e,
                ),
            )

    def unregister_command(self, name: str) -> FlextResult[bool]:
        """Unregister a command.

        Args:
            name: Command name

        Returns:
            FlextResult[bool]: True if unregistered successfully, False if not found, or error

        """
        self.logger.debug(
            "Unregistering CLI command",
            operation="unregister_command",
            command_name=name,
            current_commands_count=len(self._commands),
            source="flext-cli/src/flext_cli/commands.py",
        )

        try:
            if name in self._commands:
                del self._commands[name]
                if name in self._cli_group.commands:
                    del self._cli_group.commands[name]

                self.logger.debug(
                    "Command unregistered successfully",
                    operation="unregister_command",
                    command_name=name,
                    remaining_commands=len(self._commands),
                    source="flext-cli/src/flext_cli/commands.py",
                )

                return FlextResult[bool].ok(True)

            self.logger.warning(
                "Command not found for unregistration",
                operation="unregister_command",
                command_name=name,
                available_commands=list(self._commands.keys()),
                source="flext-cli/src/flext_cli/commands.py",
            )

            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(name=name),
            )
        except Exception as e:  # pragma: no cover
            self.logger.exception(  # pragma: no cover
                "FAILED to unregister command - unregistration aborted",  # pragma: no cover
                operation="unregister_command",  # pragma: no cover
                command_name=name,  # pragma: no cover
                error=str(e),  # pragma: no cover
                error_type=type(e).__name__,  # pragma: no cover
                consequence="Command may still be registered",  # pragma: no cover
                source="flext-cli/src/flext_cli/commands.py",  # pragma: no cover
            )  # pragma: no cover
            return FlextResult[bool].fail(  # pragma: no cover
                FlextCliConstants.ErrorMessages.COMMAND_UNREGISTRATION_FAILED.format(
                    error=e,
                ),
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
        self.logger.debug(
            "Creating command group",
            operation="create_command_group",
            group_name=name,
            description=description,
            commands_provided=commands is not None,
            commands_count=len(commands) if commands else 0,
            source="flext-cli/src/flext_cli/commands.py",
        )

        try:
            # Fast-fail if commands is None - no fallback
            if commands is None:
                self.logger.warning(
                    "Command group creation failed - commands parameter is required",
                    operation="create_command_group",
                    group_name=name,
                    consequence="Group creation aborted",
                    source="flext-cli/src/flext_cli/commands.py",
                )
                return FlextResult[object].fail(
                    FlextCliConstants.ErrorMessages.COMMANDS_REQUIRED,
                )
            validated_commands: dict[str, dict[str, object]] = commands
            group = self._CliGroup(
                name=name,
                description=description,
                commands=validated_commands,
            )

            self.logger.debug(
                "Command group created successfully",
                operation="create_command_group",
                group_name=name,
                commands_count=len(validated_commands),
                source="flext-cli/src/flext_cli/commands.py",
            )

            return FlextResult[object].ok(group)
        except Exception as e:  # pragma: no cover
            self.logger.exception(  # pragma: no cover
                "FAILED to create command group - group creation aborted",  # pragma: no cover
                operation="create_command_group",  # pragma: no cover
                group_name=name,  # pragma: no cover
                error=str(e),  # pragma: no cover
                error_type=type(e).__name__,  # pragma: no cover
                consequence="Group will not be available",  # pragma: no cover
                source="flext-cli/src/flext_cli/commands.py",  # pragma: no cover
            )  # pragma: no cover
            return FlextResult[object].fail(  # pragma: no cover
                FlextCliConstants.ErrorMessages.GROUP_CREATION_FAILED.format(error=e),
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
                    FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(name=arg),
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
        self.logger.info(
            "Running CLI interface",
            operation="run_cli",
            standalone_mode=standalone_mode,
            args_count=len(args) if args else 0,
            args=args,
            source="flext-cli/src/flext_cli/commands.py",
        )

        try:
            # Validate arguments
            self.logger.debug(
                "Validating CLI arguments",
                operation="run_cli",
                args=args,
                source="flext-cli/src/flext_cli/commands.py",
            )

            validation_result = self._validate_cli_args(args)
            if validation_result.is_failure:
                self.logger.warning(
                    "CLI argument validation failed",
                    operation="run_cli",
                    args=args,
                    error=validation_result.error,
                    consequence="CLI execution aborted",
                    source="flext-cli/src/flext_cli/commands.py",
                )
                return validation_result

            # Log CLI execution mode for debugging
            self.logger.debug(
                "CLI execution mode",
                operation="run_cli",
                standalone_mode=standalone_mode,
                args=args,
                source="flext-cli/src/flext_cli/commands.py",
            )

            # For now, just execute the service
            result = self.execute()
            if result.is_success:
                self.logger.info(
                    "CLI execution completed successfully",
                    operation="run_cli",
                    standalone_mode=standalone_mode,
                    source="flext-cli/src/flext_cli/commands.py",
                )
                return FlextResult[bool].ok(True)

            # Fast-fail: error is always present in failure case
            self.logger.error(  # pragma: no cover
                "CLI execution failed",  # pragma: no cover
                operation="run_cli",  # pragma: no cover
                error=result.error or "Unknown error",  # pragma: no cover
                consequence="CLI execution aborted",  # pragma: no cover
                source="flext-cli/src/flext_cli/commands.py",  # pragma: no cover
            )  # pragma: no cover
            return FlextResult[bool].fail(result.error or "Unknown error")  # pragma: no cover
        except Exception as e:  # pragma: no cover
            self.logger.exception(  # pragma: no cover
                "FATAL ERROR during CLI execution - execution aborted",  # pragma: no cover
                operation="run_cli",  # pragma: no cover
                error=str(e),  # pragma: no cover
                error_type=type(e).__name__,  # pragma: no cover
                consequence="CLI execution failed completely",  # pragma: no cover
                severity="critical",  # pragma: no cover
                source="flext-cli/src/flext_cli/commands.py",  # pragma: no cover
            )  # pragma: no cover
            return FlextResult[bool].fail(  # pragma: no cover
                FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e),
            )

    def get_click_group(self) -> FlextCliCommands._CliGroup:
        """Get the Click group object.

        Returns:
            Click group object

        """
        return self._cli_group

    def _execute_handler(
        self,
        handler: Callable[..., object],
        args: list[str] | None,
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
        self.logger.info(
            "Executing CLI command",
            operation="execute_command",
            command_name=command_name,
            timeout=timeout,
            args_count=len(args) if args else 0,
            source="flext-cli/src/flext_cli/commands.py",
        )

        self.logger.debug(
            "Starting command execution",
            operation="execute_command",
            command_name=command_name,
            args=args,
            timeout=timeout,
            available_commands=list(self._commands.keys()),
            source="flext-cli/src/flext_cli/commands.py",
        )

        try:
            if command_name not in self._commands:
                self.logger.error(
                    "FAILED to execute command - command not found",
                    operation="execute_command",
                    command_name=command_name,
                    available_commands=list(self._commands.keys()),
                    consequence="Command execution aborted",
                    source="flext-cli/src/flext_cli/commands.py",
                )
                return FlextResult[FlextTypes.JsonValue].fail(
                    FlextCliConstants.CommandsErrorMessages.COMMAND_NOT_FOUND_DETAIL.format(
                        command_name=command_name,
                    ),
                )

            command_info = self._commands[command_name]
            self.logger.debug(
                "Retrieved command information",
                operation="execute_command",
                command_name=command_name,
                has_handler=FlextCliConstants.CommandsDictKeys.HANDLER in command_info,
                source="flext-cli/src/flext_cli/commands.py",
            )

            if not (
                FlextRuntime.is_dict_like(command_info)
                and FlextCliConstants.CommandsDictKeys.HANDLER in command_info
            ):
                self.logger.error(
                    "FAILED to execute command - invalid command structure",
                    operation="execute_command",
                    command_name=command_name,
                    command_info_keys=list(command_info.keys())
                    if FlextRuntime.is_dict_like(command_info)
                    else None,
                    consequence="Command execution aborted",
                    source="flext-cli/src/flext_cli/commands.py",
                )
                return FlextResult[FlextTypes.JsonValue].fail(
                    FlextCliConstants.CommandsErrorMessages.INVALID_COMMAND_STRUCTURE.format(
                        command_name=command_name,
                    ),
                )

            # Handler is guaranteed to exist from previous validation
            handler = command_info[FlextCliConstants.CommandsDictKeys.HANDLER]
            if not callable(handler):
                self.logger.error(
                    "FAILED to execute command - handler is not callable",
                    operation="execute_command",
                    command_name=command_name,
                    handler_type=type(handler).__name__,
                    consequence="Command execution aborted",
                    source="flext-cli/src/flext_cli/commands.py",
                )
                return FlextResult[FlextTypes.JsonValue].fail(
                    FlextCliConstants.CommandsErrorMessages.HANDLER_NOT_CALLABLE.format(
                        command_name=command_name,
                    ),
                )

            self.logger.debug(
                "Executing command handler",
                operation="execute_command",
                command_name=command_name,
                handler_type=type(handler).__name__,
                args_provided=args is not None,
                source="flext-cli/src/flext_cli/commands.py",
            )

            result = self._execute_handler(handler, args)

            # Result from handler should be JsonValue compatible
            # Validate type at runtime if needed, but avoid unnecessary cast
            if not (
                isinstance(result, (str, int, float, bool, type(None)))
                or FlextRuntime.is_list_like(result)
                or FlextRuntime.is_dict_like(result)
            ):
                self.logger.error(
                    "FAILED to execute command - handler returned invalid type",
                    operation="execute_command",
                    command_name=command_name,
                    result_type=type(result).__name__,
                    consequence="Command execution aborted",
                    source="flext-cli/src/flext_cli/commands.py",
                )
                return FlextResult[FlextTypes.JsonValue].fail(
                    f"Handler returned invalid type: {type(result).__name__}",
                )

            self.logger.debug(
                "Command executed successfully",
                operation="execute_command",
                command_name=command_name,
                result_type=type(result).__name__,
                source="flext-cli/src/flext_cli/commands.py",
            )

            self.logger.info(
                "Command execution completed",
                operation="execute_command",
                command_name=command_name,
                success=True,
                source="flext-cli/src/flext_cli/commands.py",
            )

            return FlextResult[FlextTypes.JsonValue].ok(result)
        except Exception as e:
            self.logger.exception(
                "FATAL ERROR during command execution - execution aborted",
                operation="execute_command",
                command_name=command_name,
                error=str(e),
                error_type=type(e).__name__,
                consequence="Command execution failed completely",
                severity="critical",
                source="flext-cli/src/flext_cli/commands.py",
            )
            return FlextResult[FlextTypes.JsonValue].fail(
                FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(
                    error=e,
                ),
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
        self.logger.debug(
            "Clearing all registered commands",
            operation="clear_commands",
            current_commands_count=len(self._commands),
            source="flext-cli/src/flext_cli/commands.py",
        )

        try:
            count = len(self._commands)
            self._commands.clear()
            self._cli_group.commands.clear()

            self.logger.debug(
                "All commands cleared successfully",
                operation="clear_commands",
                cleared_count=count,
                source="flext-cli/src/flext_cli/commands.py",
            )

            return FlextResult[int].ok(count)
        except Exception as e:  # pragma: no cover
            self.logger.exception(  # pragma: no cover
                "FAILED to clear commands - operation aborted",  # pragma: no cover
                operation="clear_commands",  # pragma: no cover
                error=str(e),  # pragma: no cover
                error_type=type(e).__name__,  # pragma: no cover
                consequence="Commands may still be registered",  # pragma: no cover
                source="flext-cli/src/flext_cli/commands.py",  # pragma: no cover
            )  # pragma: no cover
            return FlextResult[int].fail(  # pragma: no cover
                FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def list_commands(self) -> FlextResult[list[str]]:
        """List all registered commands.

        Returns:
            FlextResult[list[str]]: List of command names

        """
        self.logger.debug(
            "Listing all registered commands",
            operation="list_commands",
            current_commands_count=len(self._commands),
            source="flext-cli/src/flext_cli/commands.py",
        )

        try:
            command_names = list(self._commands.keys())

            self.logger.debug(
                "Commands listed successfully",
                operation="list_commands",
                commands_count=len(command_names),
                command_names=command_names,
                source="flext-cli/src/flext_cli/commands.py",
            )

            return FlextResult[list[str]].ok(command_names)
        except Exception as e:  # pragma: no cover
            self.logger.exception(  # pragma: no cover
                "FAILED to list commands - operation aborted",  # pragma: no cover
                operation="list_commands",  # pragma: no cover
                error=str(e),  # pragma: no cover
                error_type=type(e).__name__,  # pragma: no cover
                consequence="Command list unavailable",  # pragma: no cover
                source="flext-cli/src/flext_cli/commands.py",  # pragma: no cover
            )  # pragma: no cover
            return FlextResult[list[str]].fail(  # pragma: no cover
                FlextCliConstants.CommandsErrorMessages.FAILED_LIST_COMMANDS.format(
                    error=e,
                ),
            )

    def create_main_cli(self) -> FlextCliCommands:
        """Create the main CLI instance.

        Returns:
            FlextCliCommands: Main CLI instance

        """
        return FlextCliCommands(name=self._name, description=self._description)


__all__ = ["FlextCliCommands"]
