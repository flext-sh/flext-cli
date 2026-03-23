"""Console Output - Using flext-cli for Styled Terminal Output in YOUR Code.

WHEN TO USE THIS:
- Building a CLI and want colored/styled output
- Need to display data as tables
- Want progress bars for long operations
- Need to format output for terminals
- Want status spinners for operations
- Need live-updating displays
- Want bordered content panels

FLEXT-CLI PROVIDES:
- cli.print() - Styled text output (uses Rich)
- cli.show_table() - Create and print tables in one call (no branching)
- FlextCliTables - ASCII tables for plain text (create_table for strings, export_report pattern)
- Progress bars and spinners
- Tree structures for hierarchical data
- Rich Status - Spinning status indicators
- Rich Live - Auto-refreshing displays
- Rich Panel - Bordered content boxes

HOW TO USE IN YOUR CLI:
Replace print() with cli.print() for styled output
Use cli.show_table() to display data (one call, no result handling)
Use Status() for operation spinners
Use Live() for auto-updating displays
Use Panel() for organized content

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pathlib
import time
from collections.abc import Mapping, Sequence
from pathlib import Path

from flext_core import r

from flext_cli import FlextCli, FlextCliTables, c, m, t

cli = FlextCli()
tables = FlextCliTables()


def your_cli_function() -> None:
    """Replace print() with styled output in your functions."""
    cli.print("✅ Operation successful!", style="green")
    cli.print("❌ ERROR: Operation failed", style="bold red")
    cli.print("⚠️  WARNING: Please check this", style="yellow")
    cli.print("ℹ️  Processing 100 records...", style="cyan")


def display_database_results(records: Sequence[t.Cli.JsonValue]) -> None:
    """Display database query results as a table."""
    if not records:
        cli.print("No results found", style="yellow")
        return
    rows: Sequence[Mapping[str, str]] = []
    for i, record in enumerate(records[:10], 1):
        row_data = " | ".join(str(v) for v in record.values())
        rows.append({"#": f"Row {i}", "Data": row_data})
    cli.show_table(rows, headers=["#", "Data"])


def export_report(
    data: Sequence[t.Cli.JsonValue], format_type: c.Cli.OutputFormatLiteral = "table"
) -> r[str]:
    """Create ASCII tables for logs/reports in your app."""
    config = m.Cli.TableConfig(table_format=format_type)
    result = tables.create_table(list(data), config=config)
    if result.is_success:
        return r[str].ok(result.value)
    return r[str].fail(result.error or "Failed to create table")


def process_large_dataset(items: Sequence[str]) -> None:
    """Process items with progress updates."""
    cli.print("Processing items...", style="cyan")
    total = len(items)
    for i in range(1, len(items) + 1):
        time.sleep(0.01)
        if i % 10 == 0 or i == total:
            percentage = int(i / total * 100)
            cli.print(f"Progress: {i}/{total} items ({percentage}%)", style="yellow")
    cli.print("✅ All items processed!", style="green")


def display_project_structure(root_path: str | Path) -> None:
    """Display directory tree or any hierarchical data."""
    tree_result = cli.create_tree(f"📁 {Path(root_path).name}")
    if tree_result.is_success:
        tree = tree_result.value
        for item in Path(root_path).iterdir():
            if item.is_dir():
                tree.add(f"📂 {item.name}/")
            else:
                tree.add(f"📄 {item.name}")
        cli.print(str(tree))


def process_with_status(operation_name: str) -> None:
    """Show spinning status indicator during operations."""
    cli.print(f"\n🔄 Starting: {operation_name}", style="cyan")
    stages = [
        ("Initializing...", 0.5),
        ("Connecting to database...", 1.0),
        ("Fetching records...", 1.5),
        ("Processing data...", 1.0),
        ("Saving results...", 0.8),
    ]
    for stage_name, duration in stages:
        cli.print(f"⏳ {stage_name}", style="yellow")
        time.sleep(duration)
        cli.print(f"✅ {stage_name} completed", style="green")
    cli.print("🎉 Operation completed successfully!", style="bold green")


def monitor_live_metrics() -> None:
    """Display periodic metrics updates for your application."""
    cli.print("\n📊 Starting monitoring...", style="cyan")
    for i in range(5):
        cpu = 45 + i % 40
        memory = 55 + i % 35
        requests = 150 + i * 10
        metrics_data: Sequence[Mapping[str, t.NormalizedValue]] = [
            {
                "Metric": "CPU Usage",
                "Value": f"{cpu}%",
                "Status": "🟢 Normal" if cpu < 80 else "🔴 High",
            },
            {
                "Metric": "Memory",
                "Value": f"{memory}%",
                "Status": "🟢 Normal" if memory < 80 else "🔴 High",
            },
            {"Metric": "Requests/sec", "Value": f"{requests}", "Status": "🟢 Active"},
        ]
        cli.show_table(metrics_data, headers=["Metric", "Value", "Status"])
        time.sleep(1.0)
    cli.print("✅ Monitoring session complete", style="green")


def display_with_panels(data: Mapping[str, t.NormalizedValue]) -> None:
    """Display content in organized sections."""
    cli.print("\n📦 Organized Content Display:", style="cyan")
    cli.print("\n📊 Summary:", style="bold blue")
    cli.print(f"  Total Records: {data.get('total', 0)}", style="cyan")
    cli.print(f"  Successful: {data.get('successful', 0)}", style="green")
    cli.print(f"  Failed: {data.get('failed', 0)}", style="red")
    cli.print(f"  Pending: {data.get('pending', 0)}", style="yellow")
    details_data: Sequence[Mapping[str, t.NormalizedValue]] = []
    for key, value in data.items():
        if key not in {"total", "successful", "failed", "pending"}:
            details_data.append({"Property": key, "Value": str(value)})
    if details_data:
        cli.print("\n📋 Details:", style="bold green")
        cli.show_table(details_data, headers=["Property", "Value"])
    cli.print("\n💡 Status:", style="bold yellow")
    cli.print("✅ All systems operational", style="green")


def main() -> None:
    """Examples of using output formatting in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Console Output Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n1. Styled Messages (replace print):", style="bold cyan")
    your_cli_function()
    cli.print("\n2. Rich Tables (display data):", style="bold cyan")
    sample_data: Sequence[Mapping[str, t.NormalizedValue]] = [
        {"id": 1, "name": "Alice", "status": "active"},
        {"id": 2, "name": "Bob", "status": "inactive"},
    ]
    display_database_results(sample_data)
    cli.print("\n3. ASCII Tables (for logs/reports):", style="bold cyan")
    ascii_result = export_report(sample_data, "table")
    if ascii_result.is_success:
        cli.print(ascii_result.value, style="white")
    cli.print("\n4. Progress Bars (long operations):", style="bold cyan")
    items = ["file1", "file2", "file3", "file4"]
    process_large_dataset(items)
    cli.print("\n5. Tree Structures (hierarchies):", style="bold cyan")
    display_project_structure(pathlib.Path.cwd())
    cli.print("\n6. Status Spinners (operations):", style="bold cyan")
    process_with_status("Data Migration")
    cli.print("\n7. Live Updates (real-time monitoring):", style="bold cyan")
    monitor_live_metrics()
    cli.print("\n8. Panels (organized content):", style="bold cyan")
    panel_data: Mapping[str, t.NormalizedValue] = {
        "total": 1250,
        "successful": 1100,
        "failed": 50,
        "pending": 100,
        "start_time": "2025-10-08 10:00:00",
        "end_time": "2025-10-08 11:30:00",
        "duration": "1h 30m",
    }
    display_with_panels(panel_data)
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Output Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print(
        "  • Rich tables: Use cli.show_table() for terminal display", style="white"
    )
    cli.print("  • ASCII tables: Use FlextCliTables for logs/files", style="white")
    cli.print("  • Progress: Use cli.print() with percentage updates", style="white")
    cli.print("  • Status: Use cli.print() with status messages", style="white")
    cli.print(
        "  • Tables: Use cli.show_table() for auto-refreshing data", style="white"
    )
    cli.print("  • Organization: Use cli.print() with sections", style="white")
    cli.print("  • All methods return r for error handling", style="white")
    cli.print(
        "  • NEVER import rich/click/tabulate directly - use FlextCli!", style="white"
    )


def advanced_output_example() -> None:
    """Demonstrate advanced output formatting with Python 3.13+ patterns.

    Shows how to use:
    - StrEnum for format validation
    - collections.abc.Mapping for configuration
    - Advanced Literal unions
    - Type-safe data structures
    """
    cli.print("\n=== Advanced Output Formatting ===", style="bold blue")
    output_format = "table"
    cli.print(f"Using format: {output_format}", style="cyan")
    sample_data: t.Cli.TableRows = (
        {"name": "Alice", "age": 30, "role": "developer"},
        {"name": "Bob", "age": 25, "role": "designer"},
        {"name": "Charlie", "age": 35, "role": "manager"},
    )
    valid_formats: tuple[str, ...] = tuple(sorted(c.Cli.ValidationLists.OUTPUT_FORMATS))
    cli.print(f"Supported formats: {', '.join(valid_formats)}", style="green")
    cli.show_table(list(sample_data), headers=["Name", "Age", "Role"])


if __name__ == "__main__":
    main()
    advanced_output_example()
