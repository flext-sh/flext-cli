"""CLI Command Bus Service.

- Follow SOLID principles strictly
- Unified class pattern with nested helpers

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

from flext_cli.constants import FlextCliConstants
from flext_cli.handlers import FlextCliHandlers
from flext_cli.models import FlextCliModels
from flext_core import (
    FlextBus,
    FlextDispatcher,
    FlextDispatcherRegistry,
    FlextDomainService,
    FlextHandlers,
    FlextLogger,
    FlextResult,
)


class FlextCliCommandBusService(FlextDomainService[None]):
    """CLI Command Bus Service using flext-core Command System exclusively.

    ZERO TOLERANCE COMPLIANCE:
    - Uses FlextBus for all command processing
    - NO duplication of flext-core functionality
    - Unified class with nested helpers only
    - Explicit error handling with FlextResult
    """

    def __init__(self) -> None:
        """Initialize CLI Command Bus Service."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._command_bus = FlextBus.create_command_bus()
        self._use_dispatcher = FlextCliConstants.FeatureFlags.ENABLE_DISPATCHER
        self._dispatcher = (
            FlextDispatcher(bus=self._command_bus) if self._use_dispatcher else None
        )
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Setup all CLI command handlers with the command bus."""
        try:
            # Register all CLI command handlers
            handlers = [
                FlextCliHandlers.ShowConfigCommandHandler(),
                FlextCliHandlers.SetConfigValueCommandHandler(),
                FlextCliHandlers.EditConfigCommandHandler(),
                FlextCliHandlers.AuthLoginCommandHandler(),
                FlextCliHandlers.AuthStatusCommandHandler(),
                FlextCliHandlers.AuthLogoutCommandHandler(),
                FlextCliHandlers.DebugInfoCommandHandler(),
            ]
            registry = (
                FlextDispatcherRegistry(self._dispatcher)
                if self._dispatcher is not None
                else None
            )

            for handler in handlers:
                try:
                    registered_via_dispatcher = False
                    if registry is not None:
                        typed_handler = cast("FlextHandlers[object, object]", handler)
                        registration = registry.register_handler(typed_handler)
                        if registration.is_success:
                            registered_via_dispatcher = True
                        else:
                            self._logger.error(
                                "dispatcher_registration_failed",
                                handler=getattr(
                                    handler,
                                    "handler_name",
                                    handler.__class__.__name__,
                                ),
                                error=registration.error,
                            )

                    if not registered_via_dispatcher:
                        bus_result = self._command_bus.register_handler(handler)
                        if bus_result.is_failure:
                            self._logger.error(
                                "bus_registration_failed",
                                handler=getattr(
                                    handler,
                                    "handler_name",
                                    handler.__class__.__name__,
                                ),
                                error=bus_result.error,
                            )
                            continue

                    self._logger.debug(
                        "handler_registered",
                        handler=getattr(
                            handler,
                            "handler_name",
                            handler.__class__.__name__,
                        ),
                        via_dispatcher=registered_via_dispatcher,
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
                    f"Invalid command type: {type(command).__name__} is not a FlextCommand",
                )
            return FlextResult[bool].ok(data=True)

        @staticmethod
        def validate_command_data(command: object) -> FlextResult[bool]:
            """Validate command data using command's own validation."""
            if hasattr(command, "validate_command") and callable(
                getattr(command, "validate_command", None),
            ):
                # Safe attribute access with getattr instead of direct access
                validate_method = getattr(command, "validate_command")
                result = validate_method()
                # Ensure we return proper FlextResult[bool]
                if isinstance(result, FlextResult):
                    return result
                return FlextResult[bool].ok(data=True)
            return FlextResult[bool].ok(data=True)

    def execute_show_config_command(
        self,
        output_format: str = FlextCliConstants.Output.TABLE,
        profile: str = FlextCliConstants.ProfileName.DEFAULT,
    ) -> FlextResult[dict[str, object]]:
        """Execute show config command using flext-core Command Bus."""
        command = FlextCliModels.ShowConfigCommand(
            output_format=output_format, profile=profile,
        )
        # Validate command using nested helper
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Command validation failed: {validation_result.error}",
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._dispatch(command)
        if result.is_success:
            # Cast the result to expected dictionary format
            unwrapped_result = result.unwrap()
            if isinstance(unwrapped_result, dict):
                return FlextResult[dict[str, object]].ok(unwrapped_result)
            # Convert other types to dict format
            result_dict = {"result": unwrapped_result}
            return FlextResult[dict[str, object]].ok(result_dict)
        return FlextResult[dict[str, object]].fail(
            result.error or "Command execution failed",
        )

    def execute_set_config_command(
        self, key: str, value: str, profile: str = FlextCliConstants.ProfileName.DEFAULT,
    ) -> FlextResult[bool]:
        """Execute set config command using flext-core Command Bus."""
        command = FlextCliModels.SetConfigValueCommand(
            key=key, value=value, profile=profile,
        )
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[bool].fail(
                f"Command validation failed: {validation_result.error}",
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._dispatch(command)
        if result.is_success:
            return FlextResult[bool].ok(data=True)
        return FlextResult[bool].fail(result.error or "Command execution failed")

    def execute_edit_config_command(
        self, profile: str = FlextCliConstants.ProfileName.DEFAULT, editor: str = "",
    ) -> FlextResult[bool]:
        """Execute edit config command using flext-core Command Bus."""
        command = FlextCliModels.EditConfigCommand(profile=profile, editor=editor)
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[bool].fail(
                f"Command validation failed: {validation_result.error}",
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._dispatch(command)
        if result.is_success:
            return FlextResult[bool].ok(data=True)
        return FlextResult[bool].fail(result.error or "Command execution failed")

    def execute_auth_login_command(
        self, username: str, password: str, api_url: str = "",
    ) -> FlextResult[dict[str, object]]:
        """Execute auth login command using flext-core Command Bus."""
        command = FlextCliModels.AuthLoginCommand(
            username=username, password=password, api_url=api_url,
        )
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Command validation failed: {validation_result.error}",
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._dispatch(command)
        if result.is_success:
            # Cast the result to expected dictionary format
            unwrapped_result = result.unwrap()
            if isinstance(unwrapped_result, dict):
                return FlextResult[dict[str, object]].ok(unwrapped_result)
            # Convert other types to dict format
            result_dict = {"result": unwrapped_result}
            return FlextResult[dict[str, object]].ok(result_dict)
        return FlextResult[dict[str, object]].fail(
            result.error or "Command execution failed",
        )

    def execute_auth_status_command(
        self, *, detailed: bool = False,
    ) -> FlextResult[dict[str, object]]:
        """Execute auth status command using flext-core Command Bus."""
        command = FlextCliModels.AuthStatusCommand(detailed=detailed)
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Command validation failed: {validation_result.error}",
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._dispatch(command)
        if result.is_success:
            # Cast the result to expected dictionary format
            unwrapped_result = result.unwrap()
            if isinstance(unwrapped_result, dict):
                return FlextResult[dict[str, object]].ok(unwrapped_result)
            # Convert other types to dict format
            result_dict = {"result": unwrapped_result}
            return FlextResult[dict[str, object]].ok(result_dict)
        return FlextResult[dict[str, object]].fail(
            result.error or "Command execution failed",
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _dispatch(self, command: object) -> FlextResult[object]:
        """Route commands via dispatcher when enabled."""
        if self._dispatcher is not None:
            metadata: dict[str, object] = {
                "command": command.__class__.__name__,
                "source": self.__class__.__name__,
            }
            dispatch_result: FlextResult[object] = self._dispatcher.dispatch(
                command,
                metadata=metadata,
            )
            if dispatch_result.is_failure:
                self._logger.error(
                    "dispatcher_execution_failed",
                    command=command.__class__.__name__,
                    error=dispatch_result.error,
                )
            return dispatch_result
        return self._command_bus.execute(command)

    def execute_auth_logout_command(
        self, *, all_profiles: bool = False,
    ) -> FlextResult[bool]:
        """Execute auth logout command using flext-core Command Bus."""
        command = FlextCliModels.AuthLogoutCommand(all_profiles=all_profiles)
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[bool].fail(
                f"Command validation failed: {validation_result.error}",
            )
        # Execute using flext-core Command Bus with type-safe casting
        result = self._command_bus.execute(command)
        if result.is_success:
            return FlextResult[bool].ok(data=True)
        return FlextResult[bool].fail(result.error or "Command execution failed")

    def execute_debug_info_command(
        self, *, include_system: bool = True, include_config: bool = True,
    ) -> FlextResult[dict[str, object]]:
        """Execute debug info command using flext-core Command Bus."""
        command = FlextCliModels.DebugInfoCommand(
            include_system=include_system, include_config=include_config,
        )
        validation_result = self._CommandValidator.validate_command_data(command)
        if validation_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Command validation failed: {validation_result.error}",
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
            result.error or "Command execution failed",
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
        return FlextResult[None].ok(None)
