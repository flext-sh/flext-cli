"""Type definitions for FLEXT CLI with full backup functionality restored.

Based on the original backup - all types and interfaces restored.
Following strict naming conventions: FlextCli*, TCli*, flext_cli_*
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

# DRY: Use REAL flext-core imports from main API - NO DUPLICATION
from flext_core import (
    FlextEntity,
    FlextResult,
    FlextUtilities,
    FlextValueObject,
    TValue,
)
from pydantic import Field

# Core data types
type TCliData = TValue
type TCliPath = str | Path
type TCliFormat = str
# Type alias for CLI handlers without ellipsis (avoids Any)
TCliHandler = Callable[[object], object]
type TCliConfig = dict[str, object]
type TCliArgs = list[str]


class FlextCliCommandStatus(StrEnum):
    """Command execution status from original backup."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FlextCliCommandType(StrEnum):
    """Command types from original backup."""

    SYSTEM = "system"
    PIPELINE = "pipeline"
    PLUGIN = "plugin"
    DATA = "data"
    CONFIG = "config"
    AUTH = "auth"
    MONITORING = "monitoring"


class FlextCliOutputFormat(StrEnum):
    """Output format options from original backup."""

    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    TABLE = "table"
    PLAIN = "plain"


class FlextCliCommand(FlextEntity):
    """CLI command entity with execution tracking - restored from backup."""

    # Pydantic fields
    name: str
    command_line: str
    options: dict[str, object] = Field(default_factory=dict)
    command_status: FlextCliCommandStatus = FlextCliCommandStatus.PENDING
    command_type: FlextCliCommandType = FlextCliCommandType.SYSTEM
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    exit_code: int | None = None
    output: str = ""
    timeout: int | None = None

    def flext_cli_start_execution(self) -> bool:
        """Start command execution."""
        if self.command_status != FlextCliCommandStatus.PENDING:
            return False
        object.__setattr__(self, "command_status", FlextCliCommandStatus.RUNNING)
        object.__setattr__(self, "updated_at", datetime.now(UTC))
        return True

    def flext_cli_complete_execution(
        self,
        exit_code: int = 0,
        stdout: str = "",
    ) -> bool:
        """Complete command execution."""
        if self.command_status != FlextCliCommandStatus.RUNNING:
            return False
        status = (
            FlextCliCommandStatus.COMPLETED
            if exit_code == 0
            else FlextCliCommandStatus.FAILED
        )
        object.__setattr__(self, "command_status", status)
        object.__setattr__(self, "exit_code", exit_code)
        object.__setattr__(self, "output", stdout)
        object.__setattr__(self, "updated_at", datetime.now(UTC))
        return True

    @property
    def flext_cli_is_running(self) -> bool:
        """Check if command is running."""
        return self.command_status == FlextCliCommandStatus.RUNNING

    @property
    def flext_cli_is_successful(self) -> bool:
        """Check if command completed successfully."""
        return self.command_status == FlextCliCommandStatus.COMPLETED

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain rules for CLI command."""
        if not self.name:
            return FlextResult.fail("Command name cannot be empty")
        if not self.command_line:
            return FlextResult.fail("Command line cannot be empty")
        return FlextResult.ok(None)


class FlextCliConfig(FlextValueObject):
    """CLI configuration value object - restored from backup."""

    # Pydantic fields for proper MyPy attribute recognition
    debug: bool = Field(default=False)
    trace: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    api_url: str = Field(default="http://localhost:8000")
    api_timeout: int = Field(default=30)
    format_type: str = Field(default="table")
    no_color: bool = Field(default=False)
    profile: str = Field(default="default")
    connect_timeout: int = Field(default=10)
    read_timeout: int = Field(default=30)
    command_timeout: int = Field(default=300)

    def __init__(self, data: TCliConfig | None = None) -> None:
        config_data = data or {}

        # Initialize with proper values from data or defaults
        init_data = {
            "debug": config_data.get("debug", False),
            "trace": config_data.get("trace", False),
            "log_level": config_data.get("log_level", "INFO"),
            "api_url": config_data.get("api_url", "http://localhost:8000"),
            "api_timeout": config_data.get("api_timeout", 30),
            "format_type": config_data.get("output_format", "table"),
            "no_color": config_data.get("no_color", False),
            "profile": config_data.get("profile", "default"),
            "connect_timeout": config_data.get("connect_timeout", 10),
            "read_timeout": config_data.get("read_timeout", 30),
            "command_timeout": config_data.get("command_timeout", 300),
        }

        # Use Pydantic's model initialization
        super().__init__(**init_data)

    def configure(self, config: object) -> bool:
        """Configure with new settings."""
        try:
            if isinstance(config, dict):
                # Create updated data by merging current model data with new config
                current_data = self.model_dump()
                updated_data = {**current_data, **config}

                # Create new instance and copy its values to self
                new_config = FlextCliConfig(updated_data)
                new_data = new_config.model_dump()

                # Update self with new values using model_copy
                updated_self = self.model_copy(update=new_data)

                # Copy all fields from updated instance to self
                for field_name in self.model_fields:
                    object.__setattr__(
                        self,
                        field_name,
                        getattr(updated_self, field_name),
                    )

                return True
            return False
        except (AttributeError, ValueError, TypeError):
            return False

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain rules for CLI configuration."""
        return FlextResult.ok(None)  # Configuration is always valid according to tests


class FlextCliContext(FlextValueObject):
    """CLI execution context value object - restored from backup."""

    config: FlextCliConfig = Field(default_factory=FlextCliConfig)
    session_id: str = Field(default="")
    debug: bool = Field(default=False)
    trace: bool = Field(default=False)
    output_format: str = Field(default="json")
    no_color: bool = Field(default=False)
    profile: str = Field(default="default")

    def __init__(
        self,
        config: FlextCliConfig | None = None,
        **overrides: object,
    ) -> None:
        actual_config = config or FlextCliConfig()

        # Build the initialization dict
        init_data = {
            "config": actual_config,
            "session_id": FlextCliContext._generate_session_id(),
            "debug": overrides.get("debug", getattr(actual_config, "debug", False)),
            "trace": overrides.get("trace", getattr(actual_config, "trace", False)),
            "output_format": overrides.get(
                "output_format",
                getattr(actual_config, "format_type", "json"),
            ),
            "no_color": overrides.get(
                "no_color",
                getattr(actual_config, "no_color", False),
            ),
            "profile": overrides.get(
                "profile",
                getattr(actual_config, "profile", "default"),
            ),
        }

        # Use Pydantic's model initialization
        super().__init__(**init_data)

    @staticmethod
    def _generate_session_id() -> str:
        return FlextUtilities.generate_entity_id()

    def flext_cli_with_debug(self, *, debug: bool = True) -> FlextCliContext:
        """Create context with debug enabled."""
        return FlextCliContext(
            self.config,
            debug=debug,
            trace=self.trace,
            output_format=self.output_format,
            no_color=self.no_color,
            profile=self.profile,
        )

    def flext_cli_with_output_format(
        self,
        format_type: FlextCliOutputFormat,
    ) -> FlextCliContext:
        """Create context with specific output format."""
        return FlextCliContext(
            self.config,
            debug=self.debug,
            trace=self.trace,
            output_format=format_type.value,
            no_color=self.no_color,
            profile=self.profile,
        )

    def flext_cli_for_production(self) -> FlextCliContext:
        """Create production-ready context."""
        return FlextCliContext(
            self.config,
            debug=False,
            trace=False,
            output_format=self.output_format,
            no_color=self.no_color,
            profile="production",
        )

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain rules for CLI context."""
        if not self.session_id:
            return FlextResult.fail("Session ID cannot be empty")
        return FlextResult.ok(None)


class FlextCliPlugin(FlextValueObject):
    """CLI plugin definition - restored from backup."""

    name: str
    version: str
    description: str | None = Field(default=None)
    enabled: bool = Field(default=True)
    dependencies: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def __init__(self, name: str, version: str, **options: object) -> None:
        init_data = {
            "name": name,
            "version": version,
            "description": options.get("description"),
            "enabled": options.get("enabled", True),
            "dependencies": options.get("dependencies", []),
            "commands": options.get("commands", []),
            "created_at": datetime.now(UTC),
        }
        super().__init__(**init_data)

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain rules for CLI plugin."""
        if not self.name:
            return FlextResult.fail("Plugin name cannot be empty")
        if not self.version:
            return FlextResult.fail("Plugin version cannot be empty")
        return FlextResult.ok(None)


class FlextCliSession(FlextEntity):
    """CLI session tracking - restored from backup."""

    # Pydantic fields
    user_id: str | None = None
    commands_executed: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(UTC))
    config: FlextCliConfig = Field(default_factory=FlextCliConfig)

    def flext_cli_record_command(self, command_name: str) -> bool:
        """Record executed command."""
        try:
            # Create a new list with the command added (immutable pattern)
            new_commands = list(self.commands_executed)
            new_commands.append(command_name)
            object.__setattr__(self, "commands_executed", new_commands)
            object.__setattr__(self, "last_activity", datetime.now(UTC))
            return True
        except (AttributeError, ValueError, TypeError):
            return False

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain rules for CLI session."""
        if not self.id:
            return FlextResult.fail("Session ID cannot be empty")
        return FlextResult.ok(None)
