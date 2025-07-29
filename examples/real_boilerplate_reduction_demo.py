"""Real Boilerplate Reduction Demonstration.

This example shows the actual, measurable reduction in code achieved by the new
flext-cli unified API compared to traditional approaches.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from flext_cli.core.data_exporter import FlextCliDataExporter
from flext_cli.core.formatter import FlextCliFormatter
from flext_cli import (
from flext_cli import flext_cli_aggregate_data, flext_cli_transform_data
from flext_cli.decorators import (
from flext_cli import flext_cli_pipeline


from __future__ import annotations

# Sample dataset for demonstration
sample_data = [
    {"id": 1, "name": "Alice Johnson", "role": "Software Engineer", "salary": 95000},
    {"id": 2, "name": "Bob Smith", "role": "Data Scientist", "salary": 105000},
    {"id": 3, "name": "Carol Williams", "role": "Product Manager", "salary": 110000},
    {"id": 4, "name": "David Brown", "role": "DevOps Engineer", "salary": 98000},
    {"id": 5, "name": "Eva Davis", "role": "UX Designer", "salary": 88000},
]


def traditional_approach() -> None:
    """Traditional approach - verbose and repetitive."""
    # ============================================================================
    # TRADITIONAL CODE (21+ lines for basic operations)
    # ============================================================================




    # Export operation
    exporter = FlextCliDataExporter()
    exporter.export_data(sample_data, "/tmp/traditional_employees.json", "json")

    # Format operation
    formatter = FlextCliFormatter()
    format_result = formatter.format(sample_data)
    if isinstance(format_result, str):
        pass

    # Table creation
    table_result = formatter.format_tabulate_table(
        sample_data,
        "Employee Table",
        "grid",
    )
    if table_result.success:
        pass


def modern_unified_approach() -> None:
    """Modern unified approach - concise and powerful."""
    # ============================================================================
    # UNIFIED API CODE (5 lines for same operations + enhanced capabilities)
    # ============================================================================


        flext_cli_export,
        flext_cli_format,
        flext_cli_table,
    )

    # All operations in 3 lines with automatic error handling
    flext_cli_export(sample_data, "/tmp/unified_employees.json", "json")
    flext_cli_format(sample_data)
    flext_cli_table(sample_data, "Employee Table", "grid")

    # Results automatically handled - no manual error checking needed


def enhanced_collections_demo() -> None:
    """Demonstrate enhanced collections with FlextResult integration."""


    # Transform data - filter, sort, limit
    transform_result = flext_cli_transform_data(
        sample_data,
        filter_func=lambda emp: emp["salary"] > 100000,
        sort_key="salary",
    )
    if transform_result.success:
        pass

    # Aggregate data - group by role with salary sum
    aggregate_result = flext_cli_aggregate_data(
        sample_data,
        group_by="role",
        sum_fields=["salary"],
    )
    if aggregate_result.success:
        pass


def advanced_decorators_demo() -> None:
    """Demonstrate advanced decorators for boilerplate reduction."""

        flext_cli_auto_result,
        flext_cli_cache_result,
        flext_cli_safe_operation,
        flext_cli_validate_data,
    )

    @flext_cli_auto_result("Salary calculation failed")
    @flext_cli_validate_data(not_empty=True, expected_type=list, min_length=1)
    def calculate_average_salary(data: list[dict[str, int]]) -> float:
        """Calculate average salary with automatic validation and result wrapping."""
        total = sum(emp["salary"] for emp in data)
        return total / len(data)

    @flext_cli_cache_result(ttl_seconds=60)
    @flext_cli_safe_operation(default_return="N/A")
    def format_salary_range(data: list[dict[str, int]]) -> str:
        """Get salary range with caching and safe operation."""
        salaries = [emp["salary"] for emp in data]
        return f"${min(salaries):,} - ${max(salaries):,}"

    # These functions now have automatic error handling, validation, and caching
    calculate_average_salary(sample_data)
    format_salary_range(sample_data)


def pipeline_operations_demo() -> None:
    """Demonstrate pipeline operations with single function call."""


    # Complete data pipeline in one call
    pipeline_result = flext_cli_pipeline(
        sample_data,
        export_path="/tmp/pipeline_employees",
        formats=["json", "csv"],
        dashboard=False,  # Would create dashboard if True
        analysis=True,
    )

    if pipeline_result.success:
        pass


def main() -> None:
    """Run all demonstrations."""
    traditional_approach()

    modern_unified_approach()

    enhanced_collections_demo()

    advanced_decorators_demo()

    pipeline_operations_demo()


if __name__ == "__main__":
    main()
