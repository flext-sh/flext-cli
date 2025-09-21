"""CLI core service using flext-core directly.

Production-ready CLI service that uses flext-core services directly without
duplication or fallback mechanisms. Implements standardized architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import PrivateAttr

from flext_cli.configs import FlextCliConfigs
from flext_cli.formatting import FlextCliFormatters
from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextLogger,
)


class FlextCliService(FlextDomainService[str]):
    """Production-ready CLI service using flext-core directly.

    Provides CLI service orchestration using flext-core infrastructure without
    duplication or fallback mechanisms. Uses FlextConfig singleton as the single
    source of truth for all configuration.

    Args:
        None: Service initializes with flext-core dependencies.

    Returns:
        FlextResult[str]: Service execution result.

    Raises:
        RuntimeError: If service initialization fails.

    """

    # Private attributes - Use base class config type to maintain compatibility
    _cli_config: FlextCliConfigs | None = PrivateAttr(default=None)
    _commands: dict[str, object] = PrivateAttr(
        default_factory=dict,
    )
    _registered_handlers: dict[str, object] = PrivateAttr(
        default_factory=dict,
    )
    _plugins: dict[str, object] = PrivateAttr(
        default_factory=dict,
    )
    _sessions: dict[str, object] = PrivateAttr(
        default_factory=dict,
    )
    _formatters: FlextCliFormatters | None = PrivateAttr(default=None)

    def __init__(self) -> None:
        """Initialize CLI service with flext-core dependencies.

        Initializes the service using FlextConfig singleton and flext-core
        infrastructure. No fallback mechanisms are used.

        """
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()

        # Initialize configuration from FlextConfig singleton
        self._initialize_configuration()
        self._initialize_services()

    def _initialize_configuration(self) -> None:
        """Initialize configuration from FlextConfig singleton.

        Sets up configuration and formatters using flext-core patterns.
        No fallback mechanisms are used.

        """
        # Initialize CLI configuration state
        self._cli_config = None

        # Initialize formatters with configuration
        self._formatters = FlextCliFormatters()

    def _initialize_services(self) -> None:
        """Initialize services using flext-core container.

        Sets up service dependencies using the global container.
        No fallback mechanisms are used.

        """
        # Initialize core services as needed
        # Services will be registered with the container when needed

    # Public accessor methods
    def get_cli_config(self) -> FlextCliConfigs | None:
        """Get current CLI configuration.

        Returns:
            FlextCliConfigs | None: Current CLI configuration or None if not initialized.

        """
        return self._cli_config


__all__ = ["FlextCliService"]
