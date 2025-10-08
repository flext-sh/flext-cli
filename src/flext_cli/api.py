"""FLEXT CLI API - Direct flext-core integration without over-abstraction.

Main public API for the FLEXT CLI ecosystem. Provides essential CLI functionality
by directly extending FlextService and using Rich/Click appropriately.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

from flext_core import FlextCore, FlextResult
from flext_core.base import FlextBase

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
from flext_cli.main import FlextCliMain
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import FlextCliModels
from flext_cli.output import FlextCliOutput
from flext_cli.plugins import FlextCliPlugins
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
            FlextCli: Singleton instance from FlextCore.Container

        Example:
            >>> cli = FlextCli.get_instance()
            >>> # Same instance every time - no repetitive initialization

        """
        container = FlextCore.Container.get_global()
        result = container.get("flext_cli")

        # If not registered yet, create and register
        if result.is_failure or result.value is None:
            return cls()

        # Type assertion: container.get returns FlextCli instance
        return cast("FlextCli", result.value)

    def __init__(self) -> None:
        """Initialize CLI API with minimal setup - services lazy-loaded on demand."""
        # Initialize logger first
        # Logger is automatically provided by FlextMixins.Logging mixin

        # Get global container for DI
        self._container = FlextCore.Container.get_global()

        # Register this instance as singleton in container for DI
        self._container.register("flext_cli", self)

        # Phase 1 Enhancement: Enrich context with service metadata
        FlextCore.Context.Service.set_service_name("flext-cli")
        FlextCore.Context.Service.set_service_version("1.0.0")

        # Enrich logger with correlation tracking
        correlation_id = FlextCore.Context.Correlation.generate_correlation_id()
        self._logger = FlextCore.Logger(__name__)
        self._logger.bind_global_context(
            service_name="flext-cli",
            service_type="FlextCli",
            correlation_id=correlation_id,
        )

    @property
    def logger(self) -> FlextCore.Logger:
        """Get logger instance."""
        if not hasattr(self, "_logger"):
            self._logger = FlextCore.Logger(__name__)
        return self._logger

    # ==========================================================================
    # THIN FACADE PROPERTIES - Direct access to all domain services
    # ==========================================================================

    @property
    def core(self) -> FlextCliCore:
        """Access core CLI service for command management.

        Returns:
            FlextCliCore: Core CLI service instance

        """
        return self._container.get_or_create("core", FlextCliCore).unwrap()

    @property
    def cmd(self) -> FlextCliCmd:
        """Access CLI command service for configuration management.

        Returns:
            FlextCliCmd: Command service instance

        """
        return self._container.get_or_create("cmd", FlextCliCmd).unwrap()

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

    # ==========================================================================
    # CONFIGURATION MANAGEMENT - Unified config access for CLI, Core, and Tools
    # ==========================================================================

    @property
    def config(self) -> FlextCliConfig:
        """Access CLI configuration singleton.

        Returns:
            FlextCliConfig: Singleton CLI config instance

        Example:
            >>> cli = FlextCli.get_instance()
            >>> cli.config.profile
            'default'
            >>> cli.config.output_format
            'table'

        """
        # Use singleton pattern from FlextCore.Config
        config = FlextCliConfig.get_global_instance()
        config.__class__ = FlextCliConfig
        return config

    @property
    def core_config(self) -> FlextCore.Config:
        """Access flext-core configuration singleton.

        Allows flext-cli to read and modify flext-core configuration.

        Returns:
            FlextCore.Config: Core configuration instance

        Example:
            >>> cli = FlextCli.get_instance()
            >>> cli.core_config.debug
            False

        """
        return FlextCore.Config.get_global_instance()

    def configure_cli(
        self,
        profile: str | None = None,
        output_format: str | None = None,
        *,
        verbose: bool | None = None,
        debug: bool | None = None,
        **kwargs: object,
    ) -> FlextResult[None]:
        """Configure CLI settings dynamically.

        Args:
            profile: CLI profile to use
            output_format: Output format (json, yaml, table, etc.)
            verbose: Enable verbose output
            debug: Enable debug mode
            **kwargs: Additional CLI configuration options

        Returns:
            FlextResult[None]: Success or error

        Example:
            >>> cli = FlextCli.get_instance()
            >>> result = cli.configure_cli(
            ...     profile="production", output_format="json", debug=False
            ... )
            >>> result.is_success
            True

        """
        try:
            config_dict: FlextCore.Types.Dict = {}
            if profile is not None:
                config_dict["profile"] = profile
            if output_format is not None:
                config_dict["output_format"] = output_format
            if verbose is not None:
                config_dict["verbose"] = verbose
            if debug is not None:
                config_dict["debug"] = debug

            # Add additional kwargs
            config_dict.update(kwargs)

            # Apply to CLI config
            for key, value in config_dict.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.CLI_CONFIG_FAILED.format(error=e)
            )

    def configure_core(self, **config: object) -> FlextResult[None]:
        """Configure flext-core settings.

        Allows flext-cli to modify flext-core configuration for the application.

        Args:
            **config: Core configuration options (environment, debug, etc.)

        Returns:
            FlextResult[None]: Success or error

        Example:
            >>> cli = FlextCli.get_instance()
            >>> result = cli.configure_core(environment="production", debug=False)

        """
        config_dict = dict(config)
        return self.core_config.configure(config_dict)

    def get_component_config(self, component: str) -> FlextResult[FlextCore.Types.Dict]:
        """Get component-specific configuration.

        Supports namespaced configuration for tools using flext-cli.

        Args:
            component: Component name (e.g., "myapp", "database", "api")

        Returns:
            FlextResult[FlextCore.Types.Dict]: Component configuration or error

        Example:
            >>> cli = FlextCli.get_instance()
            >>> # Get config for a tool using flext-cli
            >>> result = cli.get_component_config("myapp")
            >>> if result.is_success:
            ...     myapp_config = result.unwrap()

        """
        return self.core_config.get_component_config(component)

    def configure_component(
        self, component: str, **config: object
    ) -> FlextResult[None]:
        """Configure a specific component.

        Allows tools using flext-cli to have their own namespaced configuration.

        Args:
            component: Component name
            **config: Component configuration options

        Returns:
            FlextResult[None]: Success or error

        Example:
            >>> cli = FlextCli.get_instance()
            >>> # Configure a tool using flext-cli
            >>> result = cli.configure_component(
            ...     "myapp",
            ...     database_url="postgresql://localhost/mydb",
            ...     api_key="secret",
            ... )

        """
        try:
            # Get current component config
            result = self.get_component_config(component)
            if result.is_failure:
                # Component config doesn't exist, create it
                component_config: FlextCore.Types.Dict = {}
            else:
                component_config = result.unwrap()

            # Update with new config
            component_config.update(config)

            # Save back to core config
            core_config_dict: FlextCore.Types.Dict = {component: component_config}
            return self.core_config.configure(core_config_dict)

        except Exception as e:
            return FlextResult[None].fail(
                f"Component configuration failed for {component}: {e}"
            )

    # ==========================================================================
    # DOMAIN SERVICES - Direct access to CLI functionality
    # ==========================================================================

    @property
    def output(self) -> FlextCliOutput:
        """Access CLI output formatting service.

        Returns:
            FlextCliOutput: Output service instance

        """
        return self._container.get_or_create("output", FlextCliOutput).unwrap()

    @property
    def file_tools(self) -> FlextCliFileTools:
        """Access CLI file operations service.

        Returns:
            FlextCliFileTools: File tools instance

        """
        return self._container.get_or_create("file_tools", FlextCliFileTools).unwrap()

    @property
    def utilities(self) -> type[FlextCore.Utilities]:
        """Access utility functions from flext-core.

        Returns:
            type[FlextCore.Utilities]: Utilities class from flext-core

        """
        return FlextCore.Utilities

    @property
    def auth(self) -> FlextCliAuth:
        """Access CLI authentication service.

        Returns:
            FlextCliAuth: Auth service instance

        """
        return self._container.get_or_create("auth", FlextCliAuth).unwrap()

    @property
    def commands(self) -> FlextCliCommands:
        """Access CLI commands registry.

        Returns:
            FlextCliCommands: Commands instance

        """
        return self._container.get_or_create("commands", FlextCliCommands).unwrap()

    @property
    def context(self) -> FlextCliContext:
        """Access CLI context service.

        Returns:
            FlextCliContext: Context service instance

        """
        return self._container.get_or_create("context", FlextCliContext).unwrap()

    @property
    def debug(self) -> FlextCliDebug:
        """Access CLI debug service.

        Returns:
            FlextCliDebug: Debug service instance

        """
        return self._container.get_or_create("debug", FlextCliDebug).unwrap()

    @property
    def exceptions(self) -> type[FlextCliExceptions]:
        """Access CLI exceptions.

        Returns:
            type[FlextCliExceptions]: Exceptions class

        """
        return FlextCliExceptions

    @property
    def mixins(self) -> type[FlextCliMixins]:
        """Access CLI mixins.

        Returns:
            type[FlextCliMixins]: Mixins class

        """
        return FlextCliMixins

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
        return self._container.get_or_create("plugins", FlextCliPlugins).unwrap()

    @property
    def prompts(self) -> FlextCliPrompts:
        """Access CLI prompts.

        Returns:
            FlextCliPrompts: Prompts instance

        """
        return self._container.get_or_create("prompts", FlextCliPrompts).unwrap()

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
        return self._container.get_or_create("click", FlextCliCli).unwrap()

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
        return self._container.get_or_create("formatters", FlextCliFormatters).unwrap()

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
        return self._container.get_or_create("tables", FlextCliTables).unwrap()

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
        return self._container.get_or_create("main", FlextCliMain).unwrap()

    # ==========================================================================
    # FLEXT-CORE ADVANCED FEATURES - Event bus, registry, CQRS, etc.
    # ==========================================================================

    @property
    def bus(self) -> FlextCore.Bus:
        """Access FlextCore.Bus for event-driven architecture.

        Returns:
            FlextCore.Bus: Event bus instance for message routing

        """
        return self._container.get_or_create("bus", FlextCore.Bus).unwrap()

    @property
    def registry(self) -> FlextCore.Registry:
        """Access FlextCore.Registry for service discovery.

        Returns:
            FlextCore.Registry: Service registry instance

        """
        # Registry needs dispatcher - use lambda for dependency
        return self._container.get_or_create(
            "registry", lambda: FlextCore.Registry(dispatcher=self.dispatcher)
        ).unwrap()

    @property
    def dispatcher(self) -> FlextCore.Dispatcher:
        """Access FlextCore.Dispatcher for message dispatching.

        Returns:
            FlextCore.Dispatcher: Message dispatcher instance

        """
        return self._container.get_or_create(
            "dispatcher", FlextCore.Dispatcher
        ).unwrap()

    @property
    def container(self) -> FlextBase.Container:
        """Access FlextCore.Container for dependency injection.

        Returns:
            FlextBase.Container: DI container instance

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
            "timestamp": FlextCore.Utilities.Generators.generate_timestamp(),
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
