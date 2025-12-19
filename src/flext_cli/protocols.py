"""FlextCli protocol definitions module - Structural typing."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from typing import Protocol, Self, runtime_checkable

from flext_core import FlextProtocols

from flext_cli.typings import t


class FlextCliProtocols(FlextProtocols):
    """CLI protocol definitions extending FlextProtocols."""

    class Cli:
        """CLI protocol namespace for all CLI-specific protocols."""

        # ═══════════════════════════════════════════════════════════════════
        # LAYER 0: Domain Protocols (sem dependências internas)
        # ═══════════════════════════════════════════════════════════════════

        class Display:
            """Rich display abstraction protocols - NO IMPORTS of Rich classes."""

            @runtime_checkable
            class RichTableProtocol(Protocol):
                """Protocol for Rich Table objects."""

                def add_column(self, header: str, **kwargs: t.GeneralValueType) -> None:
                    """Add table column."""
                    ...

                def add_row(self, *cells: str, **kwargs: t.GeneralValueType) -> None:
                    """Add table row."""
                    ...

            @runtime_checkable
            class RichTreeProtocol(Protocol):
                """Protocol for Rich Tree objects."""

                def add(self, label: str, **kwargs: t.GeneralValueType) -> Self:
                    """Add tree node."""
                    ...

            @runtime_checkable
            class RichConsoleProtocol(Protocol):
                """Protocol for Rich Console objects."""

                def print(
                    self,
                    text: str,
                    style: str | None = None,
                    **kwargs: t.GeneralValueType,
                ) -> None:
                    """Print to console."""
                    ...

        class Interactive:
            """Interactive display abstraction protocols."""

            @runtime_checkable
            class RichProgressProtocol(Protocol):
                """Protocol for Rich Progress objects."""

                def __enter__(
                    self,
                ) -> Self:
                    """Context manager enter."""
                    ...

                def __exit__(self, *args: object) -> None:
                    """Context manager exit."""
                    ...

        @runtime_checkable
        class Command(Protocol):
            """Protocol for CLI commands."""

            @property
            def name(self) -> str:
                """Command name."""
                ...

            @property
            def description(self) -> str:
                """Command description."""
                ...

            @property
            def command_line(self) -> str:
                """Full command line."""
                ...

            @property
            def usage(self) -> str:
                """Command usage information."""
                ...

            @property
            def entry_point(self) -> str:
                """Command entry point."""
                ...

            @property
            def plugin_version(self) -> str:
                """Plugin version."""
                ...

            @property
            def args(self) -> Sequence[str]:
                """Command arguments."""
                ...

            @property
            def status(self) -> str:
                """Command execution status."""
                ...

            @property
            def exit_code(self) -> int | None:
                """Command exit code."""
                ...

            @property
            def output(self) -> str:
                """Command output."""
                ...

            @property
            def error_output(self) -> str:
                """Command error output."""
                ...

            @property
            def execution_time(self) -> float | None:
                """Command execution time."""
                ...

            @property
            def result(self) -> t.GeneralValueType | None:
                """Command result."""
                ...

            @property
            def kwargs(self) -> Mapping[str, t.GeneralValueType]:
                """Command keyword arguments."""
                ...

            @property
            def created_at(self) -> datetime:
                """Creation timestamp."""
                ...

            @property
            def updated_at(self) -> datetime | None:
                """Last update timestamp."""
                ...

            def execute(
                self,
                args: Sequence[str],
            ) -> FlextProtocols.Result[t.GeneralValueType]:
                """Execute command with arguments."""
                ...

            def with_status(self, status: str) -> Self:
                """Return copy with new status."""
                ...

            def with_args(self, args: Sequence[str]) -> Self:
                """Return copy with new arguments."""
                ...

            @property
            def command_summary(self) -> Mapping[str, str]:
                """Return command summary as dict."""
                ...

            def start_execution(self) -> FlextProtocols.Result[Self]:
                """Start command execution - update status to running."""
                ...

            def complete_execution(self, exit_code: int) -> FlextProtocols.Result[Self]:
                """Complete command execution with exit code."""
                ...

            def update_status(self, status: str) -> Self:
                """Update command status."""
                ...

        @runtime_checkable
        class CliSessionProtocol(Protocol):
            """Protocol for CLI session models."""

            @property
            def session_id(self) -> str:
                """Session identifier."""
                ...

            @property
            def user_id(self) -> str:
                """User identifier."""
                ...

            @property
            def status(self) -> str:
                """Session status."""
                ...

            @property
            def commands(self) -> Sequence[FlextCliProtocols.Cli.Command]:
                """Commands in session."""
                ...

            @property
            def start_time(self) -> str | None:
                """Session start time."""
                ...

            @property
            def end_time(self) -> str | None:
                """Session end time."""
                ...

            @property
            def last_activity(self) -> str | None:
                """Last activity timestamp."""
                ...

            @property
            def internal_duration_seconds(self) -> float:
                """Internal duration in seconds."""
                ...

            @property
            def commands_executed(self) -> int:
                """Number of commands executed."""
                ...

            @property
            def created_at(self) -> datetime:
                """Session creation timestamp."""
                ...

            @property
            def updated_at(self) -> datetime | None:
                """Session last update timestamp."""
                ...

            @property
            def session_summary(self) -> FlextCliProtocols.Cli.SessionData:
                """Return session summary as CliSessionData model."""
                ...

            @property
            def commands_by_status(
                self,
            ) -> Mapping[str, Sequence[FlextCliProtocols.Cli.Command]]:
                """Group commands by status."""
                ...

            def add_command(
                self, command: FlextCliProtocols.Cli.Command
            ) -> FlextProtocols.Result[Self]:
                """Add command to session."""
                ...

        @runtime_checkable
        class SessionData(Protocol):
            """Protocol for CLI session summary data."""

            @property
            def session_id(self) -> str:
                """Session identifier."""
                ...

            @property
            def status(self) -> str:
                """Session status."""
                ...

            @property
            def commands_count(self) -> int:
                """Number of commands."""
                ...

        @runtime_checkable
        class DebugData(Protocol):
            """Protocol for CLI debug summary data."""

            @property
            def service(self) -> str:
                """Service name."""
                ...

            @property
            def level(self) -> str:
                """Debug level."""
                ...

            @property
            def message(self) -> str:
                """Debug message."""
                ...

        @runtime_checkable
        class CliLoggingDataProtocol(Protocol):
            """Protocol for CLI logging summary data.

            Complete protocol matching m.Cli.CliLoggingData structure.
            """

            @property
            def level(self) -> str:
                """Log level."""
                ...

            @property
            def console_enabled(self) -> bool:
                """Console output enabled."""
                ...

        @runtime_checkable
        class CliParameterSpecProtocol(Protocol):
            """Protocol for CLI parameter specification.

            Complete protocol matching m.Cli.CliParameterSpec structure.
            """

            @property
            def field_name(self) -> str:
                """Field name."""
                ...

            @property
            def name(self) -> str:
                """Alias for field_name for compatibility."""
                ...

            @property
            def param_type(self) -> type:
                """Parameter type."""
                ...

            @property
            def click_type(self) -> str:
                """Click type."""
                ...

            @property
            def default(self) -> t.GeneralValueType | None:
                """Default value."""
                ...

            @property
            def help(self) -> str:
                """Help text."""
                ...

        @runtime_checkable
        class OptionConfigProtocol(Protocol):
            """Protocol for CLI option configuration.

            Complete protocol matching m.Cli.OptionConfig structure.
            """

            @property
            def help_text(self) -> str | None:
                """Help text for option."""
                ...

            @property
            def default(self) -> t.GeneralValueType | None:
                """Default value."""
                ...

            @property
            def type_hint(self) -> t.GeneralValueType | None:
                """Parameter type (Click type or Python type)."""
                ...

            @property
            def required(self) -> bool:
                """Whether option is required."""
                ...

            @property
            def is_flag(self) -> bool:
                """Whether this is a boolean flag."""
                ...

            @property
            def flag_value(self) -> t.GeneralValueType | None:
                """Value when flag is set."""
                ...

            @property
            def multiple(self) -> bool:
                """Allow multiple values."""
                ...

            @property
            def count(self) -> bool:
                """Count occurrences."""
                ...

            @property
            def show_default(self) -> bool:
                """Show default in help."""
                ...

        @runtime_checkable
        class ConfirmConfigProtocol(Protocol):
            """Protocol for CLI confirmation configuration."""

            @property
            def default(self) -> bool:
                """Default confirmation value."""
                ...

            @property
            def abort(self) -> bool:
                """Whether to abort on negative confirmation."""
                ...

            @property
            def prompt_suffix(self) -> str:
                """Suffix after prompt."""
                ...

            @property
            def show_default(self) -> bool:
                """Show default in prompt."""
                ...

            @property
            def err(self) -> bool:
                """Write to stderr."""
                ...

        @runtime_checkable
        class PromptConfigProtocol(Protocol):
            """Protocol for CLI prompt configuration."""

            @property
            def default(self) -> t.GeneralValueType | None:
                """Default prompt value."""
                ...

            @property
            def type_hint(self) -> t.GeneralValueType | None:
                """Value type."""
                ...

            @property
            def value_proc(self) -> Callable[[str], t.GeneralValueType] | None:
                """Value processor function."""
                ...

            @property
            def prompt_suffix(self) -> str:
                """Suffix after prompt."""
                ...

            @property
            def hide_input(self) -> bool:
                """Hide user input."""
                ...

            @property
            def confirmation_prompt(self) -> bool:
                """Ask for confirmation."""
                ...

            @property
            def show_default(self) -> bool:
                """Show default in prompt."""
                ...

            @property
            def err(self) -> bool:
                """Write to stderr."""
                ...

            @property
            def show_choices(self) -> bool:
                """Show available choices."""
                ...

        @runtime_checkable
        class TableConfigProtocol(Protocol):
            """Protocol for CLI table configuration."""

            @property
            def headers(self) -> Sequence[str]:
                """Table headers."""
                ...

            @property
            def show_header(self) -> bool:
                """Whether to show table header."""
                ...

        @runtime_checkable
        class CliParamsConfigProtocol(Protocol):
            """Protocol for CLI parameters configuration."""

            @property
            def verbose(self) -> bool | None:
                """Enable verbose output."""
                ...

            @property
            def quiet(self) -> bool | None:
                """Suppress non-essential output."""
                ...

            @property
            def debug(self) -> bool | None:
                """Enable debug mode."""
                ...

            @property
            def trace(self) -> bool | None:
                """Enable trace logging (requires debug)."""
                ...

            @property
            def log_level(self) -> str | None:
                """Log level (DEBUG, INFO, WARNING, ERROR)."""
                ...

            @property
            def log_format(self) -> str | None:
                """Log format (compact, detailed, full)."""
                ...

            @property
            def output_format(self) -> str | None:
                """Output format (table, json, yaml, csv)."""
                ...

            @property
            def no_color(self) -> bool | None:
                """Disable colored output."""
                ...

            @property
            def params(self) -> Mapping[str, t.GeneralValueType]:
                """Parameters mapping."""
                ...

        @runtime_checkable
        class SystemInfoProtocol(Protocol):
            """Protocol for system information models."""

            @property
            def python_version(self) -> str:
                """Python version."""
                ...

            @property
            def platform(self) -> str:
                """Platform information."""
                ...

            @property
            def architecture(self) -> Sequence[str]:
                """Architecture information."""
                ...

            @property
            def processor(self) -> str:
                """Processor information."""
                ...

            @property
            def hostname(self) -> str:
                """Hostname."""
                ...

        @runtime_checkable
        class EnvironmentInfoProtocol(Protocol):
            """Protocol for environment information models."""

            @property
            def env_vars(self) -> Mapping[str, str]:
                """Environment variables."""
                ...

        @runtime_checkable
        class PathInfoProtocol(Protocol):
            """Protocol for path information models."""

            @property
            def paths(self) -> Sequence[str]:
                """Path information."""
                ...

        @runtime_checkable
        class CliFormatter(Protocol):
            """Protocol for CLI formatters."""

            def format_data(
                self,
                data: t.GeneralValueType,
                **options: t.GeneralValueType,
            ) -> FlextProtocols.Result[str]:
                """Format data."""
                ...

        @runtime_checkable
        class CliConfigProvider(Protocol):
            """Protocol for CLI configuration providers."""

            def load_config(
                self,
            ) -> FlextProtocols.Result[Mapping[str, t.GeneralValueType]]:
                """Load configuration."""
                ...

            def save_config(
                self, config: Mapping[str, t.GeneralValueType]
            ) -> FlextProtocols.Result[bool]:
                """Save configuration."""
                ...

        @runtime_checkable
        class CliAuthenticator(Protocol):
            """Protocol for CLI authentication."""

            def authenticate(
                self, username: str, password: str
            ) -> FlextProtocols.Result[str]:
                """Authenticate user with credentials."""
                ...

            def validate_token(self, token: str) -> FlextProtocols.Result[bool]:
                """Validate authentication token."""
                ...

        @runtime_checkable
        class CliDebugProvider(Protocol):
            """Protocol for CLI debug providers."""

            def get_debug_info(
                self,
            ) -> FlextProtocols.Result[Mapping[str, t.GeneralValueType]]:
                """Get debug information."""
                ...

        # PEP 695 type aliases - direct type references
        # Type for registered commands (decorated functions)
        type CliRegisteredCommand = FlextCliProtocols.Cli.Command
        # Type for CLI command functions (undecorated callables for decorators)
        CliCommandFunction = Callable[..., t.GeneralValueType | None]

        @runtime_checkable
        class ModelCommandHandler(Protocol):
            """Protocol for model command handlers."""

            def handle(
                self,
                model: t.GeneralValueType,
                **kwargs: t.GeneralValueType,
            ) -> FlextProtocols.Result[t.GeneralValueType]:
                """Handle model command."""
                ...

        @runtime_checkable
        class CliContextProtocol(Protocol):
            """Protocol for CLI execution context."""

            @property
            def cwd(self) -> str:
                """Current working directory."""
                ...

            @property
            def env(self) -> Mapping[str, str]:
                """Environment variables."""
                ...

            @property
            def args(self) -> Sequence[str]:
                """Command line arguments."""
                ...

            params: Mapping[str, t.GeneralValueType]
            """Validated command parameters."""

        @runtime_checkable
        class CliOutputProtocol(Protocol):
            """Protocol for CLI output handling."""

            def write(self, text: str) -> None:
                """Write text output."""
                ...

            def write_error(self, text: str) -> None:
                """Write error output."""
                ...

            def write_success(self, text: str) -> None:
                """Write success output."""
                ...

        @runtime_checkable
        class CliPlugin(Protocol):
            """Protocol for CLI plugins."""

            @property
            def name(self) -> str:
                """Plugin name."""
                ...

            def initialize(self) -> FlextProtocols.Result[bool]:
                """Initialize plugin."""
                ...

            def shutdown(self) -> FlextProtocols.Result[bool]:
                """Shutdown plugin."""
                ...

        # ═══════════════════════════════════════════════════════════════════
        # LAYER 1: Service Protocols (can use Layer 0)
        # ═══════════════════════════════════════════════════════════════════

        @runtime_checkable
        class CliServiceProtocol(Protocol):
            """Protocol for CLI services."""

            def initialize(
                self, context: FlextCliProtocols.Cli.CliContextProtocol
            ) -> FlextProtocols.Result[bool]:
                """Initialize service with context."""
                ...

            def shutdown(self) -> FlextProtocols.Result[bool]:
                """Shutdown service."""
                ...

            def is_healthy(self) -> bool:
                """Check service health."""
                ...

        @runtime_checkable
        class CommandServiceProtocol(Protocol):
            """Protocol for command processing services."""

            def register_command(
                self, command: FlextCliProtocols.Cli.Command
            ) -> FlextProtocols.Result[bool]:
                """Register a command."""
                ...

            def get_command(
                self, name: str
            ) -> FlextProtocols.Result[FlextCliProtocols.Cli.Command]:
                """Get command by name."""
                ...

            def list_commands(
                self,
            ) -> FlextProtocols.Result[Sequence[FlextCliProtocols.Cli.Command]]:
                """List all registered commands."""
                ...

        @runtime_checkable
        class OutputServiceProtocol(Protocol):
            """Protocol for output formatting services."""

            def format_table(
                self,
                headers: Sequence[str],
                rows: Sequence[Sequence[str]],
            ) -> FlextProtocols.Result[str]:
                """Format data as table."""
                ...

            def format_json(
                self, data: t.GeneralValueType
            ) -> FlextProtocols.Result[str]:
                """Format data as JSON."""
                ...

            def format_yaml(
                self, data: t.GeneralValueType
            ) -> FlextProtocols.Result[str]:
                """Format data as YAML."""
                ...

        # ═══════════════════════════════════════════════════════════════════
        # LAYER 2: Handler Protocols (can use Layer 0 and 1)
        # ═══════════════════════════════════════════════════════════════════

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
                """Handle CLI request."""
                ...

        @runtime_checkable
        class ErrorHandlerProtocol(Protocol):
            """Protocol for error handling."""

            def handle_error(self, error: Exception) -> FlextProtocols.Result[str]:
                """Handle and format error."""
                ...

            def get_exit_code(self, error: Exception) -> int:
                """Get appropriate exit code for error."""
                ...

        # Simple command handler protocol - callable that returns a GeneralValueType
        # (matches register_command signature: Callable[..., GeneralValueType])
        CliCommandHandler = Callable[..., t.GeneralValueType]

        @runtime_checkable
        class TableStyleProtocol(Protocol):
            """Protocol for table style configuration."""

            @property
            def style(self) -> str | None:
                """Table style."""
                ...

            @property
            def show_header(self) -> bool | None:
                """Show table header."""
                ...

            @property
            def show_lines(self) -> bool | None:
                """Show table lines."""
                ...

    # ═══════════════════════════════════════════════════════════════════════
    # TOP-LEVEL ALIASES for backward compatibility
    # ═══════════════════════════════════════════════════════════════════════

    # These aliases allow access like FlextCliProtocols.CliPlugin instead of
    # FlextCliProtocols.Cli.CliPlugin
    CliPlugin = Cli.CliPlugin
    CliCommandHandler = Cli.CliCommandHandler
    Command = Cli.Command


# Direct access: use FlextCliProtocols directly
p = FlextCliProtocols


__all__ = [
    "FlextCliProtocols",
    "p",
]


# Short alias for namespace access
fcli = FlextCliProtocols
