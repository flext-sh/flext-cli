"""FLEXT CLI configuration models using flext-core base classes."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from flext_core.config import BaseSettings
from flext_core.config import singleton
from flext_core.config.base import BaseConfig
from flext_core.domain.pydantic_base import DomainValueObject


class CLIOutputConfig(DomainValueObject):
    """CLI output configuration."""

    format: Literal["table", "json", "yaml", "csv", "plain"] = Field(
        "table",
        description="Default output format",
    )
    no_color: bool = Field(False, description="Disable color output")
    quiet: bool = Field(False, description="Suppress non-error output")
    verbose: bool = Field(False, description="Enable verbose output")
    pager: str | None = Field(None, description="Pager command for output")


class CLIAPIConfig(DomainValueObject):
    """CLI API client configuration."""

    url: str = Field("http://localhost:8000", description="API base URL")
    timeout: int = Field(30, description="Request timeout in seconds")
    retries: int = Field(3, description="Number of retry attempts")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")

    @property
    def base_url(self) -> str:
        """Get the base URL with trailing slash removed.

        Returns:
            Base URL without trailing slash.

        """
        return self.url.rstrip("/")


class CLIAuthConfig(DomainValueObject):
    """CLI authentication configuration."""

    token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "auth" / "token",
        description="Path to authentication token file",
    )
    refresh_token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "auth" / "refresh_token",
        description="Path to refresh token file",
    )
    auto_refresh: bool = Field(True, description="Auto-refresh expired tokens")


class CLIDirectoryConfig(DomainValueObject):
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


class CLIConfig(BaseConfig):
    """Main CLI configuration using flext-core base classes."""

    # Core configuration
    profile: str = Field("default", description="Current configuration profile")
    debug: bool = Field(False, description="Enable debug mode")

    # Component configurations
    output: CLIOutputConfig = Field(
        default_factory=CLIOutputConfig,
        description="Output configuration",
    )
    api: CLIAPIConfig = Field(
        default_factory=CLIAPIConfig,
        description="API client configuration",
    )
    auth: CLIAuthConfig = Field(
        default_factory=CLIAuthConfig,
        description="Authentication configuration",
    )
    directories: CLIDirectoryConfig = Field(
        default_factory=CLIDirectoryConfig,
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


def get_cli_config(reload: bool = False) -> CLIConfig:
    """Get CLI configuration singleton."""
    global _cli_config

    if _cli_config is None or reload:
        _cli_config = CLIConfig()
        _cli_config.ensure_setup()

    return _cli_config


@singleton()
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
    project_name: str = Field("flext-cli", description="Project name")
    project_version: str = Field("0.7.0", description="Project version")

    # CLI specific settings
    api_url: str = Field("http://localhost:8000", description="API base URL")
    timeout: int = Field(30, description="Request timeout in seconds")
    output_format: str = Field("table", description="Default output format")
    debug: bool = Field(False, description="Debug mode")


def get_cli_settings() -> CLISettings:
    """Get CLI settings instance."""
    return CLISettings()
