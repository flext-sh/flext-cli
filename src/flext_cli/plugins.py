"""FLEXT-CLI Plugin System.

This module provides the plugin system architecture for flext-cli, enabling:
- Plugin discovery and loading
- Plugin registration and lifecycle management
- Plugin configuration
- Command plugin pattern

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Any, Protocol

from flext_core import FlextLogger, FlextResult, FlextService


class FlextCliPlugin(Protocol):
    """Protocol defining the plugin interface.

    All plugins must implement this protocol to be discoverable
    and loadable by the plugin system.

    Example:
        >>> class MyPlugin:
        ...     '''My custom plugin.'''
        ...
        ...     name = "my-plugin"
        ...     version = "1.0.0"
        ...
        ...     def initialize(self, cli_main):
        ...         '''Initialize plugin.'''
        ...         pass
        ...
        ...     def register_commands(self, cli_main):
        ...         '''Register commands.'''
        ...
        ...         @cli_main.command()
        ...         def my_command():
        ...             print("Hello from plugin!")

    """

    name: str
    version: str

    def initialize(self, cli_main: Any) -> FlextResult[None]:
        """Initialize the plugin.

        Args:
            cli_main: FlextCliMain instance

        Returns:
            FlextResult[None] indicating success or failure

        """
        ...

    def register_commands(self, cli_main: Any) -> FlextResult[None]:
        """Register plugin commands.

        Args:
            cli_main: FlextCliMain instance for command registration

        Returns:
            FlextResult[None] indicating success or failure

        """
        ...


class FlextCliPluginManager(FlextService[None]):
    """Plugin manager for flext-cli.

    Manages plugin discovery, loading, initialization, and lifecycle.

    Example:
        >>> from flext_cli import FlextCli
        >>> from flext_cli.plugins import FlextCliPluginManager
        >>>
        >>> cli = FlextCli()
        >>> plugin_manager = FlextCliPluginManager()
        >>>
        >>> # Discover plugins
        >>> discover_result = plugin_manager.discover_plugins("./plugins")
        >>> if discover_result.is_success:
        ...     plugins = discover_result.unwrap()
        ...     print(f"Found {len(plugins)} plugins")
        >>>
        >>> # Load and initialize plugin
        >>> load_result = plugin_manager.load_plugin("my_plugin")
        >>> if load_result.is_success:
        ...     plugin = load_result.unwrap()
        ...     init_result = plugin_manager.initialize_plugin(plugin, cli.main)

    """

    def __init__(self, **data: object) -> None:
        """Initialize plugin manager.

        Args:
            **data: Additional service data

        """
        super().__init__(**data)
        self._logger = FlextLogger(__name__)
        self._loaded_plugins: dict[str, Any] = {}
        self._initialized_plugins: dict[str, Any] = {}

    def discover_plugins(
        self,
        plugin_dir: str | Path,
    ) -> FlextResult[list[str]]:
        """Discover available plugins in a directory.

        Args:
            plugin_dir: Directory containing plugin modules

        Returns:
            FlextResult containing list of discovered plugin module names

        Example:
            >>> manager = FlextCliPluginManager()
            >>> result = manager.discover_plugins("./plugins")
            >>> if result.is_success:
            ...     for plugin_name in result.unwrap():
            ...         print(f"Found plugin: {plugin_name}")

        """
        try:
            plugin_path = Path(plugin_dir)

            if not plugin_path.exists():
                return FlextResult[list[str]].fail(
                    f"Plugin directory does not exist: {plugin_dir}"
                )

            if not plugin_path.is_dir():
                return FlextResult[list[str]].fail(
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

            return FlextResult[list[str]].ok(plugin_modules)

        except Exception as e:
            error_msg = f"Failed to discover plugins: {e}"
            self._logger.exception(error_msg)
            return FlextResult[list[str]].fail(error_msg)

    def load_plugin(
        self,
        plugin_module: str,
        plugin_class_name: str | None = None,
    ) -> FlextResult[Any]:
        """Load a plugin from a module.

        Args:
            plugin_module: Python module containing the plugin
            plugin_class_name: Name of plugin class (auto-detected if None)

        Returns:
            FlextResult containing loaded plugin instance

        Example:
            >>> manager = FlextCliPluginManager()
            >>> result = manager.load_plugin("my_plugin")
            >>> if result.is_success:
            ...     plugin = result.unwrap()
            ...     print(f"Loaded: {plugin.name} v{plugin.version}")

        """
        try:
            # Check if already loaded
            if plugin_module in self._loaded_plugins:
                self._logger.debug(
                    "Plugin already loaded", extra={"plugin_module": plugin_module}
                )
                return FlextResult[Any].ok(self._loaded_plugins[plugin_module])

            # Import plugin module
            module = importlib.import_module(plugin_module)

            # Find plugin class
            if plugin_class_name:
                if not hasattr(module, plugin_class_name):
                    return FlextResult[Any].fail(
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
                    return FlextResult[Any].fail(
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

            return FlextResult[Any].ok(plugin_instance)

        except Exception as e:
            error_msg = f"Failed to load plugin '{plugin_module}': {e}"
            self._logger.exception(error_msg)
            return FlextResult[Any].fail(error_msg)

    def initialize_plugin(
        self,
        plugin: Any,
        cli_main: Any,
    ) -> FlextResult[None]:
        """Initialize a loaded plugin.

        Args:
            plugin: Plugin instance
            cli_main: FlextCliMain instance

        Returns:
            FlextResult[None] indicating success or failure

        Example:
            >>> manager = FlextCliPluginManager()
            >>> load_result = manager.load_plugin("my_plugin")
            >>> if load_result.is_success:
            ...     plugin = load_result.unwrap()
            ...     init_result = manager.initialize_plugin(plugin, cli.main)
            ...     if init_result.is_success:
            ...         print("Plugin initialized")

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

            self._logger.info("Initialized plugin", extra={"plugin_name": plugin_name})

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to initialize plugin: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def load_and_initialize_plugin(
        self,
        plugin_module: str,
        cli_main: Any,
        plugin_class_name: str | None = None,
    ) -> FlextResult[Any]:
        """Load and initialize a plugin in one step.

        Args:
            plugin_module: Python module containing the plugin
            cli_main: FlextCliMain instance
            plugin_class_name: Name of plugin class (auto-detected if None)

        Returns:
            FlextResult containing initialized plugin instance

        Example:
            >>> manager = FlextCliPluginManager()
            >>> result = manager.load_and_initialize_plugin("my_plugin", cli.main)
            >>> if result.is_success:
            ...     print("Plugin loaded and initialized")

        """
        try:
            # Load plugin
            load_result = self.load_plugin(plugin_module, plugin_class_name)
            if load_result.is_failure:
                return FlextResult[Any].fail(f"Load failed: {load_result.error}")

            plugin = load_result.unwrap()

            # Initialize plugin
            init_result = self.initialize_plugin(plugin, cli_main)
            if init_result.is_failure:
                return FlextResult[Any].fail(f"Initialize failed: {init_result.error}")

            self._logger.info(
                "Loaded and initialized plugin",
                extra={"plugin_module": plugin_module, "plugin_name": plugin.name},
            )

            return FlextResult[Any].ok(plugin)

        except Exception as e:
            error_msg = f"Failed to load and initialize plugin: {e}"
            self._logger.exception(error_msg)
            return FlextResult[Any].fail(error_msg)

    def get_loaded_plugins(self) -> FlextResult[dict[str, Any]]:
        """Get all loaded plugins.

        Returns:
            FlextResult containing dict of loaded plugins (module_name -> plugin)

        Example:
            >>> manager = FlextCliPluginManager()
            >>> result = manager.get_loaded_plugins()
            >>> if result.is_success:
            ...     for name, plugin in result.unwrap().items():
            ...         print(f"{name}: {plugin.version}")

        """
        try:
            return FlextResult[dict[str, Any]].ok(self._loaded_plugins.copy())
        except Exception as e:
            error_msg = f"Failed to get loaded plugins: {e}"
            self._logger.exception(error_msg)
            return FlextResult[dict[str, Any]].fail(error_msg)

    def get_initialized_plugins(self) -> FlextResult[dict[str, Any]]:
        """Get all initialized plugins.

        Returns:
            FlextResult containing dict of initialized plugins (name -> plugin)

        Example:
            >>> manager = FlextCliPluginManager()
            >>> result = manager.get_initialized_plugins()
            >>> if result.is_success:
            ...     print(f"Active plugins: {len(result.unwrap())}")

        """
        try:
            return FlextResult[dict[str, Any]].ok(self._initialized_plugins.copy())
        except Exception as e:
            error_msg = f"Failed to get initialized plugins: {e}"
            self._logger.exception(error_msg)
            return FlextResult[dict[str, Any]].fail(error_msg)

    def unload_plugin(self, plugin_name: str) -> FlextResult[None]:
        """Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            FlextResult[None] indicating success or failure

        Example:
            >>> manager = FlextCliPluginManager()
            >>> result = manager.unload_plugin("my-plugin")
            >>> if result.is_success:
            ...     print("Plugin unloaded")

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

    def execute(self) -> FlextResult[None]:
        """Execute plugin manager operations.

        Returns:
            FlextResult[None]

        """
        return FlextResult[None].ok(None)


__all__ = [
    "FlextCliPlugin",
    "FlextCliPluginManager",
]
