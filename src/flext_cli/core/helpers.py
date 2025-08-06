"""FLEXT CLI Core Helper Classes - Utility Functions and Interactive Helpers.

This module provides essential helper classes and utility functions for FLEXT CLI
operations including user interaction, validation, file operations, and common
CLI patterns that are reused across multiple commands.

Helper Classes:
    - CLIHelper: General-purpose CLI utilities with Rich integration
    - Validation utilities for inputs, paths, and URLs
    - Interactive prompts and confirmations
    - Progress tracking and status reporting

Core Utilities:
    - User input validation and sanitization
    - File and path operations with safety checks
    - URL validation and parsing
    - Interactive confirmations for destructive operations
    - Progress tracking for long-running operations

Architecture:
    - Rich console integration for enhanced user interaction
    - Type-safe validation with comprehensive error handling
    - Reusable patterns for common CLI operations
    - Integration with CLI context and configuration

Current Implementation Status:
    ✅ Basic CLIHelper with interactive prompts
    ✅ Rich console integration for UX
    ✅ Input validation and confirmation utilities
    ⚠️ Basic implementation (TODO: Sprint 2 - enhance validation)
    ❌ Advanced file operations not implemented (TODO: Sprint 3)

TODO (docs/TODO.md):
    Sprint 2: Add comprehensive input validation and sanitization
    Sprint 3: Add advanced file and directory operations
    Sprint 7: Add monitoring and metrics collection helpers
    Sprint 8: Add interactive wizard and tutorial helpers

Features:
    - Safe user input collection with validation
    - Rich prompts with default values and validation
    - Confirmation dialogs for destructive operations
    - Progress tracking with Rich progress bars
    - Path validation and file safety checks

Usage Examples:
    >>> helper = CLIHelper()
    >>> if helper.confirm("Delete all data?", default=False):
    ...     # Perform destructive operation
    >>> username = helper.prompt("Username:", default="REDACTED_LDAP_BIND_PASSWORD")
    >>> file_path = helper.validate_file_path("/path/to/file")

Integration:
    - Used by all CLI commands for user interaction
    - Integrates with authentication for secure prompts
    - Supports configuration validation and setup
    - Compatible with Click command patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from rich.console import Console
from rich.progress import Progress
from rich.prompt import Confirm, Prompt


class CLIHelper:
    """General helper utilities for CLI applications."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def confirm(self, message: str, *, default: bool = False) -> bool:
        """Show confirmation prompt."""
        return Confirm.ask(message, default=default, console=self.console)

    def prompt(self, message: str, default: str | None = None) -> str:
        """Show text input prompt."""
        if default is not None:
            return Prompt.ask(message, default=default, console=self.console)
        return Prompt.ask(message, console=self.console)

    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except (ValueError, TypeError):
            return False

    def validate_path(self, path_str: str, *, must_exist: bool = True) -> bool:
        """Validate file path."""
        try:
            path = Path(path_str)
            if must_exist:
                return path.exists()
        except (ValueError, OSError):
            return False
        else:
            return True

    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        size_value: float = float(size_bytes)
        unit_size = 1024.0
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_value < unit_size:
                return f"{size_value:.1f} {unit}"
            size_value /= unit_size
        return f"{size_value:.1f} PB"

    def truncate_text(self, text: str, max_length: int = 50) -> str:
        """Truncate text with ellipsis."""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe filesystem usage."""
        # Remove unsafe characters
        safe_name = re.sub(r'[<>:"/\\|?*]', "_", filename)
        # Remove leading/trailing dots and spaces
        safe_name = safe_name.strip(". ")
        # Ensure it's not empty
        return safe_name or "untitled"

    def create_progress(self, description: str = "Processing...") -> Progress:
        """Create progress bar."""
        _ = description  # Currently unused but kept for future extensibility
        return Progress(console=self.console)

    def print_success(self, message: str) -> None:
        """Print success message."""
        self.console.print(f"[bold green]✓[/bold green] {message}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"[bold red]✗[/bold red] {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")

    def print_info(self, message: str) -> None:
        """Print info message."""
        self.console.print(f"[bold blue]i[/bold blue] {message}")
