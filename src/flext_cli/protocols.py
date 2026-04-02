"""FlextCli protocol definitions module - Structural typing."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from flext_cli import t
from flext_core import FlextProtocols, r


class FlextCliProtocols(FlextProtocols):
    """CLI protocol definitions extending FlextProtocols."""

    class Cli:
        """CLI protocol namespace for all CLI-specific protocols."""

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
        class ResultCommandHandler[TParams: BaseModel, TResult: t.ValueOrModel](
            Protocol
        ):
            """Protocol for model-driven CLI handlers returning `r[...]`."""

            def __call__(self, params: TParams) -> r[TResult]:
                """Execute the handler and return a railway result."""
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
        class SuccessMessageFormatter[TResult: t.ValueOrModel](Protocol):
            """Protocol for rendering a success result into a CLI message."""

            def __call__(self, value: TResult) -> str:
                """Return the success message to display."""
                ...


__all__ = ["FlextCliProtocols", "p"]

p = FlextCliProtocols
