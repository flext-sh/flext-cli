"""Base class para flext-cli services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextService

from flext_cli.config import FlextCliConfig
from flext_cli.typings import FlextCliTypes


class FlextCliServiceBase(FlextService[FlextCliTypes.Data.CliDataDict]):
    """Service base para flext-cli com acesso tipado a config.

    Acesso via instância:
        self.cli_config.output_format
        self.cli_config.debug

    Acesso estático:
        FlextCliServiceBase.get_cli_config().output_format
    """

    @property
    def cli_config(self) -> FlextCliConfig:
        """Retorna FlextCliConfig tipado."""
        return self.config.get_namespace("cli", FlextCliConfig)

    @staticmethod
    def get_cli_config() -> FlextCliConfig:
        """Retorna FlextCliConfig (singleton)."""
        return FlextCliConfig.get_instance()


__all__ = [
    "FlextCliServiceBase",
]
