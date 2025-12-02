"""Complete Integration - Building Complete CLI Apps with flext-cli.

WHEN TO USE THIS:
- Building complete CLI applications
- Integrating all flext-cli features
- Creating production-ready CLI tools
- Need end-to-end examples
- Want to see all patterns together

FLEXT-CLI PROVIDES:
- Complete CLI foundation library
- All features work seamlessly together
- Singleton pattern for consistency
- FlextResult railway pattern throughout
- Professional CLI development toolkit

HOW TO USE IN YOUR CLI:
See complete integration patterns for YOUR CLI application

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from flext_core import FlextResult, FlextTypes, FlextUtilities

from flext_cli import FlextCli, FlextCliPrompts, FlextCliTypes

cli = FlextCli()


# ============================================================================
# COMPLETE CLI APPLICATION EXAMPLE
# ============================================================================


class DataManagerCLI:
    """Complete CLI application using all flext-cli features."""

    def __init__(self) -> None:
        """Initialize data manager CLI with temporary data file."""
        super().__init__()
        self.cli = FlextCli()
        self.data_file = Path(tempfile.gettempdir()) / "app_data.json"

    def display_welcome(self) -> None:
        """Show welcome message with styled output."""
        self.cli.output.print_message("=" * 70, style="bold blue")
        self.cli.output.print_message(
            "  📊 Data Manager CLI", style="bold white on blue"
        )
        self.cli.output.print_message("=" * 70, style="bold blue")

    def save_data(self, data: FlextCliTypes.Data.CliDataDict) -> FlextResult[bool]:
        """Save data with proper error handling."""
        write_result = self.cli.file_tools.write_json_file(self.data_file, data)

        if write_result.is_failure:
            error_msg = write_result.error or "Unknown error"
            self.cli.output.print_message(
                f"❌ Save failed: {error_msg}", style="bold red"
            )
            return FlextResult[bool].fail(error_msg)

        self.cli.output.print_message(
            f"✅ Data saved to {self.data_file.name}", style="green"
        )
        return FlextResult[bool].ok(True)

    def load_data(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Load data with error handling."""
        if not self.data_file.exists():
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                "No data file found",
            )

        read_result = self.cli.file_tools.read_json_file(self.data_file)

        if read_result.is_failure:
            error_msg = read_result.error or "Unknown error"
            self.cli.output.print_message(
                f"❌ Load failed: {error_msg}", style="bold red"
            )
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(error_msg)

        # Type narrowing: ensure we return a dict
        data = read_result.unwrap()
        if not isinstance(data, dict):
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                "Data is not a dictionary",
            )
        self.cli.output.print_message("✅ Data loaded successfully", style="green")
        # Convert to JsonDict-compatible dict using FlextUtilities
        converted_data: FlextCliTypes.Data.CliDataDict = (
            FlextUtilities.DataMapper.convert_dict_to_json(data)
        )
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok(converted_data)

    def display_data(self, data: Mapping[str, FlextTypes.GeneralValueType]) -> None:
        """Display data as formatted table."""
        if not data:
            self.cli.output.print_message("⚠️  No data to display", style="yellow")
            return

        table_result = self.cli.create_table(
            data=data,
            headers=["Field", "Value"],
            title="📋 Current Data",
        )

        if table_result.is_success:
            self.cli.print_table(table_result.unwrap())

    def add_entry(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Add new entry with user prompts."""
        prompts = FlextCliPrompts(interactive_mode=False)

        # Get key
        key_result = prompts.prompt("Enter key:", default="sample_key")
        if key_result.is_failure:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Prompt failed: {key_result.error}",
            )

        key = key_result.unwrap()

        # Get value
        value_result = prompts.prompt("Enter value:", default="sample_value")
        if value_result.is_failure:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Prompt failed: {value_result.error}",
            )

        value = value_result.unwrap()

        entry = {key: value}
        self.cli.output.print_message(
            f"✅ Created entry: {key} = {value}", style="green"
        )
        # Convert to JsonDict-compatible dict using FlextUtilities
        converted_entry: FlextCliTypes.Data.CliDataDict = (
            FlextUtilities.DataMapper.convert_dict_to_json(
                cast("dict[str, FlextTypes.GeneralValueType]", entry)
            )
        )
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok(converted_entry)

    def run_workflow(self) -> FlextResult[bool]:
        """Complete workflow integrating all features."""
        # Step 1: Welcome
        self.display_welcome()

        # Step 2: Load existing data (or create new)
        self.cli.output.print_message("\n📂 Loading existing data...", style="cyan")
        load_result = self.load_data()
        current_data: dict[str, FlextTypes.GeneralValueType] = {}

        if load_result.is_success:
            # Load existing data for update operations
            # Convert Mapping to dict for mutability
            loaded_data = load_result.unwrap()
            current_data = dict(loaded_data)
        else:
            self.cli.output.print_message("   Creating new dataset", style="yellow")

        # Step 3: Display current data
        self.cli.output.print_message("\n📊 Current Data:", style="bold cyan")
        self.display_data(current_data)

        # Step 4: Add new entry
        self.cli.output.print_message("\n➕ Adding New Entry:", style="bold cyan")
        entry_result = self.add_entry()

        if entry_result.is_failure:
            return FlextResult[bool].fail(f"Add entry failed: {entry_result.error}")

        new_entry = entry_result.unwrap()
        # Convert Mapping to dict for update
        current_data.update(dict(new_entry))

        # Step 5: Save updated data
        self.cli.output.print_message("\n💾 Saving Data:", style="bold cyan")
        # Cast to expected type for save function
        save_result = self.save_data(current_data)

        if save_result.is_failure:
            return FlextResult[bool].fail(f"Save failed: {save_result.error}")

        # Step 6: Display final result
        self.cli.output.print_message("\n✨ Final Result:", style="bold cyan")
        # Cast to expected type for display function
        self.display_data(current_data)

        return FlextResult[bool].ok(True)


# ============================================================================
# RAILWAY PATTERN EXAMPLE
# ============================================================================


def process_with_railway_pattern(
    input_data: FlextCliTypes.Data.CliDataDict,
) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
    """Show railway pattern chaining operations."""
    # Removed unused temp_file variable

    # Chain operations using FlextResult
    # Step 1: Validate
    step1_data: FlextCliTypes.Data.CliDataDict = {**input_data, "validated": True}
    # Step 2: Transform
    step2_data: FlextCliTypes.Data.CliDataDict = {**step1_data, "processed": True}
    # Step 3: Enrich
    final_data: FlextCliTypes.Data.CliDataDict = cast(
        "FlextCliTypes.Data.CliDataDict",
        {**step2_data, "enriched": True},
    )

    result: FlextResult[FlextCliTypes.Data.CliDataDict] = FlextResult[
        FlextCliTypes.Data.CliDataDict
    ].ok(final_data)

    if result.is_failure:
        cli.output.print_message(
            f"❌ Pipeline failed: {result.error}", style="bold red"
        )
        return result

    cli.output.print_message("✅ Pipeline completed successfully", style="green")
    return result


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Complete CLI integration example."""
    cli.output.print_message("=" * 70, style="bold blue")
    cli.output.print_message("  Complete CLI Integration Example", style="bold white")
    cli.output.print_message("=" * 70, style="bold blue")

    # Example 1: Complete CLI application
    cli.output.print_message("\n1. Complete CLI Application:", style="bold cyan")
    app = DataManagerCLI()
    workflow_result = app.run_workflow()

    if workflow_result.is_failure:
        cli.output.print_message(
            f"   ❌ Workflow failed: {workflow_result.error}", style="bold red"
        )
    else:
        cli.output.print_message(
            "   ✅ Workflow completed successfully!", style="bold green"
        )

    # Example 2: Railway pattern
    cli.output.print_message(
        "\n2. Railway Pattern (chained operations):", style="bold cyan"
    )
    test_data_raw: dict[str, FlextTypes.GeneralValueType] = {"id": 1, "name": "test"}
    # Convert to JsonDict-compatible dict using FlextUtilities
    test_data: FlextCliTypes.Data.CliDataDict = (
        FlextUtilities.DataMapper.convert_dict_to_json(test_data_raw)
    )
    pipeline_result = process_with_railway_pattern(test_data)

    if pipeline_result.is_success:
        final_data = pipeline_result.unwrap()
        cli.output.print_message(f"   Result: {final_data}", style="green")

    # Example 3: Error handling showcase
    cli.output.print_message("\n3. Error Handling Showcase:", style="bold cyan")

    def safe_operation(value: int) -> FlextResult[int]:
        if value < 0:
            return FlextResult[int].fail("Negative values not allowed")
        return FlextResult[int].ok(value * 2)

    # Success case
    result = safe_operation(10)
    if result.is_success:
        cli.output.print_message(
            f"   ✅ Operation succeeded: {result.unwrap()}", style="green"
        )

    # Failure case
    result = safe_operation(-5)
    if result.is_failure:
        cli.output.print_message(
            f"   ℹ️  Operation failed gracefully: {result.error}", style="cyan"
        )

    # Cleanup
    app.data_file.unlink(missing_ok=True)

    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    cli.output.print_message(
        "  ✅ Complete Integration Examples Done!", style="bold green"
    )
    cli.output.print_message("=" * 70, style="bold blue")

    # Summary guide
    cli.output.print_message("\n💡 Integration Summary:", style="bold cyan")
    cli.output.print_message(
        "  • Use FlextCli() constructor for singleton access", style="white"
    )
    cli.output.print_message(
        "  • Chain operations with FlextResult.map()", style="white"
    )
    cli.output.print_message(
        "  • Handle errors gracefully with is_success/is_failure", style="white"
    )
    cli.output.print_message(
        "  • Combine all features for complete CLI apps", style="white"
    )

    # Architecture overview
    cli.output.print_message("\n🏗️  Complete CLI Architecture:", style="bold cyan")
    architecture = {
        "Output": "cli.output.print_message() + tables",
        "File I/O": "cli.file_tools.read/write",
        "User Input": "FlextCliPrompts",
        "Config": "cli.config",
        "Auth": "cli.save/get_auth_token()",
        "Error Handling": "FlextResult pattern",
    }

    for component, usage in architecture.items():
        cli.output.print_message(f"   • {component}: {usage}", style="cyan")


if __name__ == "__main__":
    main()
