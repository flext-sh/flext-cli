"""FLEXT CLI API - Direct flext-core integration without over-abstraction.

Main public API for the FLEXT CLI ecosystem. Provides essential CLI functionality
by directly extending FlextService and using Rich/Click appropriately.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json

try:
    import yaml
except ImportError:
    yaml = None

from flext_core import (
    FlextBus,
    FlextContainer,
    FlextContext,
    FlextDispatcher,
    FlextLogger,
    FlextProcessors,
    FlextRegistry,
    FlextResult,
    FlextService,
    FlextTypes,
    FlextUtilities,
)

from flext_cli.auth import FlextCliAuth
from flext_cli.cli import FlextCliClick
from flext_cli.cmd import FlextCliCmd
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.containers import FlextCliContainers
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
from flext_cli.processors import FlextCliProcessors
from flext_cli.prompts import FlextCliPrompts
from flext_cli.protocols import FlextCliProtocols
from flext_cli.tables import FlextCliTables
from flext_cli.typings import FlextCliTypes


class FlextCli(FlextService[FlextCliTypes.Data.CliDataDict]):
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
        self._click = FlextCliClick()
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
    def containers(self) -> type[FlextCliContainers]:
        """Access CLI containers.

        Returns:
            type[FlextCliContainers]: Containers class

        """
        return FlextCliContainers

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
    def click(self) -> FlextCliClick:
        """Access Click abstraction layer (ZERO TOLERANCE - ONLY Click file).

        Returns:
            FlextCliClick: Click abstraction instance

        Example:
            >>> cli = FlextCli()
            >>> cmd_result = cli.click.create_command_decorator(name="hello")

        """
        return self._click

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
        return self._formatters

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
        return self._tables

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
    def flext_processors(self) -> FlextProcessors:
        """Access FlextProcessors from flext-core for processing utilities.

        Returns:
            FlextProcessors: Core processing utilities

        """
        return FlextProcessors()

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

    # ==========================================================================
    # PHASE 3 CONVENIENCE API - Simple one-liner methods
    # ==========================================================================

    def success(self, message: str) -> None:
        """Print success message with green styling.

        Simple convenience method for common success output.

        Args:
            message: Success message to display

        Example:
            >>> cli = FlextCli()
            >>> cli.success("Operation completed successfully!")

        """
        self._formatters.print(f"[green]✓[/green] {message}")

    def error(self, message: str) -> None:
        """Print error message with red styling.

        Simple convenience method for common error output.

        Args:
            message: Error message to display

        Example:
            >>> cli = FlextCli()
            >>> cli.error("Operation failed!")

        """
        self._formatters.print(f"[red]✗[/red] {message}")

    def warning(self, message: str) -> None:
        """Print warning message with yellow styling.

        Simple convenience method for common warning output.

        Args:
            message: Warning message to display

        Example:
            >>> cli = FlextCli()
            >>> cli.warning("This action cannot be undone!")

        """
        self._formatters.print(f"[yellow]⚠[/yellow] {message}")

    def info(self, message: str) -> None:
        """Print info message with blue styling.

        Simple convenience method for common info output.

        Args:
            message: Info message to display

        Example:
            >>> cli = FlextCli()
            >>> cli.info("Processing data...")

        """
        self._formatters.print(f"[blue]i[/blue] {message}")

    def table(
        self, data: list[FlextTypes.Dict] | list[list], **_kwargs: object
    ) -> None:
        """Display data as a table with automatic formatting.

        Simple convenience method for quick table display.

        Args:
            data: Table data (list of dicts or list of lists)
            **kwargs: Additional table formatting options

        Example:
            >>> cli = FlextCli()
            >>> data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
            >>> cli.table(data)

        """
        # Extract headers if data is list of dicts
        if data and isinstance(data[0], dict):
            headers = list(data[0].keys())
            rows = [[str(row[h]) for h in headers] for row in data]
        else:
            headers = None
            rows = data

        # Use simple format for convenience API
        table_result = self._tables.create_simple_table(data=rows, headers=headers)

        if table_result.is_success:
            self._formatters.print(table_result.unwrap())

    def confirm(self, prompt: str, *, default: bool = False) -> bool:
        """Ask user for yes/no confirmation.

        Simple convenience method for quick confirmations.

        Args:
            prompt: Question to ask user
            default: Default value if user presses enter

        Returns:
            bool: True if user confirms, False otherwise

        Example:
            >>> cli = FlextCli()
            >>> if cli.confirm("Continue?"):
            ...     print("Continuing...")

        """
        result = self._click.confirm(text=prompt, default=default)
        return result.unwrap() if result.is_success else default

    def prompt_text(self, prompt: str, default: str = "") -> str:
        """Prompt user for text input.

        Simple convenience method for text input.

        Args:
            prompt: Prompt message
            default: Default value if user presses enter

        Returns:
            str: User input or default

        Example:
            >>> cli = FlextCli()
            >>> name = cli.prompt_text("Enter your name:")

        """
        result = self._click.prompt(text=prompt, default=default)
        return str(result.unwrap()) if result.is_success else default

    def display_data(self, data: FlextTypes.Dict, format_type: str = "table") -> None:
        """Display data in specified format.

        Convenience method for displaying structured data.

        Args:
            data: Data to display
            format_type: Format type ("table", "json", "yaml")

        Example:
            >>> cli = FlextCli()
            >>> cli.display_data({"name": "Alice", "age": 30})

        """
        if format_type == "table" and isinstance(data, dict):
            # Convert single dict to list of dicts for table display
            self.table([data])
        elif format_type == "json":
            self.info(json.dumps(data, indent=2))
        elif format_type == "yaml":
            if yaml is not None:
                self.info(yaml.dump(data, default_flow_style=False))
            else:
                self.info("YAML not available, displaying as JSON")
                self.info(json.dumps(data, indent=2))
        else:
            self.info(str(data))

    def display_message(self, message: str, message_type: str = "info") -> None:
        """Display message with specified type.

        Convenience method for displaying messages.

        Args:
            message: Message to display
            message_type: Message type ("info", "success", "warning", "error")

        Example:
            >>> cli = FlextCli()
            >>> cli.display_message("Operation completed", "success")

        """
        if message_type == "info":
            self.info(message)
        elif message_type == "success":
            self.success(message)
        elif message_type == "warning":
            self.warning(message)
        elif message_type == "error":
            self.error(message)
        else:
            self.info(message)

    def read_json(self, file_path: str) -> dict | list:
        """Read JSON file and return data.

        Simple convenience method for reading JSON.

        Args:
            file_path: Path to JSON file

        Returns:
            dict | list: JSON data

        Raises:
            RuntimeError: If file cannot be read

        Example:
            >>> cli = FlextCli()
            >>> config = cli.read_json("config.json")

        """
        result = self._file_tools.read_json_file(file_path)
        if result.is_failure:
            msg = f"Failed to read JSON: {result.error}"
            raise RuntimeError(msg)
        return result.unwrap()

    def write_json(
        self, data: FlextTypes.Dict, file_path: str, **_kwargs: object
    ) -> None:
        """Write data to JSON file.

        Simple convenience method for writing JSON.

        Args:
            data: Data to write
            file_path: Path to JSON file
            **_kwargs: Additional JSON write options (reserved for future use)

        Raises:
            RuntimeError: If file cannot be written

        Example:
            >>> cli = FlextCli()
            >>> cli.write_json({"key": "value"}, "output.json")

        """
        result = self._file_tools.write_json_file(file_path=file_path, data=data)
        if result.is_failure:
            msg = f"Failed to write JSON: {result.error}"
            raise RuntimeError(msg)

    def read_yaml(self, file_path: str) -> dict:
        """Read YAML file and return data.

        Simple convenience method for reading YAML.

        Args:
            file_path: Path to YAML file

        Returns:
            dict: YAML data

        Raises:
            RuntimeError: If file cannot be read

        Example:
            >>> cli = FlextCli()
            >>> config = cli.read_yaml("config.yaml")

        """
        result = self._file_tools.read_yaml_file(file_path)
        if result.is_failure:
            msg = f"Failed to read YAML: {result.error}"
            raise RuntimeError(msg)
        return result.unwrap()

    def write_yaml(self, data: dict, file_path: str) -> None:
        """Write data to YAML file.

        Simple convenience method for writing YAML.

        Args:
            data: Data to write
            file_path: Path to YAML file

        Raises:
            RuntimeError: If file cannot be written

        Example:
            >>> cli = FlextCli()
            >>> cli.write_yaml({"key": "value"}, "output.yaml")

        """
        result = self._file_tools.write_yaml_file(file_path, data)
        if result.is_failure:
            msg = f"Failed to write YAML: {result.error}"
            raise RuntimeError(msg)

    # Attribute declarations - override FlextService optional types
    # These are guaranteed initialized in __init__
    _logger: FlextLogger
    _container: FlextContainer
    _bus: FlextBus
    _context: FlextContext
    _dispatcher: FlextDispatcher

    def execute(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute CLI API operations.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: API execution result

        """
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok({
            "status": FlextCliConstants.OPERATIONAL,
            "service": FlextCliConstants.FLEXT_CLI,
            "version": "2.0.0",
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
                # Phase 1 transformation components
                "click": FlextCliConstants.AVAILABLE,
                "formatters": FlextCliConstants.AVAILABLE,
                "tables": FlextCliConstants.AVAILABLE,
                "main": FlextCliConstants.AVAILABLE,
            },
        })


__all__ = [
    "FlextCli",
]
