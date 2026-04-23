"""Complete Integration - Building Complete CLI Apps with flext-.

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
from collections.abc import (
    Mapping,
)
from pathlib import Path

from examples import c, m, p, r, t, u
from flext_cli import cli


class DataManagerCLI:
    """Complete CLI application using all flext-cli features."""

    def __init__(self) -> None:
        """Initialize data manager CLI with temporary data file."""
        super().__init__()
        self.data_file = Path(tempfile.gettempdir()) / "app_data.json"

    def add_entry(self) -> p.Result[t.JsonMapping]:
        """Add new entry with user prompts."""
        prompts = cli
        prompts.configure(m.Cli.PromptRuntimeState(interactive=False))
        key_result = prompts.prompt("Enter key:", default="sample_key")
        if key_result.failure:
            return r[t.JsonMapping].fail(f"Prompt failed: {key_result.error}")
        key = key_result.value
        value_result = prompts.prompt("Enter value:", default="sample_value")
        if value_result.failure:
            return r[t.JsonMapping].fail(f"Prompt failed: {value_result.error}")
        value = value_result.value
        cli.print(f"✅ Created entry: {key} = {value}", style=c.Cli.MessageStyles.GREEN)
        converted_entry = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
            u.Cli.normalize_json_value({key: value})
        )
        return r[t.JsonMapping].ok(converted_entry)

    def display_data(self, data: Mapping[str, t.JsonPayloadCollectionValue]) -> None:
        """Display data as formatted table."""
        if not data:
            cli.print("⚠️  No data to display", style=c.Cli.MessageStyles.YELLOW)
            return
        safe_data: t.Cli.TableMappingRow = {str(k): str(v) for k, v in data.items()}
        cli.show_table(safe_data, show_header=True, title="📋 Current Data")

    def display_welcome(self) -> None:
        """Show welcome message with styled output."""
        cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
        cli.print("  📊 Data Manager CLI", style=c.Cli.MessageStyles.BOLD_WHITE_ON_BLUE)
        cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)

    def load_data(self) -> p.Result[t.JsonMapping]:
        """Load data with error handling. Uses read_json_file for dict-only result."""
        if not self.data_file.exists():
            return r[t.JsonMapping].fail(c.EXAMPLE_ERR_NO_DATA_FILE_FOUND)
        read_result = cli.read_json_file(str(self.data_file))
        if read_result.failure:
            error_msg = read_result.error or "Unknown error"
            cli.print(
                f"❌ Load failed: {error_msg}", style=c.Cli.MessageStyles.BOLD_RED
            )
            return r[t.JsonMapping].fail(error_msg)
        if not isinstance(read_result.value, Mapping):
            return r[t.JsonMapping].fail(
                c.EXAMPLE_ERR_DATA_FILE_MUST_BE_MAPPING,
            )
        cli.print("✅ Data loaded successfully", style=c.Cli.MessageStyles.GREEN)
        return r[t.JsonMapping].ok(read_result.value)

    def run_workflow(self) -> p.Result[bool]:
        """Complete workflow integrating all features."""
        self.display_welcome()
        cli.print("\n📂 Loading existing data...", style=c.Cli.MessageStyles.CYAN)
        load_result = self.load_data()
        current_data: t.MutableJsonMapping = {}
        if load_result.success:
            loaded_data = load_result.value
            current_data = dict(loaded_data)
        else:
            cli.print("   Creating new dataset", style=c.Cli.MessageStyles.YELLOW)
        cli.print("\n📊 Current Data:", style=c.Cli.MessageStyles.BOLD_CYAN)
        self.display_data(current_data)
        cli.print("\n➕ Adding New Entry:", style=c.Cli.MessageStyles.BOLD_CYAN)
        entry_result = self.add_entry()
        if entry_result.failure:
            return r[bool].fail(f"Add entry failed: {entry_result.error}")
        new_entry = entry_result.value
        current_data.update(new_entry)
        cli.print("\n💾 Saving Data:", style=c.Cli.MessageStyles.BOLD_CYAN)
        save_result = self.save_data(current_data)
        if save_result.failure:
            return r[bool].fail(f"Save failed: {save_result.error}")
        cli.print("\n✨ Final Result:", style=c.Cli.MessageStyles.BOLD_CYAN)
        self.display_data(current_data)
        return r[bool].ok(value=True)

    def save_data(self, data: t.JsonMapping) -> p.Result[bool]:
        """Save data with proper error handling."""
        write_result = cli.write_json_file(self.data_file, data)
        if write_result.failure:
            error_msg = write_result.error or "Unknown error"
            cli.print(
                f"❌ Save failed: {error_msg}", style=c.Cli.MessageStyles.BOLD_RED
            )
            return r[bool].fail(error_msg)
        cli.print(
            f"✅ Data saved to {self.data_file.name}", style=c.Cli.MessageStyles.GREEN
        )
        return r[bool].ok(value=True)


def process_with_railway_pattern(
    input_data: Mapping[str, t.JsonPayloadCollectionValue],
) -> p.Result[t.JsonMapping]:
    """Show railway pattern chaining operations."""
    step1_data = {**input_data, "validated": True}
    step2_data = {**step1_data, "processed": True}
    final_data = {**step2_data, "enriched": True}
    normalized_final_data = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
        u.Cli.normalize_json_value(final_data)
    )
    result: p.Result[t.JsonMapping] = r[t.JsonMapping].ok(normalized_final_data)
    if result.failure:
        cli.print(
            f"❌ Pipeline failed: {result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return result
    cli.print("✅ Pipeline completed successfully", style=c.Cli.MessageStyles.GREEN)
    return result


def main() -> None:
    """Complete CLI integration example."""
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  Complete CLI Integration Example", style=c.Cli.MessageStyles.BOLD_WHITE
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n1. Complete CLI Application:", style=c.Cli.MessageStyles.BOLD_CYAN)
    app = DataManagerCLI()
    workflow_result = app.run_workflow()
    if workflow_result.failure:
        cli.print(
            f"   ❌ Workflow failed: {workflow_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
    else:
        cli.print(
            "   ✅ Workflow completed successfully!",
            style=c.Cli.MessageStyles.BOLD_GREEN,
        )
    cli.print(
        "\n2. Railway Pattern (chained operations):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    test_data = {"id": 1, "name": "test"}
    pipeline_result = process_with_railway_pattern(test_data)
    if pipeline_result.success:
        final_data = pipeline_result.value
        cli.print(f"   Result: {final_data}", style=c.Cli.MessageStyles.GREEN)
    cli.print("\n3. Error Handling Showcase:", style=c.Cli.MessageStyles.BOLD_CYAN)

    def safe_operation(value: int) -> p.Result[int]:
        if value < 0:
            return r[int].fail(c.EXAMPLE_ERR_NEGATIVE_VALUES_NOT_ALLOWED)
        return r[int].ok(value * 2)

    result = safe_operation(10)
    if result.success:
        cli.print(
            f"   ✅ Operation succeeded: {result.value}",
            style=c.Cli.MessageStyles.GREEN,
        )
    result = safe_operation(-5)
    if result.failure:
        cli.print(
            f"   ℹ️  Operation failed gracefully: {result.error}",
            style=c.Cli.MessageStyles.CYAN,
        )
    app.data_file.unlink(missing_ok=True)
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  ✅ Complete Integration Examples Done!", style=c.Cli.MessageStyles.BOLD_GREEN
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n💡 Integration Summary:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "  • Use the shared cli singleton directly", style=c.Cli.MessageStyles.WHITE
    )
    cli.print("  • Chain operations with r.map()", style=c.Cli.MessageStyles.WHITE)
    cli.print(
        "  • Handle errors gracefully with success/failure",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Combine all features for complete CLI apps",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print("\n🏗️  Complete CLI Architecture:", style=c.Cli.MessageStyles.BOLD_CYAN)
    architecture = {
        "Output": "cli.print() + cli.show_table()",
        "File I/O": "cli.read_json_file/write_json_file",
        "User Input": "cli",
        "Config": "cli.settings",
        "Auth": "cli.save/fetch_auth_token()",
        "Error Handling": "r pattern",
    }
    for component, usage in architecture.items():
        cli.print(f"   • {component}: {usage}", style=c.Cli.MessageStyles.CYAN)


if __name__ == "__main__":
    main()
