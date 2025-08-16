#!/usr/bin/env python3
"""Basic usage examples for flext-cli.

This module demonstrates the core functionality of flext-cli
with practical, real-world examples.
"""

import contextlib
import tempfile
from pathlib import Path
from typing import Any, Never

from flext_cli import (
    CLIHelper,
    flext_cli_export,
    flext_cli_format,
    flext_cli_table,
)

# Constants
PREVIEW_LENGTH_LIMIT = 100
SLOW_RESPONSE_THRESHOLD_MS = 500
HTTP_ERROR_STATUS_CODE = 400

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
    {
        "timestamp": "2024-01-15T10:00:00",
        "cpu_usage": 45.2,
        "memory_usage": 68.5,
        "disk_usage": 23.1,
    },
    {
        "timestamp": "2024-01-15T10:05:00",
        "cpu_usage": 52.1,
        "memory_usage": 71.2,
        "disk_usage": 23.2,
    },
    {
        "timestamp": "2024-01-15T10:10:00",
        "cpu_usage": 38.9,
        "memory_usage": 69.8,
        "disk_usage": 23.1,
    },
]


def example_basic_export() -> None:
    """Demonstrate basic export functionality."""
    # Use convenience functions for simple operations

    # Create temporary directory for examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 1. Export user data to JSON
        json_file = temp_path / "users.json"
        result = flext_cli_export(SAMPLE_USERS, str(json_file))
        success = result.success if hasattr(result, "success") else True

        if success and json_file.exists():
            pass

        # 2. Export sales data to CSV
        csv_file = temp_path / "sales.csv"
        result = flext_cli_export(SALES_DATA, str(csv_file))
        success = result.success if hasattr(result, "success") else True

        # 3. Auto-detect format from extension
        auto_json = temp_path / "metrics.json"
        result = flext_cli_export(SYSTEM_METRICS, str(auto_json))
        success = result.success if hasattr(result, "success") else True

        # 4. Export single record (automatically converted to list)
        single_user = {"id": 99, "name": "Test User", "email": "test@example.com"}
        single_file = temp_path / "single_user.json"
        result = flext_cli_export([single_user], str(single_file))
        success = result.success if hasattr(result, "success") else True


def example_data_formatting() -> None:
    """Demonstrate data formatting for display."""
    # 1. Format as JSON (pretty-printed)
    format_result = flext_cli_format(SAMPLE_USERS[:2])
    json_output = str(
        format_result.unwrap() if format_result.success else "Format failed",
    )
    (
        json_output[:PREVIEW_LENGTH_LIMIT] + "..."
        if len(json_output) > PREVIEW_LENGTH_LIMIT
        else json_output
    )

    # 2. Format as table for console display
    table_result = flext_cli_table(SALES_DATA, "Sales Data", "grid")
    str(
        table_result.unwrap() if table_result.success else "Table failed",
    )

    # 3. Format single record as table
    single_result = flext_cli_table([SAMPLE_USERS[0]], "User Data", "grid")
    str(
        single_result.unwrap() if single_result.success else "Table failed",
    )


def example_api_class_usage() -> None:
    """Demonstrate using the CliApi class directly for advanced features."""
    # Create helper instance
    CLIHelper()

    # 1. Simulate health check

    # 2. Add custom commands
    def calculate_total_revenue(sales_data: list[dict[str, Any]]) -> float:
        """Calculate total revenue from sales data."""
        return sum(item["revenue"] for item in sales_data)

    def user_count_by_role(users_data: list[dict[str, Any]]) -> dict[str, int]:
        """Count users by role."""
        role_counts = {}
        for user in users_data:
            role = user["role"]
            role_counts[role] = role_counts.get(role, 0) + 1
        return role_counts

    # Commands would be registered with actual CLI in practice

    # 3. Execute commands (simulated)
    calculate_total_revenue(SALES_DATA)

    user_count_by_role(SAMPLE_USERS)

    # 4. Export with detailed results
    with tempfile.TemporaryDirectory() as temp_dir:
        export_file = Path(temp_dir) / "detailed_export.json"
        export_result = flext_cli_export(SYSTEM_METRICS, str(export_file))

        success = export_result.success if hasattr(export_result, "success") else True
        if success:
            pass


def example_error_handling() -> None:
    """Demonstrate error handling patterns."""
    # Error handling examples

    # Use secure temporary files instead of hardcoded paths

    # 1. Export with invalid data
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
        invalid_path = tmp_file.name

    try:
        result = flext_cli_export([], invalid_path)  # Use empty list instead of None
        result.success if hasattr(result, "success") else False
    except (ValueError, TypeError):
        pass

    # 2. Export with unsupported format
    with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp_file:
        test_path = tmp_file.name

    try:
        result = flext_cli_export(SAMPLE_USERS, test_path)  # Remove unsupported format
        result.success if hasattr(result, "success") else False
    except (ValueError, TypeError):
        pass

    # Clean up temporary files

    try:
        Path(invalid_path).unlink()
        Path(test_path).unlink()
    except (OSError, FileNotFoundError):
        pass  # Files may not exist or already cleaned up

    # 3. Format with error handling
    try:
        format_result = flext_cli_format(SAMPLE_USERS)
        result = str(
            format_result.unwrap() if format_result.success else "Error: Format failed",
        )
    except (ValueError, TypeError):
        result = "Error: Format failed"

    # 4. Export with invalid data structure
    invalid_csv_data = ["string1", "string2"]  # Not list of dicts
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_file:
        try:
            csv_result = flext_cli_export(invalid_csv_data, tmp_file.name)
            csv_result.success if hasattr(csv_result, "success") else False
        except (ValueError, TypeError):
            pass

    # 5. Command execution errors
    def failing_command() -> Never:
        msg = "This command always fails"
        raise ValueError(msg)

    # Commands would handle errors in actual CLI implementation
    with contextlib.suppress(ValueError):
        failing_command()


def example_real_world_scenarios() -> None:
    """Demonstrate real-world usage scenarios."""
    # Scenario 1: Processing survey results
    survey_responses = [
        {
            "respondent_id": 1,
            "satisfaction": 4,
            "recommend": True,
            "feedback": "Great service!",
        },
        {
            "respondent_id": 2,
            "satisfaction": 5,
            "recommend": True,
            "feedback": "Excellent experience",
        },
        {
            "respondent_id": 3,
            "satisfaction": 3,
            "recommend": False,
            "feedback": "Could be better",
        },
        {
            "respondent_id": 4,
            "satisfaction": 5,
            "recommend": True,
            "feedback": "Perfect!",
        },
    ]

    sum(r["satisfaction"] for r in survey_responses) / len(
        survey_responses,
    )
    sum(1 for r in survey_responses if r["recommend"]) / len(
        survey_responses,
    )

    # Format results for reporting
    table_result = flext_cli_table(survey_responses, "Survey Responses", "grid")
    str(
        table_result.unwrap() if table_result.success else "Table failed",
    )

    # Scenario 2: Log analysis and export
    log_entries = [
        {
            "timestamp": "2024-01-15T10:30:00",
            "level": "INFO",
            "message": "Application started",
        },
        {
            "timestamp": "2024-01-15T10:31:22",
            "level": "WARNING",
            "message": "High memory usage detected",
        },
        {
            "timestamp": "2024-01-15T10:32:15",
            "level": "ERROR",
            "message": "Database connection failed",
        },
        {
            "timestamp": "2024-01-15T10:32:45",
            "level": "INFO",
            "message": "Database connection restored",
        },
    ]

    # Filter and export error logs
    error_logs = [log for log in log_entries if log["level"] == "ERROR"]

    with tempfile.TemporaryDirectory() as temp_dir:
        error_file = Path(temp_dir) / "error_logs.json"
        result = flext_cli_export(error_logs, str(error_file))
        success = result.success if hasattr(result, "success") else True

        if success:
            pass

    # Scenario 3: API response processing
    api_responses = [
        {"endpoint": "/users", "response_time": 120, "status_code": 200, "errors": 0},
        {"endpoint": "/orders", "response_time": 450, "status_code": 200, "errors": 0},
        {
            "endpoint": "/products",
            "response_time": 200,
            "status_code": 500,
            "errors": 1,
        },
        {
            "endpoint": "/reports",
            "response_time": 1200,
            "status_code": 200,
            "errors": 0,
        },
    ]

    # Generate performance report
    slow_endpoints = [
        r for r in api_responses if r["response_time"] > SLOW_RESPONSE_THRESHOLD_MS
    ]
    [r for r in api_responses if r["status_code"] >= HTTP_ERROR_STATUS_CODE]

    if slow_endpoints:
        table_result = flext_cli_table(slow_endpoints, "Slow Endpoints", "grid")
        str(
            table_result.unwrap() if table_result.success else "Table failed",
        )


def main() -> None:
    """Run all examples."""
    try:
        example_basic_export()
        example_data_formatting()
        example_api_class_usage()
        example_error_handling()
        example_real_world_scenarios()

    except (RuntimeError, ValueError, TypeError):
        raise


if __name__ == "__main__":
    main()
