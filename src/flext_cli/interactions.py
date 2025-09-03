"""FLEXT CLI Interactions - User interaction utilities following flext-core patterns.

Provides FlextCliInteractions class for user prompts, confirmations, and interactive
elements with FlextResult error handling and Rich integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Confirm, Prompt


class FlextCliInteractions:
    """Consolidated user interaction utilities following flext-core patterns.

    Provides comprehensive user interaction operations including prompts,
    confirmations, and progress indicators with FlextResult error handling.

    Features:
        - Interactive prompts with validation
        - Confirmation dialogs with defaults
        - Progress indicators for long operations
        - Status messages with styled output
        - Quiet mode support for automation
    """

    def __init__(self, *, console: Console | None = None, quiet: bool = False) -> None:
        """Initialize interactions manager with console and quiet mode.

        Args:
            console: Rich console instance for output
            quiet: Enable quiet mode for automation

        """
        self.console: Console = console or Console()
        self.quiet: bool = quiet

    def confirm(self, message: str, *, default: bool = False) -> FlextResult[bool]:
        """Get user confirmation with styled prompt.

        Args:
            message: Confirmation message to display
            default: Default value if user presses enter

        Returns:
            FlextResult containing user's boolean choice

        """
        if self.quiet:
            return FlextResult[bool].ok(default)
        try:
            answer = bool(Confirm.ask(message, default=default))
            return FlextResult[bool].ok(answer)
        except KeyboardInterrupt:
            return FlextResult[bool].fail("User interrupted confirmation")
        except Exception as e:
            return FlextResult[bool].fail(f"Confirmation failed: {e}")

    def prompt(self, message: str, *, default: str | None = None) -> FlextResult[str]:
        """Get user text input with validation.

        Args:
            message: Prompt message to display
            default: Default value if user presses enter

        Returns:
            FlextResult containing user's input string

        """
        if self.quiet and default is not None:
            return FlextResult[str].ok(default)
        try:
            value = str(Prompt.ask(message, default=default or "")).strip()
            if not value and default is None:
                return FlextResult[str].fail("Empty input is not allowed")
            return FlextResult[str].ok(value or (default or ""))
        except KeyboardInterrupt:
            return FlextResult[str].fail("User interrupted prompt")
        except Exception as e:
            return FlextResult[str].fail(f"Prompt failed: {e}")

    def print_status(self, message: str, *, status: str = "info") -> FlextResult[None]:
        """Print status message with styled formatting.

        Args:
            message: Status message to display
            status: Status type (info, success, warning, error)

        Returns:
            FlextResult indicating success or failure

        """
        try:
            styles = {
                "info": "[bold blue]i[/bold blue] ",
                "success": "[bold green]✓[/bold green] ",
                "warning": "[bold yellow]⚠[/bold yellow] ",
                "error": "[bold red]✗[/bold red] ",
            }
            prefix = styles.get(status, "")
            self.console.print(f"{prefix}{message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print status failed: {e}")

    def print_success(self, message: str) -> FlextResult[None]:
        """Print success message with green styling.

        Args:
            message: Success message to display

        Returns:
            FlextResult indicating success or failure

        """
        return self.print_status(message, status="success")

    def print_error(self, message: str) -> FlextResult[None]:
        """Print error message with red styling.

        Args:
            message: Error message to display

        Returns:
            FlextResult indicating success or failure

        """
        return self.print_status(message, status="error")

    def print_warning(self, message: str) -> FlextResult[None]:
        """Print warning message with yellow styling.

        Args:
            message: Warning message to display

        Returns:
            FlextResult indicating success or failure

        """
        return self.print_status(message, status="warning")

    def print_info(self, message: str) -> FlextResult[None]:
        """Print info message with blue styling.

        Args:
            message: Info message to display

        Returns:
            FlextResult indicating success or failure

        """
        return self.print_status(message, status="info")

    def create_progress(self, message: str = "") -> FlextResult[Progress]:
        """Create Rich progress indicator for long operations.

        Args:
            message: Progress description message

        Returns:
            FlextResult containing Progress instance

        """
        try:
            _ = message  # Keep signature for future use
            progress = Progress()
            return FlextResult[Progress].ok(progress)
        except Exception as e:
            return FlextResult[Progress].fail(f"Progress creation failed: {e}")

    def with_progress(
        self, items: list[object], message: str
    ) -> FlextResult[list[object]]:
        """Process items with progress indicator (minimal implementation).

        Args:
            items: Items to process
            message: Progress message

        Returns:
            FlextResult containing processed items

        """
        try:
            _ = message  # For future enhanced implementation
            return FlextResult[list[object]].ok(items)
        except Exception as e:
            return FlextResult[list[object]].fail(f"Progress processing failed: {e}")


__all__ = ["FlextCliInteractions"]
