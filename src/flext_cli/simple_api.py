"""Simple API for FLEXT CLI setup and configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Provides a simple interface for setting up the FLEXT CLI application.
"""

from __future__ import annotations

from typing import Any

# Use centralized ServiceResult from flext-core - ELIMINATE DUPLICATION
from flext_core.domain.types import ServiceResult

from flext_cli.utils.config import CLIConfig as CLISettings


def setup_cli(settings: CLISettings | None = None) -> ServiceResult[bool]:
    """Sets up a CLI application.

    Args:
        settings: CLI settings to use

    Returns:
        ServiceResult indicating success or failure

    """
    try:
        if settings is None:
            settings = CLISettings()

        # Setup logging would be done here if needed
        # For now, just pass - basic console output works

        # Configuration is handled directly in CLIConfig

        return ServiceResult.ok(True)

    except Exception as e:
        return ServiceResult.fail(f"Failed to setup CLI: {e}")


def create_development_cli_config(**overrides: Any) -> CLISettings:
    """Create development CLI configuration."""
    # Development defaults
    defaults = {
        "debug": True,
        "trace": True,
        "log_level": "DEBUG",
        "api_url": "http://localhost:8000",
        "api_timeout": 30,
        "output_format": "table",
        "no_color": False,
        "profile": "development",
        "connect_timeout": 10,
        "read_timeout": 30,
        "command_timeout": 300,
    }

    # Override with provided values
    defaults.update(overrides)

    return CLISettings.model_validate(defaults)


def create_production_cli_config(**overrides: Any) -> CLISettings:
    """Create production CLI configuration."""
    # Production defaults
    defaults = {
        "debug": False,
        "trace": False,
        "log_level": "INFO",
        "api_url": "https://api.flext-platform.com",
        "api_timeout": 30,
        "output_format": "table",
        "no_color": False,
        "profile": "production",
        "connect_timeout": 10,
        "read_timeout": 60,
        "command_timeout": 600,
    }

    # Override with provided values
    defaults.update(overrides)

    return CLISettings.model_validate(defaults)


def get_cli_settings() -> CLISettings:
    """Get CLI settings."""
    return CLISettings()


# Export convenience functions
__all__ = [
    "create_development_cli_config",
    "create_production_cli_config",
    "get_cli_settings",
    "setup_cli",
]
