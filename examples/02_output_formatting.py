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
    cli.formatters.print("✅ Success - auto-styled", style="bold green")
    cli.formatters.print("❌ Error - auto-styled", style="bold red")
    cli.formatters.print("⚠️  Warning - auto-styled", style="bold yellow")
    cli.formatters.print("ℹ️  Info - auto-styled", style="cyan")


def demonstrate_table_formatting() -> None:
    """Table auto-formatting based on terminal width."""
    users = {
        "Alice": "30 | Admin",
        "Bob": "25 | Developer",
        "Charlie": "35 | Manager",
    }

    cli.formatters.print("\n📊 User Table:", style="bold cyan")
    table_result = cli.create_table(
        data=users, headers=["Name", "Age | Role"], title="User Information"
    )
    if table_result.is_success:
        cli.formatters.console.print(table_result.unwrap())


def demonstrate_data_formatting() -> None:
    """Data formatting - auto-indented, auto-colored."""
    import json

    data = {"status": "success", "count": 42, "items": ["a", "b", "c"]}

    cli.formatters.print("\n📄 JSON Output:", style="bold cyan")
    formatted_json = json.dumps(data, indent=2)
    cli.formatters.print(formatted_json, style="green")


def main() -> None:
    """Run all demonstrations."""
    cli.formatters.print("=" * 60, style="bold blue")
    cli.formatters.print("  Output Formatting Examples", style="bold white on blue")
    cli.formatters.print("=" * 60, style="bold blue")

    demonstrate_styled_output()
    demonstrate_table_formatting()
    demonstrate_data_formatting()

    cli.formatters.print("\n" + "=" * 60, style="bold blue")
    cli.formatters.print("  ✅ All formatting examples completed!", style="bold green")
    cli.formatters.print("=" * 60, style="bold blue")


if __name__ == "__main__":
    main()
