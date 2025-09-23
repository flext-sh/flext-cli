"""CLI core service using flext-core directly.

Production-ready CLI service that uses flext-core services directly without
duplication or fallback mechanisms. Implements standardized architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.models import FlextCliModels
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
)


class FlextCliService(FlextService[str]):
    """Essential CLI service using flext-core directly.

    Provides CLI configuration management using flext-core patterns.
    No over-engineered abstractions or unused functionality.
    """

    def __init__(self) -> None:
        """Initialize CLI service with flext-core dependencies."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()
        self._cli_config = FlextCliModels.FlextCliConfig.create_default()

    def execute(self) -> FlextResult[str]:
        """Execute CLI service - required by FlextService."""
        self._logger.info("CLI service operational")
        return FlextResult[str].ok("FlextCliService operational")

    def get_cli_config(self) -> FlextCliModels.FlextCliConfig:
        """Get current CLI configuration.

        Returns:
            FlextCliModels.FlextCliConfig: Current CLI configuration.

        """
        return self._cli_config

    def set_cli_config(
        self, config: FlextCliModels.FlextCliConfig
    ) -> FlextResult[None]:
        """Set CLI configuration.

        Args:
            config: New CLI configuration

        Returns:
            FlextResult[None]: Success or failure result

        """
        if not isinstance(config, FlextCliModels.FlextCliConfig):
            return FlextResult[None].fail("Invalid configuration type")

        self._cli_config = config
        return FlextResult[None].ok(None)


__all__ = ["FlextCliService"]
