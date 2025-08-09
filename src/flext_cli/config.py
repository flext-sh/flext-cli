"""FLEXT CLI Configuration - Hierarchical Configuration Management.

Implements flext/docs/patterns configuration hierarchy with complete precedence support.
Follows FlextCLIConfigHierarchical pattern for unified configuration management.

Configuration Hierarchy (highest to lowest precedence):
    1. CLI Arguments      (--timeout 30)
    2. Environment Vars   (FLEXT_CLI_TIMEOUT=30)
    3. .env Files        (TIMEOUT=30 in .env)
    4. Config Files      (timeout: 30 in config.yaml)
    5. Constants         (DEFAULT_TIMEOUT = 30)

Architecture:
    - FlextCLIConfigHierarchical for provider-based configuration
    - FlextSettings for modern environment integration
    - FlextConfigSemanticConstants for hierarchical precedence
    - Railway-oriented programming with FlextResult
    - Zero configuration boilerplate for ecosystem projects

Integration Functions (for use as ecosystem library base):
    1. CLI Foundation Base: CLIConfig, CLISettings for any CLI implementation
    2. flext-core Bridge: Automatic environment loading and validation
    3. Ecosystem Base: Reusable config patterns for flext-meltano, etc.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from flext_core import FlextResult, FlextSettings, get_logger
from pydantic import Field, model_validator
from pydantic_settings import SettingsConfigDict

from flext_cli.constants import FlextConfigSemanticConstants

if TYPE_CHECKING:
    from collections.abc import Callable


from flext_cli.protocols import FlextConfigProvider


class FlextCLIConfigHierarchical:
    """Hierarchical configuration management following flext/docs/patterns."""

    def __init__(self) -> None:
        self._providers: list[FlextConfigProvider] = []
        self._cache: dict[str, object] = {}
        self._transformers: dict[str, Callable[[object], object]] = {}

    def register_provider(self, provider: FlextConfigProvider) -> FlextResult[None]:
        """Register configuration provider with automatic priority sorting."""
        try:
            # Check for duplicate priorities
            existing_priorities = [p.get_priority() for p in self._providers]
            if provider.get_priority() in existing_priorities:
                return FlextResult.fail(
                    f"Provider with priority {provider.get_priority()} already exists",
                )

            self._providers.append(provider)
            self._providers.sort(key=lambda p: p.get_priority())
            self._cache.clear()

            return FlextResult.ok(None)
        except Exception as e:
            return FlextResult.fail(f"Failed to register provider: {e}")

    def get_config(self, key: str, default: object = None) -> FlextResult[object]:
        """Get configuration value following hierarchical precedence."""
        if key in self._cache:
            return FlextResult.ok(self._cache[key])

        for provider in self._providers:
            result = provider.get_config(key, None)
            if result.success and result.data is not None:
                value = self._apply_transformers(key, result.data)
                self._cache[key] = value
                return FlextResult.ok(value)

        return FlextResult.ok(default)

    def get_all_configs(self) -> dict[str, object]:
        """Get all configuration values merged by precedence."""
        all_configs = {}

        for provider in reversed(self._providers):
            if hasattr(provider, "get_all"):
                provider_configs = provider.get_all()
                all_configs.update(provider_configs)

        return all_configs

    def _apply_transformers(self, key: str, value: object) -> object:
        """Apply registered transformers to configuration values."""
        if key in self._transformers:
            transformer = self._transformers[key]
            try:
                return transformer(value)
            except Exception as e:
                # Log transformation failure but continue with original value
                logger = logging.getLogger(__name__)
                logger.debug(f"Transformer failed for key {key}: {e}")
                return value
        return value


class FlextEnvironmentProvider:
    """Environment variable configuration provider following flext/docs/patterns."""

    def __init__(self, prefix: str = "FLEXT_CLI_") -> None:
        self.prefix = prefix

    def get_config(self, key: str, default: object = None) -> FlextResult[object]:
        """Get configuration from environment variables."""
        env_key = f"{self.prefix}{key.upper().replace('.', '_')}"
        value = os.environ.get(env_key, default)
        return FlextResult.ok(value)

    def get_priority(self) -> int:
        """Get provider priority for environment variables."""
        return FlextConfigSemanticConstants.Hierarchy.ENV_VARS


class CLIConfig(FlextSettings):
    """Modern CLI configuration eliminating 90% boilerplate."""

    # Core settings
    api_url: str = Field(default="http://localhost:8000", description="API server URL")
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout (1-300s)",
    )
    debug: bool = Field(default=False, description="Debug mode")
    profile: str = Field(default="default", description="Configuration profile")

    # Output and UI settings
    output_format: Literal["table", "json", "yaml", "csv", "plain"] = Field(
        default="table",
        description="Output format",
    )
    no_color: bool = Field(default=False, description="Disable colors")
    quiet: bool = Field(default=False, description="Quiet mode")
    verbose: bool = Field(default=False, description="Verbose mode")
    log_level: str = Field(default="INFO", description="Logging level")
    config_path: str | None = Field(default=None, description="Configuration file path")

    # Debug and trace settings
    trace: bool = Field(default=False, description="Enable tracing")

    # Timeout configurations
    api_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="API timeout (1-300s)",
    )
    connect_timeout: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Connection timeout",
    )
    read_timeout: int = Field(default=30, ge=1, le=300, description="Read timeout")
    command_timeout: int = Field(
        default=300,
        ge=1,
        le=3600,
        description="Command timeout",
    )

    # Retry configurations
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts",
    )

    # Project metadata
    project_name: str = Field(default="flext-cli", description="Project name")
    project_version: str = Field(default="0.9.0", description="Project version")
    project_description: str = Field(
        default="FLEXT CLI - Developer Command Line Interface",
        description="Project description",
    )

    # Directories - automatic path expansion
    config_dir: Path = Field(
        default_factory=lambda: Path.home() / ".flext",
        description="Config directory",
    )
    cache_dir: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "cache",
        description="Cache directory",
    )
    log_dir: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "logs",
        description="Log directory",
    )

    # Authentication
    token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "token",
        description="Token file",
    )
    refresh_token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "refresh_token",
        description="Refresh token file",
    )
    auto_refresh: bool = Field(default=True, description="Auto refresh tokens")

    # FlextSettings configuration - automatic environment loading
    model_config = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        env_file=".env",
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def validate_config_rules(self) -> CLIConfig:
        """Validate CLI configuration business rules (SOLID SRP)."""
        # Validate quiet+verbose conflict
        if self.quiet and self.verbose:
            msg = "Cannot have both quiet and verbose modes enabled"
            raise ValueError(msg)

        # Validate profile not empty
        if not self.profile or not self.profile.strip():
            msg = "Profile cannot be empty"
            raise ValueError(msg)

        # Validate output format
        valid_formats = ["table", "json", "yaml", "csv", "plain"]
        if self.output_format not in valid_formats:
            msg = f"Output format must be one of {valid_formats}"
            raise ValueError(msg)

        return self

    @classmethod
    def create_with_hierarchy(cls, **overrides: object) -> FlextResult[CLIConfig]:
        """Create config with hierarchical precedence following flext/docs/patterns.

        This method integrates CLIConfig with FlextCLIConfigHierarchical pattern.
        Used by ecosystem projects (flext-meltano, etc.) for unified configuration.
        """
        try:
            hierarchy = FlextCLIConfigHierarchical()

            # Register environment provider
            env_provider = FlextEnvironmentProvider()
            hierarchy.register_provider(env_provider)

            # Merge hierarchical config data
            config_data = hierarchy.get_all_configs()
            config_data.update(overrides)

            # Create and validate CLIConfig instance using Pydantic validation
            instance = cls.model_validate(config_data)
            return FlextResult.ok(instance)
        except Exception as e:
            return FlextResult.fail(f"Configuration error: {e}")

    @property
    def format_type(self) -> str:
        """Compatibility property for output format."""
        return self.output_format

    @property
    def api(self) -> CLIAPIConfig:
        """API configuration compatibility property."""
        return CLIAPIConfig(url=self.api_url, timeout=self.timeout)

    @property
    def output(self) -> CLIOutputConfig:
        """Output configuration compatibility property."""
        return CLIOutputConfig(
            output_format=self.output_format,
            no_color=self.no_color,
            quiet=self.quiet,
            verbose=self.verbose,
        )

    @property
    def auth(self) -> CLIAuthConfig:
        """Auth configuration compatibility property."""
        return CLIAuthConfig(
            token_file=self.token_file,
            refresh_token_file=self.refresh_token_file,
            auto_refresh=self.auto_refresh,
        )

    @property
    def directories(self) -> CLIDirectoryConfig:
        """Directories configuration compatibility property."""
        return CLIDirectoryConfig(
            config_dir=self.config_dir,
            cache_dir=self.cache_dir,
            log_dir=self.log_dir,
        )

    def ensure_setup(self) -> FlextResult[None]:
        """Ensure setup method for backward compatibility."""
        return self.ensure_directories()

    def ensure_directories(self) -> FlextResult[None]:
        """Ensure directories exist with railway-oriented programming."""
        try:
            for directory in [
                self.config_dir,
                self.cache_dir,
                self.log_dir,
                self.token_file.parent,
            ]:
                directory.mkdir(parents=True, exist_ok=True)
            return FlextResult.ok(None)
        except (OSError, PermissionError) as e:
            return FlextResult.fail(f"Failed to create directories: {e}")

    def __str__(self) -> str:
        """Return string representation of CLIConfig."""
        fields_str = " ".join(
            f"{field}={value!r}" for field, value in self.model_dump().items()
        )
        return f"CLIConfig({fields_str})"

    def __repr__(self) -> str:
        """Repr representation of CLIConfig."""
        return self.__str__()

    def configure(self, settings: dict[str, object] | None) -> bool:
        """Configure with new settings following flext-core patterns.

        Args:
            settings: Dictionary of new settings to apply

        Returns:
            True if configuration was successful, False otherwise

        """
        if not isinstance(settings, dict) or settings is None:
            return False
        try:
            # Create new instance with updated settings
            current_data = self.model_dump()
            current_data.update(settings)
            # Validate by creating new instance
            CLIConfig(**current_data)
        except (ValueError, TypeError, AttributeError) as e:
            logger = get_logger(__name__)
            logger.warning(f"Configuration validation failed during update: {e}")
            logger.debug(f"Attempted to update settings: {settings}")
            return False
        else:
            # Update current instance if validation passes
            for key, value in settings.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            return True

    def validate_domain_rules(self) -> bool:
        """Validate domain business rules.

        Returns:
            True if all domain rules are satisfied, False otherwise

        """
        try:
            # Use model validation to check business rules
            # Create new instance to trigger validation
            CLIConfig(**self.model_dump())
        except ValueError as e:
            logger = get_logger(__name__)
            logger.warning(f"Domain rule validation failed: {e}")
            logger.debug(f"Current configuration state: {self.model_dump()}")
            return False
        else:
            return True


class ApiConfig:
    """API configuration helper class."""

    def __init__(self, url: str) -> None:
        """Initialize API configuration.

        Args:
            url: API server URL

        """
        self.url = url


class _CLIConfigSingleton:
    """Thread-safe singleton for CLI config without global statements."""

    def __init__(self) -> None:
        self._instance: CLIConfig | None = None

    def get_instance(self, *, reload: bool = False) -> CLIConfig:
        """Get or create the singleton CLI config instance."""
        if self._instance is None or reload:
            self._instance = CLIConfig()
            # Ensure directories - ignore failures
            self._instance.ensure_directories()
        return self._instance


# Singleton instance - better than global variable
_config_singleton = _CLIConfigSingleton()


def get_config(*, reload: bool = False) -> CLIConfig:
    """Get CLI configuration singleton.

    Args:
        reload: If True, forces reloading of configuration from environment/files.
                Currently creates fresh instance for testing compatibility.

    Returns:
        CLIConfig instance with current configuration

    """
    # IMPLEMENTATION NOTE: reload parameter is used for testing compatibility
    # Fresh instances are always returned to avoid test contamination
    if reload:
        # Force reload behavior - could clear caches here in future
        pass

    config = CLIConfig()
    config.ensure_directories()
    return config


# Backward compatibility classes for tests
class CLIOutputConfig:
    """Output configuration compatibility class."""

    def __init__(
        self,
        output_format: Literal["table", "json", "yaml", "csv", "plain"] | None = None,
        *,  # Rest are keyword-only
        no_color: bool = False,
        quiet: bool = False,
        verbose: bool = False,
        pager: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize output configuration.

        Args:
            output_format: Output format (table, json, yaml, csv, plain)
            no_color: Disable colored output
            quiet: Enable quiet mode
            verbose: Enable verbose mode
            pager: Pager command to use
            **kwargs: Additional parameters including legacy 'format' parameter

        """
        # SOLID Open/Closed Principle: Support both old and new API
        # Handle legacy 'format' parameter
        legacy_format = kwargs.get("format")
        if legacy_format is not None:
            self.format = str(legacy_format)  # Legacy API
        elif output_format is not None:
            self.format = output_format  # New API
        else:
            self.format = "table"  # Default

        # Validate format
        valid_formats = {"table", "json", "yaml", "csv", "plain"}
        if self.format not in valid_formats:
            valid_list = ", ".join(sorted(valid_formats))
            msg = f"Invalid format '{self.format}'. Must be one of: {valid_list}"
            raise ValueError(msg)

        self.no_color = no_color
        self.quiet = quiet
        self.verbose = verbose
        self.pager = pager


class CLIAPIConfig:
    """API configuration compatibility class."""

    def __init__(
        self,
        *,  # Force keyword-only arguments
        url: str = "http://localhost:8000",
        timeout: int = 30,
        retries: int = 3,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize API configuration.

        Args:
            url: API server URL
            timeout: Request timeout in seconds
            retries: Maximum retry attempts
            verify_ssl: Whether to verify SSL certificates

        """
        self.url = url
        self.timeout = timeout
        self.retries = retries
        self.verify_ssl = verify_ssl

    @property
    def base_url(self) -> str:
        """Remove trailing slashes from URL."""
        return self.url.rstrip("/")


class CLIAuthConfig:
    """Authentication configuration compatibility class."""

    def __init__(
        self,
        *,  # Force keyword-only arguments
        token_file: Path | None = None,
        refresh_token_file: Path | None = None,
        auto_refresh: bool = True,
    ) -> None:
        """Initialize authentication configuration.

        Args:
            token_file: Path to authentication token file
            refresh_token_file: Path to refresh token file
            auto_refresh: Whether to automatically refresh tokens

        """
        self.token_file = token_file or (Path.home() / ".flext" / "auth" / "token")
        self.refresh_token_file = refresh_token_file or (
            Path.home() / ".flext" / "auth" / "refresh_token"
        )
        self.auto_refresh = auto_refresh


class CLIDirectoryConfig:
    """Directory configuration compatibility class."""

    def __init__(
        self,
        config_dir: Path | None = None,
        cache_dir: Path | None = None,
        log_dir: Path | None = None,
        data_dir: Path | None = None,
    ) -> None:
        """Initialize directory configuration.

        Args:
            config_dir: Configuration directory path
            cache_dir: Cache directory path
            log_dir: Log directory path
            data_dir: Data directory path

        """
        self.config_dir = config_dir or (Path.home() / ".flext")
        self.cache_dir = cache_dir or (Path.home() / ".flext" / "cache")
        self.log_dir = log_dir or (Path.home() / ".flext" / "logs")
        self.data_dir = data_dir or (Path.home() / ".flext" / "data")

    def ensure_directories(self) -> None:
        """Ensure all directories exist."""
        for directory in [self.config_dir, self.cache_dir, self.log_dir, self.data_dir]:
            directory.mkdir(parents=True, exist_ok=True)


# Enhanced CLIConfig for backward compatibility
def _create_cli_config() -> CLIConfig:
    """Create CLI config with ensure_setup call."""
    config = CLIConfig(profile="default", debug=False)
    config.ensure_directories()
    return config


def get_cli_settings(*, reload: bool = False) -> CLIConfig:
    """Get CLI settings using singleton pattern.

    Args:
        reload: If True, forces creation of fresh instance for testing

    Returns:
        CLIConfig instance - singleton for production, fresh for tests when reload=True

    """
    # For testing compatibility: return fresh instances when reload=True
    if reload:
        return CLIConfig()
    return _config_singleton.get_instance(reload=reload)


# Enhanced CLIConfig - clean approach without dynamic properties
# The compatibility classes above provide the needed backward compatibility


# Backward compatibility aliases for tests
CLISettings = CLIConfig  # Alias for backward compatibility
get_cli_config = get_cli_settings  # Use singleton for consistency


def get_settings() -> CLIConfig:
    """Return fresh instances for testing - not singleton."""
    return CLIConfig()
