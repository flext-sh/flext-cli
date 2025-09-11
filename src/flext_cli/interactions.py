"""FLEXT CLI Interactions - User interaction utilities following flext-core patterns.

Provides FlextCliInteractions class for user prompts, confirmations, and interactive
elements with FlextResult error handling and Rich integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult, FlextTypes
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Confirm, Prompt


class FlextCliInteractions:
    """User interaction utilities following SOLID principles.

    Single responsibility: User interaction operations.
    Uses Rich for output formatting with FlextResult error handling.
    """

    def __init__(self, *, console: Console | None = None, quiet: bool = False) -> None:
        """Initialize interactions manager."""
        self.console: Console = console or Console()
        self.quiet: bool = quiet

    def confirm(self, message: str, *, default: bool = False) -> FlextResult[bool]:
        """Get user confirmation."""
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
        """Get user text input."""
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
        """Print status message with styled formatting."""
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
        """Print success message."""
        return self.print_status(message, status="success")

    def print_error(self, message: str) -> FlextResult[None]:
        """Print error message."""
        return self.print_status(message, status="error")

    def print_warning(self, message: str) -> FlextResult[None]:
        """Print warning message."""
        return self.print_status(message, status="warning")

    def print_info(self, message: str) -> FlextResult[None]:
        """Print info message."""
        return self.print_status(message, status="info")

    def create_progress(self, message: str = "") -> FlextResult[Progress]:
        """Create Rich progress indicator."""
        try:
            _ = message  # Keep signature for future use
            progress = Progress()
            return FlextResult[Progress].ok(progress)
        except Exception as e:
            return FlextResult[Progress].fail(f"Progress creation failed: {e}")

    def with_progress(
        self,
        items: FlextTypes.Core.List,
        message: str,
    ) -> FlextResult[FlextTypes.Core.List]:
        """Process items with progress indicator."""
        try:
            _ = message  # For future enhanced implementation
            return FlextResult[FlextTypes.Core.List].ok(items)
        except Exception as e:
            return FlextResult[FlextTypes.Core.List].fail(
                f"Progress processing failed: {e}"
            )


__all__ = ["FlextCliInteractions"]
