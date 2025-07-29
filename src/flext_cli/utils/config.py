"""Configuration utilities for FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextBaseSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class CLIConfig(FlextBaseSettings):
    """CLI configuration using flext-core patterns."""

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

    # Authentication settings
    token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "auth_token",
        description="Authentication token file path",
    )
    refresh_token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "refresh_token",
        description="Refresh token file path",
    )
    auto_refresh: bool = Field(
        default=True,
        description="Automatically refresh authentication tokens",
    )

    # CLI behavior
    debug: bool = Field(default=False, description="Debug mode enabled")
    quiet: bool = Field(default=False, description="Quiet mode enabled")
    verbose: bool = Field(default=False, description="Verbose mode enabled")
    no_color: bool = Field(default=False, description="No color output")

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )


class CLISettings(FlextBaseSettings):
    """CLI settings from environment variables using flext-core patterns."""

    project_name: str = "flext-cli"
    project_version: str = "0.8.0"
    project_description: str = "FLEXT CLI - Developer Command Line Interface"

    # Override defaults from environment
    debug: bool = False
    log_level: str = "INFO"
    config_path: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


def get_config() -> CLIConfig:
    """Get CLI configuration instance.

    Returns:
        CLI configuration

    """
    return CLIConfig()


def get_settings() -> CLISettings:
    """Get CLI settings from environment.

    Returns:
        CLI settings

    """
    return CLISettings()
