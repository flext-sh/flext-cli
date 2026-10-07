"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli._protocols import FlextCliProtocolsBasePart03
from flext_core import p

if TYPE_CHECKING:
    # Why (multi-agent): defer flext_cli import to break the __init__-time
    # circular import; t is annotation-only (PEP 563). Matches sibling part_03.
    from flext_cli import m, t


class FlextCliProtocolsBasePart04(FlextCliProtocolsBasePart03):
    """Implementation part for FlextCliProtocolsBasePart04."""

    @runtime_checkable
    class ParsedOptionTokens(Protocol):
        """A parse-only option route without executing a command callback."""

        @property
        def values(self) -> t.JsonMapping:
            """Canonical field names and parsed scalar values."""
            ...

        @property
        def remaining(self) -> t.StrSequence:
            """Unconsumed tokens after the first positional argument."""
            ...

        @property
        def help_requested(self) -> bool:
            """Whether a standalone help option was parsed."""
            ...

    @runtime_checkable
    class ModelOptionParser(Protocol):
        """Parse model-backed option tokens without running a CLI command."""

        def parse_model_options(
            self,
            model_cls: t.ModelClass[t.Cli.ModelLike],
            arguments: t.StrSequence,
            *,
            field_names: t.StrSequence | None = None,
            stop_at_positional: bool = False,
        ) -> FlextCliProtocolsBasePart04.ParsedOptionTokens:
            """Read command routing facts from canonical option declarations."""
            ...

    @runtime_checkable
    class CliOptionSpec(Protocol):
        """Framework-neutral option model contract returned by the CLI DSL."""

        @property
        def declarations(self) -> t.StrSequence:
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
    class CmdService(Protocol):
        """Protocol for the public command/settings service surface on ``cli``."""

        def execute(self) -> p.Result[m.Cli.RuntimeStatus]:
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
