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
from collections.abc import Mapping
from pathlib import Path

from flext_cli import c, cli, m, t
from flext_core import p, r

_EXAMPLE_ERR_NO_DATA_FILE_FOUND = "No data file found"
_EXAMPLE_ERR_DATA_FILE_MUST_BE_MAPPING = "Data file must contain a mapping"


class DataManagerCLI:
    """Minimal end-to-end CLI workflow using the public facade."""

    def __init__(self) -> None:
        """Initialize data manager CLI with temporary data file."""
        self.data_file = Path(tempfile.gettempdir()) / "app_data.json"

    def add_entry(self) -> p.Result[t.JsonMapping]:
        """Create one entry through the public prompt surface."""
        cli.configure(m.Cli.PromptRuntimeState(interactive=False))
        key_result = cli.prompt("Enter key:", default="sample_key")
        if key_result.failure:
            return r[t.JsonMapping].fail(f"Prompt failed: {key_result.error}")
        key = key_result.value
        value_result = cli.prompt("Enter value:", default="sample_value")
        if value_result.failure:
            return r[t.JsonMapping].fail(f"Prompt failed: {value_result.error}")
        value = value_result.value
        cli.print(f"✅ Created entry: {key} = {value}", style=c.Cli.MessageStyles.GREEN)
        return r[t.JsonMapping].ok(
            t.Cli.JSON_MAPPING_ADAPTER.validate_python({key: value})
        )

    def load_data(self) -> p.Result[t.JsonMapping]:
        """Load previously saved data through the public file surface."""
        if not self.data_file.exists():
            return r[t.JsonMapping].fail(_EXAMPLE_ERR_NO_DATA_FILE_FOUND)
        read_result = cli.json_read_file(str(self.data_file))
        if read_result.failure:
            error_msg = read_result.error or "Unknown error"
            cli.print(
                f"❌ Load failed: {error_msg}", style=c.Cli.MessageStyles.BOLD_RED
            )
            return r[t.JsonMapping].fail(error_msg)
        if not isinstance(read_result.value, Mapping):
            return r[t.JsonMapping].fail(_EXAMPLE_ERR_DATA_FILE_MUST_BE_MAPPING)
        cli.print("✅ Data loaded successfully", style=c.Cli.MessageStyles.GREEN)
        return r[t.JsonMapping].ok(read_result.value)

    def save_data(self, data: t.JsonMapping) -> p.Result[bool]:
        """Persist the current dataset through the public file surface."""
        write_result = cli.json_write_file(self.data_file, data)
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

    def run_workflow(self) -> p.Result[bool]:
        """Run the minimal public workflow exercised by the smoke test."""
        load_result = self.load_data()
        current_data: t.MutableJsonMapping = (
            dict(load_result.value) if load_result.success else {}
        )
        if load_result.failure:
            cli.print("Creating new dataset", style=c.Cli.MessageStyles.YELLOW)
        entry_result = self.add_entry()
        if entry_result.failure:
            return r[bool].fail(f"Add entry failed: {entry_result.error}")
        current_data.update(entry_result.value)
        save_result = self.save_data(current_data)
        if save_result.failure:
            return r[bool].fail(f"Save failed: {save_result.error}")
        cli.show_table(
            [{"Key": key, "Value": str(value)} for key, value in current_data.items()],
            headers=["Key", "Value"],
            title="📋 Current Data",
        )
        return r[bool].ok(value=True)
