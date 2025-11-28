"""FLEXT CLI Configuration Module.

**MODULE**: FlextCliConfig - Enterprise CLI configuration management
**SCOPE**: Pydantic 2 settings, environment variables, terminal detection, output formatting,
          singleton pattern, functional validation, railway-oriented error handling

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib
import json
import os
import shutil
from pathlib import Path
from typing import Annotated, ClassVar, Self, cast

import yaml
from flext_core import (
    FlextConfig,
    FlextConstants,
    FlextContainer,
    FlextContext,
    FlextLogger,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)
from pydantic import (
    Field,
    SecretStr,
    StringConstraints,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes
from flext_cli.utilities import FlextCliUtilities

# Alias LogLevel from FlextConstants (moved from flext_core direct export)
LogLevel = FlextConstants.Settings.LogLevel

logger = FlextLogger(__name__)


@FlextConfig.auto_register("cli")
class FlextCliConfig(BaseSettings):
    """Single flat Pydantic 2 BaseModel class for flext-cli using AutoConfig pattern.

    **ARCHITECTURAL PATTERN**: Zero-Boilerplate Auto-Registration

    This class uses FlextConfig.AutoConfig for automatic:
    - Singleton pattern (thread-safe)
    - Namespace registration (accessible via config.cli)
    - Test reset capability (_reset_instance)

    Implements FlextCliProtocols.CliConfigProvider through structural subtyping.

    Follows standardized pattern:
    - Extends FlextConfig.AutoConfig (BaseModel) for nested config pattern
    - Flat class structure with all fields at top level
    - All defaults from FlextCliConstants
    - SecretStr for sensitive data
    - Uses FlextConfig namespace features for configuration management

    **Usage**:
        # Get singleton instance
        config = FlextCliConfig.get_instance()

        # Or via FlextConfig namespace
        from flext_core import FlextConfig
        config = FlextConfig.get_global_instance()
        cli_config = config.cli

    - Uses Python 3.13 + Pydantic 2 features
    """

    # Use FlextConfig.resolve_env_file() to ensure all FLEXT configs use same .env
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="allow",
        # Pydantic Settings environment variable support
        env_prefix="FLEXT_CLI_",
        env_file=FlextConfig.resolve_env_file(),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        # Inherit enhanced Pydantic 2.11+ features
        validate_assignment=True,
        str_strip_whitespace=True,
        validate_default=True,
        frozen=False,
        arbitrary_types_allowed=True,
        # Allow type coercion from environment variables (required for bool, int, etc.)
        strict=False,
        json_schema_extra={
            FlextCliConstants.JsonSchemaKeys.TITLE: "FLEXT CLI Configuration",
            FlextCliConstants.JsonSchemaKeys.DESCRIPTION: "Enterprise CLI configuration using AutoConfig pattern",
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

    # Python 3.13+ best practice: Use Enum value for default consistency
    # Pydantic 2 accepts Enum values in Literal-typed fields
    output_format: FlextCliConstants.OutputFormatLiteral = Field(
        default=FlextCliConstants.OutputFormats.TABLE.value,
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
        default=None,
        description="API key for authentication (sensitive)",
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
    # Core fields needed for CLI operations - using Pydantic Settings pattern
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    trace: bool = Field(
        default=False,
        description="Enable trace mode (requires debug=True)",
    )
    verbose: bool = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_VERBOSE,
        description="Enable verbose CLI output",
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
    environment: FlextCliConstants.EnvironmentLiteral = Field(
        default=FlextCliConstants.Environment.DEVELOPMENT.value,  # Python 3.13+ best practice: Use Enum value
        description="Deployment environment",
    )

    max_width: int = Field(
        default=FlextCliConstants.CliDefaults.DEFAULT_MAX_WIDTH,
        ge=FlextCliConstants.ValidationLimits.MIN_MAX_WIDTH,
        le=FlextCliConstants.ValidationLimits.MAX_MAX_WIDTH,
        description="Maximum width for CLI output",
    )

    config_file: Path | None = Field(
        default=None,
        description="Custom configuration file path",
    )

    # Network configuration
    cli_timeout: float = Field(
        default=FlextCliConstants.NetworkDefaults.DEFAULT_TIMEOUT,
        description="CLI network timeout in seconds",
        ge=0,
        le=300,
    )

    max_retries: int = Field(
        default=FlextCliConstants.NetworkDefaults.DEFAULT_MAX_RETRIES,
        description="Maximum number of retry attempts",
        ge=0,
        le=10,
    )

    # Logging configuration - centralized for all FLEXT projects
    log_verbosity: str = Field(  # Must match FlextConfig.log_verbosity type
        default=FlextCliConstants.LogVerbosity.DETAILED.value,  # Python 3.13+ best practice: Use Enum value
        description="Logging verbosity (compact, detailed, full)",
    )

    cli_log_level: LogLevel = Field(
        default=FlextConstants.Settings.LogLevel.INFO,  # Use enum value from constants
        description="CLI-specific logging level",
    )

    cli_log_verbosity: FlextCliConstants.LogVerbosityLiteral = Field(
        default=FlextCliConstants.LogVerbosity.DETAILED.value,  # Python 3.13+ best practice: Use Enum value
        description="CLI-specific logging verbosity",
    )

    log_file: str | None = Field(
        default=None,
        description="Optional log file path for persistent logging",
    )

    console_enabled: bool = Field(
        default=FlextConstants.Logging.CONSOLE_ENABLED,
        description="Enable console logging output",
    )

    def _ensure_config_directory(self) -> FlextResult[Path]:
        """Ensure config directory exists with proper error handling."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            return FlextResult.ok(self.config_dir)
        except (PermissionError, OSError) as e:
            error_msg = FlextCliConstants.ErrorMessages.CANNOT_ACCESS_CONFIG_DIR.format(
                config_dir=self.config_dir,
                error=e,
            )
            return FlextResult.fail(error_msg)

    def _propagate_to_context(self) -> FlextResult[bool]:
        """Propagate configuration to FlextContext with error recovery."""
        try:
            flext_core_module = importlib.import_module("flext_core")
            context_cls = getattr(flext_core_module, "FlextContext", FlextContext)
            context = context_cls() if context_cls else FlextContext()
            _ = context.set("cli_config", self)
            _ = context.set("cli_auto_output_format", self.auto_output_format)
            _ = context.set("cli_auto_color_support", self.auto_color_support)
            _ = context.set("cli_auto_verbosity", self.auto_verbosity)
            _ = context.set("cli_optimal_table_format", self.optimal_table_format)
            return FlextResult[bool].ok(True)
        except Exception as e:
            logger.debug("Context not available during config initialization: %s", e)
            return FlextResult[bool].ok(True)

    def _register_in_container(self) -> FlextResult[bool]:
        """Register configuration in FlextContainer for dependency injection."""
        try:
            container = FlextContainer()
            if not container.has_service("flext_cli_config"):
                _ = container.with_service("flext_cli_config", self)
            return FlextResult[bool].ok(True)
        except Exception as e:
            logger.debug("Container not available during config initialization: %s", e)
            return FlextResult[bool].ok(True)

    # Pydantic 2.11 model validator (runs after all field validators)
    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        """Validate configuration using functional composition and railway pattern."""
        validation_result = (
            self._ensure_config_directory()
            .flat_map(lambda _: self._propagate_to_context())
            .flat_map(lambda _: self._register_in_container())
        )
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
                    lambda width: (interactive, width),
                ),
            )
            .map(
                lambda capabilities: determine_format(
                    capabilities[0]
                    if isinstance(capabilities, tuple)
                    and len(capabilities)
                    >= FlextCliConstants.ConfigValidation.CAPABILITIES_TUPLE_MIN_LENGTH
                    else False,  # is_interactive
                    capabilities[1]
                    if isinstance(capabilities, tuple)
                    and len(capabilities)
                    >= FlextCliConstants.ConfigValidation.CAPABILITIES_TUPLE_MIN_LENGTH
                    else FlextCliConstants.ConfigValidation.DEFAULT_TERMINAL_WIDTH,
                    bool(self.auto_color_support),  # has_color
                ),
            )
        )
        if result.is_success:
            format_result = result.unwrap()
            # Type narrowing: determine_format returns str
            if isinstance(format_result, str):
                return format_result
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
        def map_to_verbosity(_: tuple[bool, bool]) -> str:
            """Map tuple to verbosity level."""
            return determine_verbosity()

        result = FlextResult.ok((self.verbose, self.quiet)).map(map_to_verbosity)
        if result.is_success:
            verbosity_result = result.unwrap()
            # Type narrowing: map_to_verbosity returns str
            if isinstance(verbosity_result, str):
                return verbosity_result
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
            format_result = result.unwrap()
            # Type narrowing: select_table_format returns str
            if isinstance(format_result, str):
                return format_result
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
                FlextCliConstants.ErrorMessages.INVALID_OUTPUT_FORMAT.format(
                    format=fmt,
                ),
            )

        # Railway pattern: validate input then check format
        # Create wrapper to ensure type compatibility with flat_map
        def check_format_wrapper(fmt: str) -> FlextResult[str]:
            """Wrapper to convert FlextResult[str] to FlextResult[str]."""
            result = check_format_exists(fmt)
            if result.is_success:
                return FlextResult[str].ok(result.unwrap())
            return FlextResult[str].fail(result.error or "Format validation failed")

        format_result = FlextResult.ok(value).flat_map(check_format_wrapper)
        # Convert back to FlextResult[str]
        if format_result.is_success:
            format_value = format_result.unwrap()
            if isinstance(format_value, str):
                return FlextResult[str].ok(format_value)
        return FlextResult[str].fail(format_result.error or "Format validation failed")

    @classmethod
    def load_from_config_file(cls, config_file: Path) -> FlextResult[FlextCliConfig]:
        """Load configuration from file with proper error handling."""
        try:
            if not config_file.exists():
                return FlextResult[FlextCliConfig].fail(
                    FlextCliConstants.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(
                        file=config_file,
                    ),
                )

            # Load based on file extension
            if config_file.suffix.lower() == FlextCliConstants.FileExtensions.JSON:
                with config_file.open(
                    "r",
                    encoding=FlextCliConstants.Encoding.UTF8,
                ) as f:
                    data = json.load(f)
            elif (
                config_file.suffix.lower()
                in FlextCliConstants.ConfigValidation.YAML_EXTENSIONS
            ):
                with config_file.open(
                    "r",
                    encoding=FlextCliConstants.Encoding.UTF8,
                ) as f:
                    data = yaml.safe_load(f)
            else:
                return FlextResult[FlextCliConfig].fail(
                    FlextCliConstants.ErrorMessages.UNSUPPORTED_CONFIG_FORMAT.format(
                        suffix=config_file.suffix,
                    ),
                )

            # Create config instance directly with loaded data
            config = cls(**data)
            return FlextResult[FlextCliConfig].ok(config)

        except Exception as e:
            return FlextResult[FlextCliConfig].fail(
                FlextCliConstants.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(
                    file=config_file,
                    error=e,
                ),
            )

    def execute_as_service(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute config as service operation.

        Pydantic 2 Modernization:
            - Uses ConfigServiceExecutionResult model internally
            - Serializes to dict for API compatibility
            - Type-safe with field validation

        """
        # Convert to JSON-compatible dict using model_dump() and DataMapper
        # Handles Path→str, primitives as-is, nested dicts/lists, and other types via str()
        config_dict_raw = self.model_dump()
        # Use DataMapper to get CliJsonDict (dict[str, CliJsonValue])
        config_as_json_value = FlextCliUtilities.DataMapper.convert_dict_to_json(
            config_dict_raw
        )
        result_dict: FlextCliTypes.Data.CliDataDict = {
            "status": FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            "service": FlextCliConstants.ConfigDefaults.DEFAULT_SERVICE_NAME,
            "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
            "version": FlextCliConstants.ConfigDefaults.DEFAULT_VERSION_STRING,
            "config": config_as_json_value,  # CliJsonDict is compatible with CliJsonValue
        }
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok(result_dict)

    def update_from_cli_args(
        self, **kwargs: FlextCliTypes.CliJsonValue
    ) -> FlextResult[bool]:
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
            _ = self.model_validate(self.model_dump())

            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.CLI_ARGS_UPDATE_FAILED.format(error=e),
            )

    def validate_cli_overrides(
        self,
        **overrides: FlextCliTypes.CliJsonValue,
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
            # Use mutable dict for building, then convert to JsonDict for return
            valid_overrides: dict[str, FlextTypes.Json.JsonValue] = {}
            errors: list[str] = []

            for key, value in overrides.items():
                # Check if field exists
                if not hasattr(self, key):
                    errors.append(
                        FlextCliConstants.ErrorMessages.UNKNOWN_CONFIG_FIELD.format(
                            field=key,
                        ),
                    )
                    continue

                # Try to validate the value
                try:
                    # Create test instance with override
                    test_config = self.model_copy()
                    setattr(test_config, key, value)
                    _ = test_config.model_validate(test_config.model_dump())
                    # Convert value to JsonValue for type safety
                    json_value = FlextCliUtilities.DataMapper.convert_to_json_value(
                        value
                    )
                    valid_overrides[key] = cast("FlextTypes.Json.JsonValue", json_value)
                except Exception as e:
                    errors.append(
                        FlextCliConstants.ErrorMessages.INVALID_VALUE_FOR_FIELD.format(
                            field=key,
                            error=e,
                        ),
                    )

            if errors:
                return FlextResult[FlextTypes.JsonDict].fail(
                    FlextCliConstants.ErrorMessages.VALIDATION_ERRORS.format(
                        errors="; ".join(errors),
                    ),
                )

            # Convert mutable dict to JsonDict (Mapping) for return type
            json_dict: FlextTypes.JsonDict = dict(valid_overrides)
            return FlextResult[FlextTypes.JsonDict].ok(json_dict)

        except Exception as e:
            return FlextResult[FlextTypes.JsonDict].fail(f"Validation failed: {e}")

    # Protocol-compliant methods for CliConfigProvider
    def load_config(self) -> FlextResult[FlextCliTypes.Data.CliConfigData]:
        """Load CLI configuration - implements CliConfigProvider protocol.

        Returns:
            FlextResult[FlextCliTypes.Data.CliConfigData]: Configuration data or error

        """
        try:
            # Convert model to dictionary format using model_dump()
            # FlextUtilities.DataMapper handles all type conversions automatically
            config_dict_raw = self.model_dump()
            # Use DataMapper for type compatibility
            config_data = FlextCliUtilities.DataMapper.convert_dict_to_json(
                config_dict_raw
            )
            return FlextResult[FlextCliTypes.Data.CliConfigData].ok(config_data)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliConfigData].fail(
                FlextCliConstants.ErrorMessages.CONFIG_LOAD_FAILED_MSG.format(error=e),
            )

    def save_config(
        self,
        config: FlextCliTypes.Data.CliConfigData,
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
            _ = self.model_validate(self.model_dump())
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.CONFIG_SAVE_FAILED_MSG.format(error=e),
            )

    _instance: ClassVar[FlextCliConfig | None] = None

    @classmethod
    def get_instance(cls) -> FlextCliConfig:
        """Get singleton instance of FlextCliConfig.

        Returns:
            Singleton instance of FlextCliConfig

        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _reset_instance(cls) -> None:
        """Reset singleton instance for testing purposes.

        This method is intended for use in tests only to allow
        clean state between test runs.
        """
        cls._instance = None


__all__ = [
    "FlextCliConfig",
]
