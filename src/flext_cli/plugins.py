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

from flext_core import FlextCore

from flext_cli.constants import FlextCliConstants
from flext_cli.protocols import FlextCliProtocols


class FlextCliPlugins(FlextCore.Service[object]):
    """Unified plugin system for flext-cli.

    Provides plugin discovery, loading, initialization, lifecycle management,
    and command registration through a single service interface with nested helpers.
    Extends FlextCore.Service with full flext-core integration.

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
        # Logger and container inherited from FlextCore.Service via FlextCore.Mixins

        # Initialize nested plugin components
        self._manager = self.PluginManager()

    class PluginManager(FlextCore.Service[object]):
        """Plugin manager for flext-cli.

        Manages plugin discovery, loading, initialization, and lifecycle.

        """

        def __init__(self, **data: object) -> None:
            """Initialize plugin manager.

            Args:
                **data: Additional service data

            """
            super().__init__(**data)
            # Logger and container inherited from FlextCore.Service via FlextCore.Mixins
            self._loaded_plugins: FlextCore.Types.Dict = {}
            self._initialized_plugins: FlextCore.Types.Dict = {}

        def discover_plugins(
            self,
            plugin_dir: str | Path,
        ) -> FlextCore.Result[FlextCore.Types.StringList]:
            """Discover available plugins in a directory.

            Args:
                plugin_dir: Directory containing plugin modules

            Returns:
                FlextCore.Result containing list of discovered plugin module names

            """
            try:
                plugin_path = Path(plugin_dir)

                if not plugin_path.exists():
                    return FlextCore.Result[FlextCore.Types.StringList].fail(
                        FlextCliConstants.ErrorMessages.PLUGIN_DIR_NOT_EXIST.format(
                            dir=plugin_dir
                        )
                    )

                if not plugin_path.is_dir():
                    return FlextCore.Result[FlextCore.Types.StringList].fail(
                        FlextCliConstants.ErrorMessages.PLUGIN_PATH_NOT_DIR.format(
                            path=plugin_dir
                        )
                    )

                # Find all Python files in plugin directory
                plugin_files = list(plugin_path.glob("*.py"))
                plugin_modules = [
                    f.stem
                    for f in plugin_files
                    if f.stem != "__init__" and not f.stem.startswith("_")
                ]

                self.logger.info(
                    "Discovered plugins",
                    extra={
                        "plugin_count": len(plugin_modules),
                        "plugin_dir": str(plugin_dir),
                    },
                )

                return FlextCore.Result[FlextCore.Types.StringList].ok(plugin_modules)

            except Exception as e:
                error_msg = (
                    FlextCliConstants.ErrorMessages.FAILED_DISCOVER_PLUGINS.format(
                        error=e
                    )
                )
                self.logger.exception(error_msg)
                return FlextCore.Result[FlextCore.Types.StringList].fail(error_msg)

        def load_plugin(
            self,
            plugin_module: str,
            plugin_class_name: str | None = None,
        ) -> FlextCore.Result[object]:
            """Load a plugin from a module.

            Args:
                plugin_module: Python module containing the plugin
                plugin_class_name: Name of plugin class (auto-detected if None)

            Returns:
                FlextCore.Result containing loaded plugin instance

            """
            try:
                # Check if already loaded
                if plugin_module in self._loaded_plugins:
                    self.logger.debug(
                        "Plugin already loaded", extra={"plugin_module": plugin_module}
                    )
                    return FlextCore.Result[object].ok(
                        self._loaded_plugins[plugin_module]
                    )

                # Import plugin module
                module = importlib.import_module(plugin_module)

                # Find plugin class
                if plugin_class_name:
                    if not hasattr(module, plugin_class_name):
                        return FlextCore.Result[object].fail(
                            FlextCliConstants.ErrorMessages.PLUGIN_CLASS_NOT_FOUND.format(
                                class_name=plugin_class_name
                            )
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
                        return FlextCore.Result[object].fail(
                            FlextCliConstants.ErrorMessages.NO_PLUGIN_CLASS_FOUND.format(
                                module=plugin_module
                            )
                        )

                # Instantiate plugin
                plugin_instance = plugin_class()

                # Store loaded plugin
                self._loaded_plugins[plugin_module] = plugin_instance

                self.logger.info(
                    "Loaded plugin",
                    extra={
                        "plugin_module": plugin_module,
                        "plugin_name": plugin_instance.name,
                    },
                )

                return FlextCore.Result[object].ok(plugin_instance)

            except Exception as e:
                error_msg = FlextCliConstants.ErrorMessages.FAILED_LOAD_PLUGIN.format(
                    module=plugin_module, error=e
                )
                self.logger.exception(error_msg)
                return FlextCore.Result[object].fail(error_msg)

        def initialize_plugin(
            self,
            plugin: FlextCliProtocols.Extensions.CliPlugin,
            cli_main: object,
        ) -> FlextCore.Result[None]:
            """Initialize a loaded plugin.

            Args:
                plugin: Plugin instance
                cli_main: FlextCliMain instance

            Returns:
                FlextCore.Result[None] indicating success or failure

            """
            try:
                plugin_name = getattr(plugin, "name", "unknown")

                # Check if already initialized
                if plugin_name in self._initialized_plugins:
                    self.logger.debug(
                        "Plugin already initialized", extra={"plugin_name": plugin_name}
                    )
                    return FlextCore.Result[None].ok(None)

                # Initialize plugin
                init_result = plugin.initialize(cli_main)
                if init_result.is_failure:
                    return FlextCore.Result[None].fail(
                        FlextCliConstants.ErrorMessages.PLUGIN_INIT_FAILED.format(
                            error=init_result.error
                        )
                    )

                # Register commands
                register_result = plugin.register_commands(cli_main)
                if register_result.is_failure:
                    return FlextCore.Result[None].fail(
                        FlextCliConstants.ErrorMessages.PLUGIN_REGISTER_FAILED.format(
                            error=register_result.error
                        )
                    )

                # Mark as initialized
                self._initialized_plugins[plugin_name] = plugin

                self.logger.info(
                    "Initialized plugin", extra={"plugin_name": plugin_name}
                )

                return FlextCore.Result[None].ok(None)

            except Exception as e:
                error_msg = (
                    FlextCliConstants.ErrorMessages.FAILED_INITIALIZE_PLUGIN.format(
                        error=e
                    )
                )
                self.logger.exception(error_msg)
                return FlextCore.Result[None].fail(error_msg)

        def load_and_initialize_plugin(
            self,
            plugin_module: str,
            cli_main: object,
            plugin_class_name: str | None = None,
        ) -> FlextCore.Result[object]:
            """Load and initialize a plugin in one step.

            Args:
                plugin_module: Python module containing the plugin
                cli_main: FlextCliMain instance
                plugin_class_name: Name of plugin class (auto-detected if None)

            Returns:
                FlextCore.Result containing initialized plugin instance

            """
            try:
                # Load plugin
                load_result = self.load_plugin(plugin_module, plugin_class_name)
                if load_result.is_failure:
                    return FlextCore.Result[object].fail(
                        FlextCliConstants.ErrorMessages.LOAD_FAILED.format(
                            error=load_result.error
                        )
                    )

                plugin: FlextCliProtocols.Extensions.CliPlugin = load_result.unwrap()

                # Initialize plugin
                init_result = self.initialize_plugin(plugin, cli_main)
                if init_result.is_failure:
                    return FlextCore.Result[object].fail(
                        FlextCliConstants.ErrorMessages.INITIALIZE_FAILED.format(
                            error=init_result.error
                        )
                    )

                self.logger.info(
                    "Loaded and initialized plugin",
                    extra={"plugin_module": plugin_module, "plugin_name": plugin.name},
                )

                return FlextCore.Result[object].ok(plugin)

            except Exception as e:
                error_msg = (
                    FlextCliConstants.ErrorMessages.FAILED_LOAD_AND_INIT_PLUGIN.format(
                        error=e
                    )
                )
                self.logger.exception(error_msg)
                return FlextCore.Result[object].fail(error_msg)

        def get_loaded_plugins(self) -> FlextCore.Result[FlextCore.Types.Dict]:
            """Get all loaded plugins.

            Returns:
                FlextCore.Result containing dict of loaded plugins (module_name -> plugin)

            """
            try:
                return FlextCore.Result[FlextCore.Types.Dict].ok(
                    self._loaded_plugins.copy()
                )
            except Exception as e:
                error_msg = (
                    FlextCliConstants.ErrorMessages.FAILED_GET_LOADED_PLUGINS.format(
                        error=e
                    )
                )
                self.logger.exception(error_msg)
                return FlextCore.Result[FlextCore.Types.Dict].fail(error_msg)

        def get_initialized_plugins(self) -> FlextCore.Result[FlextCore.Types.Dict]:
            """Get all initialized plugins.

            Returns:
                FlextCore.Result containing dict of initialized plugins (name -> plugin)

            """
            try:
                return FlextCore.Result[FlextCore.Types.Dict].ok(
                    self._initialized_plugins.copy()
                )
            except Exception as e:
                error_msg = (
                    FlextCliConstants.ErrorMessages.FAILED_GET_INIT_PLUGINS.format(
                        error=e
                    )
                )
                self.logger.exception(error_msg)
                return FlextCore.Result[FlextCore.Types.Dict].fail(error_msg)

        def unload_plugin(self, plugin_name: str) -> FlextCore.Result[None]:
            """Unload a plugin.

            Args:
                plugin_name: Name of plugin to unload

            Returns:
                FlextCore.Result[None] indicating success or failure

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

                self.logger.info("Unloaded plugin", extra={"plugin_name": plugin_name})

                return FlextCore.Result[None].ok(None)

            except Exception as e:
                error_msg = FlextCliConstants.ErrorMessages.FAILED_UNLOAD_PLUGIN.format(
                    error=e
                )
                self.logger.exception(error_msg)
                return FlextCore.Result[None].fail(error_msg)

        def execute(self) -> FlextCore.Result[None]:
            """Execute plugin manager operations.

            Returns:
                FlextCore.Result[None]

            """
            return FlextCore.Result[None].ok(None)

    # ==========================================================================
    # PUBLIC PROPERTIES - Access to nested plugin components
    # ==========================================================================

    @property
    def plugin_protocol(self) -> type[FlextCliProtocols.Extensions.CliPlugin]:
        """Access plugin protocol definition.

        Returns:
            type[FlextCliProtocols.Extensions.CliPlugin]: Plugin protocol class

        """
        return FlextCliProtocols.Extensions.CliPlugin

    @property
    def manager(self) -> PluginManager:
        """Access plugin manager functionality.

        Returns:
            PluginManager: Plugin manager instance

        """
        return self._manager

    # ==========================================================================
    # CONVENIENCE METHODS - Delegate to manager for easy access
    # ==========================================================================

    def discover_plugins(
        self,
        plugin_dir: str | Path,
    ) -> FlextCore.Result[FlextCore.Types.StringList]:
        """Discover available plugins in a directory.

        Args:
            plugin_dir: Directory containing plugin modules

        Returns:
            FlextCore.Result containing list of discovered plugin module names

        """
        return self._manager.discover_plugins(plugin_dir)

    def load_plugin(
        self,
        plugin_module: str,
        plugin_class_name: str | None = None,
    ) -> FlextCore.Result[object]:
        """Load a plugin from a module.

        Args:
            plugin_module: Python module containing the plugin
            plugin_class_name: Name of plugin class (auto-detected if None)

        Returns:
            FlextCore.Result containing loaded plugin instance

        """
        return self._manager.load_plugin(plugin_module, plugin_class_name)

    def initialize_plugin(
        self,
        plugin: FlextCliProtocols.Extensions.CliPlugin,
        cli_main: object,
    ) -> FlextCore.Result[None]:
        """Initialize a loaded plugin.

        Args:
            plugin: Plugin instance
            cli_main: FlextCliMain instance

        Returns:
            FlextCore.Result[None] indicating success or failure

        """
        return self._manager.initialize_plugin(plugin, cli_main)

    def load_and_initialize_plugin(
        self,
        plugin_module: str,
        cli_main: object,
        plugin_class_name: str | None = None,
    ) -> FlextCore.Result[object]:
        """Load and initialize a plugin in one step.

        Args:
            plugin_module: Python module containing the plugin
            cli_main: FlextCliMain instance
            plugin_class_name: Name of plugin class (auto-detected if None)

        Returns:
            FlextCore.Result containing initialized plugin instance

        """
        return self._manager.load_and_initialize_plugin(
            plugin_module, cli_main, plugin_class_name
        )

    def get_loaded_plugins(self) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Get all loaded plugins.

        Returns:
            FlextCore.Result containing dict of loaded plugins (module_name -> plugin)

        """
        return self._manager.get_loaded_plugins()

    def get_initialized_plugins(self) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Get all initialized plugins.

        Returns:
            FlextCore.Result containing dict of initialized plugins (name -> plugin)

        """
        return self._manager.get_initialized_plugins()

    def unload_plugin(self, plugin_name: str) -> FlextCore.Result[None]:
        """Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            FlextCore.Result[None] indicating success or failure

        """
        return self._manager.unload_plugin(plugin_name)

    class Plugin:
        """Concrete base class for FLEXT CLI plugins.

        All plugins must inherit from this class and implement the required methods.
        """

        def __init__(self, **data: object) -> None:
            """Initialize plugin."""
            self.logger = FlextCore.Logger(__name__)
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
            _cli_main: object,
        ) -> FlextCore.Result[None]:  # pragma: no cover
            """Initialize the plugin.

            Args:
                cli_main: FlextCliMain instance

            Returns:
                FlextCore.Result[None] indicating success or failure

            """
            return FlextCore.Result[None].ok(None)

        def register_commands(
            self,
            _cli_main: object,
        ) -> FlextCore.Result[None]:  # pragma: no cover
            """Register plugin commands.

            Args:
                cli_main: FlextCliMain instance for command registration

            Returns:
                FlextCore.Result[None] indicating success or failure

            """
            return FlextCore.Result[None].ok(None)

    def execute(self) -> FlextCore.Result[None]:
        """Execute plugin system operations.

        Returns:
            FlextCore.Result[None]

        """
        return FlextCore.Result[None].ok(None)


__all__ = [
    "FlextCliPlugins",
]
