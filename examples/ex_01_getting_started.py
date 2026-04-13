"""FlextCliGettingStarted - Complete getting started example with flext-.

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

from examples import c, p, r, t
from flext_cli import cli, m


class FlextCliGettingStarted:
    """Complete getting started examples for flext-cli library usage."""

    def __init__(self) -> None:
        """Initialize with flext-cli instance."""
        super().__init__()

    def advanced_types_example(self) -> None:
        """Demonstrate advanced Python 3.13+ typing patterns with flext-cli."""
        output_format = c.Cli.OutputFormats.JSON
        cli.print(
            f"Selected format: {output_format.value}", style=c.Cli.MessageStyles.BLUE
        )
        valid_formats: tuple[str, ...] = tuple(
            sorted(c.Cli.OUTPUT_FORMATS),
        )
        cli.print(f"Available formats: {', '.join(valid_formats)}")
        sample_data: t.Cli.JsonMapping = {
            "status": c.Cli.CommandStatus.COMPLETED,
            "data": [1, 2, 3],
            "metadata": {"version": "1.0"},
        }
        cli.print(f"Sample data: {sample_data}", style=c.Cli.MessageStyles.GREEN)

    def display_user_data(self, user: m.Cli.DisplayData) -> None:
        """Show how to display YOUR data as a table."""
        table_data: t.StrMapping
        if isinstance(user.data, dict):
            table_data = {str(key): str(value) for key, value in user.data.items()}
        else:
            table_data = {"value": str(user.data)}
        cli.show_table(
            table_data,
            headers=["Field", "Value"],
            title="User Information",
        )

    def load_config(self, filepath: str) -> p.Result[m.Cli.LoadedConfig]:
        """Load YOUR settings from JSON. Returns r[LoadedConfig]; no None."""
        read_result = cli.read_json_file(filepath)
        if read_result.failure:
            cli.print(
                f"Failed to load: {read_result.error}", style=c.Cli.MessageStyles.RED
            )
            return r[m.Cli.LoadedConfig].fail(
                read_result.error or c.EXAMPLE_ERR_FAILED_LOAD_CONFIG,
            )
        if not isinstance(read_result.value, Mapping):
            return r[m.Cli.LoadedConfig].fail(c.EXAMPLE_ERR_CONFIG_CONTENT_MAPPING)
        return r[m.Cli.LoadedConfig].ok(
            m.Cli.LoadedConfig(content=dict(read_result.value)),
        )

    def process_data_with_flext_result(self) -> None:
        """Use r pattern in YOUR code - no try/except needed."""
        nonexistent_file = str(Path(tempfile.gettempdir()) / "nonexistent.json")
        result = cli.read_json_file(nonexistent_file)
        if result.success:
            cli.print("Data loaded successfully", style=c.Cli.MessageStyles.GREEN)
        else:
            cli.print(f"Error: {result.error}", style=c.Cli.MessageStyles.YELLOW)

    def run_examples(self) -> None:
        """Run all getting started examples."""
        cli.print(
            "=== Flext CLI Getting Started Examples ===",
            style=c.Cli.MessageStyles.BOLD_BLUE,
        )
        cli.print("\n1. Styled Output Examples:", style=c.Cli.MessageStyles.BOLD)
        self.your_function_after()
        cli.print("\n2. File I/O Examples:", style=c.Cli.MessageStyles.BOLD)
        self.process_data_with_flext_result()
        cli.print("\n3. Advanced Types Examples:", style=c.Cli.MessageStyles.BOLD)
        self.advanced_types_example()
        cli.print("\n✅ All examples completed!", style=c.Cli.MessageStyles.BOLD_GREEN)

    def save_config(self, settings: m.Cli.LoadedConfig, filepath: str) -> bool:
        """Save YOUR settings to JSON with proper error handling."""
        write_result = cli.write_json_file(filepath, settings.content)
        if write_result.failure:
            cli.print(
                f"Failed to save: {write_result.error}", style=c.Cli.MessageStyles.RED
            )
            return False
        cli.print(f"✅ Saved to {filepath}", style=c.Cli.MessageStyles.GREEN)
        return True

    def your_function_after(self) -> None:
        """Your new code using flext-cli."""
        cli.print(c.EXAMPLE_MSG_OPERATION_COMPLETED, style=c.Cli.MessageStyles.GREEN)
        cli.print(
            c.EXAMPLE_MSG_ERROR_SOMETHING_FAILED,
            style=c.Cli.MessageStyles.BOLD_RED,
        )


def main() -> None:
    """Main entry point for the getting started examples."""
    example = FlextCliGettingStarted()
    example.run_examples()


if __name__ == "__main__":
    main()
