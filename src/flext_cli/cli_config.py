"""FLEXT CLI Configuration - Complete configuration system consolidating all CLI configs.

This module consolidates all CLI-related configuration from multiple scattered files
into a single, well-organized module following PEP8 naming conventions.

Consolidated from:
    - config.py (root level)
    - config_hierarchical.py (hierarchical configuration)
    - Various configuration definitions across modules

Design Principles:
    - PEP8 naming: cli_config.py (not config.py for clarity)
    - Single source of truth for all CLI configuration
    - Extends flext-core configuration where appropriate
    - Environment variable loading with validation
    - Type safety with comprehensive annotations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path

import toml
from flext_api.constants import FlextApiConstants as _ApiC
from flext_core import (
    FlextResult,
    FlextSettings,
)
from flext_core.constants import FlextConstants
from pydantic import Field, field_validator

from flext_cli.cli_types import ConfigDict, OutputFormat

# =============================================================================
# CORE CLI CONFIGURATION - Extending flext-core settings
# =============================================================================


def _default_api_url() -> str:
    try:
        host = getattr(FlextConstants.Platform, "DEFAULT_HOST", "localhost")
        port = getattr(FlextConstants.Platform, "FLEXT_API_PORT", 8081)
        return f"http://{host}:{port}"
    except Exception:
        return "http://localhost:8000"


class CLIConfig(FlextSettings):
    """Complete CLI configuration extending flext-core settings.

    Consolidates all CLI configuration needs into a single, comprehensive
    configuration class that handles environment variables, validation,
    and hierarchical configuration loading.
    """

    # Basic CLI settings
    profile: str = Field(
        default="default",
        description="Configuration profile name",
    )

    output_format: OutputFormat = Field(
        default=OutputFormat.TABLE,
        description="Default output format for CLI commands",
    )

    # Logging and debugging
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    # Legacy compatibility flag expected by tests
    trace: bool = Field(
        default=False,
        description="Enable trace mode (legacy flag for tests)",
    )

    verbose: bool = Field(
        default=False,
        description="Enable verbose output",
    )

    quiet: bool = Field(
        default=False,
        description="Enable quiet mode (minimal output)",
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    # Display settings
    no_color: bool = Field(
        default=False,
        description="Disable colored output",
    )

    force_color: bool = Field(
        default=False,
        description="Force colored output even in non-TTY",
    )

    # API settings
    api_url: str = Field(
        default_factory=_default_api_url,
        description="FLEXT Service API URL",
    )

    api_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="API request timeout in seconds",
    )

    # Legacy connection/read timeout fields used by tests
    connect_timeout: int = Field(default=10, ge=1, description="Connect timeout (s)")
    read_timeout: int = Field(default=30, ge=1, description="Read timeout (s)")

    api_token: str | None = Field(
        default=None,
        description="API authentication token",
    )

    # File paths
    config_file: Path | None = Field(
        default=None,
        description="Path to configuration file",
    )

    data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".flext",
        description="Data directory for CLI",
    )

    cache_dir: Path | None = Field(
        default=None,
        description="Cache directory (defaults to data_dir/cache)",
    )

    # Plugin settings
    plugin_dir: Path | None = Field(
        default=None,
        description="Plugin directory (defaults to data_dir/plugins)",
    )

    auto_load_plugins: bool = Field(
        default=True,
        description="Automatically load plugins on startup",
    )

    # Session settings
    session_timeout: int = Field(
        default=3600,
        ge=60,
        description="Session timeout in seconds",
    )

    save_session_history: bool = Field(
        default=True,
        description="Save command history in sessions",
    )

    max_history_entries: int = Field(
        default=1000,
        ge=10,
        le=10000,
        description="Maximum number of history entries to keep",
    )

    # Performance settings
    command_timeout: int = Field(
        default=300,
        ge=1,
        description="Default command timeout in seconds",
    )

    max_concurrent_commands: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent commands",
    )

    # Feature flags
    enable_interactive_mode: bool = Field(
        default=True,
        description="Enable interactive CLI mode",
    )

    enable_auto_completion: bool = Field(
        default=True,
        description="Enable command auto-completion",
    )

    enable_progress_bars: bool = Field(
        default=True,
        description="Enable progress bars for long operations",
    )

    # Advanced settings
    project_name: str = Field(
        default="FLEXT CLI",
        description="Project name for display",
    )

    project_description: str = Field(
        default="FLEXT Command Line Interface",
        description="Project description",
    )

    custom_settings: ConfigDict = Field(
        default_factory=dict,
        description="Custom settings dictionary",
    )

    class Config:
        """Pydantic configuration."""

        env_prefix = "FLX_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is recognized."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            msg = f"Log level must be one of: {', '.join(valid_levels)}"
            raise ValueError(msg)
        return v.upper()

    @field_validator("output_format", mode="before")
    @classmethod
    def validate_output_format(cls, v: object) -> OutputFormat:
        """Validate and convert output format."""
        if isinstance(v, str):
            try:
                return OutputFormat(v.lower())
            except ValueError as err:
                valid_formats = [fmt.value for fmt in OutputFormat]
                msg = f"Invalid output format '{v}'. Valid formats: {', '.join(valid_formats)}"
                raise ValueError(msg) from err
        if isinstance(v, OutputFormat):
            return v
        msg = f"Invalid output format type: {type(v)}"
        raise ValueError(msg)

    @field_validator("api_url")
    @classmethod
    def validate_api_url(cls, v: str) -> str:
        """Validate API URL format."""
        if not v.startswith(("http://", "https://")):
            msg = "API URL must start with http:// or https://"
            raise ValueError(msg)
        return v

    def model_post_init(self, __context: object, /) -> None:
        """Post-initialization setup."""
        super().model_post_init(__context)

        # Set default paths if not provided
        if self.cache_dir is None:
            self.cache_dir = self.data_dir / "cache"

        if self.plugin_dir is None:
            self.plugin_dir = self.data_dir / "plugins"

        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

    def validate_config(self) -> FlextResult[None]:
        """Validate complete configuration."""
        try:
            error: str | None = None

            if self.quiet and self.verbose:
                error = "Cannot enable both quiet and verbose mode"
            elif self.no_color and self.force_color:
                error = "Cannot disable and force colors simultaneously"
            elif self.config_file and not self.config_file.exists():
                error = f"Configuration file does not exist: {self.config_file}"
            elif self.api_timeout <= 0:
                error = "API timeout must be positive"
            elif self.command_timeout <= 0:
                error = "Command timeout must be positive"

            if error is not None:
                return FlextResult.fail(error)
            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Configuration validation failed: {e}")

    def get_effective_log_level(self) -> str:
        """Get effective log level considering debug/quiet modes."""
        if self.debug:
            return "DEBUG"
        if self.quiet:
            return "WARNING"
        return self.log_level

    # ---------------------------------------------------------------------
    # Legacy compatibility properties expected by tests
    # ---------------------------------------------------------------------

    @property
    def format_type(self) -> str:  # pragma: no cover - trivial mapping
        return self.output_format.value

    def should_use_color(self) -> bool:
        """Determine if colored output should be used."""
        if self.force_color:
            return True
        if self.no_color:
            return False
        # Check if running in TTY
        try:
            return os.isatty(1)
        except Exception:
            return False

    def get_api_headers(self) -> dict[str, str]:
        """Get API request headers."""
        headers = {
            "User-Agent": f"{self.project_name}/1.0.0",
            "Accept": _ApiC.ContentTypes.JSON,
            "Content-Type": _ApiC.ContentTypes.JSON,
        }

        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        return headers

    def load_profile_config(self, profile_name: str) -> FlextResult[ConfigDict]:
        """Load configuration for specific profile."""
        if not self.config_file or not self.config_file.exists():
            return FlextResult.ok({})

        try:
            config_data = toml.load(self.config_file)
            profiles = config_data.get("profiles", {})

            if profile_name not in profiles:
                return FlextResult.ok({})

            profile_config = profiles[profile_name]
            if not isinstance(profile_config, dict):
                return FlextResult.fail(
                    f"Invalid profile configuration for '{profile_name}'",
                )

            return FlextResult.ok(profile_config)

        except Exception as e:
            return FlextResult.fail(f"Failed to load profile '{profile_name}': {e}")

    def save_config_file(self, file_path: Path | None = None) -> FlextResult[None]:
        """Save current configuration to file."""
        try:
            target_file = file_path or self.config_file
            if not target_file:
                target_file = self.data_dir / "config.toml"

            # Convert config to dict
            config_dict = self.model_dump(exclude={"custom_settings"})

            # Add custom settings at root level
            config_dict.update(self.custom_settings)

            # Write to file
            target_file.parent.mkdir(parents=True, exist_ok=True)
            with target_file.open("w") as f:
                toml.dump(config_dict, f)

            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Failed to save configuration: {e}")

    @classmethod
    def load_from_file(cls, file_path: Path) -> FlextResult[CLIConfig]:
        """Load configuration from file."""
        try:
            if not file_path.exists():
                return FlextResult.fail(
                    f"Configuration file does not exist: {file_path}",
                )

            config_data = toml.load(file_path)

            # Extract custom settings
            known_fields = set(cls.model_fields.keys())

            custom_settings = {
                key: value
                for key, value in config_data.items()
                if key not in known_fields and key != "profiles"
            }

            # Create config instance
            config_instance = cls(
                config_file=file_path,
                custom_settings=custom_settings,
                **{k: v for k, v in config_data.items() if k in known_fields},
            )

            return FlextResult.ok(config_instance)

        except Exception as e:
            return FlextResult.fail(
                f"Failed to load configuration from {file_path}: {e}",
            )

    def to_dict(self, *, include_sensitive: bool = False) -> ConfigDict:
        """Convert configuration to dictionary."""
        config_dict = self.model_dump()

        if not include_sensitive:
            # Remove sensitive fields
            sensitive_fields = {"api_token"}
            for field in sensitive_fields:
                if field in config_dict:
                    config_dict[field] = "***"

        return config_dict

    # ------------------------------------------------------------------
    # Legacy helper methods expected by tests
    # ------------------------------------------------------------------

    def configure(self, settings: object) -> bool:
        """Apply simple settings updates from a plain dict, return success.

        This mirrors the legacy `configure` API used in tests, updating a subset
        of fields and returning True/False based on success.
        """
        if not isinstance(settings, dict):
            return False
        try:
            if "debug" in settings:
                self.debug = bool(settings["debug"])
            if "api_timeout" in settings:
                self.api_timeout = int(settings["api_timeout"])
            if "output_format" in settings:
                # Accept raw string and convert via validator
                self.output_format = settings["output_format"]
            return True
        except Exception:
            return False

    def validate_domain_rules(self) -> bool:
        """Legacy boolean validation wrapper over validate_config()."""
        result = self.validate_config()
        return result.is_success


# =============================================================================
# CONFIGURATION FACTORY FUNCTIONS
# =============================================================================


def create_cli_config(
    profile: str = "default",
    **overrides: object,
) -> FlextResult[CLIConfig]:
    """Create CLI configuration with optional overrides.

    Args:
        profile: Configuration profile to load
        **overrides: Configuration overrides

    Returns:
        Result containing CLI configuration

    """
    try:
        # Start with default configuration
        config = CLIConfig(profile=profile, **overrides)  # type: ignore[arg-type]

        # Load profile-specific settings if config file exists
        if config.config_file and config.config_file.exists():
            profile_result = config.load_profile_config(profile)
            if profile_result.is_success:
                profile_config = profile_result.unwrap()
                # Apply profile settings (overrides take precedence)
                merged_config = {**profile_config, **overrides}
                config = CLIConfig(profile=profile, **merged_config)  # type: ignore[arg-type]

        # Validate final configuration
        validation_result = config.validate_config()
        if validation_result.is_failure:
            error_msg = validation_result.error or "Configuration validation failed"
            return FlextResult.fail(error_msg)

        return FlextResult.ok(config)

    except Exception as e:
        return FlextResult.fail(f"Failed to create CLI configuration: {e}")


def create_cli_config_from_env() -> FlextResult[CLIConfig]:
    """Create CLI configuration from environment variables only."""
    try:
        config = CLIConfig()
        validation_result = config.validate_config()

        if validation_result.is_failure:
            error_msg = validation_result.error or "Configuration validation failed"
            return FlextResult.fail(error_msg)

        return FlextResult.ok(config)

    except Exception as e:
        return FlextResult.fail(f"Failed to create configuration from environment: {e}")


def create_cli_config_from_file(file_path: Path) -> FlextResult[CLIConfig]:
    """Create CLI configuration from file."""
    return CLIConfig.load_from_file(file_path)


# Legacy aliases for backward compatibility
FlextCliConfig = CLIConfig
create_flext_cli_config = create_cli_config
FlextCliConfigHierarchical = CLIConfig  # Old hierarchical config class


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core configuration
    "CLIConfig",
    # Legacy aliases
    "FlextCliConfig",
    "FlextCliConfigHierarchical",
    # Factory functions
    "create_cli_config",
    "create_cli_config_from_env",
    "create_cli_config_from_file",
    "create_flext_cli_config",
    # Compatibility helper used by simple_api
    "get_cli_settings",
]


def get_cli_settings() -> CLIConfig:
    """Compatibility helper to satisfy imports in simple_api/tests.

    Returns a default CLIConfig instance; tests generally patch this function
    or do not rely on its concrete behavior.
    """
    return CLIConfig()
