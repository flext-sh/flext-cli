"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import m, p

if TYPE_CHECKING:
    from flext_cli import m, t


class FlextCliProtocolsBase:
    """CLI protocol namespace for all CLI-specific protocols."""

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
            cwd: t.Cli.PathLike | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
        ) -> p.Result[m.Cli.CommandOutput]:
            """Execute a command and require zero exit status."""
            ...

        def capture(
            self,
            cmd: t.StrSequence,
            cwd: t.Cli.PathLike | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
        ) -> p.Result[str]:
            """Execute a command and return stripped stdout."""
            ...

        def run_raw(
            self,
            cmd: t.StrSequence,
            cwd: t.Cli.PathLike | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
            input_data: bytes | None = None,
        ) -> p.Result[m.Cli.CommandOutput]:
            """Execute a command without enforcing zero exit status."""
            ...

        def run_checked(
            self,
            cmd: t.StrSequence,
            cwd: t.Cli.PathLike | None = None,
            timeout: int | None = None,
            env: t.StrMapping | None = None,
        ) -> p.Result[bool]:
            """Execute a command and return a success flag."""
            ...

        def run_to_file(
            self,
            cmd: t.StrSequence,
            output_file: t.Cli.PathLike,
            cwd: t.Cli.PathLike | None = None,
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
        def params(self) -> t.Cli.JsonMapping:
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
    class CliCommandWrapper(Protocol):
        """Protocol for dynamically-created CLI command wrapper functions."""

        def __call__(
            self,
            *args: t.Container,
            **kwargs: t.Container,
        ) -> t.Cli.JsonValue:
            """Execute the wrapper."""
            ...

    @runtime_checkable
    class ResultCommandHandler[TParams: m.BaseModel, TResult: t.Cli.ResultValue](
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
    class ErrorMessageProvider(Protocol):
        """Protocol for deferred CLI error message resolution."""

        def __call__(self) -> str | None:
            """Return the current normalized error message, if any."""
            ...

    @runtime_checkable
    class FailureMessageRecorder(Protocol):
        """Protocol for persisting normalized CLI failure state."""

        def __call__(self, error: str | None, fallback: str) -> None:
            """Remember a CLI failure using the original and fallback messages."""
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
            data: t.Cli.YamlDumpable,
            *,
            default_flow_style: bool = True,
        ) -> str:
            """Dump data as YAML string."""
            ...


__all__: list[str] = ["FlextCliProtocolsBase"]
