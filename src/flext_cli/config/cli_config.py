"""CLI configuration management for FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Provides unified configuration using flext-core base classes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

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

    def ensure_setup(self) -> None:
        """Ensure CLI environment is properly set up.

        Creates all necessary directories and ensures the authentication
        directory structure exists.
        """
        self.directories.ensure_directories()

        # Ensure auth directory exists
        self.auth.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.auth.refresh_token_file.parent.mkdir(parents=True, exist_ok=True)


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
    project_version: str = Field(default="0.7.0", description="Project version")

    # CLI specific settings
    api_url: str = Field(default="http://localhost:8000", description="API base URL")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    output_format: str = Field(default="table", description="Default output format")
    debug: bool = Field(default=False, description="Debug mode")


def get_cli_settings() -> CLISettings:
    """Get CLI settings instance."""
    return CLISettings(
        project_name="flext-cli",
        project_version="0.7.0",
        api_url="http://localhost:8000",
        timeout=30,
        output_format="table",
        debug=False,
    )
