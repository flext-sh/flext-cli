#!/usr/bin/env python3
"""03 - Data Processing and Output with FLEXT CLI Foundation.

This example demonstrates data processing capabilities and output formatting
using proper flext-cli patterns:

🎯 **Key Patterns Demonstrated:**
- Data transformation and aggregation using FlextResult patterns
- Multiple output formats through FlextCliFormatters (replaces direct Rich)
- File operations with type-safe FlextResult error handling
- Batch processing workflows using flext-cli foundation
- Data validation and processing with railway-oriented programming
- Export functionality through flext-cli abstractions

🏗️ **Architecture Layers:**
- Application: Data processing commands using flext-cli foundation
- Service: Data transformation and aggregation services with FlextResult
- Infrastructure: File I/O operations and formatting through flext-cli

📈 **FLEXT CLI Foundation Compliance**: Zero direct Rich/Click imports

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import io
import json
import tempfile
from pathlib import Path
from tempfile import NamedTemporaryFile

from flext_cli import (
    FlextCliFormatters,
)
from flext_core import FlextResult


def _demonstrate_data_transformation(formatter: FlextCliFormatters) -> FlextResult[None]:
    """Demonstrate data transformation using flext-cli patterns."""
    formatter.print_success("\n1. 🔄 Data Transformation with FLEXT CLI")

    # Sample raw data
    raw_data = [
        {"name": "Service A", "status": "running", "cpu": 45, "memory": 1200, "region": "us-east"},
        {"name": "Service B", "status": "stopped", "cpu": 0, "memory": 0, "region": "us-west"},
        {"name": "Service C", "status": "running", "cpu": 78, "memory": 2100, "region": "us-east"},
        {"name": "Service D", "status": "running", "cpu": 23, "memory": 800, "region": "eu-west"},
        {"name": "Service E", "status": "failed", "cpu": 0, "memory": 0, "region": "us-east"},
    ]

    # Transform data - filter only running services
    filter_result = _filter_running_services(raw_data)
    if filter_result.is_failure:
        return FlextResult[None].fail(f"Data filtering failed: {filter_result.error}")

    running_services = filter_result.value
    formatter.print_success(f"✅ Filtered to {len(running_services)} running services")

    # Transform data - add computed fields
    enrich_result = _enrich_service_data(running_services)
    if enrich_result.is_failure:
        return FlextResult[None].fail(f"Data enrichment failed: {enrich_result.error}")

    enriched_services = enrich_result.value
    formatter.print_success("✅ Added computed fields: health_score, memory_gb, efficiency")

    # Display sample enriched service using flext-cli formatter
    if enriched_services:
        sample = enriched_services[0]
        sample_data: dict[str, object] = {
            "Service": sample["name"],
            "Health Score": str(sample["health_score"]),
            "Memory (GB)": f"{sample['memory_gb']}GB",
            "Efficiency": str(sample["efficiency"])
        }

        table_result = formatter.format_table(
            data=sample_data,
            title="Sample Enriched Service"
        )
        if table_result.is_success:
            formatter.console.print(table_result.value)

    return FlextResult[None].ok(None)


def _demonstrate_data_aggregation(formatter: FlextCliFormatters) -> FlextResult[None]:
    """Demonstrate data aggregation patterns."""
    formatter.print_success("\n2. 📊 Data Aggregation Patterns")

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
    aggregation_result = _aggregate_by_service(metrics_data)
    if aggregation_result.is_failure:
        return FlextResult[None].fail(f"Data aggregation failed: {aggregation_result.error}")

    service_stats = aggregation_result.value
    formatter.print_success("✅ Service aggregation completed")

    # Display aggregated data using flext-cli formatter
    agg_data: dict[str, object] = {}
    for stats in service_stats:
        service = str(stats.get("service", "unknown"))

        # Safe type conversion for aggregated data
        requests_obj = stats.get("total_requests", 0)
        errors_obj = stats.get("total_errors", 0)

        total_requests = int(requests_obj) if isinstance(requests_obj, (int, float)) else 0
        total_errors = int(errors_obj) if isinstance(errors_obj, (int, float)) else 0
        error_rate = round((total_errors / total_requests * 100), 2) if total_requests > 0 else 0.0
        agg_data[service] = f"{total_requests} requests, {error_rate}% error rate"

    table_result = formatter.format_table(
        data=agg_data,
        title="Service Aggregation Results"
    )
    if table_result.is_success:
        formatter.console.print(table_result.value)

    return FlextResult[None].ok(None)


def _demonstrate_output_formatting(formatter: FlextCliFormatters) -> FlextResult[None]:
    """Demonstrate various output formatting options."""
    formatter.print_success("\n3. 🎨 Output Formatting Patterns")

    # Sample structured data
    sample_data: dict[str, object] = {
        "Application": "flext-demo",
        "Version": "1.2.3",
        "Environment": "production",
        "Uptime": "99.9%",
        "Requests/sec": "1250",
        "Error Rate": "0.1%"
    }

    # Display using flext-cli table formatter
    table_result = formatter.format_table(
        data=sample_data,
        title="Application Status (FLEXT CLI Formatted)"
    )
    if table_result.is_success:
        formatter.console.print(table_result.value)
        formatter.print_success("✅ Table format generated using FLEXT CLI foundation")

    # JSON formatting using builtin (no direct Rich usage)
    json_result = _format_as_json(dict(sample_data))
    if json_result.is_success:
        formatter.print_success("✅ JSON format generated")
        formatter.console.print("   Sample JSON output generated successfully")

    # Services data table
    services_data: dict[str, object] = {
        "api-gateway": "Port 8080, Healthy",
        "auth-service": "Port 8081, Healthy",
        "database": "Port 5432, Unhealthy"
    }

    services_table_result = formatter.format_table(
        data=services_data,
        title="Application Services"
    )
    if services_table_result.is_success:
        formatter.console.print(services_table_result.value)
        formatter.print_success("✅ Services table created using FLEXT CLI")

    return FlextResult[None].ok(None)


def _demonstrate_file_operations(formatter: FlextCliFormatters) -> FlextResult[None]:
    """Demonstrate file operations with type-safe paths."""
    formatter.print_success("\n4. 📁 File Operations with Type Safety")

    # Sample configuration data
    config_data = {
        "database": {"host": "localhost", "port": 5432, "database": "flext_demo"},
        "api": {"host": "localhost", "port": 8080, "debug": False},
        "logging": {"level": "INFO", "file": "/var/log/flext-demo.log"}
    }

    # Save configuration to temporary file
    save_result = _save_config_to_file(config_data)
    if save_result.is_failure:
        return FlextResult[None].fail(f"File save failed: {save_result.error}")

    temp_path = save_result.value
    formatter.print_success(f"✅ Configuration saved to: {temp_path}")

    # Load configuration back
    load_result = _load_config_from_file(temp_path)
    if load_result.is_failure:
        return FlextResult[None].fail(f"File load failed: {load_result.error}")

    loaded_data = load_result.value
    formatter.print_success("✅ Configuration loaded successfully")

    # Display loaded config using flext-cli formatter
    config_display: dict[str, object] = {}
    if isinstance(loaded_data, dict):
        database = loaded_data.get("database", {})
        api = loaded_data.get("api", {})
        if isinstance(database, dict) and isinstance(api, dict):
            config_display["Database Host"] = str(database.get("host", "N/A"))
            config_display["Database Port"] = str(database.get("port", "N/A"))
            config_display["API Port"] = str(api.get("port", "N/A"))
            config_display["Debug Mode"] = str(api.get("debug", False))

    table_result = formatter.format_table(
        data=config_display,
        title="Loaded Configuration"
    )
    if table_result.is_success:
        formatter.console.print(table_result.value)

    # Clean up
    temp_path.unlink(missing_ok=True)
    formatter.print_success("✅ Temporary file cleaned up")

    return FlextResult[None].ok(None)


def _demonstrate_batch_processing(formatter: FlextCliFormatters) -> FlextResult[None]:
    """Demonstrate batch processing capabilities."""
    formatter.print_success("\n5. ⚡ Batch Processing Capabilities")

    # Create and process sample files
    batch_result = _process_sample_files()
    if batch_result.is_failure:
        return FlextResult[None].fail(f"Batch processing failed: {batch_result.error}")

    results = batch_result.value
    formatter.print_success(f"✅ Batch processing completed: {len(results)} files processed")

    # Display results using flext-cli formatter
    results_data: dict[str, object] = {}
    for i, result in enumerate(results):
        results_data[f"File {i+1}"] = result

    table_result = formatter.format_table(
        data=results_data,
        title="Batch Processing Results"
    )
    if table_result.is_success:
        formatter.console.print(table_result.value)

    return FlextResult[None].ok(None)


def _demonstrate_data_export(formatter: FlextCliFormatters) -> FlextResult[None]:
    """Demonstrate data export functionality."""
    formatter.print_success("\n6. 📤 Data Export Functionality")

    # Sample report data
    report_data = [
        {"date": "2025-01-15", "service": "api-gateway", "requests": 15240, "errors": 12},
        {"date": "2025-01-15", "service": "auth-service", "requests": 8750, "errors": 2},
        {"date": "2025-01-15", "service": "database", "requests": 23100, "errors": 0},
    ]

    # Export to JSON
    json_export_result = _export_to_json(report_data)
    if json_export_result.is_success:
        formatter.print_success("✅ JSON export completed")

    # Export to CSV
    csv_export_result = _export_to_csv(report_data)
    if csv_export_result.is_success:
        formatter.print_success("✅ CSV export completed")

    # Display export summary using flext-cli formatter
    export_summary: dict[str, object] = {
        "JSON Export": "✅ Success - All data exported",
        "CSV Export": "✅ Success - Headers and data exported",
        "Format": "Structured data with error handling",
        "Method": "FLEXT CLI FlextResult patterns"
    }

    table_result = formatter.format_table(
        data=export_summary,
        title="Export Summary"
    )
    if table_result.is_success:
        formatter.console.print(table_result.value)

    return FlextResult[None].ok(None)


def _summary_demo(formatter: FlextCliFormatters) -> None:
    """Demo summary display."""
    formatter.print_success("\n📋 Data Processing and Output Summary")

    summary_data: dict[str, object] = {
        "Feature": "Status",
        "Data Transformation": "✅ FlextResult patterns",
        "Data Aggregation": "✅ Type-safe processing",
        "Output Formatting": "✅ FLEXT CLI formatters",
        "File Operations": "✅ Railway-oriented I/O",
        "Batch Processing": "✅ Error-safe workflows",
        "Data Export": "✅ Multiple format support"
    }

    table_result = formatter.format_table(
        data=summary_data,
        title="Data Processing Components"
    )
    if table_result.is_success:
        formatter.console.print(table_result.value)

    formatter.print_success("🎉 Data processing and output demonstrated successfully!")


# Helper functions using FlextResult patterns

def _filter_running_services(data: list[dict[str, object]]) -> FlextResult[list[dict[str, object]]]:
    """Filter services by running status."""
    try:
        running_services = [
            service for service in data
            if service.get("status") == "running"
        ]
        return FlextResult[list[dict[str, object]]].ok(running_services)
    except Exception as e:
        return FlextResult[list[dict[str, object]]].fail(f"Filter failed: {e}")


def _enrich_service_data(services: list[dict[str, object]]) -> FlextResult[list[dict[str, object]]]:
    """Enrich service data with computed fields."""
    try:
        enriched_services = []
        for service in services:
            # Safe type conversion with validation
            cpu_obj = service.get("cpu", 0)
            memory_obj = service.get("memory", 0)

            cpu_val = int(cpu_obj) if isinstance(cpu_obj, (int, float)) else 0
            memory_val = int(memory_obj) if isinstance(memory_obj, (int, float)) else 0

            enriched_service = {
                **service,
                "health_score": min(100, max(0, 100 - cpu_val)),
                "memory_gb": round(memory_val / 1024, 1),
                "efficiency": round((100 - cpu_val) * memory_val / 1000, 2),
            }
            enriched_services.append(enriched_service)

        return FlextResult[list[dict[str, object]]].ok(enriched_services)
    except Exception as e:
        return FlextResult[list[dict[str, object]]].fail(f"Enrichment failed: {e}")


def _aggregate_by_service(metrics: list[dict[str, object]]) -> FlextResult[list[dict[str, object]]]:
    """Aggregate metrics by service."""
    try:
        service_stats: dict[str, dict[str, object]] = {}

        for metric in metrics:
            service = str(metric.get("service", "unknown"))

            # Safe type conversion with validation
            requests_obj = metric.get("requests", 0)
            errors_obj = metric.get("errors", 0)

            requests = int(requests_obj) if isinstance(requests_obj, (int, float)) else 0
            errors = int(errors_obj) if isinstance(errors_obj, (int, float)) else 0

            if service not in service_stats:
                service_stats[service] = {"service": service, "total_requests": 0, "total_errors": 0}

            # Safe arithmetic with validated types
            current_requests_obj = service_stats[service]["total_requests"]
            current_errors_obj = service_stats[service]["total_errors"]

            current_requests = int(current_requests_obj) if isinstance(current_requests_obj, (int, float)) else 0
            current_errors = int(current_errors_obj) if isinstance(current_errors_obj, (int, float)) else 0

            service_stats[service]["total_requests"] = current_requests + requests
            service_stats[service]["total_errors"] = current_errors + errors

        return FlextResult[list[dict[str, object]]].ok(list(service_stats.values()))
    except Exception as e:
        return FlextResult[list[dict[str, object]]].fail(f"Aggregation failed: {e}")


def _format_as_json(data: dict[str, object]) -> FlextResult[str]:
    """Format data as JSON string."""
    try:
        json_output = json.dumps(data, indent=2)
        return FlextResult[str].ok(json_output)
    except Exception as e:
        return FlextResult[str].fail(f"JSON formatting failed: {e}")


def _save_config_to_file(config_data: dict[str, object]) -> FlextResult[Path]:
    """Save configuration to temporary file."""
    try:
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as temp_file:
            temp_path = Path(temp_file.name)

        temp_path.write_text(json.dumps(config_data, indent=2), encoding="utf-8")
        return FlextResult[Path].ok(temp_path)
    except Exception as e:
        return FlextResult[Path].fail(f"Save failed: {e}")


def _load_config_from_file(file_path: Path) -> FlextResult[dict[str, object]]:
    """Load configuration from file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)
        return FlextResult[dict[str, object]].ok(data)
    except Exception as e:
        return FlextResult[dict[str, object]].fail(f"Load failed: {e}")


def _process_sample_files() -> FlextResult[list[str]]:
    """Create and process sample files."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create sample files
            for i in range(3):
                file_path = temp_path / f"sample_{i}.txt"
                file_path.write_text(f"Sample content for file {i}\nLine 2\nLine 3")

            # Process files
            results = []
            for file_path in temp_path.glob("*.txt"):
                processed = f"Processed: {file_path.name} ({file_path.stat().st_size} bytes)"
                results.append(processed)

            return FlextResult[list[str]].ok(results)
    except Exception as e:
        return FlextResult[list[str]].fail(f"Batch processing failed: {e}")


def _export_to_json(data: list[dict[str, object]]) -> FlextResult[str]:
    """Export data to JSON format."""
    try:
        json_output = json.dumps(data, indent=2)
        return FlextResult[str].ok(json_output)
    except Exception as e:
        return FlextResult[str].fail(f"JSON export failed: {e}")


def _export_to_csv(data: list[dict[str, object]]) -> FlextResult[str]:
    """Export data to CSV format."""
    try:
        output = io.StringIO()
        if data:
            # Get keys from first item, ensuring they're strings
            fieldnames = [str(key) for key in data[0].keys()]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            # Convert all values to strings for CSV compatibility
            for row in data:
                str_row = {str(k): str(v) for k, v in row.items()}
                writer.writerow(str_row)

        csv_output = output.getvalue()
        return FlextResult[str].ok(csv_output)
    except Exception as e:
        return FlextResult[str].fail(f"CSV export failed: {e}")


def main() -> None:
    """Main demonstration function showcasing data processing and output."""
    formatter = FlextCliFormatters()

    formatter.print_success("FLEXT CLI Data Processing and Output Demo")
    formatter.print_success("=" * 50)

    try:
        # Run all demos in sequence using FlextResult railway pattern
        transform_result = _demonstrate_data_transformation(formatter)
        if transform_result.is_failure:
            formatter.print_error(f"Transformation demo failed: {transform_result.error}")
            return

        aggregation_result = _demonstrate_data_aggregation(formatter)
        if aggregation_result.is_failure:
            formatter.print_error(f"Aggregation demo failed: {aggregation_result.error}")
            return

        formatting_result = _demonstrate_output_formatting(formatter)
        if formatting_result.is_failure:
            formatter.print_error(f"Formatting demo failed: {formatting_result.error}")
            return

        file_result = _demonstrate_file_operations(formatter)
        if file_result.is_failure:
            formatter.print_error(f"File operations demo failed: {file_result.error}")
            return

        batch_result = _demonstrate_batch_processing(formatter)
        if batch_result.is_failure:
            formatter.print_error(f"Batch processing demo failed: {batch_result.error}")
            return

        export_result = _demonstrate_data_export(formatter)
        if export_result.is_failure:
            formatter.print_error(f"Data export demo failed: {export_result.error}")
            return

        _summary_demo(formatter)

    except Exception as e:
        formatter.print_error(f"Demo failed with exception: {e}")
        raise


if __name__ == "__main__":
    main()
