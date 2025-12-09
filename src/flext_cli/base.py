"""Shared service foundation for flext-cli components.

Centralizes access to configuration singleton while maintaining inheritance
aligned with `FlextService` from flext-core, avoiding duplication of initialization
across library services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import s, t

from flext_cli.config import FlextCliConfig


class FlextCliServiceBase(s[t.Json.JsonDict]):
    """Base class for flext-cli services with typed configuration access."""

    @classmethod
    def _runtime_bootstrap_options(cls) -> t.Types.RuntimeBootstrapOptions:
        """Return runtime bootstrap options for CLI services.

        Business Rule: This method provides runtime bootstrap configuration for
        all CLI services, ensuring they use FlextCliConfig as the configuration
        type. This enables proper DI integration and namespace access.

        Implication: All services extending FlextCliServiceBase automatically
        use FlextCliConfig for their runtime configuration, ensuring consistent
        configuration handling across all CLI services.

        Returns:
            Runtime bootstrap options with config_type set to FlextCliConfig

        """
        return {"config_type": FlextCliConfig}

    @property
    def cli_config(self) -> FlextCliConfig:
        """Return the shared `FlextCliConfig` singleton with full type support."""
        return FlextCliConfig.get_instance()

    @staticmethod
    def get_cli_config() -> FlextCliConfig:
        """Return shared `FlextCliConfig` singleton without instantiating service."""
        return FlextCliConfig.get_instance()


__all__ = [
    "FlextCliServiceBase",
    "s",
]
