"""FlextCliServiceBase - Service base class for flext-cli modules.

Provides a typed base class for all flext-cli services with access to CLI configuration.
Handles singleton configuration access and typed service inheritance.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextService, FlextTypes

from flext_cli.config import FlextCliConfig


class FlextCliServiceBase(FlextService[FlextTypes.JsonDict]):
    """Service base para flext-cli com acesso tipado a config.

    Acesso via instância:
        self.cli_config.output_format
        self.cli_config.debug

    Acesso estático:
        FlextCliServiceBase.get_cli_config().output_format
    """

    @property
    def cli_config(self) -> FlextCliConfig:
        """Retorna FlextCliConfig tipado (singleton)."""
        return FlextCliConfig.get_instance()

    @staticmethod
    def get_cli_config() -> FlextCliConfig:
        """Retorna FlextCliConfig (singleton)."""
        return FlextCliConfig.get_instance()


__all__ = [
    "FlextCliServiceBase",
]
