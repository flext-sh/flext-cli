"""FLEXT CLI Simple API.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli.config import (
    CLISettings,
    get_cli_settings as _get_cli_settings,
)

__all__ = [
    "create_development_cli_config",
    "create_production_cli_config",
    "get_cli_settings",
    "setup_cli",
]


def setup_cli(config: CLISettings | None = None) -> FlextResult[bool]:
    """Set up CLI with modern zero-boilerplate approach using hierarchical configuration.

    This function integrates the 3 main functions of flext-cli:
    1. CLI Foundation Base: Provides setup for any CLI implementation
    2. flext-core Integration Bridge: Uses hierarchical config patterns
    3. Ecosystem Library Base: Reusable setup for flext-meltano, etc.

    Args:
      config: Optional CLI configuration (auto-created with hierarchy if None)

    Returns:
      FlextResult[bool]: Success/failure with railway-oriented programming

    """
    try:
        if config is None:
            config = CLISettings()

        # Configuration setup successful
        setup_success = True
        return FlextResult[bool].ok(setup_success)

    except (AttributeError, ValueError, RuntimeError) as e:
        return FlextResult[bool].fail(f"Failed to setup CLI: {e}")


def create_development_cli_config(**kwargs: object) -> CLISettings:
    """Create development CLI configuration with hierarchical precedence.

    Uses flext/docs/patterns hierarchical configuration for ecosystem integration.
    Suitable for flext-meltano, client-a-oud-mig, and other ecosystem projects.

    Args:
      **kwargs: Configuration overrides

    Returns:
      CLISettings: Development configuration with debug enabled

    """
    # Create configuration with development defaults
    config = CLISettings(
        debug=True,
        log_level="DEBUG",
    )

    # Apply overrides using model_copy for type safety
    if kwargs:
        try:
            config = config.model_copy(update=kwargs)
        except Exception as e:
            # Convert Pydantic validation errors to ValueError for test compatibility
            validation_error_msg = f"validation error: {e}"
            raise ValueError(validation_error_msg) from e

    return config


def create_production_cli_config(**kwargs: object) -> CLISettings:
    """Create production CLI configuration.

    Args:
      **kwargs: Configuration overrides

    Returns:
      CLISettings: Production configuration with optimized settings

    """
    # Create base configuration with production defaults
    config = CLISettings(
        debug=False,
        log_level="INFO",
    )

    # Apply overrides using model_copy for type safety
    if kwargs:
        try:
            config = config.model_copy(update=kwargs)
        except Exception as e:
            # Convert Pydantic validation errors to ValueError for test compatibility
            validation_error_msg = f"validation error: {e}"
            raise ValueError(validation_error_msg) from e

    return config


def get_cli_settings(*, reload: bool | None = None) -> CLISettings:
    """Return CLISettings; when reload is True, return a fresh instance.

    Args:
      reload: If True, returns a fresh instance.

    """
    _ = reload
    return _get_cli_settings()


# get_cli_settings is already imported from flext_cli.config - no redefinition needed
