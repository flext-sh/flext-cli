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
    FlextService,
    FlextUtilities,
)

from flext_cli.auth import FlextCliAuth
from flext_cli.cli import FlextCliCli
from flext_cli.cmd import FlextCliCmd
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext
from flext_cli.core import FlextCliService
from flext_cli.debug import FlextCliDebug
from flext_cli.exceptions import FlextCliExceptions
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.formatters import FlextCliFormatters
from flext_cli.handlers import FlextCliHandlers
from flext_cli.main import FlextCliMain
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import FlextCliModels
from flext_cli.output import FlextCliOutput
from flext_cli.plugins import FlextCliPluginSystem
from flext_cli.processors import FlextCliProcessors
from flext_cli.prompts import FlextCliPrompts
from flext_cli.protocols import FlextCliProtocols
from flext_cli.tables import FlextCliTables
from flext_cli.typings import FlextCliTypes


class FlextCliApi(FlextService[FlextCliTypes.Data.CliDataDict]):
    """Thin facade for flext-cli providing access to all CLI functionality.

    This is the single entry point for the flext-cli library, exposing all
    domain services through properties for direct access. Uses domain-specific
    types from FlextCliTypes.
    Extends FlextService with CLI-specific data dictionary types.
    """

    def __init__(self, **data: object) -> None:
        """Initialize CLI API thin facade.

        Args:
            **data: Additional service initialization data

        """
        super().__init__(**data)
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer()

        # Initialize flext-core advanced features
        self._bus = FlextBus()
        self._context = FlextContext()
        self._dispatcher = FlextDispatcher()
        self._registry = FlextRegistry(dispatcher=self._dispatcher)

        # Initialize domain services for property access
        self._core = FlextCliService()
        self._file_tools = FlextCliFileTools()
        self._output = FlextCliOutput()
        self._prompts = FlextCliPrompts()
        self._processors = FlextCliProcessors()
        self._cmd = FlextCliCmd()

        # Initialize Phase 1 transformation components (NEW)
        self._click = FlextCliCli()
        self._formatters = FlextCliFormatters()
        self._tables = FlextCliTables()
        self._main = FlextCliMain()

    # ==========================================================================
    # THIN FACADE PROPERTIES - Direct access to all domain services
    # ==========================================================================

    @property
    def core(self) -> FlextCliService:
        """Access core CLI service for command management.

        Returns:
            FlextCliService: Core CLI service instance

        """
        return self._core

    @property
    def cmd(self) -> FlextCliCmd:
        """Access CLI command service for configuration management.

        Returns:
            FlextCliCmd: Command service instance

        """
        return self._cmd

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
        """Access CLI configuration.

        Returns:
            FlextCliConfig: CLI config instance

        """
        # Create instance and ensure proper type due to inheritance issues
        config = FlextCliConfig()
        config.__class__ = FlextCliConfig
        return config

    @property
    def output(self) -> FlextCliOutput:
        """Access CLI output formatting service.

        Returns:
            FlextCliOutput: Output service instance

        """
        return self._output

    @property
    def file_tools(self) -> FlextCliFileTools:
        """Access CLI file operations service.

        Returns:
            FlextCliFileTools: File tools instance

        """
        return self._file_tools

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
        return FlextCliAuth()

    @property
    def commands(self) -> FlextCliCommands:
        """Access CLI commands registry.

        Returns:
            FlextCliCommands: Commands instance

        """
        return FlextCliCommands()

    @property
    def context(self) -> type[FlextCliContext]:
        """Access CLI context.

        Returns:
            type[FlextCliContext]: Context class

        """
        return FlextCliContext

    @property
    def debug(self) -> FlextCliDebug:
        """Access CLI debug service.

        Returns:
            FlextCliDebug: Debug service instance

        """
        return FlextCliDebug()

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
        return self._processors

    @property
    def plugins(self) -> FlextCliPluginSystem:
        """Access CLI plugin system.

        Returns:
            FlextCliPluginSystem: Plugin system instance

        Example:
            >>> cli = FlextCliApi()
            >>> plugin_system = cli.plugins
            >>> discover_result = plugin_system.discover_plugins("./plugins")

        """
        return FlextCliPluginSystem()

    @property
    def prompts(self) -> FlextCliPrompts:
        """Access CLI prompts.

        Returns:
            FlextCliPrompts: Prompts instance

        """
        return self._prompts

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
        """Access Click abstraction layer (ZERO TOLERANCE - ONLY Click file).

        Returns:
            FlextCliCli: Click abstraction instance

        Example:
            >>> cli = FlextCliApi()
            >>> cmd_result = cli.click.create_command_decorator(name="hello")

        """
        return self._click

    @property
    def formatters(self) -> FlextCliFormatters:
        """Access Rich formatters abstraction layer.

        Returns:
            FlextCliFormatters: Rich formatters instance

        Example:
            >>> cli = FlextCliApi()
            >>> panel_result = cli.formatters.create_panel(
            ...     content="Hello", title="Greeting"
            ... )

        """
        return self._formatters

    @property
    def tables(self) -> FlextCliTables:
        """Access Tabulate tables integration layer.

        Returns:
            FlextCliTables: Tabulate tables instance

        Example:
            >>> cli = FlextCliApi()
            >>> table_result = cli.tables.create_table(
            ...     data=[{"name": "Alice", "age": 30}], format="grid"
            ... )

        """
        return self._tables

    @property
    def main(self) -> FlextCliMain:
        """Access CLI command registration system.

        Returns:
            FlextCliMain: Main CLI instance

        Example:
            >>> cli = FlextCliApi()
            >>> @cli.main.command()
            >>> def hello(name: str):
            ...     print(f"Hello {name}!")

        """
        return self._main

    # ==========================================================================
    # FLEXT-CORE ADVANCED FEATURES - Event bus, registry, CQRS, etc.
    # ==========================================================================

    @property
    def bus(self) -> FlextBus:
        """Access FlextBus for event-driven architecture.

        Returns:
            FlextBus: Event bus instance for message routing

        """
        return self._busFlextLDAPModels

    @property
    def registry(self) -> FlextRegistry:
        """Access FlextRegistry for service discovery.

        Returns:
            FlextRegistry: Service registry instance

        """
        return self._registry

    @property
    def flext_context(self) -> FlextContext:
        """Access FlextContext for execution context management.

        Returns:
            FlextContext: Execution context instance

        """
        return self._contextFlextLDAPModels

    @property
    def dispatcher(self) -> FlextDispatcher:
        """Access FlextDispatcher for message dispatching.

        Returns:
            FlextDispatcher: Message dispatcher instance

        """
        return self._dispatcher

    @property
    def flext_utilities(self) -> type[FlextUtilities]:
        """Access FlextUtilities from flext-core for utility functions.

        Returns:
            type[FlextUtilities]: Core utilities class

        """
        return FlextUtilities

    @property
    def container(self) -> FlextContainer:
        """Access FlextContainer for dependency injection.

        Returns:
            FlextContainer: DI container instance

        """
        return self._containerFlextLDAPModels

    # Attributes initialized in __init__ (inherit types from FlextService)

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
    "FlextCliApi",
]
