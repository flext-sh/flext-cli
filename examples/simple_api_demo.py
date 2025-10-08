"""Simple API Demo - Flext CLI Optimized API.

This example demonstrates the optimized flext-cli API using direct access
to formatters, file_tools, and other services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import tempfile
from pathlib import Path

from flext_cli import FlextCli


def main() -> None:
    """Demonstrate all convenience methods in the optimized API."""
    cli = FlextCli.get_instance()

    # =========================================================================
    # OUTPUT MESSAGES - Simple styled messages using formatters
    # =========================================================================
    cli.formatters.print("Operation completed successfully!", style="bold green")
    cli.formatters.print("Something went wrong!", style="bold red")
    cli.formatters.print("This is a warning message", style="bold yellow")
    cli.formatters.print("Informational message", style="cyan")

    # =========================================================================
    # TABLE DISPLAY - Automatic table formatting
    # =========================================================================
    users = {
        "Alice": "30 | Admin",
        "Bob": "25 | User",
        "Charlie": "35 | Manager",
    }

    cli.formatters.print("\n--- User Table ---", style="bold cyan")
    table_result = cli.create_table(
        data=users, headers=["Name", "Age | Role"], title="User Information"
    )
    if table_result.is_success:
        cli.formatters.console.print(table_result.unwrap())

    # =========================================================================
    # FILE OPERATIONS - Simple JSON read/write using file_tools
    # =========================================================================
    cli.formatters.print("\n--- File Operations ---", style="bold cyan")

    # Create temporary directory for safe file operations
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Write JSON
        json_file = temp_path / "test_config.json"
        test_data = {"app": "flext-cli", "version": "2.0.0", "count": 3}
        write_result = cli.file_tools.write_json(test_data, str(json_file))
        if write_result.is_success:
            cli.formatters.print(f"✅ Written JSON to {json_file}", style="green")

        # Read JSON
        loaded_result = cli.file_tools.read_json(str(json_file))
        if loaded_result.is_success:
            loaded_data = loaded_result.unwrap()
            if isinstance(loaded_data, dict):
                cli.formatters.print(
                    f"✅ Loaded JSON: {loaded_data.get('app')} v{loaded_data.get('version')}",
                    style="green",
                )
        else:
            cli.formatters.print(
                f"❌ Failed to load JSON: {loaded_result.error}", style="red"
            )

    # =========================================================================
    # SUMMARY
    # =========================================================================
    cli.formatters.print("\n--- Demo Complete ---", style="bold cyan")
    cli.formatters.print(
        "✅ All optimized API methods demonstrated!", style="bold green"
    )
    cli.formatters.print(
        "📚 Using: cli.formatters, cli.create_table(), cli.file_tools", style="cyan"
    )


if __name__ == "__main__":
    main()
