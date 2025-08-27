"""Legacy compatibility layer for FLEXT CLI Configuration.

This module provides backward compatibility for old configuration patterns
and helper functions that have been deprecated in favor of the modern FlextConfig API.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli.config import FlextCliConfig


# Add compatibility properties that were removed from main config
def get_timeout(config: FlextCliConfig) -> int:
    """Legacy: Get timeout value from api_timeout for backwards compatibility."""
    return config.api_timeout


def get_max_retries(config: FlextCliConfig) -> int:
    """Legacy: Get max_retries value from retries for backwards compatibility."""
    return config.retries


# Legacy compatibility functions for accessing deprecated property names

# ----------------------------------------------------------------------------
# Legacy singleton pattern and helpers
# ----------------------------------------------------------------------------

_config: FlextCliConfig | None = None


def _create_cli_config() -> FlextCliConfig:
    """Legacy: Create a new FlextCliConfig with defaults and ensure filesystem setup.

    Deprecated: Use FlextCliConfig() directly instead.
    """
    cfg = FlextCliConfig()  # Use defaults from Field definitions
    cfg.ensure_setup()
    return cfg


def get_cli_config(*, reload: bool = False) -> FlextCliConfig:
    """Legacy: Return a singleton-style CLI configuration instance.

    Set reload=True to create and return a fresh instance, replacing the cached one.

    Deprecated: Use FlextCliConfig() directly for new instances.
    """
    global _config  # noqa: PLW0603
    if reload or _config is None:
        _config = _create_cli_config()
    return _config


def get_config() -> FlextCliConfig:
    """Legacy: Return a fresh FlextCliConfig instance each call (not a singleton).

    Deprecated: Use FlextCliConfig() directly instead.
    """
    return FlextCliConfig()


def get_cli_settings() -> FlextCliConfig:
    """Legacy: Alias for getting CLI configuration as a fresh instance.

    Deprecated: Use FlextCliConfig() directly instead.
    """
    return FlextCliConfig()


def get_settings() -> FlextCliConfig:
    """Legacy: Alias for getting CLI configuration as a fresh instance.

    Deprecated: Use FlextCliConfig() directly instead.
    """
    return FlextCliConfig()


# ----------------------------------------------------------------------------
# Legacy nested configuration classes (deprecated signatures)
# ----------------------------------------------------------------------------


class FlextCliOutputConfig:
    """Legacy placeholder for old FlextCliOutputConfig.

    Deprecated: Configuration is now consolidated in FlextCliConfig.
    Use FlextCliConfig.output_format, no_color, quiet, verbose, pager instead.
    """

    def __init__(self) -> None:
        msg = (
            "FlextCliOutputConfig is deprecated. "
            "Use FlextCliConfig with direct fields: output_format, no_color, quiet, verbose, pager"
        )
        raise DeprecationWarning(msg)


class FlextCliApiConfig:
    """Legacy placeholder for old FlextCliApiConfig.

    Deprecated: Configuration is now consolidated in FlextCliConfig.
    Use FlextCliConfig.api_url, api_timeout, connect_timeout, read_timeout, retries, verify_ssl instead.
    """

    def __init__(self) -> None:
        msg = (
            "FlextCliApiConfig is deprecated. "
            "Use FlextCliConfig with direct fields: api_url, api_timeout, connect_timeout, read_timeout, retries, verify_ssl"
        )
        raise DeprecationWarning(msg)


class FlextCliAuthConfig:
    """Legacy placeholder for old FlextCliAuthConfig.

    Deprecated: Configuration is now consolidated in FlextCliConfig.
    Use FlextCliConfig.token_file, refresh_token_file, auto_refresh instead.
    """

    def __init__(self) -> None:
        msg = (
            "FlextCliAuthConfig is deprecated. "
            "Use FlextCliConfig with direct fields: token_file, refresh_token_file, auto_refresh"
        )
        raise DeprecationWarning(msg)


class FlextCliDirectoryConfig:
    """Legacy placeholder for old FlextCliDirectoryConfig.

    Deprecated: Configuration is now consolidated in FlextCliConfig.
    Use FlextCliConfig.config_dir, cache_dir, log_dir, data_dir instead.
    """

    def __init__(self) -> None:
        msg = (
            "FlextCliDirectoryConfig is deprecated. "
            "Use FlextCliConfig with direct fields: config_dir, cache_dir, log_dir, data_dir"
        )
        raise DeprecationWarning(msg)


class FlextCliSettings:
    """Legacy placeholder for old FlextCliSettings.

    Deprecated: Use FlextCliConfig directly instead.
    """

    def __init__(self) -> None:
        msg = "FlextCliSettings is deprecated. Use FlextCliConfig directly instead."
        raise DeprecationWarning(msg)


__all__ = [
    "FlextCliApiConfig",
    "FlextCliAuthConfig",
    "FlextCliDirectoryConfig",
    "FlextCliOutputConfig",
    "FlextCliSettings",
    "_create_cli_config",
    "get_cli_config",
    "get_cli_settings",
    "get_config",
    "get_max_retries",
    "get_settings",
    "get_timeout",
]
