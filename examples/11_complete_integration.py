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
from pathlib import Path

from flext_core import FlextResult

from flext_cli import FlextCli, FlextCliPrompts

cli = FlextCli.get_instance()


# ============================================================================
# COMPLETE CLI APPLICATION EXAMPLE
# ============================================================================


class DataManagerCLI:
    """Complete CLI application using all flext-cli features."""

    def __init__(self) -> None:
        """Initialize data manager CLI with temporary data file."""
        self.cli = FlextCli.get_instance()
        self.data_file = Path(tempfile.gettempdir()) / "app_data.json"

    def display_welcome(self) -> None:
        """Show welcome message with styled output."""
        self.cli.formatters.print("=" * 70, style="bold blue")
        self.cli.formatters.print("  📊 Data Manager CLI", style="bold white on blue")
        self.cli.formatters.print("=" * 70, style="bold blue")

    def save_data(self, data: dict) -> FlextResult[None]:
        """Save data with proper error handling."""
        write_result = self.cli.file_tools.write_json_file(self.data_file, data)

        if write_result.is_failure:
            self.cli.formatters.print(
                f"❌ Save failed: {write_result.error}", style="bold red"
            )
            return FlextResult[None].fail(write_result.error)

        self.cli.formatters.print(
            f"✅ Data saved to {self.data_file.name}", style="green"
        )
        return FlextResult[None].ok(None)

    def load_data(self) -> FlextResult[dict]:
        """Load data with error handling."""
        if not self.data_file.exists():
            return FlextResult[dict].fail("No data file found")

        read_result = self.cli.file_tools.read_json_file(self.data_file)

        if read_result.is_failure:
            self.cli.formatters.print(
                f"❌ Load failed: {read_result.error}", style="bold red"
            )
            return FlextResult[dict].fail(read_result.error)

        # Type narrowing: ensure we return a dict
        data = read_result.unwrap()
        if not isinstance(data, dict):
            return FlextResult[dict].fail("Data is not a dictionary")
        self.cli.formatters.print("✅ Data loaded successfully", style="green")
        return FlextResult[dict].ok(data)

    def display_data(self, data: dict) -> None:
        """Display data as formatted table."""
        if not data:
            self.cli.formatters.print("⚠️  No data to display", style="yellow")
            return

        table_result = self.cli.create_table(
            data=data, headers=["Field", "Value"], title="📋 Current Data"
        )

        if table_result.is_success:
            self.cli.formatters.console.print(table_result.unwrap())

    def add_entry(self) -> FlextResult[dict]:
        """Add new entry with user prompts."""
        prompts = FlextCliPrompts(interactive_mode=False)

        # Get key
        key_result = prompts.prompt("Enter key:", default="sample_key")
        if key_result.is_failure:
            return FlextResult[dict].fail(f"Prompt failed: {key_result.error}")

        key = key_result.unwrap()

        # Get value
        value_result = prompts.prompt("Enter value:", default="sample_value")
        if value_result.is_failure:
            return FlextResult[dict].fail(f"Prompt failed: {value_result.error}")

        value = value_result.unwrap()

        entry = {key: value}
        self.cli.formatters.print(f"✅ Created entry: {key} = {value}", style="green")
        return FlextResult[dict].ok(entry)

    def run_workflow(self) -> FlextResult[None]:
        """Complete workflow integrating all features."""
        # Step 1: Welcome
        self.display_welcome()

        # Step 2: Load existing data (or create new)
        self.cli.formatters.print("\n📂 Loading existing data...", style="cyan")
        load_result = self.load_data()

        if load_result.is_success:
            current_data = load_result.unwrap()
        else:
            self.cli.formatters.print("   Creating new dataset", style="yellow")
            current_data = {}

        # Step 3: Display current data
        self.cli.formatters.print("\n📊 Current Data:", style="bold cyan")
        self.display_data(current_data)

        # Step 4: Add new entry
        self.cli.formatters.print("\n➕ Adding New Entry:", style="bold cyan")
        entry_result = self.add_entry()

        if entry_result.is_failure:
            return FlextResult[None].fail(f"Add entry failed: {entry_result.error}")

        new_entry = entry_result.unwrap()
        current_data.update(new_entry)

        # Step 5: Save updated data
        self.cli.formatters.print("\n💾 Saving Data:", style="bold cyan")
        save_result = self.save_data(current_data)

        if save_result.is_failure:
            return FlextResult[None].fail(f"Save failed: {save_result.error}")

        # Step 6: Display final result
        self.cli.formatters.print("\n✨ Final Result:", style="bold cyan")
        self.display_data(current_data)

        return FlextResult[None].ok(None)


# ============================================================================
# RAILWAY PATTERN EXAMPLE
# ============================================================================


def process_with_railway_pattern(input_data: dict) -> FlextResult[dict]:
    """Show railway pattern chaining operations."""
    # Removed unused temp_file variable

    # Chain operations using FlextResult
    result = (
        # Step 1: Validate
        FlextResult[dict]
        .ok(input_data)
        .map(lambda d: {**d, "validated": True})
        # Step 2: Transform
        .map(lambda d: {**d, "processed": True})
        # Step 3: Enrich
        .map(lambda d: {**d, "enriched": True})
    )

    if result.is_failure:
        cli.formatters.print(f"❌ Pipeline failed: {result.error}", style="bold red")
        return result

    cli.formatters.print("✅ Pipeline completed successfully", style="green")
    return result


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Complete CLI integration example."""
    cli.formatters.print("=" * 70, style="bold blue")
    cli.formatters.print("  Complete CLI Integration Example", style="bold white")
    cli.formatters.print("=" * 70, style="bold blue")

    # Example 1: Complete CLI application
    cli.formatters.print("\n1. Complete CLI Application:", style="bold cyan")
    app = DataManagerCLI()
    workflow_result = app.run_workflow()

    if workflow_result.is_failure:
        cli.formatters.print(
            f"   ❌ Workflow failed: {workflow_result.error}", style="bold red"
        )
    else:
        cli.formatters.print(
            "   ✅ Workflow completed successfully!", style="bold green"
        )

    # Example 2: Railway pattern
    cli.formatters.print(
        "\n2. Railway Pattern (chained operations):", style="bold cyan"
    )
    test_data = {"id": 1, "name": "test"}
    pipeline_result = process_with_railway_pattern(test_data)

    if pipeline_result.is_success:
        final_data = pipeline_result.unwrap()
        cli.formatters.print(f"   Result: {final_data}", style="green")

    # Example 3: Error handling showcase
    cli.formatters.print("\n3. Error Handling Showcase:", style="bold cyan")

    def safe_operation(value: int) -> FlextResult[int]:
        if value < 0:
            return FlextResult[int].fail("Negative values not allowed")
        return FlextResult[int].ok(value * 2)

    # Success case
    result = safe_operation(10)
    if result.is_success:
        cli.formatters.print(
            f"   ✅ Operation succeeded: {result.unwrap()}", style="green"
        )

    # Failure case
    result = safe_operation(-5)
    if result.is_failure:
        cli.formatters.print(
            f"   ℹ️  Operation failed gracefully: {result.error}", style="cyan"
        )

    # Cleanup
    app.data_file.unlink(missing_ok=True)

    cli.formatters.print("\n" + "=" * 70, style="bold blue")
    cli.formatters.print("  ✅ Complete Integration Examples Done!", style="bold green")
    cli.formatters.print("=" * 70, style="bold blue")

    # Summary guide
    cli.formatters.print("\n💡 Integration Summary:", style="bold cyan")
    cli.formatters.print(
        "  • Use FlextCli.get_instance() for singleton access", style="white"
    )
    cli.formatters.print("  • Chain operations with FlextResult.map()", style="white")
    cli.formatters.print(
        "  • Handle errors gracefully with is_success/is_failure", style="white"
    )
    cli.formatters.print(
        "  • Combine all features for complete CLI apps", style="white"
    )

    # Architecture overview
    cli.formatters.print("\n🏗️  Complete CLI Architecture:", style="bold cyan")
    architecture = {
        "Output": "cli.formatters.print() + tables",
        "File I/O": "cli.file_tools.read/write",
        "User Input": "FlextCliPrompts",
        "Config": "cli.config",
        "Auth": "cli.save/get_auth_token()",
        "Error Handling": "FlextResult pattern",
    }

    for component, usage in architecture.items():
        cli.formatters.print(f"   • {component}: {usage}", style="cyan")


if __name__ == "__main__":
    main()
