"""FlextCli - Massive Code Reduction Examples.

These examples demonstrate how flext-cli enables massive code reduction
for common data operations by providing zero-boilerplate utility functions
and chainable patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import traceback

import flext_cli

# Constants
PREVIEW_LENGTH_LIMIT = 200


def example_1_traditional_vs_flext() -> None:
    """Example 1: Traditional approach vs FlextCli approach."""
    # Sample data
    users_data = [
        {"id": 1, "name": "Alice", "role": "Admin", "salary": 75000},
        {"id": 2, "name": "Bob", "role": "User", "salary": 65000},
        {"id": 3, "name": "Carol", "role": "Manager", "salary": 85000},
    ]

    # ===============================================
    # TRADITIONAL APPROACH (50+ lines of code)
    # ===============================================
    """







    # Export to CSV
    try:
        with open("users.csv", "w", newline="") as csvfile:
            fieldnames = users_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users_data)
        print("CSV export successful")
    except (RuntimeError, ValueError, TypeError) as e:
        print(f"CSV export failed: {e}")

    # Export to JSON
    try:
        with open("users.json", "w") as jsonfile:
            json.dump(users_data, jsonfile, indent=2)
        print("JSON export successful")
    except (RuntimeError, ValueError, TypeError) as e:
        print(f"JSON export failed: {e}")

    # Create Rich table
    try:
        console = Console()
        table = Table(title="Users Data")
        for key in users_data[0].keys():
            table.add_column(key.title())
        for user in users_data:
            table.add_row(*[str(value) for value in user.values()])
        console.print(table)
    except (RuntimeError, ValueError, TypeError) as e:
        print(f"Table creation failed: {e}")

    # Generate analysis
    try:
        total_records = len(users_data)
        avg_salary = sum(user["salary"] for user in users_data) / total_records
        roles = set(user["role"] for user in users_data)
        print(f"Analysis: {total_records} records, avg salary: ${avg_salary:,.2f}")
        print(f"Roles: {', '.join(roles)}")
    except (RuntimeError, ValueError, TypeError) as e:
        print(f"Analysis failed: {e}")
    """

    # ===============================================
    # FLEXTCLI APPROACH (3 lines of code!!!)
    # ===============================================

    # Use available functionality
    # Export data using available functions
    export_result = flext_cli.flext_cli_export(
        data=users_data,
        output_path="./output/users.json",
    )
    flext_cli.flext_cli_format(users_data)

    # Combine results (simplified approach using available APIs)
    result = export_result  # Use export result as primary

    if result.success:
        result.unwrap()


def example_2_instant_data_operations() -> None:
    """Example 2: Ultra-fast data operations with zero configuration."""
    # Generate sample sales data
    sales_data = [
        {"month": "Jan", "sales": 45000, "region": "North"},
        {"month": "Feb", "sales": 52000, "region": "North"},
        {"month": "Mar", "sales": 48000, "region": "South"},
        {"month": "Apr", "sales": 55000, "region": "East"},
    ]

    # ===============================================
    # INSTANT EXPORT using available API
    # ===============================================
    # Use available export function directly
    result = flext_cli.flext_cli_export(
        data=sales_data,
        output_path="./sales_export.json",
    )
    if result.success:
        result.unwrap()

    # ===============================================
    # CHAINABLE EXPORTS (fluent interface)
    # ===============================================

    # Use available batch export for multiple formats
    chain_result = flext_cli.flext_cli_batch_export(
        {
            "sales_csv": sales_data,
            "sales_json": sales_data,
            "sales_parquet": sales_data,
        },
        base_path="./exports",
        formats=["csv", "json", "parquet"],
    )

    if chain_result.success:
        results = chain_result.unwrap()
        if isinstance(results, dict):
            for details in results.values():
                if isinstance(details, dict):
                    "✅" if details.get("success", False) else "❌"

    # ===============================================
    # BATCH EXPORT multiple datasets
    # ===============================================

    datasets = {
        "sales": sales_data,
        "summary": [{"total_sales": 200000, "avg_sales": 50000}],
        "regions": [{"region": "North", "count": 2}, {"region": "South", "count": 1}],
    }

    batch_result = flext_cli.flext_cli_batch_export(
        datasets,
        base_path="./batch_exports",
        formats=["csv", "json"],
    )

    if batch_result.success:
        batch_results = batch_result.unwrap()
        if isinstance(batch_results, dict):
            for format_results in batch_results.values():
                if isinstance(format_results, dict):
                    for details in format_results.values():
                        if isinstance(details, dict):
                            "✅" if details.get("success", False) else "❌"


def example_3_data_analysis_and_comparison() -> None:
    """Example 3: Advanced data analysis and comparison."""
    # Before and after data for comparison
    users_before = [
        {"id": 1, "name": "Alice", "status": "Active", "salary": 70000},
        {"id": 2, "name": "Bob", "status": "Inactive", "salary": 65000},
    ]

    users_after = [
        {"id": 1, "name": "Alice", "status": "Inactive", "salary": 75000},  # Changed
        {"id": 2, "name": "Bob", "status": "Inactive", "salary": 65000},  # Same
        {"id": 3, "name": "Carol", "status": "Active", "salary": 80000},  # New
    ]

    # ===============================================
    # COMPREHENSIVE DATA ANALYSIS
    # ===============================================

    # Use available aggregate function for analysis
    analysis_result = flext_cli.flext_cli_aggregate_data(
        users_after,
        group_by="status",
        sum_fields=["salary"],
    )

    if analysis_result.success:
        analysis_result.unwrap()

    # ===============================================
    # DATA COMPARISON & DIFF REPORT
    # ===============================================

    # Use available transform function for comparison analysis
    comparison_result = flext_cli.flext_cli_transform_data(
        users_after,
        filter_func=lambda x: x["id"] in [u["id"] for u in users_before],
        sort_key="id",
    )

    if comparison_result.success:
        comparison_result.unwrap()

    # ===============================================
    # MULTI-FORMAT VISUALIZATION
    # ===============================================

    # Use available format function for visualization
    format_result = flext_cli.flext_cli_format(users_after)

    if format_result.success:
        output = format_result.unwrap()
        if isinstance(output, str):
            output[:PREVIEW_LENGTH_LIMIT] + "..." if len(
                output,
            ) > PREVIEW_LENGTH_LIMIT else output


def example_4_interactive_dashboards() -> None:
    """Example 4: Auto-generated interactive dashboards."""
    # System metrics for dashboard
    system_metrics = [
        {"service": "API", "status": "UP", "response_time": "120ms", "cpu": 45},
        {"service": "Database", "status": "UP", "response_time": "25ms", "cpu": 30},
        {"service": "Cache", "status": "DOWN", "response_time": "N/A", "cpu": 0},
        {"service": "Queue", "status": "UP", "response_time": "15ms", "cpu": 60},
    ]

    # ===============================================
    # AUTO-GENERATED DASHBOARD
    # ===============================================

    # Use available table function for dashboard-like display
    dashboard_result = flext_cli.flext_cli_table(
        system_metrics,
        "System Health Dashboard",
        "grid",
    )

    if dashboard_result.success:
        pass

    # ===============================================
    # ADVANCED TABULATE FORMATTING
    # ===============================================

    # Use available table function for formatting
    table_result = flext_cli.flext_cli_table(
        system_metrics,
        "System Status",
        "fancy_grid",
    )

    if table_result.success:
        table_result.unwrap()


def example_5_real_world_scenario() -> None:
    """Example 5: Real-world data processing scenario."""
    # Simulate processing user activity data
    user_activity = [
        {
            "user_id": 1,
            "action": "login",
            "timestamp": "2024-01-15 09:00",
            "ip": "192.168.1.100",
        },
        {
            "user_id": 1,
            "action": "view_page",
            "timestamp": "2024-01-15 09:05",
            "ip": "192.168.1.100",
        },
        {
            "user_id": 2,
            "action": "login",
            "timestamp": "2024-01-15 09:10",
            "ip": "192.168.1.101",
        },
        {
            "user_id": 1,
            "action": "logout",
            "timestamp": "2024-01-15 09:30",
            "ip": "192.168.1.100",
        },
        {
            "user_id": 3,
            "action": "login",
            "timestamp": "2024-01-15 10:00",
            "ip": "192.168.1.102",
        },
    ]

    # ===============================================
    # COMPLETE DATA PROCESSING PIPELINE
    # ===============================================

    # Step 1: Analyze activity patterns
    analysis = flext_cli.flext_cli_aggregate_data(
        user_activity,
        group_by="action",
        sum_fields=["user_id"],
    )
    if analysis.success:
        pass

    # Step 2: Export in multiple formats for different teams
    # Use available batch export function
    export_results = flext_cli.flext_cli_batch_export(
        {
            "activity_csv": user_activity,
            "activity_json": user_activity,
            "activity_parquet": user_activity,
        },
        base_path="./reports",
        formats=["csv", "json", "parquet"],
    )

    if export_results.success:
        results = export_results.unwrap()
        if isinstance(results, dict):
            for _operation, _details in results.items():
                pass

    # Step 3: Create executive dashboard
    dashboard = flext_cli.flext_cli_table(
        user_activity,
        "User Activity Dashboard",
        "grid",
    )
    if dashboard.success:
        pass

    # Step 4: Generate summary report
    summary_data = [
        {"metric": "Total Actions", "value": len(user_activity)},
        {
            "metric": "Unique Users",
            "value": len({item["user_id"] for item in user_activity}),
        },
        {
            "metric": "Login Events",
            "value": len([item for item in user_activity if item["action"] == "login"]),
        },
    ]

    summary_table = flext_cli.flext_cli_table(
        summary_data,
        "Activity Summary",
        "grid",
    )

    if summary_table.success:
        pass


def main() -> None:
    """Run all examples demonstrating massive code reduction."""
    try:
        # Run all examples
        example_1_traditional_vs_flext()
        example_2_instant_data_operations()
        example_3_data_analysis_and_comparison()
        example_4_interactive_dashboards()
        example_5_real_world_scenario()

    except (RuntimeError, ValueError, TypeError):
        traceback.print_exc()


if __name__ == "__main__":
    main()
