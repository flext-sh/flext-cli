"""FLEXT CLI Configuration Management - Unified Configuration with flext-core.

This module provides unified configuration management for FLEXT CLI operations,
using Pydantic models and flext-core base classes for type-safe configuration
with environment variable support and nested configuration structures.

Configuration Components:
    - CLIOutputConfig: Output formatting and display preferences
    - CLIAPIConfig: API client settings and connection parameters
    - CLIAuthConfig: Authentication and token management
    - CLIDirectoryConfig: File system directories and paths
    - CLIConfig: Main configuration container with component composition
    - CLISettings: Environment variable-driven settings

Architecture:
    - Pydantic models for type safety and validation
    - Nested configuration with component composition
    - Environment variable support with prefix (FLEXT_CLI_)
    - Backward compatibility with legacy flat parameter structure
    - Singleton pattern for global configuration access

Current Implementation Status:
    ✅ Complete configuration model with type safety
    ✅ Nested configuration structure with components
    ✅ Environment variable support and validation
    ✅ Backward compatibility with legacy interfaces
    ✅ Directory creation and setup utilities
    ✅ Authentication token management
    ⚠️ Full functionality (TODO: Sprint 2 - enhance features)

TODO (docs/TODO.md):
    Sprint 2: Add configuration validation and schema enforcement
    Sprint 3: Add profile-based configuration inheritance
    Sprint 3: Add configuration file loading (YAML, JSON, TOML)
    Sprint 5: Add encrypted configuration support
    Sprint 7: Add configuration hot-reload and monitoring

Configuration Structure:
    CLIConfig (main):
        - output: CLIOutputConfig (format, color, verbosity)
        - api: CLIAPIConfig (URL, timeout, SSL settings)
        - auth: CLIAuthConfig (tokens, auto-refresh)
        - directories: CLIDirectoryConfig (paths and directory management)

Usage Examples:
    Basic configuration:
    >>> config = CLIConfig()
    >>> config.debug = True
    >>> config.api.url = "https://api.example.com"

    Environment variables:
    >>> settings = CLISettings()  # Loads from FLEXT_CLI_* env vars

    Component access:
    >>> config.output.format = "json"
    >>> config.auth.auto_refresh = True
    >>> config.directories.ensure_directories()

Integration:
    - Used throughout FLEXT CLI for configuration management
    - Provides type-safe configuration with validation
    - Supports environment variable overrides
    - Integrates with flext-core settings patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CLIOutputConfig(BaseModel):
    """CLI output configuration."""

    format: Literal["table", "json", "yaml", "csv", "plain"] = Field(
        "table",
        description="Default output format",
    )
    no_color: bool = Field(default=False, description="Disable color output")
    quiet: bool = Field(default=False, description="Suppress non-error output")
    verbose: bool = Field(default=False, description="Enable verbose output")
    pager: str | None = Field(None, description="Pager command for output")


class CLIAPIConfig(BaseModel):
    """CLI API client configuration."""

    url: str = Field(default="http://localhost:8000", description="API base URL")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retries: int = Field(default=3, description="Number of retry attempts")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

    @property
    def base_url(self) -> str:
        """Get the base URL with trailing slash removed.

        Returns:
            Base URL without trailing slash.

        """
        return self.url.rstrip("/")


class CLIAuthConfig(BaseModel):
    """CLI authentication configuration."""

    token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "auth" / "token",
        description="Path to authentication token file",
    )
    refresh_token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "auth" / "refresh_token",
        description="Path to refresh token file",
    )
    auto_refresh: bool = Field(default=True, description="Auto-refresh expired tokens")


class CLIDirectoryConfig(BaseModel):
    """CLI directory configuration."""

    config_dir: Path = Field(
        default_factory=lambda: Path.home() / ".flext",
        description="Configuration directory",
    )
    cache_dir: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "cache",
        description="Cache directory",
    )
    log_dir: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "logs",
        description="Log directory",
    )
    data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "data",
        description="Data directory",
    )

    def ensure_directories(self) -> None:
        """Ensure all configured directories exist.

        Creates all configured directories with their parent directories
        if they don't already exist.
        """
        for dir_path in [self.config_dir, self.cache_dir, self.log_dir, self.data_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)


class CLIConfig(BaseModel):
    """Main CLI configuration using flext-core base classes."""

    # Core configuration
    profile: str = Field(default="default", description="Current configuration profile")
    debug: bool = Field(default=False, description="Enable debug mode")

    # Component configurations
    output: CLIOutputConfig = Field(
        default_factory=lambda: CLIOutputConfig(
            format="table",
            no_color=False,
            quiet=False,
            verbose=False,
            pager=None,
        ),
        description="Output configuration",
    )
    api: CLIAPIConfig = Field(
        default_factory=lambda: CLIAPIConfig(
            url="http://localhost:8000",
            timeout=30,
            retries=3,
            verify_ssl=True,
        ),
        description="API client configuration",
    )
    auth: CLIAuthConfig = Field(
        default_factory=lambda: CLIAuthConfig(
            token_file=Path.home() / ".flext" / "auth" / "token",
            refresh_token_file=Path.home() / ".flext" / "auth" / "refresh_token",
            auto_refresh=True,
        ),
        description="Authentication configuration",
    )
    directories: CLIDirectoryConfig = Field(
        default_factory=lambda: CLIDirectoryConfig(
            config_dir=Path.home() / ".flext",
            cache_dir=Path.home() / ".flext" / "cache",
            log_dir=Path.home() / ".flext" / "logs",
            data_dir=Path.home() / ".flext" / "data",
        ),
        description="Directory configuration",
    )

    def __init__(self, **data: object) -> None:
        """Initialize CLIConfig with backward compatibility for flat parameters."""
        self._migrate_legacy_parameters(data)
        super().__init__(**data)

    def _migrate_legacy_parameters(self, data: dict[str, object]) -> None:
        """Migrate legacy flat parameters to nested structure."""
        # API-related parameters
        api_migrations = [
            ("api_url", "url"),
            ("timeout", "timeout"),
            ("max_retries", "retries"),
        ]
        self._migrate_to_section(data, "api", api_migrations)

        # Directory-related parameters
        dir_migrations = [
            ("cache_dir", "cache_dir"),
            ("config_dir", "config_dir"),
        ]
        self._migrate_to_section(data, "directories", dir_migrations)

    def _migrate_to_section(
        self,
        data: dict[str, object],
        section: str,
        migrations: list[tuple[str, str]],
    ) -> None:
        """Migrate parameters to a specific section."""
        for old_key, new_key in migrations:
            if old_key in data:
                if section not in data:
                    data[section] = {}
                section_dict = cast("dict[str, object]", data[section])
                section_dict[new_key] = data.pop(old_key)

    def ensure_setup(self) -> None:
        """Ensure CLI environment is properly set up.

        Creates all necessary directories and ensures the authentication
        directory structure exists.
        """
        self.directories.ensure_directories()

        # Ensure auth directory exists
        self.auth.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.auth.refresh_token_file.parent.mkdir(parents=True, exist_ok=True)

    # Compatibility properties for backward compatibility with tests
    @property
    def api_url(self) -> str:
        """API URL for backward compatibility."""
        return self.api.url

    @property
    def timeout(self) -> int:
        """Timeout for backward compatibility."""
        return self.api.timeout

    @property
    def max_retries(self) -> int:
        """Max retries for backward compatibility."""
        return self.api.retries

    @property
    def cache_dir(self) -> Path:
        """Cache directory for backward compatibility."""
        return self.directories.cache_dir

    @property
    def config_dir(self) -> Path:
        """Config directory for backward compatibility."""
        return self.directories.config_dir

    @property
    def token_file(self) -> Path:
        """Token file for backward compatibility."""
        return Path.home() / ".flext" / ".token"

    @property
    def refresh_token_file(self) -> Path:
        """Refresh token file for backward compatibility."""
        return Path.home() / ".flext" / ".refresh_token"

    @property
    def auto_refresh(self) -> bool:
        """Auto refresh for backward compatibility."""
        return self.auth.auto_refresh

    @property
    def log_level(self) -> str:
        """Log level for backward compatibility."""
        return "INFO"  # Default log level

    @property
    def output_format(self) -> str:
        """Output format for backward compatibility."""
        return self.output.format


# Singleton instance
_cli_config: CLIConfig | None = None


def get_cli_config(*, reload: bool = False) -> CLIConfig:
    """Get CLI configuration singleton."""
    global _cli_config  # noqa: PLW0603

    if _cli_config is None or reload:
        _cli_config = _create_cli_config()

    return _cli_config


def _create_cli_config() -> CLIConfig:
    """Create and configure CLI config instance."""
    config = CLIConfig(
        profile="default",
        debug=False,
    )
    config.ensure_setup()
    return config


class CLISettings(BaseSettings):
    """FLEXT CLI settings with environment variable support.

    Uses flext-core BaseSettings foundation with standardized patterns.
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    # Project identification
    project_name: str = Field(default="flext-cli", description="Project name")
    project_version: str = Field(default="0.9.0", description="Project version")

    # CLI specific settings
    api_url: str = Field(default="http://localhost:8000", description="API base URL")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    output_format: str = Field(default="table", description="Default output format")
    debug: bool = Field(default=False, description="Debug mode")


def get_cli_settings() -> CLISettings:
    """Get CLI settings instance."""
    return CLISettings(
        project_name="flext-cli",
        project_version="0.9.0",
        api_url="http://localhost:8000",
        timeout=30,
        output_format="table",
        debug=False,
    )
