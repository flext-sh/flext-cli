"""FLEXT CLI Context - CLI execution context management.

Provides CLI execution context with type-safe operations and FlextCore.Result patterns.
Follows FLEXT standards with single CliContext class per module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import uuid

from flext_core import FlextCore
from pydantic import Field

from flext_cli.config import FlextCliConfig
from flext_cli.typings import FlextCliTypes


class FlextCliContext(FlextCore.Service[FlextCliTypes.Data.CliDataDict]):
    """CLI execution context model extending FlextCore.Service.

    Manages CLI execution context with enhanced type safety using FlextCliTypes
    instead of generic FlextCore.Types types. Provides CLI-specific context with domain types
    and uses FlextCore.Result railway pattern for all operations.

    CRITICAL: Moved from models.py to follow FLEXT standards requiring
    service classes to be in appropriate modules, not mixed with data models.
    """

    # Direct attributes - no properties needed
    id: str = ""
    command: str | None = None
    arguments: FlextCore.Types.StringList = Field(default_factory=list)
    environment_variables: FlextCore.Types.Dict = Field(default_factory=dict)
    working_directory: str | None = None
    context_metadata: FlextCore.Types.Dict = Field(default_factory=dict)

    # Context state
    is_active: bool = False
    created_at: str = ""
    timeout_seconds: int = Field(default=30)

    def __init__(
        self,
        command: str | None = None,
        arguments: FlextCore.Types.StringList | None = None,
        environment_variables: FlextCore.Types.Dict | None = None,
        working_directory: str | None = None,
        **data: object,
    ) -> None:
        """Initialize CLI context with enhanced type safety.

        Args:
            command: Command being executed
            arguments: Command line arguments
            environment_variables: Environment variables using CLI-specific config data types
            working_directory: Current working directory
            **data: Additional entity initialization data

        """
        # Generate id if not provided
        if "id" not in data:
            data["id"] = str(uuid.uuid4())

        # Initialize parent FlextCore.Service
        super().__init__(**data)

        # Set id from data or generated
        self.id = str(data.get("id", str(uuid.uuid4())))

        # Set CLI context attributes directly
        self.command = command
        self.arguments = arguments or []
        self.environment_variables = environment_variables or {}
        self.working_directory = working_directory
        self.context_metadata = {}

        # Context state
        self.is_active = False
        self.created_at = FlextCore.Utilities.Generators.generate_timestamp()
        self.timeout_seconds = FlextCliConfig.get_global_instance().timeout_seconds

    def activate(self) -> FlextCore.Result[None]:
        """Activate CLI context for execution."""
        try:
            if self.is_active:
                return FlextCore.Result[None].fail("Context is already active")

            self.is_active = True
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(f"Context activation failed: {e}")

    def deactivate(self) -> FlextCore.Result[None]:
        """Deactivate CLI context."""
        try:
            if not self.is_active:
                return FlextCore.Result[None].fail("Context is not currently active")

            self.is_active = False
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(f"Context deactivation failed: {e}")

    def get_environment_variable(self, name: str) -> FlextCore.Result[str]:
        """Get specific environment variable value."""
        if not name or not isinstance(name, str):
            return FlextCore.Result[str].fail(
                "Variable name must be a non-empty string"
            )

        try:
            if name in self.environment_variables:
                value = self.environment_variables[name]
                return FlextCore.Result[str].ok(str(value))
            return FlextCore.Result[str].fail(
                f"Environment variable '{name}' not found"
            )
        except Exception as e:
            return FlextCore.Result[str].fail(
                f"Environment variable retrieval failed: {e}"
            )

    def set_environment_variable(self, name: str, value: str) -> FlextCore.Result[None]:
        """Set environment variable value."""
        if not name or not isinstance(name, str):
            return FlextCore.Result[None].fail(
                "Variable name must be a non-empty string"
            )

        if not isinstance(value, str):
            return FlextCore.Result[None].fail("Variable value must be a string")

        try:
            self.environment_variables[name] = value
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(
                f"Environment variable setting failed: {e}"
            )

    def add_argument(self, argument: str) -> FlextCore.Result[None]:
        """Add command line argument."""
        if not argument or not isinstance(argument, str):
            return FlextCore.Result[None].fail("Argument must be a non-empty string")

        try:
            self.arguments.append(argument)
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(f"Argument addition failed: {e}")

    def remove_argument(self, argument: str) -> FlextCore.Result[None]:
        """Remove command line argument."""
        if not argument or not isinstance(argument, str):
            return FlextCore.Result[None].fail("Argument must be a non-empty string")

        try:
            if argument in self.arguments:
                self.arguments.remove(argument)
                return FlextCore.Result[None].ok(None)
            return FlextCore.Result[None].fail(f"Argument '{argument}' not found")
        except Exception as e:
            return FlextCore.Result[None].fail(f"Argument removal failed: {e}")

    def set_metadata(self, key: str, value: object) -> FlextCore.Result[None]:
        """Set context metadata using CLI-specific data types."""
        if not key or not isinstance(key, str):
            return FlextCore.Result[None].fail(
                "Metadata key must be a non-empty string"
            )

        try:
            self.context_metadata[key] = value
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(f"Metadata setting failed: {e}")

    def get_metadata(self, key: str) -> FlextCore.Result[object]:
        """Get context metadata value."""
        if not key or not isinstance(key, str):
            return FlextCore.Result[object].fail(
                "Metadata key must be a non-empty string"
            )

        try:
            if key in self.context_metadata:
                return FlextCore.Result[object].ok(self.context_metadata[key])
            return FlextCore.Result[object].fail(f"Metadata key '{key}' not found")
        except Exception as e:
            return FlextCore.Result[object].fail(f"Metadata retrieval failed: {e}")

    def get_context_summary(
        self,
    ) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Get comprehensive context summary using CLI-specific data types."""
        try:
            summary: FlextCore.Types.Dict = {
                "context_id": self.id,
                "command": self.command or "none",
                "arguments_count": len(self.arguments),
                "arguments": list(self.arguments),
                "environment_variables_count": len(self.environment_variables),
                "working_directory": self.working_directory or "not_set",
                "is_active": self.is_active,
                "created_at": self.created_at,
                "metadata_keys": list(self.context_metadata.keys()),
                "metadata_count": len(self.context_metadata),
            }

            return FlextCore.Result[FlextCore.Types.Dict].ok(summary)
        except Exception as e:
            return FlextCore.Result[FlextCore.Types.Dict].fail(
                f"Context summary generation failed: {e}",
            )

    def execute(self) -> FlextCore.Result[FlextCliTypes.Data.CliDataDict]:
        """Execute the CLI context."""
        try:
            result: FlextCliTypes.Data.CliDataDict = {
                "context_executed": True,
                "command": self.command,
                "arguments_count": len(self.arguments) if self.arguments else 0,
                "timestamp": FlextCore.Utilities.Generators.generate_timestamp(),
            }
            return FlextCore.Result[FlextCliTypes.Data.CliDataDict].ok(result)
        except Exception as e:
            return FlextCore.Result[FlextCliTypes.Data.CliDataDict].fail(
                f"Context execution failed: {e}"
            )

    def to_dict(self) -> FlextCore.Types.Dict:
        """Convert context to dictionary."""
        return {
            "id": self.id,
            "command": self.command,
            "arguments": self.arguments or [],
            "environment_variables": self.environment_variables or {},
            "working_directory": self.working_directory,
            "created_at": self.created_at,
            "timeout_seconds": self.timeout_seconds,
        }


__all__ = [
    "FlextCliContext",
]
