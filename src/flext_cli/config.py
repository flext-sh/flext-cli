"""FLEXT CLI Configuration Models."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from flext_core.config import FlextSettings
from flext_core.constants import FlextConstants
from pydantic import BaseModel, Field

# ----------------------------------------------------------------------------
# Component configurations
# ----------------------------------------------------------------------------


class CLIOutputConfig(BaseModel):
    """Output configuration for CLI rendering and verbosity."""

    format: Literal["table", "json", "yaml", "csv", "plain"] = Field(
        default="table",
        description="Default output format",
    )
    no_color: bool = Field(default=False, description="Disable colored output")
    quiet: bool = Field(default=False, description="Minimal output mode")
    verbose: bool = Field(default=False, description="Verbose output mode")
    pager: str | None = Field(
        default=None,
        description="Optional pager command (e.g., 'less -R')",
    )


def _default_api_url() -> str:
    try:
        return f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
    except Exception:
        return "http://localhost:8000"


class CLIAPIConfig(BaseModel):
    """API connectivity configuration for FLEXT services."""

    url: str = Field(default_factory=_default_api_url)
    timeout: int = Field(default=30, le=300)
    connect_timeout: int = Field(default=10)
    read_timeout: int = Field(default=30)
    retries: int = Field(default=3)
    verify_ssl: bool = Field(default=True)

    @property
    def base_url(self) -> str:
        """Return URL without trailing slashes."""
        return self.url.rstrip("/")


class CLIAuthConfig(BaseModel):
    """Authentication token storage configuration."""

    token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "auth" / "token",
    )
    refresh_token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "auth" / "refresh_token",
    )
    auto_refresh: bool = Field(default=True)


class CLIDirectoryConfig(BaseModel):
    """Filesystem directory configuration for the CLI."""

    config_dir: Path = Field(default_factory=lambda: Path.home() / ".flext")
    cache_dir: Path = Field(default_factory=lambda: Path.home() / ".flext" / "cache")
    log_dir: Path = Field(default_factory=lambda: Path.home() / ".flext" / "logs")
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".flext" / "data")

    def ensure_directories(self) -> None:
        """Create the configured directories if they do not exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------------
# Main configuration and settings
# ----------------------------------------------------------------------------


class CLIConfig(BaseModel):
    """Top-level CLI configuration aggregate."""

    model_config = {"frozen": True}

    profile: str = Field(default="default")
    debug: bool = Field(default=False)
    trace: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    output: CLIOutputConfig = Field(default_factory=CLIOutputConfig)
    api: CLIAPIConfig = Field(default_factory=CLIAPIConfig)
    auth: CLIAuthConfig = Field(default_factory=CLIAuthConfig)
    directories: CLIDirectoryConfig = Field(default_factory=CLIDirectoryConfig)

    command_timeout: int = Field(default=300)

    def ensure_setup(self) -> None:
        """Ensure on-disk directories for config/cache/logs and auth exist."""
        self.directories.ensure_directories()
        self.auth.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.auth.refresh_token_file.parent.mkdir(parents=True, exist_ok=True)

    def validate_domain_rules(self) -> bool:
        """Validate simple invariants expected by tests."""
        if self.api.timeout <= 0:
            return False
        return not self.command_timeout <= 0


def _default_settings_api_url() -> str:
    try:
        return f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
    except Exception:
        return "http://localhost:8000"


class CLISettings(FlextSettings):
    """Application-level settings for the CLI.

    Uses environment variables with the prefix 'FLEXT_CLI_'.
    """

    project_name: str = Field(default="flext-cli")
    project_version: str = Field(default="0.9.0")
    project_description: str = Field(
        default="FLEXT CLI - Developer Command Line Interface",
    )

    api_url: str = Field(default_factory=_default_settings_api_url)
    timeout: int = Field(default=30)
    output_format: Literal["table", "json", "yaml", "csv", "plain"] = Field(
        default="table",
    )

    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    config_path: str | None = Field(default=None)

    class Config:  # noqa: D106
        env_prefix = "FLEXT_CLI_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# ----------------------------------------------------------------------------
# Accessors (singleton + factories)
# ----------------------------------------------------------------------------

_config: CLIConfig | None = None


def _create_cli_config() -> CLIConfig:
    """Create a new CLIConfig with defaults and ensure filesystem setup."""
    cfg = CLIConfig(profile="default", debug=False)
    cfg.ensure_setup()
    return cfg


def get_cli_config(*, reload: bool = False) -> CLIConfig:
    """Return a singleton-style CLI configuration instance.

    Set reload=True to create and return a fresh instance, replacing the cached one.
    """
    global _config  # noqa: PLW0603
    if reload or _config is None:
        _config = _create_cli_config()
    return _config


# Factory-style helpers used by some tests


def get_config() -> CLIConfig:
    """Return a fresh CLIConfig instance each call (not a singleton)."""
    return CLIConfig()


def get_settings() -> CLISettings:
    """Return a fresh CLISettings instance each call."""
    return CLISettings()


def get_cli_settings() -> CLISettings:
    """Alias for getting CLI settings as a fresh instance."""
    return CLISettings()


__all__ = [
    "CLIAPIConfig",
    "CLIAuthConfig",
    "CLIConfig",
    "CLIDirectoryConfig",
    "CLIOutputConfig",
    "CLISettings",
    # Accessors
    "_create_cli_config",
    "get_cli_config",
    "get_cli_settings",
    "get_config",
    "get_settings",
]
