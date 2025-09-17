"""FLEXT CLI Commands - Unified command models following single-class-per-module pattern.

FLEXT ARCHITECTURAL COMPLIANCE:
- Single unified class with FlextCli prefix (one class per module rule)
- Nested command classes for organizational clarity
- Explicit validation with FlextResult patterns
- Follows SOLID principles and DDD patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from flext_cli.constants import FlextCliConstants
from flext_core import FlextResult


class FlextCliCommands:
    """Unified CLI commands class following single-class-per-module architecture."""

    class ShowConfigCommand(BaseModel):
        """Show CLI configuration command using direct BaseModel pattern."""

        command_type: str = Field(
            default="show_config", description="Command type identifier"
        )

        output_format: str = Field(
            default=FlextCliConstants.OutputFormat.TABLE,
            description="Output format (table, json, yaml)",
        )
        profile: str = Field(
            default=FlextCliConstants.ProfileName.DEFAULT,
            description="Configuration profile to display",
        )

        def validate_command(self) -> FlextResult[bool]:
            """Validate show config command parameters."""
            if self.output_format not in {"table", "json", "yaml"}:
                return FlextResult[bool].fail(
                    f"Invalid output format: {self.output_format}. Must be one of: table, json, yaml"
                )
            return FlextResult[bool].ok(data=True)

    class SetConfigValueCommand(BaseModel):
        """Set configuration value command using direct BaseModel pattern."""

        command_type: str = Field(
            default="set_config_value", description="Command type identifier"
        )

        key: str = Field(description="Configuration key to set")
        value: str = Field(description="Configuration value to set")
        profile: str = Field(
            default=FlextCliConstants.ProfileName.DEFAULT,
            description="Configuration profile to modify",
        )

        def validate_command(self) -> FlextResult[bool]:
            """Validate set config command parameters."""
            if not self.key.strip():
                return FlextResult[bool].fail("Configuration key cannot be empty")
            if not self.value.strip():
                return FlextResult[bool].fail("Configuration value cannot be empty")
            return FlextResult[bool].ok(data=True)

    class EditConfigCommand(BaseModel):
        """Edit configuration command using direct BaseModel pattern."""

        command_type: str = Field(
            default="edit_config", description="Command type identifier"
        )

        profile: str = Field(
            default=FlextCliConstants.ProfileName.DEFAULT,
            description="Configuration profile to edit",
        )
        editor: str = Field(
            default="", description="Editor to use (defaults to $EDITOR env var)"
        )

        def validate_command(self) -> FlextResult[bool]:
            """Validate edit config command parameters."""
            return FlextResult[bool].ok(data=True)

    class AuthLoginCommand(BaseModel):
        """Authentication login command using direct BaseModel pattern."""

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

    class AuthStatusCommand(BaseModel):
        """Authentication status command using direct BaseModel pattern."""

        command_type: str = Field(
            default="auth_status", description="Command type identifier"
        )
        detailed: bool = Field(
            default=False, description="Show detailed authentication information"
        )

        def validate_command(self) -> FlextResult[bool]:
            """Validate auth status command parameters."""
            return FlextResult[bool].ok(data=True)

    class AuthLogoutCommand(BaseModel):
        """Authentication logout command using direct BaseModel pattern."""

        command_type: str = Field(
            default="auth_logout", description="Command type identifier"
        )

        all_profiles: bool = Field(default=False, description="Logout from all profiles")

        def validate_command(self) -> FlextResult[bool]:
            """Validate auth logout command parameters."""
            return FlextResult[bool].ok(data=True)

    class DebugInfoCommand(BaseModel):
        """Debug information command using direct BaseModel pattern."""

        command_type: str = Field(
            default="debug_info", description="Command type identifier"
        )

        include_system: bool = Field(default=True, description="Include system information")
        include_config: bool = Field(
            default=True, description="Include configuration information"
        )

        def validate_command(self) -> FlextResult[bool]:
            """Validate debug info command parameters."""
            return FlextResult[bool].ok(data=True)


__all__ = [
    "FlextCliCommands",
]
