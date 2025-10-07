"""FLEXT CLI API - Direct flext-core integration without over-abstraction.

Main public API for the FLEXT CLI ecosystem. Provides essential CLI functionality
by directly extending FlextService and using Rich/Click appropriately.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import (
    FlextBus,
    FlextContainer,
    FlextContext,
    FlextDispatcher,
    FlextLogger,
    FlextRegistry,
    FlextResult,
    FlextUtilities,
)

from flext_cli.auth import FlextCliAuth
from flext_cli.cli import FlextCliCli
from flext_cli.cmd import FlextCliCmd
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext
from flext_cli.core import FlextCliCore
from flext_cli.debug import FlextCliDebug
from flext_cli.exceptions import FlextCliExceptions
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.formatters import FlextCliFormatters
from flext_cli.handlers import FlextCliHandlers
from flext_cli.main import FlextCliMain
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import FlextCliModels
from flext_cli.output import FlextCliOutput
from flext_cli.plugins import FlextCliPlugins
from flext_cli.processors import FlextCliProcessors
from flext_cli.prompts import FlextCliPrompts
from flext_cli.protocols import FlextCliProtocols
from flext_cli.tables import FlextCliTables
from flext_cli.typings import FlextCliTypes


class FlextCli:
    """Thin facade for flext-cli providing access to all CLI functionality.

    This is the single entry point for the flext-cli library, exposing all
    domain services through properties for direct access. Uses domain-specific
    types from FlextCliTypes.
    Extends FlextService with CLI-specific data dictionary types.
    """

    @classmethod
    def get_instance(cls) -> FlextCli:
        """Get singleton FlextCli instance from container.

        Returns:
            FlextCli: Singleton instance from FlextContainer

        Example:
            >>> cli = FlextCli.get_instance()
            >>> # Same instance every time - no repetitive initialization

        """
        container = FlextContainer.get_global()
        result = container.get("flext_cli")

        # If not registered yet, create and register
        if result.is_failure or result.value is None:
            return cls()

        # Type assertion: container.get returns FlextCli instance
        return result.value  # type: ignore[return-value]

    def __init__(self) -> None:
        """Initialize CLI API with minimal setup - services lazy-loaded on demand."""
        # Initialize logger first
        self.logger = FlextLogger(__name__)

        # Get global container for DI
        self._container = FlextContainer.get_global()

        # Register this instance as singleton in container for DI
        self._container.register("flext_cli", self)

        # Phase 1 Enhancement: Enrich context with service metadata
        FlextContext.Service.set_service_name("flext-cli")
        FlextContext.Service.set_service_version("1.0.0")

        # Enrich logger with correlation tracking
        correlation_id = FlextContext.Correlation.generate_correlation_id()
        self.logger.bind_global_context(
            service_name="flext-cli",
            service_type="FlextCli",
            correlation_id=correlation_id,
        )

    # ==========================================================================
    # THIN FACADE PROPERTIES - Direct access to all domain services
    # ==========================================================================

    @property
    def core(self) -> FlextCliCore:
        """Access core CLI service for command management.

        Returns:
            FlextCliCore: Core CLI service instance

        """
        return self._container.get_or_register("core", FlextCliCore).unwrap()

    @property
    def cmd(self) -> FlextCliCmd:
        """Access CLI command service for configuration management.

        Returns:
            FlextCliCmd: Command service instance

        """
        return self._container.get_or_register("cmd", FlextCliCmd).unwrap()

    @property
    def models(self) -> type[FlextCliModels]:
        """Access CLI models for Pydantic validation.

        Returns:
            type[FlextCliModels]: CLI models class

        """
        return FlextCliModels

    @property
    def types(self) -> type[FlextCliTypes]:
        """Access CLI type definitions.

        Returns:
            type[FlextCliTypes]: CLI types class

        """
        return FlextCliTypes

    @property
    def constants(self) -> type[FlextCliConstants]:
        """Access CLI constants.

        Returns:
            type[FlextCliConstants]: CLI constants class

        """
        return FlextCliConstants

    @property
    def config(self) -> FlextCliConfig:
        """Access CLI configuration singleton.

        Returns:
            FlextCliConfig: Singleton CLI config instance from FlextContainer

        """
        # Use singleton pattern from FlextConfig
        config = FlextCliConfig.get_global_instance()
        config.__class__ = FlextCliConfig
        return config

    @property
    def output(self) -> FlextCliOutput:
        """Access CLI output formatting service.

        Returns:
            FlextCliOutput: Output service instance

        """
        return self._container.get_or_register("output", FlextCliOutput).unwrap()

    @property
    def file_tools(self) -> FlextCliFileTools:
        """Access CLI file operations service.

        Returns:
            FlextCliFileTools: File tools instance

        """
        return self._container.get_or_register(
            "file_tools", FlextCliFileTools
        ).unwrap()

    @property
    def utilities(self) -> type[FlextUtilities]:
        """Access utility functions from flext-core.

        Returns:
            type[FlextUtilities]: Utilities class from flext-core

        """
        return FlextUtilities

    @property
    def auth(self) -> FlextCliAuth:
        """Access CLI authentication service.

        Returns:
            FlextCliAuth: Auth service instance

        """
        return self._container.get_or_register("auth", FlextCliAuth).unwrap()

    @property
    def commands(self) -> FlextCliCommands:
        """Access CLI commands registry.

        Returns:
            FlextCliCommands: Commands instance

        """
        return self._container.get_or_register("commands", FlextCliCommands).unwrap()

    @property
    def context(self) -> FlextCliContext:
        """Access CLI context service.

        Returns:
            FlextCliContext: Context service instance

        """
        return self._container.get_or_register("context", FlextCliContext).unwrap()

    @property
    def debug(self) -> FlextCliDebug:
        """Access CLI debug service.

        Returns:
            FlextCliDebug: Debug service instance

        """
        return self._container.get_or_register("debug", FlextCliDebug).unwrap()

    @property
    def exceptions(self) -> type[FlextCliExceptions]:
        """Access CLI exceptions.

        Returns:
            type[FlextCliExceptions]: Exceptions class

        """
        return FlextCliExceptions

    @property
    def handlers(self) -> type[FlextCliHandlers]:
        """Access CLI handlers.

        Returns:
            type[FlextCliHandlers]: Handlers class

        """
        return FlextCliHandlers

    @property
    def mixins(self) -> type[FlextCliMixins]:
        """Access CLI mixins.

        Returns:
            type[FlextCliMixins]: Mixins class

        """
        return FlextCliMixins

    @property
    def processors(self) -> FlextCliProcessors:
        """Access CLI processors.

        Returns:
            FlextCliProcessors: Processors instance

        """
        return self._container.get_or_register(
            "processors", FlextCliProcessors
        ).unwrap()

    @property
    def plugins(self) -> FlextCliPlugins:
        """Access CLI plugin system.

        Returns:
            FlextCliPlugins: Plugin system instance

        Example:
            >>> cli = FlextCli.get_instance()
            >>> plugin_system = cli.plugins
            >>> discover_result = plugin_system.discover_plugins("./plugins")

        """
        return self._container.get_or_register("plugins", FlextCliPlugins).unwrap()

    @property
    def prompts(self) -> FlextCliPrompts:
        """Access CLI prompts.

        Returns:
            FlextCliPrompts: Prompts instance

        """
        return self._container.get_or_register("prompts", FlextCliPrompts).unwrap()

    @property
    def protocols(self) -> type[FlextCliProtocols]:
        """Access CLI protocols.

        Returns:
            type[FlextCliProtocols]: Protocols class

        """
        return FlextCliProtocols

    # ==========================================================================
    # PHASE 1 TRANSFORMATION COMPONENTS - Click/Rich/Tabulate abstractions
    # ==========================================================================

    @property
    def click(self) -> FlextCliCli:
        """Access Click abstraction layer.

        ZERO TOLERANCE - ONLY Click file should import click directly.

        Returns:
            FlextCliCli: Click abstraction instance

        Example:
            >>> cli = FlextCli()
            >>> cmd_result = cli.click.create_command_decorator(name="hello")

        """
        return self._container.get_or_register("click", FlextCliCli).unwrap()

    @property
    def formatters(self) -> FlextCliFormatters:
        """Access Rich formatters abstraction layer.

        Returns:
            FlextCliFormatters: Rich formatters instance

        Example:
            >>> cli = FlextCli()
            >>> panel_result = cli.formatters.create_panel(
            ...     content="Hello", title="Greeting"
            ... )

        """
        return self._container.get_or_register(
            "formatters", FlextCliFormatters
        ).unwrap()

    @property
    def tables(self) -> FlextCliTables:
        """Access Tabulate tables integration layer.

        Returns:
            FlextCliTables: Tabulate tables instance

        Example:
            >>> cli = FlextCli()
            >>> table_result = cli.tables.create_table(
            ...     data=[{"name": "Alice", "age": 30}], format="grid"
            ... )

        """
        return self._container.get_or_register("tables", FlextCliTables).unwrap()

    @property
    def main(self) -> FlextCliMain:
        """Access CLI command registration system.

        Returns:
            FlextCliMain: Main CLI instance

        Example:
            >>> cli = FlextCli()
            >>> @cli.main.command()
            >>> def hello(name: str):
            ...     print(f"Hello {name}!")

        """
        return self._container.get_or_register("main", FlextCliMain).unwrap()

    # ==========================================================================
    # FLEXT-CORE ADVANCED FEATURES - Event bus, registry, CQRS, etc.
    # ==========================================================================

    @property
    def bus(self) -> FlextBus:
        """Access FlextBus for event-driven architecture.

        Returns:
            FlextBus: Event bus instance for message routing

        """
        return self._container.get_or_register("bus", FlextBus).unwrap()

    @property
    def registry(self) -> FlextRegistry:
        """Access FlextRegistry for service discovery.

        Returns:
            FlextRegistry: Service registry instance

        """
        # Registry needs dispatcher - use lambda for dependency
        return self._container.get_or_register(
            "registry", lambda: FlextRegistry(dispatcher=self.dispatcher)
        ).unwrap()

    @property
    def dispatcher(self) -> FlextDispatcher:
        """Access FlextDispatcher for message dispatching.

        Returns:
            FlextDispatcher: Message dispatcher instance

        """
        return self._container.get_or_register("dispatcher", FlextDispatcher).unwrap()

    @property
    def container(self) -> FlextContainer:
        """Access FlextContainer for dependency injection.

        Returns:
            FlextContainer: DI container instance

        """
        return self._container

    # Attributes initialized in __init__ (inherit types from FlextService)

    def run(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Run CLI API operations.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: API execution result

        """
        return self.execute()

    def execute(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute CLI API operations.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: API execution result

        """
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": FlextCliConstants.FLEXT_CLI,
            "version": FlextCliConstants.VERSION,
            "timestamp": FlextUtilities.Generators.generate_timestamp(),
            "components": {
                "api": FlextCliConstants.AVAILABLE,
                "auth": FlextCliConstants.AVAILABLE,
                "config": FlextCliConstants.AVAILABLE,
                "debug": FlextCliConstants.AVAILABLE,
                "core": FlextCliConstants.AVAILABLE,
                "cmd": FlextCliConstants.AVAILABLE,
                "file_tools": FlextCliConstants.AVAILABLE,
                "output": FlextCliConstants.AVAILABLE,
                "utilities": FlextCliConstants.AVAILABLE,
                "prompts": FlextCliConstants.AVAILABLE,
                "processors": FlextCliConstants.AVAILABLE,
            },
        })


__all__ = [
    "FlextCli",
]
