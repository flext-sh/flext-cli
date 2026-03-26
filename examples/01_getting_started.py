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
from collections.abc import Mapping
from pathlib import Path

from flext_core import r

from flext_cli import c, cli, m, t


class FlextCliGettingStarted:
    """Complete getting started examples for flext-cli library usage."""

    def __init__(self) -> None:
        """Initialize with flext-cli instance."""
        super().__init__()

    def advanced_types_example(self) -> None:
        """Demonstrate advanced Python 3.13+ typing patterns with flext-cli."""
        output_format = c.Cli.OutputFormats.JSON
        cli.print(f"Selected format: {output_format.value}", style="blue")
        valid_formats: tuple[str, ...] = tuple(
            sorted(c.Cli.ValidationLists.OUTPUT_FORMATS),
        )
        cli.print(f"Available formats: {', '.join(valid_formats)}")
        sample_data: t.Cli.JsonDict = {
            "status": c.Cli.CommandStatus.COMPLETED.value,
            "data": [1, 2, 3],
            "metadata": {"version": "1.0"},
        }
        cli.print(f"Sample data: {sample_data}", style="green")

    def display_user_data(self, user: m.Cli.DisplayData) -> None:
        """Show how to display YOUR data as a table."""
        table_data: Mapping[str, str]
        if isinstance(user.data, dict):
            table_data = {str(key): str(value) for key, value in user.data.items()}
        else:
            table_data = {"value": str(user.data)}
        cli.show_table(
            table_data,
            headers=["Field", "Value"],
            title="User Information",
        )

    def load_config(self, filepath: str) -> r[m.Cli.LoadedConfig]:
        """Load YOUR config from JSON. Returns r[LoadedConfig]; no None."""
        read_result = cli.read_json_file(filepath)
        if read_result.is_failure:
            cli.print(f"Failed to load: {read_result.error}", style="red")
            return r[m.Cli.LoadedConfig].fail(
                read_result.error or "Failed to load config",
            )
        return r[m.Cli.LoadedConfig].ok(m.Cli.LoadedConfig(content=read_result.value))

    def process_data_with_flext_result(self) -> None:
        """Use r pattern in YOUR code - no try/except needed."""
        nonexistent_file = str(Path(tempfile.gettempdir()) / "nonexistent.json")
        result = cli.read_json_file(nonexistent_file)
        if result.is_success:
            cli.print("Data loaded successfully", style="green")
        else:
            cli.print(f"Error: {result.error}", style="yellow")

    def run_examples(self) -> None:
        """Run all getting started examples."""
        cli.print("=== Flext CLI Getting Started Examples ===", style="bold blue")
        cli.print("\n1. Styled Output Examples:", style="bold")
        self.your_function_after()
        cli.print("\n2. File I/O Examples:", style="bold")
        self.process_data_with_flext_result()
        cli.print("\n3. Advanced Types Examples:", style="bold")
        self.advanced_types_example()
        cli.print("\n✅ All examples completed!", style="bold green")

    def save_config(self, config: m.Cli.LoadedConfig, filepath: str) -> bool:
        """Save YOUR config to JSON with proper error handling."""
        write_result = cli.write_json_file(filepath, config.content)
        if write_result.is_failure:
            cli.print(f"Failed to save: {write_result.error}", style="red")
            return False
        cli.print(f"✅ Saved to {filepath}", style="green")
        return True

    def your_function_after(self) -> None:
        """Your new code using flext-cli."""
        cli.print("Operation completed", style="green")
        cli.print("ERROR: Something failed", style="bold red")

    def your_function_before(self) -> None:
        """Your old code using print()."""


def main() -> None:
    """Main entry point for the getting started examples."""
    example = FlextCliGettingStarted()
    example.run_examples()


if __name__ == "__main__":
    main()
