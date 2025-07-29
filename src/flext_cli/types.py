"""Type definitions for FLEXT CLI with full backup functionality restored.

Based on the original backup - all types and interfaces restored.
Following strict naming conventions: FlextCli*, TCli*, flext_cli_*
"""

from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from flext_core.entities import FlextEntity
from flext_core.types import TValue
from flext_core.value_objects import FlextValueObject
from pydantic import Field

# Core data types
type TCliData = TValue
type TCliPath = str | Path
type TCliFormat = str
type TCliHandler = Callable[..., Any]
type TCliConfig = dict[str, Any]
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
    options: dict[str, Any] = Field(default_factory=dict)
    command_status: FlextCliCommandStatus = FlextCliCommandStatus.PENDING
    command_type: FlextCliCommandType = FlextCliCommandType.SYSTEM
    updated_at: datetime = Field(default_factory=datetime.now)
    exit_code: int | None = None
    output: str = ""

    def flext_cli_start_execution(self) -> bool:
        """Start command execution."""
        if self.command_status != FlextCliCommandStatus.PENDING:
            return False
        self.command_status = FlextCliCommandStatus.RUNNING
        self.updated_at = datetime.now()
        return True

    def flext_cli_complete_execution(
        self,
        exit_code: int = 0,
        stdout: str = "",
    ) -> bool:
        """Complete command execution."""
        if self.command_status != FlextCliCommandStatus.RUNNING:
            return False
        self.command_status = (
            FlextCliCommandStatus.COMPLETED
            if exit_code == 0
            else FlextCliCommandStatus.FAILED
        )
        self.exit_code = exit_code
        self.output = stdout
        self.updated_at = datetime.now()
        return True

    @property
    def flext_cli_is_running(self) -> bool:
        """Check if command is running."""
        return self.command_status == FlextCliCommandStatus.RUNNING

    @property
    def flext_cli_is_successful(self) -> bool:
        """Check if command completed successfully."""
        return self.command_status == FlextCliCommandStatus.COMPLETED

    def validate_domain_rules(self) -> bool:
        """Validate domain rules for CLI command."""
        return bool(self.name and self.command_line)


class FlextCliConfig(FlextValueObject):
    """CLI configuration value object - restored from backup."""

    def __init__(self, data: TCliConfig | None = None) -> None:
        super().__init__()
        config_data = data or {}

        # Configuration from original backup
        object.__setattr__(self, "debug", config_data.get("debug", False))
        object.__setattr__(self, "trace", config_data.get("trace", False))
        object.__setattr__(self, "log_level", config_data.get("log_level", "INFO"))
        object.__setattr__(
            self,
            "api_url",
            config_data.get("api_url", "http://localhost:8000"),
        )
        object.__setattr__(self, "api_timeout", config_data.get("api_timeout", 30))
        object.__setattr__(
            self,
            "format_type",
            config_data.get("output_format", "table"),
        )
        object.__setattr__(self, "no_color", config_data.get("no_color", False))
        object.__setattr__(self, "profile", config_data.get("profile", "default"))
        object.__setattr__(
            self,
            "connect_timeout",
            config_data.get("connect_timeout", 10),
        )
        object.__setattr__(self, "read_timeout", config_data.get("read_timeout", 30))
        object.__setattr__(
            self,
            "command_timeout",
            config_data.get("command_timeout", 300),
        )

    def configure(self, config: Any) -> bool:
        """Configure with new settings."""
        try:
            if isinstance(config, dict):
                # Create new instance with updated config
                updated_data = {**self.__dict__, **config}
                new_config = FlextCliConfig(updated_data)
                # Copy attributes
                for key, value in new_config.__dict__.items():
                    object.__setattr__(self, key, value)
                return True
            return False
        except Exception:
            return False

    def validate_domain_rules(self) -> bool:
        """Validate domain rules for CLI configuration."""
        return True  # Configuration is always valid


class FlextCliContext(FlextValueObject):
    """CLI execution context value object - restored from backup."""

    def __init__(self, config: FlextCliConfig | None = None, **overrides: Any) -> None:
        super().__init__()
        self.config = config or FlextCliConfig()

        # Context properties from original backup
        object.__setattr__(self, "session_id", self._generate_session_id())
        object.__setattr__(self, "debug", overrides.get("debug", self.config.debug))
        object.__setattr__(self, "trace", overrides.get("trace", self.config.trace))
        object.__setattr__(
            self,
            "output_format",
            overrides.get("output_format", self.config.format_type),
        )
        object.__setattr__(
            self,
            "no_color",
            overrides.get("no_color", self.config.no_color),
        )
        object.__setattr__(
            self,
            "profile",
            overrides.get("profile", self.config.profile),
        )

    def _generate_session_id(self) -> str:
        from flext_core.utilities import FlextUtilities

        return FlextUtilities.generate_entity_id()

    def flext_cli_with_debug(self, debug: bool = True) -> "FlextCliContext":
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
    ) -> "FlextCliContext":
        """Create context with specific output format."""
        return FlextCliContext(
            self.config,
            debug=self.debug,
            trace=self.trace,
            output_format=format_type.value,
            no_color=self.no_color,
            profile=self.profile,
        )

    def flext_cli_for_production(self) -> "FlextCliContext":
        """Create production-ready context."""
        return FlextCliContext(
            self.config,
            debug=False,
            trace=False,
            output_format=self.output_format,
            no_color=self.no_color,
            profile="production",
        )

    def validate_domain_rules(self) -> bool:
        """Validate domain rules for CLI context."""
        return bool(self.session_id)


class FlextCliPlugin(FlextValueObject):
    """CLI plugin definition - restored from backup."""

    def __init__(self, name: str, version: str, **options: Any) -> None:
        super().__init__()
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "description", options.get("description"))
        object.__setattr__(self, "enabled", options.get("enabled", True))
        object.__setattr__(self, "dependencies", options.get("dependencies", []))
        object.__setattr__(self, "commands", options.get("commands", []))
        object.__setattr__(self, "created_at", datetime.now())

    def validate_domain_rules(self) -> bool:
        """Validate domain rules for CLI plugin."""
        return bool(self.name and self.version)


class FlextCliSession(FlextEntity):
    """CLI session tracking - restored from backup."""

    # Pydantic fields
    user_id: str | None = None
    commands_executed: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    config: FlextCliConfig = Field(default_factory=FlextCliConfig)

    def flext_cli_record_command(self, command_name: str) -> bool:
        """Record executed command."""
        try:
            self.commands_executed.append(command_name)
            self.last_activity = datetime.now()
            return True
        except Exception:
            return False

    def validate_domain_rules(self) -> bool:
        """Validate domain rules for CLI session."""
        return bool(self.entity_id)
