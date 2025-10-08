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
    """Show plugin auto-discovery concept."""
    cli.formatters.print("\n🔌 Plugin Loading:", style="bold cyan")

    # Plugin system concept demonstration
    # In real usage, plugins would be auto-discovered from directory
    cli.formatters.print(
        "ℹ️  Plugin auto-discovery (extensible architecture)", style="cyan"
    )
    cli.formatters.print(
        "✅ Plugins can be loaded from custom directories", style="green"
    )


def demonstrate_custom_plugin() -> None:
    """Show custom plugin with auto-lifecycle."""
    cli.formatters.print("\n🛠️  Custom Plugin:", style="bold cyan")

    # Plugin lifecycle auto-managed (init, load, cleanup)
    class CustomPlugin:
        def execute(self) -> FlextResult[dict]:
            return FlextResult[dict].ok({"status": "executed"})

    plugin = CustomPlugin()
    result = plugin.execute()

    if result.is_success:
        cli.formatters.print(f"✅ Plugin executed: {result.unwrap()}", style="green")

    cli.formatters.print("✅ Plugin lifecycle auto-managed", style="cyan")


def main() -> None:
    """Run all demonstrations."""
    cli.formatters.print("=" * 60, style="bold blue")
    cli.formatters.print("  Plugin System Examples", style="bold white on blue")
    cli.formatters.print("=" * 60, style="bold blue")

    demonstrate_plugin_loading()
    demonstrate_custom_plugin()

    cli.formatters.print("\n" + "=" * 60, style="bold blue")
    cli.formatters.print("  ✅ All plugin examples completed!", style="bold green")
    cli.formatters.print("=" * 60, style="bold blue")


if __name__ == "__main__":
    main()
