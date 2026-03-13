"""FlextCli protocol definitions module - Structural typing."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from types import TracebackType
from typing import Protocol, Self, runtime_checkable

from flext_core import FlextProtocols, t


class FlextCliProtocols(FlextProtocols):
    """CLI protocol definitions extending FlextProtocols."""

    class Cli:
        """CLI protocol namespace for all CLI-specific protocols."""

        class Display:
            """Rich display abstraction protocols - NO IMPORTS of Rich classes."""

            @runtime_checkable
            class RichTableProtocol(Protocol):
                """Protocol for Rich Table objects."""

                def add_column(self, header: str, **kwargs: t.Scalar) -> None:
                    """Add a column to the table."""
                    ...

                def add_row(self, *cells: str, **kwargs: t.Scalar) -> None:
                    """Add a row to the table."""
                    ...

            @runtime_checkable
            class RichTreeProtocol(Protocol):
                """Protocol for Rich Tree objects."""

                def add(
                    self, label: str, **kwargs: t.Scalar
                ) -> FlextCliProtocols.Cli.Display.RichTreeProtocol:
                    """Add a branch to the tree."""
                    ...

            @runtime_checkable
            class RichConsoleProtocol(Protocol):
                """Protocol for Rich Console objects."""

                def print(
                    self, text: str, style: str | None = None, **kwargs: t.Scalar
                ) -> None:
                    """Print text to the console."""
                    ...

        class Interactive:
            """Interactive display abstraction protocols."""

            @runtime_checkable
            class RichProgressProtocol(Protocol):
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
            def args(self) -> Sequence[str]:
                """Get command arguments."""
                ...

            @property
            def command_line(self) -> str:
                """Get full command line."""
                ...

            @property
            def command_summary(self) -> Mapping[str, str]:
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
            def kwargs(self) -> Mapping[str, object]:
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
            def result(self) -> object | None:
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

            def complete_execution(self, exit_code: int) -> FlextProtocols.Result[Self]:
                """Complete command execution."""
                ...

            def execute(self, args: Sequence[str]) -> FlextProtocols.Result[object]:
                """Execute the command."""
                ...

            def start_execution(self) -> FlextProtocols.Result[Self]:
                """Start command execution."""
                ...

            def update_status(self, status: str) -> Self:
                """Update command status."""
                ...

            def with_args(self, args: Sequence[str]) -> Self:
                """Return a copy with updated arguments."""
                ...

            def with_status(self, status: str) -> Self:
                """Return a copy with updated status."""
                ...

        @runtime_checkable
        class CliSessionProtocol(Protocol):
            """Protocol for CLI session models."""

            @property
            def commands(self) -> Sequence[FlextCliProtocols.Cli.Command]:
                """Get session commands."""
                ...

            @property
            def commands_by_status(
                self,
            ) -> Mapping[str, Sequence[FlextCliProtocols.Cli.Command]]:
                """Get commands grouped by status."""
                ...

            @property
            def commands_executed(self) -> int:
                """Get number of commands executed."""
                ...

            @property
            def created_at(self) -> datetime:
                """Get creation timestamp."""
                ...

            @property
            def end_time(self) -> str | None:
                """Get session end time."""
                ...

            @property
            def internal_duration_seconds(self) -> float:
                """Get internal duration in seconds."""
                ...

            @property
            def last_activity(self) -> str | None:
                """Get last activity timestamp."""
                ...

            @property
            def session_id(self) -> str:
                """Get session ID."""
                ...

            @property
            def session_summary(self) -> FlextCliProtocols.Cli.SessionData:
                """Get session summary data."""
                ...

            @property
            def start_time(self) -> str | None:
                """Get session start time."""
                ...

            @property
            def status(self) -> str:
                """Get session status."""
                ...

            @property
            def updated_at(self) -> datetime | None:
                """Get update timestamp."""
                ...

            @property
            def user_id(self) -> str:
                """Get user ID."""
                ...

            def add_command(
                self, command: FlextCliProtocols.Cli.Command
            ) -> FlextProtocols.Result[Self]:
                """Add a command to the session."""
                ...

        @runtime_checkable
        class SessionData(Protocol):
            """Protocol for CLI session summary data."""

            @property
            def commands_count(self) -> int:
                """Get number of commands."""
                ...

            @property
            def session_id(self) -> str:
                """Get session ID."""
                ...

            @property
            def status(self) -> str:
                """Get session status."""
                ...

        @runtime_checkable
        class DebugData(Protocol):
            """Protocol for CLI debug summary data."""

            @property
            def level(self) -> str:
                """Get debug level."""
                ...

            @property
            def message(self) -> str:
                """Get debug message."""
                ...

            @property
            def service(self) -> str:
                """Get service name."""
                ...

        @runtime_checkable
        class CliLoggingDataProtocol(Protocol):
            """Protocol for CLI logging summary data matching m.Cli.CliLoggingData."""

            @property
            def console_enabled(self) -> bool:
                """Check if console logging is enabled."""
                ...

            @property
            def level(self) -> str:
                """Get logging level."""
                ...

        @runtime_checkable
        class CliParameterSpecProtocol(Protocol):
            """Protocol for CLI parameter specification matching m.Cli.CliParameterSpec."""

            @property
            def click_type(self) -> str:
                """Get Click type name."""
                ...

            @property
            def default(self) -> object | None:
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
        class OptionConfigProtocol(Protocol):
            """Protocol for CLI option configuration matching m.Cli.OptionConfig."""

            @property
            def count(self) -> bool:
                """Check if option is a counter."""
                ...

            @property
            def default(self) -> object | None:
                """Get default value."""
                ...

            @property
            def flag_value(self) -> object | None:
                """Get flag value."""
                ...

            @property
            def help_text(self) -> str | None:
                """Get help text."""
                ...

            @property
            def is_flag(self) -> bool:
                """Check if option is a flag."""
                ...

            @property
            def multiple(self) -> bool:
                """Check if multiple values are allowed."""
                ...

            @property
            def required(self) -> bool:
                """Check if option is required."""
                ...

            @property
            def show_default(self) -> bool:
                """Check if default value should be shown."""
                ...

            @property
            def type_hint(self) -> object | None:
                """Get type hint."""
                ...

        @runtime_checkable
        class ConfirmConfigProtocol(Protocol):
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
        class PromptConfigProtocol(Protocol):
            """Protocol for CLI prompt configuration."""

            @property
            def confirmation_prompt(self) -> bool:
                """Check if confirmation prompt is enabled."""
                ...

            @property
            def default(self) -> object | None:
                """Get default value."""
                ...

            @property
            def err(self) -> bool:
                """Check if output should go to stderr."""
                ...

            @property
            def hide_input(self) -> bool:
                """Check if input should be hidden."""
                ...

            @property
            def prompt_suffix(self) -> str:
                """Get prompt suffix."""
                ...

            @property
            def show_choices(self) -> bool:
                """Check if choices should be shown."""
                ...

            @property
            def show_default(self) -> bool:
                """Check if default value should be shown."""
                ...

            @property
            def type_hint(self) -> object | None:
                """Get type hint."""
                ...

            @property
            def value_proc(self) -> Callable[[str], object] | None:
                """Get value processor."""
                ...

        @runtime_checkable
        class TableConfigProtocol(Protocol):
            """Protocol for CLI table configuration."""

            @property
            def headers(self) -> Sequence[str]:
                """Get table headers."""
                ...

            @property
            def show_header(self) -> bool:
                """Check if header should be shown."""
                ...

        @runtime_checkable
        class CliParamsConfigProtocol(Protocol):
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
            def params(self) -> Mapping[str, object]:
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

        @runtime_checkable
        class SystemInfoProtocol(Protocol):
            """Protocol for system information models."""

            @property
            def architecture(self) -> Sequence[str]:
                """Get architecture information."""
                ...

            @property
            def hostname(self) -> str:
                """Get hostname."""
                ...

            @property
            def platform(self) -> str:
                """Get platform name."""
                ...

            @property
            def processor(self) -> str:
                """Get processor information."""
                ...

            @property
            def python_version(self) -> str:
                """Get Python version."""
                ...

        @runtime_checkable
        class EnvironmentInfoProtocol(Protocol):
            """Protocol for environment information models."""

            @property
            def env_vars(self) -> Mapping[str, str]:
                """Get environment variables."""
                ...

        @runtime_checkable
        class PathInfoProtocol(Protocol):
            """Protocol for path information models."""

            @property
            def paths(self) -> Sequence[str]:
                """Get system paths."""
                ...

        @runtime_checkable
        class CliFormatter(Protocol):
            """Protocol for CLI formatters."""

            def format_data(
                self, data: object, **options: t.Scalar
            ) -> FlextProtocols.Result[str]:
                """Format data."""
                ...

        @runtime_checkable
        class CliConfigProvider(Protocol):
            """Protocol for CLI configuration providers."""

            def load_config(self) -> FlextProtocols.Result[Mapping[str, object]]:
                """Load configuration."""
                ...

            def save_config(
                self, config: Mapping[str, object]
            ) -> FlextProtocols.Result[bool]:
                """Save configuration."""
                ...

        @runtime_checkable
        class CliAuthenticator(Protocol):
            """Protocol for CLI authentication."""

            def authenticate(
                self, username: str, password: str
            ) -> FlextProtocols.Result[str]:
                """Authenticate user."""
                ...

            def validate_token(self, token: str) -> FlextProtocols.Result[bool]:
                """Validate token."""
                ...

        @runtime_checkable
        class CliDebugProvider(Protocol):
            """Protocol for CLI debug providers."""

            def get_debug_info(
                self,
            ) -> FlextProtocols.Result[Mapping[str, object]]:
                """Get debug information."""
                ...

        type CliRegisteredCommand = FlextCliProtocols.Cli.Command

        @runtime_checkable
        class CliCommandFunction(Protocol):
            """Protocol for CLI command functions that may return None."""

            def __call__(self, *args: object, **kwargs: t.Scalar) -> object | None:
                """Execute the function."""
                ...

        @runtime_checkable
        class CliCommandWrapper(Protocol):
            """Protocol for dynamically-created CLI command wrapper functions."""

            def __call__(self, *args: object, **kwargs: t.Scalar) -> object:
                """Execute the wrapper."""
                ...

        @runtime_checkable
        class CommandHandlerCallable(Protocol):
            """Protocol for command handlers returning r."""

            def __call__(
                self, *args: object, **kwargs: t.Scalar
            ) -> FlextProtocols.Result[object]:
                """Execute the handler."""
                ...

        @runtime_checkable
        class ModelCommandHandler(Protocol):
            """Protocol for model command handlers."""

            def handle(
                self, model: object, **kwargs: t.Scalar
            ) -> FlextProtocols.Result[object]:
                """Handle the model command."""
                ...

        @runtime_checkable
        class CliContextProtocol(Protocol):
            """Protocol for CLI execution context."""

            @property
            def args(self) -> Sequence[str]:
                """Get command arguments."""
                ...

            @property
            def cwd(self) -> str:
                """Get current working directory."""
                ...

            @property
            def env(self) -> Mapping[str, str]:
                """Get environment variables."""
                ...

            params: Mapping[str, object]

        @runtime_checkable
        class CliOutputProtocol(Protocol):
            """Protocol for CLI output handling."""

            def write(self, text: str) -> None:
                """Write text to output."""
                ...

            def write_error(self, text: str) -> None:
                """Write error text."""
                ...

            def write_success(self, text: str) -> None:
                """Write success text."""
                ...

        @runtime_checkable
        class CliPlugin(Protocol):
            """Protocol for CLI plugins."""

            @property
            def name(self) -> str:
                """Get plugin name."""
                ...

            def initialize(self) -> FlextProtocols.Result[bool]:
                """Initialize the plugin."""
                ...

            def shutdown(self) -> FlextProtocols.Result[bool]:
                """Shutdown the plugin."""
                ...

        @runtime_checkable
        class CliServiceProtocol(Protocol):
            """Protocol for CLI services."""

            def initialize(
                self, context: FlextCliProtocols.Cli.CliContextProtocol
            ) -> FlextProtocols.Result[bool]:
                """Initialize the service."""
                ...

            def is_healthy(self) -> bool:
                """Check service health."""
                ...

            def shutdown(self) -> FlextProtocols.Result[bool]:
                """Shutdown the service."""
                ...

        @runtime_checkable
        class CommandServiceProtocol(Protocol):
            """Protocol for command processing services."""

            def get_command(
                self, name: str
            ) -> FlextProtocols.Result[FlextCliProtocols.Cli.Command]:
                """Get a command by name."""
                ...

            def list_commands(
                self,
            ) -> FlextProtocols.Result[Sequence[FlextCliProtocols.Cli.Command]]:
                """List all commands."""
                ...

            def register_command(
                self, command: FlextCliProtocols.Cli.Command
            ) -> FlextProtocols.Result[bool]:
                """Register a command."""
                ...

        @runtime_checkable
        class OutputServiceProtocol(Protocol):
            """Protocol for output formatting services."""

            def format_json(self, data: object) -> FlextProtocols.Result[str]:
                """Format data as JSON."""
                ...

            def format_table(
                self, headers: Sequence[str], rows: Sequence[Sequence[str]]
            ) -> FlextProtocols.Result[str]:
                """Format data as a table."""
                ...

            def format_yaml(self, data: object) -> FlextProtocols.Result[str]:
                """Format data as YAML."""
                ...

        @runtime_checkable
        class CliHandlerProtocol(Protocol):
            """Protocol for CLI request handlers."""

            def can_handle(self, args: Sequence[str]) -> bool:
                """Check if handler can process arguments."""
                ...

            def handle(
                self,
                args: Sequence[str],
                context: FlextCliProtocols.Cli.CliContextProtocol,
                output: FlextCliProtocols.Cli.CliOutputProtocol,
            ) -> FlextProtocols.Result[int]:
                """Handle the CLI request."""
                ...

        @runtime_checkable
        class ErrorHandlerProtocol(Protocol):
            """Protocol for error handling."""

            def get_exit_code(self, error: Exception) -> int:
                """Get exit code for exception."""
                ...

            def handle_error(self, error: Exception) -> FlextProtocols.Result[str]:
                """Handle an exception."""
                ...

        @runtime_checkable
        class CliCommandHandler(Protocol):
            """Protocol for CLI command handlers."""

            def __call__(self, **kwargs: t.Scalar) -> object:
                """Execute the command handler."""
                ...

        @runtime_checkable
        class TableStyleProtocol(Protocol):
            """Protocol for table style configuration."""

            @property
            def show_header(self) -> bool | None:
                """Check if header should be shown."""
                ...

            @property
            def show_lines(self) -> bool | None:
                """Check if lines should be shown."""
                ...

            @property
            def style(self) -> str | None:
                """Get table style."""
                ...

        @runtime_checkable
        class MiddlewareProtocol(Protocol):
            """Middleware protocol for CLI commands."""

            def __call__(
                self,
                ctx: FlextCliProtocols.Cli.CliContextProtocol,
                next_: Callable[
                    [FlextCliProtocols.Cli.CliContextProtocol],
                    FlextProtocols.Result[object],
                ],
            ) -> FlextProtocols.Result[object]:
                """Process and pass to next middleware."""
                ...

        @runtime_checkable
        class CliAppProtocol(Protocol):
            """Protocol for CLI application base classes.

            Structural interface extracted from FlextCliAppBase ABC.
            Subclasses must implement _register_commands.
            """

            def execute_cli(
                self, args: list[str] | None = None
            ) -> FlextProtocols.Result[bool]:
                """Execute the CLI with Railway-pattern error handling."""
                ...

            def _register_commands(self) -> None:
                """Register CLI commands - implement in subclass."""
                ...


p = FlextCliProtocols
__all__ = ["FlextCliProtocols", "p"]
