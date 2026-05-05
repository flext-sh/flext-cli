"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import EllipsisType
from typing import TYPE_CHECKING, Protocol, Self, runtime_checkable

from flext_core import p

if TYPE_CHECKING:
    from flext_cli import c, m, t


class FlextCliProtocolsBase:
    """CLI protocol namespace for all CLI-specific protocols."""

    @runtime_checkable
    class Settings(Protocol):
        """Protocol for CLI runtime settings consumed by the public services."""

        @property
        def app_name(self) -> str:
            """Application name."""
            ...

        @property
        def cli_log_level(self) -> c.LogLevel:
            """Get CLI log level."""
            ...

        @property
        def debug(self) -> bool:
            """Check if debug mode is enabled."""
            ...

        @property
        def log_verbosity(self) -> str:
            """Get log verbosity mode."""
            ...

        @property
        def no_color(self) -> bool:
            """Check if color output is disabled."""
            ...

        @property
        def output_format(self) -> str:
            """Get configured output format."""
            ...

        @property
        def quiet(self) -> bool:
            """Check if quiet mode is enabled."""
            ...

        token_file: str | None
        """Mutable path to the configured authentication token file."""

        @property
        def trace(self) -> bool:
            """Check if trace mode is enabled."""
            ...

        @property
        def verbose(self) -> bool:
            """Check if verbose mode is enabled."""
            ...

        def model_dump(self) -> t.JsonMapping:
            """Dump the settings model into a JSON-compatible mapping."""
            ...

        def clone(self, **overrides: t.JsonPayload | None) -> Self:
            """Return a cloned settings instance with overrides applied."""
            ...

        def apply_override(
            self,
            key: str,
            value: t.Scalar | t.ScalarList | t.ScalarMapping,
        ) -> bool:
            """Apply one runtime override to the live settings object."""
            ...

    @runtime_checkable
    class CommandOutput(Protocol):
        """Minimal external command execution output contract."""

        @property
        def duration(self) -> float:
            """Return the command duration in seconds."""
            ...

        @property
        def exit_code(self) -> int:
            """Return the command exit code."""
            ...

        @property
        def stderr(self) -> str:
            """Return the command standard error."""
            ...

        @property
        def stdout(self) -> str:
            """Return the command standard output."""
            ...

    @runtime_checkable
    class CommandRunner(Protocol):
        """Contract for generic command execution services."""

        def run(
            self,
            cmd: t.StrSequence,
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
        ) -> p.Result[m.Cli.CommandOutput]:
            """Execute a command and require zero exit status."""
            ...

        def capture(
            self,
            cmd: t.StrSequence,
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
        ) -> p.Result[str]:
            """Execute a command and return stripped stdout."""
            ...

        def run_raw(
            self,
            cmd: t.StrSequence,
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
            input_data: bytes | None = None,
        ) -> p.Result[m.Cli.CommandOutput]:
            """Execute a command without enforcing zero exit status."""
            ...

        def run_checked(
            self,
            cmd: t.StrSequence,
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
        ) -> p.Result[bool]:
            """Execute a command and return a success flag."""
            ...

        def run_to_file(
            self,
            cmd: t.StrSequence,
            output_file: t.Cli.TextPath,
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
        ) -> p.Result[int]:
            """Execute a command and write combined output to a file."""
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
        def params(self) -> t.JsonMapping:
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
    class CliOptionSpec(Protocol):
        """Protocol for Typer option objects returned by the public CLI DSL."""

        @property
        def default(self) -> t.JsonPayload | EllipsisType | None:
            """Get the normalized default value for the option."""
            ...

        @property
        def param_decls(self) -> t.StrSequence | None:
            """Get the declared CLI flag names for the option."""
            ...

    @runtime_checkable
    class CommandRegistry(Protocol):
        """Protocol for the lightweight CLI command registry service."""

        @property
        def name(self) -> str:
            """Get the registry name."""
            ...

        def execute(self) -> p.Result[t.JsonMapping]:
            """Return the public service status payload."""
            ...

        def execute_command(
            self,
            name: str,
            args: t.StrSequence | None = None,
            **kwargs: t.Scalar,
        ) -> p.Result[t.JsonValue]:
            """Execute one registered command."""
            ...

        def list_commands(self) -> p.Result[t.StrSequence]:
            """Return the registered command names."""
            ...

        def register_handler(
            self,
            name: str,
            handler: t.Cli.JsonCommandFn,
        ) -> p.Result[bool]:
            """Register one command handler."""
            ...

        def run_cli(self, args: t.StrSequence | None = None) -> p.Result[t.JsonValue]:
            """Execute the registry through the public CLI runner surface."""
            ...

    @runtime_checkable
    class CmdService(Protocol):
        """Protocol for the public command/settings service surface on ``cli``."""

        def execute(self) -> p.Result[t.JsonMapping]:
            """Return the public operational status payload."""
            ...

        def show_settings(self) -> p.Result[bool]:
            """Display the current settings through the public command surface."""
            ...

        def validate_settings(self) -> p.Result[bool]:
            """Validate the current settings through the public command surface."""
            ...

    @runtime_checkable
    class AuthService(Protocol):
        """Protocol for the public authentication service surface on ``cli``."""

        def validate_credentials(self, username: str, password: str) -> p.Result[bool]:
            """Validate direct username/password credentials."""
            ...

        def save_auth_token(self, token: str) -> p.Result[bool]:
            """Persist an authentication token."""
            ...

        def fetch_auth_token(self) -> p.Result[str]:
            """Load the persisted authentication token."""
            ...

        def authenticate(self, credentials: t.StrMapping) -> p.Result[str]:
            """Authenticate with a token or username/password."""
            ...

        def clear_auth_tokens(self) -> p.Result[bool]:
            """Delete persisted authentication tokens."""
            ...

    @runtime_checkable
    class CliCommandWrapper(Protocol):
        """Protocol for dynamically-created CLI command wrapper functions."""

        def __call__(
            self,
            *args: t.JsonPayload,
            **kwargs: t.JsonPayload,
        ) -> t.JsonPayload:
            """Execute the wrapper."""
            ...

    @runtime_checkable
    class ResultCommandHandler[TParams: t.Cli.ModelLike, TResult: t.Cli.ResultValue](
        Protocol
    ):
        """Protocol for model-driven CLI handlers returning `r[...]`."""

        def __call__(self, params: TParams, /) -> p.Result[TResult]:
            """Execute the handler and return a railway result."""
            ...

    @runtime_checkable
    class ErasedCommandResult(Protocol):
        """Type-erased result surface consumed by declarative CLI routes."""

        @property
        def failure(self) -> bool:
            """Indicate whether the command failed."""
            ...

        @property
        def error(self) -> str | None:
            """Expose the normalized failure message, if any."""
            ...

        @property
        def value(self) -> t.Cli.ResultValue:
            """Expose the successful payload for message formatting."""
            ...

    @runtime_checkable
    class SuccessMessageFormatter[TResult: t.Cli.ResultValue](Protocol):
        """Protocol for rendering a success result into a CLI message."""

        def __call__(self, value: TResult) -> str:
            """Return the success message to display."""
            ...

    @runtime_checkable
    class YamlModule(Protocol):
        """Protocol for YAML serialization module interface."""

        def dump(
            self,
            data: t.JsonPayload,
            *,
            default_flow_style: bool = True,
        ) -> str:
            """Dump data as YAML string."""
            ...


__all__: list[str] = ["FlextCliProtocolsBase"]
