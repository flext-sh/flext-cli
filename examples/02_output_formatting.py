"""Output Formatting - Auto-Configured Terminal Output.

Demonstrates auto-configuration: terminal detection, color support, formatting.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_styled_output() -> None:
    """Styled messages - auto-color detection."""
    cli.output.print_success("✅ Success - auto-styled")
    cli.output.print_error("❌ Error - auto-styled")
    cli.output.print_warning("⚠️  Warning - auto-styled")
    cli.output.print_message("ℹ️  Info - auto-styled")


def demonstrate_table_formatting() -> None:
    """Table auto-formatting based on terminal width."""
    users = [
        {"name": "Alice", "age": 30, "role": "Admin"},
        {"name": "Bob", "age": 25, "role": "Developer"},
    ]

    table_result = cli.tables.create_grid_table(users)
    if table_result.is_success:
        print(table_result.value)


def demonstrate_data_formatting() -> None:
    """Data formatting - auto-indented, auto-colored."""
    data = {"status": "success", "count": 42, "items": ["a", "b", "c"]}

    json_result = cli.output.format_json(data)
    if json_result.is_success:
        print(json_result.value)


def main() -> None:
    """Run all demonstrations."""
    demonstrate_styled_output()
    demonstrate_table_formatting()
    demonstrate_data_formatting()


if __name__ == "__main__":
    main()
