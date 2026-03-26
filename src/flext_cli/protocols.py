"""FlextCli protocol definitions module - Structural typing."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols

from flext_cli import t


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


__all__ = ["FlextCliProtocols", "p"]

p = FlextCliProtocols
