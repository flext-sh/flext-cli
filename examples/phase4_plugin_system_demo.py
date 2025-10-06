"""FLEXT-CLI Phase 4 Plugin System Demo.

This example demonstrates Phase 4 plugin system:
- Plugin discovery and loading
- Plugin initialization
- Plugin command registration
- Plugin lifecycle management

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path

from flext_cli import (
    FlextCli,
    FlextCliPluginSystem,
)

# Add plugins directory to path for demo
plugins_dir = Path(__file__).parent / "plugins"
if str(plugins_dir) not in sys.path:
    sys.path.insert(0, str(plugins_dir))


def demo_plugin_discovery() -> None:
    """Demo 1: Plugin Discovery."""
    plugin_manager = FlextCliPluginSystem.PluginManager()

    # Discover plugins
    discover_result = plugin_manager.discover_plugins("examples/plugins")

    if discover_result.is_success:
        plugins = discover_result.unwrap()
        for _plugin_name in plugins:
            pass


def demo_plugin_loading() -> None:
    """Demo 2: Plugin Loading."""
    plugin_manager = FlextCliPluginSystem.PluginManager()

    # Load plugin
    load_result = plugin_manager.load_plugin("example_plugin")

    if load_result.is_success:
        load_result.unwrap()

    # Get loaded plugins
    loaded_result = plugin_manager.get_loaded_plugins()

    if loaded_result.is_success:
        loaded = loaded_result.unwrap()
        for _plugin in loaded.values():
            pass


def demo_plugin_initialization() -> None:
    """Demo 3: Plugin Initialization."""
    cli = FlextCli()
    plugin_manager = FlextCliPluginSystem.PluginManager()

    # Load plugin
    load_result = plugin_manager.load_plugin("example_plugin")

    if load_result.is_success:
        plugin = load_result.unwrap()

        # Initialize plugin
        init_result = plugin_manager.initialize_plugin(plugin, cli.main)

        if init_result.is_success:
            pass

        # Get initialized plugins
        initialized_result = plugin_manager.get_initialized_plugins()

        if initialized_result.is_success:
            initialized = initialized_result.unwrap()
            for _name in initialized:
                pass


def demo_plugin_commands() -> None:
    """Demo 4: Plugin Commands (conceptual - shows registered commands)."""
    cli = FlextCli()
    plugin_manager = FlextCliPluginSystem.PluginManager()

    # Load and initialize plugin
    result = plugin_manager.load_and_initialize_plugin("example_plugin", cli.main)

    if result.is_success:
        result.unwrap()

        # Show registered commands (conceptual)


def demo_multiple_plugins() -> None:
    """Demo 5: Loading Multiple Plugins."""
    cli = FlextCli()
    plugin_manager = FlextCliPluginSystem.PluginManager()

    plugins_to_load = [
        ("example_plugin", "ExamplePlugin"),
        ("example_plugin", "DataProcessorPlugin"),
    ]

    loaded_count = 0

    for module_name, class_name in plugins_to_load:
        load_result = plugin_manager.load_plugin(module_name, class_name)

        if load_result.is_success:
            plugin = load_result.unwrap()

            # Initialize
            init_result = plugin_manager.initialize_plugin(plugin, cli.main)
            if init_result.is_success:
                loaded_count += 1

    # Get all initialized
    initialized_result = plugin_manager.get_initialized_plugins()
    if initialized_result.is_success:
        initialized_result.unwrap()


def demo_plugin_lifecycle() -> None:
    """Demo 6: Plugin Lifecycle Management."""
    cli = FlextCli()
    plugin_manager = FlextCliPluginSystem.PluginManager()

    # Load and initialize
    result = plugin_manager.load_and_initialize_plugin("example_plugin", cli.main)

    if result.is_success:
        plugin = result.unwrap()

        # Check loaded status
        loaded_result = plugin_manager.get_loaded_plugins()
        if loaded_result.is_success:
            pass

        # Unload plugin
        unload_result = plugin_manager.unload_plugin(plugin.name)

        if unload_result.is_success:
            # Verify unloaded
            loaded_after = plugin_manager.get_loaded_plugins()
            initialized_after = plugin_manager.get_initialized_plugins()

            if loaded_after.is_success and initialized_after.is_success:
                pass


def main() -> None:
    """Run all Phase 4 plugin system demos."""
    # Run all demos
    demo_plugin_discovery()
    demo_plugin_loading()
    demo_plugin_initialization()
    demo_plugin_commands()
    demo_multiple_plugins()
    demo_plugin_lifecycle()

    # Final summary


if __name__ == "__main__":
    main()
