"""FLEXT CLI Commands - Single unified class following FLEXT standards.

Command creation and management using flext-core patterns.
Single FlextCliCommands class with nested helpers following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TypeVar, cast, override

from flext_core import (
    FlextConstants,
    FlextDecorators,
    FlextExceptions,
    FlextHandlers,
    FlextMixins,
    FlextModels,
    FlextProtocols,
    FlextResult,
    FlextRuntime,
    FlextService,
    t,
    u,
)
from pydantic import PrivateAttr

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.protocols import FlextCliProtocols

# Aliases for static method calls and type references
# Use u.* for FlextUtilities static methods
# Use t.* for FlextTypes type references
# Use c.* for FlextConstants constants
# Use m.* for FlextModels model references
# Use p.* for FlextProtocols protocol references
# Use r.* for FlextResult methods
# Use e.* for FlextExceptions
# Use d.* for FlextDecorators decorators
# Use s.* for FlextService service base
# Use x.* for FlextMixins mixins
# Use h.* for FlextHandlers handlers
# u is already imported from flext_core
# t is already imported from flext_core
c = FlextConstants
m = FlextModels
p = FlextProtocols
r = FlextResult
e = FlextExceptions
d = FlextDecorators
s = FlextService
x = FlextMixins
h = FlextHandlers

T = TypeVar("T")


class FlextCliCommands(FlextCliServiceBase):
    """Single unified CLI commands class following FLEXT standards.

    Business Rules:
    ───────────────
    1. Command names MUST be unique within a CLI group
    2. Command handlers MUST be callable and return r[T]
    3. Command registration MUST validate handler protocol compliance
    4. Commands MUST be registered before execution
    5. Command execution MUST handle exceptions gracefully
    6. Command metadata (name, description) MUST be immutable after registration
    7. CLI groups MUST support nested command organization
    8. All operations MUST use r[T] for error handling

    Architecture Implications:
    ───────────────────────────
    - Extends FlextCliServiceBase for consistent logging and container access
    - Uses PrivateAttr for mutable command registry (frozen model compatibility)
    - Command handlers stored as Protocol-compatible callables
    - CLI groups enable hierarchical command organization
    - Railway-Oriented Programming via FlextResult for composable error handling

    Audit Implications:
    ───────────────────
    - Command registrations MUST be logged with command name and handler info
    - Command executions MUST be logged with arguments (no sensitive data)
    - Command failures MUST be logged with full context (no sensitive data)
    - Command metadata changes MUST be logged for audit trail
    - Handler protocol violations MUST be logged for debugging

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
            commands: dict[
                str,
                dict[
                    str,
                    t.GeneralValueType | FlextCliProtocols.Cli.CliCommandHandler,
                ],
            ],
        ) -> None:
            """Initialize CLI group."""
            self.name = name
            self.description = description
            self.commands = commands

    # Private attributes for frozen model - use PrivateAttr for mutability
    _name: str = PrivateAttr()
    _description: str = PrivateAttr()
    _commands: dict[
        str,
        dict[str, t.GeneralValueType | FlextCliProtocols.Cli.CliCommandHandler],
    ] = PrivateAttr(default_factory=dict)
    _cli_group: _CliGroup = PrivateAttr()

    @override
    def __init__(
        self,
        name: str = FlextCliConstants.CommandsDefaults.DEFAULT_CLI_NAME,
        description: str = FlextCliConstants.CommandsDefaults.DEFAULT_DESCRIPTION,
        **data: t.GeneralValueType,
    ) -> None:
        """Initialize CLI commands manager with Phase 1 context enrichment."""
        super().__init__(**data)
        # Logger is automatically provided by FlextMixins mixin
        # Use object.__setattr__ for frozen model private attributes
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_description", description)
        # Commands store handler callables - use dict[str, dict] for mutability
        # Handler is CliCommandHandler Protocol, but name/description are GeneralValueType (str)
        empty_commands: dict[
            str,
            dict[
                str,
                t.GeneralValueType | FlextCliProtocols.Cli.CliCommandHandler,
            ],
        ] = {}
        object.__setattr__(
            self,
            "_cli_group",
            self._CliGroup(
                name=name,
                description=description,
                commands=empty_commands,
            ),
        )

        self.logger.debug(
            "Initialized CLI commands manager",
            operation="__init__",
            cli_name=name,
            description=description,
            commands_count=0,
            source="flext-cli/src/flext_cli/commands.py",
        )

    def execute(self, **_kwargs: t.JsonDict) -> r[t.JsonDict]:
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

        result = r[t.JsonDict].ok({
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
        handler: FlextCliProtocols.Cli.CliCommandHandler,
        description: str = FlextCliConstants.CommandsDefaults.DEFAULT_DESCRIPTION,
    ) -> r[bool]:
        """Register a command.

        Args:
            name: Command name
            handler: Command handler function
            description: Command description

        Returns:
            r[bool]: True if registered successfully, or error

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
            # Store command metadata - handler is CliCommandFunction Protocol
            # Use type ignore for Protocol in dict (structural typing allows this)
            command_metadata: dict[
                str,
                t.GeneralValueType | FlextCliProtocols.Cli.CliCommandHandler,
            ] = {
                FlextCliConstants.CommandsDictKeys.NAME: name,
                FlextCliConstants.CommandsDictKeys.HANDLER: handler,
                FlextCliConstants.CommandsDictKeys.DESCRIPTION: description,
            }
            self._commands[name] = command_metadata
            # Update CLI group commands - copy dict for type compatibility
            updated_commands: dict[
                str,
                dict[
                    str,
                    t.GeneralValueType | FlextCliProtocols.Cli.CliCommandHandler,
                ],
            ] = dict(self._commands)
            self._cli_group.commands = updated_commands

            self.logger.debug(
                "Command registered successfully",
                operation="register_command",
                command_name=name,
                total_commands=len(self._commands),
                source="flext-cli/src/flext_cli/commands.py",
            )

            return r[bool].ok(True)
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
            return r[bool].fail(  # pragma: no cover
                FlextCliConstants.ErrorMessages.COMMAND_REGISTRATION_FAILED.format(
                    error=e,
                ),
            )

    def unregister_command(self, name: str) -> r[bool]:
        """Unregister a command.

        Args:
            name: Command name

        Returns:
            r[bool]: True if unregistered successfully, False if not found, or error

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

                return r[bool].ok(True)

            self.logger.warning(
                "Command not found for unregistration",
                operation="unregister_command",
                command_name=name,
                available_commands=list(self._commands.keys()),
                source="flext-cli/src/flext_cli/commands.py",
            )

            return r[bool].fail(
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
            return r[bool].fail(  # pragma: no cover
                FlextCliConstants.ErrorMessages.COMMAND_UNREGISTRATION_FAILED.format(
                    error=e,
                ),
            )

    def create_command_group(
        self,
        name: str,
        description: str = "",
        commands: dict[
            str,
            dict[
                str,
                t.GeneralValueType | FlextCliProtocols.Cli.CliCommandHandler,
            ],
        ]
        | None = None,
    ) -> r[FlextCliCommands._CliGroup]:
        """Create a command group.

        Args:
            name: Group name
            description: Group description
            commands: Dictionary of command names and handler objects in group

        Returns:
            r[_CliGroup]: Group object or error

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
                return r[FlextCliCommands._CliGroup].fail(
                    FlextCliConstants.ErrorMessages.COMMANDS_REQUIRED,
                )
            validated_commands: dict[
                str,
                dict[
                    str,
                    t.GeneralValueType | FlextCliProtocols.Cli.CliCommandHandler,
                ],
            ] = commands
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

            return r[FlextCliCommands._CliGroup].ok(group)
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
            return r[FlextCliCommands._CliGroup].fail(  # pragma: no cover
                FlextCliConstants.ErrorMessages.GROUP_CREATION_FAILED.format(error=e),
            )

    def _validate_cli_args(self, args: list[str] | None) -> r[bool]:
        """Validate CLI arguments.

        Args:
            args: Command line arguments to validate

        Returns:
            r[bool]: True if all args are valid, or error

        """
        if not args:
            return r[bool].ok(True)

        for arg in args:
            if arg.startswith(FlextCliConstants.CommandsDefaults.OPTION_PREFIX):
                continue  # Skip options
            if arg not in self._commands:
                return r[bool].fail(
                    FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(name=arg),
                )

        return r[bool].ok(True)

    def run_cli(
        self,
        args: list[str] | None = None,
        *,
        standalone_mode: bool = True,
    ) -> r[bool]:
        """Run the CLI interface.

        Args:
            args: Command line arguments
            standalone_mode: Whether to run in standalone mode

        Returns:
            r[bool]: True if executed successfully, or error

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
                return r[bool].ok(True)

            # Fast-fail: error is always present in failure case
            self.logger.error(  # pragma: no cover
                "CLI execution failed",  # pragma: no cover
                operation="run_cli",  # pragma: no cover
                error=result.error or "Unknown error",  # pragma: no cover
                consequence="CLI execution aborted",  # pragma: no cover
                source="flext-cli/src/flext_cli/commands.py",  # pragma: no cover
            )  # pragma: no cover
            return r[bool].fail(
                result.error or "Unknown error"
            )  # pragma: no cover
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
            return r[bool].fail(  # pragma: no cover
                FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e),
            )

    def get_click_group(self) -> FlextCliCommands._CliGroup:
        """Get the Click group object.

        Returns:
            Click group object

        """
        return self._cli_group

    @staticmethod
    def _execute_handler(
        handler: FlextCliProtocols.Cli.CliCommandHandler,
        args: list[str] | None,
    ) -> t.GeneralValueType:
        """Execute command handler with appropriate arguments.

        Args:
            handler: Handler Protocol to execute
            args: Optional command arguments

        Returns:
            Handler execution result as GeneralValueType

        Note:
            Handlers can have different signatures:
            - No args: `lambda: result`
            - Single list arg: `def handler(args: list[str]) -> str`
            - Unpacked args: `def handler(*args: str) -> str`
            This method tries to call handlers appropriately.

        """
        # CliCommandHandler Protocol has __call__ method
        # Try calling with args as single argument first (for handlers like cmd_with_args(args: list[str]))
        # Then fallback to unpacked args or no args
        if args:
            try:
                # Try calling with args as single argument (for handlers expecting list[str])
                result: object = handler(args)
            except TypeError:
                # Handler doesn't accept single list argument, try unpacking
                try:
                    result = handler(*args)
                except TypeError:
                    # Handler doesn't accept unpacked args either, try without args
                    result = handler()
        else:
            # No args provided, call handler without arguments
            result = handler()
        # Convert result to GeneralValueType
        # GeneralValueType = ScalarValue | Sequence[GeneralValueType] | Mapping[str, GeneralValueType]
        # ScalarValue = str | int | float | bool | datetime | None
        # Type narrowing: result is object, narrow to GeneralValueType
        if isinstance(result, (str, int, float, bool, type(None))):
            # ScalarValue is part of GeneralValueType
            return result
        if isinstance(result, dict):
            # dict[str, GeneralValueType] is compatible with Mapping[str, GeneralValueType]
            return result
        if isinstance(result, list):
            # list[GeneralValueType] is compatible with Sequence[GeneralValueType]
            return result
        # Fallback: convert to string (ScalarValue)
        return str(result)

    def execute_command(
        self,
        command_name: str,
        args: list[str] | None = None,
        timeout: int = FlextCliConstants.TIMEOUTS.DEFAULT,
    ) -> r[t.GeneralValueType]:
        """Execute a specific command.

        Args:
            command_name: Name of the command to execute
            args: Command arguments
            timeout: Command timeout in seconds

        Returns:
            r[t.GeneralValueType]: Command result

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
                return r[t.GeneralValueType].fail(
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

            # Type narrowing: command_info is dict, convert to GeneralValueType for is_dict_like
            # Use cast to satisfy type checker - command_info is dict[str, GeneralValueType | CliCommandHandler]
            command_info_as_general: t.GeneralValueType = cast(
                "t.GeneralValueType", command_info
            )
            if not (
                FlextRuntime.is_dict_like(command_info_as_general)
                and FlextCliConstants.CommandsDictKeys.HANDLER in command_info
            ):
                self.logger.error(
                    "FAILED to execute command - invalid command structure",
                    operation="execute_command",
                    command_name=command_name,
                    command_info_keys=list(command_info.keys())
                    if isinstance(command_info, dict)
                    else None,
                    consequence="Command execution aborted",
                    source="flext-cli/src/flext_cli/commands.py",
                )
                return r[t.GeneralValueType].fail(
                    FlextCliConstants.CommandsErrorMessages.INVALID_COMMAND_STRUCTURE.format(
                        command_name=command_name,
                    ),
                )

            # Handler is guaranteed to exist from previous validation
            # Structural typing: handler conforms to CliCommandHandler Protocol
            # Type narrowing: handler_value is GeneralValueType | CliCommandHandler
            # Runtime check ensures it's callable (CliCommandHandler)
            handler_value: (
                t.GeneralValueType | FlextCliProtocols.Cli.CliCommandHandler
            ) = command_info[FlextCliConstants.CommandsDictKeys.HANDLER]
            # Runtime check: ensure handler is callable (CliCommandHandler Protocol)
            if not isinstance(handler_value, FlextCliProtocols.Cli.CliCommandHandler):
                # This should never happen if register_command was used correctly
                # But defensive check for type safety - handler is not callable
                self.logger.error(
                    "FAILED to execute command - handler is not callable",
                    operation="execute_command",
                    command_name=command_name,
                    handler_type=type(handler_value).__name__,
                    consequence="Command execution aborted",
                    source="flext-cli/src/flext_cli/commands.py",
                )
                return r[t.GeneralValueType].fail(
                    FlextCliConstants.CommandsErrorMessages.HANDLER_NOT_CALLABLE.format(
                        command_name=command_name,
                    ),
                )
            handler: FlextCliProtocols.Cli.CliCommandHandler = handler_value

            self.logger.debug(
                "Executing command handler",
                operation="execute_command",
                command_name=command_name,
                handler_type=type(handler).__name__,
                args_provided=args is not None,
                source="flext-cli/src/flext_cli/commands.py",
            )

            result = FlextCliCommands._execute_handler(handler, args)

            # Result from handler is already GeneralValueType compatible from _execute_handler
            # _execute_handler guarantees GeneralValueType return
            self.logger.info(
                "Command execution completed",
                operation="execute_command",
                command_name=command_name,
                success=True,
                source="flext-cli/src/flext_cli/commands.py",
            )

            return r[t.GeneralValueType].ok(result)
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
            return r[t.GeneralValueType].fail(
                FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def get_commands(
        self,
    ) -> dict[
        str,
        Mapping[str, t.GeneralValueType | FlextCliProtocols.Cli.CliCommandHandler],
    ]:
        """Get all registered commands.

        Returns:
            dict[str, CliCommandMetadata]: Dictionary of registered commands

        """

        # Return copy of commands dict - convert dict to Mapping for return type
        # _commands is typed as dict[str, dict[...]], so v is guaranteed to be dict
        # Use u.process to create copy
        def copy_command(_k: str, v: dict) -> dict:
            """Copy single command dict."""
            return dict(v)

        process_result = u.process(
            self._commands, processor=copy_command, on_error="skip"
        )
        return (
            dict(process_result.value)
            if process_result.is_success and isinstance(process_result.value, dict)
            else {}
        )

    def clear_commands(self) -> r[int]:
        """Clear all registered commands.

        Returns:
            r[int]: Number of commands cleared

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
            # Clear CLI group commands - create empty dict
            self._cli_group.commands = {}

            self.logger.debug(
                "All commands cleared successfully",
                operation="clear_commands",
                cleared_count=count,
                source="flext-cli/src/flext_cli/commands.py",
            )

            return r[int].ok(count)
        except Exception as e:  # pragma: no cover
            self.logger.exception(  # pragma: no cover
                "FAILED to clear commands - operation aborted",  # pragma: no cover
                operation="clear_commands",  # pragma: no cover
                error=str(e),  # pragma: no cover
                error_type=type(e).__name__,  # pragma: no cover
                consequence="Commands may still be registered",  # pragma: no cover
                source="flext-cli/src/flext_cli/commands.py",  # pragma: no cover
            )  # pragma: no cover
            return r[int].fail(  # pragma: no cover
                FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def list_commands(self) -> r[list[str]]:
        """List all registered commands.

        Returns:
            r[list[str]]: List of command names

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

            return r[list[str]].ok(command_names)
        except Exception as e:  # pragma: no cover
            self.logger.exception(  # pragma: no cover
                "FAILED to list commands - operation aborted",  # pragma: no cover
                operation="list_commands",  # pragma: no cover
                error=str(e),  # pragma: no cover
                error_type=type(e).__name__,  # pragma: no cover
                consequence="Command list unavailable",  # pragma: no cover
                source="flext-cli/src/flext_cli/commands.py",  # pragma: no cover
            )  # pragma: no cover
            return r[list[str]].fail(  # pragma: no cover
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
