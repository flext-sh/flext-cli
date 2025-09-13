"""CLI Commands - Unified Class Pattern.

FLEXT ARCHITECTURAL COMPLIANCE:
- Single unified class with nested command classes
- Uses FlextCommands.Models.Command exclusively
- Follow SOLID principles strictly
- Explicit error handling with FlextResult

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextCommands, FlextDomainService, FlextLogger, FlextResult
from pydantic import Field

from flext_cli.utils import (
    bool_field,
    command_type_field,
)


class FlextCliCommands(FlextDomainService[None]):
    """Unified CLI Commands Service following FLEXT architectural patterns.

    ZERO TOLERANCE COMPLIANCE:
    - Single unified class per module
    - All command classes nested within this service
    - NO loose functions outside classes
    - Explicit FlextResult error handling
    """

    def __init__(self) -> None:
        """Initialize CLI Commands Service."""
        super().__init__()
        self._logger = FlextLogger(__name__)

    class ShowConfigCommand(FlextCommands.Models.Command):
        """Show CLI configuration command using flext-core Command pattern."""

        command_type: str = Field(
            default="show_config", description="Command type identifier"
        )

        output_format: str = Field(
            default="table", description="Output format (table, json, yaml)"
        )
        profile: str = Field(
            default="default", description="Configuration profile to display"
        )

        def validate_command(self) -> FlextResult[bool]:
            """Validate show config command parameters."""
            if self.output_format not in {"table", "json", "yaml"}:
                return FlextResult[bool].fail(
                    f"Invalid output format: {self.output_format}. Must be one of: table, json, yaml"
                )
            return FlextResult[bool].ok(data=True)

    class SetConfigValueCommand(FlextCommands.Models.Command):
        """Set configuration value command using flext-core Command pattern."""

        command_type: str = Field(
            default="set_config_value", description="Command type identifier"
        )

        key: str = Field(description="Configuration key to set")
        value: str = Field(description="Configuration value to set")
        profile: str = Field(
            default="default", description="Configuration profile to modify"
        )

        def validate_command(self) -> FlextResult[bool]:
            """Validate set config command parameters."""
            if not self.key.strip():
                return FlextResult[bool].fail("Configuration key cannot be empty")
            if not self.value.strip():
                return FlextResult[bool].fail("Configuration value cannot be empty")
            return FlextResult[bool].ok(data=True)

    class EditConfigCommand(FlextCommands.Models.Command):
        """Edit configuration command using flext-core Command pattern."""

        command_type: str = Field(
            default="edit_config", description="Command type identifier"
        )

        profile: str = Field(
            default="default", description="Configuration profile to edit"
        )
        editor: str = Field(
            default="", description="Editor to use (defaults to $EDITOR env var)"
        )

        def validate_command(self) -> FlextResult[bool]:
            """Validate edit config command parameters."""
            return FlextResult[bool].ok(data=True)

    class AuthLoginCommand(FlextCommands.Models.Command):
        """Authentication login command using flext-core Command pattern."""

        command_type: str = Field(
            default="auth_login", description="Command type identifier"
        )

        username: str = Field(description="Username for authentication")
        password: str = Field(description="Password for authentication")
        api_url: str = Field(default="", description="API URL override for login")

        def validate_command(self) -> FlextResult[bool]:
            """Validate auth login command parameters."""
            if not self.username.strip():
                return FlextResult[bool].fail("Username cannot be empty")
            if not self.password.strip():
                return FlextResult[bool].fail("Password cannot be empty")
            return FlextResult[bool].ok(data=True)

    class AuthStatusCommand(FlextCommands.Models.Command):
        """Authentication status command using flext-core Command pattern."""

        command_type: str = command_type_field("auth_status")
        detailed: bool = bool_field(
            False, description="Show detailed authentication information"
        )

        def validate_command(self) -> FlextResult[bool]:
            """Validate auth status command parameters."""
            return FlextResult[bool].ok(data=True)

    class AuthLogoutCommand(FlextCommands.Models.Command):
        """Authentication logout command using flext-core Command pattern."""

        command_type: str = command_type_field("auth_logout")

        all_profiles: bool = Field(
            default=False, description="Logout from all profiles"
        )

        def validate_command(self) -> FlextResult[bool]:
            """Validate auth logout command parameters."""
            return FlextResult[bool].ok(data=True)

    class DebugInfoCommand(FlextCommands.Models.Command):
        """Debug information command using flext-core Command pattern."""

        command_type: str = Field(
            default="debug_info", description="Command type identifier"
        )

        include_system: bool = Field(
            default=True, description="Include system information"
        )
        include_config: bool = Field(
            default=True, description="Include configuration information"
        )

        def validate_command(self) -> FlextResult[bool]:
            """Validate debug info command parameters."""
            return FlextResult[bool].ok(data=True)

    class _CommandFactory:
        """Nested helper class for creating command instances - NO loose functions."""

        @staticmethod
        def create_show_config_command(
            output_format: str = "table", profile: str = "default"
        ) -> FlextCliCommands.ShowConfigCommand:
            """Create show config command instance."""
            return FlextCliCommands.ShowConfigCommand(
                output_format=output_format, profile=profile
            )

        @staticmethod
        def create_set_config_value_command(
            key: str, value: str, profile: str = "default"
        ) -> FlextCliCommands.SetConfigValueCommand:
            """Create set config value command instance."""
            return FlextCliCommands.SetConfigValueCommand(
                key=key, value=value, profile=profile
            )

        @staticmethod
        def create_edit_config_command(
            profile: str = "default", editor: str = ""
        ) -> FlextCliCommands.EditConfigCommand:
            """Create edit config command instance."""
            return FlextCliCommands.EditConfigCommand(profile=profile, editor=editor)

        @staticmethod
        def create_auth_login_command(
            username: str, password: str, api_url: str = ""
        ) -> FlextCliCommands.AuthLoginCommand:
            """Create auth login command instance."""
            return FlextCliCommands.AuthLoginCommand(
                username=username, password=password, api_url=api_url
            )

        @staticmethod
        def create_auth_status_command(
            *, detailed: bool = False
        ) -> FlextCliCommands.AuthStatusCommand:
            """Create auth status command instance."""
            return FlextCliCommands.AuthStatusCommand(detailed=detailed)

        @staticmethod
        def create_auth_logout_command(
            *, all_profiles: bool = False
        ) -> FlextCliCommands.AuthLogoutCommand:
            """Create auth logout command instance."""
            return FlextCliCommands.AuthLogoutCommand(all_profiles=all_profiles)

        @staticmethod
        def create_debug_info_command(
            *, include_system: bool = True, include_config: bool = True
        ) -> FlextCliCommands.DebugInfoCommand:
            """Create debug info command instance."""
            return FlextCliCommands.DebugInfoCommand(
                include_system=include_system, include_config=include_config
            )

    def get_available_commands(self) -> list[str]:
        """Get list of available command types."""
        return [
            "show_config",
            "set_config_value",
            "edit_config",
            "auth_login",
            "auth_status",
            "auth_logout",
            "debug_info",
        ]

    def validate_command_type(self, command_type: str) -> FlextResult[bool]:
        """Validate that command type is supported."""
        if command_type not in self.get_available_commands():
            return FlextResult[bool].fail(
                f"Invalid command type: {command_type}. Available commands: {self.get_available_commands()}"
            )
        return FlextResult[bool].ok(data=True)

    def execute(self) -> FlextResult[None]:
        """Execute domain service - returns command service status."""
        self._logger.info(
            f"CLI Commands Service initialized with {len(self.get_available_commands())} command types"
        )
        return FlextResult[None].ok(data=None)


# Export individual command classes for backward compatibility
ShowConfigCommand = FlextCliCommands.ShowConfigCommand
SetConfigValueCommand = FlextCliCommands.SetConfigValueCommand
EditConfigCommand = FlextCliCommands.EditConfigCommand
AuthLoginCommand = FlextCliCommands.AuthLoginCommand
AuthStatusCommand = FlextCliCommands.AuthStatusCommand
AuthLogoutCommand = FlextCliCommands.AuthLogoutCommand
DebugInfoCommand = FlextCliCommands.DebugInfoCommand
