"""FlextCli protocol definitions module - Structural typing."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from types import TracebackType
from typing import Protocol, Self, runtime_checkable

from flext_core import FlextProtocols, r

from flext_cli import t


class FlextCliProtocols(FlextProtocols):
    """CLI protocol definitions extending FlextProtocols."""

    class Cli:
        """CLI protocol namespace for all CLI-specific protocols."""

        """Rich display abstraction protocols - NO IMPORTS of Rich classes."""

        @runtime_checkable
        class RichTable(Protocol):
            """Protocol for Rich Table objects."""

            def add_column(self, header: str, **kwargs: t.Scalar) -> None:
                """Add a column to the table."""
                ...

            def add_row(self, *cells: str, **kwargs: t.Scalar) -> None:
                """Add a row to the table."""
                ...

        @runtime_checkable
        class RichTree(Protocol):
            """Protocol for Rich Tree objects."""

            def add(
                self,
                label: str,
                **kwargs: t.Scalar,
            ) -> FlextCliProtocols.Cli.RichTree:
                """Add a branch to the tree."""
                ...

        @runtime_checkable
        class RichConsole(Protocol):
            """Protocol for Rich Console objects."""

            def print(
                self,
                text: str,
                style: str | None = None,
                **kwargs: t.Scalar,
            ) -> None:
                """Print text to the console."""
                ...

        # """Interactive display abstraction protocols."""

        @runtime_checkable
        class RichProgress(Protocol):
            """Protocol for Rich Progress objects."""

            def __enter__(self) -> Self:
                """Enter the context manager."""
                ...

            def __exit__(
                self,
                exc_type: type[BaseException] | None,
                exc_val: BaseException | None,
                exc_tb: TracebackType | None,
            ) -> None:
                """Exit the context manager."""
                ...

        @runtime_checkable
        class Command(Protocol):
            """Protocol for CLI commands."""

            @property
            def args(self) -> t.StrSequence:
                """Get command arguments."""
                ...

            @property
            def command_line(self) -> str:
                """Get full command line."""
                ...

            @property
            def command_summary(self) -> t.StrMapping:
                """Get command summary."""
                ...

            @property
            def created_at(self) -> datetime:
                """Get creation timestamp."""
                ...

            @property
            def description(self) -> str:
                """Get command description."""
                ...

            @property
            def entry_point(self) -> str:
                """Get command entry point."""
                ...

            @property
            def error_output(self) -> str:
                """Get command error output."""
                ...

            @property
            def execution_time(self) -> float | None:
                """Get execution time in seconds."""
                ...

            @property
            def exit_code(self) -> int | None:
                """Get command exit code."""
                ...

            @property
            def kwargs(self) -> Mapping[str, t.Cli.JsonValue]:
                """Get command keyword arguments."""
                ...

            @property
            def name(self) -> str:
                """Get command name."""
                ...

            @property
            def output(self) -> str:
                """Get command output."""
                ...

            @property
            def plugin_version(self) -> str:
                """Get plugin version."""
                ...

            @property
            def result(self) -> t.Cli.JsonValue | None:
                """Get command result."""
                ...

            @property
            def status(self) -> str:
                """Get command status."""
                ...

            @property
            def updated_at(self) -> datetime | None:
                """Get update timestamp."""
                ...

            @property
            def usage(self) -> str:
                """Get command usage."""
                ...

            def complete_execution(self, exit_code: int) -> r[Self]:
                """Complete command execution."""
                ...

            def execute(
                self,
                args: t.StrSequence,
            ) -> r[t.Cli.JsonValue]:
                """Execute the command."""
                ...

            def start_execution(self) -> r[Self]:
                """Start command execution."""
                ...

            def update_status(self, status: str) -> Self:
                """Update command status."""
                ...

            def with_args(self, args: t.StrSequence) -> Self:
                """Return a copy with updated arguments."""
                ...

            def with_status(self, status: str) -> Self:
                """Return a copy with updated status."""
                ...

        @runtime_checkable
        class CliParameterSpec(Protocol):
            """Protocol for CLI parameter specification matching m.Cli.CliParameterSpec."""

            @property
            def click_type(self) -> str:
                """Get Click type name."""
                ...

            @property
            def default(self) -> t.Cli.JsonValue | None:
                """Get default value."""
                ...

            @property
            def field_name(self) -> str:
                """Get field name."""
                ...

            @property
            def help(self) -> str:
                """Get help text."""
                ...

            @property
            def name(self) -> str:
                """Get parameter name."""
                ...

            @property
            def param_type(self) -> type:
                """Get parameter type."""
                ...

        @runtime_checkable
        class ConfirmConfig(Protocol):
            """Protocol for CLI confirmation configuration."""

            @property
            def abort(self) -> bool:
                """Check if should abort on negative confirmation."""
                ...

            @property
            def default(self) -> bool:
                """Get default confirmation value."""
                ...

            @property
            def err(self) -> bool:
                """Check if output should go to stderr."""
                ...

            @property
            def prompt_suffix(self) -> str:
                """Get prompt suffix."""
                ...

            @property
            def show_default(self) -> bool:
                """Check if default value should be shown."""
                ...

        @runtime_checkable
        class TableConfig(Protocol):
            """Protocol for CLI table configuration."""

            @property
            def headers(self) -> t.StrSequence:
                """Get table headers."""
                ...

            @property
            def show_header(self) -> bool:
                """Check if header should be shown."""
                ...

        @runtime_checkable
        class CliParamsConfig(Protocol):
            """Protocol for CLI parameters configuration."""

            @property
            def debug(self) -> bool | None:
                """Check if debug mode is enabled."""
                ...

            @property
            def log_format(self) -> str | None:
                """Get log format."""
                ...

            @property
            def log_level(self) -> str | None:
                """Get log level."""
                ...

            @property
            def no_color(self) -> bool | None:
                """Check if color is disabled."""
                ...

            @property
            def output_format(self) -> str | None:
                """Get output format."""
                ...

            @property
            def params(self) -> Mapping[str, t.Cli.JsonValue]:
                """Get configuration parameters."""
                ...

            @property
            def quiet(self) -> bool | None:
                """Check if quiet mode is enabled."""
                ...

            @property
            def trace(self) -> bool | None:
                """Check if trace mode is enabled."""
                ...

            @property
            def verbose(self) -> bool | None:
                """Check if verbose mode is enabled."""
                ...

        type CliRegisteredCommand = FlextCliProtocols.Cli.Command

        @runtime_checkable
        class CliCommandFunction(Protocol):
            """Protocol for CLI command functions that may return None."""

            def __call__(
                self,
                *args: t.Cli.JsonValue,
                **kwargs: t.Scalar,
            ) -> t.Cli.JsonValue | None:
                """Execute the function."""
                ...

        @runtime_checkable
        class CliCommandWrapper(Protocol):
            """Protocol for dynamically-created CLI command wrapper functions."""

            def __call__(
                self,
                *args: t.Cli.JsonValue,
                **kwargs: t.Scalar,
            ) -> t.Cli.JsonValue:
                """Execute the wrapper."""
                ...

        @runtime_checkable
        class CommandHandlerCallable(Protocol):
            """Protocol for command handlers returning r."""

            def __call__(
                self,
                *args: t.Cli.JsonValue,
                **kwargs: t.Scalar,
            ) -> r[t.Cli.JsonValue]:
                """Execute the handler."""
                ...

        @runtime_checkable
        class CliContext(Protocol):
            """Protocol for CLI execution context."""

            @property
            def args(self) -> t.StrSequence:
                """Get command arguments."""
                ...

            @property
            def cwd(self) -> str:
                """Get current working directory."""
                ...

            @property
            def env(self) -> t.StrMapping:
                """Get environment variables."""
                ...

            params: Mapping[str, t.Cli.JsonValue]

        @runtime_checkable
        class CliCommandHandler(Protocol):
            """Protocol for CLI command handlers."""

            def __call__(self, **kwargs: t.Scalar) -> t.Cli.JsonValue:
                """Execute the command handler."""
                ...

        @runtime_checkable
        class DecoratorCommandLike(Protocol):
            """Structural type for typer/click Command-like objects (name + callback)."""

            @property
            def name(self) -> str:
                """Command name."""
                ...

            @property
            def callback(self) -> Callable[..., t.Cli.JsonValue]:
                """Command callback callable."""
                ...


__all__ = ["FlextCliProtocols", "p"]

p = FlextCliProtocols
