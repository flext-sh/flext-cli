"""Shared service foundation for flext-cli components.

Centralizes access to configuration singleton while maintaining inheritance
aligned with `FlextService` from flext-core, avoiding duplication of initialization
across library services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import ABC
from collections.abc import Mapping, Sequence
from types import ModuleType
from typing import override

from pydantic_settings import BaseSettings

from flext_core import p, s, t as core_t

from flext_cli import FlextCliSettings, t


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
        del cls
        options = _RuntimeBootstrapOptions(config_type=FlextCliSettings)
        return options

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


class _RuntimeBootstrapOptions:
    """Concrete runtime bootstrap options compatible with core protocol."""

    def __init__(
        self,
        *,
        config_type: type[BaseSettings] | None = None,
    ) -> None:
        self.config_type: type[BaseSettings] | None = config_type
        self.config_overrides: Mapping[str, core_t.Scalar] | None = None
        self.context: p.Context | None = None
        self.subproject: str | None = None
        self.services: Mapping[str, core_t.RegisterableService] | None = None
        self.factories: Mapping[str, core_t.FactoryCallable] | None = None
        self.resources: Mapping[str, core_t.ResourceCallable] | None = None
        self.container_overrides: Mapping[str, core_t.Scalar] | None = None
        self.wire_modules: Sequence[ModuleType] | None = None
        self.wire_packages: Sequence[str] | None = None
        self.wire_classes: Sequence[type] | None = None
