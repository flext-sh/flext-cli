"""Plugin System - PATTERN GUIDE (NOT A FLEXT-CLI BUILT-IN FEATURE)..

⚠️  IMPORTANT: This is a PATTERN GUIDE showing how YOU can implement
plugin systems in YOUR own CLI application using flext-cli as a foundation.

flext-cli does NOT provide FlextCliPlugin or FlextCliPluginManager built-in.
This example demonstrates patterns and best practices for YOUR implementation.

WHEN TO USE THIS PATTERN IN YOUR CLI:
- Building CLI tools that support extensions/plugins
- Need to allow third-party functionality additions
- Want modular CLI architecture
- Building extensible command systems
- Need dynamic command registration

WHAT YOU CAN BUILD USING THIS PATTERN:
- Custom plugin classes for YOUR application
- Plugin manager for YOUR CLI
- r integration for error handling
- Lifecycle hooks (initialize, execute, cleanup)

HOW TO IMPLEMENT IN YOUR CLI:
Use flext-cli foundation (r, FlextCli) to build plugin architecture

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from pathlib import Path

from flext_core import r

from flext_cli import FlextCli, FlextCliTables, m, t

cli = FlextCli()


class DataExportPlugin:
    """Example plugin for YOUR CLI - data export functionality."""

    def __init__(self) -> None:
        """Initialize data export plugin with name and version."""
        super().__init__()
        self.name = "data-export"
        self.version = "1.0.0"

    @staticmethod
    def execute(
        data: dict[str, t.NormalizedValue], output_format: str = "json"
    ) -> r[str]:
        """Execute plugin logic in YOUR application."""
        if output_format == "json":
            output = json.dumps(data, indent=2)
            cli.print(f"✅ Exported data as JSON ({len(output)} chars)", style="green")
            return r[str].ok(output)
        return r[str].fail(f"Unsupported format: {output_format}")


class ReportGeneratorPlugin:
    """Example plugin for YOUR CLI - report generation."""

    def __init__(self) -> None:
        """Initialize report generator plugin with name and version."""
        super().__init__()
        self.name = "report-generator"
        self.version = "1.0.0"

    @staticmethod
    def execute(data: list[dict[str, t.NormalizedValue]]) -> r[str]:
        """Generate report from data in YOUR CLI."""
        tables = FlextCliTables()
        config = m.Cli.TableConfig(table_format="grid")
        table_result = tables.create_table(data, config=config)
        if table_result.is_failure:
            return r[str].fail(f"Report generation failed: {table_result.error}")
        report = table_result.value
        cli.print(f"✅ Generated report ({len(report)} chars)", style="green")
        return r[str].ok(report)


class MyAppPluginManager:
    """Plugin manager for YOUR CLI application."""

    def __init__(self) -> None:
        """Initialize plugin manager with empty plugin registry."""
        super().__init__()
        self.plugins: dict[str, t.NormalizedValue] = {}

    def execute_plugin(
        self, plugin_name: str, **kwargs: t.Container
    ) -> r[t.Cli.JsonValue]:
        """Execute plugin by name in YOUR CLI."""
        if plugin_name not in self.plugins:
            return r.fail(f"Plugin not found: {plugin_name}")
        plugin = self.plugins[plugin_name]
        execute_attr = getattr(plugin, "execute", None)
        if not callable(execute_attr):
            return r.fail(f"Plugin {plugin_name} does not have execute method")
        execute_method = execute_attr
        try:
            raw = execute_method(**kwargs)
            if hasattr(raw, "is_success") and hasattr(raw, "value"):
                if getattr(raw, "is_failure", False):
                    return r.fail(
                        getattr(raw, "error", "Unknown error") or "Unknown error"
                    )
                result_value = getattr(raw, "value")
            else:
                result_value = raw
            normalized = m.Cli.CliNormalizedJson(result_value).root
            return r.ok(normalized)
        except Exception as e:
            return r.fail(f"Plugin execution failed: {e}")

    def list_plugins(self) -> None:
        """List all registered plugins in YOUR CLI."""
        if not self.plugins:
            cli.print("⚠️  No plugins registered", style="yellow")
            return

        def get_plugin_version(_name: str, plugin: t.NormalizedValue) -> str:
            """Get plugin version."""
            return getattr(plugin, "version", "1.0.0")

        plugin_items = {
            name: get_plugin_version(name, plugin)
            for name, plugin in self.plugins.items()
        }
        rows: list[dict[str, t.NormalizedValue]] = [
            {"Plugin": name, "Version": ver} for name, ver in plugin_items.items()
        ]
        cli.show_table(rows, headers=["Plugin", "Version"])

    def register_plugin(self, plugin: DataExportPlugin | ReportGeneratorPlugin) -> None:
        """Register plugin in YOUR CLI."""
        plugin_name = getattr(plugin, "name", plugin.__class__.__name__)
        self.plugins[plugin_name] = plugin
        cli.print(f"🔌 Registered plugin: {plugin_name}", style="cyan")


def load_plugins_from_directory(plugin_dir: Path) -> MyAppPluginManager:
    """Load plugins from directory in YOUR CLI."""
    manager = MyAppPluginManager()
    cli.print(f"🔍 Scanning for plugins in: {plugin_dir}", style="cyan")
    if not plugin_dir.exists():
        cli.print(f"⚠️  Plugin directory not found: {plugin_dir}", style="yellow")
        return manager
    manager.register_plugin(DataExportPlugin())
    manager.register_plugin(ReportGeneratorPlugin())
    cli.print(f"✅ Loaded {len(manager.plugins)} plugins", style="green")
    return manager


class ConfigurablePlugin:
    """Example of configurable plugin for YOUR CLI."""

    def __init__(self, config: dict[str, t.NormalizedValue]) -> None:
        """Initialize configurable plugin with configuration dictionary."""
        super().__init__()
        self.name = "configurable-plugin"
        self.config: dict[str, t.NormalizedValue] = config

    def execute(self) -> r[dict[str, t.NormalizedValue]]:
        """Execute with configuration in YOUR CLI."""
        cli.print(f"🔧 Plugin config: {self.config}", style="cyan")
        result_data: dict[str, t.NormalizedValue] = {
            "plugin": self.name,
            "config_applied": True,
            **self.config,
        }
        return r[dict[str, t.NormalizedValue]].ok(result_data)


class LifecyclePlugin:
    """Plugin with lifecycle hooks for YOUR CLI."""

    def __init__(self) -> None:
        """Initialize lifecycle plugin with initialization state tracking."""
        super().__init__()
        self.name = "lifecycle-plugin"
        self.initialized = False

    def cleanup(self) -> r[bool]:
        """Cleanup plugin resources."""
        cli.print(f"🧹 Cleaning up {self.name}...", style="cyan")
        self.initialized = False
        return r[bool].ok(value=True)

    def execute(self, data: str) -> r[str]:
        """Execute plugin logic."""
        if not self.initialized:
            return r[str].fail("Plugin not initialized")
        processed = data.upper()
        cli.print(f"✅ Processed: {processed}", style="green")
        return r[str].ok(processed)

    def initialize(self) -> r[bool]:
        """Initialize plugin resources."""
        cli.print(f"🚀 Initializing {self.name}...", style="cyan")
        self.initialized = True
        return r[bool].ok(value=True)


def main() -> None:
    """Examples of using plugin system in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Plugin System Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n1. Plugin Registration (basic):", style="bold cyan")
    manager = MyAppPluginManager()
    manager.register_plugin(DataExportPlugin())
    manager.register_plugin(ReportGeneratorPlugin())
    cli.print("\n2. List Plugins (inventory):", style="bold cyan")
    manager.list_plugins()
    cli.print("\n3. Execute Plugin (data export):", style="bold cyan")
    test_data: dict[str, t.NormalizedValue] = {
        "id": 1,
        "name": "Test",
        "status": "active",
    }
    export_result = manager.execute_plugin(
        "data-export",
        data=json.dumps(test_data),
        format="json",
    )
    if export_result.is_success:
        result_value = export_result.value
        output_preview = str(result_value)[:100] if result_value else ""
        cli.print(f"   Output: {output_preview}...", style="white")
    cli.print("\n4. Report Plugin (table generation):", style="bold cyan")
    report_data: list[dict[str, t.NormalizedValue]] = [
        {"metric": "Users", "value": "1,234"},
        {"metric": "Orders", "value": "567"},
    ]
    report_result = manager.execute_plugin(
        "report-generator",
        data=json.dumps(report_data),
    )
    if report_result.is_success:
        cli.print(
            f"   Report length: {len(str(report_result.value))} chars", style="green"
        )
    cli.print("\n5. Configurable Plugin:", style="bold cyan")
    config: dict[str, t.NormalizedValue] = {"theme": "dark", "verbose": True}
    config_plugin = ConfigurablePlugin(config)
    config_result = config_plugin.execute()
    if config_result.is_success:
        cli.print(f"   Result: {config_result.value}", style="green")
    cli.print("\n6. Plugin Lifecycle (init/execute/cleanup):", style="bold cyan")
    lifecycle_plugin = LifecyclePlugin()
    init_ok = lifecycle_plugin.initialize()
    if init_ok.is_success:
        exec_result = lifecycle_plugin.execute("hello world")
        if exec_result.is_success:
            cli.print(f"   Output: {exec_result.value}", style="white")
        cleanup_result = lifecycle_plugin.cleanup()
        if cleanup_result.is_failure:
            cli.print(f"   Cleanup warning: {cleanup_result.error}", style="yellow")
    cli.print("\n7. Load from Directory (dynamic discovery):", style="bold cyan")
    plugin_dir = Path.home() / ".myapp" / "plugins"
    loaded_manager = load_plugins_from_directory(plugin_dir)
    cli.print(
        f"   Plugins available: {list(loaded_manager.plugins.keys())}", style="white"
    )
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Plugin Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print("  • Create plugin classes with execute() method", style="white")
    cli.print("  • Use plugin manager to register and execute plugins", style="white")
    cli.print("  • Add lifecycle hooks (initialize, cleanup) as needed", style="white")
    cli.print("  • Use r for plugin error handling", style="white")


if __name__ == "__main__":
    main()
