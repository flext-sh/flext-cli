#!/usr/bin/env python3
"""Quick functionality test for refactored flext-cli helpers.

Tests the actual functionality of the refactored helpers to ensure they work correctly.
"""

from __future__ import annotations

import pathlib
import sys

# Test data
sample_data = [
    {"id": 1, "name": "Alice", "role": "Engineer", "salary": 95000},
    {"id": 2, "name": "Bob", "role": "Scientist", "salary": 105000},
    {"id": 3, "name": "Carol", "role": "Manager", "salary": 110000},
]


def test_basic_helpers():
    """Test basic helper functions."""
    from flext_cli import flext_cli_format, flext_cli_table

    # Test formatting
    format_result = flext_cli_format(sample_data)

    # Test table creation
    table_result = flext_cli_table(sample_data, "Test Table")

    return format_result.success and table_result.success


def test_new_helpers():
    """Test new boilerplate reduction helpers."""
    from flext_cli import flext_cli_aggregate_data, flext_cli_transform_data

    # Test data transformation
    transform_result = flext_cli_transform_data(
        sample_data,
        filter_func=lambda x: x["salary"] > 100000,
        sort_key="salary",
    )
    if transform_result.success:
        pass

    # Test data aggregation
    aggregate_result = flext_cli_aggregate_data(
        sample_data,
        group_by="role",
        sum_fields=["salary"],
    )
    if aggregate_result.success:
        pass

    return transform_result.success and aggregate_result.success


def test_exports():
    """Test export functionality."""
    import tempfile

    from flext_cli import flext_cli_batch_export, flext_cli_export

    # Test single export
    with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".json", delete=False) as tmp:
        export_result = flext_cli_export(sample_data, tmp.name, "json")

        # Cleanup
        if pathlib.Path(tmp.name).exists():
            pathlib.Path(tmp.name).unlink()

    # Test batch export
    with tempfile.TemporaryDirectory() as tmpdir:
        datasets = {"employees": sample_data, "summary": [{"total": len(sample_data)}]}
        batch_result = flext_cli_batch_export(datasets, tmpdir, "json")
        if batch_result.success:
            pass

    return export_result.success and batch_result.success


def test_core_helpers():
    """Test core helper utilities."""
    from flext_cli import flext_cli_unwrap_or_default, flext_cli_unwrap_or_none
    from flext_core import flext_fail, flext_ok

    # Test unwrap helpers
    success_result = flext_ok("test_data")
    fail_result = flext_fail("test_error")

    # Unwrap or default
    unwrapped_success = flext_cli_unwrap_or_default(success_result, "default")
    unwrapped_fail = flext_cli_unwrap_or_default(fail_result, "default")

    # Unwrap or none
    unwrapped_none = flext_cli_unwrap_or_none(fail_result)

    return (
        unwrapped_success == "test_data"
        and unwrapped_fail == "default"
        and unwrapped_none is None
    )


def main() -> int | None:
    """Run all tests."""
    test_results = []

    try:
        test_results.extend((test_basic_helpers(), test_new_helpers(), test_exports(), test_core_helpers()))

        success_count = sum(test_results)
        total_tests = len(test_results)

        if success_count == total_tests:
            return 0
        return 1

    except Exception:
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
