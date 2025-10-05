"""FLEXT-CLI Plugin System.

Unified plugin system architecture for flext-cli providing discovery,
loading, lifecycle management, and command registration through a single service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Protocol

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)


class FlextCliPluginSystem(FlextService[object]):
    """Unified plugin system for flext-cli.

    Provides plugin discovery, loading, initialization, lifecycle management,
    and command registration through a single service interface with nested helpers.
    Extends FlextService with full flext-core integration.

    Example:
        >>> from flext_cli.plugins import FlextCliPluginSystem
        >>>
        >>> plugin_system = FlextCliPluginSystem()
        >>>
        >>> # Discover plugins
        >>> discover_result = plugin_system.discover_plugins("./plugins")
        >>> if discover_result.is_success:
        ...     plugins = discover_result.unwrap()
        >>> # Load and initialize plugin
        >>> load_result = plugin_system.load_and_initialize_plugin(
        ...     "my_plugin", cli_main
        ... )
        >>> if load_result.is_success:
        ...     print("Plugin ready")

    """

    def __init__(self, **data: object) -> None:
        """Initialize unified plugin system.

        Args:
            **data: Additional service initialization data

        """
        super().__init__(**data)
        self._logger = FlextLogger(__name__)

        # Initialize nested plugin components
        self._manager = self._PluginManager()

    class PluginProtocol(Protocol):
        """Protocol defining the plugin interface.

        All plugins must implement this protocol to be discoverable
        and loadable by the plugin system.

        """

        name: str
        version: str

        def initialize(self, cli_main: object) -> FlextResult[None]:
            """Initialize the plugin.

            Args:
                cli_main: FlextCliMain instance

            Returns:
                FlextResult[None] indicating success or failure

            """
            ...

        def register_commands(self, cli_main: object) -> FlextResult[None]:
            """Register plugin commands.

            Args:
                cli_main: FlextCliMain instance for command registration

            Returns:
                FlextResult[None] indicating success or failure

            """
            ...

    class _PluginManager(FlextService[object]):
        """Plugin manager for flext-cli.

        Manages plugin discovery, loading, initialization, and lifecycle.

        """

        # Attribute declarations - override FlextService optional types
        _logger: FlextLogger
        _container: FlextContainer

        def __init__(self, **data: object) -> None:
            """Initialize plugin manager.

            Args:
                **data: Additional service data

            """
            super().__init__(**data)
            self._logger = FlextLogger(__name__)
            self._loaded_plugins: FlextTypes.Dict = {}
            self._initialized_plugins: FlextTypes.Dict = {}

        def discover_plugins(
            self,
            plugin_dir: str | Path,
        ) -> FlextResult[FlextTypes.StringList]:
            """Discover available plugins in a directory.

            Args:
                plugin_dir: Directory containing plugin modules

            Returns:
                FlextResult containing list of discovered plugin module names

            """
            try:
                plugin_path = Path(plugin_dir)

                if not plugin_path.exists():
                    return FlextResult[FlextTypes.StringList].fail(
                        f"Plugin directory does not exist: {plugin_dir}"
                    )

                if not plugin_path.is_dir():
                    return FlextResult[FlextTypes.StringList].fail(
                        f"Plugin path is not a directory: {plugin_dir}"
                    )

                # Find all Python files in plugin directory
                plugin_files = list(plugin_path.glob("*.py"))
                plugin_modules = [
                    f.stem
                    for f in plugin_files
                    if f.stem != "__init__" and not f.stem.startswith("_")
                ]

                self._logger.info(
                    "Discovered plugins",
                    extra={
                        "plugin_count": len(plugin_modules),
                        "plugin_dir": str(plugin_dir),
                    },
                )

                return FlextResult[FlextTypes.StringList].ok(plugin_modules)

            except Exception as e:
                error_msg = f"Failed to discover plugins: {e}"
                self._logger.exception(error_msg)
                return FlextResult[FlextTypes.StringList].fail(error_msg)

        def load_plugin(
            self,
            plugin_module: str,
            plugin_class_name: str | None = None,
        ) -> FlextResult[object]:
            """Load a plugin from a module.

            Args:
                plugin_module: Python module containing the plugin
                plugin_class_name: Name of plugin class (auto-detected if None)

            Returns:
                FlextResult containing loaded plugin instance

            """
            try:
                # Check if already loaded
                if plugin_module in self._loaded_plugins:
                    self._logger.debug(
                        "Plugin already loaded", extra={"plugin_module": plugin_module}
                    )
                    return FlextResult[object].ok(self._loaded_plugins[plugin_module])

                # Import plugin module
                module = importlib.import_module(plugin_module)

                # Find plugin class
                if plugin_class_name:
                    if not hasattr(module, plugin_class_name):
                        return FlextResult[object].fail(
                            f"Plugin class '{plugin_class_name}' not found in module"
                        )
                    plugin_class = getattr(module, plugin_class_name)
                else:
                    # Auto-detect plugin class (look for class implementing plugin protocol)
                    plugin_class = None
                    for _name, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            hasattr(obj, "name")
                            and hasattr(obj, "version")
                            and hasattr(obj, "initialize")
                            and hasattr(obj, "register_commands")
                        ):
                            plugin_class = obj
                            break

                    if plugin_class is None:
                        return FlextResult[object].fail(
                            f"No plugin class found in module '{plugin_module}'"
                        )

                # Instantiate plugin
                plugin_instance = plugin_class()

                # Store loaded plugin
                self._loaded_plugins[plugin_module] = plugin_instance

                self._logger.info(
                    "Loaded plugin",
                    extra={
                        "plugin_module": plugin_module,
                        "plugin_name": plugin_instance.name,
                    },
                )

                return FlextResult[object].ok(plugin_instance)

            except Exception as e:
                error_msg = f"Failed to load plugin '{plugin_module}': {e}"
                self._logger.exception(error_msg)
                return FlextResult[object].fail(error_msg)

        def initialize_plugin(
            self,
            plugin: FlextCliPluginSystem.PluginProtocol,
            cli_main: object,
        ) -> FlextResult[None]:
            """Initialize a loaded plugin.

            Args:
                plugin: Plugin instance
                cli_main: FlextCliMain instance

            Returns:
                FlextResult[None] indicating success or failure

            """
            try:
                plugin_name = getattr(plugin, "name", "unknown")

                # Check if already initialized
                if plugin_name in self._initialized_plugins:
                    self._logger.debug(
                        "Plugin already initialized", extra={"plugin_name": plugin_name}
                    )
                    return FlextResult[None].ok(None)

                # Initialize plugin
                init_result = plugin.initialize(cli_main)
                if init_result.is_failure:
                    return FlextResult[None].fail(
                        f"Plugin initialization failed: {init_result.error}"
                    )

                # Register commands
                register_result = plugin.register_commands(cli_main)
                if register_result.is_failure:
                    return FlextResult[None].fail(
                        f"Plugin command registration failed: {register_result.error}"
                    )

                # Mark as initialized
                self._initialized_plugins[plugin_name] = plugin

                self._logger.info(
                    "Initialized plugin", extra={"plugin_name": plugin_name}
                )

                return FlextResult[None].ok(None)

            except Exception as e:
                error_msg = f"Failed to initialize plugin: {e}"
                self._logger.exception(error_msg)
                return FlextResult[None].fail(error_msg)

        def load_and_initialize_plugin(
            self,
            plugin_module: str,
            cli_main: object,
            plugin_class_name: str | None = None,
        ) -> FlextResult[object]:
            """Load and initialize a plugin in one step.

            Args:
                plugin_module: Python module containing the plugin
                cli_main: FlextCliMain instance
                plugin_class_name: Name of plugin class (auto-detected if None)

            Returns:
                FlextResult containing initialized plugin instance

            """
            try:
                # Load plugin
                load_result = self.load_plugin(plugin_module, plugin_class_name)
                if load_result.is_failure:
                    return FlextResult[object].fail(f"Load failed: {load_result.error}")

                plugin: FlextCliPluginSystem.PluginProtocol = load_result.unwrap()

                # Initialize plugin
                init_result = self.initialize_plugin(plugin, cli_main)
                if init_result.is_failure:
                    return FlextResult[object].fail(
                        f"Initialize failed: {init_result.error}"
                    )

                self._logger.info(
                    "Loaded and initialized plugin",
                    extra={"plugin_module": plugin_module, "plugin_name": plugin.name},
                )

                return FlextResult[object].ok(plugin)

            except Exception as e:
                error_msg = f"Failed to load and initialize plugin: {e}"
                self._logger.exception(error_msg)
                return FlextResult[object].fail(error_msg)

        def get_loaded_plugins(self) -> FlextResult[FlextTypes.Dict]:
            """Get all loaded plugins.

            Returns:
                FlextResult containing dict of loaded plugins (module_name -> plugin)

            """
            try:
                return FlextResult[FlextTypes.Dict].ok(self._loaded_plugins.copy())
            except Exception as e:
                error_msg = f"Failed to get loaded plugins: {e}"
                self._logger.exception(error_msg)
                return FlextResult[FlextTypes.Dict].fail(error_msg)

        def get_initialized_plugins(self) -> FlextResult[FlextTypes.Dict]:
            """Get all initialized plugins.

            Returns:
                FlextResult containing dict of initialized plugins (name -> plugin)

            """
            try:
                return FlextResult[FlextTypes.Dict].ok(self._initialized_plugins.copy())
            except Exception as e:
                error_msg = f"Failed to get initialized plugins: {e}"
                self._logger.exception(error_msg)
                return FlextResult[FlextTypes.Dict].fail(error_msg)

        def unload_plugin(self, plugin_name: str) -> FlextResult[None]:
            """Unload a plugin.

            Args:
                plugin_name: Name of plugin to unload

            Returns:
                FlextResult[None] indicating success or failure

            """
            try:
                # Remove from initialized
                if plugin_name in self._initialized_plugins:
                    del self._initialized_plugins[plugin_name]

                # Find and remove from loaded
                module_to_remove = None
                for module_name, plugin in self._loaded_plugins.items():
                    if getattr(plugin, "name", None) == plugin_name:
                        module_to_remove = module_name
                        break

                if module_to_remove:
                    del self._loaded_plugins[module_to_remove]

                self._logger.info("Unloaded plugin", extra={"plugin_name": plugin_name})

                return FlextResult[None].ok(None)

            except Exception as e:
                error_msg = f"Failed to unload plugin: {e}"
                self._logger.exception(error_msg)
                return FlextResult[None].fail(error_msg)

        def execute(self) -> FlextResult[object]:
            """Execute plugin manager operations.

            Returns:
                FlextResult[None]

            """
            return FlextResult[None].ok(None)

    # ==========================================================================
    # PUBLIC PROPERTIES - Access to nested plugin components
    # ==========================================================================

    @property
    def plugin_protocol(self) -> type[PluginProtocol]:
        """Access plugin protocol definition.

        Returns:
            type[PluginProtocol]: Plugin protocol class

        """
        return self.PluginProtocol

    @property
    def manager(self) -> _PluginManager:
        """Access plugin manager functionality.

        Returns:
            _PluginManager: Plugin manager instance

        """
        return self._manager

    # ==========================================================================
    # CONVENIENCE METHODS - Delegate to manager for easy access
    # ==========================================================================

    def discover_plugins(
        self,
        plugin_dir: str | Path,
    ) -> FlextResult[FlextTypes.StringList]:
        """Discover available plugins in a directory.

        Args:
            plugin_dir: Directory containing plugin modules

        Returns:
            FlextResult containing list of discovered plugin module names

        """
        return self._manager.discover_plugins(plugin_dir)

    def load_plugin(
        self,
        plugin_module: str,
        plugin_class_name: str | None = None,
    ) -> FlextResult[object]:
        """Load a plugin from a module.

        Args:
            plugin_module: Python module containing the plugin
            plugin_class_name: Name of plugin class (auto-detected if None)

        Returns:
            FlextResult containing loaded plugin instance

        """
        return self._manager.load_plugin(plugin_module, plugin_class_name)

    def initialize_plugin(
        self,
        plugin: PluginProtocol,
        cli_main: object,
    ) -> FlextResult[None]:
        """Initialize a loaded plugin.

        Args:
            plugin: Plugin instance
            cli_main: FlextCliMain instance

        Returns:
            FlextResult[None] indicating success or failure

        """
        return self._manager.initialize_plugin(plugin, cli_main)

    def load_and_initialize_plugin(
        self,
        plugin_module: str,
        cli_main: object,
        plugin_class_name: str | None = None,
    ) -> FlextResult[object]:
        """Load and initialize a plugin in one step.

        Args:
            plugin_module: Python module containing the plugin
            cli_main: FlextCliMain instance
            plugin_class_name: Name of plugin class (auto-detected if None)

        Returns:
            FlextResult containing initialized plugin instance

        """
        return self._manager.load_and_initialize_plugin(
            plugin_module, cli_main, plugin_class_name
        )

    def get_loaded_plugins(self) -> FlextResult[FlextTypes.Dict]:
        """Get all loaded plugins.

        Returns:
            FlextResult containing dict of loaded plugins (module_name -> plugin)

        """
        return self._manager.get_loaded_plugins()

    def get_initialized_plugins(self) -> FlextResult[FlextTypes.Dict]:
        """Get all initialized plugins.

        Returns:
            FlextResult containing dict of initialized plugins (name -> plugin)

        """
        return self._manager.get_initialized_plugins()

    def unload_plugin(self, plugin_name: str) -> FlextResult[None]:
        """Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            FlextResult[None] indicating success or failure

        """
        return self._manager.unload_plugin(plugin_name)

    def execute(self) -> FlextResult[object]:
        """Execute plugin system operations.

        Returns:
            FlextResult[None]

        """
        return FlextResult[None].ok(None)


# ==========================================================================
# BACKWARD COMPATIBILITY ALIASES
# ==========================================================================


class FlextCliPlugin:
    """Concrete base class for FLEXT CLI plugins.

    All plugins must inherit from this class and implement the required methods.
    """

    def __init__(self, **data: object) -> None:
        """Initialize plugin."""
        self._logger = FlextLogger(__name__)
        # Store any additional data for extensibility
        for key, value in data.items():
            setattr(self, f"_{key}", value)

    @property
    def name(self) -> str:
        """Plugin name."""
        return getattr(self, "_name", self.__class__.__name__)

    @property
    def version(self) -> str:
        """Plugin version."""
        return getattr(self, "_version", "1.0.0")

    def initialize(
        self,
        cli_main: object,
    ) -> FlextResult[None]:  # pragma: no cover
        """Initialize the plugin.

        Args:
            cli_main: FlextCliMain instance

        Returns:
            FlextResult[None] indicating success or failure

        """
        return FlextResult[None].ok(None)

    def register_commands(
        self,
        cli_main: object,
    ) -> FlextResult[None]:  # pragma: no cover
        """Register plugin commands.

        Args:
            cli_main: FlextCliMain instance for command registration

        Returns:
            FlextResult[None] indicating success or failure

        """
        return FlextResult[None].ok(None)


# Type alias for backward compatibility
FlextCliPluginProtocol = FlextCliPluginSystem.PluginProtocol
FlextCliPluginManager = FlextCliPluginSystem._PluginManager


__all__ = [
    "FlextCliPlugin",
    "FlextCliPluginManager",
    "FlextCliPluginProtocol",
    "FlextCliPluginSystem",
]
