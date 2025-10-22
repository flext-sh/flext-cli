"""FLEXT CLI Config - Single flat Pydantic 2 Settings class for flext-cli.

Single FlextCliConfig class with nested configuration subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib
import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from flext_core import (
    FlextConfig,
    FlextContainer,
    FlextContext,
    FlextLogger,
    FlextResult,
    FlextTypes,
    LogLevel,
    RetryCount,
    TimeoutSeconds,
)
from pydantic import (
    Field,
    SecretStr,
    computed_field,
    model_validator,
)
from pydantic_settings import SettingsConfigDict

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes

logger = FlextLogger(__name__)


class FlextCliConfig(FlextConfig):
    """Single flat Pydantic 2 Settings class for flext-cli extending FlextConfig.

    Implements FlextCliProtocols.CliConfigProvider through structural subtyping.

    Follows standardized pattern:
    - Extends FlextConfig from flext-core directly (no nested classes)
    - Flat class structure with all fields at top level
    - All defaults from FlextCliConstants
    - SecretStr for sensitive data
    - Uses FlextConfig features for configuration management

    # Explicitly declare Pydantic methods for Pyrefly
    def model_dump(self, **kwargs) -> dict: ...
    def model_validate(self, obj) -> FlextCliConfig: ...
    def model_copy(self, **kwargs) -> FlextCliConfig: ...
    - Uses Python 3.13 + Pydantic 2 features
    """

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="allow",
        # Inherit enhanced Pydantic 2.11+ features from FlextConfig
        validate_assignment=True,
        str_strip_whitespace=True,
        # Environment parsing configuration
        env_parse_enums=True,
        json_schema_extra={
            FlextCliConstants.JsonSchemaKeys.TITLE: "FLEXT CLI Configuration",
            FlextCliConstants.JsonSchemaKeys.DESCRIPTION: "Enterprise CLI configuration extending FlextConfig",
        },
    )

    # CLI-specific configuration fields using FlextCliConstants for defaults
    profile: str = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_PROFILE,
        description="CLI profile to use for configuration",
    )

    output_format: Literal["json", "yaml", "csv", "table", "plain"] = Field(
        default="table",  # FlextCliConstants.OutputFormats.TABLE
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
        default=FlextCliConstants.ConfigDefaults.AUTO_REFRESH,
        description="Automatically refresh authentication tokens",
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

    trace: bool = Field(
        default=False,
        description="Enable trace mode (requires debug=True)",
    )

    # Inherited from FlextConfig - use parent's type
    # log_level: FlextConstants.Settings.LogLevel (defined in parent class)

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
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development",  # FlextCliConstants.CliDefaults.DEFAULT_ENVIRONMENT
        description="Deployment environment",
    )

    max_width: int = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_MAX_WIDTH,
        ge=FlextCliConstants.ValidationLimits.MIN_MAX_WIDTH,
        le=FlextCliConstants.ValidationLimits.MAX_MAX_WIDTH,
        description="Maximum width for CLI output",
    )

    config_file: Path | None = Field(
        default=None, description="Custom configuration file path"
    )

    # Network configuration
    cli_timeout: TimeoutSeconds = Field(
        default=FlextCliConstants.NetworkDefaults.DEFAULT_TIMEOUT,
        description="CLI network timeout in seconds",
    )

    max_retries: RetryCount = Field(
        default=FlextCliConstants.NetworkDefaults.DEFAULT_MAX_RETRIES,
        description="Maximum number of retry attempts",
    )

    # Logging configuration - centralized for all FLEXT projects
    log_verbosity: str = Field(  # Must match FlextConfig.log_verbosity type
        default="detailed",  # FlextCliConstants.CliDefaults.DEFAULT_LOG_VERBOSITY
        description="Logging verbosity (compact, detailed, full)",
    )

    cli_log_level: LogLevel = Field(
        default="INFO",  # FlextCliConstants.CliDefaults.DEFAULT_CLI_LOG_LEVEL
        description="CLI-specific logging level",
    )

    cli_log_verbosity: Literal["compact", "detailed", "full"] = Field(
        default="detailed",  # FlextCliConstants.CliDefaults.DEFAULT_CLI_LOG_VERBOSITY
        description="CLI-specific logging verbosity",
    )

    log_file: str | None = Field(
        default=None,
        description="Optional log file path for persistent logging",
    )

    # Pydantic 2.11 field validators
    @model_validator(mode="after")
    def validate_configuration(self) -> FlextCliConfig:
        """Validate configuration and auto-propagate to FlextContext/FlextContainer.

        This method:
        1. Validates business rules from FlextConfig
        2. Ensures config directory exists
        3. Auto-propagates config to FlextContext for global access
        4. Auto-registers in FlextContainer for dependency injection

        """
        # Use FlextConfig business rules validation
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

        # Auto-propagate config to FlextContext for global access
        try:
            # Resolve context dynamically so test monkeypatching works
            flext_core_module = importlib.import_module("flext_core")
            context_cls = getattr(flext_core_module, "FlextContext", FlextContext)
            context = context_cls()
            context.set("cli_config", self)
            context.set("cli_auto_output_format", self.auto_output_format)
            context.set("cli_auto_color_support", self.auto_color_support)
            context.set("cli_auto_verbosity", self.auto_verbosity)
            context.set("cli_optimal_table_format", self.optimal_table_format)
        except Exception as e:
            # FlextContext might not be initialized yet - continue gracefully
            logger.debug(f"Context not available during config initialization: {e}")

        # Auto-register in FlextContainer for dependency injection
        try:
            container = FlextContainer.get_global()
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
        if not os.isatty(FlextCliConstants.ConfigValidation.STDOUT_FD):
            return FlextCliConstants.OutputFormats.JSON.value

        # Get terminal width
        terminal_width = shutil.get_terminal_size(
            fallback=(
                FlextCliConstants.ConfigValidation.TERMINAL_FALLBACK_WIDTH,
                FlextCliConstants.ConfigValidation.TERMINAL_FALLBACK_HEIGHT,
            )
        ).columns

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
            return FlextCliConstants.ConfigDefaults.DEFAULT_VERBOSITY
        if self.quiet:
            return FlextCliConstants.ConfigDefaults.QUIET_VERBOSITY

        # Default to normal verbosity
        return FlextCliConstants.ConfigDefaults.NORMAL_VERBOSITY

    @computed_field
    def optimal_table_format(self) -> str:
        """Best tabulate format for current terminal width.

        Returns:
            str: Optimal tabulate format based on terminal width

        """
        terminal_width = shutil.get_terminal_size(
            fallback=(
                FlextCliConstants.ConfigValidation.TERMINAL_FALLBACK_WIDTH,
                FlextCliConstants.ConfigValidation.TERMINAL_FALLBACK_HEIGHT,
            )
        ).columns

        # Narrow terminals: simple format
        if terminal_width < FlextCliConstants.TERMINAL_WIDTH_NARROW:
            return FlextCliConstants.TableFormats.SIMPLE

        # Medium terminals: github format
        if terminal_width < FlextCliConstants.TERMINAL_WIDTH_MEDIUM:
            return FlextCliConstants.TableFormats.GITHUB

        # Wide terminals: grid format (most visually appealing)
        return FlextCliConstants.TableFormats.GRID

    # CLI-specific methods

    def validate_output_format_result(self, value: str) -> FlextResult[str]:
        """Validate output format using FlextCliConstants and return FlextResult."""
        if value not in FlextCliConstants.OUTPUT_FORMATS_LIST:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                    format=value
                )
            )
        return FlextResult[str].ok(value)

    @classmethod
    def load_from_config_file(cls, config_file: Path) -> FlextResult[FlextCliConfig]:
        """Load configuration from file with proper error handling."""
        try:
            if not config_file.exists():
                return FlextResult[FlextCliConfig].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(
                        file=config_file
                    )
                )

            # Load based on file extension
            if config_file.suffix.lower() == FlextCliConstants.FileExtensions.JSON:
                with config_file.open(
                    "r", encoding=FlextCliConstants.Encoding.UTF8
                ) as f:
                    data = json.load(f)
            elif (
                config_file.suffix.lower()
                in FlextCliConstants.ConfigValidation.YAML_EXTENSIONS
            ):
                import yaml

                with config_file.open(
                    "r", encoding=FlextCliConstants.Encoding.UTF8
                ) as f:
                    data = yaml.safe_load(f)
            else:
                return FlextResult[FlextCliConfig].fail(
                    FlextCliConstants.ErrorMessages.UNSUPPORTED_CONFIG_FORMAT.format(
                        suffix=config_file.suffix
                    )
                )

            # Create config instance directly with loaded data
            config = cls(**data)
            return FlextResult[FlextCliConfig].ok(config)

        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                FlextCliConstants.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=config_file, error=e
                )
            )

    def execute_as_service(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute config as service operation."""
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok({
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.ConfigDefaults.DEFAULT_SERVICE_NAME,
            FlextCliConstants.DictKeys.TIMESTAMP: datetime.now(UTC).isoformat(),
            FlextCliConstants.DictKeys.VERSION: FlextCliConstants.ConfigDefaults.DEFAULT_VERSION_STRING,
            FlextCliConstants.DictKeys.CONFIG: self.model_dump(),
        })

    def update_from_cli_args(self, **kwargs: FlextTypes.JsonValue) -> FlextResult[None]:
        """Update configuration from CLI arguments with validation.

        Allows CLI commands to override configuration values dynamically.
        All updates are validated against Pydantic field validators.

        Args:
            **kwargs: Configuration key-value pairs to update

        Returns:
            FlextResult[None]: Success or validation error

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
            valid_updates: dict[str, object] = {
                key: value for key, value in kwargs.items() if hasattr(self, key)
            }

            # Apply updates using Pydantic's validation
            for key, value in valid_updates.items():
                setattr(self, key, value)

            # Re-validate entire model to ensure consistency
            self.model_validate(self.model_dump())

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.CLI_ARGS_UPDATE_FAILED.format(error=e)
            )

    def merge_with_env(self) -> FlextResult[None]:
        """Re-load environment variables and merge with current config.

        Useful when environment variables change during runtime.
        Existing config values take precedence over environment variables.

        Returns:
            FlextResult[None]: Success or error

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

            # Read-only/computed fields that cannot be set (includes FlextConfig computed fields)
            readonly_fields = {
                "auto_output_format",
                "auto_color_support",
                "auto_verbosity",
                "optimal_table_format",
                "effective_log_level",
                "effective_timeout",
                "has_cache",
                "has_database",
                "is_debug_enabled",
                "is_production",
            }

            # Create new instance from environment
            env_config = FlextCliConfig()

            # Merge: current config overrides env (skip read-only fields)
            for key, value in current_config.items():
                if key not in readonly_fields and value != getattr(
                    self.__class__(), key, None
                ):
                    # Value was explicitly set, keep it
                    setattr(env_config, key, value)

            # Copy merged config back (skip read-only fields)
            for key in current_config:
                if key not in readonly_fields:
                    setattr(self, key, getattr(env_config, key))

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.ENV_MERGE_FAILED.format(error=e)
            )

    def validate_cli_overrides(
        self, **overrides: FlextTypes.JsonValue
    ) -> FlextResult[dict[str, object]]:
        """Validate CLI overrides without applying them.

        Useful for checking if CLI arguments are valid before applying.

        Args:
            **overrides: Configuration overrides to validate

        Returns:
            FlextResult[dict[str, object]]: Valid overrides or validation errors

        Example:
            >>> config = FlextCliConfig()
            >>> result = config.validate_cli_overrides(
            ...     output_format="json", max_width=120
            ... )
            >>> if result.is_success:
            ...     config.update_from_cli_args(**result.unwrap())

        """
        try:
            valid_overrides: dict[str, object] = {}
            errors: list[str] = []

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
                return FlextResult[dict[str, object]].fail(
                    FlextCliConstants.ErrorMessages.VALIDATION_ERRORS.format(
                        errors="; ".join(errors)
                    )
                )

            return FlextResult[dict[str, object]].ok(valid_overrides)

        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Validation failed: {e}")

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
                FlextCliConstants.ErrorMessages.CONFIG_LOAD_FAILED_MSG.format(error=e)
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
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.CONFIG_SAVE_FAILED_MSG.format(error=e)
            )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate configuration business rules.

        Returns:
            FlextResult[None]: Success if all rules pass, error otherwise

        """
        try:
            # Basic validation rules for CLI config
            if not self.profile:
                return FlextResult[None].fail("Profile cannot be empty")

            if not self.config_dir:
                return FlextResult[None].fail("Config directory cannot be empty")

            # Validate output format is supported
            supported_formats = [
                FlextCliConstants.OutputFormats.TABLE.value,
                FlextCliConstants.OutputFormats.JSON.value,
                FlextCliConstants.OutputFormats.YAML.value,
                FlextCliConstants.OutputFormats.CSV.value,
            ]
            if self.output_format not in supported_formats:
                supported_list = ", ".join(supported_formats)
                message = f"Unsupported output format: {self.output_format}. Supported: {supported_list}"
                return FlextResult[None].fail(message)

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Business rules validation failed: {e}")


__all__ = [
    "FlextCliConfig",
]
