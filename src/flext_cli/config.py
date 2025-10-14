"""FLEXT CLI Config - Single flat Pydantic 2 Settings class for flext-cli.

Single FlextCliConfig class with nested configuration subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

from flext_core import FlextCore
from pydantic import (
    Field,
    SecretStr,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import SettingsConfigDict

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes

logger = FlextCore.Logger(__name__)


class FlextCliConfig(FlextCore.Config):
    """Single flat Pydantic 2 Settings class for flext-cli extending FlextCore.Config.

    Implements FlextCliProtocols.CliConfigProvider through structural subtyping.

    Follows standardized pattern:
    - Extends FlextCore.Config from flext-core directly (no nested classes)
    - Flat class structure with all fields at top level
    - All defaults from FlextCliConstants
    - SecretStr for sensitive data
    - Uses FlextCore.Config features for configuration management
    - Uses Python 3.13 + Pydantic 2 features
    """

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="allow",
        # Inherit enhanced Pydantic 2.11+ features from FlextCore.Config
        validate_assignment=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "title": "FLEXT CLI Configuration",
            "description": "Enterprise CLI configuration extending FlextCore.Config",
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

    no_color: bool = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_NO_COLOR,
        description="Disable colored output in CLI",
    )

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
    verbose: bool = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_VERBOSE,
        description="Enable verbose output",
    )
    debug: bool = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_DEBUG,
        description="Enable debug mode",
    )
    app_name: str = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_APP_NAME,
        description="Application name",
    )
    version: str = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_VERSION,
        description="Application version",
    )
    quiet: bool = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_QUIET,
        description="Enable quiet mode",
    )
    interactive: bool = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_INTERACTIVE,
        description="Enable interactive mode",
    )
    environment: str = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_ENVIRONMENT,
        description="Deployment environment",
    )

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
            msg = FlextCliConstants.ValidationMessages.INVALID_OUTPUT_FORMAT_MUST_BE.format(
                format=v, valid_formats=valid_formats
            )
            raise ValueError(msg)
        return v

    @field_validator("profile")
    @classmethod
    def validate_profile(cls, v: str) -> str:
        """Validate profile name is not empty."""
        if not v or not v.strip():
            msg = FlextCliConstants.ValidationMessages.PROFILE_NAME_CANNOT_BE_EMPTY
            raise ValueError(msg)
        return v.strip()

    @field_validator("api_url")
    @classmethod
    def validate_api_url(cls, v: str) -> str:
        """Validate API URL format."""
        if not v.startswith(("http://", "https://")):
            msg = (
                FlextCliConstants.ValidationMessages.INVALID_API_URL_MUST_START.format(
                    url=v
                )
            )
            raise ValueError(msg)
        return v

    @field_validator("log_level", "cli_log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        level_upper = v.upper()
        if level_upper not in valid_levels:
            msg = FlextCliConstants.ValidationMessages.INVALID_LOG_LEVEL_MUST_BE.format(
                level=v, valid_levels=", ".join(valid_levels)
            )
            raise ValueError(msg)
        return level_upper

    @field_validator("log_verbosity", "cli_log_verbosity")
    @classmethod
    def validate_log_verbosity(cls, v: str) -> str:
        """Validate log verbosity is one of the allowed values."""
        valid_verbosity = {"compact", "detailed", "full"}
        verbosity_lower = v.lower()
        if verbosity_lower not in valid_verbosity:
            msg = FlextCliConstants.ValidationMessages.INVALID_LOG_VERBOSITY_MUST_BE.format(
                verbosity=v, valid_verbosity=", ".join(valid_verbosity)
            )
            raise ValueError(msg)
        return verbosity_lower

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values."""
        valid_environments = {"development", "staging", "production", "test"}
        env_lower = v.lower()
        if env_lower not in valid_environments:
            msg = f"Invalid environment '{v}'. Must be one of: {', '.join(valid_environments)}"
            raise ValueError(msg)
        return env_lower

    @model_validator(mode="after")
    def validate_configuration(self) -> FlextCliConfig:
        """Validate configuration and auto-propagate to FlextCore.Context/FlextCore.Container.

        This method:
        1. Validates business rules from FlextCore.Config
        2. Ensures config directory exists
        3. Auto-propagates config to FlextCore.Context for global access
        4. Auto-registers in FlextCore.Container for dependency injection

        """
        # Use FlextCore.Config business rules validation
        validation_result = self.validate_business_rules()
        if validation_result.is_failure:
            msg = (
                FlextCliConstants.ErrorMessages.BUSINESS_RULES_VALIDATION_FAILED.format(
                    error=validation_result.error
                )
            )
            raise ValueError(msg)

        # Ensure config directory exists or can be created
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            msg = FlextCliConstants.ErrorMessages.CANNOT_ACCESS_CONFIG_DIR.format(
                config_dir=self.config_dir, error=e
            )
            raise ValueError(msg) from e

        # Auto-propagate config to FlextCore.Context for global access
        try:
            # Create context instance and set values
            context = FlextCore.Context()
            context.set("cli_config", self)
            context.set("cli_auto_output_format", self.auto_output_format)
            context.set("cli_auto_color_support", self.auto_color_support)
            context.set("cli_auto_verbosity", self.auto_verbosity)
            context.set("cli_optimal_table_format", self.optimal_table_format)
        except Exception as e:
            # FlextCore.Context might not be initialized yet - continue gracefully
            logger.debug(f"Context not available during config initialization: {e}")

        # Auto-register in FlextCore.Container for dependency injection
        try:
            container = FlextCore.Container.get_global()
            container.register("flext_cli_config", self)
        except Exception as e:
            # Container might not be initialized yet - continue gracefully
            logger.debug(f"Container not available during config initialization: {e}")

        return self

    # Pydantic 2 computed fields for smart auto-configuration
    @computed_field
    def auto_output_format(self) -> str:
        """Auto-detect optimal output format based on terminal capabilities.

        Detects:
        - Terminal width for best table format
        - Color support for styling
        - Interactive vs non-interactive mode

        Returns:
            str: Optimal output format (table, json, plain, etc.)

        """
        # Check if output is being piped (non-interactive)
        if not os.isatty(1):  # stdout is not a terminal
            return FlextCliConstants.OutputFormats.JSON.value

        # Get terminal width
        terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns

        # For narrow terminals, use simple format
        if terminal_width < FlextCliConstants.TERMINAL_WIDTH_NARROW:
            return FlextCliConstants.OutputFormats.PLAIN.value

        # For wide terminals with color support, use table
        if bool(self.auto_color_support):
            return FlextCliConstants.OutputFormats.TABLE.value

        # Fallback to JSON for compatibility
        return FlextCliConstants.OutputFormats.JSON.value

    @computed_field
    def auto_color_support(self) -> bool:
        """Auto-detect if terminal supports colors.

        Checks:
        - Configuration setting (no_color)

        Returns:
            bool: True if colors are supported, False otherwise

        """
        # Check if user explicitly disabled colors in config
        return not self.no_color

    @computed_field
    def auto_verbosity(self) -> str:
        """Auto-set verbosity based on configuration.

        Returns:
            str: Verbosity level (verbose, normal, quiet)

        """
        # Check if explicitly set via config
        if self.verbose:
            return "verbose"
        if self.quiet:
            return "quiet"

        # Default to normal verbosity
        return "normal"

    @computed_field
    def optimal_table_format(self) -> str:
        """Best tabulate format for current terminal width.

        Returns:
            str: Optimal tabulate format based on terminal width

        """
        terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns

        # Narrow terminals: simple format
        if terminal_width < FlextCliConstants.TERMINAL_WIDTH_NARROW:
            return "simple"

        # Medium terminals: github format
        if terminal_width < FlextCliConstants.TERMINAL_WIDTH_MEDIUM:
            return "github"

        # Wide terminals: grid format (most visually appealing)
        return "grid"

    # CLI-specific methods

    def validate_output_format_result(self, value: str) -> FlextCore.Result[str]:
        """Validate output format using FlextCliConstants and return FlextCore.Result."""
        if value not in FlextCliConstants.OUTPUT_FORMATS_LIST:
            return FlextCore.Result[str].fail(
                FlextCliConstants.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                    format=value
                )
            )
        return FlextCore.Result[str].ok(value)

    @classmethod
    def load_from_config_file(
        cls, config_file: Path
    ) -> FlextCore.Result[FlextCliConfig]:
        """Load configuration from file with proper error handling."""
        try:
            if not config_file.exists():
                return FlextCore.Result[FlextCliConfig].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(
                        file=config_file
                    )
                )

            # Load based on file extension
            if config_file.suffix.lower() == ".json":
                with config_file.open(
                    "r", encoding=FlextCliConstants.Encoding.UTF8
                ) as f:
                    data = json.load(f)
            elif config_file.suffix.lower() in {".yml", ".yaml"}:
                import yaml

                with config_file.open(
                    "r", encoding=FlextCliConstants.Encoding.UTF8
                ) as f:
                    data = yaml.safe_load(f)
            else:
                return FlextCore.Result[FlextCliConfig].fail(
                    FlextCliConstants.ErrorMessages.UNSUPPORTED_CONFIG_FORMAT.format(
                        suffix=config_file.suffix
                    )
                )

            # Create config instance directly with loaded data
            config = cls(**data)
            return FlextCore.Result[FlextCliConfig].ok(config)

        except Exception as e:
            return FlextCore.Result[FlextCliConfig].fail(
                FlextCliConstants.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=config_file, error=e
                )
            )

    def execute_as_service(self) -> FlextCore.Result[FlextCliTypes.Data.CliDataDict]:
        """Execute config as service operation."""
        return FlextCore.Result[FlextCliTypes.Data.CliDataDict].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": "flext-cli-config",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
            "config": self.model_dump(),
        })

    def update_from_cli_args(self, **kwargs: object) -> FlextCore.Result[None]:
        """Update configuration from CLI arguments with validation.

        Allows CLI commands to override configuration values dynamically.
        All updates are validated against Pydantic field validators.

        Args:
            **kwargs: Configuration key-value pairs to update

        Returns:
            FlextCore.Result[None]: Success or validation error

        Example:
            >>> config = FlextCliConfig()
            >>> result = config.update_from_cli_args(
            ...     profile="production", output_format="json", verbose=True
            ... )
            >>> result.is_success
            True

        """
        try:
            # Filter only valid configuration fields using dictionary comprehension
            valid_updates: FlextCore.Types.Dict = {
                key: value for key, value in kwargs.items() if hasattr(self, key)
            }

            # Apply updates using Pydantic's validation
            for key, value in valid_updates.items():
                setattr(self, key, value)

            # Re-validate entire model to ensure consistency
            self.model_validate(self.model_dump())

            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.CLI_ARGS_UPDATE_FAILED.format(error=e)
            )

    def merge_with_env(self) -> FlextCore.Result[None]:
        """Re-load environment variables and merge with current config.

        Useful when environment variables change during runtime.
        Existing config values take precedence over environment variables.

        Returns:
            FlextCore.Result[None]: Success or error

        Example:
            >>> config = FlextCliConfig()
            >>> # Environment changes
            >>> os.environ["FLEXT_CLI_PROFILE"] = "staging"
            >>> result = config.merge_with_env()
            >>> config.profile  # Will be "staging" if not already set

        """
        try:
            # Get current config snapshot
            current_config = self.model_dump()

            # Create new instance from environment
            env_config = FlextCliConfig()

            # Merge: current config overrides env
            for key, value in current_config.items():
                if value != getattr(self.__class__(), key, None):
                    # Value was explicitly set, keep it
                    setattr(env_config, key, value)

            # Copy merged config back
            for key in current_config:
                setattr(self, key, getattr(env_config, key))

            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.ENV_MERGE_FAILED.format(error=e)
            )

    def validate_cli_overrides(
        self, **overrides: object
    ) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Validate CLI overrides without applying them.

        Useful for checking if CLI arguments are valid before applying.

        Args:
            **overrides: Configuration overrides to validate

        Returns:
            FlextCore.Result[FlextCore.Types.Dict]: Valid overrides or validation errors

        Example:
            >>> config = FlextCliConfig()
            >>> result = config.validate_cli_overrides(
            ...     output_format="json", max_width=120
            ... )
            >>> if result.is_success:
            ...     config.update_from_cli_args(**result.unwrap())

        """
        try:
            valid_overrides: FlextCore.Types.Dict = {}
            errors: FlextCore.Types.StringList = []

            for key, value in overrides.items():
                # Check if field exists
                if not hasattr(self, key):
                    errors.append(
                        FlextCliConstants.ErrorMessages.UNKNOWN_CONFIG_FIELD.format(
                            field=key
                        )
                    )
                    continue

                # Try to validate the value
                try:
                    # Create test instance with override
                    test_config = self.model_copy()
                    setattr(test_config, key, value)
                    test_config.model_validate(test_config.model_dump())
                    valid_overrides[key] = value
                except Exception as e:
                    errors.append(
                        FlextCliConstants.ErrorMessages.INVALID_VALUE_FOR_FIELD.format(
                            field=key, error=e
                        )
                    )

            if errors:
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    FlextCliConstants.ErrorMessages.VALIDATION_ERRORS.format(
                        errors="; ".join(errors)
                    )
                )

            return FlextCore.Result[FlextCore.Types.Dict].ok(valid_overrides)

        except Exception as e:
            return FlextCore.Result[FlextCore.Types.Dict].fail(
                f"Validation failed: {e}"
            )

    # Protocol-compliant methods for CliConfigProvider
    def load_config(self) -> FlextCore.Result[FlextCliTypes.Data.CliConfigData]:
        """Load CLI configuration - implements CliConfigProvider protocol.

        Returns:
            FlextCore.Result[FlextCliTypes.Data.CliConfigData]: Configuration data or error

        """
        try:
            # Convert model to dictionary format expected by protocol
            config_data = self.model_dump()
            return FlextCore.Result[FlextCliTypes.Data.CliConfigData].ok(config_data)
        except Exception as e:
            return FlextCore.Result[FlextCliTypes.Data.CliConfigData].fail(
                FlextCliConstants.ErrorMessages.CONFIG_LOAD_FAILED_MSG.format(error=e)
            )

    def save_config(
        self, config: FlextCliTypes.Data.CliConfigData
    ) -> FlextCore.Result[None]:
        """Save CLI configuration - implements CliConfigProvider protocol.

        Args:
            config: Configuration data to save

        Returns:
            FlextCore.Result[None]: Success or error

        """
        try:
            # Update model fields with provided config data
            for key, value in config.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            # Validate the updated configuration
            self.model_validate(self.model_dump())
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(
                FlextCliConstants.ErrorMessages.CONFIG_SAVE_FAILED_MSG.format(error=e)
            )

    def validate_business_rules(self) -> FlextCore.Result[None]:
        """Validate configuration business rules.

        Returns:
            FlextCore.Result[None]: Success if all rules pass, error otherwise

        """
        try:
            # Basic validation rules for CLI config
            if not self.profile:
                return FlextCore.Result[None].fail("Profile cannot be empty")

            if not self.output_format:
                return FlextCore.Result[None].fail("Output format cannot be empty")

            if not self.config_dir:
                return FlextCore.Result[None].fail("Config directory cannot be empty")

            # Validate output format is supported
            supported_formats = [
                FlextCliConstants.OutputFormats.TABLE,
                FlextCliConstants.OutputFormats.JSON,
                FlextCliConstants.OutputFormats.YAML,
                FlextCliConstants.OutputFormats.CSV,
            ]
            if self.output_format not in supported_formats:
                return FlextCore.Result[None].fail(
                    f"Unsupported output format: {self.output_format}. "
                    f"Supported: {', '.join(supported_formats)}"
                )

            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(f"Business rules validation failed: {e}")


__all__ = [
    "FlextCliConfig",
]
