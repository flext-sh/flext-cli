"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import EllipsisType
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli._protocols._base_parts.flextcliprotocolsbase_part_03 import (
    FlextCliProtocolsBase as FlextCliProtocolsBasePart03,
)
from flext_core import p

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliProtocolsBase(FlextCliProtocolsBasePart03):
    """Implementation part for FlextCliProtocolsBase."""

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


__all__: list[str] = ["FlextCliProtocolsBase"]
