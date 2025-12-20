"""Shell Interaction - PATTERN GUIDE (NOT A FLEXT-CLI BUILT-IN FEATURE)..

⚠️  IMPORTANT: This is a PATTERN GUIDE showing how YOU can implement
interactive shell/REPL in YOUR own CLI application using flext-cli as a foundation.

flext-cli does NOT provide FlextCliShell or REPL features built-in.
This example demonstrates patterns and best practices for YOUR implementation.

WHEN TO USE THIS PATTERN IN YOUR CLI:
- Building interactive REPL-style CLIs
- Need command history and auto-completion
- Want multi-command interactive sessions
- Building debugging/REDACTED_LDAP_BIND_PASSWORD consoles
- Need syntax highlighting in terminal

WHAT YOU CAN BUILD USING THIS PATTERN:
- Custom interactive shell for YOUR application
- Command dispatcher with FlextResult integration
- Command history tracking
- Multi-line input support
- Auto-completion for YOUR commands

HOW TO IMPLEMENT IN YOUR CLI:
Use flext-cli foundation (FlextResult, FlextCli) + prompt_toolkit library

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import time

from flext_cli import FlextCli, r, t, u

cli = FlextCli()


# ============================================================================
# PATTERN 1: Simple command handler for YOUR interactive CLI
# ============================================================================


def handle_status_command() -> r[t.JsonDict]:
    """Status command in YOUR interactive CLI."""
    status = {
        "status": "running",
        "user": os.getenv("USER", "unknown"),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    cli.formatters.print(f"✅ Status: {status['status']}", style="green")
    cli.formatters.print(f"   User: {status['user']}", style="cyan")
    cli.formatters.print(f"   Time: {status['timestamp']}", style="cyan")

    # Use u.transform for JSON conversion
    transform_result = u.transform(
        status,
        to_json=True,
    )
    typed_status: t.JsonDict = (
        transform_result.value if transform_result.is_success else status
    )
    return r[t.JsonDict].ok(typed_status)


def handle_list_command(
    filter_text: str = "",
) -> r[list[str]]:
    """List command with filtering in YOUR CLI."""
    items = ["item1", "item2", "item3", "test_item"]

    if filter_text:
        filtered = [item for item in items if filter_text in item]
        cli.formatters.print(
            f"📋 Found {len(filtered)} items matching '{filter_text}'",
            style="cyan",
        )
        # Cast to expected type (runtime type is compatible)
        return r[list[str]].ok(filtered)

    cli.formatters.print(f"📋 Total items: {len(items)}", style="cyan")
    # Cast to expected type (runtime type is compatible)
    return r[list[str]].ok(items)


def handle_config_command(key: str = "", value: str = "") -> r[str]:
    """Config management in YOUR interactive CLI."""
    if key and value:
        cli.formatters.print(f"✅ Set {key}={value}", style="green")
        return r[str].ok(f"Set {key}={value}")
    if key:
        # Get config value
        cli.formatters.print(f"📖 Reading {key}...", style="cyan")
        return r[str].ok("value")
    cli.formatters.print("⚠️  Usage: config <key> [value]", style="yellow")
    return r[str].fail("Missing key")


# ============================================================================
# PATTERN 2: Command dispatcher for YOUR shell
# ============================================================================


class InteractiveShell:
    """Interactive shell for YOUR CLI application."""

    def __init__(self) -> None:
        """Initialize interactive shell with command registry."""
        super().__init__()
        self.commands = {
            "status": handle_status_command,
            "list": handle_list_command,
            "config": handle_config_command,
            "help": self.show_help,
            "exit": self.exit_shell,
        }
        self.running = False

    def show_help(self) -> r[bool]:
        """Show available commands."""
        cli.formatters.print("\n📚 Available Commands:", style="bold cyan")
        for cmd in self.commands:
            cli.formatters.print(f"   • {cmd}", style="white")
        return r[bool].ok(True)

    def exit_shell(self) -> r[bool]:
        """Exit interactive shell."""
        cli.formatters.print("👋 Goodbye!", style="cyan")
        self.running = False
        return r[bool].ok(True)

    def execute_command(self, command_line: str) -> r[object]:
        """Execute command from user input."""
        parts = command_line.strip().split()
        if not parts:
            return r[object].fail("Empty command")

        cmd_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if cmd_name not in self.commands:
            return r[object].fail(f"Unknown command: {cmd_name}")

        handler = self.commands[cmd_name]

        try:
            # Call handler with args - type narrowing
            if callable(handler):
                result = handler(*args) if args else handler()
                # Type narrowing: ensure r
                if isinstance(result, r):
                    # Type narrowing: result is r[T] for some T
                    # r is covariant, so r[T] is compatible with r[object]
                    # Return with explicit type annotation to satisfy type checker
                    return_val: r[object] = result
                    return return_val
                # Wrap non-r in r
                return r[object].ok(result)
            return r[object].fail("Handler is not callable")
        except Exception as e:
            return r[object].fail(f"Command error: {e}")


# ============================================================================
# PATTERN 3: Multi-line input support
# ============================================================================


def handle_multiline_input(lines: list[str]) -> str:
    """Process multi-line input in YOUR interactive CLI."""
    combined = "\n".join(lines)
    cli.formatters.print(f"📝 Processing {len(lines)} lines...", style="cyan")
    cli.formatters.print(f"   Total chars: {len(combined)}", style="white")
    return combined


# ============================================================================
# PATTERN 4: Command history
# ============================================================================


class CommandHistory:
    """Command history for YOUR interactive CLI."""

    def __init__(self, max_size: int = 100) -> None:
        """Initialize command history with maximum size limit."""
        super().__init__()
        self.history: list[str] = []
        self.max_size = max_size

    def add(self, command: str) -> None:
        """Add command to history."""
        self.history.append(command)
        if len(self.history) > self.max_size:
            self.history.pop(0)

    def get_recent(self, count: int = 10) -> list[str]:
        """Get recent commands."""
        return self.history[-count:]

    def display_history(self) -> None:
        """Display command history."""
        if not self.history:
            cli.formatters.print("📜 No command history", style="yellow")
            return

        cli.formatters.print("\n📜 Recent Commands (last 10):", style="bold cyan")
        for i, cmd in enumerate(self.get_recent(), 1):
            cli.formatters.print(f"   {i}. {cmd}", style="white")


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of shell interaction in YOUR code."""
    cli.formatters.print("=" * 70, style="bold blue")
    cli.formatters.print("  Interactive Shell Library Usage", style="bold white")
    cli.formatters.print("=" * 70, style="bold blue")

    # Example 1: Command handlers
    cli.formatters.print(
        "\n1. Command Handlers (status, list, config):",
        style="bold cyan",
    )
    handle_status_command()
    handle_list_command(filter_text="test")
    handle_config_command(key="theme", value="dark")

    # Example 2: Interactive shell
    cli.formatters.print(
        "\n2. Interactive Shell (command dispatcher):",
        style="bold cyan",
    )
    shell = InteractiveShell()
    shell.show_help()

    # Simulate command execution
    cli.formatters.print("\n   Simulating: status", style="yellow")
    shell.execute_command("status")

    cli.formatters.print("\n   Simulating: list test", style="yellow")
    shell.execute_command("list test")

    # Example 3: Multi-line input
    cli.formatters.print(
        "\n3. Multi-Line Input (combined processing):",
        style="bold cyan",
    )
    lines = ["SELECT * FROM users", "WHERE active = true", "ORDER BY created_at DESC"]
    handle_multiline_input(lines)

    # Example 4: Command history
    cli.formatters.print("\n4. Command History (tracking):", style="bold cyan")
    history = CommandHistory()
    history.add("status")
    history.add("list test")
    history.add("config theme dark")
    history.display_history()

    cli.formatters.print("\n" + "=" * 70, style="bold blue")
    cli.formatters.print("  ✅ Shell Interaction Examples Complete", style="bold green")
    cli.formatters.print("=" * 70, style="bold blue")

    # Integration guide
    cli.formatters.print("\n💡 Integration Tips:", style="bold cyan")
    cli.formatters.print(
        "  • Create command handlers with FlextResult returns",
        style="white",
    )
    cli.formatters.print(
        "  • Build command dispatcher to route user input",
        style="white",
    )
    cli.formatters.print("  • Add command history for better UX", style="white")
    cli.formatters.print(
        "  • Support multi-line input for complex commands",
        style="white",
    )


if __name__ == "__main__":
    main()
