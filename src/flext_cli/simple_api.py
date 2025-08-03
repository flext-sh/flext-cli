"""FLEXT CLI Simple API - Programmatic CLI Setup and Configuration.

This module provides a simplified programmatic interface for setting up and
configuring the FLEXT CLI application. Designed for embedding CLI functionality
into other applications or for programmatic CLI initialization.

API Functions:
    - setup_cli: Initialize CLI application with custom settings
    - Simplified configuration and initialization patterns
    - Integration with flext-core FlextResult patterns

Features:
    - Programmatic CLI initialization without Click entry points
    - Custom settings injection for embedded use cases
    - FlextResult-based error handling and validation
    - Integration with dependency injection container
    - Configuration validation and setup

Current Implementation Status:
    ✅ Basic setup_cli function with settings
    ✅ FlextResult integration for error handling
    ⚠️ Simple implementation (TODO: Sprint 2 - enhance setup)
    ❌ Advanced container setup not implemented (TODO: Sprint 1)

Use Cases:
    - Embedding CLI in other applications
    - Programmatic CLI testing and automation
    - Custom CLI initialization workflows
    - Integration with application frameworks

TODO (docs/TODO.md):
    Sprint 1: Integrate with FlextContainer setup
    Sprint 2: Add comprehensive CLI validation
    Sprint 3: Add programmatic command execution
    Sprint 8: Add embedded interactive mode support

Usage Examples:
    Basic setup:
    >>> from flext_cli.simple_api import setup_cli
    >>> from flext_cli.utils.config import CLISettings
    >>> settings = CLISettings(debug=True)
    >>> result = setup_cli(settings)
    >>> if result.is_success:
    ...     print("CLI ready for use")

    Custom configuration:
    >>> settings = CLISettings(
    ...     api_url="https://api.example.com",
    ...     output_format="json"
    ... )
    >>> setup_cli(settings)

Integration:
    - Used by main CLI entry point for initialization
    - Supports testing frameworks for CLI testing
    - Integrates with configuration management
    - Provides foundation for embedded CLI use

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
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
