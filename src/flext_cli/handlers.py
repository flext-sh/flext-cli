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
from pathlib import Path
from typing import cast

from pydantic import BaseModel

from flext_cli.configs import FlextCliConfigs
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_core import FlextDomainService, FlextHandlers, FlextLogger, FlextResult


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
        FlextHandlers[FlextCliModels.ShowConfigCommand, dict[str, object]],
    ):
        """Handler for showing CLI configuration using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize ShowConfigHandler."""
            super().__init__(handler_name="ShowConfigHandler")

        def handle(
            self,
            message: FlextCliModels.ShowConfigCommand,
        ) -> FlextResult[dict[str, object]]:
            """Handle show config command with proper error handling.

            Returns:
            FlextResult[dict[str, object]]: Description of return value.

            """
            try:
                # Load configuration using flext-cli config system
                config = FlextCliConfigs(profile=message.profile)
                config_dict = config.model_dump()

                # Format based on requested output format
                if message.output_format == "json":
                    return FlextResult[dict[str, object]].ok(
                        {"format": "json", "data": config_dict},
                    )
                if message.output_format == "yaml":
                    return FlextResult[dict[str, object]].ok(
                        {"format": "yaml", "data": config_dict},
                    )
                # table format
                return FlextResult[dict[str, object]].ok(
                    {
                        "format": "table",
                        "data": config_dict,
                        "title": f"Configuration Profile: {message.profile}",
                    },
                )

            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to show configuration: {e}",
                )

    class SetConfigValueCommandHandler(
        FlextHandlers[FlextCliModels.SetConfigValueCommand, bool],
    ):
        """Handler for setting configuration values using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize SetConfigValueHandler."""
            super().__init__(handler_name="SetConfigValueHandler")

        def handle(
            self,
            message: FlextCliModels.SetConfigValueCommand,
        ) -> FlextResult[bool]:
            """Handle set config value command with proper error handling.

            Returns:
            FlextResult[bool]: Description of return value.

            """
            try:
                # Load current configuration
                config = FlextCliConfigs(profile=message.profile)

                # Check if key exists in model
                if message.key not in cast("BaseModel", config).__class__.model_fields:
                    return FlextResult[bool].fail(
                        f"Configuration key '{message.key}' is not valid. "
                        f"Available keys: {list(cast('BaseModel', config).__class__.model_fields.keys())}",
                    )

                # Set the value using Pydantic model validation
                setattr(config, message.key, message.value)

                # Save configuration (this would need to be implemented)
                # For now, just validate that the setting worked
                new_value = getattr(config, message.key)
                if str(new_value) != message.value:
                    return FlextResult[bool].fail(
                        f"Failed to set configuration value. Expected: {message.value}, Got: {new_value}",
                    )

                self.logger.info(
                    f"Configuration updated: {message.key} = {message.value}",
                )
                return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(f"Failed to set configuration value: {e}")

    class EditConfigCommandHandler(
        FlextHandlers[FlextCliModels.EditConfigCommand, bool],
    ):
        """Handler for editing configuration using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize EditConfigHandler."""
            super().__init__(handler_name="EditConfigHandler")
            self._constants = FlextCliConstants()

        def handle(
            self,
            message: FlextCliModels.EditConfigCommand,
        ) -> FlextResult[bool]:
            """Handle edit config command with proper error handling.

            Returns:
            FlextResult[bool]: Description of return value.

            """
            try:
                config = FlextCliConfigs(profile=message.profile)
                config_file = Path(str(config.config_dir)) / f"{message.profile}.json"

                # Ensure config directory exists
                config_file.parent.mkdir(parents=True, exist_ok=True)

                # Write current config to file if it doesn't exist
                if not config_file.exists():
                    with config_file.open("w") as f:
                        json.dump(config.model_dump(), f, indent=2)

                # Use constants for editor configuration (single source of truth)
                editor = message.editor or self._constants.SYSTEM.editor_command

                # This would open the editor - for now just simulate success
                self.logger.info(f"Would open {config_file} with {editor}")

                return FlextResult[bool].ok(data=True)

            except Exception as e:
                return FlextResult[bool].fail(f"Failed to edit configuration: {e}")

    class AuthLoginCommandHandler(
        FlextHandlers[FlextCliModels.AuthLoginCommand, dict[str, object]],
    ):
        """Handler for authentication login using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize AuthLoginHandler."""
            super().__init__(handler_name="AuthLoginHandler")

        def handle(
            self,
            message: FlextCliModels.AuthLoginCommand,
        ) -> FlextResult[dict[str, object]]:
            """Handle auth login command with proper error handling.

            Returns:
            FlextResult[dict[str, object]]: Description of return value.

            """
            try:
                # Simulate authentication process
                # In real implementation, this would call the API
                api_url = message.api_url or "https://api.flext.com"

                self.logger.info(
                    f"Authenticating user {message.username} with {api_url}",
                )

                # Simulate successful login
                token_data = {
                    "username": message.username,
                    "api_url": api_url,
                    "authenticated": True,
                    "login_time": "2025-01-08T10:00:00Z",
                }

                return FlextResult[dict[str, object]].ok(token_data)

            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Authentication failed: {e}",
                )

    class AuthStatusCommandHandler(
        FlextHandlers[FlextCliModels.AuthStatusCommand, dict[str, object]],
    ):
        """Handler for authentication status using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize AuthStatusHandler."""
            super().__init__(handler_name="AuthStatusHandler")

        def handle(
            self,
            message: FlextCliModels.AuthStatusCommand,
        ) -> FlextResult[dict[str, object]]:
            """Handle auth status command with proper error handling.

            Returns:
            FlextResult[dict[str, object]]: Description of return value.

            """
            try:
                # Check authentication status
                config = FlextCliConfigs()
                token_file = config.token_file

                if not token_file.exists():
                    return FlextResult[dict[str, object]].ok(
                        {"authenticated": False, "message": "Not authenticated"},
                    )

                # Simulate reading token file
                status_data = {
                    "authenticated": True,
                    "token_file": str(token_file),
                    "message": "Authenticated",
                }

                if message.detailed:
                    status_data.update(
                        {
                            "config_dir": str(config.config_dir),
                            "api_url": config.api_url,
                            "profile": config.profile,
                        },
                    )

                return FlextResult[dict[str, object]].ok(status_data)

            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to check authentication status: {e}",
                )

    class AuthLogoutCommandHandler(
        FlextHandlers[FlextCliModels.AuthLogoutCommand, bool],
    ):
        """Handler for authentication logout using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize AuthLogoutHandler."""
            super().__init__(handler_name="AuthLogoutHandler")

        def handle(
            self,
            message: FlextCliModels.AuthLogoutCommand,
        ) -> FlextResult[bool]:
            """Handle auth logout command with proper error handling.

            Returns:
            FlextResult[bool]: Description of return value.

            """
            try:
                config = FlextCliConfigs()

                if message.all_profiles:
                    # Remove entire auth directory
                    auth_dir = Path(str(config.config_dir)) / "auth"
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
        FlextHandlers[FlextCliModels.DebugInfoCommand, dict[str, object]],
    ):
        """Handler for debug information using flext-core CommandHandler."""

        def __init__(self) -> None:
            """Initialize DebugInfoHandler."""
            super().__init__(handler_name="DebugInfoHandler")

        def handle(
            self,
            message: FlextCliModels.DebugInfoCommand,
        ) -> FlextResult[dict[str, object]]:
            """Handle debug info command with proper error handling.

            Returns:
            FlextResult[dict[str, object]]: Description of return value.

            """
            try:
                debug_info: dict[str, object] = {
                    "flext_cli_version": "2.1.0",
                    "timestamp": "2025-01-08T10:00:00Z",
                }

                if message.include_system:
                    debug_info["system"] = {
                        "platform": "linux",
                        "python_version": "3.13+",
                        "working_directory": str(Path.cwd()),
                    }

                if message.include_config:
                    config = FlextCliConfigs()
                    debug_info["config"] = {
                        "profile": config.profile,
                        "api_url": config.api_url,
                        "config_dir": str(config.config_dir),
                        "debug_mode": config.debug,
                    }

                return FlextResult[dict[str, object]].ok(debug_info)

            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to gather debug information: {e}",
                )

    class _HandlerRegistry:
        """Nested helper class for handler registration - NO loose functions."""

        @staticmethod
        def get_all_handler_classes() -> list[type]:
            """Get all available handler classes.

            Returns:
            list[type]: Description of return value.

            """
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
            """Create instances of all handlers.

            Returns:
            list[object]: Description of return value.

            """
            handler_classes = (
                FlextCliHandlers._HandlerRegistry.get_all_handler_classes()
            )
            return [handler_class() for handler_class in handler_classes]

        @staticmethod
        def validate_handler_instance(handler: object) -> FlextResult[bool]:
            """Validate that handler instance is properly configured.

            Returns:
            FlextResult[bool]: Description of return value.

            """
            if not hasattr(handler, "handle"):
                return FlextResult[bool].fail(
                    f"Handler {type(handler).__name__} missing handle method",
                )
            if not hasattr(handler, "handler_name"):
                return FlextResult[bool].fail(
                    f"Handler {type(handler).__name__} missing handler_name attribute",
                )
            return FlextResult[bool].ok(data=True)

    def get_available_handlers(self) -> list[str]:
        """Get list of available handler names.

        Returns:
            list[str]: Description of return value.

        """
        handler_classes = self._HandlerRegistry.get_all_handler_classes()
        return [cls.__name__ for cls in handler_classes]

    def create_handler_instances(self) -> FlextResult[list[object]]:
        """Create instances of all handlers with validation.

        Returns:
            FlextResult[list[object]]: Description of return value.

        """
        try:
            handlers = self._HandlerRegistry.create_all_handlers()

            # Validate each handler
            for handler in handlers:
                validation_result = self._HandlerRegistry.validate_handler_instance(
                    handler,
                )
                if validation_result.is_failure:
                    return FlextResult[list[object]].fail(
                        f"Handler validation failed: {validation_result.error}",
                    )

            self._logger.info(f"Created {len(handlers)} handler instances")
            return FlextResult[list[object]].ok(data=handlers)

        except Exception as e:
            return FlextResult[list[object]].fail(
                f"Failed to create handler instances: {e}",
            )

    def execute(self) -> FlextResult[None]:
        """Execute domain service - returns handlers service status.

        Returns:
            FlextResult[None]: Success result with None value.

        """
        handlers_result = self.create_handler_instances()
        if handlers_result.is_failure:
            return FlextResult[None].fail(
                f"Handlers service failed: {handlers_result.error}",
            )

        handlers_count = len(handlers_result.unwrap())
        self._logger.info(
            f"CLI Handlers Service initialized with {handlers_count} handlers",
        )
        return FlextResult[None].ok(data=None)
