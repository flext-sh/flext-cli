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
- Command dispatcher with r integration
- Command history tracking
- Multi-line input support
- Auto-completion for YOUR commands

HOW TO IMPLEMENT IN YOUR CLI:
Use flext-cli foundation (r, cli) + prompt_toolkit library

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import time
from collections.abc import MutableSequence

from examples import c, t
from flext_cli import cli
from flext_core import r


def handle_status_command() -> r[t.RecursiveContainerMapping]:
    """Status command in YOUR interactive CLI."""
    status = {
        "status": "running",
        "user": os.getenv("USER", "unknown"),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    cli.print(f"✅ Status: {status['status']}", style=c.Cli.MessageStyles.GREEN)
    cli.print(f"   User: {status['user']}", style=c.Cli.MessageStyles.CYAN)
    return r[t.RecursiveContainerMapping].ok(dict(status))


def handle_list_command(filter_text: str = "") -> r[t.StrSequence]:
    """List command with filtering in YOUR CLI."""
    items = list(c.EXAMPLE_DEFAULT_SHELL_ITEMS)
    if filter_text:
        filtered = [item for item in items if filter_text in item]
        cli.print(
            f"📋 Found {len(filtered)} items matching '{filter_text}'",
            style=c.Cli.MessageStyles.CYAN,
        )
        return r[t.StrSequence].ok(filtered)
    cli.print(f"📋 Total items: {len(items)}", style=c.Cli.MessageStyles.CYAN)
    return r[t.StrSequence].ok(items)


def handle_config_command(key: str = "", value: str = "") -> r[str]:
    """Config management in YOUR interactive CLI."""
    if key and value:
        cli.print(f"✅ Set {key}={value}", style=c.Cli.MessageStyles.GREEN)
        return r[str].ok(f"Set {key}={value}")
    if key:
        cli.print(f"📖 Reading {key}...", style=c.Cli.MessageStyles.CYAN)
        return r[str].ok("value")
    cli.print("⚠️  Usage: settings <key> [value]", style=c.Cli.MessageStyles.YELLOW)
    return r[str].fail("Missing key")


class InteractiveShell:
    """Interactive shell for YOUR CLI application."""

    def __init__(self) -> None:
        """Initialize interactive shell with command registry."""
        super().__init__()
        self.commands = {
            "status": handle_status_command,
            "list": handle_list_command,
            "settings": handle_config_command,
            "help": self.show_help,
            "exit": self.exit_shell,
        }
        self.running = False

    def execute_command(self, command_line: str) -> r[str]:
        """Execute command from user input."""
        parts = command_line.strip().split()
        if not parts:
            return r[str].fail("Empty command")
        cmd_name = parts[0]
        args: t.StrSequence = parts[1:] if len(parts) > 1 else []
        if cmd_name not in self.commands:
            return r[str].fail(f"Unknown command: {cmd_name}")
        handler = self.commands[cmd_name]
        try:
            if callable(handler):
                result = handler(*args) if args else handler()
                if hasattr(result, "failure") and hasattr(result, "value"):
                    if result.failure:
                        return r[str].fail(result.error or "Unknown command error")
                    payload = result.value
                else:
                    payload = result
                return r[str].ok(str(payload))
            return r[str].fail("Handler is not callable")
        except Exception as e:
            return r[str].fail(f"Command error: {e}")

    def exit_shell(self) -> r[bool]:
        """Exit interactive shell."""
        cli.print("👋 Goodbye!", style=c.Cli.MessageStyles.CYAN)
        self.running = False
        return r[bool].ok(value=True)

    def show_help(self) -> r[bool]:
        """Show available commands."""
        cli.print("\n📚 Available Commands:", style=c.Cli.MessageStyles.BOLD_CYAN)
        for cmd in self.commands:
            cli.print(f"   • {cmd}", style=c.Cli.MessageStyles.WHITE)
        return r[bool].ok(value=True)


def handle_multiline_input(lines: t.StrSequence) -> str:
    """Process multi-line input in YOUR interactive CLI."""
    combined = "\n".join(lines)
    cli.print(f"📝 Processing {len(lines)} lines...", style=c.Cli.MessageStyles.CYAN)
    cli.print(f"   Total chars: {len(combined)}", style=c.Cli.MessageStyles.WHITE)
    return combined


class CommandHistory:
    """Command history for YOUR interactive CLI."""

    def __init__(self, max_size: int = 100) -> None:
        """Initialize command history with maximum size limit."""
        super().__init__()
        self.history: MutableSequence[str] = []
        self.max_size = max_size

    def add(self, command: str) -> None:
        """Add command to history."""
        self.history.append(command)
        if len(self.history) > self.max_size:
            self.history.pop(0)

    def display_history(self) -> None:
        """Display command history."""
        if not self.history:
            cli.print("📜 No command history", style=c.Cli.MessageStyles.YELLOW)
            return
        cli.print(
            "\n📜 Recent Commands (last 10):", style=c.Cli.MessageStyles.BOLD_CYAN
        )
        for i, cmd in enumerate(self.recent(), 1):
            cli.print(f"   {i}. {cmd}", style=c.Cli.MessageStyles.WHITE)

    def recent(self, count: int = 10) -> t.StrSequence:
        """Get recent commands."""
        return self.history[-count:]


def main() -> None:
    """Examples of shell interaction in YOUR code."""
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("  Interactive Shell Library Usage", style=c.Cli.MessageStyles.BOLD_WHITE)
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "\n1. Command Handlers (status, list, settings):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    handle_status_command()
    handle_list_command(filter_text="test")
    handle_config_command(key="theme", value="dark")
    cli.print(
        "\n2. Interactive Shell (command dispatcher):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    shell = InteractiveShell()
    shell.show_help()
    cli.print("\n   Simulating: status", style=c.Cli.MessageStyles.YELLOW)
    shell.execute_command("status")
    cli.print("\n   Simulating: list test", style=c.Cli.MessageStyles.YELLOW)
    shell.execute_command("list test")
    cli.print(
        "\n3. Multi-Line Input (combined processing):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    lines = ["SELECT * FROM users", "WHERE active = true", "ORDER BY created_at DESC"]
    combined = handle_multiline_input(lines)
    cli.print(f"   First 50 chars: {combined[:50]}...", style=c.Cli.MessageStyles.WHITE)
    cli.print("\n4. Command History (tracking):", style=c.Cli.MessageStyles.BOLD_CYAN)
    history = CommandHistory()
    history.add("status")
    history.add("list test")
    history.add("settings theme dark")
    history.display_history()
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  ✅ Shell Interaction Examples Complete", style=c.Cli.MessageStyles.BOLD_GREEN
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n💡 Integration Tips:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "  • Create command handlers with r returns", style=c.Cli.MessageStyles.WHITE
    )
    cli.print(
        "  • Build command dispatcher to route user input",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print("  • Add command history for better UX", style=c.Cli.MessageStyles.WHITE)
    cli.print(
        "  • Support multi-line input for complex commands",
        style=c.Cli.MessageStyles.WHITE,
    )


if __name__ == "__main__":
    main()
