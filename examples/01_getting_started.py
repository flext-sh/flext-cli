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

from flext_core import r

from flext_cli import FlextCli, c, m, t


class FlextCliGettingStarted:
    """Complete getting started examples for flext-cli library usage.

    Demonstrates all major flext-cli capabilities:
    - Styled console output with Rich integration
    - Table formatting with tabulate and Rich
    - File I/O with JSON, YAML, CSV support
    - Railway-oriented error handling (r)
    - Configuration management patterns
    - Interactive user prompts

    All examples use modern Python 3.13+ features and follow FLEXT standards.
    """

    def __init__(self) -> None:
        """Initialize with flext-cli instance."""
        super().__init__()
        self.cli = FlextCli()

    def advanced_types_example(self) -> None:
        """Demonstrate advanced Python 3.13+ typing patterns with flext-cli.

        Shows how to use:
        - StrEnum for runtime validation
        - collections.abc.Mapping for immutable data
        - PEP 695 type aliases
        - Advanced Literal unions
        """
        output_format = c.Cli.OutputFormats.JSON
        self.cli.print(f"Selected format: {output_format.value}", style="blue")
        valid_formats: tuple[str, ...] = tuple(
            sorted(c.Cli.ValidationLists.OUTPUT_FORMATS)
        )
        self.cli.print(f"Available formats: {', '.join(valid_formats)}")
        sample_data: t.Cli.JsonDict = {
            "status": c.Cli.CommandStatus.COMPLETED.value,
            "data": [1, 2, 3],
            "metadata": {"version": "1.0"},
        }
        self.cli.print(f"Sample data: {sample_data}", style="green")

    def display_user_data(self, user: m.Cli.DisplayData) -> None:
        """Show how to display YOUR data as a table."""
        self.cli.show_table(
            dict(user.data), headers=["Field", "Value"], title="User Information"
        )

    def load_config(self, filepath: str) -> r[m.Cli.LoadedConfig]:
        """Load YOUR config from JSON. Returns r[LoadedConfig]; no None."""
        read_result = self.cli.file_tools.read_json_dict(filepath)
        if read_result.is_failure:
            self.cli.print(f"Failed to load: {read_result.error}", style="red")
            return r[m.Cli.LoadedConfig].fail(
                read_result.error or "Failed to load config"
            )
        return r[m.Cli.LoadedConfig].ok(m.Cli.LoadedConfig(content=read_result.value))

    def process_data_with_flext_result(self) -> None:
        """Use r pattern in YOUR code - no try/except needed."""
        nonexistent_file = str(Path(tempfile.gettempdir()) / "nonexistent.json")
        result = self.cli.file_tools.read_json_dict(nonexistent_file)
        if result.is_success:
            self.cli.print("Data loaded successfully", style="green")
        else:
            self.cli.print(f"Error: {result.error}", style="yellow")

    def run_examples(self) -> None:
        """Run all getting started examples."""
        self.cli.print("=== Flext CLI Getting Started Examples ===", style="bold blue")
        self.cli.print("\n1. Styled Output Examples:", style="bold")
        self.your_function_after()
        self.cli.print("\n2. File I/O Examples:", style="bold")
        self.process_data_with_flext_result()
        self.cli.print("\n3. Advanced Types Examples:", style="bold")
        self.advanced_types_example()
        self.cli.print("\n✅ All examples completed!", style="bold green")

    def save_config(self, config: m.Cli.LoadedConfig, filepath: str) -> bool:
        """Save YOUR config to JSON with proper error handling."""
        write_result = self.cli.file_tools.write_json_file(filepath, config.content)
        if write_result.is_failure:
            self.cli.print(f"Failed to save: {write_result.error}", style="red")
            return False
        self.cli.print(f"✅ Saved to {filepath}", style="green")
        return True

    def your_function_after(self) -> None:
        """Your new code using flext-cli."""
        self.cli.print("Operation completed", style="green")
        self.cli.print("ERROR: Something failed", style="bold red")

    def your_function_before(self) -> None:
        """Your old code using print()."""


def main() -> None:
    """Main entry point for the getting started examples."""
    example = FlextCliGettingStarted()
    example.run_examples()


if __name__ == "__main__":
    main()
