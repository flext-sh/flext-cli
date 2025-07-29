#!/usr/bin/env python3
"""Basic usage examples for flext-cli.

This module demonstrates the core functionality of flext-cli
with practical, real-world examples.
"""

import tempfile
from pathlib import Path
from typing import Never

from flext_cli import CliApi, export, format_data

# Example data sets for demonstrations
SAMPLE_USERS = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "REDACTED_LDAP_BIND_PASSWORD"},
    {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "user"},
    {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "role": "user"},
]

SALES_DATA = [
    {"product": "Widget A", "quantity": 150, "revenue": 15000.00, "month": "2024-01"},
    {"product": "Widget B", "quantity": 230, "revenue": 34500.00, "month": "2024-01"},
    {"product": "Widget C", "quantity": 89, "revenue": 8900.00, "month": "2024-01"},
]

SYSTEM_METRICS = [
    {"timestamp": "2024-01-15T10:00:00", "cpu_usage": 45.2, "memory_usage": 68.5, "disk_usage": 23.1},
    {"timestamp": "2024-01-15T10:05:00", "cpu_usage": 52.1, "memory_usage": 71.2, "disk_usage": 23.2},
    {"timestamp": "2024-01-15T10:10:00", "cpu_usage": 38.9, "memory_usage": 69.8, "disk_usage": 23.1},
]


def example_basic_export() -> None:
    """Demonstrate basic export functionality."""
    print("=== Basic Export Examples ===")

    # Use convenience functions for simple operations

    # Create temporary directory for examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 1. Export user data to JSON
        json_file = temp_path / "users.json"
        success = export(SAMPLE_USERS, str(json_file), "json")
        print(f"✓ JSON export: {'Success' if success else 'Failed'}")

        if success and json_file.exists():
            print(f"  File size: {json_file.stat().st_size} bytes")

        # 2. Export sales data to CSV
        csv_file = temp_path / "sales.csv"
        success = export(SALES_DATA, str(csv_file), "csv")
        print(f"✓ CSV export: {'Success' if success else 'Failed'}")

        # 3. Auto-detect format from extension
        auto_json = temp_path / "metrics.json"
        success = export(SYSTEM_METRICS, str(auto_json), "auto")
        print(f"✓ Auto-detect export: {'Success' if success else 'Failed'}")

        # 4. Export single record (automatically converted to list)
        single_user = {"id": 99, "name": "Test User", "email": "test@example.com"}
        single_file = temp_path / "single_user.json"
        success = export(single_user, str(single_file))
        print(f"✓ Single record export: {'Success' if success else 'Failed'}")


def example_data_formatting() -> None:
    """Demonstrate data formatting for display."""
    print("\n=== Data Formatting Examples ===")

    # 1. Format as JSON (pretty-printed)
    json_output = format_data(SAMPLE_USERS[:2], "json")
    print("JSON format:")
    print(json_output[:100] + "..." if len(json_output) > 100 else json_output)

    # 2. Format as table for console display
    table_output = format_data(SALES_DATA, "table")
    print("\nTable format:")
    print(table_output)

    # 3. Format single record as table
    single_table = format_data(SAMPLE_USERS[0], "table")
    print("\nSingle record table:")
    print(single_table)


def example_api_class_usage() -> None:
    """Demonstrate using the CliApi class directly for advanced features."""
    print("\n=== Advanced API Usage ===")

    # Create API instance
    api = CliApi()

    # 1. Health check
    health_result = api.health()
    if health_result.is_success:
        health_data = health_result.data
        print(f"✓ Service status: {health_data['status']}")
        print(f"  Supported formats: {', '.join(health_data['formats'])}")
        print(f"  Version: {health_data['version']}")

    # 2. Add custom commands
    def calculate_total_revenue(sales_data):
        """Calculate total revenue from sales data."""
        return sum(item["revenue"] for item in sales_data)

    def user_count_by_role(users_data):
        """Count users by role."""
        role_counts = {}
        for user in users_data:
            role = user["role"]
            role_counts[role] = role_counts.get(role, 0) + 1
        return role_counts

    # Register commands
    add_result = api.add_command("total_revenue", calculate_total_revenue)
    print(f"✓ Command registration: {'Success' if add_result.is_success else 'Failed'}")

    api.add_command("user_roles", user_count_by_role)

    # 3. Execute commands
    revenue_result = api.execute("total_revenue", SALES_DATA)
    if revenue_result.is_success:
        print(f"  Total revenue: ${revenue_result.data:,.2f}")

    roles_result = api.execute("user_roles", SAMPLE_USERS)
    if roles_result.is_success:
        print(f"  User roles: {roles_result.data}")

    # 4. Export with detailed results
    with tempfile.TemporaryDirectory() as temp_dir:
        export_file = Path(temp_dir) / "detailed_export.json"
        export_result = api.export(SYSTEM_METRICS, str(export_file), "json")

        if export_result.is_success:
            print(f"✓ Detailed export result: {export_result.data}")


def example_error_handling() -> None:
    """Demonstrate error handling patterns."""
    print("\n=== Error Handling Examples ===")

    api = CliApi()

    # 1. Export with invalid data
    success = export(None, "/tmp/invalid.json")
    print(f"✓ Invalid data handling: {'Handled' if not success else 'Unexpected success'}")

    # 2. Export with unsupported format
    success = export(SAMPLE_USERS, "/tmp/test.xyz", "xml")
    print(f"✓ Unsupported format: {'Handled' if not success else 'Unexpected success'}")

    # 3. Format with unsupported style
    result = format_data(SAMPLE_USERS, "xml")
    print(f"✓ Format error handling: {'Handled' if result.startswith('Error:') else 'Unexpected success'}")

    # 4. CSV export with invalid data structure
    invalid_csv_data = ["string1", "string2"]  # Not list of dicts
    csv_result = api.export(invalid_csv_data, "/tmp/invalid.csv", "csv")
    print(f"✓ CSV validation: {'Handled' if not csv_result.is_success else 'Unexpected success'}")

    # 5. Command execution errors
    def failing_command() -> Never:
        msg = "This command always fails"
        raise ValueError(msg)

    api.add_command("fail_test", failing_command)
    fail_result = api.execute("fail_test")
    print(f"✓ Command error handling: {'Handled' if not fail_result.is_success else 'Unexpected success'}")


def example_real_world_scenarios() -> None:
    """Demonstrate real-world usage scenarios."""
    print("\n=== Real-World Scenarios ===")

    # Scenario 1: Processing survey results
    survey_responses = [
        {"respondent_id": 1, "satisfaction": 4, "recommend": True, "feedback": "Great service!"},
        {"respondent_id": 2, "satisfaction": 5, "recommend": True, "feedback": "Excellent experience"},
        {"respondent_id": 3, "satisfaction": 3, "recommend": False, "feedback": "Could be better"},
        {"respondent_id": 4, "satisfaction": 5, "recommend": True, "feedback": "Perfect!"},
    ]

    print("Survey Analysis:")
    avg_satisfaction = sum(r["satisfaction"] for r in survey_responses) / len(survey_responses)
    recommend_rate = sum(1 for r in survey_responses if r["recommend"]) / len(survey_responses)

    print(f"  Average satisfaction: {avg_satisfaction:.1f}/5")
    print(f"  Recommendation rate: {recommend_rate:.1%}")

    # Format results for reporting
    summary_table = format_data(survey_responses, "table")
    print("\nSurvey responses table:")
    print(summary_table)

    # Scenario 2: Log analysis and export
    log_entries = [
        {"timestamp": "2024-01-15T10:30:00", "level": "INFO", "message": "Application started"},
        {"timestamp": "2024-01-15T10:31:22", "level": "WARNING", "message": "High memory usage detected"},
        {"timestamp": "2024-01-15T10:32:15", "level": "ERROR", "message": "Database connection failed"},
        {"timestamp": "2024-01-15T10:32:45", "level": "INFO", "message": "Database connection restored"},
    ]

    # Filter and export error logs
    error_logs = [log for log in log_entries if log["level"] == "ERROR"]

    with tempfile.TemporaryDirectory() as temp_dir:
        error_file = Path(temp_dir) / "error_logs.json"
        success = export(error_logs, str(error_file))
        print(f"\n✓ Error log export: {'Success' if success else 'Failed'}")

        if success:
            print(f"  Exported {len(error_logs)} error entries")

    # Scenario 3: API response processing
    api_responses = [
        {"endpoint": "/users", "response_time": 120, "status_code": 200, "errors": 0},
        {"endpoint": "/orders", "response_time": 450, "status_code": 200, "errors": 0},
        {"endpoint": "/products", "response_time": 200, "status_code": 500, "errors": 1},
        {"endpoint": "/reports", "response_time": 1200, "status_code": 200, "errors": 0},
    ]

    # Generate performance report
    slow_endpoints = [r for r in api_responses if r["response_time"] > 500]
    error_endpoints = [r for r in api_responses if r["status_code"] >= 400]

    print("\nAPI Performance Analysis:")
    print(f"  Slow endpoints (>500ms): {len(slow_endpoints)}")
    print(f"  Error endpoints: {len(error_endpoints)}")

    if slow_endpoints:
        print("\nSlow endpoints:")
        slow_table = format_data(slow_endpoints, "table")
        print(slow_table)


def main() -> None:
    """Run all examples."""
    print("FLEXT-CLI Usage Examples")
    print("=" * 50)

    try:
        example_basic_export()
        example_data_formatting()
        example_api_class_usage()
        example_error_handling()
        example_real_world_scenarios()

        print("\n" + "=" * 50)
        print("✓ All examples completed successfully!")

    except (RuntimeError, ValueError, TypeError) as e:
        print(f"\n❌ Example failed: {e}")
        raise


if __name__ == "__main__":
    main()
