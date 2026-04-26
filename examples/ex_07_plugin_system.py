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
Use flext-cli foundation (r, cli) to build plugin architecture

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from collections.abc import (
    Mapping,
    MutableMapping,
    Sequence,
)
from pathlib import Path

from examples import c, m, t, u
from flext_cli import cli
from flext_core import p, r


class DataExportPlugin:
    """Example plugin for YOUR CLI - data export functionality."""

    def __init__(self) -> None:
        """Initialize data export plugin with name and version."""
        super().__init__()
        self.name = "data-export"
        self.version = "1.0.0"

    @staticmethod
    def execute(
        data: t.JsonMapping,
        output_format: c.Cli.OutputFormats = c.Cli.OutputFormats.JSON,
    ) -> p.Result[str]:
        """Execute plugin logic in YOUR application."""
        if output_format == c.Cli.OutputFormats.JSON:
            output = json.dumps(data, indent=2)
            cli.print(
                f"✅ Exported data as JSON ({len(output)} chars)",
                style=c.Cli.MessageStyles.GREEN,
            )
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
    def execute(data: Sequence[t.JsonMapping]) -> p.Result[str]:
        """Generate report from data in YOUR CLI."""
        table_result = cli.format_table(data, table_format=c.Cli.TabularFormat.GRID)
        if table_result.failure:
            return r[str].fail(f"Report generation failed: {table_result.error}")
        report = table_result.value
        cli.print(
            f"✅ Generated report ({len(report)} chars)",
            style=c.Cli.MessageStyles.GREEN,
        )
        return r[str].ok(report)


class MyAppPluginManager:
    """Plugin manager for YOUR CLI application."""

    def __init__(self) -> None:
        """Initialize plugin manager with empty plugin registry."""
        super().__init__()
        self.plugins: MutableMapping[str, DataExportPlugin | ReportGeneratorPlugin] = {}

    def execute_plugin(
        self,
        plugin_name: str,
        **kwargs: t.JsonValue,
    ) -> p.Result[t.JsonValue]:
        """Execute plugin by name in YOUR CLI."""
        if plugin_name not in self.plugins:
            return r[t.JsonValue].fail(f"Plugin not found: {plugin_name}")
        plugin = self.plugins[plugin_name]
        try:
            if isinstance(plugin, DataExportPlugin):
                data_val = kwargs.get("data", "")
                fmt_val = kwargs.get("format", c.Cli.OutputFormats.JSON)
                plugin_format = (
                    fmt_val
                    if isinstance(fmt_val, c.Cli.OutputFormats)
                    else c.Cli.OutputFormats(str(fmt_val))
                )
                raw = plugin.execute(
                    data={"raw": str(data_val)},
                    output_format=plugin_format,
                )
            else:
                data_val = kwargs.get("data", "")
                raw = plugin.execute(data=[{"raw": str(data_val)}])
            if raw.failure:
                return r[t.JsonValue].fail(raw.error or "Unknown error")
            normalized = m.Cli.CliNormalizedJson(raw.value).root
            return r[t.JsonValue].ok(normalized)
        except Exception as e:
            return r[t.JsonValue].fail(f"Plugin execution failed: {e}")

    def list_plugins(self) -> None:
        """List all registered plugins in YOUR CLI."""
        if not self.plugins:
            cli.print("⚠️  No plugins registered", style=c.Cli.MessageStyles.YELLOW)
            return

        def resolve_plugin_version(
            plugin: DataExportPlugin | ReportGeneratorPlugin,
        ) -> str:
            """Get plugin version."""
            return plugin.version

        plugin_items = {
            name: resolve_plugin_version(plugin)
            for name, plugin in self.plugins.items()
        }
        rows: Sequence[t.JsonMapping] = [
            {"Plugin": name, "Version": ver} for name, ver in plugin_items.items()
        ]
        cli.show_table(rows, headers=["Plugin", "Version"])

    def register_plugin(self, plugin: DataExportPlugin | ReportGeneratorPlugin) -> None:
        """Register plugin in YOUR CLI."""
        plugin_name = getattr(plugin, "name", plugin.__class__.__name__)
        self.plugins[plugin_name] = plugin
        cli.print(
            f"🔌 Registered plugin: {plugin_name}", style=c.Cli.MessageStyles.CYAN
        )


def load_plugins_from_directory(plugin_dir: Path) -> MyAppPluginManager:
    """Load plugins from directory in YOUR CLI."""
    manager = MyAppPluginManager()
    cli.print(
        f"🔍 Scanning for plugins in: {plugin_dir}", style=c.Cli.MessageStyles.CYAN
    )
    if not plugin_dir.exists():
        cli.print(
            f"⚠️  Plugin directory not found: {plugin_dir}",
            style=c.Cli.MessageStyles.YELLOW,
        )
        return manager
    manager.register_plugin(DataExportPlugin())
    manager.register_plugin(ReportGeneratorPlugin())
    cli.print(
        f"✅ Loaded {len(manager.plugins)} plugins", style=c.Cli.MessageStyles.GREEN
    )
    return manager


class ConfigurablePlugin:
    """Example of configurable plugin for YOUR CLI."""

    def __init__(self, settings: Mapping[str, t.JsonPayloadCollectionValue]) -> None:
        """Initialize configurable plugin with configuration dictionary."""
        super().__init__()
        self.name = "configurable-plugin"
        self.settings: Mapping[str, t.JsonPayloadCollectionValue] = settings

    def execute(self) -> p.Result[t.JsonMapping]:
        """Execute with configuration in YOUR CLI."""
        cli.print(
            f"🔧 Plugin settings: {self.settings}", style=c.Cli.MessageStyles.CYAN
        )
        result_data = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
            u.Cli.normalize_json_value({
                "plugin": self.name,
                "config_applied": True,
                **self.settings,
            })
        )
        return r[t.JsonMapping].ok(result_data)


class LifecyclePlugin:
    """Plugin with lifecycle hooks for YOUR CLI."""

    def __init__(self) -> None:
        """Initialize lifecycle plugin with initialization state tracking."""
        super().__init__()
        self.name = "lifecycle-plugin"
        self.initialized = False

    def cleanup(self) -> p.Result[bool]:
        """Cleanup plugin resources."""
        cli.print(f"🧹 Cleaning up {self.name}...", style=c.Cli.MessageStyles.CYAN)
        self.initialized = False
        return r[bool].ok(value=True)

    def execute(self, data: str) -> p.Result[str]:
        """Execute plugin logic."""
        if not self.initialized:
            return r[str].fail("Plugin not initialized")
        processed = data.upper()
        cli.print(f"✅ Processed: {processed}", style=c.Cli.MessageStyles.GREEN)
        return r[str].ok(processed)

    def initialize(self) -> p.Result[bool]:
        """Initialize plugin resources."""
        cli.print(f"🚀 Initializing {self.name}...", style=c.Cli.MessageStyles.CYAN)
        self.initialized = True
        return r[bool].ok(value=True)


def main() -> None:
    """Examples of using plugin system in YOUR code."""
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("  Plugin System Library Usage", style=c.Cli.MessageStyles.BOLD_WHITE)
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n1. Plugin Registration (basic):", style=c.Cli.MessageStyles.BOLD_CYAN)
    manager = MyAppPluginManager()
    manager.register_plugin(DataExportPlugin())
    manager.register_plugin(ReportGeneratorPlugin())
    cli.print("\n2. List Plugins (inventory):", style=c.Cli.MessageStyles.BOLD_CYAN)
    manager.list_plugins()
    cli.print("\n3. Execute Plugin (data export):", style=c.Cli.MessageStyles.BOLD_CYAN)
    test_data = {
        "id": 1,
        "name": "Test",
        "status": "active",
    }
    export_result = manager.execute_plugin(
        "data-export",
        data=json.dumps(test_data),
        format=c.Cli.OutputFormats.JSON,
    )
    if export_result.success:
        result_value = export_result.value
        output_preview = str(result_value)[:100] if result_value else ""
        cli.print(f"   Output: {output_preview}...", style=c.Cli.MessageStyles.WHITE)
    cli.print(
        "\n4. Report Plugin (table generation):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    report_data: Sequence[t.JsonMapping] = [
        {"metric": "Users", "value": "1,234"},
        {"metric": "Orders", "value": "567"},
    ]
    report_result = manager.execute_plugin(
        "report-generator",
        data=json.dumps(report_data),
    )
    if report_result.success:
        cli.print(
            f"   Report length: {len(str(report_result.value))} chars",
            style=c.Cli.MessageStyles.GREEN,
        )
    cli.print("\n5. Configurable Plugin:", style=c.Cli.MessageStyles.BOLD_CYAN)
    settings = {"theme": "dark", "verbose": True}
    config_plugin = ConfigurablePlugin(settings)
    config_result = config_plugin.execute()
    if config_result.success:
        cli.print(f"   Result: {config_result.value}", style=c.Cli.MessageStyles.GREEN)
    cli.print(
        "\n6. Plugin Lifecycle (init/execute/cleanup):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    lifecycle_plugin = LifecyclePlugin()
    init_ok = lifecycle_plugin.initialize()
    if init_ok.success:
        exec_result = lifecycle_plugin.execute("hello world")
        if exec_result.success:
            cli.print(
                f"   Output: {exec_result.value}", style=c.Cli.MessageStyles.WHITE
            )
        cleanup_result = lifecycle_plugin.cleanup()
        if cleanup_result.failure:
            cli.print(
                f"   Cleanup warning: {cleanup_result.error}",
                style=c.Cli.MessageStyles.YELLOW,
            )
    cli.print(
        "\n7. Load from Directory (dynamic discovery):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    plugin_dir = Path.home() / ".myapp" / "plugins"
    loaded_manager = load_plugins_from_directory(plugin_dir)
    cli.print(
        f"   Plugins available: {list(loaded_manager.plugins.keys())}",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("  ✅ Plugin Examples Complete", style=c.Cli.MessageStyles.BOLD_GREEN)
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n💡 Integration Tips:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "  • Create plugin classes with execute() method",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Use plugin manager to register and execute plugins",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Add lifecycle hooks (initialize, cleanup) as needed",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print("  • Use r for plugin error handling", style=c.Cli.MessageStyles.WHITE)


if __name__ == "__main__":
    main()
