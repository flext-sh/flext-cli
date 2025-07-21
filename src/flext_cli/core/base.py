"""Base classes and utilities for FLEXT CLI framework.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import logging
import sys
import traceback
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

import click
from flext_core import Field
from flext_core.domain.pydantic_base import DomainBaseModel
from flext_core.domain.types import ServiceResult
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

# Import CLI config from utils
from flext_cli.utils.config import get_config

if TYPE_CHECKING:
    from flext_cli.utils.config import CLIConfig


# Use centralized ServiceResult from flext-core - ELIMINATE DUPLICATION


# Type variables for decorators
F = TypeVar("F", bound=Callable[..., Any])


class CLICommand(DomainBaseModel):
    """Base command model using flext-core patterns."""

    name: str = Field(..., description="Command name")
    description: str = Field(..., description="Command description")
    help_text: str = Field(..., description="Command help text")


class CLIContext(DomainBaseModel):
    """CLI context model using flext-core patterns."""

    profile: str = Field(default="default", description="Active profile")
    output_format: str = Field(default="table", description="Output format")
    debug: bool = Field(default=False, description="Debug mode")
    quiet: bool = Field(default=False, description="Quiet mode")
    verbose: bool = Field(default=False, description="Verbose mode")
    no_color: bool = Field(default=False, description="No color mode")


class CLIResultRenderer(ABC):
    """Abstract renderer for CLI results using flext-core interfaces."""

    @abstractmethod
    def render_success(self, result: ServiceResult[Any]) -> None:
        """Render successful result."""
        ...

    @abstractmethod
    def render_error(self, result: ServiceResult[Any]) -> None:
        """Render error result."""
        ...

    @abstractmethod
    def render_table(self, data: list[Any], title: str | None = None) -> None:
        """Render data as table."""
        ...


class RichCLIRenderer(CLIResultRenderer):
    """Rich-based CLI renderer implementation."""

    def __init__(self, console: Console, config: CLIConfig) -> None:
        """Initialize Rich CLI renderer.

        Args:
            console: Rich console instance
            config: CLI configuration

        """
        self.console = console
        self.config = config
        self.logger = logging.getLogger("cli-renderer")

    def render_success(self, result: ServiceResult[Any]) -> None:
        """Render successful result."""
        if result.is_success and not self.config.quiet:
            self.console.print(f"[bold green]✓[/bold green] {result.data}")
        self.logger.info(f"Success: {result.data}")

    def render_error(self, result: ServiceResult[Any]) -> None:
        """Render error result."""
        if not result.is_success:
            self.console.print(f"[bold red]Error:[/bold red] {result.error}")
        self.logger.error(f"Error: {result.error}")

    def render_table(self, data: list[Any], title: str | None = None) -> None:
        """Render data as table."""
        from flext_cli.core.formatters import FormatterFactory

        if not data:
            if not self.config.quiet:
                self.console.print("[yellow]No data to display[/yellow]")
            return

        # Use the existing formatter system
        formatter = FormatterFactory.create(self.config.output_format)
        formatter.format(data, self.console)

    def render_any(self, data: Any) -> None:
        """Render arbitrary data."""
        from flext_cli.core.formatters import FormatterFactory

        formatter = FormatterFactory.create(self.config.output_format)
        formatter.format(data, self.console)


class BaseCLI(ABC):
    """Base class for all FLEXT CLI applications using Clean Architecture."""

    def __init__(self, name: str, version: str, description: str) -> None:
        """Initialize base CLI application.

        Args:
            name: Application name
            version: Application version
            description: Application description

        """
        self.name = name
        self.version = version
        self.description = description

        # Use flext-core config exclusively
        self.config = get_config()
        self.config.project_name = name
        self.config.project_version = version

        # Initialize console and logger
        self.console = Console(no_color=self.config.no_color)
        self.logger = logging.getLogger(name)

        # Initialize renderer
        self.renderer = RichCLIRenderer(self.console, self.config)

        # Initialize context
        self.context = CLIContext(
            profile=self.config.profile,
            output_format=self.config.output_format,
            debug=self.config.debug,
            quiet=self.config.quiet,
            verbose=self.config.verbose,
            no_color=self.config.no_color,
        )

    def print_header(self) -> None:
        """Print application header."""
        if not self.config.quiet:
            self.console.print(
                Panel.fit(
                    f"[bold cyan]{self.name}[/bold cyan] v{self.version}\n"
                    f"{self.description}",
                    border_style="cyan",
                ),
            )

    def handle_result(self, result: ServiceResult[Any]) -> None:
        """Handle service result."""
        if result.is_success:
            self.renderer.render_success(result)
        else:
            self.renderer.render_error(result)
            sys.exit(1)

    def create_table(
        self,
        title: str | None = None,
        columns: list[tuple[str, str]] | None = None,
    ) -> Table:
        """Create Rich table."""
        table = Table(title=title, show_header=True, header_style="bold cyan")
        if columns:
            for name, style in columns:
                table.add_column(name, style=style)
        return table

    def create_tree(self, label: str, style: str = "cyan") -> Tree:
        """Create Rich tree."""
        return Tree(label, style=style)

    def create_progress(self, description: str = "Processing...") -> Progress:
        """Create Rich progress bar."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        )

    @abstractmethod
    def create_cli(self) -> click.Group:
        """Create CLI application."""
        ...


# Clean Architecture CLI Decorators using flext-core patterns


def with_context[F: Callable[..., Any]](f: F) -> F:
    """Decorator to inject CLI context."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Extract context from Click context
        ctx = click.get_current_context()
        cli_context = ctx.obj.get("cli_context")
        if cli_context:
            kwargs["cli_context"] = cli_context
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper  # type: ignore[return-value]


def handle_service_result[F: Callable[..., Any]](f: F) -> F:
    """Decorator to handle service results."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            result = f(*args, **kwargs)
            if hasattr(result, "success"):
                # Check if it's a ServiceResult-like object
                ctx = click.get_current_context()
                cli_context = ctx.obj.get("cli_context")
                if cli_context:
                    if result.success:
                        cli_context.print_success(str(result.data))
                    else:
                        cli_context.print_error(str(result.error))
                        sys.exit(1)
            return result
        except Exception as e:
            ctx = click.get_current_context()
            cli_context = ctx.obj.get("cli_context")
            if cli_context:
                cli_context.print_error(str(e))
                if hasattr(cli_context, "is_debug") and cli_context.is_debug:
                    cli_context.print_debug(traceback.format_exc())
            sys.exit(1)

    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper  # type: ignore[return-value]
