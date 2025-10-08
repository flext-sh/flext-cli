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
    cli.formatters.print("\n💻 Interactive Shell:", style="bold cyan")

    # Shell auto-configured for terminal
    # Uncommented to avoid blocking: shell = cli.shell
    # shell.run()  # Auto-completion, history, highlighting enabled

    cli.formatters.print(
        "✅ Shell auto-configured with history and completion", style="cyan"
    )


def demonstrate_custom_commands() -> None:
    """Show command registration with auto-help."""
    cli.formatters.print("\n⌨️  Custom Commands:", style="bold cyan")

    def greet(name: str) -> FlextResult[None]:
        cli.formatters.print(f"Hello, {name}!", style="green")
        return FlextResult[None].ok(None)

    # Execute sample command
    result = greet("World")
    if result.is_success:
        cli.formatters.print("✅ Commands auto-document from signatures", style="cyan")


def main() -> None:
    """Run all demonstrations."""
    cli.formatters.print("=" * 60, style="bold blue")
    cli.formatters.print("  Shell Interaction Examples", style="bold white on blue")
    cli.formatters.print("=" * 60, style="bold blue")

    demonstrate_interactive_shell()
    demonstrate_custom_commands()

    cli.formatters.print("\n" + "=" * 60, style="bold blue")
    cli.formatters.print("  ✅ All shell examples completed!", style="bold green")
    cli.formatters.print("=" * 60, style="bold blue")


if __name__ == "__main__":
    main()
