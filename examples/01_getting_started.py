"""FlextCliGettingStarted - Complete getting started example with flext-cli.

This module demonstrates how to use flext-cli as a library in your Python projects.
Provides comprehensive examples of all major flext-cli features including styled output,
table formatting, file I/O, error handling, and configuration management.

SCOPE: Getting started guide, integration examples, best practices.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_cli import FlextCli, FlextCliTypes


class FlextCliGettingStarted:
    """Complete getting started examples for flext-cli library usage.

    Demonstrates all major flext-cli capabilities:
    - Styled console output with Rich integration
    - Table formatting with tabulate and Rich
    - File I/O with JSON, YAML, CSV support
    - Railway-oriented error handling (FlextResult)
    - Configuration management patterns
    - Interactive user prompts

    All examples use modern Python 3.13+ features and follow FLEXT standards.
    """

    def __init__(self) -> None:
        """Initialize with flext-cli instance."""
        self.cli = FlextCli()

    # ============================================================================
    # PATTERN 1: Replace print() with styled output
    # ============================================================================

    def your_function_before(self) -> None:
        """Your old code using print()."""

    def your_function_after(self) -> None:
        """Your new code using flext-cli."""
        self.cli.print("Operation completed", style="green")
        self.cli.print("ERROR: Something failed", style="bold red")

    # ============================================================================
    # PATTERN 2: Display data as tables
    # ============================================================================

    def display_user_data(self, user: FlextCliTypes.Data.CliDataDict) -> None:
        """Show how to display YOUR data as a table."""
        # Your data (from database, API, etc.)
        # Create table from user data
        table_result = self.cli.create_table(
            data=user,
            headers=["Field", "Value"],
            title="User Information",
        )

        if table_result.is_success:
            self.cli.print_table(table_result.unwrap())

    # ============================================================================
    # PATTERN 3: File I/O with error handling
    # ============================================================================

    def save_config(
        self, config: FlextCliTypes.Data.CliDataDict, filepath: str
    ) -> bool:
        """Save YOUR config to JSON with proper error handling."""
        write_result = self.cli.file_tools.write_json_file(
            filepath,
            config,
        )

        if write_result.is_failure:
            self.cli.output.print_message(f"Failed to save: {write_result.error}")
            return False

        self.cli.output.print_message(f"✅ Saved to {filepath}")
        return True

    def load_config(self, filepath: str) -> dict[str, object] | None:
        """Load YOUR config from JSON with error handling."""
        read_result = self.cli.file_tools.read_json_file(filepath)

        if read_result.is_failure:
            self.cli.output.print_message(f"Failed to load: {read_result.error}")
            return None

        # Type narrowing: ensure we return a dict
        data = read_result.unwrap()
        if isinstance(data, dict):
            return data
        return None

    # ============================================================================
    # PATTERN 4: Error handling without exceptions
    # ============================================================================

    def process_data_with_flext_result(self) -> None:
        """Use FlextResult pattern in YOUR code - no try/except needed."""
        # This won't throw an exception even if file doesn't exist
        nonexistent_file = str(Path(tempfile.gettempdir()) / "nonexistent.json")
        result = self.cli.file_tools.read_json_file(nonexistent_file)

        if result.is_success:
            result.unwrap()
            # Process your data
            self.cli.print("Data loaded successfully", style="green")
        else:
            # Handle error gracefully
            self.cli.print(f"Error: {result.error}", style="yellow")
            # Continue execution - no crash!


# ============================================================================
# REAL USAGE EXAMPLE
# ============================================================================


def main() -> None:
    """Main entry point for the getting started examples."""
    example = FlextCliGettingStarted()
    example.run_examples()


if __name__ == "__main__":
    main()
