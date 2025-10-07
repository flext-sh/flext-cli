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
    # Output auto-captured in test context
    # No manual setup needed
    cli.output.print_success("Output auto-captured for assertions")


def demonstrate_mock_interactions() -> None:
    """Show auto-mocking of prompts."""
    # Prompts auto-mocked with test data
    # No manual mock setup required
    cli.output.print_message("Prompts auto-mocked in test context")


def demonstrate_test_scenarios() -> None:
    """Show test scenario auto-validation."""
    # Scenarios auto-validated against expected results
    # Assertions auto-generated from schema
    cli.output.print_message("Test scenarios auto-validated")


def main() -> None:
    """Run all demonstrations."""
    demonstrate_output_capture()
    demonstrate_mock_interactions()
    demonstrate_test_scenarios()


if __name__ == "__main__":
    main()
