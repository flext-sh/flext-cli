#!/usr/bin/env python3
"""03 - Data Processing and Output Formatting.

This example demonstrates data processing capabilities and output formatting
using flext-cli patterns:

Key Patterns Demonstrated:
- Data transformation and aggregation using flext-cli utilities
- Multiple output formats (JSON, YAML, CSV, Rich tables)
- File operations with type-safe paths (ExistingFile, NewFile, ExistingDir)
- Formatter factory pattern for consistent output formatting
- Data validation and processing with FlextResult pattern
- Batch processing and data export functionality

Architecture Layers:
- Application: Data processing commands with various output formats
- Service: Data transformation and aggregation services
- Infrastructure: File I/O operations and formatting systems

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from flext_core import FlextResult
from rich.console import Console
from rich.panel import Panel

from flext_cli import (
    ExistingDir,
    ExistingFile,
    FormatterFactory,
    NewFile,
    PlainFormatter,
    cli_batch_process_files,
    cli_create_table,
    cli_enhanced,
    cli_load_data_file,
    cli_measure_time,
    cli_save_data_file,
    flext_cli_aggregate_data,
    flext_cli_export,
    flext_cli_format,
    flext_cli_transform_data,
)


def demonstrate_data_transformation() -> FlextResult[None]:
    """Demonstrate data transformation using flext-cli utilities."""
    console = Console()
    console.print("[bold blue]Data Transformation with FLEXT-CLI[/bold blue]")

    # Sample raw data
    raw_data = [
        {"name": "Service A", "status": "running", "cpu": 45, "memory": 1200, "region": "us-east"},
        {"name": "Service B", "status": "stopped", "cpu": 0, "memory": 0, "region": "us-west"},
        {"name": "Service C", "status": "running", "cpu": 78, "memory": 2100, "region": "us-east"},
        {"name": "Service D", "status": "running", "cpu": 23, "memory": 800, "region": "eu-west"},
        {"name": "Service E", "status": "failed", "cpu": 0, "memory": 0, "region": "us-east"},
    ]

    console.print("\n[green]1. Basic Data Transformation[/green]")

    # Transform data - filter only running services
    filter_result = flext_cli_transform_data(
        raw_data,
        lambda data: [service for service in data if service["status"] == "running"]
    )

    if filter_result.success:
        running_services = filter_result.unwrap()
        console.print(f"✅ Filtered to {len(running_services)} running services")

        # Transform data - add computed fields
        enrich_result = flext_cli_transform_data(
            running_services,
            lambda data: [
                {
                    **service,
                    "health_score": min(100, max(0, 100 - service["cpu"])),
                    "memory_gb": round(service["memory"] / 1024, 1),
                    "efficiency": round((100 - service["cpu"]) * service["memory"] / 1000, 2)
                }
                for service in data
            ]
        )

        if enrich_result.success:
            enriched_services = enrich_result.unwrap()
            console.print("✅ Added computed fields: health_score, memory_gb, efficiency")

            # Display first enriched service as example
            if enriched_services:
                sample = enriched_services[0]
                console.print(f"   Sample: {sample['name']} - Health: {sample['health_score']}, "
                            f"Memory: {sample['memory_gb']}GB, Efficiency: {sample['efficiency']}")

            return FlextResult.ok(enriched_services)

    return FlextResult.fail("Data transformation failed")


def demonstrate_data_aggregation() -> FlextResult[None]:
    """Demonstrate data aggregation patterns."""
    console = Console()
    console.print("\n[green]2. Data Aggregation Patterns[/green]")

    # Sample metrics data
    metrics_data = [
        {"timestamp": "2025-01-15T10:00:00", "service": "api", "requests": 150, "errors": 2},
        {"timestamp": "2025-01-15T10:00:00", "service": "auth", "requests": 75, "errors": 0},
        {"timestamp": "2025-01-15T10:00:00", "service": "db", "requests": 200, "errors": 1},
        {"timestamp": "2025-01-15T11:00:00", "service": "api", "requests": 180, "errors": 3},
        {"timestamp": "2025-01-15T11:00:00", "service": "auth", "requests": 90, "errors": 1},
        {"timestamp": "2025-01-15T11:00:00", "service": "db", "requests": 240, "errors": 0},
    ]

    # Aggregate by service
    service_agg_result = flext_cli_aggregate_data(
        metrics_data,
        group_by="service",
        aggregations={
            "total_requests": lambda group: sum(item["requests"] for item in group),
            "total_errors": lambda group: sum(item["errors"] for item in group),
            "avg_requests": lambda group: round(sum(item["requests"] for item in group) / len(group), 1),
            "error_rate": lambda group: round(
                sum(item["errors"] for item in group) / sum(item["requests"] for item in group) * 100, 2
            ) if sum(item["requests"] for item in group) > 0 else 0.0
        }
    )

    if service_agg_result.success:
        service_stats = service_agg_result.unwrap()
        console.print("✅ Service aggregation completed:")

        for service, stats in service_stats.items():
            console.print(f"   {service}: {stats['total_requests']} requests, "
                        f"{stats['error_rate']}% error rate")

        return FlextResult.ok(service_stats)

    return FlextResult.fail("Data aggregation failed")


@cli_enhanced
@cli_measure_time
def demonstrate_output_formatting() -> FlextResult[None]:
    """Demonstrate various output formatting options."""
    console = Console()
    console.print("\n[green]3. Output Formatting Patterns[/green]")

    # Sample structured data
    sample_data = {
        "application": "flext-demo",
        "version": "1.2.3",
        "environment": "production",
        "services": [
            {"name": "api-gateway", "port": 8080, "healthy": True},
            {"name": "auth-service", "port": 8081, "healthy": True},
            {"name": "database", "port": 5432, "healthy": False},
        ],
        "metrics": {
            "uptime": "99.9%",
            "requests_per_second": 1250,
            "error_rate": "0.1%"
        }
    }

    # 1. JSON formatting
    json_result = flext_cli_format(sample_data, format_type="json")
    if json_result.success:
        console.print("✅ JSON format generated")
        # Show first few lines of JSON
        json_lines = json_result.unwrap().split("\n")[:3]
        for line in json_lines:
            console.print(f"   {line}")
        console.print("   ... (truncated)")

    # 2. Using FormatterFactory
    formatter_factory = FormatterFactory()

    # Get JSON formatter
    json_formatter = formatter_factory.get_formatter("json")
    json_format_result = json_formatter.format(sample_data)
    if json_format_result.success:
        console.print("✅ FormatterFactory JSON formatting successful")

    # Get plain text formatter
    plain_formatter = PlainFormatter()
    plain_result = plain_formatter.format(sample_data)
    if plain_result.success:
        console.print("✅ Plain text formatting successful")

    # 3. Rich table creation for services
    services_table_result = cli_create_table(
        data=sample_data["services"],
        title="Application Services",
        columns=["name", "port", "healthy"]
    )

    if services_table_result.success:
        console.print("✅ Rich table created for services:")
        table = services_table_result.unwrap()
        console.print(table)

    return FlextResult.ok(None)


def demonstrate_file_operations() -> FlextResult[None]:
    """Demonstrate file operations with type-safe paths."""
    console = Console()
    console.print("\n[green]4. File Operations with Type Safety[/green]")

    # Sample configuration data
    config_data = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "database": "flext_demo",
            "username": "REDACTED_LDAP_BIND_PASSWORD"
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8080,
            "debug": False,
            "cors_enabled": True
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "/var/log/flext-demo.log"
        }
    }

    try:
        # 1. Save configuration to temporary file
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        save_result = cli_save_data_file(
            data=config_data,
            file_path=temp_path,
            format_type="json"
        )

        if save_result.success:
            console.print(f"✅ Configuration saved to: {temp_path}")

            # 2. Validate file exists and load it back
            if temp_path.exists():
                existing_file = ExistingFile(str(temp_path))
                console.print(f"✅ File validated as existing: {existing_file}")

                # Load data back
                load_result = cli_load_data_file(
                    file_path=temp_path,
                    format_type="json"
                )

                if load_result.success:
                    loaded_data = load_result.unwrap()
                    console.print("✅ Configuration loaded successfully")
                    console.print(f"   Database host: {loaded_data['database']['host']}")
                    console.print(f"   API port: {loaded_data['api']['port']}")

        # 3. Demonstrate directory operations
        current_dir = ExistingDir(".")
        console.print(f"✅ Current directory validated: {current_dir}")

        # 4. Prepare new file path
        new_config_path = temp_path.parent / "new_config.yaml"
        new_file = NewFile(str(new_config_path))
        console.print(f"✅ New file path prepared: {new_file}")

        # Clean up temporary file
        temp_path.unlink(missing_ok=True)
        console.print("✅ Temporary file cleaned up")

    except Exception as e:
        return FlextResult.fail(f"File operations failed: {e}")

    return FlextResult.ok(None)


def demonstrate_batch_processing() -> FlextResult[None]:
    """Demonstrate batch processing capabilities."""
    console = Console()
    console.print("\n[green]5. Batch Processing Capabilities[/green]")

    try:
        # Create temporary directory with sample files
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create sample text files
            sample_files = []
            for i in range(3):
                file_path = temp_path / f"sample_{i}.txt"
                file_path.write_text(f"Sample content for file {i}\nLine 2\nLine 3")
                sample_files.append(file_path)

            console.print(f"✅ Created {len(sample_files)} sample files")

            # Process files in batch
            batch_result = cli_batch_process_files(
                input_directory=temp_path,
                file_pattern="*.txt",
                processor=lambda file: f"Processed: {file.name} ({file.stat().st_size} bytes)"
            )

            if batch_result.success:
                results = batch_result.unwrap()
                console.print(f"✅ Batch processing completed: {len(results)} files processed")

                for result in results:
                    console.print(f"   {result}")

                return FlextResult.ok(results)

    except Exception as e:
        return FlextResult.fail(f"Batch processing failed: {e}")

    return FlextResult.fail("Batch processing not completed")


def demonstrate_data_export() -> FlextResult[None]:
    """Demonstrate data export functionality."""
    console = Console()
    console.print("\n[green]6. Data Export Functionality[/green]")

    # Sample report data
    report_data = [
        {
            "date": "2025-01-15",
            "service": "api-gateway",
            "requests": 15240,
            "response_time_ms": 45,
            "errors": 12,
            "uptime": 99.8
        },
        {
            "date": "2025-01-15",
            "service": "auth-service",
            "requests": 8750,
            "response_time_ms": 28,
            "errors": 2,
            "uptime": 100.0
        },
        {
            "date": "2025-01-15",
            "service": "database",
            "requests": 23100,
            "response_time_ms": 15,
            "errors": 0,
            "uptime": 100.0
        }
    ]

    # Export to JSON (as string)
    json_export_result = flext_cli_export(
        report_data,
        format_type="json",
        output_file=None  # Return as string
    )

    if json_export_result.success:
        json_output = json_export_result.unwrap()
        console.print("✅ JSON export completed")
        # Show first few characters
        console.print(f"   Preview: {json_output[:100]}...")

    # Export to CSV format
    csv_export_result = flext_cli_export(
        report_data,
        format_type="csv",
        output_file=None
    )

    if csv_export_result.success:
        csv_output = csv_export_result.unwrap()
        console.print("✅ CSV export completed")
        # Show first line (headers)
        csv_lines = csv_output.split("\n")
        if csv_lines:
            console.print(f"   Headers: {csv_lines[0]}")

    return FlextResult.ok(None)


def main() -> None:
    """Main demonstration function."""
    console = Console()

    console.print(Panel(
        "[bold cyan]03 - Data Processing and Output Formatting[/bold cyan]\n\n"
        "[yellow]Comprehensive demonstration of flext-cli data processing capabilities:[/yellow]\n"
        "• Data transformation and filtering\n"
        "• Aggregation and statistical analysis\n"
        "• Multiple output formats (JSON, YAML, CSV, Rich tables)\n"
        "• Type-safe file operations\n"
        "• Batch processing workflows\n"
        "• Data export and formatting patterns",
        expand=False
    ))

    try:
        # Run all demonstrations
        transform_result = demonstrate_data_transformation()
        if transform_result.failure:
            console.print(f"[red]Transformation demo failed: {transform_result.error}[/red]")

        aggregate_result = demonstrate_data_aggregation()
        if aggregate_result.failure:
            console.print(f"[red]Aggregation demo failed: {aggregate_result.error}[/red]")

        format_result = demonstrate_output_formatting()
        if format_result.failure:
            console.print(f"[red]Formatting demo failed: {format_result.error}[/red]")

        file_result = demonstrate_file_operations()
        if file_result.failure:
            console.print(f"[red]File operations demo failed: {file_result.error}[/red]")

        batch_result = demonstrate_batch_processing()
        if batch_result.failure:
            console.print(f"[red]Batch processing demo failed: {batch_result.error}[/red]")

        export_result = demonstrate_data_export()
        if export_result.failure:
            console.print(f"[red]Data export demo failed: {export_result.error}[/red]")

        # Final summary
        console.print(Panel(
            "[bold green]✅ Data Processing and Output Demo Completed![/bold green]\n\n"
            "[cyan]Key Features Demonstrated:[/cyan]\n"
            "🔄 Data transformation with flext_cli_transform_data\n"
            "📊 Aggregation patterns with flext_cli_aggregate_data\n"
            "🎨 Multiple output formats (JSON, CSV, Rich tables)\n"
            "📁 Type-safe file operations (ExistingFile, NewFile, ExistingDir)\n"
            "⚡ Batch processing with cli_batch_process_files\n"
            "📤 Data export with flext_cli_export\n"
            "🏭 FormatterFactory pattern for consistent formatting\n\n"
            "[yellow]All operations used FlextResult pattern for error handling![/yellow]",
            expand=False
        ))

    except Exception as e:
        console.print(f"[bold red]❌ Demo error: {e}[/bold red]")


if __name__ == "__main__":
    main()
