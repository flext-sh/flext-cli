"""FLEXT CLI Configuration - Modern Python 3.13 patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Uses flext-core BaseSettings with structured value objects.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic_settings import SettingsConfigDict

from flext_core.config import get_container
from flext_core.config import singleton
from flext_core.config.base import BaseSettings
from flext_core.domain.pydantic_base import DomainValueObject
from flext_core.domain.pydantic_base import Field


class APIConfig(DomainValueObject):
    """API configuration value object."""

    url: str = Field("http://localhost:8000", description="API base URL")
    token: str | None = Field(None, description="API authentication token")
    timeout: int = Field(30, ge=1, le=300, description="API request timeout in seconds")
    retries: int = Field(3, ge=0, le=10, description="API retry attempts")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")


class DirectoryConfig(DomainValueObject):
    """Directory configuration value object."""

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
    plugin_dir: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "plugins",
        description="Plugin directory",
    )


class OutputConfig(DomainValueObject):
    """Output configuration value object."""

    format: str = Field(
        "table",
        description="Default output format (table, json, yaml, csv, plain)",
    )
    no_color: bool = Field(False, description="Disable color output")
    quiet: bool = Field(False, description="Suppress non-error output")
    verbose: bool = Field(False, description="Enable verbose output")
    pager: str | None = Field(None, description="Pager command")


class AuthConfig(DomainValueObject):
    """Authentication configuration value object."""

    token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "token",
        description="Auth token file",
    )
    auto_refresh: bool = Field(True, description="Auto-refresh expired tokens")
    session_timeout: int = Field(
        3600,
        ge=300,
        le=86400,
        description="Session timeout in seconds",
    )


class PluginConfig(DomainValueObject):
    """Plugin configuration value object."""

    auto_update: bool = Field(False, description="Auto-update plugins")
    registry_url: str = Field(
        "https://registry.flext.sh",
        description="Plugin registry URL",
    )
    max_concurrent: int = Field(
        5,
        ge=1,
        le=20,
        description="Maximum concurrent plugin operations",
    )


@singleton()
class CLISettings(BaseSettings):
    """FLEXT CLI configuration settings with environment variable support.

    All settings can be overridden via environment variables with the
    prefix FLEXT_CLI_ (e.g., FLEXT_CLI_API__URL).

    Uses flext-core BaseSettings foundation with DI support.
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    # Project identification
    project_name: str = Field("flext-cli", description="Project name")
    project_version: str = Field("0.7.0", description="Project version")

    # Configuration value objects
    api: APIConfig = Field(default_factory=APIConfig, description="API configuration")
    directories: DirectoryConfig = Field(
        default_factory=DirectoryConfig,
        description="Directory configuration",
    )
    output: OutputConfig = Field(
        default_factory=OutputConfig,
        description="Output configuration",
    )
    auth: AuthConfig = Field(
        default_factory=AuthConfig,
        description="Authentication configuration",
    )
    plugins: PluginConfig = Field(
        default_factory=PluginConfig,
        description="Plugin configuration",
    )

    # Profile and environment
    profile: str = Field("default", description="Configuration profile")
    environment: str = Field("development", description="Environment name")
    debug: bool = Field(False, description="Debug mode")
    log_level: str = Field("INFO", description="Log level")

    # Legacy properties for backward compatibility
    @property
    def api_url(self) -> str:
        """Get API URL from configuration.

        Returns:
            API base URL.

        """
        return self.api.url

    @property
    def api_token(self) -> str | None:
        """Get API token from configuration.

        Returns:
            API authentication token or None.

        """
        return self.api.token

    @property
    def api_timeout(self) -> int:
        """Get API timeout from configuration.

        Returns:
            API request timeout in seconds.

        """
        return self.api.timeout

    @property
    def config_dir(self) -> Path:
        """Get configuration directory from configuration.

        Returns:
            Path to configuration directory.

        """
        return self.directories.config_dir

    @property
    def cache_dir(self) -> Path:
        """Get cache directory from configuration.

        Returns:
            Path to cache directory.

        """
        return self.directories.cache_dir

    @property
    def log_dir(self) -> Path:
        """Get log directory from configuration.

        Returns:
            Path to log directory.

        """
        return self.directories.log_dir

    @property
    def output_format(self) -> str:
        """Get output format from configuration.

        Returns:
            Default output format.

        """
        return self.output.format

    @property
    def no_color(self) -> bool:
        """Get no color setting from configuration.

        Returns:
            True if color output is disabled.

        """
        return self.output.no_color

    @property
    def quiet(self) -> bool:
        """Get quiet mode setting from configuration.

        Returns:
            True if quiet mode is enabled.

        """
        return self.output.quiet

    @property
    def verbose(self) -> bool:
        """Get verbose mode setting from configuration.

        Returns:
            True if verbose mode is enabled.

        """
        return self.output.verbose

    @property
    def token_file(self) -> Path:
        """Get token file path from configuration.

        Returns:
            Path to authentication token file.

        """
        return self.auth.token_file

    def configure_dependencies(self, container: Any = None) -> None:
        """Configure dependency injection container.

        Args:
            container: Dependency injection container.

        """
        if container is None:
            container = get_container()

        # Register this settings instance
        container.register(CLISettings, self)

        # Call parent configuration
        super().configure_dependencies(container)


# Convenience functions for getting settings
def get_cli_settings() -> CLISettings:
    """Get CLI settings instance.

    Returns:
        CLI settings singleton instance.

    """
    return CLISettings()


def create_development_cli_config() -> CLISettings:
    """Create CLI configuration for development environment.

    Returns:
        CLI settings configured for development.

    """
    return CLISettings(
        environment="development",
        debug=True,
        api=APIConfig(
            url="http://localhost:8000",
            timeout=60,
            verify_ssl=False,
        ),
        output=OutputConfig(
            verbose=True,
            no_color=False,
        ),
        auth=AuthConfig(
            auto_refresh=True,
            session_timeout=7200,  # 2 hours for development
        ),
        plugins=PluginConfig(
            auto_update=False,
        ),
    )


def create_production_cli_config() -> CLISettings:
    """Create CLI configuration for production environment.

    Returns:
        CLI settings configured for production.

    """
    return CLISettings(
        environment="production",
        debug=False,
        log_level="WARNING",
        api=APIConfig(
            url="https://api.flext.sh",
            timeout=30,
            retries=3,
            verify_ssl=True,
        ),
        output=OutputConfig(
            verbose=False,
            quiet=False,
        ),
        auth=AuthConfig(
            auto_refresh=True,
            session_timeout=3600,  # 1 hour for production
        ),
        plugins=PluginConfig(
            auto_update=True,
            max_concurrent=3,
        ),
    )
