"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from flext_cli._typings.base import FlextCliTypesBase as cli_t
from flext_core import t
from flext_core.result import FlextResult as r


class FlextCliProtocolsBase:
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
    class CliCommandWrapper(Protocol):
        """Protocol for dynamically-created CLI command wrapper functions."""

        def __call__(
            self,
            *args: t.JsonValue,
            **kwargs: t.JsonValue,
        ) -> t.JsonValue:
            """Execute the wrapper."""
            ...

    @runtime_checkable
    class ResultCommandHandler[TParams: BaseModel, TResult: t.ValueOrModel](Protocol):
        """Protocol for model-driven CLI handlers returning `r[...]`."""

        def __call__(self, params: TParams, /) -> r[TResult]:
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

    @runtime_checkable
    class YamlModule(Protocol):
        """Protocol for YAML serialization module interface."""

        def dump(
            self,
            data: cli_t.YamlDumpable,
            *,
            default_flow_style: bool = True,
        ) -> str:
            """Dump data as YAML string."""
            ...


__all__ = ["FlextCliProtocolsBase"]
