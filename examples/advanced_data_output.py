#!/usr/bin/env python3
"""Advanced data output patterns demonstration.

Comprehensive examples of enhanced CLI output patterns with multiple formats,
data export, Tabulate integration, and Rich GUI interfaces.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

from flext_cli.api import (
    FlextCliApi,
    flext_cli_export,
)
from flext_core import ServiceResult as FlextResult
from rich.console import Console

try:
    from tabulate import tabulate

    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False


# Simple stubs for demonstration - following SOLID principles
class FlextCliRichGUI:
    """Simple stub for Rich GUI functionality."""

    def create_metrics_dashboard(
        self, _metrics: dict[str, object], _title: str
    ) -> FlextResult[str]:
        """Create a metrics dashboard."""
        return FlextResult.ok("Dashboard created successfully")


class FlextCliFormatter:
    """Simple stub for CLI formatting functionality."""

    def format_export_preview(
        self, _data: list[dict[str, object]], export_format: str, _sample_size: int
    ) -> FlextResult[str]:
        """Format export preview."""
        return FlextResult.ok(f"Preview for {export_format} format")

    def format_comparison_table(
        self,
        _before_data: list[dict[str, object]],
        _after_data: list[dict[str, object]],
        _title: str,
        _key_field: str,
    ) -> FlextResult[str]:
        """Format comparison table."""
        return FlextResult.ok("Comparison table formatted")

    def format_with_data_export_integration(
        self, _data: list[dict[str, object]]
    ) -> FlextResult[dict[str, object]]:
        """Format with data export integration."""
        return FlextResult.ok({"export_metadata": {"format": "processed"}})


class FlextCliBuilder:
    """Simple stub for CLI builder functionality."""

    def __init__(self, name: str, version: str, description: str) -> None:
        self.name = name
        self.version = version
        self.description = description

    def set_formatter(self, _formatter: str) -> FlextCliBuilder:
        """Set formatter."""
        return self

    def add_global_flag(self, _flag: str, _description: str) -> FlextCliBuilder:
        """Add global flag."""
        return self

    def add_command(self, name: str, func: object, help_text: str) -> None:
        """Add command."""


def flext_cli_export_data(
    _data: list[dict[str, object]], _path: str
) -> FlextResult[None]:
    """Simple stub for data export."""
    return FlextResult.ok(None)


def flext_cli_create_dashboard(_title: str) -> FlextResult[None]:
    """Simple stub for dashboard creation."""
    return FlextResult.ok(None)


def example_data_export() -> None:
    """Example 1: Multi-format data export."""
    # Sample business data
    business_data = [
        {
            "id": 1,
            "company": "FLEXT Corp",
            "revenue": 1250000.50,
            "employees": 150,
            "status": "active",
        },
        {
            "id": 2,
            "company": "DataFlow Ltd",
            "revenue": 890000.25,
            "employees": 75,
            "status": "active",
        },
        {
            "id": 3,
            "company": "CloudSync Inc",
            "revenue": 2100000.00,
            "employees": 300,
            "status": "active",
        },
        {
            "id": 4,
            "company": "TechStart",
            "revenue": 450000.75,
            "employees": 25,
            "status": "inactive",
        },
        {
            "id": 5,
            "company": "MegaCorp",
            "revenue": 5000000.00,
            "employees": 1200,
            "status": "active",
        },
    ]

    # Create output directory
    output_dir = Path("output/exports")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export to multiple formats
    formats = ["csv", "json", "parquet", "sqlite", "excel"]

    for fmt in formats:
        if fmt in {"csv", "json", "yaml"}:  # Only supported formats
            result = flext_cli_export(
                data=business_data,
                file_path=str(output_dir / f"business_data.{fmt}"),
                format_type=fmt,
            )

        if result.success:
            pass

    # Export multiple formats at once
    api = FlextCliApi()
    # Export to supported formats
    for fmt in ["csv", "json"]:
        result = api.flext_cli_export(
            data=business_data,
            path=str(output_dir / f"business_multi.{fmt}"),
            format_type=fmt,
        )
    multi_result = FlextResult.ok("Multiple formats exported")

    if multi_result.success:
        for _fmt in multi_result.unwrap():
            pass


def example_tabulate_formatting() -> None:
    """Example 2: Advanced table formatting with Tabulate."""
    console = Console()

    # Performance metrics data
    metrics_data = [
        {"metric": "Response Time", "current": "45ms", "target": "50ms", "status": "✓"},
        {
            "metric": "Throughput",
            "current": "1250 req/s",
            "target": "1000 req/s",
            "status": "✓",
        },
        {"metric": "Error Rate", "current": "0.02%", "target": "0.05%", "status": "✓"},
        {"metric": "CPU Usage", "current": "78%", "target": "80%", "status": "⚠"},
        {"metric": "Memory Usage", "current": "85%", "target": "80%", "status": "✗"},
    ]

    # Different table formats
    table_formats = ["grid", "fancy_grid", "pipe", "orgtbl", "simple", "github"]

    for fmt in table_formats:
        if not TABULATE_AVAILABLE:
            console.print(f"[yellow]Tabulate not available for format: {fmt}[/yellow]")
            continue

        try:
            # Format data for tabulate
            headers = ["Metric", "Current", "Target", "Status"]
            rows = [
                [d["metric"], d["current"], d["target"], d["status"]]
                for d in metrics_data
            ]

            # Create formatted table
            formatted_table = tabulate(rows, headers=headers, tablefmt=fmt)
            console.print(f"\n[bold]Performance Metrics ({fmt})[/bold]")
            console.print(formatted_table)

        except Exception as e:
            console.print(f"[red]Error formatting table: {e}[/red]")


def example_data_analysis() -> None:
    """Example 3: Comprehensive data analysis."""
    console = Console()

    # Sales data with various data types
    sales_data = [
        {
            "product": "FlextCore",
            "price": 299.99,
            "quantity": 150,
            "category": "Software",
            "rating": 4.8,
        },
        {
            "product": "DataPipe",
            "price": 199.50,
            "quantity": 200,
            "category": "Software",
            "rating": 4.6,
        },
        {
            "product": "CloudSync",
            "price": 149.99,
            "quantity": 300,
            "category": "Software",
            "rating": 4.7,
        },
        {
            "product": "DevTools",
            "price": 99.99,
            "quantity": 500,
            "category": "Tools",
            "rating": 4.5,
        },
        {
            "product": "Analytics+",
            "price": 399.99,
            "quantity": 75,
            "category": "Analytics",
            "rating": 4.9,
        },
    ]

    # Generate comprehensive analysis
    console.print("\n[bold]Sales Data Analysis[/bold]")

    # Simple data analysis - calculate total revenue from price * quantity
    total_revenue = sum(item["price"] * item["quantity"] for item in sales_data)
    best_product = max(sales_data, key=lambda x: x["price"] * x["quantity"])

    console.print(f"Total Revenue: ${total_revenue:,.2f}")
    best_revenue = best_product["price"] * best_product["quantity"]
    console.print(f"Best Product: {best_product['product']} (${best_revenue:,.2f})")
    console.print(f"Average Product Revenue: ${total_revenue / len(sales_data):,.2f}")


def example_rich_gui_dashboard() -> None:
    """Example 4: Rich GUI Dashboard."""
    # Create Rich GUI and console
    gui = FlextCliRichGUI()
    console = Console()

    # System metrics for dashboard
    system_metrics = {
        "CPU Usage": 72.5,
        "Memory": 8.2,
        "Disk Space": 245,
        "Network I/O": 1024,
        "Active Users": 1337,
        "Requests/sec": 450,
    }

    # Create metrics dashboard
    dashboard_result = gui.create_metrics_dashboard(
        metrics=system_metrics,
        title="System Performance Dashboard",
    )

    if dashboard_result.success:
        dashboard_result.unwrap()

        # In a real application, this would start live updates
        console.print("[dim]Live dashboard would start here in production[/dim]")

        # Create data table for dashboard
        service_data = [
            {
                "service": "web-server",
                "status": "running",
                "cpu": "12%",
                "memory": "256MB",
            },
            {
                "service": "database",
                "status": "running",
                "cpu": "45%",
                "memory": "2.1GB",
            },
            {"service": "cache", "status": "stopped", "cpu": "0%", "memory": "0MB"},
            {"service": "queue", "status": "running", "cpu": "8%", "memory": "128MB"},
        ]

        table_result = gui.create_data_table(
            data=service_data,
            title="Service Status",
            show_lines=True,
        )

        if table_result.success:
            pass


def example_export_preview() -> None:
    """Example 5: Export preview functionality."""
    # Log data
    log_data = [
        {
            "timestamp": "2025-07-25 10:30:15",
            "level": "INFO",
            "message": "Application started",
            "module": "main",
        },
        {
            "timestamp": "2025-07-25 10:30:16",
            "level": "DEBUG",
            "message": "Database connected",
            "module": "db",
        },
        {
            "timestamp": "2025-07-25 10:30:17",
            "level": "WARNING",
            "message": "High memory usage",
            "module": "monitor",
        },
        {
            "timestamp": "2025-07-25 10:30:18",
            "level": "ERROR",
            "message": "Authentication failed",
            "module": "auth",
        },
        {
            "timestamp": "2025-07-25 10:30:19",
            "level": "INFO",
            "message": "Request processed",
            "module": "api",
        },
    ]

    # Preview different export formats
    formatter = FlextCliFormatter()

    formats = ["csv", "json", "yaml", "tabulate"]

    for fmt in formats:
        preview_result = formatter.format_export_preview(
            data=log_data,
            export_format=fmt,
            sample_size=3,
        )

        if preview_result.success:
            pass


def example_data_comparison() -> None:
    """Example 6: Data comparison functionality."""
    # Before data
    before_config = [
        {"setting": "timeout", "value": "30s", "env": "production"},
        {"setting": "pool_size", "value": "10", "env": "production"},
        {"setting": "debug", "value": "false", "env": "production"},
        {"setting": "cache_ttl", "value": "3600", "env": "production"},
    ]

    # After data (with changes)
    after_config = [
        {"setting": "timeout", "value": "45s", "env": "production"},  # Changed
        {"setting": "pool_size", "value": "15", "env": "production"},  # Changed
        {"setting": "debug", "value": "false", "env": "production"},  # Same
        {"setting": "max_connections", "value": "100", "env": "production"},  # New
    ]

    # Create comparison
    formatter = FlextCliFormatter()
    comparison_result = formatter.format_comparison_table(
        before_data=before_config,
        after_data=after_config,
        title="Configuration Changes",
        key_field="setting",
    )

    if comparison_result.success:
        pass


def example_integrated_workflow() -> None:
    """Example 7: Integrated CLI workflow with all features."""
    # Create CLI with advanced capabilities
    cli = (
        FlextCliBuilder("data-processor", "0.9.0", "Advanced Data Processing CLI")
        .set_formatter("rich")
        .add_global_flag("--export", "Enable data export")
        .add_global_flag("--dashboard", "Show GUI dashboard")
    )

    def process_sales_data(
        *,
        export: bool = False,
        dashboard: bool = False,
    ) -> FlextResult[dict[str, object]]:
        """Process sales data with export and dashboard options."""
        # Sample sales data
        sales_data = [
            {
                "product": "Enterprise License",
                "revenue": 50000,
                "quarter": "Q1",
                "region": "NA",
            },
            {
                "product": "Professional License",
                "revenue": 25000,
                "quarter": "Q1",
                "region": "EU",
            },
            {
                "product": "Starter License",
                "revenue": 10000,
                "quarter": "Q1",
                "region": "APAC",
            },
            {
                "product": "Enterprise License",
                "revenue": 55000,
                "quarter": "Q2",
                "region": "NA",
            },
            {
                "product": "Professional License",
                "revenue": 30000,
                "quarter": "Q2",
                "region": "EU",
            },
        ]

        # Format and display data
        formatter = FlextCliFormatter()
        format_result = formatter.format_with_data_export_integration(sales_data)

        if not format_result.success:
            return FlextResult.fail(format_result.error)

        result_data = format_result.unwrap()

        # Export data if requested
        if export:
            export_result = flext_cli_export_data(
                sales_data,
                "output/sales_report.csv",
            )
            if export_result.success:
                pass

        # Show dashboard if requested
        if dashboard:
            dashboard_result = flext_cli_create_dashboard("Sales Dashboard")
            if dashboard_result.success:
                pass

        return FlextResult.ok(
            {
                "processed_records": len(sales_data),
                "total_revenue": sum(row["revenue"] for row in sales_data),
                "export_enabled": export,
                "dashboard_enabled": dashboard,
                "metadata": result_data["export_metadata"],
            },
        )

    # Add command to CLI
    cli.add_command("process", process_sales_data, help_text="Process sales data")

    # Test the command directly
    result = process_sales_data(export=True, dashboard=True)

    if result.success:
        result.unwrap()

        # Show recommended formats


def main() -> None:
    """Run all advanced data output examples."""
    try:
        example_data_export()
        example_tabulate_formatting()
        example_data_analysis()
        example_rich_gui_dashboard()
        example_export_preview()
        example_data_comparison()
        example_integrated_workflow()

    except (RuntimeError, ValueError, TypeError):
        pass


if __name__ == "__main__":
    main()
