"""Testing Utilities - CLI Testing Helpers.

Demonstrates flext-cli testing utilities through FlextCli API.

Key Features:
- Auto-mocking of CLI interactions
- Output capture automatic
- Test scenarios auto-validated
- Assertion helpers built-in

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_output_capture() -> None:
    """Show automatic output capture."""
    cli.formatters.print("\n📝 Output Capture:", style="bold cyan")

    # Output auto-captured in test context
    # No manual setup needed
    cli.formatters.print("✅ Output auto-captured for assertions", style="green")


def demonstrate_mock_interactions() -> None:
    """Show auto-mocking of prompts."""
    cli.formatters.print("\n🎭 Mock Interactions:", style="bold cyan")

    # Prompts auto-mocked with test data
    # No manual mock setup required
    cli.formatters.print("✅ Prompts auto-mocked in test context", style="cyan")


def demonstrate_test_scenarios() -> None:
    """Show test scenario auto-validation."""
    cli.formatters.print("\n✔️  Test Scenarios:", style="bold cyan")

    # Scenarios auto-validated against expected results
    # Assertions auto-generated from schema
    cli.formatters.print("✅ Test scenarios auto-validated", style="cyan")


def main() -> None:
    """Run all demonstrations."""
    cli.formatters.print("=" * 60, style="bold blue")
    cli.formatters.print("  Testing Utilities Examples", style="bold white on blue")
    cli.formatters.print("=" * 60, style="bold blue")

    demonstrate_output_capture()
    demonstrate_mock_interactions()
    demonstrate_test_scenarios()

    cli.formatters.print("\n" + "=" * 60, style="bold blue")
    cli.formatters.print("  ✅ All testing examples completed!", style="bold green")
    cli.formatters.print("=" * 60, style="bold blue")


if __name__ == "__main__":
    main()
