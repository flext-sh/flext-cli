"""Simple API for FLEXT CLI setup and configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Provides a simple interface for setting up the FLEXT CLI application.
"""

from __future__ import annotations

from typing import Any

# Use simplified import from flext-core - NEW ARCHITECTURE
from flext_core.domain.shared_types import ServiceResult

from flext_cli.config import CLIConfig, CLIOutputFormat, CLISettings


def setup_cli(settings: CLIConfig | None = None) -> ServiceResult[dict[str, Any]]:
    """Setup CLI application.

    Args:
        settings: CLI settings to use

    Returns:
        ServiceResult indicating success or failure

    """
    try:
        if settings is None:
            settings = CLIConfig()

        # Setup logging would be done here if needed
        # For now, just pass - basic console output works

        # Configuration is handled directly in CLIConfig

        return ServiceResult.ok({"setup_complete": True})

    except Exception as e:
        return ServiceResult.fail(f"Failed to setup CLI: {e}")


def create_development_cli_config(**overrides: Any) -> CLISettings:
    """Create development CLI configuration.

    Args:
        **overrides: Configuration overrides

    Returns:
        CLISettings instance with development defaults

    """
    # Development defaults - use actual CLISettings structure
    defaults = {
        "project_name": "flext-cli",
        "project_version": "0.7.0",
        "api_url": "http://localhost:8000",
        "timeout": 30,
        "output_format": "table",
        "debug": True,  # Development-specific: enable debug
    }

    # Override with provided values
    defaults.update(overrides)

    # Create using model_validate to handle extra fields properly
    return CLISettings.model_validate(defaults)


def create_production_cli_config(**overrides: Any) -> CLISettings:
    """Create production CLI configuration.

    Args:
        **overrides: Configuration overrides

    Returns:
        CLISettings instance with production defaults

    """
    # Production defaults - use actual CLISettings structure
    defaults = {
        "project_name": "flext-cli",
        "project_version": "0.7.0",
        "api_url": "https://api.flext-platform.com",
        "timeout": 30,
        "output_format": "table",
        "debug": False,
    }

    # Override with provided values
    defaults.update(overrides)

    # Create using model_validate to handle extra fields properly
    return CLISettings.model_validate(defaults)


def get_cli_settings() -> CLISettings:
    """Get CLI settings instance.

    Returns:
        CLISettings instance with default values

    """
    return CLISettings(
        project_name="flext-cli",
        project_version="0.7.0",
        api_url="http://localhost:8000",
        timeout=30,
        output_format=CLIOutputFormat.TABLE,
        debug=False,
    )


# Export convenience functions
__all__ = [
    "create_development_cli_config",
    "create_production_cli_config",
    "get_cli_settings",
    "setup_cli",
]
