"""Massive Boilerplate Reduction - Before vs After Comparison.

Real examples showing dramatic reduction in code volume using new flext-cli helpers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

import flext_cli


def example_before_vs_after() -> None:
    """Compare traditional FlextResult handling vs new helpers."""
    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    # ===============================================
    # TRADITIONAL APPROACH (verbose and repetitive)
    # ===============================================
    """
    # Export data
    export_result = flext_cli.flext_cli_export_data(data, "users.csv")
    if export_result.success:
      filepath = export_result.unwrap()
      print(f"Exported to: {filepath}")
    else:
      print(f"Export failed: {export_result.error}")

    # Format data
    format_result = flext_cli.flext_cli_format_output(data, "json")
    if format_result.success:
      formatted = format_result.unwrap()
      print(formatted)
    else:
      print("Formatting failed")

    # Analyze data
    analysis_result = flext_cli.flext_cli_analyze_data(data)
    if analysis_result.success:
      analysis = analysis_result.unwrap()
      with open("analysis.txt", "w") as f:
          f.write(analysis)
      print("Analysis saved")
    else:
      print("Analysis failed")

    # Compare datasets
    comparison_result = flext_cli.flext_cli_data_compare(data, data)
    if comparison_result.success:
      comparison = comparison_result.unwrap()
      if len(comparison) > 100:
          print("Large comparison result")
      else:
          print(comparison)
    else:
      print("Comparison failed")
    """

    # ===============================================
    # NEW APPROACH (massive reduction!)
    # ===============================================

    # Export data - using available functions
    export_result = flext_cli.flext_cli_export(data, "users.csv")
    flext_cli.flext_cli_unwrap_or_none(export_result)

    # Format and print data - using available functions
    format_result = flext_cli.flext_cli_format(data)
    if format_result.success:
        pass

    # Analyze and save - using available aggregation
    analysis_result = flext_cli.flext_cli_aggregate_data(
        data,
        group_by="id",
        sum_fields=[],
    )
    analysis = flext_cli.flext_cli_unwrap_or_default(
        analysis_result,
        "No analysis available",
    )
    with Path("analysis.txt").open("w", encoding="utf-8") as f:
        f.write(str(analysis))

    # Transform data for comparison-like functionality
    comparison_result = flext_cli.flext_cli_transform_data(
        data,
        filter_func=lambda _: True,  # Keep all data (noqa: ARG005)
        sort_key="id",
    )
    comparison = flext_cli.flext_cli_unwrap_or_none(comparison_result)
    if comparison:
        pass


def example_silent_execution() -> None:
    """Silent execution for fire-and-forget operations."""
    data = [{"metric": "cpu", "value": 75}, {"metric": "memory", "value": 60}]

    # ===============================================
    # TRADITIONAL (error handling boilerplate)
    # ===============================================
    """
    try:
      result = flext_cli.flext_cli_instant_export(data, "csv")
      if result.success:
          print(f"Exported: {result.unwrap()}")
      else:
          print("Export failed")
    except (RuntimeError, ValueError, TypeError) as e:
      print(f"Unexpected error: {e}")

    try:
      dashboard_result = flext_cli.flext_cli_auto_dashboard(data)
      if dashboard_result.success:
          print("Dashboard created")
    except (RuntimeError, ValueError, TypeError):
      pass  # Dashboard errors are non-critical for this comparison
    """

    # ===============================================
    # NEW APPROACH (fire-and-forget)
    # ===============================================

    # Simple execution using available functions
    export_result = flext_cli.flext_cli_export(data, "metrics.csv")
    exported_file = flext_cli.flext_cli_unwrap_or_none(export_result)
    if exported_file:
        pass

    # Table creation for dashboard-like functionality
    table_result = flext_cli.flext_cli_table(
        data,
        "System Metrics",
        "grid",
    )
    flext_cli.flext_cli_unwrap_or_none(table_result)


def example_chainable_operations() -> None:
    """Chainable operations with built-in error handling."""
    users = [
        {"id": 1, "name": "Alice", "role": "Admin"},
        {"id": 2, "name": "Bob", "role": "User"},
        {"id": 3, "name": "Carol", "role": "Manager"},
    ]

    # ===============================================
    # TRADITIONAL (nested if statements)
    # ===============================================
    """
    export_result = flext_cli.flext_cli_export_data(users, "users.json")
    if export_result.success:
      analysis_result = flext_cli.flext_cli_analyze_data(users)
      if analysis_result.success:
          format_result = flext_cli.flext_cli_format_all(users, ["table", "yaml"])
          if format_result.success:
              dashboard_result = flext_cli.flext_cli_auto_dashboard(users)
              if dashboard_result.success:
                  print("All operations completed successfully")
              else:
                  print("Dashboard creation failed")
          else:
              print("Formatting failed")
      else:
          print("Analysis failed")
    else:
      print("Export failed")
    """

    # ===============================================
    # NEW APPROACH (flat chain with defaults)
    # ===============================================

    # Chain operations with sensible defaults using available functions
    export_result = flext_cli.flext_cli_export(users, "users.json")
    flext_cli.flext_cli_unwrap_or_default(
        export_result,
        "Export unavailable",
    )

    analysis_result = flext_cli.flext_cli_aggregate_data(
        users,
        group_by="role",
        sum_fields=[],
    )
    flext_cli.flext_cli_unwrap_or_default(
        analysis_result,
        "Analysis unavailable",
    )

    format_result = flext_cli.flext_cli_format(users)
    flext_cli.flext_cli_unwrap_or_default(
        format_result,
        "Data unavailable",
    )

    # Table creation for dashboard-like functionality
    table_result = flext_cli.flext_cli_table(
        users,
        "User Dashboard",
        "grid",
    )
    flext_cli.flext_cli_unwrap_or_none(table_result)


def example_batch_operations() -> None:
    """Batch operations with massive error handling reduction."""
    datasets = {
        "users": [{"id": 1, "name": "Alice"}],
        "products": [{"id": 100, "name": "Widget"}],
        "orders": [{"id": 1001, "user_id": 1, "product_id": 100}],
    }

    # ===============================================
    # TRADITIONAL (tons of error handling)
    # ===============================================
    """
    results = {}
    for name, data in datasets.items():
      export_result = flext_cli.flext_cli_instant_export(data, "json")
      if export_result.success:
          results[f"{name}_export"] = export_result.unwrap()
      else:
          results[f"{name}_export"] = f"Failed: {export_result.error}"

      analysis_result = flext_cli.flext_cli_analyze_data(data)
      if analysis_result.success:
          results[f"{name}_analysis"] = "Available"
      else:
          results[f"{name}_analysis"] = "Failed"

      format_result = flext_cli.flext_cli_format_output(data, "table")
      if format_result.success:
          results[f"{name}_table"] = len(format_result.unwrap())
      else:
          results[f"{name}_table"] = 0
    """

    # ===============================================
    # NEW APPROACH (ultra-compact)
    # ===============================================

    results = {}
    for name, data in datasets.items():
        # All operations using available functions with automatic defaults
        export_result = flext_cli.flext_cli_export(data, f"{name}.json")
        results[f"{name}_export"] = flext_cli.flext_cli_unwrap_or_default(
            export_result,
            "Export failed",
        )

        analysis_result = flext_cli.flext_cli_aggregate_data(
            data,
            group_by="id" if "id" in str(data) else "name",
            sum_fields=[],
        )
        results[f"{name}_analysis"] = (
            "Available"
            if flext_cli.flext_cli_unwrap_or_none(analysis_result)
            else "Failed"
        )

        format_result = flext_cli.flext_cli_format(data)
        formatted_output = flext_cli.flext_cli_unwrap_or_default(
            format_result,
            "",
        )
        results[f"{name}_table_size"] = len(str(formatted_output))

    # Print summary
    for _key, _value in results.items():
        pass


def main() -> None:
    """Run all examples showing massive boilerplate reduction."""
    example_before_vs_after()

    example_silent_execution()

    example_chainable_operations()

    example_batch_operations()


if __name__ == "__main__":
    main()
