"""FLEXT CLI Configuration Model.

Modern CLI configuration using FlextConfig base class with all functionality
consolidated into a single class without auxiliary helpers or duplications.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, override

from flext_core import FlextConfig, FlextConstants, FlextResult
from pydantic import Field


class FlextCliConfig(FlextConfig):
    """Modern CLI configuration using FlextConfig base with consolidated functionality."""

    # Core CLI settings
    profile: str = Field(default="default", description="Configuration profile")
    debug: bool = Field(default=False, description="Enable debug mode")
    trace: bool = Field(default=False, description="Enable trace mode")
    log_level: str = Field(default="INFO", description="Logging level")
    command_timeout: int = Field(default=FlextConstants.Performance.COMMAND_TIMEOUT, description="Command execution timeout")

    # Project identity
    project_name: str = Field(default="flext-cli", description="Project name")
    project_description: str = Field(
        default="FLEXT CLI - Developer Command Line Interface",
        description="Project description",
    )

    # API configuration (consolidated from FlextCliApiConfig)
    api_url: str = Field(default=f"http://{FlextConstants.Infrastructure.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}", description="API base URL")
    api_timeout: int = Field(default=FlextConstants.Defaults.TIMEOUT, le=300, description="API request timeout")
    connect_timeout: int = Field(default=FlextConstants.Defaults.CONNECTION_TIMEOUT, description="Connection timeout")
    read_timeout: int = Field(default=FlextConstants.Defaults.TIMEOUT, description="Read timeout")
    retries: int = Field(default=FlextConstants.Defaults.MAX_RETRIES, description="Maximum retry attempts")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

    # Output configuration (consolidated from FlextCliOutputConfig)
    output_format: Literal["table", "json", "yaml", "csv", "plain"] = Field(
        default="table", description="Default output format"
    )
    no_color: bool = Field(default=False, description="Disable colored output")
    quiet: bool = Field(default=False, description="Minimal output mode")
    verbose: bool = Field(default=False, description="Verbose output mode")
    pager: str | None = Field(default=None, description="Optional pager command")

    # Directory configuration (consolidated from FlextCliDirectoryConfig)
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

    # Authentication configuration (consolidated from FlextCliAuthConfig)
    token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "auth" / "token",
        description="Authentication token file",
    )
    refresh_token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "auth" / "refresh_token",
        description="Refresh token file",
    )
    auto_refresh: bool = Field(default=True, description="Automatic token refresh")

    def ensure_setup(self) -> None:
        """Ensure on-disk directories for config/cache/logs and auth exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.refresh_token_file.parent.mkdir(parents=True, exist_ok=True)

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate configuration business rules."""
        if self.api_timeout <= 0 or self.command_timeout <= 0:
            return FlextResult[None].fail("Invalid timeout values")
        if self.retries < 0:
            return FlextResult[None].fail("Retries cannot be negative")
        return FlextResult[None].ok(None)

    # Compatibility properties for legacy API usage
    @property
    def base_url(self) -> str:
        """Return API URL without trailing slashes."""
        return self.api_url.rstrip("/")

    @property
    def project_version(self) -> str:
        """CLI project version."""
        return "0.9.0"

    @override
    def __repr__(self) -> str:
        """Return string representation of FlextCliConfig."""
        return f"FlextCliConfig(api_url='{self.api_url}', timeout={self.api_timeout}, profile='{self.profile}')"

    @override
    def __str__(self) -> str:
        """Return string representation of FlextCliConfig."""
        return self.__repr__()

    @override
    def __hash__(self) -> int:
        """Return hash value for FlextCliConfig."""
        key = (
            self.profile,
            self.api_url,
            self.api_timeout,
            self.output_format,
            self.debug,
            self.log_level,
        )
        return hash(key)


# Module-level configuration instances and functions following flext-core patterns
class _ConfigSingleton:
    """Singleton for configuration instance."""

    _instance: FlextCliConfig | None = None

    @classmethod
    def get_instance(cls) -> FlextCliConfig:
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = FlextCliConfig()
            cls._instance.ensure_setup()
        return cls._instance


def get_config() -> FlextCliConfig:
    """Get global CLI configuration instance using flext-core patterns."""
    return _ConfigSingleton.get_instance()


def get_cli_config() -> FlextCliConfig:
    """Alias for get_config() for backward compatibility."""
    return get_config()


def flext_cli_settings() -> FlextCliConfig:
    """Factory function for FlextCliConfig for backward compatibility."""
    return FlextCliConfig()


# Keep the uppercase version for backward compatibility
FlextCliSettings = flext_cli_settings


def get_cli_settings() -> FlextCliConfig:
    """Get CLI settings - alias for get_config for backward compatibility."""
    return get_config()


__all__ = [
    "FlextCliConfig",
    "FlextCliSettings",
    "flext_cli_settings",
    "get_cli_config",
    "get_cli_settings",
    "get_config",
]
