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
- cli.formatters.print() - Styled text output (uses Rich)
- cli.create_table() - Rich tables with borders/colors
- FlextCliTables - ASCII tables for plain text (uses Tabulate)
- Progress bars and spinners
- Tree structures for hierarchical data
- Rich Status - Spinning status indicators
- Rich Live - Auto-refreshing displays
- Rich Panel - Bordered content boxes

HOW TO USE IN YOUR CLI:
Replace print() with cli.formatters.print() for styled output
Use cli.create_table() to display your data
Use Status() for operation spinners
Use Live() for auto-updating displays
Use Panel() for organized content

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pathlib
import time
from pathlib import Path
from typing import cast

from flext_core import FlextCore

from flext_cli import FlextCli, FlextCliTables
from flext_cli.typings import FlextCliTypes

cli = FlextCli.get_instance()
tables = FlextCliTables()


# ============================================================================
# PATTERN 1: Styled console messages in YOUR CLI
# ============================================================================


def your_cli_function() -> None:
    """Replace print() with styled output in your functions."""
    # Instead of: print("Success")
    cli.formatters.print("✅ Operation successful!", style="green")

    # Instead of: print("ERROR: Failed")
    cli.formatters.print("❌ ERROR: Operation failed", style="bold red")

    # Instead of: print("Warning: Check this")
    cli.formatters.print("⚠️  WARNING: Please check this", style="yellow")

    # Info messages
    cli.formatters.print("ℹ️  Processing 100 records...", style="cyan")


# ============================================================================
# PATTERN 2: Display YOUR data as Rich tables
# ============================================================================


def display_database_results(records: list[dict]) -> None:
    """Display database query results as a table."""
    if not records:
        cli.formatters.print("No results found", style="yellow")
        return

    # Convert your data to table
    # Example: records from SQLAlchemy, MongoDB, etc.
    first_record = records[0]
    list(first_record.keys())

    # For dict data, convert to table format
    table_data: FlextCliTypes.Data.CliDataDict = cast(
        "FlextCliTypes.Data.CliDataDict",
        {
            f"Row {i}": " | ".join(str(v) for v in record.values())
            for i, record in enumerate(records[:10], 1)
        },
    )

    table_result = cli.create_table(
        data=table_data,
        headers=["#", "Data"],
        title=f"Query Results ({len(records)} total)",
    )

    if table_result.is_success:
        cli.formatters.console.print(table_result.unwrap())


# ============================================================================
# PATTERN 3: ASCII tables for plain text output
# ============================================================================


def export_report(data: list[dict], format_type: str = "grid") -> str | None:
    """Create ASCII tables for logs/reports in your app."""
    # Good for: log files, email reports, markdown docs

    # Grid format (default)
    if format_type == "grid":
        result = tables.create_table(data, table_format="grid")

    # Markdown format (for README files, docs)
    elif format_type == "pipe":
        result = tables.create_table(data, table_format="pipe")

    # Simple format (minimal)
    else:
        result = tables.create_table(data, table_format="simple")

    if result.is_success:
        return result.unwrap()  # Returns string you can save to file
    return None


# ============================================================================
# PATTERN 4: Progress bars for YOUR long operations
# ============================================================================


def process_large_dataset(items: list) -> None:
    """Process items with progress updates."""
    cli.formatters.print("Processing items...", style="cyan")

    total = len(items)
    for i in range(1, len(items) + 1):
        # Your actual processing code here
        time.sleep(0.01)  # Simulate work
        # process_item(items[i-1])

        # Show progress updates
        if i % 10 == 0 or i == total:
            percentage = int((i / total) * 100)
            cli.formatters.print(
                f"Progress: {i}/{total} items ({percentage}%)", style="yellow"
            )

    cli.formatters.print("✅ All items processed!", style="green")


# ============================================================================
# PATTERN 5: Tree structures for YOUR hierarchical data
# ============================================================================


def display_project_structure(root_path: str | Path) -> None:
    """Display directory tree or any hierarchical data."""
    tree_result = cli.create_tree(f"📁 {Path(root_path).name}")

    if tree_result.is_success:
        tree = tree_result.unwrap()

        # Add your items to the tree
        # Example: file system, org chart, data hierarchy
        for item in Path(root_path).iterdir():
            if item.is_dir():
                tree.add(f"📂 {item.name}/")
            else:
                tree.add(f"📄 {item.name}")

        cli.formatters.console.print(tree)


# ============================================================================
# PATTERN 6: Status spinners for YOUR operations
# ============================================================================


def process_with_status(operation_name: str) -> None:
    """Show spinning status indicator during operations."""
    cli.formatters.print(f"\n🔄 Starting: {operation_name}", style="cyan")

    # Your operation stages
    stages = [
        ("Initializing...", 0.5),
        ("Connecting to database...", 1.0),
        ("Fetching records...", 1.5),
        ("Processing data...", 1.0),
        ("Saving results...", 0.8),
    ]

    for stage_name, duration in stages:
        cli.formatters.print(f"⏳ {stage_name}", style="yellow")
        time.sleep(duration)  # Replace with your actual work
        cli.formatters.print(f"✅ {stage_name} completed", style="green")

    cli.formatters.print("🎉 Operation completed successfully!", style="bold green")


# ============================================================================
# PATTERN 7: Live-updating displays for YOUR data
# ============================================================================


def monitor_live_metrics() -> None:
    """Display periodic metrics updates for your application."""
    cli.formatters.print("\n📊 Starting monitoring...", style="cyan")

    # Run monitoring for a few updates
    for i in range(5):
        # Simulate changing metrics from YOUR application
        cpu = 45 + (i % 40)
        memory = 55 + (i % 35)
        requests = 150 + (i * 10)

        # Create metrics data as ASCII table using FlextCliTables
        metrics_data: list[FlextCore.Types.Dict] = [
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

        # Display using ASCII table (FlextCliTables handles list[dict])
        table_result = tables.create_table(metrics_data, table_format="grid")

        if table_result.is_success:
            cli.formatters.print(f"\n{table_result.unwrap()}", style="white")
        else:
            cli.formatters.print(
                f"Failed to create table: {table_result.error}", style="red"
            )

        time.sleep(1.0)

    cli.formatters.print("✅ Monitoring session complete", style="green")


# ============================================================================
# PATTERN 8: Panels for organized content in YOUR CLI
# ============================================================================


def display_with_panels(data: dict) -> None:
    """Display content in organized sections."""
    cli.formatters.print("\n📦 Organized Content Display:", style="cyan")

    # Section 1: Summary information
    cli.formatters.print("\n📊 Summary:", style="bold blue")
    cli.formatters.print(f"  Total Records: {data.get('total', 0)}", style="cyan")
    cli.formatters.print(f"  Successful: {data.get('successful', 0)}", style="green")
    cli.formatters.print(f"  Failed: {data.get('failed', 0)}", style="red")
    cli.formatters.print(f"  Pending: {data.get('pending', 0)}", style="yellow")

    # Section 2: Details table
    details_data = []
    for key, value in data.items():
        if key not in {"total", "successful", "failed", "pending"}:
            details_data.append({"Property": key, "Value": str(value)})

    if details_data:
        cli.formatters.print("\n📋 Details:", style="bold green")
        # Use FlextCliTables for list[dict] data
        table_result = tables.create_table(details_data, table_format="grid")
        if table_result.is_success:
            cli.formatters.print(f"\n{table_result.unwrap()}", style="white")

    # Section 3: Status message
    cli.formatters.print("\n💡 Status:", style="bold yellow")
    cli.formatters.print("✅ All systems operational", style="green")


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of using output formatting in YOUR code."""
    cli.formatters.print("=" * 70, style="bold blue")
    cli.formatters.print("  Console Output Library Usage", style="bold white")
    cli.formatters.print("=" * 70, style="bold blue")

    # Example 1: Styled messages
    cli.formatters.print("\n1. Styled Messages (replace print):", style="bold cyan")
    your_cli_function()

    # Example 2: Rich tables
    cli.formatters.print("\n2. Rich Tables (display data):", style="bold cyan")
    sample_data = [
        {"id": 1, "name": "Alice", "status": "active"},
        {"id": 2, "name": "Bob", "status": "inactive"},
    ]
    display_database_results(sample_data)

    # Example 3: ASCII tables
    cli.formatters.print("\n3. ASCII Tables (for logs/reports):", style="bold cyan")
    ascii_table = export_report(sample_data, "grid")
    if ascii_table:
        print(ascii_table)  # This is plain text - can save to file

    # Example 4: Progress bars
    cli.formatters.print("\n4. Progress Bars (long operations):", style="bold cyan")
    items = ["file1", "file2", "file3", "file4"]
    process_large_dataset(items)

    # Example 5: Tree structures
    cli.formatters.print("\n5. Tree Structures (hierarchies):", style="bold cyan")
    display_project_structure(pathlib.Path.cwd())

    # Example 6: Status spinners
    cli.formatters.print("\n6. Status Spinners (operations):", style="bold cyan")
    process_with_status("Data Migration")

    # Example 7: Live-updating displays
    cli.formatters.print("\n7. Live Updates (real-time monitoring):", style="bold cyan")
    monitor_live_metrics()

    # Example 8: Panels for organization
    cli.formatters.print("\n8. Panels (organized content):", style="bold cyan")
    panel_data = {
        "total": 1250,
        "successful": 1100,
        "failed": 50,
        "pending": 100,
        "start_time": "2025-10-08 10:00:00",
        "end_time": "2025-10-08 11:30:00",
        "duration": "1h 30m",
    }
    display_with_panels(panel_data)

    cli.formatters.print("\n" + "=" * 70, style="bold blue")
    cli.formatters.print("  ✅ Output Examples Complete", style="bold green")
    cli.formatters.print("=" * 70, style="bold blue")

    # Integration guide
    cli.formatters.print("\n💡 Integration Tips:", style="bold cyan")
    cli.formatters.print(
        "  • Rich tables: Use cli.create_table() for terminal display", style="white"
    )
    cli.formatters.print(
        "  • ASCII tables: Use FlextCliTables for logs/files", style="white"
    )
    cli.formatters.print(
        "  • Progress: Use cli.formatters.print() with percentage updates",
        style="white",
    )
    cli.formatters.print(
        "  • Status: Use cli.formatters.print() with status messages", style="white"
    )
    cli.formatters.print(
        "  • Tables: Use cli.create_table() for auto-refreshing data", style="white"
    )
    cli.formatters.print(
        "  • Organization: Use cli.formatters.print() with sections", style="white"
    )
    cli.formatters.print(
        "  • All methods return FlextCore.Result for error handling", style="white"
    )
    cli.formatters.print(
        "  • NEVER import rich/click/tabulate directly - use FlextCli!", style="white"
    )


if __name__ == "__main__":
    main()
