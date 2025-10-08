"""Getting Started - Basic FlextCli Usage.

Demonstrates the fundamentals of using flext-cli as a library with optimized API.

Key Features:
- Singleton pattern with module-level instance (zero repetition)
- Direct formatters access for output operations
- FlextResult railway pattern for error handling
- Zero manual configuration required

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli import FlextCli

# Module-level singleton - ONE TIME initialization
cli = FlextCli.get_instance()


def demonstrate_singleton_pattern() -> None:
    """Singleton pattern - auto-configured, reusable."""
    # Direct formatters access - optimized API
    cli.formatters.print(
        "✅ Singleton pattern - zero repetitive initialization", style="bold green"
    )

    # Verify same instance everywhere
    cli2 = FlextCli.get_instance()
    if cli is cli2:
        cli.formatters.print("✅ Singleton verified - same instance", style="green")
    else:
        cli.formatters.print("❌ Singleton pattern failed", style="bold red")


def demonstrate_auto_configuration() -> None:
    """Auto-configuration - zero manual setup."""
    # Everything auto-configured by library
    cli.formatters.print("\\n📋 Table Example:", style="bold cyan")

    users = {"Alice": "30", "Bob": "25", "Charlie": "35"}
    table_result = cli.create_table(
        data=users, headers=["Name", "Age"], title="User Information"
    )

    if table_result.is_success:
        cli.formatters.console.print(table_result.unwrap())


def demonstrate_basic_output() -> None:
    """Basic output operations using optimized API."""
    cli.formatters.print("\\n🎨 Output Styles:", style="bold cyan")
    cli.formatters.print("✅ Success: Operation completed!", style="bold green")
    cli.formatters.print("❌ Error: Something went wrong", style="bold red")
    cli.formatters.print("⚠️  Warning: Proceed with caution", style="bold yellow")
    cli.formatters.print("ℹ️  Info: General information", style="cyan")


def demonstrate_flext_result_pattern() -> None:
    """FlextResult railway-oriented programming."""

    def process_data(data: dict) -> FlextResult[dict]:
        if not data:
            return FlextResult[dict].fail("Data cannot be empty")
        return FlextResult[dict].ok({"original": data, "processed": True})

    # Railway pattern - chain operations
    cli.formatters.print("\\n🚂 FlextResult Railway Pattern:", style="bold cyan")

    result = (
        process_data({"key": "value"})
        .map(lambda d: {**d, "chained": True})
        .map(lambda d: {**d, "final": "processed"})
    )

    if result.is_success:
        cli.formatters.print(
            f"✅ Processed successfully: {result.unwrap()}", style="green"
        )
    else:
        cli.formatters.print(f"❌ Processing failed: {result.error}", style="bold red")


def main() -> None:
    """Run all demonstrations."""
    cli.formatters.print("=" * 60, style="bold blue")
    cli.formatters.print(
        "  FLEXT-CLI Getting Started Examples", style="bold white on blue"
    )
    cli.formatters.print("=" * 60, style="bold blue")

    demonstrate_singleton_pattern()
    demonstrate_auto_configuration()
    demonstrate_basic_output()
    demonstrate_flext_result_pattern()

    cli.formatters.print("\\n" + "=" * 60, style="bold blue")
    cli.formatters.print(
        "  ✅ All examples completed successfully!", style="bold green"
    )
    cli.formatters.print("=" * 60, style="bold blue")


if __name__ == "__main__":
    main()
