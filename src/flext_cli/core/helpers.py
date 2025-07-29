"""Helper classes for FLEXT CLI framework.

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
            return True
        except (ValueError, OSError):
            return False

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
