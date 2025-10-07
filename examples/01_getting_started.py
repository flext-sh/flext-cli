"""Getting Started - Basic FlextCli Usage.

Demonstrates the fundamentals of using flext-cli as a library.

Key Features:
- Singleton pattern with module-level instance (zero repetition)
- Auto-configuration via library defaults (zero manual setup)
- FlextResult railway pattern for error handling

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

from flext_core import FlextResult

from flext_cli import FlextCli

# Module-level singleton - ONE TIME initialization
cli = FlextCli.get_instance()


def demonstrate_singleton_pattern() -> None:
    """Singleton pattern - auto-configured, reusable."""
    # Direct access - no repeated get_instance() calls
    cli.output.print_success("Singleton pattern - zero repetitive initialization")

    # Verify same instance everywhere
    cli2 = FlextCli.get_instance()
    if cli is not cli2:
        cli.output.print_error("Singleton pattern failed")
        return


def demonstrate_auto_configuration() -> None:
    """Auto-configuration - zero manual setup."""
    # Everything auto-configured by library
    users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    table_result = cli.tables.create_grid_table(cast("list[dict[str, object]]", users))

    if table_result.is_success:
        print(table_result.value)


def demonstrate_basic_output() -> None:
    """Basic output operations."""
    cli.output.print_success("Operation completed!")
    cli.output.print_error("Error message")
    cli.output.print_warning("Warning message")
    cli.output.print_message("Info message")


def demonstrate_flext_result_pattern() -> None:
    """FlextResult railway-oriented programming."""

    def process_data(data: dict) -> FlextResult[dict]:
        if not data:
            return FlextResult[dict].fail("Data cannot be empty")
        return FlextResult[dict].ok({"original": data, "processed": True})

    # Railway pattern - chain operations
    result = (
        process_data({"key": "value"})
        .map(lambda d: {**d, "chained": True})
        .map(lambda d: {**d, "final": "processed"})
    )

    if result.is_success:
        cli.output.print_success(f"Processed: {result.value}")


def main() -> None:
    """Run all demonstrations."""
    demonstrate_singleton_pattern()
    demonstrate_auto_configuration()
    demonstrate_basic_output()
    demonstrate_flext_result_pattern()


if __name__ == "__main__":
    main()
