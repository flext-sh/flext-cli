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
- r railway pattern throughout
- Professional CLI development toolkit

HOW TO USE IN YOUR CLI:
See complete integration patterns for YOUR CLI application

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_core import r

from flext_cli import FlextCli, FlextCliPrompts, t

cli = FlextCli()


class DataManagerCLI:
    """Complete CLI application using all flext-cli features."""

    def __init__(self) -> None:
        """Initialize data manager CLI with temporary data file."""
        super().__init__()
        self.cli = FlextCli()
        self.data_file = Path(tempfile.gettempdir()) / "app_data.json"

    def add_entry(self) -> r[t.ContainerMapping]:
        """Add new entry with user prompts."""
        prompts = FlextCliPrompts(interactive_mode=False)
        key_result = prompts.prompt("Enter key:", default="sample_key")
        if key_result.is_failure:
            return r[t.ContainerMapping].fail(f"Prompt failed: {key_result.error}")
        key = key_result.value
        value_result = prompts.prompt("Enter value:", default="sample_value")
        if value_result.is_failure:
            return r[t.ContainerMapping].fail(f"Prompt failed: {value_result.error}")
        value = value_result.value
        self.cli.print(f"✅ Created entry: {key} = {value}", style="green")
        converted_entry: t.ContainerMapping = {key: value}
        return r[t.ContainerMapping].ok(converted_entry)

    def display_data(self, data: t.ContainerMapping) -> None:
        """Display data as formatted table."""
        if not data:
            self.cli.print("⚠️  No data to display", style="yellow")
            return
        self.cli.show_table(data, headers=["Field", "Value"], title="📋 Current Data")

    def display_welcome(self) -> None:
        """Show welcome message with styled output."""
        self.cli.print("=" * 70, style="bold blue")
        self.cli.print("  📊 Data Manager CLI", style="bold white on blue")
        self.cli.print("=" * 70, style="bold blue")

    def load_data(self) -> r[t.ContainerMapping]:
        """Load data with error handling. Uses read_json_dict for dict-only result."""
        if not self.data_file.exists():
            return r[t.ContainerMapping].fail("No data file found")
        read_result = self.cli.file_tools.read_json_dict(str(self.data_file))
        if read_result.is_failure:
            error_msg = read_result.error or "Unknown error"
            self.cli.print(f"❌ Load failed: {error_msg}", style="bold red")
            return r[t.ContainerMapping].fail(error_msg)
        self.cli.print("✅ Data loaded successfully", style="green")
        return r[t.ContainerMapping].ok(read_result.value)

    def run_workflow(self) -> r[bool]:
        """Complete workflow integrating all features."""
        self.display_welcome()
        self.cli.print("\n📂 Loading existing data...", style="cyan")
        load_result = self.load_data()
        current_data: t.MutableContainerMapping = {}
        if load_result.is_success:
            loaded_data = load_result.value
            current_data = dict(loaded_data) if isinstance(loaded_data, dict) else {}
        else:
            self.cli.print("   Creating new dataset", style="yellow")
        self.cli.print("\n📊 Current Data:", style="bold cyan")
        self.display_data(current_data)
        self.cli.print("\n➕ Adding New Entry:", style="bold cyan")
        entry_result = self.add_entry()
        if entry_result.is_failure:
            return r[bool].fail(f"Add entry failed: {entry_result.error}")
        new_entry = entry_result.value
        current_data.update(new_entry)
        self.cli.print("\n💾 Saving Data:", style="bold cyan")
        save_result = self.save_data(current_data)
        if save_result.is_failure:
            return r[bool].fail(f"Save failed: {save_result.error}")
        self.cli.print("\n✨ Final Result:", style="bold cyan")
        self.display_data(current_data)
        return r[bool].ok(value=True)

    def save_data(self, data: t.ContainerMapping) -> r[bool]:
        """Save data with proper error handling."""
        write_result = self.cli.file_tools.write_json_file(self.data_file, data)
        if write_result.is_failure:
            error_msg = write_result.error or "Unknown error"
            self.cli.print(f"❌ Save failed: {error_msg}", style="bold red")
            return r[bool].fail(error_msg)
        self.cli.print(f"✅ Data saved to {self.data_file.name}", style="green")
        return r[bool].ok(value=True)


def process_with_railway_pattern(
    input_data: t.ContainerMapping,
) -> r[t.ContainerMapping]:
    """Show railway pattern chaining operations."""
    step1_data: t.ContainerMapping = {**input_data, "validated": True}
    step2_data: t.ContainerMapping = {**step1_data, "processed": True}
    final_data: t.ContainerMapping = {**step2_data, "enriched": True}
    result: r[t.ContainerMapping] = r[t.ContainerMapping].ok(final_data)
    if result.is_failure:
        cli.print(f"❌ Pipeline failed: {result.error}", style="bold red")
        return result
    cli.print("✅ Pipeline completed successfully", style="green")
    return result


def main() -> None:
    """Complete CLI integration example."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Complete CLI Integration Example", style="bold white")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n1. Complete CLI Application:", style="bold cyan")
    app = DataManagerCLI()
    workflow_result = app.run_workflow()
    if workflow_result.is_failure:
        cli.print(f"   ❌ Workflow failed: {workflow_result.error}", style="bold red")
    else:
        cli.print("   ✅ Workflow completed successfully!", style="bold green")
    cli.print("\n2. Railway Pattern (chained operations):", style="bold cyan")
    test_data: t.ContainerMapping = {"id": 1, "name": "test"}
    pipeline_result = process_with_railway_pattern(test_data)
    if pipeline_result.is_success:
        final_data = pipeline_result.value
        cli.print(f"   Result: {final_data}", style="green")
    cli.print("\n3. Error Handling Showcase:", style="bold cyan")

    def safe_operation(value: int) -> r[int]:
        if value < 0:
            return r[int].fail("Negative values not allowed")
        return r[int].ok(value * 2)

    result = safe_operation(10)
    if result.is_success:
        cli.print(f"   ✅ Operation succeeded: {result.value}", style="green")
    result = safe_operation(-5)
    if result.is_failure:
        cli.print(f"   ℹ️  Operation failed gracefully: {result.error}", style="cyan")
    app.data_file.unlink(missing_ok=True)
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Complete Integration Examples Done!", style="bold green")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n💡 Integration Summary:", style="bold cyan")
    cli.print("  • Use FlextCli() constructor for singleton access", style="white")
    cli.print("  • Chain operations with r.map()", style="white")
    cli.print("  • Handle errors gracefully with is_success/is_failure", style="white")
    cli.print("  • Combine all features for complete CLI apps", style="white")
    cli.print("\n🏗️  Complete CLI Architecture:", style="bold cyan")
    architecture = {
        "Output": "cli.print() + cli.show_table()",
        "File I/O": "cli.file_tools.read_json_dict/write",
        "User Input": "FlextCliPrompts",
        "Config": "cli.config",
        "Auth": "cli.save/get_auth_token()",
        "Error Handling": "r pattern",
    }
    for component, usage in architecture.items():
        cli.print(f"   • {component}: {usage}", style="cyan")


if __name__ == "__main__":
    main()
