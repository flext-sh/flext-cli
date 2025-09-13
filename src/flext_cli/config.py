"""FLEXT CLI Config - Minimal CLI configuration extending flext-core.

Uses flext-core FlextConfig EXTENSIVELY - NO duplication.
Only adds CLI-specific fields that don't exist in flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import override

from flext_core import FlextConfig, FlextResult, FlextUtilities
from pydantic import field_validator, model_validator

from flext_cli.constants import FlextCliConstants
from flext_cli.utils import (
    SETTINGS_CONFIG_DICT,
    bool_field,
    description_field,
    optional_field,
    path_field,
    positive_int_field,
    refresh_token_file_path,
    timeout_field,
    token_file_path,
    version_field,
)


class FlextCliConfig(FlextConfig):
    """CLI-specific configuration extending FlextConfig.

    Inherits all base configuration from FlextConfig and adds only
    CLI-specific fields. Uses FlextConfig as the single source of truth
    for all shared configuration values.
    """

    model_config = SETTINGS_CONFIG_DICT

    # Override app_name for CLI-specific configuration
    app_name: str = description_field("flext-cli", description="CLI application name")

    # Nested class for CLI defaults (expected by tests)
    class CliDefaults:
        """CLI-specific default values."""

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

    # =========================================================================
    # CLI-SPECIFIC FIELDS ONLY (not in FlextConfig)
    # =========================================================================

    # CLI profile management
    profile: str = description_field(
        "default", description="CLI configuration profile name"
    )

    # CLI output settings
    output_format: str = description_field(
        "table", description="CLI output format (table, json, yaml, csv)"
    )
    no_color: bool = bool_field(False, description="Disable colored CLI output")
    quiet: bool = bool_field(False, description="Minimal output mode")
    verbose: bool = bool_field(False, description="Verbose output mode")
    pager: str | None = optional_field(
        description="Optional pager command for long output"
    )

    # CLI directories (simplified pattern using base directory)
    @staticmethod
    def _base_dir() -> Path:
        """Base directory for CLI operations."""
        return Path.home() / FlextCliConstants.FLEXT_DIR_NAME

    @staticmethod
    def _cache_dir() -> Path:
        """Cache directory for CLI operations."""
        return FlextCliConfig._base_dir() / "cache"

    @staticmethod
    def _log_dir() -> Path:
        """Log directory for CLI operations."""
        return FlextCliConfig._base_dir() / "logs"

    @staticmethod
    def _data_dir() -> Path:
        """Data directory for CLI operations."""
        return FlextCliConfig._base_dir() / "data"

    config_dir: Path = path_field(_base_dir)
    cache_dir: Path = path_field(_cache_dir)
    log_dir: Path = path_field(_log_dir)
    data_dir: Path = path_field(_data_dir)

    # Authentication files (CLI-specific)
    token_file: Path = path_field(
        token_file_path, description="CLI authentication token file"
    )
    refresh_token_file: Path = path_field(
        refresh_token_file_path, description="CLI refresh token file"
    )
    auto_refresh: bool = bool_field(
        default=True, description="Enable automatic token refresh"
    )

    # API-related fields (aliases for compatibility)
    api_url: str = description_field(
        FlextCliConstants.FALLBACK_API_URL, description="API URL (alias for base_url)"
    )
    api_timeout: int = timeout_field(30, description="API timeout in seconds")
    connect_timeout: int = timeout_field(
        30, description="Connection timeout in seconds"
    )
    read_timeout: int = timeout_field(60, description="Read timeout in seconds")
    verify_ssl: bool = bool_field(default=True, description="Verify SSL certificates")

    # Retry configuration (aliases for compatibility)
    retries: int = positive_int_field(
        3, max_val=10, description="Number of retries (alias for max_command_retries)"
    )
    max_retries: int = positive_int_field(
        3, max_val=10, description="Maximum retries (alias for max_command_retries)"
    )

    # Project metadata (CLI-specific overrides)
    project_name: str = description_field(
        "flext-cli", description="Project name for CLI"
    )
    project_description: str = description_field(
        "FLEXT CLI - Developer Command Line Interface",
        description="Project description",
    )
    project_version: str = version_field(description="CLI version")

    # =========================================================================
    # VALIDATORS
    # =========================================================================

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, value: str) -> str:
        """Validate output format."""
        valid_formats = {"table", "json", "yaml", "csv"}
        if value not in valid_formats:
            msg = f"Invalid output format '{value}'. Must be one of: {valid_formats}"
            raise ValueError(msg)
        return value

    @field_validator("profile")
    @classmethod
    def validate_profile(cls, value: str) -> str:
        """Validate profile name."""
        if not value or not value.strip():
            msg = "Profile name cannot be empty"
            raise ValueError(msg)
        # Use FlextUtilities for string processing
        cleaned = FlextUtilities.TextProcessor.clean_text(value)
        if not cleaned:
            msg = "Profile name must contain valid characters"
            raise ValueError(msg)
        return cleaned

    @model_validator(mode="after")
    def sync_api_fields(self) -> FlextCliConfig:
        """Synchronize API-related fields for backward compatibility.

        Ensures that api_url and base_url are synchronized, and that
        retries/max_retries/max_command_retries are consistent.
        """
        # Use direct __dict__ access to avoid validation recursion

        # Sync api_url with base_url (base_url takes precedence if set)
        if (
            hasattr(self, "base_url")
            and self.base_url != FlextCliConstants.FALLBACK_API_URL
        ):
            self.__dict__["api_url"] = self.base_url
        elif self.api_url != FlextCliConstants.FALLBACK_API_URL:
            # If api_url was explicitly set, update base_url
            self.__dict__["base_url"] = self.api_url

        # Sync retry fields (max_command_retries from FlextConfig takes precedence)
        if hasattr(self, "max_command_retries") and self.max_command_retries > 0:
            self.__dict__["retries"] = self.max_command_retries
            self.__dict__["max_retries"] = self.max_command_retries
        elif self.max_retries > 0:
            self.__dict__["retries"] = self.max_retries
            if hasattr(self, "max_command_retries"):
                self.__dict__["max_command_retries"] = self.max_retries
        elif self.retries > 0:
            self.__dict__["max_retries"] = self.retries
            if hasattr(self, "max_command_retries"):
                self.__dict__["max_command_retries"] = self.retries

        # Sync timeout fields for consistency
        if (
            hasattr(self, "timeout_seconds")
            and self.timeout_seconds > 0
            and hasattr(self, "command_timeout")
        ):
            self.__dict__["command_timeout"] = self.timeout_seconds

        return self

    @model_validator(mode="after")
    def validate_configuration_consistency(self) -> FlextCliConfig:
        """Override parent validation to allow flexible CLI configuration.

        CLI tools need more flexibility than server applications, so we
        override some of the strict validations from FlextConfig.
        """
        # CLI allows any log level regardless of environment
        # (users should have full control in CLI tools)

        # Ensure required CLI fields are set
        if not self.profile:
            self.profile = "default"
        if not self.output_format:
            self.output_format = "table"

        return self

    # =========================================================================
    # COMPATIBILITY METHODS
    # =========================================================================

    def __init__(self, /, **data: object) -> None:
        """Initialize with backward compatibility support."""
        # Handle backward compatibility aliases
        if "base_url" in data and "api_url" not in data:
            data["api_url"] = data["base_url"]
        if "max_command_retries" in data:
            data["retries"] = data["max_command_retries"]
            data["max_retries"] = data["max_command_retries"]

        # Call parent __init__ with correct parameters
        # FlextConfig will handle all field setting via its __init__
        try:
            super().__init__(_factory_mode=False, **data)
        except TypeError:
            # If direct init fails, use individual field setting
            super().__init__(_factory_mode=False)

        # After parent init, check if command_timeout was properly set
        # If not, set it manually (this handles edge cases)
        if (
            "command_timeout" in data
            and self.command_timeout != data["command_timeout"]
        ):
            # Use __dict__ to avoid validation recursion
            self.__dict__["command_timeout"] = data["command_timeout"]

        # Set CLI-specific fields that parent doesn't know about
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
                # Use __dict__ to avoid validation recursion
                self.__dict__[key] = value

    @override
    def model_dump(self, **kwargs: object) -> dict[str, object]:
        """Dump model with all fields for compatibility."""
        # Get base dump - use type cast for kwargs
        result = super().model_dump(**kwargs)

        # Add CLI-specific fields explicitly
        cli_fields = {
            "profile": self.profile,
            "output_format": self.output_format,
            "no_color": self.no_color,
            "quiet": self.quiet,
            "verbose": self.verbose,
            "api_url": self.api_url,
            "api_timeout": self.api_timeout,
            "retries": self.retries,
            "max_retries": self.max_retries,
            "auto_refresh": self.auto_refresh,
        }

        result.update(cli_fields)

        # Add nested output structure for backward compatibility
        result["output"] = {"format": self.output_format}

        return result

    @property
    def is_development_mode(self) -> bool:
        """Check if in development mode."""
        return self.profile == "development" or self.debug

    @property
    def is_production_mode(self) -> bool:
        """Check if in production mode."""
        return self.profile == "production" and not self.debug

    # =========================================================================
    # CLI-SPECIFIC VALIDATION
    # =========================================================================

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI-specific business rules."""
        # Validate output format
        if self.output_format not in {"table", "json", "yaml", "csv"}:
            return FlextResult[None].fail(
                f"Invalid output format: {self.output_format}"
            )

        # Validate profile using Python 3.13+ walrus operator and modern validation
        if not self.profile or not (profile_stripped := self.profile.strip()):
            return FlextResult[None].fail("Profile name cannot be empty")

        # Validate timeouts
        if self.api_timeout <= 0 or self.connect_timeout <= 0:
            return FlextResult[None].fail("Timeout values must be positive")

        # Validate retries
        if self.retries < 0 or self.max_retries < 0:
            return FlextResult[None].fail("Retry values cannot be negative")

        return FlextResult[None].ok(None)

    def ensure_directories(self) -> FlextResult[None]:
        """Ensure CLI directories exist."""
        try:
            # Create essential directories
            for directory in [
                self.config_dir,
                self.cache_dir,
                self.log_dir,
                self.data_dir,
            ]:
                directory.mkdir(parents=True, exist_ok=True)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to create directories: {e}")

    def ensure_setup(self) -> FlextResult[None]:
        """Ensure CLI setup is complete (alias for ensure_directories)."""
        return self.ensure_directories()

    @classmethod
    def setup_cli(
        cls, config: FlextCliConfig | None = None
    ) -> FlextResult[FlextCliConfig]:
        """Set up CLI with configuration."""
        try:
            if config is None:
                config = cls.get_global_instance()

            # Validate configuration
            validation_result = config.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[FlextCliConfig].fail(
                    f"Configuration validation failed: {validation_result.error}"
                )

            return FlextResult[FlextCliConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextCliConfig].fail(f"CLI setup failed: {e}")

    # =========================================================================
    # FACTORY METHODS
    # =========================================================================

    @classmethod
    def create_development_config(cls) -> FlextResult[FlextCliConfig]:
        """Create development configuration."""
        try:
            config = cls(
                profile="development",
                debug=True,
                trace=True,
                log_level="DEBUG",
                verbose=True,
                output_format="table",
            )
            return FlextResult[FlextCliConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to create development config: {e}"
            )

    @classmethod
    def create_production_config(cls) -> FlextResult[FlextCliConfig]:
        """Create production configuration."""
        try:
            config = cls(
                profile="production",
                debug=False,
                log_level="INFO",
                quiet=True,
                output_format="json",
                verify_ssl=True,
            )
            return FlextResult[FlextCliConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to create production config: {e}"
            )

    @classmethod
    def get_global_instance(cls) -> FlextCliConfig:
        """Get global CLI configuration instance.

        Uses FlextConfig.get_global_instance() as the base and extends it
        with CLI-specific settings while preserving FlextCliConfig defaults
        and ensuring environment variables take precedence.
        """
        # Get base config from FlextConfig (single source of truth)
        base_config = FlextConfig.get_global_instance()

        # If the base config is already a FlextCliConfig, return it directly
        if isinstance(base_config, cls):
            return base_config

        base_data = base_config.model_dump()

        # Remove fields that should use FlextCliConfig defaults or environment variables
        # instead of base config values
        cli_specific_overrides = ["app_name"]  # FlextCliConfig should use "flext-cli"

        # Also remove fields that have environment variables set (so env vars take precedence)
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
            if field in base_data:
                del base_data[field]

        # Create CLI config extending the base - this will automatically pick up
        # environment variables due to Pydantic's SettingsConfigDict behavior
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
    def get_current(cls) -> FlextCliConfig:
        """Get current CLI configuration (alias for get_global_instance)."""
        return cls.get_global_instance()

    @classmethod
    def create_with_directories(
        cls, config_data: dict[str, object] | None = None
    ) -> FlextResult[FlextCliConfig]:
        """Create CLI configuration with directory setup."""
        try:
            # Create config with provided data
            config = cls(**config_data) if config_data else cls()

            # Ensure directories exist
            dir_result = config.ensure_directories()
            if dir_result.is_failure:
                return FlextResult[FlextCliConfig].fail(
                    f"Failed to create directories: {dir_result.error}"
                )

            return FlextResult[FlextCliConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextCliConfig].fail(f"Failed to create config: {e}")

    @classmethod
    def load_from_profile(cls, profile_name: str) -> FlextResult[FlextCliConfig]:
        """Load configuration from a specific profile."""
        try:
            if not profile_name or not profile_name.strip():
                return FlextResult[FlextCliConfig].fail("Profile name cannot be empty")

            config = cls(profile=profile_name.strip())
            return FlextResult[FlextCliConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to load profile '{profile_name}': {e}"
            )

    @classmethod
    def apply_cli_overrides(
        cls, cli_params: dict[str, object]
    ) -> FlextResult[FlextCliConfig]:
        """Apply CLI parameter overrides to configuration with proper precedence."""
        try:
            # Get current config
            current_config = cls.get_global_instance()

            # Map CLI params to config fields with precedence groups
            # Format: config_field -> [(priority, cli_param), ...]
            # Higher priority number = takes precedence
            param_mappings = {
                "profile": [(1, "profile")],
                "debug": [(1, "debug")],
                "output_format": [
                    (1, "output"),
                    (2, "output_format"),
                ],  # Long form takes precedence
                "log_level": [
                    (1, "log_level"),
                    (2, "log-level"),
                ],  # Kebab case takes precedence
                "quiet": [(1, "quiet")],
                "verbose": [(1, "verbose")],
                "no_color": [
                    (1, "no_color"),
                    (2, "no-color"),
                ],  # Kebab case takes precedence
                "api_url": [
                    (1, "api_url"),
                    (2, "api-url"),
                ],  # Kebab case takes precedence
                "timeout_seconds": [
                    (1, "timeout")
                ],  # timeout CLI param maps to timeout_seconds field
                "command_timeout": [
                    (1, "command_timeout"),
                    (2, "command-timeout"),
                ],  # Kebab case takes precedence
                "api_timeout": [
                    (1, "api_timeout"),
                    (2, "api-timeout"),
                ],  # Kebab case takes precedence
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
                new_config = cls(**{**current_config.model_dump(), **config_updates})
                cls.set_global_instance(new_config)
                return FlextResult[FlextCliConfig].ok(new_config)

            return FlextResult[FlextCliConfig].ok(current_config)
        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to apply CLI overrides: {e}"
            )

    @classmethod
    def sync_with_flext_config(cls) -> FlextResult[FlextCliConfig]:
        """Synchronize with base FlextConfig."""
        try:
            # Get base config
            base_config = FlextConfig.get_global_instance()

            # Create CLI config from base
            cli_config = cls(**base_config.model_dump())

            # Set as global
            cls.set_global_instance(cli_config)

            return FlextResult[FlextCliConfig].ok(cli_config)
        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to sync with FlextConfig: {e}"
            )

    @classmethod
    def ensure_flext_config_integration(cls) -> FlextResult[None]:
        """Ensure integration with FlextConfig is maintained."""
        try:
            # Verify that FlextConfig base functionality is working
            base_config = FlextConfig.get_global_instance()
            if base_config is None:
                return FlextResult[None].fail(
                    "FlextConfig global instance not available"
                )

            # Ensure CLI-specific extensions are compatible
            cli_config = cls.get_global_instance()

            # Basic validation that inheritance chain is intact
            if not isinstance(cli_config, FlextConfig):
                return FlextResult[None].fail(
                    "FlextCliConfig is not properly inheriting from FlextConfig"
                )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"FlextConfig integration check failed: {e}")

    @property
    def timeout(self) -> int:
        """Timeout alias for backward compatibility."""
        return self.timeout_seconds


__all__ = ["FlextCliConfig"]
