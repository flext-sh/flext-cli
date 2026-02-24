"""Shared service foundation for flext-cli components.

Centralizes access to configuration singleton while maintaining inheritance
aligned with `FlextService` from flext-core, avoiding duplication of initialization
across library services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import ABC
from collections.abc import Mapping
from typing import override

from flext_core import s
from flext_core.protocols import p

from flext_cli.settings import FlextCliSettings
from flext_cli.typings import t


class FlextCliServiceBase(s[Mapping[str, t.JsonValue]], ABC):
    """Base class for flext-cli services with typed configuration access.

    Note: This is an abstract base class. Subclasses must implement the
    `execute` method from FlextService.
    """

    @override
    @classmethod
    def _runtime_bootstrap_options(
        cls,
    ) -> p.RuntimeBootstrapOptions:
        """Return runtime bootstrap options for CLI services.

        Business Rule: This method provides runtime bootstrap configuration for
        all CLI services, ensuring they use FlextCliSettings as the configuration
        type. This enables proper DI integration and namespace access.

        Implication: All services extending FlextCliServiceBase automatically
        use FlextCliSettings for their runtime configuration, ensuring consistent
        configuration handling across all CLI services.

        Returns:
            Runtime bootstrap options with config_type set to FlextCliSettings

        """
        return p.RuntimeBootstrapOptions(config_type=FlextCliSettings)

    @property
    def cli_config(self) -> FlextCliSettings:
        """Return the shared `FlextCliSettings` singleton with full type support."""
        return FlextCliSettings.get_instance()

    @staticmethod
    def get_cli_config() -> FlextCliSettings:
        """Return shared `FlextCliSettings` singleton without instantiating service."""
        return FlextCliSettings.get_instance()


__all__ = [
    "FlextCliServiceBase",
    "s",
]
