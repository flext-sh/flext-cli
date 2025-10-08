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

import contextlib
import json
import pathlib
import tempfile

from flext_core import FlextResult

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_complete_workflow() -> FlextResult[dict]:
    """Show complete workflow with all features auto-configured."""
    cli.formatters.print("\n🔄 Complete Workflow:", style="bold cyan")

    # Auth auto-managed with secure storage
    auth_result = cli.save_auth_token("example_token")
    if auth_result.is_success:
        cli.formatters.print("✅ Auth token saved", style="green")

    # File I/O with auto-validation and formatting
    test_data = {"users": [{"name": "Alice", "role": "Admin"}]}

    # Use secure temporary file instead of hardcoded path
    with tempfile.NamedTemporaryFile(
        encoding="utf-8", mode="w", suffix=".json", delete=False
    ) as tmp_file:
        tmp_path = tmp_file.name

    try:
        write_result = cli.file_tools.write_json(test_data, tmp_path)
        if write_result.is_success:
            cli.formatters.print("✅ Data written to file", style="green")

        # Read with auto-validation
        read_result = cli.file_tools.read_json(tmp_path)
        if read_result.is_failure:
            return FlextResult[dict].fail(f"Read failed: {read_result.error}")

        data = read_result.unwrap()
        cli.formatters.print(f"✅ Data read: {data}", style="green")

        # Table display with optimized API
        if isinstance(data, dict) and "users" in data:
            users_data = {
                user["name"]: user["role"]
                for user in data["users"]
                if isinstance(user, dict)
            }
            table_result = cli.create_table(
                data=users_data, headers=["Name", "Role"], title="User Information"
            )
            if table_result.is_success:
                cli.formatters.console.print(table_result.unwrap())

        # Success output with auto-styling
        cli.formatters.print(
            "✅ Workflow complete - all features auto-configured", style="bold green"
        )

        return FlextResult[dict].ok(data)
    finally:
        # Clean up temporary file
        with contextlib.suppress(OSError):
            pathlib.Path(tmp_path).unlink()


def demonstrate_railway_pattern() -> None:
    """Show FlextResult railway pattern across modules."""
    cli.formatters.print("\n🚂 Railway Pattern:", style="bold cyan")

    # Create a temporary file for the demo
    test_data = {"status": "demo", "data": [1, 2, 3]}
    with tempfile.NamedTemporaryFile(
        encoding="utf-8", mode="w", suffix=".json", delete=False
    ) as tmp_file:
        tmp_path = tmp_file.name
        json.dump(test_data, tmp_file)

    try:
        # Chain operations with automatic error propagation
        result = (
            cli.file_tools.read_json(tmp_path)
            .map(lambda d: {**d, "processed": True} if isinstance(d, dict) else d)
            .map(lambda d: {**d, "validated": True} if isinstance(d, dict) else d)
        )

        if result.is_success:
            cli.formatters.print(
                f"✅ Chained operations: {result.unwrap()}", style="green"
            )
    finally:
        # Clean up temporary file
        with contextlib.suppress(OSError):
            pathlib.Path(tmp_path).unlink()


def demonstrate_zero_configuration() -> None:
    """Show zero-configuration usage."""
    cli.formatters.print("\n⚙️  Zero Configuration:", style="bold cyan")

    # Terminal capabilities auto-detected
    # Colors auto-enabled/disabled
    # Table format auto-selected
    # Output format auto-optimized
    cli.formatters.print(
        "✅ All features auto-configured - zero manual setup", style="cyan"
    )


def main() -> None:
    """Run all demonstrations."""
    cli.formatters.print("=" * 60, style="bold blue")
    cli.formatters.print("  Complete Integration Examples", style="bold white on blue")
    cli.formatters.print("=" * 60, style="bold blue")

    workflow_result = demonstrate_complete_workflow()
    if workflow_result.is_failure:
        cli.formatters.print(
            f"❌ Workflow failed: {workflow_result.error}", style="bold red"
        )

    demonstrate_railway_pattern()
    demonstrate_zero_configuration()

    cli.formatters.print("\n" + "=" * 60, style="bold blue")
    cli.formatters.print("  ✅ All integration examples completed!", style="bold green")
    cli.formatters.print("=" * 60, style="bold blue")


if __name__ == "__main__":
    main()
