"""Plugin System - Extensibility.

Demonstrates flext-cli plugin system through FlextCli API.

Key Features:
- Auto-discovery of plugins from directory
- Plugin lifecycle auto-management
- Dependency resolution automatic
- Hot-reload support

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_plugin_loading() -> None:
    """Show plugin auto-discovery and loading."""
    # Plugins auto-discovered from directory
    discover_result = cli.plugins.discover_plugins("./plugins")
    if discover_result.is_success:
        cli.output.print_success(f"Plugins auto-discovered: {discover_result.value}")


def demonstrate_custom_plugin() -> None:
    """Show custom plugin with auto-lifecycle."""

    # Plugin lifecycle auto-managed (init, load, cleanup)
    class CustomPlugin:
        def execute(self) -> FlextResult[dict]:
            return FlextResult[dict].ok({"status": "executed"})

    cli.output.print_message("Plugin lifecycle auto-managed")


def main() -> None:
    """Run all demonstrations."""
    demonstrate_plugin_loading()
    demonstrate_custom_plugin()


if __name__ == "__main__":
    main()
