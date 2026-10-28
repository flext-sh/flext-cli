"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from flext_core import p

from flext_cli import t
from flext_cli._protocols._base import FlextCliProtocolsBasePart03


class FlextCliProtocolsBasePart04(FlextCliProtocolsBasePart03):
    """Implementation part for FlextCliProtocolsBasePart04."""

    @runtime_checkable
    class CliOptionSpec(Protocol):
        """Framework-neutral option model contract returned by the CLI DSL."""

        @property
        def declarations(self) -> Sequence[str]:
            """Ordered option flag declarations."""
            ...

        @property
        def help_text(self) -> str:
            """Human-readable option help text."""
            ...

        @property
        def default(self) -> t.Cli.CliValue | None:
            """Normalized default value for the option."""
            ...

        @property
        def required(self) -> bool:
            """Indicate whether the option requires an explicit value."""
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
    class ResultCommandHandler[TParams: t.Cli.ModelLike, TResult](
        Protocol,
    ):
        """Protocol for model-driven CLI handlers returning `r[...]`."""

        def __call__(self, params: TParams, /) -> p.Result[TResult]:
            """Execute the handler and return a railway result."""
            ...

    @runtime_checkable
    class ErasedCommandResult(p.FailureLike, Protocol):
        """Type-erased result surface consumed by declarative CLI routes."""

        @property
        def value(self) -> t.Cli.ResultValue:
            """Expose the successful payload for message formatting."""
            ...

    # mro-j47u (codex): formatter callables have one owner in t.Cli.


__all__: list[str] = ["FlextCliProtocolsBasePart04"]
