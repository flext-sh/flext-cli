"""FLEXT CLI Commands - Single unified class following FLEXT standards.

Command creation and management using flext-core patterns.
Single FlextCliCommands class with nested helpers following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import override

from flext_core import (
    r,
    s,
)
from pydantic import PrivateAttr

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.typings import t


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
                    t.GeneralValueType | Callable[..., t.GeneralValueType],
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
        dict[str, t.GeneralValueType | Callable[..., t.GeneralValueType]],
    ] = PrivateAttr(default_factory=dict)
    _cli_group: _CliGroup = PrivateAttr()

    @override
    def __init__(
        self,
        name: str = FlextCliConstants.Cli.CommandsDefaults.DEFAULT_CLI_NAME,
        description: str = FlextCliConstants.Cli.CommandsDefaults.DEFAULT_DESCRIPTION,
        **data: t.GeneralValueType,
    ) -> None:
        """Initialize CLI commands manager with Phase 1 context enrichment."""
        # Convert data for super().__init__()
        # FlextService.__init__ accepts **data: t.GeneralValueType
        # Note: mypy has generic type inference issue with FlextService[JsonDict].__init__
        # but runtime accepts dict[str, t.GeneralValueType] as **kwargs: t.GeneralValueType
        if not isinstance(data, dict):
            msg = "data must be dict"
            raise TypeError(msg)
        # Pass data directly - FlextService base class accepts **kwargs: t.GeneralValueType
        s[dict[str, t.GeneralValueType]].__init__(self, **data)
        # Logger is automatically provided by FlextMixins mixin
        # Use object.__setattr__ for frozen model private attributes
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_description", description)
        # Commands store handler callables - use dict[str, dict] for mutability
        # Handler is Callable[..., t.GeneralValueType]
        empty_commands: dict[
            str,
            dict[
                str,
                t.GeneralValueType | Callable[..., t.GeneralValueType],
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

    def execute(self) -> r[dict[str, t.GeneralValueType]]:
        """Execute the main domain service operation - required by FlextService."""
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

        # Build result dict with proper types
        result_dict: dict[str, t.GeneralValueType] = {
            FlextCliConstants.Cli.CommandsDictKeys.STATUS: FlextCliConstants.Cli.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.Cli.CommandsDictKeys.SERVICE: FlextCliConstants.Cli.FLEXT_CLI,
            FlextCliConstants.Cli.CommandsDictKeys.COMMANDS: list(
                self._commands.keys()
            ),
        }
        result = r[dict[str, t.GeneralValueType]].ok(result_dict)

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
        handler: Callable[..., t.GeneralValueType],
        description: str = FlextCliConstants.Cli.CommandsDefaults.DEFAULT_DESCRIPTION,
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
            # Store command metadata - handler is Callable[..., t.GeneralValueType]
            command_metadata: dict[
                str,
                t.GeneralValueType | Callable[..., t.GeneralValueType],
            ] = {
                FlextCliConstants.Cli.CommandsDictKeys.NAME: name,
                FlextCliConstants.Cli.CommandsDictKeys.HANDLER: handler,
                FlextCliConstants.Cli.CommandsDictKeys.DESCRIPTION: description,
            }
            self._commands[name] = command_metadata
            # Update CLI group commands - copy dict for type compatibility
            updated_commands: dict[
                str,
                dict[
                    str,
                    t.GeneralValueType | Callable[..., t.GeneralValueType],
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
                FlextCliConstants.Cli.ErrorMessages.COMMAND_REGISTRATION_FAILED.format(
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
                FlextCliConstants.Cli.ErrorMessages.COMMAND_NOT_FOUND.format(name=name),
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
                FlextCliConstants.Cli.ErrorMessages.COMMAND_UNREGISTRATION_FAILED.format(
                    error=e,
                ),
            )

    def create_command_group(
        self,
        name: str,
        description: str = "",
        commands: (
            dict[
                str,
                dict[
                    str,
                    t.GeneralValueType | Callable[..., t.GeneralValueType],
                ],
            ]
            | None
        ) = None,
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
                    FlextCliConstants.Cli.ErrorMessages.COMMANDS_REQUIRED,
                )
            validated_commands: dict[
                str,
                dict[
                    str,
                    t.GeneralValueType | Callable[..., t.GeneralValueType],
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
                FlextCliConstants.Cli.ErrorMessages.GROUP_CREATION_FAILED.format(
                    error=e
                ),
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
            if arg.startswith(FlextCliConstants.Cli.CommandsDefaults.OPTION_PREFIX):
                continue  # Skip options
            if arg not in self._commands:
                return r[bool].fail(
                    FlextCliConstants.Cli.ErrorMessages.COMMAND_NOT_FOUND.format(
                        name=arg
                    ),
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
            return r[bool].fail(result.error or "Unknown error")  # pragma: no cover
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
                FlextCliConstants.Cli.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e),
            )

    def get_click_group(self) -> FlextCliCommands._CliGroup:
        """Get the Click group object.

        Returns:
            Click group object

        """
        return self._cli_group

    @staticmethod
    def _execute_handler(
        handler: Callable[..., t.GeneralValueType],
        args: list[str] | None,
    ) -> t.GeneralValueType:
        """Execute command handler with appropriate arguments.

        Args:
            handler: Handler Protocol to execute
            args: Optional command arguments

        Returns:
            Handler execution result as t.GeneralValueType

        Note:
            Handlers can have different signatures:
            - No args: `lambda: result`
            - Single list arg: `def handler(args: list[str]) -> str`
            - Unpacked args: `def handler(*args: str) -> str`
            This method tries to call handlers appropriately.

        """
        # CliCommandHandler Protocol has __call__ method
        # Try unpacking args first (for handlers like handler(*args: str))
        # Then fallback to single list arg or no args
        if args:
            try:
                # Try calling with unpacked args (for handlers expecting *args)
                result: object = handler(*args)
            except TypeError:
                # Handler doesn't accept unpacked args, try single list argument
                try:
                    result = handler(args)
                except TypeError:
                    # Handler doesn't accept list or unpacked args, try without args
                    result = handler()
        else:
            # No args provided, call handler without arguments
            result = handler()

        # === CRITICAL: Unwrap FlextResult if handler returned one ===
        # Handlers may return r[T].ok(value) or r[T].fail(error)
        # We need the unwrapped value/error, not the FlextResult wrapper
        if hasattr(result, "is_success") and hasattr(result, "value"):
            # Result is FlextResult-like (duck typing)
            if result.is_success:
                # Unwrap success value
                result = result.value
            else:
                # Unwrap failure error to string
                result = str(result.error) if hasattr(result, "error") else str(result)

        # Convert result to t.GeneralValueType
        # t.GeneralValueType = ScalarValue | Sequence[t.GeneralValueType] | Mapping[str, t.GeneralValueType]
        # ScalarValue = str | int | float | bool | datetime | None
        # Type narrowing: result is object, narrow to t.GeneralValueType
        if isinstance(result, (str, int, float, bool, type(None))):
            # ScalarValue is part of t.GeneralValueType
            return result
        if isinstance(result, dict):
            # dict[str, t.GeneralValueType] is compatible with Mapping[str, t.GeneralValueType]
            return result
        if isinstance(result, list):
            # list[t.GeneralValueType] is compatible with Sequence[t.GeneralValueType]
            return result
        # Fallback: convert to string (ScalarValue)
        return str(result)

    def execute_command(
        self,
        command_name: str,
        args: list[str] | None = None,
        timeout: int = FlextCliConstants.Cli.TIMEOUTS.DEFAULT,
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
                    FlextCliConstants.Cli.CommandsErrorMessages.COMMAND_NOT_FOUND_DETAIL.format(
                        command_name=command_name,
                    ),
                )

            command_info_raw = self._commands[command_name]
            # Type narrowing: command_info is not a dict, need to check if dict
            if not isinstance(command_info_raw, dict):
                self.logger.error(
                    "FAILED to execute command - command_info is not a dict",
                    operation="execute_command",
                    command_name=command_name,
                    source="flext-cli/src/flext_cli/commands.py",
                )
                return r[t.GeneralValueType].fail(
                    FlextCliConstants.Cli.CommandsErrorMessages.INVALID_COMMAND_STRUCTURE.format(
                        name=command_name,
                    ),
                )
            # Type narrowing: command_info is dict after isinstance check
            command_info: dict[
                str, t.GeneralValueType | Callable[..., t.GeneralValueType]
            ] = command_info_raw
            self.logger.debug(
                "Retrieved command information",
                operation="execute_command",
                command_name=command_name,
                has_handler=FlextCliConstants.Cli.CommandsDictKeys.HANDLER
                in command_info,
                source="flext-cli/src/flext_cli/commands.py",
            )

            # Validate command structure: must be dict-like with handler
            is_valid_structure = (
                FlextCliConstants.Cli.CommandsDictKeys.HANDLER in command_info
            )
            if not is_valid_structure:
                self.logger.error(
                    "FAILED to execute command - invalid command structure",
                    operation="execute_command",
                    command_name=command_name,
                    command_info_keys=(
                        list(command_info.keys())
                        if isinstance(command_info, dict)
                        else None
                    ),
                    consequence="Command execution aborted",
                    source="flext-cli/src/flext_cli/commands.py",
                )
                return r[t.GeneralValueType].fail(
                    FlextCliConstants.Cli.CommandsErrorMessages.INVALID_COMMAND_STRUCTURE.format(
                        command_name=command_name,
                    ),
                )

            # Handler is guaranteed to exist from previous validation
            # Structural typing: handler conforms to Callable[..., t.GeneralValueType]
            # Type narrowing: handler_value is t.GeneralValueType | Callable[..., t.GeneralValueType]
            # Runtime check ensures it's callable
            handler_value: t.GeneralValueType | Callable[..., t.GeneralValueType] = (
                command_info[FlextCliConstants.Cli.CommandsDictKeys.HANDLER]
            )
            # Runtime check: ensure handler is callable
            if not callable(handler_value):
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
                    FlextCliConstants.Cli.CommandsErrorMessages.HANDLER_NOT_CALLABLE.format(
                        command_name=command_name,
                    ),
                )
            handler: Callable[..., t.GeneralValueType] = handler_value

            self.logger.debug(
                "Executing command handler",
                operation="execute_command",
                command_name=command_name,
                handler_type=type(handler).__name__,
                args_provided=args is not None,
                source="flext-cli/src/flext_cli/commands.py",
            )

            result = FlextCliCommands._execute_handler(handler, args)

            # Result from handler is already t.GeneralValueType compatible from _execute_handler
            # _execute_handler guarantees t.GeneralValueType return
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
                FlextCliConstants.Cli.ErrorMessages.COMMAND_EXECUTION_FAILED.format(
                    error=e,
                ),
            )

    def get_commands(
        self,
    ) -> dict[
        str,
        Mapping[str, t.GeneralValueType | Callable[..., t.GeneralValueType]],
    ]:
        """Get all registered commands.

        Returns:
            dict[str, CliCommandMetadata]: Dictionary of registered commands

        """
        # Return copy of commands dict - convert dict to Mapping for return type
        # _commands is typed as dict[str, dict[...]], so v is guaranteed to be dict
        # Use FlextCliUtilities.process to create copy
        return {k: dict(v) for k, v in self._commands.items()}

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
                FlextCliConstants.Cli.ErrorMessages.COMMAND_EXECUTION_FAILED.format(
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
                FlextCliConstants.Cli.CommandsErrorMessages.FAILED_LIST_COMMANDS.format(
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
