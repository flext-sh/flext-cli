"""FlextCli protocol definitions module - Structural typing."""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from typing import Protocol, Self, runtime_checkable

from flext_core import FlextProtocols, FlextTypes as t


class FlextCliProtocols(FlextProtocols):
    """CLI protocol definitions extending FlextProtocols."""

    class Cli:
        """CLI protocol namespace for all CLI-specific protocols."""

        class Display:
            """Rich display abstraction protocols - NO IMPORTS of Rich classes."""

            @runtime_checkable
            class RichTableProtocol(Protocol):
                """Protocol for Rich Table objects."""

                def add_column(self, header: str, **kwargs: t.GeneralValueType) -> None: ...
                def add_row(self, *cells: str, **kwargs: t.GeneralValueType) -> None: ...

            @runtime_checkable
            class RichTreeProtocol(Protocol):
                """Protocol for Rich Tree objects."""

                def add(
                    self, label: str, **kwargs: t.GeneralValueType
                ) -> FlextCliProtocols.Cli.Display.RichTreeProtocol: ...

            @runtime_checkable
            class RichConsoleProtocol(Protocol):
                """Protocol for Rich Console objects."""

                def print(
                    self, text: str, style: str | None = None, **kwargs: t.GeneralValueType,
                ) -> None: ...

        class Interactive:
            """Interactive display abstraction protocols."""

            @runtime_checkable
            class RichProgressProtocol(Protocol):
                """Protocol for Rich Progress objects."""

                def __enter__(self) -> Self: ...
                def __exit__(self, *args: object) -> None: ...

        @runtime_checkable
        class Command(Protocol):
            """Protocol for CLI commands."""

            @property
            def name(self) -> str: ...
            @property
            def description(self) -> str: ...
            @property
            def command_line(self) -> str: ...
            @property
            def usage(self) -> str: ...
            @property
            def entry_point(self) -> str: ...
            @property
            def plugin_version(self) -> str: ...
            @property
            def args(self) -> Sequence[str]: ...
            @property
            def status(self) -> str: ...
            @property
            def exit_code(self) -> int | None: ...
            @property
            def output(self) -> str: ...
            @property
            def error_output(self) -> str: ...
            @property
            def execution_time(self) -> float | None: ...
            @property
            def result(self) -> t.GeneralValueType | None: ...
            @property
            def kwargs(self) -> Mapping[str, t.GeneralValueType]: ...
            @property
            def created_at(self) -> datetime: ...
            @property
            def updated_at(self) -> datetime | None: ...

            def execute(
                self, args: Sequence[str],
            ) -> FlextProtocols.Result[t.GeneralValueType]: ...
            def with_status(self, status: str) -> Self: ...
            def with_args(self, args: Sequence[str]) -> Self: ...

            @property
            def command_summary(self) -> Mapping[str, str]: ...

            def start_execution(self) -> FlextProtocols.Result[Self]: ...
            def complete_execution(self, exit_code: int) -> FlextProtocols.Result[Self]: ...
            def update_status(self, status: str) -> Self: ...

        @runtime_checkable
        class CliSessionProtocol(Protocol):
            """Protocol for CLI session models."""

            @property
            def session_id(self) -> str: ...
            @property
            def user_id(self) -> str: ...
            @property
            def status(self) -> str: ...
            @property
            def commands(self) -> Sequence[FlextCliProtocols.Cli.Command]: ...
            @property
            def start_time(self) -> str | None: ...
            @property
            def end_time(self) -> str | None: ...
            @property
            def last_activity(self) -> str | None: ...
            @property
            def internal_duration_seconds(self) -> float: ...
            @property
            def commands_executed(self) -> int: ...
            @property
            def created_at(self) -> datetime: ...
            @property
            def updated_at(self) -> datetime | None: ...
            @property
            def session_summary(self) -> FlextCliProtocols.Cli.SessionData: ...
            @property
            def commands_by_status(
                self,
            ) -> Mapping[str, Sequence[FlextCliProtocols.Cli.Command]]: ...

            def add_command(
                self, command: FlextCliProtocols.Cli.Command,
            ) -> FlextProtocols.Result[Self]: ...

        @runtime_checkable
        class SessionData(Protocol):
            """Protocol for CLI session summary data."""

            @property
            def session_id(self) -> str: ...
            @property
            def status(self) -> str: ...
            @property
            def commands_count(self) -> int: ...

        @runtime_checkable
        class DebugData(Protocol):
            """Protocol for CLI debug summary data."""

            @property
            def service(self) -> str: ...
            @property
            def level(self) -> str: ...
            @property
            def message(self) -> str: ...

        @runtime_checkable
        class CliLoggingDataProtocol(Protocol):
            """Protocol for CLI logging summary data matching m.Cli.CliLoggingData."""

            @property
            def level(self) -> str: ...
            @property
            def console_enabled(self) -> bool: ...

        @runtime_checkable
        class CliParameterSpecProtocol(Protocol):
            """Protocol for CLI parameter specification matching m.Cli.CliParameterSpec."""

            @property
            def field_name(self) -> str: ...
            @property
            def name(self) -> str: ...
            @property
            def param_type(self) -> type: ...
            @property
            def click_type(self) -> str: ...
            @property
            def default(self) -> t.GeneralValueType | None: ...
            @property
            def help(self) -> str: ...

        @runtime_checkable
        class OptionConfigProtocol(Protocol):
            """Protocol for CLI option configuration matching m.Cli.OptionConfig."""

            @property
            def help_text(self) -> str | None: ...
            @property
            def default(self) -> t.GeneralValueType | None: ...
            @property
            def type_hint(self) -> t.GeneralValueType | None: ...
            @property
            def required(self) -> bool: ...
            @property
            def is_flag(self) -> bool: ...
            @property
            def flag_value(self) -> t.GeneralValueType | None: ...
            @property
            def multiple(self) -> bool: ...
            @property
            def count(self) -> bool: ...
            @property
            def show_default(self) -> bool: ...

        @runtime_checkable
        class ConfirmConfigProtocol(Protocol):
            """Protocol for CLI confirmation configuration."""

            @property
            def default(self) -> bool: ...
            @property
            def abort(self) -> bool: ...
            @property
            def prompt_suffix(self) -> str: ...
            @property
            def show_default(self) -> bool: ...
            @property
            def err(self) -> bool: ...

        @runtime_checkable
        class PromptConfigProtocol(Protocol):
            """Protocol for CLI prompt configuration."""

            @property
            def default(self) -> t.GeneralValueType | None: ...
            @property
            def type_hint(self) -> t.GeneralValueType | None: ...
            @property
            def value_proc(self) -> Callable[[str], t.GeneralValueType] | None: ...
            @property
            def prompt_suffix(self) -> str: ...
            @property
            def hide_input(self) -> bool: ...
            @property
            def confirmation_prompt(self) -> bool: ...
            @property
            def show_default(self) -> bool: ...
            @property
            def err(self) -> bool: ...
            @property
            def show_choices(self) -> bool: ...

        @runtime_checkable
        class TableConfigProtocol(Protocol):
            """Protocol for CLI table configuration."""

            @property
            def headers(self) -> Sequence[str]: ...
            @property
            def show_header(self) -> bool: ...

        @runtime_checkable
        class CliParamsConfigProtocol(Protocol):
            """Protocol for CLI parameters configuration."""

            @property
            def verbose(self) -> bool | None: ...
            @property
            def quiet(self) -> bool | None: ...
            @property
            def debug(self) -> bool | None: ...
            @property
            def trace(self) -> bool | None: ...
            @property
            def log_level(self) -> str | None: ...
            @property
            def log_format(self) -> str | None: ...
            @property
            def output_format(self) -> str | None: ...
            @property
            def no_color(self) -> bool | None: ...
            @property
            def params(self) -> Mapping[str, t.GeneralValueType]: ...

        @runtime_checkable
        class SystemInfoProtocol(Protocol):
            """Protocol for system information models."""

            @property
            def python_version(self) -> str: ...
            @property
            def platform(self) -> str: ...
            @property
            def architecture(self) -> Sequence[str]: ...
            @property
            def processor(self) -> str: ...
            @property
            def hostname(self) -> str: ...

        @runtime_checkable
        class EnvironmentInfoProtocol(Protocol):
            """Protocol for environment information models."""

            @property
            def env_vars(self) -> Mapping[str, str]: ...

        @runtime_checkable
        class PathInfoProtocol(Protocol):
            """Protocol for path information models."""

            @property
            def paths(self) -> Sequence[str]: ...

        @runtime_checkable
        class CliFormatter(Protocol):
            """Protocol for CLI formatters."""

            def format_data(
                self, data: t.GeneralValueType, **options: t.GeneralValueType,
            ) -> FlextProtocols.Result[str]: ...

        @runtime_checkable
        class CliConfigProvider(Protocol):
            """Protocol for CLI configuration providers."""

            def load_config(self) -> FlextProtocols.Result[Mapping[str, t.GeneralValueType]]: ...
            def save_config(
                self, config: Mapping[str, t.GeneralValueType],
            ) -> FlextProtocols.Result[bool]: ...

        @runtime_checkable
        class CliAuthenticator(Protocol):
            """Protocol for CLI authentication."""

            def authenticate(
                self, username: str, password: str,
            ) -> FlextProtocols.Result[str]: ...
            def validate_token(self, token: str) -> FlextProtocols.Result[bool]: ...

        @runtime_checkable
        class CliDebugProvider(Protocol):
            """Protocol for CLI debug providers."""

            def get_debug_info(
                self,
            ) -> FlextProtocols.Result[Mapping[str, t.GeneralValueType]]: ...

        type CliRegisteredCommand = FlextCliProtocols.Cli.Command

        @runtime_checkable
        class CliCommandFunction(Protocol):
            """Protocol for CLI command functions that may return None."""

            def __call__(
                self, *args: t.GeneralValueType, **kwargs: t.GeneralValueType,
            ) -> t.GeneralValueType | None: ...

        @runtime_checkable
        class CliCommandWrapper(Protocol):
            """Protocol for dynamically-created CLI command wrapper functions."""

            def __call__(
                self, *args: t.GeneralValueType, **kwargs: t.GeneralValueType,
            ) -> t.GeneralValueType: ...

        @runtime_checkable
        class CommandHandlerCallable(Protocol):
            """Protocol for command handlers returning FlextResult."""

            def __call__(
                self, *args: t.GeneralValueType, **kwargs: t.GeneralValueType,
            ) -> FlextProtocols.Result[t.GeneralValueType]: ...

        @runtime_checkable
        class ModelCommandHandler(Protocol):
            """Protocol for model command handlers."""

            def handle(
                self, model: t.GeneralValueType, **kwargs: t.GeneralValueType,
            ) -> FlextProtocols.Result[t.GeneralValueType]: ...

        @runtime_checkable
        class CliContextProtocol(Protocol):
            """Protocol for CLI execution context."""

            @property
            def cwd(self) -> str: ...
            @property
            def env(self) -> Mapping[str, str]: ...
            @property
            def args(self) -> Sequence[str]: ...
            params: Mapping[str, t.GeneralValueType]

        @runtime_checkable
        class CliOutputProtocol(Protocol):
            """Protocol for CLI output handling."""

            def write(self, text: str) -> None: ...
            def write_error(self, text: str) -> None: ...
            def write_success(self, text: str) -> None: ...

        @runtime_checkable
        class CliPlugin(Protocol):
            """Protocol for CLI plugins."""

            @property
            def name(self) -> str: ...
            def initialize(self) -> FlextProtocols.Result[bool]: ...
            def shutdown(self) -> FlextProtocols.Result[bool]: ...

        @runtime_checkable
        class CliServiceProtocol(Protocol):
            """Protocol for CLI services."""

            def initialize(
                self, context: FlextCliProtocols.Cli.CliContextProtocol,
            ) -> FlextProtocols.Result[bool]: ...
            def shutdown(self) -> FlextProtocols.Result[bool]: ...
            def is_healthy(self) -> bool: ...

        @runtime_checkable
        class CommandServiceProtocol(Protocol):
            """Protocol for command processing services."""

            def register_command(
                self, command: FlextCliProtocols.Cli.Command,
            ) -> FlextProtocols.Result[bool]: ...
            def get_command(
                self, name: str,
            ) -> FlextProtocols.Result[FlextCliProtocols.Cli.Command]: ...
            def list_commands(
                self,
            ) -> FlextProtocols.Result[Sequence[FlextCliProtocols.Cli.Command]]: ...

        @runtime_checkable
        class OutputServiceProtocol(Protocol):
            """Protocol for output formatting services."""

            def format_table(
                self, headers: Sequence[str], rows: Sequence[Sequence[str]],
            ) -> FlextProtocols.Result[str]: ...
            def format_json(self, data: t.GeneralValueType) -> FlextProtocols.Result[str]: ...
            def format_yaml(self, data: t.GeneralValueType) -> FlextProtocols.Result[str]: ...

        @runtime_checkable
        class CliHandlerProtocol(Protocol):
            """Protocol for CLI request handlers."""

            def can_handle(self, args: Sequence[str]) -> bool: ...
            def handle(
                self, args: Sequence[str],
                context: FlextCliProtocols.Cli.CliContextProtocol,
                output: FlextCliProtocols.Cli.CliOutputProtocol,
            ) -> FlextProtocols.Result[int]: ...

        @runtime_checkable
        class ErrorHandlerProtocol(Protocol):
            """Protocol for error handling."""

            def handle_error(self, error: Exception) -> FlextProtocols.Result[str]: ...
            def get_exit_code(self, error: Exception) -> int: ...

        @runtime_checkable
        class CliCommandHandler(Protocol):
            """Protocol for CLI command handlers."""

            def __call__(self, **kwargs: t.GeneralValueType) -> t.GeneralValueType: ...

        @runtime_checkable
        class TableStyleProtocol(Protocol):
            """Protocol for table style configuration."""

            @property
            def style(self) -> str | None: ...
            @property
            def show_header(self) -> bool | None: ...
            @property
            def show_lines(self) -> bool | None: ...

        @runtime_checkable
        class MiddlewareProtocol(Protocol):
            """Middleware protocol for CLI commands.

            Middleware functions process the CLI context and pass control to the next
            middleware or handler in the chain. They can modify the context, log
            execution, validate inputs, retry operations, etc.
            """

            def __call__(
                self,
                ctx: FlextCliProtocols.Cli.CliContextProtocol,
                next_: Callable[
                    [FlextCliProtocols.Cli.CliContextProtocol],
                    FlextProtocols.Result[t.GeneralValueType],
                ],
            ) -> FlextProtocols.Result[t.GeneralValueType]:
                """Process and pass to next middleware.

                Args:
                    ctx: CLI execution context.
                    next_: Next middleware or handler in the chain.

                Returns:
                    Result[t.GeneralValueType]: Result from next middleware or handler.

                """
                ...


p = FlextCliProtocols
__all__ = [
    "FlextCliProtocols",
    "p",
]
