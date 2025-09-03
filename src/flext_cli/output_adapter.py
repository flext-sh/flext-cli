"""FlextCli Output Adapter - Clean protocol implementation."""

from __future__ import annotations

import json

from flext_core import FlextResult
from rich.console import Console


class FlextCliOutputAdapter:
    """Clean adapter implementing FlextCliOutputProtocol."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def print_data(self, data: object, format_type: str = "table") -> FlextResult[None]:
        """Print data to terminal in specified format."""
        try:
            if format_type == "json":
                self.console.print(json.dumps(data, indent=2, default=str))
            elif format_type == "yaml":
                try:
                    import yaml

                    self.console.print(yaml.safe_dump(data))
                except ImportError:
                    self.console.print(str(data))
            else:
                self.console.print(str(data))
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print failed: {e}")

    def print_success(self, message: str) -> FlextResult[None]:
        """Print success message with styling."""
        try:
            self.console.print(f"[bold green]✓[/bold green] {message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print success failed: {e}")

    def print_error(self, message: str) -> FlextResult[None]:
        """Print error message with styling."""
        try:
            self.console.print(f"[bold red]✗[/bold red] {message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print error failed: {e}")

    def print_warning(self, message: str) -> FlextResult[None]:
        """Print warning message with styling."""
        try:
            self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print warning failed: {e}")

    def print_info(self, message: str) -> FlextResult[None]:
        """Print info message with styling."""
        try:
            self.console.print(f"[bold blue]i[/bold blue] {message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print info failed: {e}")

    def show_progress(self, description: str, total: int | None = None) -> object:
        """Show progress indicator."""
        if total:
            return self.console.status(f"{description} (0/{total})")
        return self.console.status(description)


__all__ = ["FlextCliOutputAdapter"]
