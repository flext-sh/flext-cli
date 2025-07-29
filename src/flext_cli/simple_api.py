"""Simple API for FLEXT CLI setup and configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Provides a simple interface for setting up the FLEXT CLI application.
"""

from __future__ import annotations

from flext_core.result import FlextResult

from flext_cli.utils.config import CLISettings


def setup_cli(settings: CLISettings | None = None) -> FlextResult[bool]:
    """Set up a CLI application.

    Args:
        settings: CLI settings to use

    Returns:
        FlextResult indicating success or failure

        FlextResult indicating success or failure

    """
    try:
        if settings is None:
            settings = CLISettings()

        # Setup logging would be done here if needed
        # For now, just pass - basic console output works

        # Configuration is handled directly in CLIConfig

        success = True
        return FlextResult.ok(success)

    except (ImportError, AttributeError, ValueError) as e:
        return FlextResult.fail(f"Failed to setup CLI: {e}")
    except (RuntimeError, TypeError, OSError) as e:
        error_msg = f"Unexpected CLI setup error: {e}"
        return FlextResult.fail(error_msg)


def create_development_cli_config(**overrides: object) -> CLISettings:
    """Create development CLI configuration."""
    # Development defaults - only use fields that exist in CLISettings
    defaults = {
        "debug": True,
        "log_level": "DEBUG",
        "config_path": None,
    }

    # Override with provided values
    defaults.update(overrides)

    return CLISettings.model_validate(defaults)


def create_production_cli_config(**overrides: object) -> CLISettings:
    """Create production CLI configuration."""
    # Production defaults - only use fields that exist in CLISettings
    defaults = {
        "debug": False,
        "log_level": "INFO",
        "config_path": None,
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
