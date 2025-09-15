"""FLEXT CLI Handlers - Unified Class Pattern.

FLEXT ARCHITECTURAL COMPLIANCE:
- Single unified class with nested handler classes
- Command handlers for CLI operations using flext-core patterns
- NO loose functions outside classes
- Explicit error handling with FlextResult

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import cast

from flext_core import FlextCommands, FlextDomainService, FlextLogger, FlextResult
from pydantic import BaseModel

from flext_cli.commands import (
    AuthLoginCommand,
    AuthLogoutCommand,
    AuthStatusCommand,
    DebugInfoCommand,
    EditConfigCommand,
    SetConfigValueCommand,
    ShowConfigCommand,
)
from flext_cli.config import FlextCliConfig


class FlextCliHandlers(FlextDomainService[None]):
    """Unified CLI Handlers Service following FLEXT architectural patterns.

    ZERO TOLERANCE COMPLIANCE:
    - Single unified class per module
    - All handler classes nested within this service
    - NO loose functions outside classes
    - Explicit FlextResult error handling
    """

    def __init__(self) -> None:
        """Initialize CLI Handlers Service."""
        super().__init__()
        self._logger = FlextLogger(__name__)

    class ShowConfigCommandHandler(
        FlextCommands.Handlers.CommandHandler[ShowConfigCommand, dict[str, object]]
    ):
        """Handler for showing CLI configuration using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize ShowConfigHandler."""
            super().__init__(handler_name="ShowConfigHandler")

        def handle(self, command: ShowConfigCommand) -> FlextResult[dict[str, object]]:
            """Handle show config command with proper error handling."""
            try:
                # Load configuration using flext-cli config system
                config = FlextCliConfig(profile=command.profile)
                config_dict = config.model_dump()

                # Format based on requested output format
                if command.output_format == "json":
                    return FlextResult[dict[str, object]].ok(
                        {"format": "json", "data": config_dict}
                    )
                if command.output_format == "yaml":
                    return FlextResult[dict[str, object]].ok(
                        {"format": "yaml", "data": config_dict}
                    )
                # table format
                return FlextResult[dict[str, object]].ok(
                    {
                        "format": "table",
                        "data": config_dict,
                        "title": f"Configuration Profile: {command.profile}",
                    }
                )

            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to show configuration: {e}"
                )

    class SetConfigValueCommandHandler(
        FlextCommands.Handlers.CommandHandler[SetConfigValueCommand, bool]
    ):
        """Handler for setting configuration values using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize SetConfigValueHandler."""
            super().__init__(handler_name="SetConfigValueHandler")

        def handle(self, command: SetConfigValueCommand) -> FlextResult[bool]:
            """Handle set config value command with proper error handling."""
            try:
                # Load current configuration
                config = FlextCliConfig(profile=command.profile)

                # Check if key exists in model
                if command.key not in cast(BaseModel, config.__class__).model_fields:
                    return FlextResult[bool].fail(
                        f"Configuration key '{command.key}' is not valid. "
                        f"Available keys: {list(cast(BaseModel, config.__class__).model_fields.keys())}"
                    )

                # Set the value using Pydantic model validation
                setattr(config, command.key, command.value)

                # Save configuration (this would need to be implemented)
                # For now, just validate that the setting worked
                new_value = getattr(config, command.key)
                if str(new_value) != command.value:
                    return FlextResult[bool].fail(
                        f"Failed to set configuration value. Expected: {command.value}, Got: {new_value}"
                    )

                self.logger.info(
                    f"Configuration updated: {command.key} = {command.value}"
                )
                return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(f"Failed to set configuration value: {e}")

    class EditConfigCommandHandler(
        FlextCommands.Handlers.CommandHandler[EditConfigCommand, bool]
    ):
        """Handler for editing configuration using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize EditConfigHandler."""
            super().__init__(handler_name="EditConfigHandler")

        def handle(self, command: EditConfigCommand) -> FlextResult[bool]:
            """Handle edit config command with proper error handling."""
            try:
                config = FlextCliConfig(profile=command.profile)
                config_file = config.config_dir / f"{command.profile}.json"

                # Ensure config directory exists
                config_file.parent.mkdir(parents=True, exist_ok=True)

                # Write current config to file if it doesn't exist
                if not config_file.exists():
                    with config_file.open("w") as f:
                        json.dump(config.model_dump(), f, indent=2)

                # Determine editor
                editor = command.editor or os.environ.get("EDITOR", "nano")

                # This would open the editor - for now just simulate success
                self.logger.info(f"Would open {config_file} with {editor}")

                return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(f"Failed to edit configuration: {e}")

    class AuthLoginCommandHandler(
        FlextCommands.Handlers.CommandHandler[AuthLoginCommand, dict[str, object]]
    ):
        """Handler for authentication login using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize AuthLoginHandler."""
            super().__init__(handler_name="AuthLoginHandler")

        def handle(self, command: AuthLoginCommand) -> FlextResult[dict[str, object]]:
            """Handle auth login command with proper error handling."""
            try:
                # Simulate authentication process
                # In real implementation, this would call the API
                api_url = command.api_url or "https://api.flext.com"

                self.logger.info(
                    f"Authenticating user {command.username} with {api_url}"
                )

                # Simulate successful login
                token_data = {
                    "username": command.username,
                    "api_url": api_url,
                    "authenticated": True,
                    "login_time": "2025-01-08T10:00:00Z",
                }

                return FlextResult[dict[str, object]].ok(token_data)

            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Authentication failed: {e}"
                )

    class AuthStatusCommandHandler(
        FlextCommands.Handlers.CommandHandler[AuthStatusCommand, dict[str, object]]
    ):
        """Handler for authentication status using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize AuthStatusHandler."""
            super().__init__(handler_name="AuthStatusHandler")

        def handle(self, command: AuthStatusCommand) -> FlextResult[dict[str, object]]:
            """Handle auth status command with proper error handling."""
            try:
                # Check authentication status
                config = FlextCliConfig()
                token_file = config.token_file

                if not token_file.exists():
                    return FlextResult[dict[str, object]].ok(
                        {"authenticated": False, "message": "Not authenticated"}
                    )

                # Simulate reading token file
                status_data = {
                    "authenticated": True,
                    "token_file": str(token_file),
                    "message": "Authenticated",
                }

                if command.detailed:
                    status_data.update(
                        {
                            "config_dir": str(config.config_dir),
                            "api_url": config.api_url,
                            "profile": config.profile,
                        }
                    )

                return FlextResult[dict[str, object]].ok(status_data)

            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to check authentication status: {e}"
                )

    class AuthLogoutCommandHandler(
        FlextCommands.Handlers.CommandHandler[AuthLogoutCommand, bool]
    ):
        """Handler for authentication logout using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize AuthLogoutHandler."""
            super().__init__(handler_name="AuthLogoutHandler")

        def handle(self, command: AuthLogoutCommand) -> FlextResult[bool]:
            """Handle auth logout command with proper error handling."""
            try:
                config = FlextCliConfig()

                if command.all_profiles:
                    # Remove entire auth directory
                    auth_dir = config.config_dir / "auth"
                    if auth_dir.exists():
                        # In real implementation, would remove files
                        self.logger.info("Would remove all authentication tokens")
                else:
                    # Remove specific token files
                    token_file = config.token_file
                    refresh_token_file = config.refresh_token_file

                    files_removed = []
                    if token_file.exists():
                        files_removed.append(str(token_file))
                    if refresh_token_file.exists():
                        files_removed.append(str(refresh_token_file))

                    self.logger.info(f"Would remove token files: {files_removed}")

                return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(f"Logout failed: {e}")

    class DebugInfoCommandHandler(
        FlextCommands.Handlers.CommandHandler[DebugInfoCommand, dict[str, object]]
    ):
        """Handler for debug information using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize DebugInfoHandler."""
            super().__init__(handler_name="DebugInfoHandler")

        def handle(self, command: DebugInfoCommand) -> FlextResult[dict[str, object]]:
            """Handle debug info command with proper error handling."""
            try:
                debug_info: dict[str, object] = {
                    "flext_cli_version": "2.1.0",
                    "timestamp": "2025-01-08T10:00:00Z",
                }

                if command.include_system:
                    debug_info["system"] = {
                        "platform": "linux",
                        "python_version": "3.13+",
                        "working_directory": str(Path.cwd()),
                    }

                if command.include_config:
                    config = FlextCliConfig()
                    debug_info["config"] = {
                        "profile": config.profile,
                        "api_url": config.api_url,
                        "config_dir": str(config.config_dir),
                        "debug_mode": config.debug,
                    }

                return FlextResult[dict[str, object]].ok(debug_info)

            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to gather debug information: {e}"
                )

    class _HandlerRegistry:
        """Nested helper class for handler registration - NO loose functions."""

        @staticmethod
        def get_all_handler_classes() -> list[type]:
            """Get all available handler classes."""
            return [
                FlextCliHandlers.ShowConfigCommandHandler,
                FlextCliHandlers.SetConfigValueCommandHandler,
                FlextCliHandlers.EditConfigCommandHandler,
                FlextCliHandlers.AuthLoginCommandHandler,
                FlextCliHandlers.AuthStatusCommandHandler,
                FlextCliHandlers.AuthLogoutCommandHandler,
                FlextCliHandlers.DebugInfoCommandHandler,
            ]

        @staticmethod
        def create_all_handlers() -> list[object]:
            """Create instances of all handlers."""
            handler_classes = (
                FlextCliHandlers._HandlerRegistry.get_all_handler_classes()
            )
            return [handler_class() for handler_class in handler_classes]

        @staticmethod
        def validate_handler_instance(handler: object) -> FlextResult[bool]:
            """Validate that handler instance is properly configured."""
            if not hasattr(handler, "handle"):
                return FlextResult[bool].fail(
                    f"Handler {type(handler).__name__} missing handle method"
                )
            if not hasattr(handler, "handler_name"):
                return FlextResult[bool].fail(
                    f"Handler {type(handler).__name__} missing handler_name attribute"
                )
            return FlextResult[bool].ok(data=True)

    def get_available_handlers(self) -> list[str]:
        """Get list of available handler names."""
        handler_classes = self._HandlerRegistry.get_all_handler_classes()
        return [cls.__name__ for cls in handler_classes]

    def create_handler_instances(self) -> FlextResult[list[object]]:
        """Create instances of all handlers with validation."""
        try:
            handlers = self._HandlerRegistry.create_all_handlers()

            # Validate each handler
            for handler in handlers:
                validation_result = self._HandlerRegistry.validate_handler_instance(
                    handler
                )
                if validation_result.is_failure:
                    return FlextResult[list[object]].fail(
                        f"Handler validation failed: {validation_result.error}"
                    )

            self._logger.info(f"Created {len(handlers)} handler instances")
            return FlextResult[list[object]].ok(data=handlers)

        except Exception as e:
            return FlextResult[list[object]].fail(
                f"Failed to create handler instances: {e}"
            )

    def execute(self) -> FlextResult[None]:
        """Execute domain service - returns handlers service status."""
        handlers_result = self.create_handler_instances()
        if handlers_result.is_failure:
            return FlextResult[None].fail(
                f"Handlers service failed: {handlers_result.error}"
            )

        handlers_count = len(handlers_result.unwrap())
        self._logger.info(
            f"CLI Handlers Service initialized with {handlers_count} handlers"
        )
        return FlextResult[None].ok(data=None)


# Export individual handler classes for backward compatibility
ShowConfigCommandHandler = FlextCliHandlers.ShowConfigCommandHandler
SetConfigValueCommandHandler = FlextCliHandlers.SetConfigValueCommandHandler
EditConfigCommandHandler = FlextCliHandlers.EditConfigCommandHandler
AuthLoginCommandHandler = FlextCliHandlers.AuthLoginCommandHandler
AuthStatusCommandHandler = FlextCliHandlers.AuthStatusCommandHandler
AuthLogoutCommandHandler = FlextCliHandlers.AuthLogoutCommandHandler
DebugInfoCommandHandler = FlextCliHandlers.DebugInfoCommandHandler
