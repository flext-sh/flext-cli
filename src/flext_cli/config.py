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
from flext_core import (
    FlextConfig,
    FlextResult,
)
from pydantic import (
    Field,
    SecretStr,
    field_validator,
    model_validator,
)
from pydantic_settings import SettingsConfigDict

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes


class FlextCliConfig(FlextConfig):
    """Single flat Pydantic 2 Settings class for flext-cli extending FlextConfig.

    Implements FlextCliProtocols.CliConfigProvider through structural subtyping.

    Follows standardized pattern:
    - Extends FlextConfig from flext-core directly (no nested classes)
    - Flat class structure with all fields at top level
    - All defaults from FlextCliConstants
    - SecretStr for sensitive data
    - Uses FlextConfig features for configuration management
    - Uses Python 3.13 + Pydantic 2 features
    """

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
    def validate_configuration(self) -> FlextCliConfig:
        """Validate configuration using FlextConfig validation and custom rules."""
        # Use FlextConfig business rules validation
        validation_result = self.validate_business_rules()
        if validation_result.is_failure:
            msg = f"Business rules validation failed: {validation_result.error}"
            raise ValueError(msg)

        # Ensure config directory exists or can be created
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            msg = f"Cannot access config directory {self.config_dir}: {e}"
            raise ValueError(msg) from e

        return self

    # CLI-specific methods
    def get_cli_context(self) -> FlextCliTypes.Data.CliDataDict:
        """REMOVED: Access config attributes directly.

        Migration:
            # Old pattern
            cli_context = config.get_cli_context()
            profile = cli_context["profile"]

            # New pattern - direct attribute access
            cli_context = {
                "profile": config.profile,
                "output_format": config.output_format,
                "no_color": config.no_color,
                "verbose": config.verbose,
                "debug": config.debug,
                "max_width": config.max_width,
                "api_url": config.api_url,
                "timeout": config.timeout,
                "log_level": config.log_level,
                "log_verbosity": config.log_verbosity,
                "cli_log_level": config.cli_log_level,
                "cli_log_verbosity": config.cli_log_verbosity,
            }
            profile = config.profile  # Or direct access

        """
        msg = (
            "FlextCliConfig.get_cli_context() has been removed. "
            "Access configuration attributes directly."
        )
        raise NotImplementedError(msg)

    def get_auth_context(self) -> FlextCliTypes.Configuration.AuthenticationConfig:
        """REMOVED: Access config attributes directly.

        Migration:
            # Old pattern
            auth_context = config.get_auth_context()
            api_url = auth_context["api_url"]

            # New pattern - direct attribute access
            auth_context = {
                "api_url": config.api_url,
                "token_file": str(config.token_file),
                "refresh_token_file": str(config.refresh_token_file),
                "auto_refresh": config.auto_refresh,
                "api_key_configured": config.cli_api_key is not None,
            }
            api_url = config.api_url  # Or direct access

        """
        msg = (
            "FlextCliConfig.get_auth_context() has been removed. "
            "Access authentication configuration attributes directly."
        )
        raise NotImplementedError(msg)

    def get_logging_context(self) -> FlextCliTypes.Configuration.LogConfig:
        """REMOVED: Access config attributes directly.

        Migration:
            # Old pattern
            logging_context = config.get_logging_context()
            log_level = logging_context["log_level"]

            # New pattern - direct attribute access
            logging_context = {
                "log_level": config.log_level,
                "log_verbosity": config.log_verbosity,
                "cli_log_level": config.cli_log_level,
                "cli_log_verbosity": config.cli_log_verbosity,
                "log_file": str(config.log_file) if config.log_file else None,
            }
            log_level = config.log_level  # Or direct access

        """
        msg = (
            "FlextCliConfig.get_logging_context() has been removed. "
            "Access logging configuration attributes directly."
        )
        raise NotImplementedError(msg)

    def validate_output_format_result(self, value: str) -> FlextResult[str]:
        """Validate output format using FlextCliConstants and return FlextResult."""
        if value not in FlextCliConstants.OUTPUT_FORMATS_LIST:
            return FlextResult[str].fail(f"Invalid output format: {value}")
        return FlextResult[str].ok(value)

    @classmethod
    def create_for_environment(
        cls, environment: str, **overrides: object
    ) -> FlextCliConfig:
        """REMOVED: Use direct instantiation with environment parameter.

        Migration:
            # Old pattern
            config = FlextCliConfig.create_for_environment("production", debug=False)

            # New pattern - direct instantiation
            config = FlextCliConfig(environment="production", debug=False)

        """
        msg = (
            "FlextCliConfig.create_for_environment() has been removed. "
            "Use FlextCliConfig(environment='...') for direct instantiation."
        )
        raise NotImplementedError(msg)

    @classmethod
    def create_default(cls) -> FlextCliConfig:
        """REMOVED: Use direct instantiation.

        Migration:
            # Old pattern
            config = FlextCliConfig.create_default()

            # New pattern - direct instantiation
            config = FlextCliConfig()

        """
        msg = (
            "FlextCliConfig.create_default() has been removed. "
            "Use FlextCliConfig() for direct instantiation."
        )
        raise NotImplementedError(msg)

    @classmethod
    def create_for_profile(cls, profile: str, **kwargs: object) -> FlextCliConfig:
        """REMOVED: Use direct instantiation with profile parameter.

        Migration:
            # Old pattern
            config = FlextCliConfig.create_for_profile("dev", debug=True)

            # New pattern - direct instantiation
            config = FlextCliConfig(profile="dev", debug=True)

        """
        msg = (
            "FlextCliConfig.create_for_profile() has been removed. "
            "Use FlextCliConfig(profile='...') for direct instantiation."
        )
        raise NotImplementedError(msg)

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

            # Create config instance directly with loaded data
            config = cls(**data)
            return FlextResult[FlextCliConfig].ok(config)

        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to load configuration from {config_file}: {e}"
            )

    @classmethod
    def get_global_instance(cls) -> FlextCliConfig:
        """REMOVED: Use direct instantiation.

        Migration:
            # Old pattern
            config = FlextCliConfig.get_global_instance()

            # New pattern - direct instantiation
            config = FlextCliConfig()

            # Or for singleton pattern, manage explicitly
            import threading
            _config_lock = threading.RLock()
            _config_instance: FlextCliConfig | None = None

            with _config_lock:
                if _config_instance is None:
                    _config_instance = FlextCliConfig()
                config = _config_instance

        """
        msg = (
            "FlextCliConfig.get_global_instance() has been removed. "
            "Use FlextCliConfig() to create instances directly."
        )
        raise NotImplementedError(msg)

    def execute_as_service(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute config as service operation."""
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": "flext-cli-config",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
            "config": self.model_dump(),
        })

    def load_config_file(self, config_path: str) -> FlextResult[FlextCliConfig]:
        """Load configuration from file using FlextConfig.from_file."""
        result = FlextCliConfig.from_file(config_path)
        if result.is_failure:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to load config: {result.error}"
            )
        # Cast to FlextCliConfig since from_file returns FlextConfig

        return FlextResult[FlextCliConfig].ok(cast("FlextCliConfig", result.unwrap()))

    def save_config_file(self, config_path: str) -> FlextResult[None]:
        """Save configuration to file with proper Path serialization."""
        try:
            # Convert model to dict and ensure all values are JSON serializable
            config_dict = self.model_dump()
            # Convert any Path objects to strings
            for key, value in config_dict.items():
                if isinstance(value, Path):
                    config_dict[key] = str(value)

            # Save using JSON directly for proper control
            import json

            path = Path(config_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with path.open("w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2)

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Save failed: {e}")

    # Protocol-compliant methods for CliConfigProvider
    def load_config(self) -> FlextResult[FlextCliTypes.Data.CliConfigData]:
        """Load CLI configuration - implements CliConfigProvider protocol.

        Returns:
            FlextResult[FlextCliTypes.Data.CliConfigData]: Configuration data or error

        """
        try:
            # Convert model to dictionary format expected by protocol
            config_data = self.model_dump()
            return FlextResult[FlextCliTypes.Data.CliConfigData].ok(config_data)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliConfigData].fail(
                f"Config load failed: {e}"
            )

    def save_config(
        self, config: FlextCliTypes.Data.CliConfigData
    ) -> FlextResult[None]:
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
