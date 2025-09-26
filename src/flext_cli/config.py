"""FLEXT CLI Configuration - Single unified class following FLEXT standards.

Provides unified configuration management for the FLEXT CLI ecosystem
using Pydantic Settings for environment variable support.
Single FlextCliConfig class with nested configuration subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, override

import yaml
from pydantic import (
    Field,
    SecretStr,
    field_validator,
    model_validator,
)

from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_core import (
    FlextConfig,
    FlextResult,
    FlextService,
)


class FlextCliConfig(FlextConfig):
    """Single flat Pydantic 2 Settings class for flext-cli extending FlextConfig.

    Follows standardized pattern:
    - Extends FlextConfig from flext-core
    - Flat class structure (no nested classes)
    - All defaults from FlextCliConstants
    - SecretStr for sensitive data
    - Singleton pattern with shared dependency injection
    """

    # Singleton pattern attributes
    _global_instance: ClassVar[FlextCliConfig | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    class MainConfig(FlextCliModels.FlextCliConfig):
        """Main configuration settings for CLI operations extending FlextCliModels.FlextCliConfig."""

        debug: bool = Field(default=False, description="Enable debug mode")
        debug_mode: bool = Field(default=False, description="Enable debug mode (alias)")
        app_name: str = Field(default="flext-cli", description="Application name")
        version: str = Field(default="2.0.0", description="Application version")
        profile: str = Field(default="default", description="Configuration profile")
        output_format: str = Field(default="table", description="Default output format")
        log_level: str = Field(default="INFO", description="Logging level")
        config_dir: str = Field(
            default="~/.flext", description="Configuration directory"
        )

        def validate_output_format(self, value: str) -> FlextResult[str]:
            """Validate output format and return FlextResult."""
            valid_formats = ["json", "yaml", "csv", "table", "plain"]
            if value not in valid_formats:
                return FlextResult[str].fail(f"Invalid output format: {value}")
            return FlextResult[str].ok(value)

    class CliOptions:
        """CLI-specific options and settings."""

        verbose: bool = False
        quiet: bool = False
        interactive: bool = True

    # CLI-specific configuration fields using FlextCliConstants for defaults
    profile: str = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_PROFILE,
        description="CLI profile to use for configuration",
    )

    output_format: str = Field(
        default=FlextCliConstants.OutputFormats.TABLE,
        description="Default output format for CLI commands",
    )

    no_color: bool = Field(default=False, description="Disable colored output in CLI")

    config_dir: Path = Field(
        default_factory=lambda: Path.home() / FlextCliConstants.FLEXT_DIR_NAME,
        description="Configuration directory path",
    )

    project_name: str = Field(
        default=FlextCliConstants.PROJECT_NAME,
        description="Project name for CLI operations",
    )

    # Authentication configuration using SecretStr for sensitive data
    api_url: str = Field(
        default=FlextCliConstants.NetworkDefaults.DEFAULT_API_URL,
        description="API URL for remote operations",
    )

    cli_api_key: SecretStr | None = Field(
        default=None, description="API key for authentication (sensitive)"
    )

    token_file: Path = Field(
        default_factory=lambda: Path.home()
        / FlextCliConstants.FLEXT_DIR_NAME
        / FlextCliConstants.TOKEN_FILE_NAME,
        description="Path to authentication token file",
    )

    refresh_token_file: Path = Field(
        default_factory=lambda: Path.home()
        / FlextCliConstants.FLEXT_DIR_NAME
        / FlextCliConstants.REFRESH_TOKEN_FILE_NAME,
        description="Path to refresh token file",
    )

    auto_refresh: bool = Field(
        default=True, description="Automatically refresh authentication tokens"
    )

    # CLI behavior configuration
    verbose: bool = Field(default=False, description="Enable verbose output")

    max_width: int = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_MAX_WIDTH,
        ge=40,
        le=200,
        description="Maximum width for CLI output",
    )

    config_file: Path | None = Field(
        default=None, description="Custom configuration file path"
    )

    # Network configuration
    timeout: int = Field(
        default=FlextCliConstants.NetworkDefaults.DEFAULT_TIMEOUT,
        ge=1,
        le=300,
        description="Network timeout in seconds",
    )

    max_retries: int = Field(
        default=FlextCliConstants.NetworkDefaults.DEFAULT_MAX_RETRIES,
        ge=0,
        le=10,
        description="Maximum number of retry attempts",
    )

    # Logging configuration - centralized for all FLEXT projects
    log_level: str = Field(
        default="INFO",
        description="Global logging level for FLEXT projects",
    )

    log_verbosity: str = Field(
        default="detailed",
        description="Logging verbosity (compact, detailed, full)",
    )

    cli_log_level: str = Field(
        default="INFO",
        description="CLI-specific logging level",
    )

    cli_log_verbosity: str = Field(
        default="detailed",
        description="CLI-specific logging verbosity",
    )

    log_file: str | None = Field(
        default=None,
        description="Optional log file path for persistent logging",
    )

    # Pydantic 2.11 field validators
    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        """Validate output format is one of the allowed values."""
        if v not in FlextCliConstants.OUTPUT_FORMATS_LIST:
            valid_formats = ", ".join(FlextCliConstants.OUTPUT_FORMATS_LIST)
            msg = f"Invalid output format: {v}. Must be one of: {valid_formats}"
            raise ValueError(msg)
        return v

    @field_validator("profile")
    @classmethod
    def validate_profile(cls, v: str) -> str:
        """Validate profile name is not empty."""
        if not v or not v.strip():
            msg = "Profile name cannot be empty"
            raise ValueError(msg)
        return v.strip()

    @field_validator("api_url")
    @classmethod
    def validate_api_url(cls, v: str) -> str:
        """Validate API URL format."""
        if not v.startswith(("http://", "https://")):
            msg = f"Invalid API URL format: {v}. Must start with http:// or https://"
            raise ValueError(msg)
        return v

    @field_validator("log_level", "cli_log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        level_upper = v.upper()
        if level_upper not in valid_levels:
            msg = f"Invalid log level: {v}. Must be one of: {', '.join(valid_levels)}"
            raise ValueError(msg)
        return level_upper

    @field_validator("log_verbosity", "cli_log_verbosity")
    @classmethod
    def validate_log_verbosity(cls, v: str) -> str:
        """Validate log verbosity is one of the allowed values."""
        valid_verbosity = {"compact", "detailed", "full"}
        verbosity_lower = v.lower()
        if verbosity_lower not in valid_verbosity:
            msg = f"Invalid log verbosity: {v}. Must be one of: {', '.join(valid_verbosity)}"
            raise ValueError(msg)
        return verbosity_lower

    @model_validator(mode="after")
    def validate_paths(self) -> FlextCliConfig:
        """Validate that configuration paths are accessible."""
        # Ensure config directory exists or can be created
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            msg = f"Cannot access config directory {self.config_dir}: {e}"
            raise ValueError(msg) from e

        return self

    # CLI-specific methods
    def get_cli_context(self) -> dict[str, object]:
        """Get CLI context for command execution."""
        return {
            "profile": self.profile,
            "output_format": self.output_format,
            "no_color": self.no_color,
            "verbose": self.verbose,
            "max_width": self.max_width,
            "api_url": self.api_url,
            "timeout": self.timeout,
            "log_level": self.log_level,
            "log_verbosity": self.log_verbosity,
            "cli_log_level": self.cli_log_level,
            "cli_log_verbosity": self.cli_log_verbosity,
        }

    def get_auth_context(self) -> dict[str, object]:
        """Get authentication context (without exposing secrets)."""
        return {
            "api_url": self.api_url,
            "token_file": str(self.token_file),
            "refresh_token_file": str(self.refresh_token_file),
            "auto_refresh": self.auto_refresh,
            "api_key_configured": self.cli_api_key is not None,
        }

    def get_logging_context(self) -> dict[str, object]:
        """Get logging context for centralized logging configuration."""
        return {
            "log_level": self.log_level,
            "log_verbosity": self.log_verbosity,
            "cli_log_level": self.cli_log_level,
            "cli_log_verbosity": self.cli_log_verbosity,
            "log_file": str(self.log_file) if self.log_file else None,
        }

    @classmethod
    def create_for_profile(cls, profile: str, **kwargs: object) -> FlextCliConfig:
        """Create configuration for specific profile."""
        return cls(profile=profile, **kwargs)

    @classmethod
    def load_from_config_file(cls, config_file: Path) -> FlextResult[FlextCliConfig]:
        """Load configuration from file with proper error handling."""
        try:
            if not config_file.exists():
                return FlextResult[FlextCliConfig].fail(
                    f"Configuration file not found: {config_file}"
                )

            # Load based on file extension
            if config_file.suffix.lower() == ".json":
                with config_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            elif config_file.suffix.lower() in {".yml", ".yaml"}:
                if yaml is None:
                    return FlextResult[FlextCliConfig].fail(
                        "PyYAML not installed. Cannot load YAML configuration."
                    )
                with config_file.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            else:
                return FlextResult[FlextCliConfig].fail(
                    f"Unsupported configuration file format: {config_file.suffix}"
                )

            config = cls(**data)
            return FlextResult[FlextCliConfig].ok(config)

        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to load configuration from {config_file}: {e}"
            )

    # Singleton pattern override for proper typing
    @classmethod
    def get_global_instance(cls) -> FlextCliConfig:
        """Get the global singleton instance of FlextCliConfig."""
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = cls()
        return cls._global_instance

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextCliConfig instance (mainly for testing)."""
        cls._global_instance = None


class FlextCliConfigService(FlextService):
    """Service class for FlextCliConfig operations."""

    @override
    @override
    def __init__(self) -> None:
        """Initialize config service."""
        super().__init__()
        self._config = FlextCliConfig.create()

    @override
    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute config service operation."""
        return FlextResult[dict[str, object]].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": "flext-cli-config",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
            "config": self._config.model_dump(),
        })

    async def execute_async(self) -> FlextResult[dict[str, object]]:
        """Execute config service operation asynchronously."""
        return FlextResult[dict[str, object]].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": "flext-cli-config",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
            "config": self._config.model_dump(),
        })


__all__ = [
    "FlextCliConfig",
    "FlextCliConfigService",
]
