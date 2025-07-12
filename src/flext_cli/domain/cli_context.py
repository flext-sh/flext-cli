"""CLI context for dependency injection and state management."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ConfigDict, Field

from flext_core.domain.pydantic_base import DomainValueObject

if TYPE_CHECKING:
    from rich.console import Console

    from flext_cli.utils.config import CLIConfig
    from flext_cli.utils.config import CLISettings


class CLIContext(DomainValueObject):
    """CLI context containing configuration and services."""

    config: CLIConfig = Field(..., description="CLI configuration")
    settings: CLISettings = Field(..., description="CLI settings")
    console: Console = Field(..., description="Rich console instance")

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Allow Console type

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled.

        Returns:
            True if debug/verbose mode is enabled.

        """
        return self.config.verbose

    @property
    def is_quiet(self) -> bool:
        """Check if quiet mode is enabled.

        Returns:
            True if quiet mode is enabled.

        """
        return self.config.quiet

    @property
    def is_verbose(self) -> bool:
        """Check if verbose mode is enabled.

        Returns:
            True if verbose mode is enabled.

        """
        return self.config.verbose

    def print_debug(self, message: str) -> None:
        """Print debug message if debug mode is enabled.

        Args:
            message: Debug message to print.

        """
        if self.is_debug:
            self.console.print(f"[dim][DEBUG][/dim] {message}")

    def print_info(self, message: str) -> None:
        """Print info message if not in quiet mode.

        Args:
            message: Info message to print.

        """
        if not self.is_quiet:
            self.console.print(f"[blue][INFO][/blue] {message}")

    def print_success(self, message: str) -> None:
        """Print success message.

        Args:
            message: Success message to print.

        """
        self.console.print(f"[green][SUCCESS][/green] {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message.

        Args:
            message: Warning message to print.

        """
        self.console.print(f"[yellow][WARNING][/yellow] {message}")

    def print_error(self, message: str) -> None:
        """Print error message.

        Args:
            message: Error message to print.

        """
        self.console.print(f"[red][ERROR][/red] {message}")

    def print_verbose(self, message: str) -> None:
        """Print verbose message if verbose mode is enabled.

        Args:
            message: Verbose message to print.

        """
        if self.is_verbose:
            self.console.print(f"[dim][VERBOSE][/dim] {message}")
