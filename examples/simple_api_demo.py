"""Simple API Demo - Flext CLI Convenience Methods.

This example demonstrates the Phase 3 convenience API that provides
simple one-liner methods for common CLI operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from flext_cli import FlextCli


def main() -> None:
    """Demonstrate all convenience methods in the simple API."""
    cli = FlextCli()

    # =========================================================================
    # OUTPUT MESSAGES - Simple styled messages
    # =========================================================================
    cli.success("Operation completed successfully!")
    cli.error("Something went wrong!")
    cli.warning("This is a warning message")
    cli.info("Informational message")

    # =========================================================================
    # TABLE DISPLAY - Automatic table formatting
    # =========================================================================
    users = [
        {"name": "Alice", "age": 30, "role": "Admin"},
        {"name": "Bob", "age": 25, "role": "User"},
        {"name": "Charlie", "age": 35, "role": "Manager"},
    ]

    print("\n--- User Table ---")
    cli.table(users)

    # =========================================================================
    # INTERACTIVE PROMPTS - User input
    # =========================================================================
    print("\n--- Interactive Prompts ---")

    # Confirmation
    if cli.confirm("Do you want to continue?", default=True):
        cli.success("Continuing...")
    else:
        cli.info("Skipped")

    # Text input
    name = cli.prompt_text("What's your name?", default="Guest")
    cli.info(f"Hello, {name}!")

    # =========================================================================
    # FILE OPERATIONS - Simple JSON/YAML read/write
    # =========================================================================
    print("\n--- File Operations ---")

    # Write JSON
    test_data = {"app": "flext-cli", "version": "0.9.0", "users": users}
    cli.write_json(test_data, "/tmp/test_config.json")
    cli.success("Written JSON to /tmp/test_config.json")

    # Read JSON
    loaded_data = cli.read_json("/tmp/test_config.json")
    cli.info(f"Loaded JSON: {loaded_data['app']} v{loaded_data['version']}")

    # Write YAML
    cli.write_yaml(test_data, "/tmp/test_config.yaml")
    cli.success("Written YAML to /tmp/test_config.yaml")

    # Read YAML
    yaml_data = cli.read_yaml("/tmp/test_config.yaml")
    cli.info(f"Loaded YAML: {yaml_data['app']} v{yaml_data['version']}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n--- Demo Complete ---")
    cli.success("All convenience methods demonstrated!")
    cli.info("This is the Phase 3 simplified API")
    cli.info("For advanced features, use cli.formatters, cli.tables, cli.file_tools")


if __name__ == "__main__":
    main()
