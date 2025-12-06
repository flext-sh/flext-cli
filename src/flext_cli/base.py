"""Shared service foundation for flext-cli components.

Centraliza o acesso ao singleton de configuração enquanto mantém a herança
alinhada ao `FlextService` do flext-core, evitando duplicação de inicialização
entre os serviços da biblioteca.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextService, t

from flext_cli.config import FlextCliConfig


class FlextCliServiceBase(FlextService[t.Json.JsonDict]):
    """Base class for flext-cli services with typed configuration access."""

    @property
    def cli_config(self) -> FlextCliConfig:
        """Return the shared `FlextCliConfig` singleton with full type support."""
        return FlextCliConfig.get_instance()

    @staticmethod
    def get_cli_config() -> FlextCliConfig:
        """Return shared `FlextCliConfig` singleton without instantiating service."""
        return FlextCliConfig.get_instance()


s = FlextCliServiceBase

__all__ = [
    "FlextCliServiceBase",
    "s",
]
