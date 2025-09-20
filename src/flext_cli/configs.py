"""Unified CLI configurations module with single FlextCliConfigs class.

This module consolidates ALL configuration-related functionality into a single
unified class following SOLID principles and flext-core patterns.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Self, cast

from pydantic import BaseModel, Field, field_validator, model_validator

from flext_cli.constants import FlextCliConstants
from flext_cli.utils import FlextCliUtilities
from flext_core import (
    FlextConfig,
    FlextResult,
)


class FlextCliConfigs(FlextConfig):
    """Unified CLI configurations following single class pattern.

    Consolidates ALL configuration functionality including:
    - CLI-specific configurations
    - Profile management
    - Directory management
    - API configuration
    - Authentication settings
    - Output formatting settings
    - Validation and business rules

    Uses Pydantic 2 advanced features and extends flext-core FlextConfig.
    """

    model_config = FlextCliUtilities.get_settings_config_dict()

    # Override app_name for CLI-specific configuration
    app_name: str = Field(default="flext-cli", description="CLI application name")

    class CliDefaults:
        """CLI-specific default values following nested class pattern."""

        class Command:
            """Command execution defaults."""

            timeout_seconds: int = 30
            max_timeout_seconds: int = 300
            max_retries: int = 3

        class Output:
            """Output formatting defaults."""

            default_format: str = "table"
            default_width: int = 80

        class Auth:
            """Authentication defaults."""

            token_expiry_hours: int = 24
            refresh_expiry_days: int = 30

    class ProfileManager:
        """Nested profile management functionality."""

        @staticmethod
        def validate_profile_name(profile: str) -> FlextResult[str]:
            """Validate profile name."""
            if not profile or not profile.strip():
                return FlextResult[str].fail("Profile name cannot be empty")

            cleaned = str(profile).strip()
            if not cleaned:
                return FlextResult[str].fail(
                    "Profile name must contain valid characters",
                )
            return FlextResult[str].ok(cleaned)

        @staticmethod
        def create_development_profile() -> dict[str, object]:
            """Create development profile configuration."""
            return {
                "profile": "development",
                "debug": True,
                "trace": True,
                "log_level": "DEBUG",
                "verbose": True,
                "output_format": "table",
            }

        @staticmethod
        def create_production_profile() -> dict[str, object]:
            """Create production profile configuration."""
            return {
                "profile": "production",
                "debug": False,
                "log_level": "INFO",
                "quiet": True,
                "output_format": "json",
                "verify_ssl": True,
            }

    class DirectoryManager:
        """Nested directory management functionality."""

        @staticmethod
        def base_dir() -> Path:
            """Base directory for CLI operations."""
            return Path.home() / FlextCliConstants.FLEXT_DIR_NAME

        @staticmethod
        def cache_dir() -> Path:
            """Cache directory for CLI operations."""
            return FlextCliConfigs.DirectoryManager.base_dir() / "cache"

        @staticmethod
        def log_dir() -> Path:
            """Log directory for CLI operations."""
            return FlextCliConfigs.DirectoryManager.base_dir() / "logs"

        @staticmethod
        def data_dir() -> Path:
            """Data directory for CLI operations."""
            return FlextCliConfigs.DirectoryManager.base_dir() / "data"

        @staticmethod
        def ensure_directories(config: FlextCliConfigs) -> FlextResult[None]:
            """Ensure CLI directories exist."""
            directories = [
                config.config_dir,
                config.cache_dir,
                config.log_dir,
                config.data_dir,
            ]

            for directory in directories:
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
            return FlextResult[None].ok(None)

    class ApiConfigManager:
        """Nested API configuration management."""

        @staticmethod
        def validate_timeouts(
            api_timeout: int,
            connect_timeout: int,
        ) -> FlextResult[None]:
            """Validate timeout values."""
            if api_timeout <= 0 or connect_timeout <= 0:
                return FlextResult[None].fail("Timeout values must be positive")
            return FlextResult[None].ok(None)

        @staticmethod
        def validate_retries(retries: int, max_retries: int) -> FlextResult[None]:
            """Validate retry values."""
            if retries < 0 or max_retries < 0:
                return FlextResult[None].fail("Retry values cannot be negative")
            return FlextResult[None].ok(None)

        @staticmethod
        def sync_api_fields(config: FlextCliConfigs) -> None:
            """Synchronize API-related fields."""
            # Sync api_url with base_url (base_url takes precedence if set)
            if (
                hasattr(config, "base_url")
                and config.base_url != FlextCliConstants.FALLBACK_API_URL
            ):
                config.__dict__["api_url"] = config.base_url
            elif config.api_url != FlextCliConstants.FALLBACK_API_URL:
                config.__dict__["base_url"] = config.api_url

            # Sync retry fields
            if (
                hasattr(config, "max_command_retries")
                and config.max_command_retries > 0
            ):
                config.__dict__["retries"] = config.max_command_retries
                config.__dict__["max_retries"] = config.max_command_retries
            elif config.max_retries > 0:
                config.__dict__["retries"] = config.max_retries
                if hasattr(config, "max_command_retries"):
                    config.__dict__["max_command_retries"] = config.max_retries

    class ValidationManager:
        """Nested validation management functionality."""

        @staticmethod
        def validate_output_format(value: str) -> FlextResult[str]:
            """Validate output format."""
            valid_formats = {"table", "json", "yaml", "csv", "plain"}
            if value not in valid_formats:
                return FlextResult[str].fail(
                    f"Invalid output format '{value}'. Must be one of: {valid_formats}",
                )
            return FlextResult[str].ok(value)

        @staticmethod
        def validate_business_rules(config: FlextCliConfigs) -> FlextResult[None]:
            """Validate CLI-specific business rules."""
            # Validate output format
            format_result = FlextCliConfigs.ValidationManager.validate_output_format(
                config.output_format,
            )
            if format_result.is_failure:
                return FlextResult[None].fail(
                    format_result.error or "Format validation failed",
                )

            # Validate profile
            profile_result = FlextCliConfigs.ProfileManager.validate_profile_name(
                config.profile,
            )
            if profile_result.is_failure:
                return FlextResult[None].fail(
                    profile_result.error or "Profile validation failed",
                )

            # Validate timeouts
            timeout_result = FlextCliConfigs.ApiConfigManager.validate_timeouts(
                config.api_timeout,
                config.connect_timeout,
            )
            if timeout_result.is_failure:
                return FlextResult[None].fail(
                    timeout_result.error or "Timeout validation failed",
                )

            # Validate retries
            retry_result = FlextCliConfigs.ApiConfigManager.validate_retries(
                config.retries,
                config.max_retries,
            )
            if retry_result.is_failure:
                return FlextResult[None].fail(
                    retry_result.error or "Retry validation failed",
                )

            return FlextResult[None].ok(None)

    # =========================================================================
    # CLI-SPECIFIC FIELDS ONLY (not in FlextConfig)
    # =========================================================================

    # CLI profile management
    profile: str = Field(
        default="default",
        description="CLI configuration profile name",
    )

    # CLI output settings
    output_format: str = Field(
        default="table",
        description="CLI output format (table, json, yaml, csv)",
    )
    no_color: bool = Field(default=False, description="Disable colored CLI output")
    quiet: bool = Field(default=False, description="Minimal output mode")
    verbose: bool = Field(default=False, description="Verbose output mode")
    pager: str | None = Field(
        default=None,
        description="Optional pager command for long output",
    )

    # CLI directories
    config_dir: Path = Field(default_factory=DirectoryManager.base_dir)
    cache_dir: Path = Field(default_factory=DirectoryManager.cache_dir)
    log_dir: Path = Field(default_factory=DirectoryManager.log_dir)
    data_dir: Path = Field(default_factory=DirectoryManager.data_dir)

    # Authentication files (CLI-specific)
    token_file: Path = Field(
        default_factory=FlextCliUtilities.token_file_path,
        description="CLI authentication token file",
    )
    refresh_token_file: Path = Field(
        default_factory=FlextCliUtilities.refresh_token_file_path,
        description="CLI refresh token file",
    )
    auto_refresh: bool = Field(
        default=True,
        description="Enable automatic token refresh",
    )

    # API-related fields
    api_url: str = Field(
        default=FlextCliConstants.FALLBACK_API_URL,
        description="API URL",
    )
    api_timeout: int = Field(
        default=30,
        ge=1,
        le=3600,
        description="API timeout in seconds",
    )
    connect_timeout: int = Field(
        default=30,
        ge=1,
        le=3600,
        description="Connection timeout in seconds",
    )
    read_timeout: int = Field(
        default=60,
        ge=1,
        le=3600,
        description="Read timeout in seconds",
    )
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

    # Retry configuration
    retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retries",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retries",
    )

    # Project metadata (CLI-specific overrides)
    project_name: str = Field(default="flext-cli", description="Project name for CLI")
    project_description: str = Field(
        default="FLEXT CLI - Developer Command Line Interface",
        description="Project description",
    )
    project_version: str = Field(
        default="0.9.0",
        pattern=r"^\d+\.\d+\.\d+",
        description="CLI version",
    )

    # =========================================================================
    # PYDANTIC 2 VALIDATORS
    # =========================================================================

    @field_validator("output_format")
    @classmethod
    def validate_output_format_field(cls, value: str) -> str:
        """Validate output format field."""
        result = cls.ValidationManager.validate_output_format(value)
        if result.is_failure:
            raise ValueError(result.error)
        return result.unwrap()

    @field_validator("profile")
    @classmethod
    def validate_profile_field(cls, value: str) -> str:
        """Validate profile field."""
        result = cls.ProfileManager.validate_profile_name(value)
        if result.is_failure:
            raise ValueError(result.error)
        return result.unwrap()

    @model_validator(mode="after")
    def sync_api_fields_validator(self) -> Self:
        """Synchronize API-related fields."""
        self.ApiConfigManager.sync_api_fields(self)
        return self

    @model_validator(mode="after")
    def validate_configuration_consistency_validator(self) -> Self:
        """Validate configuration consistency."""
        return self.validate_configuration_consistency()

    # =========================================================================
    # BUSINESS LOGIC METHODS
    # =========================================================================

    def validate_configuration_consistency(self) -> Self:
        """Override parent validation to allow flexible CLI configuration."""
        # CLI allows any log level regardless of environment
        # Ensure required CLI fields are set
        if not self.profile:
            self.profile = "default"
        if not self.output_format:
            self.output_format = "table"
        return self

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI-specific business rules."""
        return self.ValidationManager.validate_business_rules(self)

    def ensure_directories(self) -> FlextResult[None]:
        """Ensure CLI directories exist."""
        return self.DirectoryManager.ensure_directories(self)

    def ensure_setup(self) -> FlextResult[None]:
        """Ensure CLI setup is complete."""
        return self.ensure_directories()

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def is_development_mode(self) -> bool:
        """Check if in development mode."""
        return self.profile == "development" or bool(self.debug)

    @property
    def is_production_mode(self) -> bool:
        """Check if in production mode."""
        return self.profile == "production" and not self.debug

    @property
    def timeout(self) -> int:
        """Get timeout in seconds."""
        return self.timeout_seconds

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def __init__(self, **data: object) -> None:
        """Initialize CLI configuration with flext-core integration - NO legacy aliases."""
        # Call parent __init__ - FlextConfig handles initialization
        super().__init__()

        # Set fields manually after parent initialization
        readonly_properties = {"is_development_mode", "is_production_mode"}
        for key, value in data.items():
            if (
                hasattr(self, key)
                and value is not None
                and key not in readonly_properties
            ):
                setattr(self, key, value)

        # Set CLI-specific fields
        cli_specific_fields = {
            "profile",
            "output_format",
            "no_color",
            "quiet",
            "verbose",
            "pager",
            "api_url",
            "api_timeout",
            "connect_timeout",
            "read_timeout",
            "verify_ssl",
            "retries",
            "max_retries",
            "auto_refresh",
        }
        for key, value in data.items():
            if hasattr(self, key) and value is not None and key in cli_specific_fields:
                self.__dict__[key] = value

    # =========================================================================
    # FACTORY METHODS
    # =========================================================================

    @classmethod
    def create_development_config(cls) -> FlextResult[FlextCliConfigs]:
        """Create development configuration."""
        config_data = cls.ProfileManager.create_development_profile()
        config = cls(**config_data)
        return FlextResult[FlextCliConfigs].ok(config)

    @classmethod
    def create_production_config(cls) -> FlextResult[FlextCliConfigs]:
        """Create production configuration."""
        config_data = cls.ProfileManager.create_production_profile()
        config = cls(**config_data)
        return FlextResult[FlextCliConfigs].ok(config)

    @classmethod
    def get_global_instance(cls) -> FlextCliConfigs:
        """Get global CLI configuration instance."""
        # Get base config from FlextConfig (single source of truth)
        base_config = FlextConfig.get_global_instance()

        # If the base config is already a FlextCliConfigs, return it directly
        if isinstance(base_config, cls):
            return base_config

        # Get base config data
        if hasattr(base_config, "model_dump"):
            base_data = cast("BaseModel", base_config).model_dump()
        else:
            base_data = {}
            if hasattr(base_config.__class__, "model_fields"):
                for field_name in cast("BaseModel", base_config.__class__).model_fields:
                    if hasattr(base_config, field_name):
                        base_data[field_name] = getattr(base_config, field_name)

        # Remove fields that should use FlextCliConfigs defaults
        cli_specific_overrides = ["app_name"]  # FlextCliConfigs should use "flext-cli"

        # Check for environment variables
        env_prefix = "FLEXT_CLI_"
        env_fields_to_check = [
            "debug",
            "output_format",
            "log_level",
            "quiet",
            "verbose",
            "no_color",
        ]

        for field in env_fields_to_check:
            env_var_name = f"{env_prefix}{field.upper()}"
            if env_var_name in os.environ:
                cli_specific_overrides.append(field)

        for field in cli_specific_overrides:
            base_data.pop(field, None)

        return cls(**base_data)

    @classmethod
    def set_global_instance(cls, config: FlextConfig) -> None:
        """Set global instance (delegates to FlextConfig)."""
        FlextConfig.set_global_instance(config)

    @classmethod
    def clear_global_instance(cls) -> None:
        """Clear global instance (delegates to FlextConfig)."""
        FlextConfig.clear_global_instance()

    @classmethod
    def get_current(cls) -> FlextCliConfigs:
        """Get current CLI configuration."""
        return cls.get_global_instance()

    @classmethod
    def create_with_directories(
        cls,
        config_data: dict[str, object] | None = None,
    ) -> FlextResult[FlextCliConfigs]:
        """Create CLI configuration with directory setup."""
        config = cls(**config_data) if config_data else cls()

        dir_result = config.ensure_directories()
        if dir_result.is_failure:
            return FlextResult[FlextCliConfigs].fail(
                f"Failed to create directories: {dir_result.error}",
            )

        return FlextResult[FlextCliConfigs].ok(config)

    @classmethod
    def load_from_profile(cls, profile_name: str) -> FlextResult[FlextCliConfigs]:
        """Load configuration from a specific profile."""
        profile_result = cls.ProfileManager.validate_profile_name(profile_name)
        if profile_result.is_failure:
            return FlextResult[FlextCliConfigs].fail(
                profile_result.error or "Profile validation failed",
            )

        config = cls(profile=profile_result.unwrap())
        return FlextResult[FlextCliConfigs].ok(config)

    @classmethod
    def apply_cli_overrides(
        cls,
        cli_params: dict[str, object],
    ) -> FlextResult[FlextCliConfigs]:
        """Apply CLI parameter overrides to configuration."""
        try:
            current_config = cls.get_global_instance()

            # Parameter mappings with precedence
            param_mappings = {
                "profile": [(1, "profile")],
                "debug": [(1, "debug")],
                "output_format": [(1, "output"), (2, "output_format")],
                "log_level": [(1, "log_level"), (2, "log-level")],
                "quiet": [(1, "quiet")],
                "verbose": [(1, "verbose")],
                "no_color": [(1, "no_color"), (2, "no-color")],
                "api_url": [(1, "api_url"), (2, "api-url")],
                "timeout_seconds": [(1, "timeout")],
                "command_timeout": [(1, "command_timeout"), (2, "command-timeout")],
                "api_timeout": [(1, "api_timeout"), (2, "api-timeout")],
                "trace": [(1, "trace")],
            }

            config_updates = {}

            # Process parameters with precedence
            for config_field, param_options in param_mappings.items():
                best_value = None
                best_priority = 0

                for priority, cli_param in param_options:
                    if (
                        cli_param in cli_params
                        and cli_params[cli_param] is not None
                        and priority > best_priority
                    ):
                        best_priority = priority
                        best_value = cli_params[cli_param]

                if best_value is not None:
                    config_updates[config_field] = best_value

            # Create new config with overrides
            if config_updates:
                current_data = {
                    key: getattr(current_config, key)
                    for key in cls.model_fields
                    if hasattr(current_config, key)
                }
                new_config = cls(**{**current_data, **config_updates})
                cls.set_global_instance(new_config)
                return FlextResult[FlextCliConfigs].ok(new_config)

            return FlextResult[FlextCliConfigs].ok(current_config)
        except Exception as e:
            return FlextResult[FlextCliConfigs].fail(
                f"Failed to apply CLI overrides: {e}",
            )

    @classmethod
    def setup_cli(
        cls,
        config: FlextCliConfigs | None = None,
    ) -> FlextResult[FlextCliConfigs]:
        """Set up CLI with configuration."""
        if config is None:
            config = cls.get_global_instance()

        # Validate configuration
        validation_result = config.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult[FlextCliConfigs].fail(
                f"Configuration validation failed: {validation_result.error}",
            )

        return FlextResult[FlextCliConfigs].ok(config)

    @classmethod
    def sync_with_flext_config(cls) -> FlextResult[FlextCliConfigs]:
        """Synchronize with base FlextConfig."""
        try:
            base_config = FlextConfig.get_global_instance()

            # Create CLI config from base
            base_data = {}
            if hasattr(base_config, "model_dump"):
                base_data = cast("BaseModel", base_config).model_dump()
            elif hasattr(base_config.__class__, "model_fields"):
                for field_name in base_config.__class__.model_fields:
                    if hasattr(base_config, field_name):
                        base_data[field_name] = getattr(base_config, field_name)

            cli_config = cls(**base_data)
            cls.set_global_instance(cli_config)

            return FlextResult[FlextCliConfigs].ok(cli_config)
        except Exception as e:
            return FlextResult[FlextCliConfigs].fail(
                f"Failed to sync with FlextConfig: {e}",
            )

    @classmethod
    def ensure_flext_config_integration(cls) -> FlextResult[None]:
        """Ensure integration with FlextConfig is maintained."""
        try:
            FlextConfig.get_global_instance()
        except Exception as e:
            return FlextResult[None].fail(
                f"FlextConfig global instance not available: {e}",
            )

        try:
            cls.get_global_instance()
        except Exception as e:
            return FlextResult[None].fail(f"CLI config instance not available: {e}")

        return FlextResult[None].ok(None)


__all__ = ["FlextCliConfigs"]
