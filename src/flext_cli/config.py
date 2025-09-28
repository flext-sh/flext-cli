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
from typing import cast

import yaml
from pydantic import (
    Field,
    SecretStr,
    field_validator,
    model_validator,
)
from pydantic_settings import SettingsConfigDict

from flext_cli.constants import FlextCliConstants
from flext_core import (
    FlextConfig,
    FlextResult,
)


class FlextCliConfig(FlextConfig):
    """Single flat Pydantic 2 Settings class for flext-cli extending FlextConfig.

    Implements FlextCliProtocols.CliConfigProvider through structural subtyping.

    Follows standardized pattern:
    - Extends FlextConfig from flext-core directly (no nested classes)
    - Flat class structure with all fields at top level
    - All defaults from FlextCliConstants
    - SecretStr for sensitive data
    - Uses enhanced singleton pattern with inverse dependency injection
    - Uses Python 3.13 + Pydantic 2 features
    """

    # Class variable for singleton pattern
    _shared_instance: FlextCliConfig | None = None

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        case_sensitive=False,
        extra="allow",
        # Inherit enhanced Pydantic 2.11+ features from FlextConfig
        validate_assignment=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "title": "FLEXT CLI Configuration",
            "description": "Enterprise CLI configuration extending FlextConfig",
        },
    )

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

    # CLI behavior configuration (flattened from previous nested classes)
    verbose: bool = Field(default=False, description="Enable verbose output")
    debug: bool = Field(default=False, description="Enable debug mode")
    debug_mode: bool = Field(default=False, description="Enable debug mode (alias)")
    app_name: str = Field(default="flext-cli", description="Application name")
    version: str = Field(default="2.0.0", description="Application version")
    quiet: bool = Field(default=False, description="Enable quiet mode")
    interactive: bool = Field(default=True, description="Enable interactive mode")

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
            "debug": self.debug,
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

    def validate_output_format_result(self, value: str) -> FlextResult[str]:
        """Validate output format and return FlextResult."""
        valid_formats = ["json", "yaml", "csv", "table", "plain"]
        if value not in valid_formats:
            return FlextResult[str].fail(f"Invalid output format: {value}")
        return FlextResult[str].ok(value)

    @classmethod
    def create_for_environment(
        cls, environment: str, **overrides: object
    ) -> FlextCliConfig:
        """Create configuration for specific environment using enhanced singleton pattern."""
        config = cls.get_or_create_shared_instance(
            project_name="flext-cli", environment=environment, **overrides
        )
        return cast("FlextCliConfig", config)

    @classmethod
    def create_default(cls) -> FlextCliConfig:
        """Create default configuration instance using enhanced singleton pattern."""
        config = cls.get_or_create_shared_instance(project_name="flext-cli")
        return cast("FlextCliConfig", config)

    @classmethod
    def create_for_profile(cls, profile: str, **kwargs: object) -> FlextCliConfig:
        """Create configuration for specific profile using enhanced singleton pattern."""
        config = cls.get_or_create_shared_instance(
            project_name="flext-cli", profile=profile, **kwargs
        )
        return cast("FlextCliConfig", config)

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
                with config_file.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            else:
                return FlextResult[FlextCliConfig].fail(
                    f"Unsupported configuration file format: {config_file.suffix}"
                )

            # Use enhanced singleton pattern with loaded data
            config = cls.get_or_create_shared_instance(project_name="flext-cli", **data)
            return FlextResult[FlextCliConfig].ok(cast("FlextCliConfig", config))

        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to load configuration from {config_file}: {e}"
            )

    @classmethod
    def get_global_instance(cls) -> FlextCliConfig:
        """Get the global singleton instance using enhanced FlextConfig pattern."""
        # Get the parent global instance
        parent_config = super().get_global_instance()

        # If it's already a FlextCliConfig, return it
        if isinstance(parent_config, FlextCliConfig):
            return parent_config

        # Otherwise, create a new FlextCliConfig instance with the parent's data
        # This ensures we have all the CLI-specific fields
        config_data = (
            parent_config.model_dump() if hasattr(parent_config, "model_dump") else {}
        )
        return cls(**config_data)

    @classmethod
    def reset_shared_instance(cls) -> None:
        """Reset the shared instance for testing purposes."""
        # Reset the singleton instance
        cls._shared_instance = None

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextCliConfig instance (mainly for testing)."""
        cls.reset_shared_instance()
        # Use the enhanced FlextConfig reset mechanism

    # Service operations (previously FlextCliConfigService) - unified pattern
    class _ConfigServiceHelper:
        """Nested helper class for config service operations."""

        @staticmethod
        def execute_service_operation(
            config: FlextCliConfig,
        ) -> FlextResult[dict[str, object]]:
            """Execute config service operation."""
            return FlextResult[dict[str, object]].ok({
                "status": FlextCliConstants.OPERATIONAL,
                "service": "flext-cli-config",
                "timestamp": datetime.now(UTC).isoformat(),
                "version": "2.0.0",
                "config": config.model_dump(),
            })

        @staticmethod
        def load_config_from_file(config_path: str) -> FlextResult[FlextCliConfig]:
            """Load configuration from file."""
            try:
                path = Path(config_path)
                if not path.exists():
                    return FlextResult[FlextCliConfig].fail(
                        f"Config file not found: {config_path}"
                    )

                with path.open("r", encoding="utf-8") as f:
                    config_data = json.load(f)

                config = FlextCliConfig.model_validate(config_data)
                return FlextResult[FlextCliConfig].ok(config)
            except Exception as e:
                return FlextResult[FlextCliConfig].fail(f"Failed to load config: {e}")

        @staticmethod
        def save_config_to_file(
            config_path: str, config: FlextCliConfig
        ) -> FlextResult[None]:
            """Save configuration to file."""
            try:
                path = Path(config_path)
                path.parent.mkdir(parents=True, exist_ok=True)

                # Convert model to dict and ensure all values are JSON serializable
                config_dict = config.model_dump()
                # Convert any Path objects to strings
                for key, value in config_dict.items():
                    if isinstance(value, Path):
                        config_dict[key] = str(value)

                with path.open("w", encoding="utf-8") as f:
                    json.dump(config_dict, f, indent=2)

                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Failed to save config: {e}")

    def execute_as_service(self) -> FlextResult[dict[str, object]]:
        """Execute config as service operation using nested helper."""
        return self._ConfigServiceHelper.execute_service_operation(self)

    def load_config_file(self, config_path: str) -> FlextResult[FlextCliConfig]:
        """Load configuration from file using nested helper."""
        return self._ConfigServiceHelper.load_config_from_file(config_path)

    def save_config_file(self, config_path: str) -> FlextResult[None]:
        """Save configuration to file using nested helper."""
        return self._ConfigServiceHelper.save_config_to_file(config_path, self)

    # Protocol-compliant methods for CliConfigProvider
    def load_config(self) -> FlextResult[dict[str, object]]:
        """Load CLI configuration - implements CliConfigProvider protocol.

        Returns:
            FlextResult[dict[str, object]]: Configuration data or error

        """
        try:
            # Convert model to dictionary format expected by protocol
            config_data = self.model_dump()
            return FlextResult[dict[str, object]].ok(config_data)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Config load failed: {e}")

    def save_config(self, config: dict[str, object]) -> FlextResult[None]:
        """Save CLI configuration - implements CliConfigProvider protocol.

        Args:
            config: Configuration data to save

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            # Update model fields with provided config data
            for key, value in config.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            # Validate the updated configuration
            self.model_validate(self.model_dump())
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Config save failed: {e}")


# Merged into FlextCliConfig - removed redundant class


# Service functionality merged into FlextCliConfig - removed redundant class


__all__ = [
    "FlextCliConfig",
]
