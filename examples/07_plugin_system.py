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
- FlextResult integration for error handling
- Lifecycle hooks (initialize, execute, cleanup)

HOW TO IMPLEMENT IN YOUR CLI:
Use flext-cli foundation (FlextResult, FlextCli) to build plugin architecture

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from pathlib import Path

from flext_cli import (
    FlextCli,
    FlextCliTables,
    m,
    r,
    t,
    u,
)

cli = FlextCli()


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

    @staticmethod
    def execute(
        data: t.JsonDict,
        output_format: str = "json",
    ) -> r[str]:
        """Execute plugin logic in YOUR application."""
        if output_format == "json":
            output = json.dumps(data, indent=2)
            _ = cli.print(
                f"✅ Exported data as JSON ({len(output)} chars)",
                style="green",
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
    def execute(data: list[t.JsonDict]) -> r[str]:
        """Generate report from data in YOUR CLI."""
        tables = FlextCliTables()
        config = m.Cli.TableConfig(table_format="grid")
        table_result = tables.create_table(data, config=config)

        if table_result.is_failure:
            return r[str].fail(
                f"Report generation failed: {table_result.error}",
            )

        report = table_result.value
        _ = cli.print(f"✅ Generated report ({len(report)} chars)", style="green")
        return r[str].ok(report)


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
        _ = cli.print(f"🔌 Registered plugin: {plugin_name}", style="cyan")

    def execute_plugin(
        self,
        plugin_name: str,
        **kwargs: object,
    ) -> r[t.JsonValue]:
        """Execute plugin by name in YOUR CLI."""
        if plugin_name not in self.plugins:
            return r[t.JsonValue].fail(
                f"Plugin not found: {plugin_name}",
            )

        plugin = self.plugins[plugin_name]

        execute_attr = getattr(plugin, "execute", None)
        if not callable(execute_attr):
            return r[t.JsonValue].fail(
                f"Plugin {plugin_name} does not have execute method",
            )

        execute_method = execute_attr

        try:
            result = execute_method(**kwargs)
            # Result is dynamically typed, convert to JsonValue using u
            # Type narrowing: ensure result is JsonValue compatible
            json_result: t.JsonValue = str(result)  # Default fallback
            if isinstance(result, (str, int, float, bool, type(None))):
                json_result = result
            elif isinstance(result, dict):
                # Type narrowing: dict[str, JsonValue] is JsonValue compatible
                transform_result = u.transform(result, to_json=True)
                if transform_result.is_success:
                    json_result = transform_result.value
                else:
                    # dict[str, str] is JsonValue compatible via type narrowing
                    json_result = result
            elif isinstance(result, list):
                # Type narrowing: list[JsonValue] is JsonValue compatible
                json_result = result
            else:
                json_result = str(result)
            return r[t.JsonValue].ok(json_result)
        except Exception as e:
            return r[t.JsonValue].fail(
                f"Plugin execution failed: {e}",
            )

    def list_plugins(self) -> None:
        """List all registered plugins in YOUR CLI."""
        if not self.plugins:
            _ = cli.print("⚠️  No plugins registered", style="yellow")
            return

        # Use u.Cli.process to create plugin data dict
        def get_plugin_version(_name: str, plugin: object) -> str:
            """Get plugin version."""
            return getattr(plugin, "version", "1.0.0")

        process_result = u.Cli.process(
            self.plugins,
            processor=get_plugin_version,
            on_error="skip",
        )
        plugin_data: t.JsonDict = (
            dict(process_result.value)
            if process_result.is_success and isinstance(process_result.value, dict)
            else {}
        )

        # Cast to expected type for table creation
        table_result = cli.create_table(
            data=plugin_data,
            headers=["Plugin", "Version"],
            title="Registered Plugins",
        )

        if table_result.is_success:
            _ = cli.print_table(table_result.value)


# ============================================================================
# PATTERN 3: Dynamic plugin loading from directory
# ============================================================================


def load_plugins_from_directory(plugin_dir: Path) -> MyAppPluginManager:
    """Load plugins from directory in YOUR CLI."""
    manager = MyAppPluginManager()

    _ = cli.print(f"🔍 Scanning for plugins in: {plugin_dir}", style="cyan")

    if not plugin_dir.exists():
        _ = cli.print(f"⚠️  Plugin directory not found: {plugin_dir}", style="yellow")
        return manager

    # In real usage, you would:
    # 1. Scan directory for .py files
    # 2. Import modules dynamically
    # 3. Find plugin classes
    # 4. Register them

    # For demo, register built-in plugins
    manager.register_plugin(DataExportPlugin())
    manager.register_plugin(ReportGeneratorPlugin())

    _ = cli.print(f"✅ Loaded {len(manager.plugins)} plugins", style="green")
    return manager


# ============================================================================
# PATTERN 4: Plugin with configuration
# ============================================================================


class ConfigurablePlugin:
    """Example of configurable plugin for YOUR CLI."""

    def __init__(self, config: t.JsonDict) -> None:
        """Initialize configurable plugin with configuration dictionary."""
        super().__init__()
        self.name = "configurable-plugin"
        self.config: t.JsonDict = config

    def execute(self) -> r[t.JsonDict]:
        """Execute with configuration in YOUR CLI."""
        _ = cli.print(f"🔧 Plugin config: {self.config}", style="cyan")

        # Your plugin logic using config
        result_data: t.JsonDict = {
            "plugin": self.name,
            "config_applied": True,
            **self.config,  # Unpack config dict instead of using update()
        }

        # Cast to expected type (runtime type is compatible)
        return r[t.JsonDict].ok(result_data)


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

    def initialize(self) -> r[bool]:
        """Initialize plugin resources."""
        _ = cli.print(f"🚀 Initializing {self.name}...", style="cyan")
        # Your initialization logic
        self.initialized = True
        return r[bool].ok(True)

    def execute(self, data: str) -> r[str]:
        """Execute plugin logic."""
        if not self.initialized:
            return r[str].fail("Plugin not initialized")

        processed = data.upper()  # Your processing logic
        _ = cli.print(f"✅ Processed: {processed}", style="green")
        return r[str].ok(processed)

    def cleanup(self) -> r[bool]:
        """Cleanup plugin resources."""
        _ = cli.print(f"🧹 Cleaning up {self.name}...", style="cyan")
        # Your cleanup logic
        self.initialized = False
        return r[bool].ok(True)


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of using plugin system in YOUR code."""
    _ = cli.print("=" * 70, style="bold blue")
    _ = cli.print("  Plugin System Library Usage", style="bold white")
    _ = cli.print("=" * 70, style="bold blue")

    # Example 1: Simple plugin registration
    _ = cli.print("\n1. Plugin Registration (basic):", style="bold cyan")
    manager = MyAppPluginManager()
    manager.register_plugin(DataExportPlugin())
    manager.register_plugin(ReportGeneratorPlugin())

    # Example 2: List plugins
    _ = cli.print("\n2. List Plugins (inventory):", style="bold cyan")
    manager.list_plugins()

    # Example 3: Execute plugin
    _ = cli.print("\n3. Execute Plugin (data export):", style="bold cyan")
    test_data: t.JsonDict = {
        "id": 1,
        "name": "Test",
        "status": "active",
    }
    export_result = manager.execute_plugin("data-export", data=test_data, format="json")
    if export_result.is_success:
        result_value = export_result.value
        output_preview = str(result_value)[:100] if result_value else ""
        _ = cli.print(f"   Output: {output_preview}...", style="white")

    # Example 4: Report plugin
    _ = cli.print("\n4. Report Plugin (table generation):", style="bold cyan")
    report_data: list[t.JsonDict] = [
        {"metric": "Users", "value": "1,234"},
        {"metric": "Orders", "value": "567"},
    ]
    _ = manager.execute_plugin("report-generator", data=report_data)

    # Example 5: Plugin with config
    _ = cli.print("\n5. Configurable Plugin:", style="bold cyan")
    config: t.JsonDict = {"theme": "dark", "verbose": True}
    config_plugin = ConfigurablePlugin(config)
    config_result = config_plugin.execute()
    if config_result.is_success:
        _ = cli.print(f"   Result: {config_result.value}", style="green")

    # Example 6: Lifecycle management
    _ = cli.print("\n6. Plugin Lifecycle (init/execute/cleanup):", style="bold cyan")
    lifecycle_plugin = LifecyclePlugin()
    _ = lifecycle_plugin.initialize()
    _ = lifecycle_plugin.execute("hello world")
    _ = lifecycle_plugin.cleanup()

    # Example 7: Load from directory
    _ = cli.print("\n7. Load from Directory (dynamic discovery):", style="bold cyan")
    plugin_dir = Path.home() / ".myapp" / "plugins"
    _ = load_plugins_from_directory(plugin_dir)

    _ = cli.print("\n" + "=" * 70, style="bold blue")
    _ = cli.print("  ✅ Plugin Examples Complete", style="bold green")
    _ = cli.print("=" * 70, style="bold blue")

    # Integration guide
    _ = cli.print("\n💡 Integration Tips:", style="bold cyan")
    _ = cli.print("  • Create plugin classes with execute() method", style="white")
    _ = cli.print(
        "  • Use plugin manager to register and execute plugins",
        style="white",
    )
    _ = cli.print(
        "  • Add lifecycle hooks (initialize, cleanup) as needed",
        style="white",
    )
    _ = cli.print("  • Use FlextResult for plugin error handling", style="white")


if __name__ == "__main__":
    main()
