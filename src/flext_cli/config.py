"""FLEXT CLI Config - Configuration management following flext-core patterns.

Provides CLI-specific configuration management extending flext-core FlextConfig
with CLI domain-specific settings, directory management, and validation patterns.
Follows consolidated class pattern with nested configuration domains.

Module Role in Architecture:
    FlextCliConfig serves as the CLI-specific configuration extending flext-core
    FlextConfig with command execution, authentication, output formatting, and
    directory management configuration for CLI applications.

Classes and Methods:
    FlextCliConfig:                        # Consolidated CLI configuration
        # Nested Classes:
        CliDefaults                       # CLI-specific default values
        CliDirectories                    # Directory management configuration
        CliSettings                       # Environment-aware settings

        # Factory Methods:
        create_with_directories(config_data) -> FlextCliConfig
        load_from_profile(profile_name) -> FlextCliConfig
        create_development_config() -> FlextCliConfig
        create_production_config() -> FlextCliConfig

        # Validation Methods:
        validate_cli_rules() -> FlextResult[None]
        validate_directories() -> FlextResult[None]
        ensure_setup() -> FlextResult[None]

Usage Examples:
    Basic configuration creation:
        config = FlextCliConfig(
            profile="development",
            debug=True,
            output_format="table"
        )

    Environment-aware configuration:
        settings = FlextCliConfig.CliSettings()
        # Automatically loads from FLEXT_CLI_* environment variables

    Directory setup:
        config = FlextCliConfig()
        setup_result = config.ensure_setup()
        if setup_result.is_success:
            print("Directories created successfully")

Integration:
    FlextCliConfig integrates with flext-core FlextConfig patterns,
    CLI-specific constants from FlextCliConstants, and validation
    through FlextResult for type safety and error handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar, override
from urllib.parse import urlparse

from flext_core import FlextResult
from flext_core.config import FlextConfig
from pydantic import ConfigDict, Field, field_serializer

from flext_cli.constants import FlextCliConstants


class FlextCliConfig(FlextConfig):
    """Consolidated CLI configuration extending FlextConfig patterns.

    Following exact semantic pattern from flext-core:
        - Module: config.py → Class: FlextConfig → FlextCliConfig
        - CLI-specific configuration domains extending flext-core base config
        - Nested classes for defaults, directories, and environment settings
        - Type-safe validation methods following railway-oriented programming

    CLI-specific configuration domains:
        - CliDefaults: CLI-specific default values and constants
        - CliDirectories: Directory structure and path management
        - CliSettings: Environment-aware configuration loading
    """

    # Reference to flext-core config for inheritance
    Core: ClassVar[type[FlextConfig]] = FlextConfig

    # Advanced Pydantic v2 configuration
    model_config = ConfigDict(
        # Enable advanced features for flext-core integration
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="forbid",
        # JSON schema configuration
        json_schema_extra={
            "examples": [
                {"profile": "development", "debug": True, "output_format": "table"},
                {"profile": "production", "debug": False, "output_format": "json"},
            ]
        },
    )

    # =========================================================================
    # CLI-SPECIFIC CONFIGURATION FIELDS
    # =========================================================================

    # Core CLI settings
    profile: str = Field(
        default="default",
        description="Configuration profile name",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    trace: bool = Field(
        default=False,
        description="Enable trace mode",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    command_timeout: int = Field(
        default=FlextCliConstants.TIMEOUTS.default_command_timeout,
        description="Command execution timeout in seconds",
    )

    # Project identity
    project_name: str = Field(
        default="flext-cli",
        description="Project name",
    )
    project_description: str = Field(
        default="FLEXT CLI - Developer Command Line Interface",
        description="Project description",
    )
    project_version: str = Field(
        default="0.9.0",
        description="Project version",
    )

    # API configuration
    api_url: str = Field(
        default=FlextCliConstants.HTTP.default_api_url,
        description="API base URL",
    )
    api_timeout: int = Field(
        default=FlextCliConstants.TIMEOUTS.default_api_timeout,
        le=FlextCliConstants.TIMEOUTS.max_command_timeout,
        description="API request timeout in seconds",
    )
    connect_timeout: int = Field(
        default=FlextCliConstants.TIMEOUTS.default_api_timeout,
        description="Connection timeout in seconds",
    )
    read_timeout: int = Field(
        default=FlextCliConstants.TIMEOUTS.default_read_timeout,
        description="Read timeout in seconds",
    )
    retries: int = Field(
        default=FlextCliConstants.OUTPUT.default_retries,
        description="Maximum retry attempts",
    )
    verify_ssl: bool = Field(
        default=True,
        description="Verify SSL certificates",
    )

    # Output configuration
    output_format: str = Field(
        default="table",
        description="Default output format",
    )
    no_color: bool = Field(
        default=False,
        description="Disable colored output",
    )
    quiet: bool = Field(
        default=False,
        description="Minimal output mode",
    )
    verbose: bool = Field(
        default=False,
        description="Verbose output mode",
    )
    pager: str | None = Field(
        default=None,
        description="Optional pager command",
    )

    # Directory configuration
    config_dir: Path = Field(
        default_factory=lambda: Path.home() / FlextCliConstants.FLEXT_DIR_NAME,
        description="Configuration directory",
    )
    cache_dir: Path = Field(
        default_factory=lambda: Path.home()
        / FlextCliConstants.FLEXT_DIR_NAME
        / FlextCliConstants.CACHE_DIR_NAME,
        description="Cache directory",
    )
    log_dir: Path = Field(
        default_factory=lambda: Path.home()
        / FlextCliConstants.FLEXT_DIR_NAME
        / FlextCliConstants.LOGS_DIR_NAME,
        description="Log directory",
    )
    data_dir: Path = Field(
        default_factory=lambda: Path.home()
        / FlextCliConstants.FLEXT_DIR_NAME
        / FlextCliConstants.DATA_DIR_NAME,
        description="Data directory",
    )

    # Authentication configuration
    token_file: Path = Field(
        default_factory=lambda: (
            Path.home()
            / FlextCliConstants.FLEXT_DIR_NAME
            / FlextCliConstants.AUTH_DIR_NAME
            / FlextCliConstants.TOKEN_FILE_NAME
        ),
        description="Authentication token file",
    )
    refresh_token_file: Path = Field(
        default_factory=lambda: (
            Path.home()
            / FlextCliConstants.FLEXT_DIR_NAME
            / FlextCliConstants.AUTH_DIR_NAME
            / FlextCliConstants.REFRESH_TOKEN_FILE_NAME
        ),
        description="Refresh token file",
    )
    auto_refresh: bool = Field(
        default=True,
        description="Enable automatic token refresh",
    )

    # =========================================================================
    # ADVANCED PYDANTIC V2 SERIALIZERS AND VALIDATORS
    # =========================================================================

    @field_serializer("api_url")
    def serialize_api_url(self, value: str) -> str:
        """Serialize API URL with masking for security in logs."""
        if not value:
            return value
        # Keep protocol and domain, mask path for security

        try:
            parsed = urlparse(value)
            # URL path masking length for security
            min_path_length_for_masking = FlextCliConstants.MIN_PATH_LENGTH_FOR_MASKING
            if parsed.path and len(parsed.path) > min_path_length_for_masking:
                masked_path = parsed.path[:min_path_length_for_masking] + "***"
                return f"{parsed.scheme}://{parsed.netloc}{masked_path}"
            return value
        except (ValueError, AttributeError):
            # URL parsing failed, return original value
            # Log the error if debug is enabled (would need logging context here)
            return value

    @field_serializer("token_file", "refresh_token_file")
    def serialize_token_paths(self, value: Path) -> str:
        """Serialize token file paths with home directory masking."""
        try:
            # Replace home directory with ~ for privacy
            return str(value).replace(str(Path.home()), "~")
        except (OSError, AttributeError):
            # Path handling failed, return string representation of value
            return str(value)

    # =========================================================================
    # NESTED CONFIGURATION CLASSES
    # =========================================================================

    class CliDefaults:
        """CLI-specific default values extending FlextConfig.SystemDefaults.

        Provides CLI-specific default values organized by functional domain
        using FlextCliConstants as the single source of truth.
        """

        class Command:
            """Command execution defaults."""

            timeout_seconds: int = FlextCliConstants.TIMEOUTS.default_command_timeout
            max_timeout_seconds: int = FlextCliConstants.TIMEOUTS.max_command_timeout
            min_timeout_seconds: int = FlextCliConstants.OUTPUT.min_length
            max_retries: int = FlextCliConstants.OUTPUT.default_retries
            retry_delay_seconds: int = FlextCliConstants.OUTPUT.min_length
            max_history_size: int = FlextCliConstants.LIMITS.max_history_size
            max_output_size: int = FlextCliConstants.MAX_OUTPUT_SIZE

        class Output:
            """Output formatting defaults."""

            default_format: str = "table"
            default_width: int = FlextCliConstants.OUTPUT.default_output_width
            max_table_rows: int = FlextCliConstants.LIMITS.max_table_rows
            table_padding: int = FlextCliConstants.OUTPUT.default_table_padding
            max_cell_width: int = FlextCliConstants.LIMITS.max_profile_name_length
            progress_bar_width: int = FlextCliConstants.OUTPUT.default_progress_bar_width

        class Auth:
            """Authentication defaults."""

            token_expiry_hours: int = FlextCliConstants.TOKEN_EXPIRY_HOURS
            refresh_expiry_days: int = FlextCliConstants.REFRESH_EXPIRY_DAYS
            session_timeout_minutes: int = FlextCliConstants.SESSION_TIMEOUT_MINUTES
            min_token_length: int = FlextCliConstants.OUTPUT.default_token_min_length
            max_login_attempts: int = FlextCliConstants.OUTPUT.default_retries

        class Config:
            """Configuration management defaults."""

            max_profile_name_length: int = FlextCliConstants.LIMITS.max_profile_name_length
            max_config_key_length: int = FlextCliConstants.MAX_CONFIG_KEY_LENGTH
            max_config_value_length: int = FlextCliConstants.LIMITS.max_config_value_length

        class Validation:
            """Input validation defaults."""

            min_command_length: int = FlextCliConstants.OUTPUT.min_length
            max_command_length: int = FlextCliConstants.LIMITS.max_config_value_length
            min_profile_length: int = FlextCliConstants.OUTPUT.min_length
            max_profile_length: int = FlextCliConstants.LIMITS.max_profile_name_length
            valid_output_formats: tuple[str, ...] = (
                FlextCliConstants.VALID_OUTPUT_FORMATS
            )
            valid_log_levels: tuple[str, ...] = FlextCliConstants.VALID_LOG_LEVELS

    class CliDirectories:
        """CLI directory structure management.

        Provides methods for directory creation, validation, and path management
        following CLI configuration patterns.
        """

        def __init__(self, config: FlextCliConfig) -> None:
            """Initialize directory manager with configuration."""
            self.config = config

        def create_directories(self) -> FlextResult[None]:
            """Create all necessary directories for CLI operation.

            Returns:
                FlextResult indicating success or failure of directory creation

            """
            try:
                directories_to_create = [
                    self.config.config_dir,
                    self.config.cache_dir,
                    self.config.log_dir,
                    self.config.data_dir,
                    self.config.token_file.parent,
                    self.config.refresh_token_file.parent,
                ]

                for directory in directories_to_create:
                    directory.mkdir(parents=True, exist_ok=True)

                return FlextResult[None].ok(None)

            except (OSError, PermissionError, RuntimeError, ValueError, TypeError) as e:
                return FlextResult[None].fail(f"Failed to create directories: {e}")

        def validate_directories(self) -> FlextResult[None]:
            """Validate that all directories exist and are accessible.

            Returns:
                FlextResult indicating validation success or failure

            """
            try:
                directories_to_check = [
                    ("config_dir", self.config.config_dir),
                    ("cache_dir", self.config.cache_dir),
                    ("log_dir", self.config.log_dir),
                    ("data_dir", self.config.data_dir),
                    ("token_dir", self.config.token_file.parent),
                    ("refresh_token_dir", self.config.refresh_token_file.parent),
                ]

                for name, directory in directories_to_check:
                    if not directory.exists():
                        return FlextResult[None].fail(
                            f"Directory does not exist: {name} ({directory})"
                        )

                    if not directory.is_dir():
                        return FlextResult[None].fail(
                            f"Path is not a directory: {name} ({directory})"
                        )

                    # Test write access
                    test_file = directory / FlextCliConstants.TEST_WRITE_FILE_NAME
                    try:
                        test_file.touch()
                        test_file.unlink()
                    except Exception as e:
                        return FlextResult[None].fail(
                            f"Directory not writable: {name} ({directory}): {e}"
                        )

                return FlextResult[None].ok(None)

            except (OSError, PermissionError, RuntimeError, ValueError) as e:
                return FlextResult[None].fail(f"Directory validation failed: {e}")

    class CliSettings(FlextConfig.Settings):
        """Environment-aware CLI settings extending FlextConfig.Settings.

        Automatically loads configuration from environment variables
        with FLEXT_CLI_ prefix following pydantic-settings patterns.
        """

        # FlextConfig.Settings already provides proper configuration

        # Core CLI settings with environment variable mapping
        profile: str = Field(
            default="default",
            description="Configuration profile name",
        )
        debug: bool = Field(
            default=False,
            description="Enable debug mode",
        )
        output_format: str = Field(
            default="table",
            description="Default output format",
        )
        api_url: str = Field(
            default=FlextCliConstants.HTTP.default_api_url,
            description="API base URL",
        )
        log_level: str = Field(
            default=FlextCliConstants.LOG_LEVEL_INFO,
            description="Logging level",
        )

    # =========================================================================
    # VALIDATION METHODS - CLI-specific business rules
    # =========================================================================

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI-specific business rules extending base validation.

        Returns:
            FlextResult indicating validation success or failure

        """
        try:
            # Call parent validation first and collect all validation errors
            base_validation = super().validate_business_rules()
            if base_validation.is_failure:
                return base_validation

            # Execute all CLI-specific validations
            validations = [
                self._validate_timeouts(),
                self._validate_retries(),
                self._validate_output_format(),
                self._validate_profile_name(),
                self._validate_log_level(),
            ]

            # Return first failure or success if all pass
            for validation in validations:
                if validation.is_failure:
                    return validation

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Configuration validation failed: {e}")

    def _validate_timeouts(self) -> FlextResult[None]:
        """Validate timeout configuration values."""
        if self.api_timeout <= 0 or self.command_timeout <= 0:
            return FlextResult[None].fail("Timeout values must be positive")

        if self.command_timeout > FlextCliConstants.TIMEOUTS.max_command_timeout:
            return FlextResult[None].fail(
                f"Command timeout exceeds maximum: {FlextCliConstants.TIMEOUTS.max_command_timeout}s"
            )
        return FlextResult[None].ok(None)

    def _validate_retries(self) -> FlextResult[None]:
        """Validate retry configuration."""
        if self.retries < 0:
            return FlextResult[None].fail("Retries cannot be negative")
        return FlextResult[None].ok(None)

    def _validate_output_format(self) -> FlextResult[None]:
        """Validate output format against CLI constants."""
        if self.output_format not in {"table", "json", "yaml", "csv"}:
            return FlextResult[None].fail(
                f"Invalid output format '{self.output_format}'. "
                f"Valid options: {['table', 'json', 'yaml', 'csv']}"
            )
        return FlextResult[None].ok(None)

    def _validate_profile_name(self) -> FlextResult[None]:
        """Validate profile name length and format."""
        if len(self.profile) < FlextCliConstants.OUTPUT.min_length:
            return FlextResult[None].fail(
                f"Profile name too short. Minimum length: {FlextCliConstants.OUTPUT.min_length}"
            )

        if len(self.profile) > FlextCliConstants.LIMITS.max_profile_name_length:
            return FlextResult[None].fail(
                f"Profile name too long. Maximum length: {FlextCliConstants.LIMITS.max_profile_name_length}"
            )

        # Basic pattern validation
        if not self.profile.replace("_", "").replace("-", "").isalnum():
            return FlextResult[None].fail(
                "Profile name must contain only alphanumeric characters, hyphens, and underscores"
            )

        return FlextResult[None].ok(None)

    def _validate_log_level(self) -> FlextResult[None]:
        """Validate log level against CLI constants."""
        if self.log_level not in FlextCliConstants.VALID_LOG_LEVELS:
            return FlextResult[None].fail(
                f"Invalid log level '{self.log_level}'. "
                f"Valid options: {list(FlextCliConstants.VALID_LOG_LEVELS)}"
            )
        return FlextResult[None].ok(None)

    def validate_directories(self) -> FlextResult[None]:
        """Validate directory configuration and accessibility.

        Returns:
            FlextResult indicating directory validation success or failure

        """
        directory_manager = self.CliDirectories(self)
        return directory_manager.validate_directories()

    def ensure_setup(self) -> FlextResult[None]:
        """Ensure all CLI directories and files are properly set up.

        Returns:
            FlextResult indicating setup success or failure

        """
        directory_manager = self.CliDirectories(self)
        return directory_manager.create_directories()

    # =========================================================================
    # FACTORY METHODS - Type-safe configuration creation
    # =========================================================================

    @classmethod
    def create_with_directories(
        cls,
        config_data: dict[str, object] | None = None,
    ) -> FlextResult[FlextCliConfig]:
        """Create CLI configuration with automatic directory setup.

        Args:
            config_data: Optional configuration data

        Returns:
            FlextResult containing CLI configuration or error

        """
        try:
            config_dict = config_data or {}
            config = cls.model_validate(config_dict)

            # Validate configuration
            validation_result = config.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[FlextCliConfig].fail(
                    validation_result.error or "Configuration validation failed"
                )

            # Setup directories
            setup_result = config.ensure_setup()
            if setup_result.is_failure:
                return FlextResult[FlextCliConfig].fail(
                    setup_result.error or "Directory setup failed"
                )

            return FlextResult[FlextCliConfig].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to create CLI configuration: {e}"
            )

    @classmethod
    def load_from_profile(
        cls,
        profile_name: str,
    ) -> FlextResult[FlextCliConfig]:
        """Load configuration from a specific profile.

        Args:
            profile_name: Name of the configuration profile

        Returns:
            FlextResult containing CLI configuration or error

        """
        try:
            # Validate profile name
            if not profile_name or len(profile_name.strip()) == 0:
                return FlextResult[FlextCliConfig].fail("Profile name cannot be empty")

            # Create configuration with profile
            config_data: dict[str, object] = {"profile": profile_name.strip()}
            return cls.create_with_directories(config_data)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to load profile '{profile_name}': {e}"
            )

    @classmethod
    def create_development_config(cls) -> FlextResult[FlextCliConfig]:
        """Create development-optimized CLI configuration.

        Returns:
            FlextResult containing development CLI configuration or error

        """
        try:
            config_data = {
                "profile": FlextCliConstants.DEVELOPMENT_PROFILE,
                "debug": True,
                "trace": True,
                "log_level": FlextCliConstants.LOG_LEVEL_DEBUG,
                "output_format": FlextCliConstants.OUTPUT.default_output_format,
                "verbose": True,
                "command_timeout": FlextCliConstants.TIMEOUTS.default_dev_timeout,  # Shorter timeout for development
                "api_timeout": FlextCliConstants.TIMEOUTS.default_api_timeout,
            }

            return cls.create_with_directories(config_data)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to create development configuration: {e}"
            )

    @classmethod
    def create_production_config(cls) -> FlextResult[FlextCliConfig]:
        """Create production-optimized CLI configuration.

        Returns:
            FlextResult containing production CLI configuration or error

        """
        try:
            config_data = {
                "profile": FlextCliConstants.PRODUCTION_PROFILE,
                "debug": False,
                "trace": False,
                "log_level": FlextCliConstants.LOG_LEVEL_INFO,
                "output_format": "json",
                "quiet": True,
                "command_timeout": FlextCliConstants.TIMEOUTS.default_command_timeout,
                "api_timeout": FlextCliConstants.PRODUCTION_API_TIMEOUT,  # Longer timeout for production
                "verify_ssl": True,
            }

            return cls.create_with_directories(config_data)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[FlextCliConfig].fail(
                f"Failed to create production configuration: {e}"
            )

    # =========================================================================
    # UTILITY METHODS AND PROPERTIES
    # =========================================================================

    @property
    def base_url(self) -> str:
        """Return API URL without trailing slashes for compatibility."""
        return self.api_url.rstrip("/")

    @property
    def is_development_mode(self) -> bool:
        """Check if configuration is for development environment."""
        return self.profile == "development" or self.debug

    @property
    def is_development_env(self) -> bool:
        """Check if configuration is for development environment."""
        return self.profile == "development" or self.debug

    @property
    def is_production_mode(self) -> bool:
        """Check if configuration is for production environment."""
        return self.profile == "production" and not self.debug

    @property
    def is_production_env(self) -> bool:
        """Check if configuration is for production environment."""
        return self.profile == "production" and not self.debug

    # =========================================================================
    # CONFIGURATION PROVIDERS - CLI-specific configuration providers
    # =========================================================================

    class ArgsProvider:
        """CLI arguments configuration provider (highest precedence)."""

        def __init__(self, args: dict[str, object]) -> None:
            """Initialize provider with CLI args dict."""
            self.args = args

        def get_config(self, key: str, default: object = None) -> FlextResult[object]:
            """Get configuration from CLI arguments."""
            value = self.args.get(key, default)
            return FlextResult[object].ok(value)

        def get_priority(self) -> int:
            """Get provider priority."""
            return FlextCliConstants.HIGH_PRIORITY_VALUE  # Highest priority

        def get_all(self) -> dict[str, object]:
            """Get all CLI arguments."""
            return self.args.copy()

    class ConstantsProvider:
        """Constants configuration provider (lowest precedence)."""

        def __init__(self, constants: dict[str, object]) -> None:
            """Initialize provider with constants dict."""
            self.constants = constants

        def get_config(self, key: str, default: object = None) -> FlextResult[object]:
            """Get configuration from constants."""
            value = self.constants.get(key, default)
            return FlextResult[object].ok(value)

        def get_priority(self) -> int:
            """Get provider priority."""
            return 0  # Lowest priority

        def get_all(self) -> dict[str, object]:
            """Get all constants."""
            return self.constants.copy()

    @override
    def __repr__(self) -> str:
        """Return string representation of FlextCliConfig."""
        return (
            f"FlextCliConfig("
            f"profile='{self.profile}', "
            f"debug={self.debug}, "
            f"output_format='{self.output_format}', "
            f"api_url='{self.api_url}'"
            f")"
        )

    @override
    def __str__(self) -> str:
        """Return string representation of FlextCliConfig."""
        return self.__repr__()

    @property
    def config_path(self) -> str | None:
        """Legacy alias for config_dir.

        Returns None by default unless explicitly set via config_path override.
        This maintains backwards compatibility with tests.
        """
        # Check if this instance was created with explicit config_path
        explicit = getattr(self, "_explicit_config_path", None)
        if explicit is not None:
            return str(explicit)
        # Return None by default for backwards compatibility
        return None

    @classmethod
    def setup_cli(
        cls, config: FlextCliConfig | None = None
    ) -> FlextResult[FlextCliConfig]:
        """Set up CLI with configuration.

        Args:
            config: Optional configuration instance

        Returns:
            FlextResult[FlextCliConfig]: Setup result with config

        """
        try:
            if config is None:
                config = cls()

            # Validate configuration
            validation_result = config.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[FlextCliConfig].fail(
                    f"Configuration validation failed: {validation_result.error}"
                )

            return FlextResult[FlextCliConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextCliConfig].fail(f"CLI setup failed: {e}")

    @classmethod
    def get_current(cls) -> FlextCliConfig:
        """Get default CLI configuration instance.

        Returns:
            FlextCliConfig: Default configuration instance

        """
        return cls()


# =============================================================================
# EXPORTS - Single unified class only
# =============================================================================

__all__ = [
    "FlextCliConfig",
]
