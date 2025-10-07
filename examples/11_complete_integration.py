"""Complete Integration - All Features Together.

Demonstrates complete flext-cli integration using all modules.

Key Features:
- Singleton pattern eliminates repetitive initialization
- Auto-configuration propagates to all services
- FlextResult railway pattern throughout
- All modules work seamlessly together

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pathlib
from typing import cast

from flext_core import FlextResult

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_complete_workflow() -> FlextResult[dict]:
    """Show complete workflow with all features auto-configured."""
    # Auth auto-managed with secure storage
    cli.auth.save_auth_token("example_token")

    # File I/O with auto-validation and formatting
    import tempfile

    test_data = {"users": [{"name": "Alice", "role": "Admin"}]}

    # Use secure temporary file instead of hardcoded path
    with tempfile.NamedTemporaryFile(
        encoding="utf-8", mode="w", suffix=".json", delete=False
    ) as tmp_file:
        tmp_path = tmp_file.name

    try:
        cli.file_tools.write_json(tmp_path, cast("object", test_data))

        # Read with auto-validation
        read_result = cli.file_tools.read_json(tmp_path)
        if read_result.is_failure:
            return FlextResult[dict].fail(f"Read failed: {read_result.error}")

        # Table display with auto-format selection
        table_result = cli.tables.create_grid_table(
            cast("list[dict[str, object]]", cast("dict", read_result.value)["users"])
        )
        if table_result.is_success:
            print(table_result.value)  # Auto-formatted for terminal

        # Success output with auto-styling
        cli.output.print_success("✅ Workflow complete - all features auto-configured")

        return FlextResult[dict].ok(cast("dict", read_result.value))
    finally:
        # Clean up temporary file
        try:
            pathlib.Path(tmp_path).unlink()
        except OSError:
            pass  # File may have been cleaned up already


def demonstrate_railway_pattern() -> None:
    """Show FlextResult railway pattern across modules."""
    import tempfile

    # Create a temporary file for the demo
    test_data = {"status": "demo", "data": [1, 2, 3]}
    with tempfile.NamedTemporaryFile(
        encoding="utf-8", mode="w", suffix=".json", delete=False
    ) as tmp_file:
        tmp_path = tmp_file.name
        import json

        json.dump(test_data, tmp_file)

    try:
        # Chain operations with automatic error propagation
        result = (
            cli.file_tools.read_json(tmp_path)
            .map(lambda d: {**d, "processed": True})
            .map(lambda d: {**d, "validated": True})
        )

        if result.is_success:
            cli.output.print_success(f"Chained operations: {result.value}")
    finally:
        # Clean up temporary file
        try:
            pathlib.Path(tmp_path).unlink()
        except OSError:
            pass  # File may have been cleaned up already


def demonstrate_zero_configuration() -> None:
    """Show zero-configuration usage."""
    # Terminal capabilities auto-detected
    # Colors auto-enabled/disabled
    # Table format auto-selected
    # Output format auto-optimized
    cli.output.print_message("All features auto-configured - zero manual setup")


def main() -> None:
    """Run all demonstrations."""
    workflow_result = demonstrate_complete_workflow()
    if workflow_result.is_failure:
        print(f"Workflow failed: {workflow_result.error}")

    demonstrate_railway_pattern()
    demonstrate_zero_configuration()


if __name__ == "__main__":
    main()
