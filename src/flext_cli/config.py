"""FLEXT CLI Configuration - Single unified class following FLEXT standards.

Provides unified configuration management for the FLEXT CLI ecosystem
using Pydantic Settings for environment variable support.
Single FlextCliConfig class with nested configuration subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import yaml
from pydantic import (
    BaseModel,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)

from flext_cli.constants import FlextCliConstants
from flext_core import (
    FlextConfig,
    FlextResult,
    FlextService,
)


class LoggingConfig(BaseModel):
    """Logging configuration model."""

    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )
    console_output: bool = Field(default=True, description="Enable console output")
    log_file: str | None = Field(default=None, description="Log file path")
    log_level_source: str = Field(default="default", description="Source of log level")


class FlextCliConfig(FlextConfig):
    """Single Pydantic 2 Settings class for flext-cli extending FlextConfig.

    Follows standardized pattern:
    - Extends FlextConfig from flext-core
    - No nested classes within Config
    - All defaults from FlextCliConstants
    - Dependency injection integration with flext-core container
    - Uses Pydantic 2.11+ features (SecretStr for secrets)
    """

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


class FlextCliConfigService(FlextService):
    """Service class for FlextCliConfig operations."""

    def __init__(self) -> None:
        """Initialize config service."""
        super().__init__()
        self._config = FlextCliConfig.create()

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute config service operation."""
        return FlextResult[dict[str, object]].ok({
            "status": "operational",
            "service": "flext-cli-config",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
            "config": self._config.model_dump(),
        })

    async def execute_async(self) -> FlextResult[dict[str, object]]:
        """Execute config service operation asynchronously."""
        return FlextResult[dict[str, object]].ok({
            "status": "operational",
            "service": "flext-cli-config",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
            "config": self._config.model_dump(),
        })


__all__ = [
    "FlextCliConfig",
    "FlextCliConfigService",
    "LoggingConfig",
]
