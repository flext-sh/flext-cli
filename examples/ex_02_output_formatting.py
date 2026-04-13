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
- cli.format_table() - Format tables as strings for logs, files, and reports
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
from collections.abc import MutableSequence, Sequence
from pathlib import Path

from examples import c, t
from flext_cli import cli


def your_cli_function() -> None:
    """Replace print() with styled output in your functions."""
    cli.print("✅ Operation successful!", style=c.Cli.MessageStyles.GREEN)
    cli.print("❌ ERROR: Operation failed", style=c.Cli.MessageStyles.BOLD_RED)
    cli.print("⚠️  WARNING: Please check this", style=c.Cli.MessageStyles.YELLOW)
    cli.print("ℹ️  Processing 100 records...", style=c.Cli.MessageStyles.CYAN)


def display_database_results(records: Sequence[t.Cli.TableMappingRow]) -> None:
    """Display database query results as a table."""
    if not records:
        cli.print("No results found", style=c.Cli.MessageStyles.YELLOW)
        return
    rows: MutableSequence[t.StrMapping] = []
    for i, record in enumerate(records[:10], 1):
        row_data = " | ".join(str(v) for v in record.values())
        rows.append({"#": f"Row {i}", "Data": row_data})
    cli.show_table(rows, headers=["#", "Data"])


def export_report(
    data: Sequence[t.Cli.TableMappingRow],
    format_type: c.Cli.OutputFormats = c.Cli.OutputFormats.TABLE,
) -> p.Result[str]:
    """Create ASCII tables for logs/reports in your app."""
    return cli.format_table(list(data) if data else [], table_format=format_type)


def process_large_dataset(items: t.StrSequence) -> None:
    """Process items with progress updates."""
    cli.print("Processing items...", style=c.Cli.MessageStyles.CYAN)
    total = len(items)
    for i in range(1, len(items) + 1):
        time.sleep(0.01)
        if i % 10 == 0 or i == total:
            percentage = int(i / total * 100)
            cli.print(
                f"Progress: {i}/{total} items ({percentage}%)",
                style=c.Cli.MessageStyles.YELLOW,
            )
    cli.print("✅ All items processed!", style=c.Cli.MessageStyles.GREEN)


def display_project_structure(root_path: str | Path) -> None:
    """Display directory tree or any hierarchical data."""
    tree_result = cli.create_tree(f"📁 {Path(root_path).name}")
    if tree_result.success:
        tree = tree_result.value
        for item in Path(root_path).iterdir():
            if item.is_dir():
                tree.add(f"📂 {item.name}/")
            else:
                tree.add(f"📄 {item.name}")
        cli.print(str(tree))


def process_with_status(operation_name: str) -> None:
    """Show spinning status indicator during operations."""
    cli.print(f"\n🔄 Starting: {operation_name}", style=c.Cli.MessageStyles.CYAN)
    stages = [
        ("Initializing...", 0.5),
        ("Connecting to database...", 1.0),
        ("Fetching records...", 1.5),
        ("Processing data...", 1.0),
        ("Saving results...", 0.8),
    ]
    for stage_name, duration in stages:
        cli.print(f"⏳ {stage_name}", style=c.Cli.MessageStyles.YELLOW)
        time.sleep(duration)
        cli.print(f"✅ {stage_name} completed", style=c.Cli.MessageStyles.GREEN)
    cli.print(
        "🎉 Operation completed successfully!", style=c.Cli.MessageStyles.BOLD_GREEN
    )


def monitor_live_metrics() -> None:
    """Display periodic metrics updates for your application."""
    cli.print("\n📊 Starting monitoring...", style=c.Cli.MessageStyles.CYAN)
    for i in range(5):
        cpu = 45 + i % 40
        memory = 55 + i % 35
        requests = 150 + i * 10
        metrics_data: Sequence[t.RecursiveContainerMapping] = [
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
    cli.print("✅ Monitoring session complete", style=c.Cli.MessageStyles.GREEN)


def display_with_panels(data: t.RecursiveContainerMapping) -> None:
    """Display content in organized sections."""
    cli.print("\n📦 Organized Content Display:", style=c.Cli.MessageStyles.CYAN)
    cli.print("\n📊 Summary:", style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        f"  Total Records: {data.get('total', 0)}", style=c.Cli.MessageStyles.CYAN
    )
    cli.print(
        f"  Successful: {data.get('successful', 0)}", style=c.Cli.MessageStyles.GREEN
    )
    cli.print(f"  Failed: {data.get('failed', 0)}", style=c.Cli.MessageStyles.RED)
    cli.print(f"  Pending: {data.get('pending', 0)}", style=c.Cli.MessageStyles.YELLOW)
    details_data: MutableSequence[t.RecursiveContainerMapping] = []
    for key, value in data.items():
        if key not in {"total", "successful", "failed", "pending"}:
            details_data.append({"Property": key, "Value": str(value)})
    if details_data:
        cli.print("\n📋 Details:", style=c.Cli.MessageStyles.BOLD_GREEN)
        cli.show_table(details_data, headers=["Property", "Value"])
    cli.print("\n💡 Status:", style=c.Cli.MessageStyles.BOLD_YELLOW)
    cli.print("✅ All systems operational", style=c.Cli.MessageStyles.GREEN)


def main() -> None:
    """Examples of using output formatting in YOUR code."""
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("  Console Output Library Usage", style=c.Cli.MessageStyles.BOLD_WHITE)
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "\n1. Styled Messages (replace print):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    your_cli_function()
    cli.print("\n2. Rich Tables (display data):", style=c.Cli.MessageStyles.BOLD_CYAN)
    sample_data: Sequence[t.Cli.TableMappingRow] = [
        {"id": 1, "name": "Alice", "status": "active"},
        {"id": 2, "name": "Bob", "status": "inactive"},
    ]
    display_database_results(sample_data)
    cli.print(
        "\n3. ASCII Tables (for logs/reports):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    ascii_result = export_report(sample_data, c.Cli.OutputFormats.TABLE)
    if ascii_result.success:
        cli.print(ascii_result.value, style=c.Cli.MessageStyles.WHITE)
    cli.print(
        "\n4. Progress Bars (long operations):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    items = ["file1", "file2", "file3", "file4"]
    process_large_dataset(items)
    cli.print(
        "\n5. Tree Structures (hierarchies):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    display_project_structure(pathlib.Path.cwd())
    cli.print("\n6. Status Spinners (operations):", style=c.Cli.MessageStyles.BOLD_CYAN)
    process_with_status("Data Migration")
    cli.print(
        "\n7. Live Updates (real-time monitoring):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    monitor_live_metrics()
    cli.print("\n8. Panels (organized content):", style=c.Cli.MessageStyles.BOLD_CYAN)
    panel_data: t.RecursiveContainerMapping = {
        "total": 1250,
        "successful": 1100,
        "failed": 50,
        "pending": 100,
        "start_time": "2025-10-08 10:00:00",
        "end_time": "2025-10-08 11:30:00",
        "duration": "1h 30m",
    }
    display_with_panels(panel_data)
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("  ✅ Output Examples Complete", style=c.Cli.MessageStyles.BOLD_GREEN)
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n💡 Integration Tips:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "  • Rich tables: Use cli.show_table() for terminal display",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • ASCII tables: Use cli.format_table() for logs/files",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Progress: Use cli.print() with percentage updates",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Status: Use cli.print() with status messages",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Tables: Use cli.show_table() for auto-refreshing data",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Organization: Use cli.print() with sections",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • All methods return r for error handling", style=c.Cli.MessageStyles.WHITE
    )
    cli.print(
        "  • NEVER import rich/click/tabulate directly - use cli!",
        style=c.Cli.MessageStyles.WHITE,
    )


def advanced_output_example() -> None:
    """Demonstrate advanced output formatting with Python 3.13+ patterns.

    Shows how to use:
    - StrEnum for format validation
    - collections.abc.Mapping for configuration
    - Advanced Literal unions
    - Type-safe data structures
    """
    cli.print(
        "\n=== Advanced Output Formatting ===", style=c.Cli.MessageStyles.BOLD_BLUE
    )
    output_format: c.Cli.OutputFormats = c.Cli.OutputFormats.TABLE
    cli.print(f"Using format: {output_format}", style=c.Cli.MessageStyles.CYAN)
    sample_data: t.Cli.TableRows = (
        {"name": "Alice", "age": 30, "role": "developer"},
        {"name": "Bob", "age": 25, "role": "designer"},
        {"name": "Charlie", "age": 35, "role": "manager"},
    )
    valid_formats: tuple[str, ...] = tuple(sorted(c.Cli.OUTPUT_FORMATS))
    cli.print(
        f"Supported formats: {', '.join(valid_formats)}",
        style=c.Cli.MessageStyles.GREEN,
    )
    cli.show_table(list(sample_data), headers=["Name", "Age", "Role"])


if __name__ == "__main__":
    main()
    advanced_output_example()
