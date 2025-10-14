"""Getting Started - Using flext-cli as a Library in YOUR Code.

WHAT IS flext-cli?
A CLI foundation library that provides:
- Styled console output (Rich integration)
- Table formatting (Rich + Tabulate)
- File I/O (JSON, YAML, CSV)
- Error handling (FlextCore.Result pattern)
- Configuration management
- User prompts

WHEN TO USE:
- Building a Python CLI application
- Need styled console output
- Want easy table formatting
- Need file I/O with error handling
- Building interactive CLI tools

HOW TO INTEGRATE INTO YOUR PROJECT:
1. Install: pip install flext-cli
2. Import: from flext_cli import FlextCli
3. Use: cli = FlextCli.get_instance()

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import cast

from flext_cli import FlextCli
from flext_cli.typings import FlextCliTypes

# Initialize once - reuse everywhere
cli = FlextCli.get_instance()


# ============================================================================
# PATTERN 1: Replace print() with styled output
# ============================================================================


def your_function_before() -> None:
    """Your old code using print()."""


def your_function_after() -> None:
    """Your new code using flext-cli."""
    cli.print("Operation completed", style="green")
    cli.print("ERROR: Something failed", style="bold red")


# ============================================================================
# PATTERN 2: Display data as tables
# ============================================================================


def display_user_data(user: FlextCliTypes.Data.CliDataDict) -> None:
    """Show how to display YOUR data as a table."""
    # Your data (from database, API, etc.)
    # Cast to expected type for table creation
    table_result = cli.create_table(
        data=user,
        headers=["Field", "Value"],
        title="User Information",
    )

    if table_result.is_success:
        cli.print_table(table_result.unwrap())


# ============================================================================
# PATTERN 3: File I/O with error handling
# ============================================================================


def save_config(config: FlextCliTypes.Data.CliDataDict, filepath: str) -> bool:
    """Save YOUR config to JSON with proper error handling."""
    write_result = cli.file_tools.write_json_file(filepath, config)

    if write_result.is_failure:
        cli.print(f"Failed to save: {write_result.error}", style="bold red")
        return False

    cli.print(f"✅ Saved to {filepath}", style="green")
    return True


def load_config(filepath: str) -> FlextCliTypes.Data.CliDataDict | None:
    """Load YOUR config from JSON with error handling."""
    read_result = cli.file_tools.read_json_file(filepath)

    if read_result.is_failure:
        cli.print(f"Failed to load: {read_result.error}", style="bold red")
        return None

    # Type narrowing: ensure we return a dict
    data = read_result.unwrap()
    if isinstance(data, dict):
        # Cast to expected type (runtime type is compatible)
        return cast("FlextCliTypes.Data.CliDataDict", data)
    return None


# ============================================================================
# PATTERN 4: Error handling without exceptions
# ============================================================================


def process_data_with_flext_result() -> None:
    """Use FlextCore.Result pattern in YOUR code - no try/except needed."""
    # This won't throw an exception even if file doesn't exist
    nonexistent_file = str(Path(tempfile.gettempdir()) / "nonexistent.json")
    result = cli.file_tools.read_json_file(nonexistent_file)

    if result.is_success:
        result.unwrap()
        # Process your data
        cli.print("Data loaded successfully", style="green")
    else:
        # Handle error gracefully
        cli.print(f"Error: {result.error}", style="yellow")
        # Continue execution - no crash!


# ============================================================================
# REAL USAGE EXAMPLE
# ============================================================================


def main() -> None:
    """Example of how YOU would use flext-cli in your project."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Using flext-cli in YOUR Code", style="bold white")
    cli.print("=" * 70, style="bold blue")

    # Example 1: Styled output
    cli.print("\n1. Styled Console Output:", style="bold cyan")
    cli.print("   Replace print() with styled output:")
    your_function_after()

    # Example 2: Tables
    cli.print("\n2. Display Data as Tables:", style="bold cyan")
    user_data: FlextCliTypes.Data.CliDataDict = {
        "name": "Alice",
        "email": "alice@example.com",
        "role": "admin",
    }
    display_user_data(user_data)

    # Example 3: File I/O
    cli.print("\n3. File Operations:", style="bold cyan")
    temp_file = Path(tempfile.gettempdir()) / "my_config.json"
    config: FlextCliTypes.Data.CliDataDict = {"app": "my-cli-tool", "version": "1.0.0"}

    save_config(config, str(temp_file))
    loaded = load_config(str(temp_file))

    if loaded:
        cli.print(f"   Loaded: {loaded}", style="cyan")

    temp_file.unlink(missing_ok=True)

    # Example 4: Error handling
    cli.print("\n4. Error Handling (No Exceptions):", style="bold cyan")
    process_data_with_flext_result()

    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Integration Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")

    # Show how to integrate into YOUR code
    cli.print("\n📚 Integration Steps:", style="bold cyan")
    cli.print("  1. Import: from flext_cli import FlextCli", style="white")
    cli.print("  2. Init:   cli = FlextCli.get_instance()", style="white")
    cli.print(
        "  3. Use:    cli.print(), cli.file_tools.write_json_file(), etc.",
        style="white",
    )
    cli.print(
        "\n💡 All methods return FlextCore.Result for error handling without exceptions!",
        style="yellow",
    )


if __name__ == "__main__":
    main()
