"""CLI Command Bus Service.

- Follow SOLID principles strictly
- Unified class pattern with nested helpers

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextCommands, FlextDomainService, FlextLogger, FlextResult

from flext_cli.commands import (
    AuthLoginCommand,
    AuthLogoutCommand,
    AuthStatusCommand,
    DebugInfoCommand,
    EditConfigCommand,
    SetConfigValueCommand,
    ShowConfigCommand,
)
from flext_cli.handlers import (
    AuthLoginCommandHandler,
    AuthLogoutCommandHandler,
    AuthStatusCommandHandler,
    DebugInfoCommandHandler,
    EditConfigCommandHandler,
    SetConfigValueCommandHandler,
    ShowConfigCommandHandler,
)


class FlextCliCommandBusService(FlextDomainService[None]):
    """CLI Command Bus Service using flext-core Command System exclusively.

    ZERO TOLERANCE COMPLIANCE:
    - Uses FlextCommands.Bus for all command processing
    - NO duplication of flext-core functionality
    - Unified class with nested helpers only
    - Explicit error handling with FlextResult
    """

    def __init__(self) -> None:
        """Initialize CLI Command Bus Service."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._command_bus = FlextCommands.Factories.create_command_bus()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Setup all CLI command handlers with the command bus."""
        try:
            # Register all CLI command handlers
            handlers = [
                ShowConfigCommandHandler(),
                SetConfigValueCommandHandler(),
                EditConfigCommandHandler(),
                AuthLoginCommandHandler(),
                AuthStatusCommandHandler(),
                AuthLogoutCommandHandler(),
                DebugInfoCommandHandler(),
            ]
            for handler in handlers:
                try:
                    self._command_bus.register_handler(handler)
                    self._logger.debug(
                        f"Registered handler: {getattr(handler, 'handler_name', 'unknown')}"
                    )
                except Exception:
                    self._logger.exception("Failed to register handler")
        except Exception:
            self._logger.exception("Failed to setup command handlers")

    class _CommandValidator:
        """Nested helper for command validation - NO loose functions."""

        @staticmethod
        def validate_command_type(command: object) -> FlextResult[bool]:
            """Validate that command is a proper FlextCommand."""
            if not hasattr(command, "validate_command"):
                return FlextResult[bool].fail(
                    f"Invalid command type: {type(command).__name__} is not a FlextCommand"
                )
            return FlextResult[bool].ok(data=True)

        @staticmethod
        def validate_command_data(command: object) -> FlextResult[bool]:
            """Validate command data using command's own validation."""
            if hasattr(command, "validate_command") and callable(
                getattr(command, "validate_command")
            ):
                result = getattr(command, "validate_command")()
                # Ensure we return proper FlextResult[bool]
                if isinstance(result, FlextResult):
                    return result
                return FlextResult[bool].ok(data=True)
            return FlextResult[bool].ok(data=True)

    def execute_show_config_command(
        self, output_format: str = "table", profile: str = "default"
    ) -> FlextResult[dict[str, object]]:
        """Execute show config command using flext-core Command Bus."""
        command = ShowConfigCommand(output_format=output_format, profile=profile)
        # Validate command using nested helper
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Command validation failed: {validation_result.error}"
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._command_bus.execute(command)
        if result.is_success:
            # Cast the result to expected dictionary format
            unwrapped_result = result.unwrap()
            if isinstance(unwrapped_result, dict):
                return FlextResult[dict[str, object]].ok(unwrapped_result)
            # Convert other types to dict format
            result_dict = {"result": unwrapped_result}
            return FlextResult[dict[str, object]].ok(result_dict)
        return FlextResult[dict[str, object]].fail(
            result.error or "Command execution failed"
        )

    def execute_set_config_command(
        self, key: str, value: str, profile: str = "default"
    ) -> FlextResult[bool]:
        """Execute set config command using flext-core Command Bus."""
        command = SetConfigValueCommand(key=key, value=value, profile=profile)
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[bool].fail(
                f"Command validation failed: {validation_result.error}"
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._command_bus.execute(command)
        if result.is_success:
            return FlextResult[bool].ok(data=True)
        return FlextResult[bool].fail(result.error or "Command execution failed")

    def execute_edit_config_command(
        self, profile: str = "default", editor: str = ""
    ) -> FlextResult[bool]:
        """Execute edit config command using flext-core Command Bus."""
        command = EditConfigCommand(profile=profile, editor=editor)
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[bool].fail(
                f"Command validation failed: {validation_result.error}"
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._command_bus.execute(command)
        if result.is_success:
            return FlextResult[bool].ok(data=True)
        return FlextResult[bool].fail(result.error or "Command execution failed")

    def execute_auth_login_command(
        self, username: str, password: str, api_url: str = ""
    ) -> FlextResult[dict[str, object]]:
        """Execute auth login command using flext-core Command Bus."""
        command = AuthLoginCommand(
            username=username, password=password, api_url=api_url
        )
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Command validation failed: {validation_result.error}"
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._command_bus.execute(command)
        if result.is_success:
            # Cast the result to expected dictionary format
            unwrapped_result = result.unwrap()
            if isinstance(unwrapped_result, dict):
                return FlextResult[dict[str, object]].ok(unwrapped_result)
            # Convert other types to dict format
            result_dict = {"result": unwrapped_result}
            return FlextResult[dict[str, object]].ok(result_dict)
        return FlextResult[dict[str, object]].fail(
            result.error or "Command execution failed"
        )

    def execute_auth_status_command(
        self, *, detailed: bool = False
    ) -> FlextResult[dict[str, object]]:
        """Execute auth status command using flext-core Command Bus."""
        command = AuthStatusCommand(detailed=detailed)
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Command validation failed: {validation_result.error}"
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._command_bus.execute(command)
        if result.is_success:
            # Cast the result to expected dictionary format
            unwrapped_result = result.unwrap()
            if isinstance(unwrapped_result, dict):
                return FlextResult[dict[str, object]].ok(unwrapped_result)
            # Convert other types to dict format
            result_dict = {"result": unwrapped_result}
            return FlextResult[dict[str, object]].ok(result_dict)
        return FlextResult[dict[str, object]].fail(
            result.error or "Command execution failed"
        )

    def execute_auth_logout_command(
        self, *, all_profiles: bool = False
    ) -> FlextResult[bool]:
        """Execute auth logout command using flext-core Command Bus."""
        command = AuthLogoutCommand(all_profiles=all_profiles)
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[bool].fail(
                f"Command validation failed: {validation_result.error}"
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._command_bus.execute(command)
        if result.is_success:
            return FlextResult[bool].ok(data=True)
        return FlextResult[bool].fail(result.error or "Command execution failed")

    def execute_debug_info_command(
        self, *, include_system: bool = True, include_config: bool = True
    ) -> FlextResult[dict[str, object]]:
        """Execute debug info command using flext-core Command Bus."""
        command = DebugInfoCommand(
            include_system=include_system, include_config=include_config
        )
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Command validation failed: {validation_result.error}"
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._command_bus.execute(command)
        if result.is_success:
            # Cast the result to expected dictionary format
            unwrapped_result = result.unwrap()
            if isinstance(unwrapped_result, dict):
                return FlextResult[dict[str, object]].ok(unwrapped_result)
            # Convert other types to dict format
            result_dict = {"result": unwrapped_result}
            return FlextResult[dict[str, object]].ok(result_dict)
        return FlextResult[dict[str, object]].fail(
            result.error or "Command execution failed"
        )

    def get_registered_handlers(self) -> list[str]:
        """Get list of registered command handlers."""
        try:
            handlers = self._command_bus.get_registered_handlers()
            return [
                getattr(handler, "handler_name", "unknown")
                for handler in handlers.values()
            ]
        except Exception:
            self._logger.exception("Failed to get registered handlers")
            return []

    def get_command_bus_status(self) -> dict[str, object]:
        """Get command bus status information."""
        return {
            "handlers_count": len(self.get_registered_handlers()),
            "registered_handlers": self.get_registered_handlers(),
            "bus_initialized": self._command_bus is not None,
        }

    def execute(self) -> FlextResult[None]:
        """Execute domain service - returns status of command bus."""
        status = self.get_command_bus_status()
        self._logger.info(f"Command bus status: {status}")
        return FlextResult[None].ok(data=None)
