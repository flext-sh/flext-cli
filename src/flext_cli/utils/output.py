"""Output utilities for FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console

# Global console instance
_console: Console | None = None

# Color enable/disable flag (for testing)
COLORS_ENABLED = True


def setup_console(console: Console | None = None) -> Console:
    """Setup console for CLI output.

    Args:
        console: Optional console instance to use

    Returns:
        Console instance

    """
    global _console

    if console is not None:
        _console = console
        return console

    if _console is None:
        from rich.console import Console
        _console = Console()

    return _console


def get_console() -> Console:
    """Get the current console instance.

    Returns:
        Console instance

    """
    if _console is None:
        return setup_console()
    return _console


def print_success(message: str) -> None:
    """Print success message in green.

    Args:
        message: Success message to print

    """
    console = get_console()
    if COLORS_ENABLED:
        console.print(f"[green]✅ {message}[/green]")


def print_error(message: str) -> None:
    """Print error message in red.

    Args:
        message: Error message to print

    """
    console = get_console()
    if COLORS_ENABLED:
        console.print(f"[red]❌ {message}[/red]")


def print_warning(message: str) -> None:
    """Print warning message in yellow.

    Args:
        message: Warning message to print

    """
    console = get_console()
    if COLORS_ENABLED:
        console.print(f"[yellow]⚠️ {message}[/yellow]")


def print_info(message: str) -> None:
    """Print info message in blue.

    Args:
        message: Info message to print

    """
    console = get_console()
    if COLORS_ENABLED:
        console.print(f"[blue]ℹ️ {message}[/blue]")


def print_debug(message: str) -> None:
    """Print debug message in dim style.

    Args:
        message: Debug message to print

    """
    if os.getenv("FLEXT_CLI_DEBUG"):
        console = get_console()
        if COLORS_ENABLED:
            console.print(f"[dim]🔍 DEBUG: {message}[/dim]")


__all__ = [
    "COLORS_ENABLED",
    "get_console",
    "print_debug",
    "print_error",
    "print_info",
    "print_success",
    "print_warning",
    "setup_console",
]
