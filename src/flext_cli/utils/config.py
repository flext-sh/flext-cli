"""FLEXT CLI Configuration Utilities - Settings Management with FlextBaseSettings.

This module provides configuration management utilities for the FLEXT CLI using
flext-core FlextBaseSettings patterns. Supports hierarchical configuration,
environment variable overrides, and profile-based settings management.

Configuration Classes:
    - CLIConfig: Main CLI configuration with flext-core integration
    - CLISettings: Application settings with environment variable support
    - Profile-specific configuration loading and validation

Features:
    - FlextBaseSettings integration for type safety
    - Environment variable override support (FLX_*, FLEXT_CLI_*)
    - Profile-based configuration (dev, staging, prod)
    - Configuration validation and error handling
    - Secure value handling for sensitive data

Current Implementation Status:
    ✅ Basic CLIConfig with FlextBaseSettings
    ✅ Environment variable support
    ✅ Configuration validation and parsing
    ⚠️ Basic profile support (TODO: Sprint 1 - hierarchical profiles)
    ❌ Configuration encryption not implemented (TODO: Sprint 2)

Configuration Hierarchy:
    1. Command-line arguments (highest priority)
    2. Environment variables (FLX_*, FLEXT_CLI_*)
    3. Profile-specific configuration files (~/.flx/profiles/)
    4. Global configuration file (~/.flx/config.yaml)
    5. Default values (lowest priority)

TODO (docs/TODO.md):
    Sprint 1: Implement hierarchical profile loading system
    Sprint 2: Add configuration value encryption for secrets
    Sprint 3: Add configuration templates and validation schemas
    Sprint 9: Add advanced profile management with inheritance

Integration:
    - Used by all CLI commands for configuration access
    - Integrates with authentication for secure settings
    - Supports ecosystem service configuration
    - Profile-aware for multi-environment deployments

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from flext_core.models import FlextBaseSettings
from flext_core.result import FlextResult
from pydantic import Field
from pydantic_settings import SettingsConfigDict

if TYPE_CHECKING:
    from flext_core.flext_types import TConfigValue


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
    project_version: str = "0.9.0"
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


def parse_config_value(value: str) -> FlextResult[TConfigValue]:
    """Parse configuration value from string, attempting JSON first.

    This function eliminates code duplication in config commands.
    Follows SOLID principles and DRY pattern.

    Args:
        value: String value to parse

    Returns:
        FlextResult containing parsed value or error

    """
    try:
        # Try parsing as JSON first
        parsed_value = json.loads(value)
        return FlextResult.ok(parsed_value)
    except json.JSONDecodeError:
        # If not JSON, treat as string
        return FlextResult.ok(value)
    except (ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to parse config value: {e}")


def set_config_attribute(
    target_object: object,
    key: str,
    value: TConfigValue,
) -> FlextResult[str]:
    """Set configuration attribute on target object.

    This function eliminates code duplication in config commands.
    Follows SOLID principles and DRY pattern.

    Args:
        target_object: Object to set attribute on
        key: Attribute key
        value: Parsed value to set

    Returns:
        FlextResult containing success message or error

    """
    try:
        if hasattr(target_object, key):
            setattr(target_object, key, value)
            return FlextResult.ok(
                f"Set {target_object.__class__.__name__.lower()}.{key} = {value}",
            )
        return FlextResult.fail(
            f"Attribute '{key}' not found on {target_object.__class__.__name__}",
        )
    except (AttributeError, TypeError, ValueError) as e:
        return FlextResult.fail(f"Failed to set attribute '{key}': {e}")
