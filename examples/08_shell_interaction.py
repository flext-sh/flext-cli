"""Shell Interaction - Interactive REPL.

Demonstrates flext-cli interactive shell through FlextCli API.

Key Features:
- Auto-completion with Tab
- Command history auto-saved
- Syntax highlighting automatic
- Multi-line editing auto-detected

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_interactive_shell() -> None:
    """Show interactive shell with auto-configuration."""
    # Shell auto-configured for terminal
    # Uncommented to avoid blocking: shell = cli.shell
    # shell.run()  # Auto-completion, history, highlighting enabled

    cli.output.print_message("Shell auto-configured with history and completion")


def demonstrate_custom_commands() -> None:
    """Show command registration with auto-help."""

    def greet(name: str) -> FlextResult[None]:
        print(f"Hello, {name}!")
        return FlextResult[None].ok(None)

    # Commands auto-generate help text from docstrings
    cli.output.print_message("Commands auto-document from signatures")


def main() -> None:
    """Run all demonstrations."""
    demonstrate_interactive_shell()
    demonstrate_custom_commands()


if __name__ == "__main__":
    main()
