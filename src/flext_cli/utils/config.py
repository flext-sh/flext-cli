"""Configuration utilities for FLEXT CLI - using flext-core exclusively.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic_settings import SettingsConfigDict

# Use flext-core exclusively - NO DIRECT PYDANTIC IMPORTS
from flext_core import ServiceResult
from flext_core.config.base import BaseConfig, BaseSettings
from flext_core.domain.pydantic_base import Field


class CLIConfig(BaseConfig):
    """CLI configuration using flext-core declarative patterns."""

    # CLI-specific settings
    api_url: str = Field(
        default="http://localhost:8000",
        description="API server URL",
    )
    output_format: str = Field(
        default="table",
        description="Output format (table, json, yaml, csv, plain)",
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
    )
    profile: str = Field(
        default="default",
        description="Configuration profile",
    )

    # Directory settings
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

    # Auth settings
    token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "token",
        description="Auth token file",
    )
    refresh_token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "refresh_token",
        description="Refresh token file",
    )
    auto_refresh: bool = Field(
        default=True,
        description="Auto-refresh tokens",
    )

    # Output settings
    no_color: bool = Field(
        default=False,
        description="Disable colored output",
    )
    quiet: bool = Field(
        default=False,
        description="Suppress non-error output",
    )
    verbose: bool = Field(
        default=False,
        description="Enable verbose output",
    )

    # Project metadata (needed by BaseCLI)
    project_name: str = Field(default="flext-cli", description="Project name")
    project_version: str = Field(default="0.7.0", description="Project version")
    debug: bool = Field(default=False, description="Enable debug mode")


class CLISettings(BaseSettings):
    """CLI settings using flext-core BaseSettings."""

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        case_sensitive=False,
    )

    # Inherit from BaseSettings: project_name, project_version, environment, debug
    project_name: str = Field(default="flext-cli", description="Project name")
    project_version: str = Field(default="0.7.0", description="Project version")


# Global configuration instance
_config: CLIConfig | None = None


def get_config() -> CLIConfig:
    global _config
    if _config is None:
        _config = CLIConfig()
        # Force model rebuild to resolve forward references
        try:
            from flext_cli.domain.cli_context import CLIContext
            CLIContext.model_rebuild()
        except ImportError:
            pass  # CLIContext may not be imported yet
    return _config


def get_config_value(key: str, default: Any = None) -> Any:
    config = get_config()
    return getattr(config, key, default)


def set_config_value(key: str, value: Any) -> ServiceResult[None]:
    try:
        config = get_config()
        setattr(config, key, value)
        return ServiceResult.success(None)
    except Exception as e:
        return ServiceResult.failure(f"Failed to set config value: {e}")


def list_config_values() -> dict[str, Any]:
    config = get_config()
    return config.model_dump()


# Convenience functions
def get_config_dir() -> Path:
    return get_config().config_dir


def get_cache_dir() -> Path:
    return get_config().cache_dir


def get_log_dir() -> Path:
    return get_config().log_dir
