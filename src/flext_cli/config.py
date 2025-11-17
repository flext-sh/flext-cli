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
from typing import Annotated, Self

from flext_core import (
    FlextConfig,
    FlextConstants,
    FlextContainer,
    FlextContext,
    FlextLogger,
    FlextResult,
    FlextTypes,
    RetryCount,
    TimeoutSeconds,
)
from pydantic import (
    Field,
    SecretStr,
    StringConstraints,
    computed_field,
    model_validator,
)
from pydantic_settings import SettingsConfigDict

from flext_cli._models_config import ConfigServiceExecutionResult
from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes

# Alias LogLevel from FlextConstants (moved from flext_core direct export)
LogLevel = FlextConstants.Settings.LogLevel

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
    def model_dump(self, **kwargs) -> FlextTypes.JsonDict: ...
    def model_validate(self, obj: object, **kwargs) -> FlextCliConfig: ...
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
    # Using Annotated with StringConstraints for automatic validation (Pydantic 2)
    profile: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)] = (
        Field(
            default=FlextCliConstants.CliDefaults.DEFAULT_PROFILE,
            description="CLI profile to use for configuration",
        )
    )

    output_format: FlextCliConstants.OutputFormatLiteral = Field(
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
    environment: FlextCliConstants.EnvironmentLiteral = Field(
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
        default=FlextConstants.Settings.LogLevel.INFO,  # Use enum value from constants
        description="CLI-specific logging level",
    )

    cli_log_verbosity: FlextCliConstants.LogVerbosityLiteral = Field(
        default="detailed",  # FlextCliConstants.CliDefaults.DEFAULT_CLI_LOG_VERBOSITY
        description="CLI-specific logging verbosity",
    )

    log_file: str | None = Field(
        default=None,
        description="Optional log file path for persistent logging",
    )

    # Pydantic 2.11 model validator (runs after all field validators)
    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        """Validate configuration using functional composition and railway pattern.

        This method runs AFTER all field validators, implementing comprehensive
        configuration validation with functional error handling and auto-setup.

        Uses railway pattern for:
        1. Directory creation with proper error handling
        2. Context propagation with graceful degradation
        3. Container registration with conflict avoidance

        """

        # Functional directory validation using railway pattern
        def ensure_config_directory() -> FlextResult[Path]:
            """Ensure config directory exists with proper error handling."""
            try:
                self.config_dir.mkdir(parents=True, exist_ok=True)
                return FlextResult.ok(self.config_dir)
            except (PermissionError, OSError) as e:
                error_msg = (
                    FlextCliConstants.ErrorMessages.CANNOT_ACCESS_CONFIG_DIR.format(
                        config_dir=self.config_dir, error=e
                    )
                )
                return FlextResult.fail(error_msg)

        # Functional context propagation with graceful degradation
        def propagate_to_context() -> FlextResult[bool]:
            """Propagate configuration to FlextContext with error recovery."""
            try:
                # Resolve context dynamically for test compatibility
                flext_core_module = importlib.import_module("flext_core")
                context_cls = getattr(flext_core_module, "FlextContext", FlextContext)
                context = context_cls() if context_cls else FlextContext()

                # Propagate configuration values
                context.set("cli_config", self)
                context.set("cli_auto_output_format", self.auto_output_format)
                context.set("cli_auto_color_support", self.auto_color_support)
                context.set("cli_auto_verbosity", self.auto_verbosity)
                context.set("cli_optimal_table_format", self.optimal_table_format)

                return FlextResult[bool].ok(True)
            except Exception as e:
                # Log but don't fail - context might not be initialized yet
                logger.debug(
                    "Context not available during config initialization: %s", e
                )
                return FlextResult[bool].ok(True)  # Graceful degradation

        # Functional container registration with conflict avoidance
        def register_in_container() -> FlextResult[bool]:
            """Register configuration in FlextContainer for dependency injection."""
            try:
                container = FlextContainer.get_global()
                # Register only if not already registered (avoids test conflicts)
                if not container.has_service("flext_cli_config"):
                    container.with_service("flext_cli_config", self)
                return FlextResult[bool].ok(True)
            except Exception as e:
                # Container might not be initialized yet - continue gracefully
                logger.debug(
                    "Container not available during config initialization: %s", e
                )
                return FlextResult[bool].ok(True)  # Graceful degradation

        # Execute validation pipeline using railway pattern
        validation_result = (
            ensure_config_directory()
            .flat_map(lambda _: propagate_to_context())
            .flat_map(lambda _: register_in_container())
        )

        # Convert validation result to configuration result
        if validation_result.is_failure:
            msg = f"Configuration validation failed: {validation_result.error}"
            raise ValueError(msg)

        return self

    # Pydantic 2 computed fields for smart auto-configuration
    @computed_field
    def auto_output_format(self) -> str:
        """Auto-detect optimal output format using functional composition and railway pattern.

        Detects terminal capabilities using functional pipeline:
        - Interactive vs piped output detection
        - Terminal width assessment
        - Color support evaluation
        - Format selection based on capabilities

        Returns:
            str: Optimal output format (table, json, plain, etc.)

        """

        # Functional terminal capability detection
        def detect_interactive_mode() -> FlextResult[bool]:
            """Detect if output is interactive (not piped)."""
            is_interactive = os.isatty(FlextCliConstants.ConfigValidation.STDOUT_FD)
            return FlextResult.ok(is_interactive)

        def get_terminal_width() -> FlextResult[int]:
            """Get terminal width - fast-fail on error."""
            try:
                terminal_size = shutil.get_terminal_size()
                return FlextResult.ok(terminal_size.columns)
            except Exception as e:
                return FlextResult[int].fail(f"Failed to get terminal width: {e}")

        def determine_format(is_interactive: bool, width: int, has_color: bool) -> str:
            """Determine optimal format based on capabilities."""
            # Non-interactive always uses JSON
            if not is_interactive:
                return FlextCliConstants.OutputFormats.JSON.value

            # Narrow terminals use plain format
            if width < FlextCliConstants.TERMINAL_WIDTH_NARROW:
                return FlextCliConstants.OutputFormats.PLAIN.value

            # Color terminals use table format
            if has_color:
                return FlextCliConstants.OutputFormats.TABLE.value

            # Default to JSON for non-color interactive terminals
            return FlextCliConstants.OutputFormats.JSON.value

        # Railway pattern: detect capabilities then determine format
        result = (
            detect_interactive_mode()
            .flat_map(
                lambda interactive: get_terminal_width().map(
                    lambda width: (interactive, width)
                )
            )
            .map(
                lambda capabilities: determine_format(
                    capabilities[0],  # is_interactive
                    capabilities[1],  # width
                    bool(self.auto_color_support),  # has_color
                )
            )
        )
        if result.is_success:
            return result.unwrap()
        # Fast-fail: return error format on failure
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
        """Auto-set verbosity using functional pattern matching and railway approach.

        Determines verbosity level based on configuration flags with clear priority:
        - Explicit verbose flag takes precedence
        - Quiet flag overrides normal
        - Falls back to normal verbosity

        Returns:
            str: Verbosity level (verbose, normal, quiet)

        """

        # Functional verbosity determination using pattern matching
        def determine_verbosity() -> str:
            """Determine verbosity level based on configuration."""
            match (self.verbose, self.quiet):
                case (True, _):  # Verbose takes precedence
                    return FlextCliConstants.ConfigDefaults.DEFAULT_VERBOSITY
                case (_, True):  # Quiet overrides normal
                    return FlextCliConstants.ConfigDefaults.QUIET_VERBOSITY
                case _:  # Default case
                    return FlextCliConstants.ConfigDefaults.NORMAL_VERBOSITY

        # Railway pattern: validate and determine verbosity
        result = FlextResult.ok((self.verbose, self.quiet)).map(
            lambda _: determine_verbosity()
        )
        if result.is_success:
            return result.unwrap()
        # Fast-fail: return normal verbosity on failure
        return FlextCliConstants.ConfigDefaults.NORMAL_VERBOSITY

    @computed_field
    def optimal_table_format(self) -> str:
        """Determine optimal table format using functional composition and railway pattern.

        Analyzes terminal width using functional pipeline to select the best
        tabulate format for optimal visual presentation.

        Returns:
            str: Optimal tabulate format (simple, github, grid)

        """

        # Functional terminal width detection
        def get_terminal_width() -> FlextResult[int]:
            """Get terminal width - fast-fail on error."""
            try:
                terminal_size = shutil.get_terminal_size()
                return FlextResult.ok(terminal_size.columns)
            except Exception as e:
                return FlextResult[int].fail(f"Failed to get terminal width: {e}")

        def select_table_format(width: int) -> str:
            """Select optimal table format based on terminal width."""
            if width < FlextCliConstants.TERMINAL_WIDTH_NARROW:
                return FlextCliConstants.TableFormats.SIMPLE
            if width < FlextCliConstants.TERMINAL_WIDTH_MEDIUM:
                return FlextCliConstants.TableFormats.GITHUB
            return FlextCliConstants.TableFormats.GRID

        # Railway pattern: get width then select format
        result = get_terminal_width().map(select_table_format)
        if result.is_success:
            return result.unwrap()
        # Fast-fail: return simple format on failure
        return FlextCliConstants.TableFormats.SIMPLE

    # CLI-specific methods

    def validate_output_format_result(self, value: str) -> FlextResult[str]:
        """Validate output format using functional composition and railway pattern.

        Performs format validation using functional pipeline with clear error
        messages and type-safe result handling.

        Args:
            value: Output format to validate

        Returns:
            FlextResult[str]: Validated format or error with details

        """

        # Functional validation using railway pattern
        def check_format_exists(fmt: str) -> FlextResult[str]:
            """Check if format exists in allowed list."""
            if fmt in FlextCliConstants.OUTPUT_FORMATS_LIST:
                return FlextResult.ok(fmt)
            return FlextResult.fail(
                FlextCliConstants.ErrorMessages.INVALID_OUTPUT_FORMAT.format(format=fmt)
            )

        # Railway pattern: validate input then check format
        return FlextResult.ok(value).flat_map(check_format_exists)

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
        """Execute config as service operation.

        Pydantic 2 Modernization:
            - Uses ConfigServiceExecutionResult model internally
            - Serializes to dict for API compatibility
            - Type-safe with field validation

        """
        # Convert Path objects to strings for JSON compatibility
        config_dict = self.model_dump()
        # Convert PosixPath to str for JSON serialization
        for key, value in config_dict.items():
            if isinstance(value, Path):
                config_dict[key] = str(value)

        # Create Pydantic model with type-safe fields
        result_model = ConfigServiceExecutionResult(
            status=FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            service=FlextCliConstants.ConfigDefaults.DEFAULT_SERVICE_NAME,
            timestamp=datetime.now(UTC).isoformat(),
            version=FlextCliConstants.ConfigDefaults.DEFAULT_VERSION_STRING,
            config=config_dict,
        )
        # Serialize to dict for API compatibility
        result_dict: FlextCliTypes.Data.CliDataDict = result_model.model_dump()
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok(result_dict)

    def update_from_cli_args(self, **kwargs: FlextTypes.JsonValue) -> FlextResult[bool]:
        """Update configuration from CLI arguments with validation.

        Allows CLI commands to override configuration values dynamically.
        All updates are validated against Pydantic field validators.

        Args:
            **kwargs: Configuration key-value pairs to update

        Returns:
            FlextResult[bool]: True if update succeeded, failure on error

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
            valid_updates: FlextTypes.JsonDict = {
                key: value for key, value in kwargs.items() if hasattr(self, key)
            }

            # Apply updates using Pydantic's validation
            for key, value in valid_updates.items():
                setattr(self, key, value)

            # Re-validate entire model to ensure consistency
            self.model_validate(self.model_dump())

            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.CLI_ARGS_UPDATE_FAILED.format(error=e)
            )

    def merge_with_env(self) -> FlextResult[bool]:
        """Re-load environment variables and merge with current config.

        Useful when environment variables change during runtime.
        Existing config values take precedence over environment variables.

        Returns:
            FlextResult[bool]: True if merge succeeded, failure on error

        Example:
            >>> config = FlextCliConfig()
            >>> # Environment changes
            >>> os.environ["FLEXT_CLI_PROFILE"] = "staging"
            >>> result = config.merge_with_env()
            >>> config.profile  # Will be "staging" if not already set

        """
        try:
            # Get current config snapshot
            # Convert Path objects to strings for JSON compatibility
            config_dict = self.model_dump()
            # Convert PosixPath to str for JSON serialization
            for key, value in config_dict.items():
                if isinstance(value, Path):
                    config_dict[key] = str(value)

            current_config = config_dict

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

            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.ENV_MERGE_FAILED.format(error=e)
            )

    def validate_cli_overrides(
        self, **overrides: FlextTypes.JsonValue
    ) -> FlextResult[FlextTypes.JsonDict]:
        """Validate CLI overrides without applying them.

        Useful for checking if CLI arguments are valid before applying.

        Args:
            **overrides: Configuration overrides to validate

        Returns:
            FlextResult[FlextTypes.JsonDict]: Valid overrides or validation errors

        Example:
            >>> config = FlextCliConfig()
            >>> result = config.validate_cli_overrides(
            ...     output_format="json", max_width=120
            ... )
            >>> if result.is_success:
            ...     config.update_from_cli_args(**result.unwrap())

        """
        try:
            valid_overrides: FlextTypes.JsonDict = {}
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
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.ErrorMessages.VALIDATION_ERRORS.format(
                        errors="; ".join(errors)
                    )
                )

            return FlextResult[FlextTypes.JsonDict].ok(valid_overrides)

        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(f"Validation failed: {e}")

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
    ) -> FlextResult[bool]:
        """Save CLI configuration - implements CliConfigProvider protocol.

        Args:
            config: Configuration data to save

        Returns:
            FlextResult[bool]: True if save succeeded, failure on error

        """
        try:
            # Update model fields with provided config data
            for key, value in config.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            # Validate the updated configuration
            self.model_validate(self.model_dump())
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.CONFIG_SAVE_FAILED_MSG.format(error=e)
            )


__all__ = [
    "FlextCliConfig",
]
