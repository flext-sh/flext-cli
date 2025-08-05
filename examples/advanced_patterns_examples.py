"""FlextCli - Advanced Patterns Examples.

Demonstrates advanced usage patterns and architectural excellence
of flext-cli library for enterprise-grade applications.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import traceback

from flext_cli import (
    flext_cli_batch_export,
    flext_cli_export,
    flext_cli_format,
    flext_cli_table,
    flext_cli_transform_data,
    flext_cli_aggregate_data,
    flext_cli_unwrap_or_default,
    flext_cli_unwrap_or_none,
)
from flext_core import FlextResult

# Constants
HIGH_VALUE_THRESHOLD = 80


def example_1_enterprise_data_pipeline() -> None:
    """Example 1: Enterprise-grade data pipeline with error handling."""
    # Simulate enterprise data sources
    customer_data = [
        {"id": 1, "name": "Enterprise Corp", "revenue": 5000000, "industry": "Tech"},
        {
            "id": 2,
            "name": "Global Solutions",
            "revenue": 3200000,
            "industry": "Finance",
        },
        {
            "id": 3,
            "name": "Innovation Ltd",
            "revenue": 1800000,
            "industry": "Healthcare",
        },
    ]

    transaction_data = [
        {"customer_id": 1, "amount": 150000, "date": "2024-01-15", "type": "recurring"},
        {"customer_id": 2, "amount": 89000, "date": "2024-01-16", "type": "one-time"},
        {
            "customer_id": 1,
            "amount": 200000,
            "date": "2024-01-17",
            "type": "enterprise",
        },
    ]

    # ===============================================
    # ENTERPRISE PIPELINE with FlextResult patterns
    # ===============================================

    # Use available batch export functionality
    # Export customer data to multiple destinations
    customer_export_result = flext_cli_batch_export(
        {"customers": customer_data},
        base_path="./enterprise_exports",
        formats=["json", "csv"],
    )

    # Batch export with enterprise resilience
    datasets = {
        "customers": customer_data,
        "transactions": transaction_data,
        "summary": [
            {
                "total_customers": len(customer_data),
                "total_revenue": sum(c["revenue"] for c in customer_data),
            },
        ],
    }

    # Export to multiple storage systems using available functions
    enterprise_result = flext_cli_batch_export(
        datasets,
        base_path="./enterprise_exports",
        formats=["json", "csv"],  # Use available formats
    )

    analytics_result = flext_cli_batch_export(
        datasets,
        base_path="./analytics_exports",
        formats=["json", "csv"],  # Use available formats
    )

    # Process results with enterprise error handling
    if (enterprise_result.success if hasattr(enterprise_result, 'success') else True) and \
       (analytics_result.success if hasattr(analytics_result, 'success') else True):
        pass
    else:
        if hasattr(enterprise_result, 'success') and not enterprise_result.success:
            pass
        if hasattr(analytics_result, 'success') and not analytics_result.success:
            pass


def example_2_flext_result_chaining() -> None:
    """Example 2: Advanced FlextResult chaining and error recovery."""
    # Sample data for processing
    raw_data = [
        {"id": 1, "value": "100.50", "category": "A"},
        {
            "id": 2,
            "value": "invalid",
            "category": "B",
        },  # This will cause processing error
        {"id": 3, "value": "75.25", "category": "A"},
    ]

    # ===============================================
    # CHAINABLE OPERATIONS with error recovery
    # ===============================================

    def validate_data(
        data: list[dict[str, object]],
    ) -> FlextResult[list[dict[str, object]]]:
        """Validate and clean data."""
        try:
            # Simple validation
            cleaned = [
                {
                    **item,
                    "value": float(item["value"]),  # Convert to float
                    "processed": True,
                }
                for item in data
                if item["value"] != "invalid"
            ]

            if not cleaned:
                return FlextResult.fail("No valid data after cleaning")

            return FlextResult.ok(cleaned)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Validation failed: {e}")

    def enrich_data(
        data: list[dict[str, object]],
    ) -> FlextResult[list[dict[str, object]]]:
        """Enrich data with additional calculations."""
        try:
            enriched = [
                {
                    **item,
                    "value_squared": item["value"] ** 2,
                    "is_high_value": item["value"] > HIGH_VALUE_THRESHOLD,
                    "enrichment_timestamp": "2024-01-15T10:30:00Z",
                }
                for item in data
            ]

            return FlextResult.ok(enriched)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Enrichment failed: {e}")

    # Chain operations with error handling
    validation_result = validate_data(raw_data)

    # Use flatMap for chaining FlextResult operations
    final_result = validation_result.flat_map(enrich_data)

    if final_result.success:
        processed_data = final_result.unwrap()

        # Export the processed data
        exporter = flext_cli.FlextCliDataExporter()
        export_result = exporter.instant(processed_data, "json")

        if export_result.success:
            export_result.unwrap()
    else:
        # Recovery: export raw data for manual processing
        recovery_exporter = flext_cli.FlextCliDataExporter()
        recovery_result = recovery_exporter.instant(raw_data, "csv")

        if recovery_result.success:
            recovery_result.unwrap()


def example_3_factory_patterns() -> None:
    """Example 3: Factory patterns for specialized use cases."""
    # Different data types requiring specialized handling
    financial_data = [
        {"symbol": "AAPL", "price": 150.25, "volume": 1000000, "currency": "USD"},
        {"symbol": "GOOGL", "price": 2500.50, "volume": 500000, "currency": "USD"},
    ]

    log_data = [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "level": "INFO",
            "message": "Service started",
        },
        {
            "timestamp": "2024-01-15T10:31:00Z",
            "level": "ERROR",
            "message": "Connection failed",
        },
    ]

    user_data = [
        {"user_id": 1, "email": "alice@company.com", "last_login": "2024-01-15"},
        {"user_id": 2, "email": "bob@company.com", "last_login": "2024-01-14"},
    ]

    # ===============================================
    # SPECIALIZED EXPORTERS
    # ===============================================

    # Financial data -> High-performance columnar format
    financial_exporter = flext_cli.FlextCliDataExporter.create_parquet_exporter()
    financial_result = financial_exporter.instant(financial_data, auto_name=True)

    # Log data -> Database for querying
    log_exporter = flext_cli.FlextCliDataExporter.create_database_exporter()
    log_result = log_exporter.export_data(
        log_data,
        "logs.sqlite",
        "sqlite",
        table_name="application_logs",
    )

    # User data -> CSV for business users
    user_exporter = flext_cli.FlextCliDataExporter.create_csv_exporter()
    user_result = user_exporter.instant(user_data, auto_name=True)

    # ===============================================
    # SPECIALIZED FORMATTERS
    # ===============================================

    # Create different formatters for different audiences
    exec_formatter = flext_cli.FlextCliFormatter("rich")  # Executive dashboard
    tech_formatter = flext_cli.FlextCliFormatter("json")  # Technical audience
    business_formatter = flext_cli.FlextCliFormatter("table")  # Business users

    # Executive summary
    exec_formatter.format(financial_data, title="📈 Financial Summary")

    # Technical report
    tech_formatter.format(log_data, title="System Logs")

    # Business report
    business_formatter.format(user_data, title="User Activity")

    # ===============================================
    # RESULTS SUMMARY
    # ===============================================

    sum(1 for result in [financial_result, log_result, user_result] if result.success)

    if financial_result.success:
        pass
    if log_result.success:
        pass
    if user_result.success:
        pass


def example_4_gui_integration() -> None:
    """Example 4: Advanced Rich GUI integration."""
    # System monitoring data
    system_stats = [
        {
            "service": "Web API",
            "status": "UP",
            "cpu": 45,
            "memory": 60,
            "requests": 1250,
        },
        {
            "service": "Database",
            "status": "UP",
            "cpu": 30,
            "memory": 75,
            "connections": 45,
        },
        {"service": "Cache", "status": "DOWN", "cpu": 0, "memory": 0, "hits": 0},
        {"service": "Queue", "status": "UP", "cpu": 25, "memory": 40, "jobs": 123},
    ]

    # ===============================================
    # MULTI-PANEL DASHBOARD
    # ===============================================

    gui = flext_cli.FlextCliRichGUI()

    # Main dashboard
    dashboard_result = gui.create_dashboard("🖥️ System Monitoring Dashboard")

    if dashboard_result.success:
        # Data table panel
        table_result = gui.create_data_table(system_stats, "Service Status")
        if table_result.success:
            pass

        # Metrics panel
        metrics = {
            "total_services": {
                "value": len(system_stats),
                "unit": "services",
                "trend": "stable",
            },
            "services_up": {
                "value": len([s for s in system_stats if s["status"] == "UP"]),
                "unit": "online",
                "trend": "up",
            },
            "avg_cpu": {
                "value": sum(s["cpu"] for s in system_stats) / len(system_stats),
                "unit": "%",
                "trend": "down",
            },
            "total_memory": {
                "value": sum(s["memory"] for s in system_stats),
                "unit": "%",
                "trend": "up",
            },
        }

        metrics_result = gui.create_metrics_dashboard(metrics, "Key Metrics")
        if metrics_result.success:
            pass

        # Status grid
        status_grid = {
            service["service"]: {
                "status": service["status"].lower(),
                "color": "green" if service["status"] == "UP" else "red",
            }
            for service in system_stats
        }

        grid_result = gui.create_status_grid(status_grid, "Service Grid")
        if grid_result.success:
            pass

    # ===============================================
    # INTERACTIVE MENU SYSTEM
    # ===============================================

    menu_items = [
        {"key": "1", "label": "📊 View System Stats", "action": "stats"},
        {"key": "2", "label": "📁 Export Data", "action": "export"},
        {"key": "3", "label": "🔄 Refresh Dashboard", "action": "refresh"},
        {"key": "4", "label": "⚙️ System Settings", "action": "settings"},
        {"key": "q", "label": "🚪 Quit", "action": "quit"},
    ]

    menu_result = gui.create_interactive_menu(menu_items, "Main Menu")
    if menu_result.success:
        pass


def example_5_performance_patterns() -> None:
    """Example 5: Performance optimization patterns."""
    # Generate large dataset for performance testing
    large_dataset = [
        {
            "id": i,
            "name": f"User_{i}",
            "email": f"user_{i}@company.com",
            "department": f"Dept_{i % 10}",
            "salary": 50000 + (i * 100),
            "join_date": f"2024-01-{(i % 28) + 1:02d}",
        }
        for i in range(10000)  # 10K records
    ]

    # ===============================================
    # PERFORMANCE-OPTIMIZED EXPORT
    # ===============================================

    # Use specialized exporters for performance
    parquet_exporter = flext_cli.FlextCliDataExporter.create_parquet_exporter()

    # Batch operations for efficiency
    performance_datasets = {
        "employees": large_dataset[:5000],  # First half
        "contractors": large_dataset[5000:],  # Second half
    }

    # Parallel batch export
    batch_result = parquet_exporter.batch_export(
        performance_datasets,
        base_path="./performance_exports",
        formats=["parquet", "feather"],  # Fast columnar formats
    )

    if batch_result.success:
        results = batch_result.unwrap()
        for _formats in results.values():
            pass

    # ===============================================
    # STREAMING ANALYSIS
    # ===============================================

    # Analyze in chunks for memory efficiency
    chunk_size = 2000
    analysis_results = []

    for i in range(0, len(large_dataset), chunk_size):
        chunk = large_dataset[i : i + chunk_size]

        # Quick analysis on chunk
        chunk_analysis = flext_cli.flext_cli_analyze_data(
            chunk,
            f"Chunk {i // chunk_size + 1} Analysis",
        )

        if chunk_analysis.success:
            analysis_results.append(f"Chunk {i // chunk_size + 1}: ✅ Processed")
        else:
            analysis_results.append(f"Chunk {i // chunk_size + 1}: ❌ Failed")

    # ===============================================
    # OPTIMIZED FORMATTING
    # ===============================================

    # Sample subset for quick preview
    sample_data = large_dataset[:100]  # Just 100 records for preview

    # Multiple format preview (optimized)
    format_result = flext_cli.flext_cli_format_all(
        sample_data,
        styles=["json", "table"],  # Only essential formats
    )

    if format_result.success:
        format_result.unwrap()


def main() -> None:
    """Run advanced patterns examples."""
    try:
        example_1_enterprise_data_pipeline()
        example_2_flext_result_chaining()
        example_3_factory_patterns()
        example_4_gui_integration()
        example_5_performance_patterns()

    except (RuntimeError, ValueError, TypeError):
        traceback.print_exc()


if __name__ == "__main__":
    main()
