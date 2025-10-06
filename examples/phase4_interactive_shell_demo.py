"""FLEXT-CLI Phase 4.4 Interactive Shell Demo.

This example demonstrates Phase 4.4 interactive shell (REPL) features:
- Interactive command shell with REPL
- Command history and persistence
- Tab completion support
- Built-in shell commands
- Session management
- Shell builder pattern

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCli, FlextCliShell


def demo_basic_shell() -> None:
    """Demo 1: Basic Interactive Shell."""
    # Create CLI with commands
    cli = FlextCli()

    @cli.main.command()
    def hello(name: str = "World") -> None:
        """Say hello."""

    @cli.main.command()
    def status() -> None:
        """Show status."""

    @cli.main.command()
    def info() -> None:
        """Show information."""

    # Create shell
    FlextCliShell(cli_main=cli.main, prompt="demo> ")


def demo_shell_with_history() -> None:
    """Demo 2: Shell with Command History."""
    cli = FlextCli()

    @cli.main.command()
    def data(action: str) -> None:
        """Data management."""

    # Create shell with history
    FlextCliShell(
        cli_main=cli.main,
        prompt="history-demo> ",
        history_file="~/.flext_demo_history",
    )


def demo_shell_with_completion() -> None:
    """Demo 3: Shell with Tab Completion."""
    cli = FlextCli()

    @cli.main.command()
    def deploy(environment: str) -> None:
        """Deploy to environment."""

    @cli.main.command()
    def test(suite: str) -> None:
        """Run test suite."""

    # Create shell with completion
    FlextCliShell(
        cli_main=cli.main,
        prompt="complete> ",
        enable_completion=True,
    )


def demo_shell_builder() -> None:
    """Demo 4: Shell Builder Pattern."""
    cli = FlextCli()

    @cli.main.command()
    def build(target: str) -> None:
        """Build target."""

    @cli.main.command()
    def clean() -> None:
        """Clean build artifacts."""

    # Use builder pattern
    builder = FlextCliShell(cli.main)

    (
        builder.with_prompt("builder> ")
        .with_history("~/.flext_builder_history")
        .with_completion(True)
        .build()
    )


def demo_builtin_commands() -> None:
    """Demo 5: Built-in Shell Commands."""


def demo_session_management() -> None:
    """Demo 6: Session Management."""


def demo_error_handling() -> None:
    """Demo 7: Error Handling in Shell."""


def demo_full_featured_shell() -> None:
    """Demo 8: Full-Featured Shell Example."""
    # Create CLI with realistic commands
    cli = FlextCli()

    @cli.main.group()
    def db() -> None:
        """Database commands."""

    @db.command()
    def connect(host: str = "localhost") -> None:
        """Connect to database."""

    @db.command()
    def status() -> None:
        """Show database status."""

    @cli.main.group()
    def cache() -> None:
        """Cache commands."""

    @cache.command()
    def clear() -> None:
        """Clear cache."""

    @cache.command()
    def stats() -> None:
        """Show cache statistics."""

    # Create full-featured shell
    (
        FlextCliShell(cli.main)
        .with_prompt("myapp> ")
        .with_history("~/.myapp_history")
        .with_completion(True)
        .build()
    )


def main() -> None:
    """Run all Phase 4.4 interactive shell demos."""
    # Run all demos
    demo_basic_shell()
    demo_shell_with_history()
    demo_shell_with_completion()
    demo_shell_builder()
    demo_builtin_commands()
    demo_session_management()
    demo_error_handling()
    demo_full_featured_shell()

    # Final summary


if __name__ == "__main__":
    main()
