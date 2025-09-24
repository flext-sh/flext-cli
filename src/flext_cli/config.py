"""FLEXT CLI Configuration - Single unified class following FLEXT standards.

Provides unified configuration management for the FLEXT CLI ecosystem
using Pydantic Settings for environment variable support.
Single FlextCliConfig class with nested configuration subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from flext_cli.constants import FlextCliConstants
from flext_cli.mixins import FlextCliMixins
from flext_core import (
    FlextConfig,
    FlextConstants,
    FlextResult,
)


class FlextCliConfig(FlextConfig):
    """Single unified CLI configuration class following FLEXT standards.

    Contains all configuration subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Inherits from FlextConfig to avoid duplication
    - Uses centralized validation via FlextConfig.Validation
    - Implements CLI-specific extensions while reusing core functionality
    CRITICAL ARCHITECTURE: ALL configuration validation is centralized in FlextConfig.
    NO inline validation is allowed in service methods.
    """

    # =========================================================================
    # BASE CLASSES - Common functionality for CLI configurations
    # =========================================================================

    class _BaseConfig(BaseModel, FlextCliMixins.ValidationMixin):
        """Base configuration model with common config validation patterns."""

    # =========================================================================
    # CLI CONFIGURATION SUBCLASSES
    # =========================================================================

    class MainConfig(FlextConfig):
        """Main CLI configuration class extending FlextConfig.

        Provides unified configuration management for the FLEXT CLI ecosystem
        using Pydantic Settings for environment variable support.
        Inherits core configuration from FlextConfig and adds CLI-specific fields.
        """

        model_config = SettingsConfigDict(
            env_prefix="FLEXT_CLI_",
            case_sensitive=False,
            extra="allow",
        )

        # CLI-specific configuration fields (inherits debug, timeout_seconds from FlextConfig)
        profile: str = Field(default="default")
        output_format: str = Field(default="table")
        no_color: bool = Field(default=False)
        config_dir: Path = Field(default_factory=lambda: Path("~/.flext").expanduser())

        # Test compatibility fields (will be consolidated with FlextConfig inheritance)
        project_name: str = Field(default="flext-cli")

        @property
        def debug_mode(self) -> bool:
            """Alias for debug field from FlextConfig."""
            return bool(self.debug)

        def validate_output_format(self, format_type: str) -> FlextResult[str]:
            """Validate output format using centralized validation."""
            # Use centralized validation patterns
            if format_type not in FlextCliConstants.OUTPUT_FORMATS_LIST:
                return FlextResult[str].fail(
                    f"Invalid output format: {format_type}. "
                    f"Valid formats: {', '.join(FlextCliConstants.OUTPUT_FORMATS_LIST)}"
                )
            return FlextResult[str].ok(format_type)

        def set_output_format(self, format_type: str) -> FlextResult[None]:
            """Set the output format."""
            validation_result = self.validate_output_format(format_type)
            if not validation_result.is_success:
                return FlextResult[None].fail(
                    validation_result.error or "Output format validation failed"
                )

            self.output_format = validation_result.value
            return FlextResult[None].ok(None)

        def load_configuration(self) -> FlextResult[dict[str, object]]:
            """Load configuration data from current settings.

            Returns:
                FlextResult[dict[str, object]]: Configuration data or error

            """
            try:
                # Use FlextConfig's inherited fields where possible
                config_data: dict[str, object] = {
                    "profile": self.profile,
                    "output_format": self.output_format,
                    "debug_mode": self.debug,
                    "debug": self.debug,
                    "project_name": self.project_name,
                    "database_url": None,  # Will be populated from FlextConfig inheritance
                    "cache_enabled": True,  # Will be populated from FlextConfig inheritance
                    "api_timeout": self.timeout_seconds,
                    "max_connections": 10,  # Will be populated from FlextConfig inheritance
                    "timeout_seconds": self.timeout_seconds,
                    "no_color": self.no_color,
                    "config_dir": str(self.config_dir),
                    "config_file": str(self.config_dir / "config.yaml"),
                }
                return FlextResult[dict[str, object]].ok(config_data)
            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Configuration load failed: {e}"
                )

        def validate_configuration(self) -> FlextResult[None]:
            """Validate configuration settings.

            Returns:
                FlextResult[None]: Validation result

            """
            try:
                # Validate output format
                if self.output_format not in FlextCliConstants.OUTPUT_FORMATS_LIST:
                    return FlextResult[None].fail(
                        f"Invalid output format: {self.output_format}"
                    )

                # Validate profile
                if not self.profile or not self.profile.strip():
                    return FlextResult[None].fail("Profile cannot be empty")

                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Configuration validation failed: {e}")

    class CliOptions(BaseModel):
        """CLI options configuration model extending BaseModel."""

        output_format: str = Field(default="table")
        verbose: bool = False
        debug: bool = False
        no_color: bool = False
        max_width: int = 120
        config_file: Path | None = None

    class AuthConfig(_BaseConfig, FlextCliMixins.BusinessRulesMixin):
        """Authentication configuration model extending _BaseConfig."""

        api_url: str = Field(default="http://localhost:8000")
        token_file: Path = Field(
            default_factory=lambda: Path("~/.flext").expanduser() / "token"
        )
        refresh_token_file: Path = Field(
            default_factory=lambda: Path("~/.flext").expanduser() / "refresh_token"
        )
        auto_refresh: bool = Field(default=True)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate auth configuration business rules using centralized validation."""
            # Use simple URL validation for now - can be enhanced with FlextModels.Validation later
            if not self.api_url.startswith(("http://", "https://")):
                return FlextResult[None].fail(f"Invalid API URL format: {self.api_url}")

            return FlextResult[None].ok(None)

    class LoggingConfig(_BaseConfig, FlextCliMixins.BusinessRulesMixin):
        """Logging configuration model extending _BaseConfig."""

        log_level: str = Field(default="INFO")
        log_format: str = Field(
            default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_output: bool = Field(default=True)
        log_file: Path | None = Field(default=None)
        log_level_source: str = Field(default="default")

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate logging configuration business rules using centralized validation."""
            # Use FlextConfig's validation for log level
            if self.log_level not in FlextConstants.Logging.VALID_LEVELS:
                return FlextResult[None].fail(
                    f"Invalid log level: {self.log_level}. "
                    f"Valid levels: {', '.join(FlextConstants.Logging.VALID_LEVELS)}"
                )

            return FlextResult[None].ok(None)

    # =========================================================================
    # CENTRALIZED VALIDATION ARCHITECTURE - Delegates to FlextConfig.Validation
    # =========================================================================

    class Validation:
        """CLI-specific validation extending FlextConfig.Validation."""

        @staticmethod
        def validate_output_format(format_type: str) -> FlextResult[str]:
            """Validate CLI output format."""
            if format_type not in FlextCliConstants.OUTPUT_FORMATS_LIST:
                return FlextResult[str].fail(
                    f"Invalid output format: {format_type}. "
                    f"Valid formats: {', '.join(FlextCliConstants.OUTPUT_FORMATS_LIST)}"
                )
            return FlextResult[str].ok(format_type)

        @staticmethod
        def validate_cli_options(options: dict[str, object]) -> FlextResult[None]:
            """Validate CLI options configuration."""
            # Use parent validation for common patterns
            if "output_format" in options:
                format_result = FlextCliConfig.Validation.validate_output_format(
                    str(options["output_format"])
                )
                if not format_result.is_success:
                    return FlextResult[None].fail(
                        format_result.error or "Validation failed"
                    )

            return FlextResult[None].ok(None)

    def validate_configuration(self: object) -> FlextResult[None]:
        """CENTRALIZED configuration validation - delegates to FlextConfig and adds CLI-specific logic.

        This method consolidates ALL configuration validation logic that was
        previously scattered across multiple modules. Uses FlextConfig.Validation
        for common patterns and adds CLI-specific validation.

        Returns:
            FlextResult[None]: Success if all configuration is valid, failure otherwise

        """
        try:
            # Validate CLI-specific nested configurations
            auth_result = FlextCliConfig.AuthConfig().validate_business_rules()
            if not auth_result.is_success:
                return FlextResult[None].fail(
                    f"Auth config validation failed: {auth_result.error}"
                )

            logging_result = FlextCliConfig.LoggingConfig().validate_business_rules()
            if not logging_result.is_success:
                return FlextResult[None].fail(
                    f"Logging config validation failed: {logging_result.error}"
                )

            # Additional CLI-specific validation using centralized patterns
            # This replaces all scattered validation across the codebase

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Configuration validation failed: {e}")

    @classmethod
    def create_default(cls) -> FlextCliConfig.MainConfig:
        """Create default configuration.

        Returns:
            FlextCliConfig.MainConfig: Default configuration instance

        """
        return cls.MainConfig(profile="default", output_format="table", debug=False)


__all__ = [
    "FlextCliConfig",
]
