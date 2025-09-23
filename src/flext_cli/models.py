"""FLEXT CLI Models - Single unified class following FLEXT standards.

Provides CLI-specific Pydantic models using flext-core standardization.
Single FlextCliModels class with nested model subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from flext_cli.constants import FlextCliConstants
from flext_core import FlextConfig, FlextResult


class FlextCliModels:
    """Single unified CLI models class following FLEXT standards.

    Contains all Pydantic model subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    class CliConfig(BaseModel):
        """CLI configuration model extending BaseModel."""

        profile: str = Field(default=FlextCliConstants.Defaults.PROFILE)
        output_format: str = Field(default=FlextCliConstants.Defaults.OUTPUT_FORMAT)
        debug_mode: bool = Field(default=False)
        config_dir: Path = Field(
            default_factory=lambda: FlextCliConstants.Defaults.CONFIG_DIR
        )

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate configuration business rules."""
            if not self.profile or not self.profile.strip():
                return FlextResult[None].fail("Profile cannot be empty")

            if self.output_format not in FlextCliConstants.OUTPUT_FORMATS_LIST:
                return FlextResult[None].fail(
                    f"Invalid output format. Valid: {FlextCliConstants.OUTPUT_FORMATS_LIST}"
                )

            return FlextResult[None].ok(None)

    class CliCommand(BaseModel):
        """CLI command model extending BaseModel."""

        id: str = Field(
            default_factory=lambda: f"cmd_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
        )
        command: str = Field(min_length=1)
        args: list[str] = Field(default_factory=list)
        status: str = Field(default=FlextCliConstants.CommandStatus.PENDING.value)
        created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        exit_code: int | None = None
        output: str = Field(default="")
        error_output: str = Field(default="")
        name: str = Field(default="")
        entry_point: str = Field(default="")
        plugin_version: str = Field(default="1.0.0")

        def __init__(
            self,
            command_line: str | None = None,
            execution_time: datetime | None = None,
            name: str | None = None,
            entry_point: str | None = None,
            plugin_version: str | None = None,
            **data: object,
        ) -> None:
            """Initialize with compatibility for command_line and execution_time parameters."""
            if command_line is not None:
                data["command"] = command_line
            if execution_time is not None:
                data["created_at"] = execution_time
            if name is not None:
                data["name"] = name
            if entry_point is not None:
                data["entry_point"] = entry_point
            if plugin_version is not None:
                data["plugin_version"] = plugin_version
            super().__init__(**data)

        @property
        def command_line(self) -> str:
            """Compatibility property for command_line access."""
            return self.command

        @property
        def execution_time(self) -> datetime:
            """Compatibility property for execution_time access."""
            return self.created_at

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate command business rules."""
            if not self.command or not self.command.strip():
                return FlextResult[None].fail("Command line cannot be empty")

            if self.status not in FlextCliConstants.COMMAND_STATUSES_LIST:
                return FlextResult[None].fail(
                    f"Invalid status. Valid: {FlextCliConstants.COMMAND_STATUSES_LIST}"
                )

            return FlextResult[None].ok(None)

        def start_execution(self) -> FlextResult[None]:
            """Start command execution."""
            if self.status != FlextCliConstants.CommandStatus.PENDING.value:
                return FlextResult[None].fail("Command is not in pending state")

            self.status = FlextCliConstants.CommandStatus.RUNNING.value
            return FlextResult[None].ok(None)

        def complete_execution(
            self, exit_code: int, output: str = ""
        ) -> FlextResult[None]:
            """Complete command execution."""
            if self.status != FlextCliConstants.CommandStatus.RUNNING.value:
                return FlextResult[None].fail("Command is not in running state")

            self.exit_code = exit_code
            self.output = output
            self.status = FlextCliConstants.CommandStatus.COMPLETED.value
            return FlextResult[None].ok(None)

    class AuthConfig(BaseModel):
        """Authentication configuration model extending BaseModel."""

        api_url: str = Field(default="http://localhost:8000")
        token_file: Path = Field(
            default_factory=lambda: FlextCliConstants.Defaults.CONFIG_DIR / "token"
        )
        refresh_token_file: Path = Field(
            default_factory=lambda: FlextCliConstants.Defaults.CONFIG_DIR
            / "refresh_token"
        )
        auto_refresh: bool = Field(default=True)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate auth configuration business rules."""
            if not self.api_url or not self.api_url.strip():
                return FlextResult[None].fail("API URL cannot be empty")

            if not self.api_url.startswith(("http://", "https://")):
                return FlextResult[None].fail(
                    "API URL must start with http:// or https://"
                )

            return FlextResult[None].ok(None)

    class DebugInfo(BaseModel):
        """Debug information model extending BaseModel."""

        service: str = Field(default="FlextCliDebug")
        status: str = Field(default="operational")
        timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
        system_info: dict[str, str] = Field(default_factory=dict)
        config_info: dict[str, str] = Field(default_factory=dict)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate debug info business rules."""
            if not self.service or not self.service.strip():
                return FlextResult[None].fail("Service name cannot be empty")

            return FlextResult[None].ok(None)

    class LoggingConfig(BaseModel):
        """Logging configuration model extending BaseModel."""

        log_level: str = Field(default=FlextCliConstants.Defaults.LOG_LEVEL)
        log_format: str = Field(
            default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_output: bool = Field(default=True)
        log_file: Path | None = Field(default=None)
        log_level_source: str = Field(default="default")

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate logging configuration business rules."""
            if self.log_level not in FlextCliConstants.LOG_LEVELS_LIST:
                return FlextResult[None].fail(
                    f"Invalid log level. Valid: {FlextCliConstants.LOG_LEVELS_LIST}"
                )

            return FlextResult[None].ok(None)

    class FormatOptions(BaseModel):
        """Format options for CLI output extending BaseModel."""

        title: str | None = None
        headers: list[str] | None = None
        show_lines: bool = True
        max_width: int | None = None

    class CliOptions(BaseModel):
        """CLI options configuration model extending BaseModel."""

        output_format: str = Field(default=FlextCliConstants.Defaults.OUTPUT_FORMAT)
        verbose: bool = False
        debug: bool = False
        no_color: bool = False
        max_width: int = FlextCliConstants.Defaults.MAX_WIDTH
        config_file: Path | None = None

    class FlextCliConfig(FlextConfig):
        """Main CLI configuration class extending FlextConfig.

        Provides unified configuration management for the FLEXT CLI ecosystem
        using Pydantic Settings for environment variable support.
        Inherits core configuration from FlextConfig.
        """

        model_config = SettingsConfigDict(
            env_prefix="FLEXT_CLI_",
            case_sensitive=False,
            extra="allow",
        )

        # CLI-specific configuration fields (inherits debug, timeout_seconds from FlextConfig)
        profile: str = Field(default=FlextCliConstants.Defaults.PROFILE)
        output_format: str = Field(default=FlextCliConstants.Defaults.OUTPUT_FORMAT)
        no_color: bool = Field(default=False)
        config_dir: Path = Field(default_factory=lambda: FlextCliConstants.Defaults.CONFIG_DIR)

        # Test compatibility fields
        project_name: str = Field(default="flext-cli")
        database_url: str = Field(default="postgresql://localhost:5432/flext_cli")
        cache_enabled: bool = Field(default=True)
        api_timeout: int = Field(default=30)
        max_connections: int = Field(default=10)

        @property
        def debug_mode(self) -> bool:
            """Alias for debug field from FlextConfig."""
            return self.debug

        def get_config_dir(self) -> Path:
            """Get the configuration directory."""
            return FlextCliConstants.Defaults.CONFIG_DIR

        def get_config_file(self) -> Path:
            """Get the main configuration file path."""
            return self.get_config_dir() / FlextCliConstants.Defaults.CONFIG_FILE

        def validate_output_format(self, format_type: str) -> FlextResult[str]:
            """Validate output format."""
            if format_type not in FlextCliConstants.OUTPUT_FORMATS_LIST:
                return FlextResult[str].fail(
                    f"Invalid output format: {format_type}. "
                     f"Valid formats: {', '.join(FlextCliConstants.OUTPUT_FORMATS_LIST)}"
                )
            return FlextResult[str].ok(format_type)

        def is_debug_enabled(self) -> bool:
            """Check if debug mode is enabled."""
            return self.debug

        def get_output_format(self) -> str:
            """Get the current output format."""
            return self.output_format

        def set_output_format(self, format_type: str) -> FlextResult[None]:
            """Set the output format."""
            validation_result = self.validate_output_format(format_type)
            if validation_result.is_failure:
                return FlextResult[None].fail(
                    validation_result.error or "Output format validation failed"
                )

            self.output_format = validation_result.unwrap()
            return FlextResult[None].ok(None)

        def create_cli_options(self) -> FlextCliModels.CliOptions:
            """Create CLI options from current configuration."""
            return FlextCliModels.CliOptions(
                output_format=self.output_format,
                debug=self.debug,
                max_width=FlextCliConstants.Defaults.MAX_WIDTH,
                no_color=self.no_color,
        )

        @classmethod
        def create_default(cls) -> FlextCliModels.FlextCliConfig:
            """Create default CLI configuration."""
            return cls(
                profile=FlextCliConstants.Defaults.PROFILE,
                output_format=FlextCliConstants.Defaults.OUTPUT_FORMAT,
                debug=False,
            )

        def load_configuration(self) -> FlextResult[dict[str, object]]:
            """Load configuration data from current settings.

            Returns:
                FlextResult[dict[str, object]]: Configuration data or error

            """
            try:
                config_data: dict[str, object] = {
                    "profile": self.profile,
                    "output_format": self.output_format,
                    "debug_mode": self.debug,
                    "debug": self.debug,
                    "project_name": self.project_name,
                    "database_url": self.database_url,
                    "cache_enabled": self.cache_enabled,
                    "api_timeout": self.api_timeout,
                    "max_connections": self.max_connections,
                    "timeout_seconds": self.timeout_seconds,
                    "no_color": self.no_color,
                    "config_dir": str(self.get_config_dir()),
                    "config_file": str(self.get_config_file()),
                }
                return FlextResult[dict[str, object]].ok(config_data)
            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Configuration load failed: {e}"
                )

    class CliSession(BaseModel):
        """CLI session model extending BaseModel."""

        id: str = Field(
            default_factory=lambda: f"session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        )
        session_id: str = Field(
            default_factory=lambda: f"session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        )
        start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
        end_time: datetime | None = None
        duration_seconds: float = Field(default=0.0)
        commands_executed: int = Field(default=0)
        status: str = Field(default="active")
        user_id: str | None = None

        def __init__(
            self,
            session_id: str | None = None,
            user_id: str | None = None,
            start_time: datetime | None = None,
            **data: object,
        ) -> None:
            """Initialize with compatibility for session_id, user_id, and start_time parameters."""
            if session_id is not None:
                data["id"] = session_id
                data["session_id"] = session_id
            if start_time is not None:
                data["start_time"] = start_time
            if user_id is not None:
                data["user_id"] = user_id
            super().__init__(**data)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate session business rules."""
            if not self.id or not self.id.strip():
                return FlextResult[None].fail("Session ID cannot be empty")

            if self.status not in {"active", "completed", "terminated"}:
                return FlextResult[None].fail(
                    "Invalid status. Valid: active, completed, terminated"
                )

            return FlextResult[None].ok(None)

    class CliFormatters(BaseModel):
        """CLI formatters model extending BaseModel."""

        def list_formats(self) -> list[str]:
            """List available output formats."""
            return ["json", "yaml", "csv", "table", "plain"]

    class Pipeline(BaseModel):
        """Pipeline model for CLI operations extending BaseModel."""

        id: str = Field(
            default_factory=lambda: f"pipeline_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        )
        name: str = Field(min_length=1)
        description: str = Field(default="")
        status: str = Field(default=FlextCliConstants.CommandStatus.PENDING.value)
        created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        steps: list[dict[str, Any]] = Field(default_factory=list)
        config: dict[str, object] = Field(default_factory=dict)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate pipeline business rules."""
            if not self.name or not self.name.strip():
                return FlextResult[None].fail("Pipeline name cannot be empty")

            if self.status not in FlextCliConstants.COMMAND_STATUSES_LIST:
                return FlextResult[None].fail(
                    f"Invalid status. Valid: {FlextCliConstants.COMMAND_STATUSES_LIST}"
                )

            return FlextResult[None].ok(None)

        def add_step(self, step: dict[str, object]) -> FlextResult[None]:
            """Add a step to the pipeline."""
            if not step or not isinstance(step, dict):
                return FlextResult[None].fail("Step must be a non-empty dictionary")

            self.steps.append(step)
            self.updated_at = datetime.now(UTC)
            return FlextResult[None].ok(None)

        def update_status(self, new_status: str) -> FlextResult[None]:
            """Update pipeline status."""
            if new_status not in FlextCliConstants.COMMAND_STATUSES_LIST:
                return FlextResult[None].fail(
                    f"Invalid status. Valid: {FlextCliConstants.COMMAND_STATUSES_LIST}"
                )

            self.status = new_status
            self.updated_at = datetime.now(UTC)
            return FlextResult[None].ok(None)

    class PipelineConfig(BaseModel):
        """Pipeline configuration model extending BaseModel."""

        name: str = Field(min_length=1)
        description: str = Field(default="")
        steps: list[dict[str, Any]] = Field(default_factory=list)
        config: dict[str, object] = Field(default_factory=dict)
        enabled: bool = Field(default=True)
        timeout_seconds: int = Field(default=300)
        retry_count: int = Field(default=3)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate pipeline configuration business rules."""
            if not self.name or not self.name.strip():
                return FlextResult[None].fail("Pipeline name cannot be empty")

            if self.timeout_seconds <= 0:
                return FlextResult[None].fail("Timeout must be positive")

            if self.retry_count < 0:
                return FlextResult[None].fail("Retry count cannot be negative")

            return FlextResult[None].ok(None)

        def add_step(self, step: dict[str, object]) -> FlextResult[None]:
            """Add a step to the pipeline configuration."""
            if not step or not isinstance(step, dict):
                return FlextResult[None].fail("Step must be a non-empty dictionary")

            self.steps.append(step)
            return FlextResult[None].ok(None)


__all__ = [
    "FlextCliModels",
]
