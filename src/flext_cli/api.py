"""FLEXT CLI API - Direct flext-core integration without over-abstraction.

Main public API for the FLEXT CLI ecosystem. Provides essential CLI functionality
by directly extending FlextService and using Rich/Click appropriately.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

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

    # Declare attributes for type checking
    _bus: FlextBus
    _context: FlextContext
    _dispatcher: FlextDispatcher
    _registry: FlextRegistry
    _core: FlextCliCore
    _file_tools: FlextCliFileTools
    _output: FlextCliOutput
    _prompts: FlextCliPrompts
    _processors: FlextCliProcessors
    _cmd: FlextCliCmd
    _click: FlextCliCli
    _formatters: FlextCliFormatters
    _tables: FlextCliTables
    _main: FlextCliMain

    def __init__(self) -> None:
        """Initialize CLI API thin facade with Phase 1 context enrichment."""
        # Initialize logger first
        self.logger = FlextLogger(__name__)

        # Initialize flext-core advanced features
        self._bus = FlextBus()
        self._context = FlextContext()
        self._dispatcher = FlextDispatcher()
        self._registry = FlextRegistry(dispatcher=self._dispatcher)
        self._container = FlextContainer()

        # Phase 1 Enhancement: Enrich context with service metadata
        # This automatically adds CLI service information to all logs
        FlextContext.Service.set_service_name("flext-cli")
        FlextContext.Service.set_service_version("1.0.0")

        # Enrich logger with correlation tracking
        correlation_id = FlextContext.Correlation.generate_correlation_id()
        self.logger.bind_global_context(
            service_name="flext-cli",
            service_type="FlextCli",
            correlation_id=correlation_id,
        )

        # Initialize domain services for property access
        self._core = FlextCliCore()
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
    def core(self) -> FlextCliCore:
        """Access core CLI service for command management.

        Returns:
            FlextCliCore: Core CLI service instance

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
    def context(self) -> FlextCliContext:
        """Access CLI context service.

        Returns:
            FlextCliContext: Context service instance

        """
        return FlextCliContext()

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
    def plugins(self) -> FlextCliPlugins:
        """Access CLI plugin system.

        Returns:
            FlextCliPlugins: Plugin system instance

        Example:
            >>> cli = FlextCliApi()
            >>> plugin_system = cli.plugins
            >>> discover_result = plugin_system.discover_plugins("./plugins")

        """
        return FlextCliPlugins()

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
    # MODEL-DRIVEN CLI UTILITIES - Pydantic model integration for CLI
    # ==========================================================================

    @property
    def model_converter(self) -> type[FlextCliModels.CliModelConverter]:
        """Access Pydantic model to CLI parameter converter.

        Returns:
            type[FlextCliModels.CliModelConverter]: Model converter utilities

        Example:
            >>> cli = FlextCli()
            >>> converter = cli.model_converter()
            >>> params_result = converter.model_to_cli_params(MyModel)

        """
        return FlextCliModels.CliModelConverter

    @property
    def model_decorators(self) -> type[FlextCliModels.CliModelDecorators]:
        """Access model-driven CLI decorators.

        Returns:
            type[FlextCliModels.CliModelDecorators]: Model decorator utilities

        Example:
            >>> from flext_cli import FlextCli
            >>> cli = FlextCli()
            >>> @cli.model_decorators.cli_from_model(ConfigModel)
            >>> def configure(config: ConfigModel):
            ...     pass

        """
        return FlextCliModels.CliModelDecorators

    @property
    def model_handler_factory(self) -> type[FlextCliHandlers.ModelHandlerFactory]:
        """Access model-driven handler factory.

        Returns:
            type[FlextCliHandlers.ModelHandlerFactory]: Handler factory utilities

        Example:
            >>> cli = FlextCli()
            >>> factory = cli.model_handler_factory()
            >>> handler = factory.create_command_handler_from_model(Model, logic)

        """
        return FlextCliHandlers.ModelHandlerFactory

    @property
    def model_handler_decorators(self) -> type[FlextCliHandlers.ModelHandlerDecorators]:
        """Access model-driven handler decorators.

        Returns:
            type[FlextCliHandlers.ModelHandlerDecorators]: Handler decorator utilities

        Example:
            >>> from flext_cli import FlextCli
            >>> cli = FlextCli()
            >>> @cli.model_handler_decorators.model_command_handler(Model)
            >>> def handler(model: Model):
            ...     pass

        """
        return FlextCliHandlers.ModelHandlerDecorators

    @property
    def model_processor(self) -> type[FlextCliProcessors.ModelProcessor]:
        """Access model validation and processing utilities.

        Returns:
            type[FlextCliProcessors.ModelProcessor]: Model processor class

        Example:
            >>> cli = FlextCli()
            >>> processor = cli.model_processor()
            >>> result = processor.validate_with_model(data, Model)

        """
        return FlextCliProcessors.ModelProcessor

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
        return self._bus

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
        return self._context

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
        return self._container

    # Attributes initialized in __init__ (inherit types from FlextService)

    # ==========================================================================
    # CONVENIENCE METHODS - Direct access to common CLI operations
    # ==========================================================================

    def info(self, message: str, **kwargs: object) -> FlextResult[None]:
        """Display informational message.

        Args:
            message: Message to display
            **kwargs: Additional formatting options

        Returns:
            FlextResult[None]: Operation result

        """
        return self.output.display_message(message, message_type="info", **kwargs)

    def success(self, message: str, **kwargs: object) -> FlextResult[None]:
        """Display success message.

        Args:
            message: Message to display
            **kwargs: Additional formatting options

        Returns:
            FlextResult[None]: Operation result

        """
        return self.output.display_message(message, message_type="success", **kwargs)

    def error(self, message: str, **kwargs: object) -> FlextResult[None]:
        """Display error message.

        Args:
            message: Message to display
            **kwargs: Additional formatting options

        Returns:
            FlextResult[None]: Operation result

        """
        return self.output.display_message(message, message_type="error", **kwargs)

    def warning(self, message: str, **kwargs: object) -> FlextResult[None]:
        """Display warning message.

        Args:
            message: Message to display
            **kwargs: Additional formatting options

        Returns:
            FlextResult[None]: Operation result

        """
        return self.output.display_message(message, message_type="warning", **kwargs)

    def display_message(
        self, message: str, message_type: str = "info", **kwargs: object
    ) -> FlextResult[None]:
        """Display message with specified type.

        Args:
            message: Message to display
            message_type: Type of message (info, success, error, warning)
            **kwargs: Additional formatting options

        Returns:
            FlextResult[None]: Operation result

        """
        return self.output.display_message(message, message_type=message_type, **kwargs)

    def display_data(
        self, data: object, format_type: str = "table", **kwargs: object
    ) -> FlextResult[None]:
        """Display data in specified format.

        Args:
            data: Data to display
            format_type: Format type (table, json, yaml, etc.)
            **kwargs: Additional formatting options

        Returns:
            FlextResult[None]: Operation result

        """
        return self.output.display_data(data, format_type=format_type, **kwargs)

    def table(self, data: object, **kwargs: object) -> FlextResult[None]:
        """Display data as table.

        Args:
            data: Data to display as table
            **kwargs: Additional table options

        Returns:
            FlextResult[None]: Operation result

        """
        return self.output.display_data(data, format_type="table", **kwargs)

    def confirm(self, message: str, *, default: bool = False) -> FlextResult[bool]:
        """Prompt user for confirmation.

        Args:
            message: Confirmation message
            default: Default value if no input

        Returns:
            FlextResult[bool]: User confirmation result

        """
        return self.prompts.confirm(message, default=default)

    def prompt_text(
        self, message: str, default: str = "", **kwargs: object
    ) -> FlextResult[str]:
        """Prompt user for text input.

        Args:
            message: Prompt message
            default: Default value
            **kwargs: Additional prompt options

        Returns:
            FlextResult[str]: User input result

        """
        return self.prompts.prompt_text(message, default=default, **kwargs)

    def write_json(
        self, data: object, path: str | Path, **kwargs: object
    ) -> FlextResult[None]:
        """Write data to JSON file.

        Args:
            data: Data to write
            path: File path
            **kwargs: Additional write options

        Returns:
            FlextResult[None]: Write operation result

        """
        return self.file_tools.write_json(data, path, **kwargs)

    def read_json(self, path: str | Path, **kwargs: object) -> FlextResult[object]:
        """Read data from JSON file.

        Args:
            path: File path
            **kwargs: Additional read options

        Returns:
            FlextResult[object]: Read operation result

        """
        return self.file_tools.read_json(path, **kwargs)

    def write_yaml(
        self, data: object, path: str | Path, **kwargs: object
    ) -> FlextResult[None]:
        """Write data to YAML file.

        Args:
            data: Data to write
            path: File path
            **kwargs: Additional write options

        Returns:
            FlextResult[None]: Write operation result

        """
        return self.file_tools.write_yaml(data, path, **kwargs)

    def read_yaml(self, path: str | Path, **kwargs: object) -> FlextResult[object]:
        """Read data from YAML file.

        Args:
            path: File path
            **kwargs: Additional read options

        Returns:
            FlextResult[object]: Read operation result

        """
        return self.file_tools.read_yaml(path, **kwargs)

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
