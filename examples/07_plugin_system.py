"""Plugin System - Using flext-cli for Extensible CLIs.

WHEN TO USE THIS:
- Building CLI tools that support extensions/plugins
- Need to allow third-party functionality additions
- Want modular CLI architecture
- Building extensible command systems
- Need dynamic command registration

FLEXT-CLI PROVIDES:
- FlextCliPlugin - Base plugin class
- FlextCliPluginManager - Plugin discovery and management
- FlextResult integration - Error handling for plugins
- Lifecycle hooks - initialize, execute, cleanup

HOW TO USE IN YOUR CLI:
Create plugin-based architecture in YOUR CLI application

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from pathlib import Path

from flext_core import FlextResult

from flext_cli import FlextCli, FlextCliTables
from flext_cli.typings import FlextCliTypes

cli = FlextCli.get_instance()


# ============================================================================
# PATTERN 1: Create custom plugin for YOUR CLI
# ============================================================================


class DataExportPlugin:
    """Example plugin for YOUR CLI - data export functionality."""

    def __init__(self) -> None:
        """Initialize data export plugin with name and version."""
        super().__init__()
        self.name = "data-export"
        self.version = "1.0.0"

    def execute(
        self, data: FlextCliTypes.Data.CliDataDict, output_format: str = "json"
    ) -> FlextResult[str]:
        """Execute plugin logic in YOUR application."""
        if output_format == "json":
            output = json.dumps(data, indent=2)
            cli.print(f"✅ Exported data as JSON ({len(output)} chars)", style="green")
            return FlextResult[str].ok(output)
        return FlextResult[str].fail(f"Unsupported format: {format}")


class ReportGeneratorPlugin:
    """Example plugin for YOUR CLI - report generation."""

    def __init__(self) -> None:
        """Initialize report generator plugin with name and version."""
        super().__init__()
        self.name = "report-generator"
        self.version = "1.0.0"

    def execute(self, data: list[FlextCliTypes.Data.CliDataDict]) -> FlextResult[str]:
        """Generate report from data in YOUR CLI."""
        tables = FlextCliTables()
        table_result = tables.create_table(data, table_format="grid")

        if table_result.is_failure:
            return FlextResult[str].fail(
                f"Report generation failed: {table_result.error}"
            )

        report = table_result.unwrap()
        cli.print(f"✅ Generated report ({len(report)} chars)", style="green")
        return FlextResult[str].ok(report)


# ============================================================================
# PATTERN 2: Plugin manager for YOUR CLI
# ============================================================================


class MyAppPluginManager:
    """Plugin manager for YOUR CLI application."""

    def __init__(self) -> None:
        """Initialize plugin manager with empty plugin registry."""
        super().__init__()
        self.plugins: dict[str, object] = {}

    def register_plugin(self, plugin: object) -> None:
        """Register plugin in YOUR CLI."""
        plugin_name = getattr(plugin, "name", plugin.__class__.__name__)
        self.plugins[plugin_name] = plugin
        cli.print(f"🔌 Registered plugin: {plugin_name}", style="cyan")

    def execute_plugin(self, plugin_name: str, **kwargs: object) -> FlextResult[object]:
        """Execute plugin by name in YOUR CLI."""
        if plugin_name not in self.plugins:
            return FlextResult[object].fail(f"Plugin not found: {plugin_name}")

        plugin = self.plugins[plugin_name]
        if not hasattr(plugin, "execute"):
            return FlextResult[object].fail(
                f"Plugin {plugin_name} does not have execute method"
            )

        try:
            # Type guard: we checked execute exists
            execute_method = getattr(plugin, "execute")
            return execute_method(**kwargs)
        except Exception as e:
            return FlextResult[object].fail(f"Plugin execution failed: {e}")

    def list_plugins(self) -> None:
        """List all registered plugins in YOUR CLI."""
        if not self.plugins:
            cli.print("⚠️  No plugins registered", style="yellow")
            return

        plugin_data: FlextCliTypes.Data.CliDataDict = {
            name: getattr(plugin, "version", "1.0.0")
            for name, plugin in self.plugins.items()
        }

        # Cast to expected type for table creation
        table_result = cli.create_table(
            data=plugin_data, headers=["Plugin", "Version"], title="Registered Plugins"
        )

        if table_result.is_success:
            cli.print_table(table_result.unwrap())


# ============================================================================
# PATTERN 3: Dynamic plugin loading from directory
# ============================================================================


def load_plugins_from_directory(plugin_dir: Path) -> MyAppPluginManager:
    """Load plugins from directory in YOUR CLI."""
    manager = MyAppPluginManager()

    cli.print(f"🔍 Scanning for plugins in: {plugin_dir}", style="cyan")

    if not plugin_dir.exists():
        cli.print(f"⚠️  Plugin directory not found: {plugin_dir}", style="yellow")
        return manager

    # In real usage, you would:
    # 1. Scan directory for .py files
    # 2. Import modules dynamically
    # 3. Find plugin classes
    # 4. Register them

    # For demo, register built-in plugins
    manager.register_plugin(DataExportPlugin())
    manager.register_plugin(ReportGeneratorPlugin())

    cli.print(f"✅ Loaded {len(manager.plugins)} plugins", style="green")
    return manager


# ============================================================================
# PATTERN 4: Plugin with configuration
# ============================================================================


class ConfigurablePlugin:
    """Example of configurable plugin for YOUR CLI."""

    def __init__(self, config: FlextCliTypes.Data.CliDataDict) -> None:
        """Initialize configurable plugin with configuration dictionary."""
        super().__init__()
        self.name = "configurable-plugin"
        self.config: FlextCliTypes.Data.CliDataDict = config

    def execute(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute with configuration in YOUR CLI."""
        cli.print(f"🔧 Plugin config: {self.config}", style="cyan")

        # Your plugin logic using config
        result_data: FlextCliTypes.Data.CliDataDict = {
            "plugin": self.name,
            "config_applied": True,
            **self.config,  # Unpack config dict instead of using update()
        }

        # Cast to expected type (runtime type is compatible)
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok(result_data)


# ============================================================================
# PATTERN 5: Plugin lifecycle hooks
# ============================================================================


class LifecyclePlugin:
    """Plugin with lifecycle hooks for YOUR CLI."""

    def __init__(self) -> None:
        """Initialize lifecycle plugin with initialization state tracking."""
        super().__init__()
        self.name = "lifecycle-plugin"
        self.initialized = False

    def initialize(self) -> FlextResult[None]:
        """Initialize plugin resources."""
        cli.print(f"🚀 Initializing {self.name}...", style="cyan")
        # Your initialization logic
        self.initialized = True
        return FlextResult[None].ok(None)

    def execute(self, data: str) -> FlextResult[str]:
        """Execute plugin logic."""
        if not self.initialized:
            return FlextResult[str].fail("Plugin not initialized")

        processed = data.upper()  # Your processing logic
        cli.print(f"✅ Processed: {processed}", style="green")
        return FlextResult[str].ok(processed)

    def cleanup(self) -> FlextResult[None]:
        """Cleanup plugin resources."""
        cli.print(f"🧹 Cleaning up {self.name}...", style="cyan")
        # Your cleanup logic
        self.initialized = False
        return FlextResult[None].ok(None)


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of using plugin system in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Plugin System Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")

    # Example 1: Simple plugin registration
    cli.print("\n1. Plugin Registration (basic):", style="bold cyan")
    manager = MyAppPluginManager()
    manager.register_plugin(DataExportPlugin())
    manager.register_plugin(ReportGeneratorPlugin())

    # Example 2: List plugins
    cli.print("\n2. List Plugins (inventory):", style="bold cyan")
    manager.list_plugins()

    # Example 3: Execute plugin
    cli.print("\n3. Execute Plugin (data export):", style="bold cyan")
    test_data: FlextCliTypes.Data.CliDataDict = {
        "id": 1,
        "name": "Test",
        "status": "active",
    }
    export_result = manager.execute_plugin("data-export", data=test_data, format="json")
    if export_result.is_success:
        result_value = export_result.unwrap()
        output_preview = str(result_value)[:100] if result_value else ""
        cli.print(f"   Output: {output_preview}...", style="white")

    # Example 4: Report plugin
    cli.print("\n4. Report Plugin (table generation):", style="bold cyan")
    report_data: list[FlextCliTypes.Data.CliDataDict] = [
        {"metric": "Users", "value": "1,234"},
        {"metric": "Orders", "value": "567"},
    ]
    manager.execute_plugin("report-generator", data=report_data)

    # Example 5: Plugin with config
    cli.print("\n5. Configurable Plugin:", style="bold cyan")
    config: FlextCliTypes.Data.CliDataDict = {"theme": "dark", "verbose": True}
    config_plugin = ConfigurablePlugin(config)
    config_result = config_plugin.execute()
    if config_result.is_success:
        cli.print(f"   Result: {config_result.unwrap()}", style="green")

    # Example 6: Lifecycle management
    cli.print("\n6. Plugin Lifecycle (init/execute/cleanup):", style="bold cyan")
    lifecycle_plugin = LifecyclePlugin()
    lifecycle_plugin.initialize()
    lifecycle_plugin.execute("hello world")
    lifecycle_plugin.cleanup()

    # Example 7: Load from directory
    cli.print("\n7. Load from Directory (dynamic discovery):", style="bold cyan")
    plugin_dir = Path.home() / ".myapp" / "plugins"
    load_plugins_from_directory(plugin_dir)

    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Plugin Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")

    # Integration guide
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print("  • Create plugin classes with execute() method", style="white")
    cli.print("  • Use plugin manager to register and execute plugins", style="white")
    cli.print("  • Add lifecycle hooks (initialize, cleanup) as needed", style="white")
    cli.print("  • Use FlextResult for plugin error handling", style="white")


if __name__ == "__main__":
    main()
