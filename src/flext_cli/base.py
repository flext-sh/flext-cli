"""Shared service foundation for flext-cli components.

Centralizes access to configuration singleton while maintaining inheritance
aligned with `FlextService` from flext-core, avoiding duplication of initialization
across library services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import s as flext_service, t

from flext_cli.config import FlextCliConfig


class FlextCliServiceBase(flext_service[t.Json.JsonDict]):
    """Base class for flext-cli services with typed configuration access."""

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
]
