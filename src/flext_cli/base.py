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
from dataclasses import dataclass
from types import ModuleType
from typing import override

from flext_core import s
from pydantic_settings import BaseSettings

from flext_cli import FlextCliSettings, m, p, t


@dataclass
class _CliRuntimeBootstrapOptions:
    config_type: type[BaseSettings] | None = FlextCliSettings
    config_overrides: Mapping[str, t.Scalar] | None = None
    context: p.Context | None = None
    subproject: str | None = None
    services: Mapping[str, t.RegisterableService] | None = None
    factories: Mapping[str, t.FactoryCallable] | None = None
    resources: Mapping[str, t.ResourceCallable] | None = None
    container_overrides: Mapping[str, t.Scalar] | None = None
    wire_modules: Sequence[ModuleType] | None = None
    wire_packages: Sequence[str] | None = None
    wire_classes: Sequence[type] | None = None


class FlextCliServiceBase(s[Mapping[str, t.Cli.JsonValue]], ABC):
    """Base class for flext-cli services with typed configuration access.

    Note: This is an abstract base class. Subclasses must implement the
    `execute` method from FlextService.
    """

    @property
    def cli_config(self) -> FlextCliSettings:
        """Return the shared `FlextCliSettings` singleton with full type support."""
        return FlextCliSettings.get_global()

    @override
    @classmethod
    def _runtime_bootstrap_options(cls) -> p.RuntimeBootstrapOptions | None:
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
        return m.RuntimeBootstrapOptions(config_type=FlextCliSettings)

    @staticmethod
    def get_cli_config() -> FlextCliSettings:
        """Return shared `FlextCliSettings` singleton without instantiating service."""
        return FlextCliSettings.get_global()


__all__ = ["FlextCliServiceBase", "s"]
