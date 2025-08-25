"""FLEXT CLI Configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

from flext_core import (
    FlextResult,
)

from flext_cli.config import FlextCliConfig

# =============================================================================
# CONFIGURATION FACTORY FUNCTIONS
# =============================================================================


def create_cli_config(
    profile: str = "default",
    **overrides: object,
) -> FlextResult[FlextCliConfig]:
    """Create CLI configuration with optional overrides.

    Args:
      profile: Configuration profile to load
      **overrides: Configuration overrides

    Returns:
      Result containing CLI configuration

    """
    try:
        # Start with default configuration
        # Use model_validate for proper construction
        config_data: dict[str, object] = {"profile": profile}
        config_data.update(overrides)
        config = FlextCliConfig.model_validate(config_data)

        # Configuration is already validated by Pydantic during model creation
        # No additional profile loading needed for basic usage

        return FlextResult[FlextCliConfig].ok(config)

    except Exception as e:
        return FlextResult[FlextCliConfig].fail(
            f"Failed to create CLI configuration: {e}"
        )


def create_cli_config_from_env() -> FlextResult[FlextCliConfig]:
    """Create CLI configuration from environment variables only."""
    try:
        config = FlextCliConfig()
        return FlextResult[FlextCliConfig].ok(config)

    except Exception as e:
        return FlextResult[FlextCliConfig].fail(
            f"Failed to create configuration from environment: {e}"
        )


def create_cli_config_from_file(file_path: Path) -> FlextResult[FlextCliConfig]:
    """Create CLI configuration from file."""
    try:
        # For now, use basic config creation until file loading is implemented
        config = FlextCliConfig()
        return FlextResult[FlextCliConfig].ok(config)
    except Exception as e:
        return FlextResult[FlextCliConfig].fail(
            f"Failed to load config from {file_path}: {e}"
        )


# Configuration aliases
# FlextCliConfig already defined above
create_flext_cli_config = create_cli_config
# FlextCliConfigHierarchical = FlextCliConfig  # Removed - FlextCliConfig moved to config.py


def get_cli_settings() -> object:
    """Compatibility helper for imports in simple_api/tests - returns default FlextCliConfig.

    This function returns a default FlextCliConfig instance with all fields set to their
    default values (profile='default', output_format=TABLE, debug=False, etc.).

    Important: This is a compatibility helper used primarily for imports in simple_api
    and test scenarios. Production code should not rely on its concrete behavior but
    should inject or construct a FlextCliConfig explicitly with proper configuration.

    Tests typically patch or monkeypatch this function to provide controlled configurations.

    Thread safety: This function is thread-safe as it creates a new instance each time.
    No side effects or global state modifications occur.

    Returns:
      A new FlextCliConfig instance with default values

    """
    return FlextCliConfig()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Factory functions
    "create_cli_config",
    "create_cli_config_from_env",
    "create_cli_config_from_file",
    "create_flext_cli_config",
    # Helper functions
    "get_cli_settings",
]
