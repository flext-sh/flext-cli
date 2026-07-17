"""FlextCli protocol definitions - Structural typing contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_cli._protocols._base.flextcliprotocolsbase_part_03 import (
    FlextCliProtocolsBase as FlextCliProtocolsBasePart03,
)
from flext_core import p, t


class FlextCliProtocolsBase(FlextCliProtocolsBasePart03):
    """Implementation part for FlextCliProtocolsBase."""

    # mro-wkii.17.26 (codex): public status results are structural p contracts;
    # importing local m/t here re-enters facades that p is still composing.
    @runtime_checkable
    class RuntimeComponents(Protocol):
        """Observable CLI runtime component states."""

        @property
        def settings(self) -> str: ...

        @property
        def formatters(self) -> str: ...

        @property
        def prompts(self) -> str: ...

        @property
        def rules(self) -> str: ...

    @runtime_checkable
    class RuntimeStatus(Protocol):
        """Observable public CLI runtime status."""

        @property
        def status(self) -> str: ...

        @property
        def service(self) -> str: ...

        @property
        def timestamp(self) -> str: ...

        @property
        def version(self) -> str: ...

        @property
        def components(self) -> FlextCliProtocolsBase.RuntimeComponents: ...

    @runtime_checkable
    class OptionSpec(Protocol):
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
        def default(
            self,
        ) -> (
            t.Scalar | t.StrSequence | t.MappingKV[str, t.Scalar | t.StrSequence] | None
        ):
            """Normalized option default value."""
            ...

        @property
        def required(self) -> bool:
            """Indicate whether the option requires an explicit value."""
            ...

    @runtime_checkable
    class CmdService(Protocol):
        """Protocol for the public command/settings service surface on ``cli``."""

        def execute(self) -> p.Result[FlextCliProtocolsBase.RuntimeStatus]:
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
    class CommandWrapper(Protocol):
        """Protocol for dynamically-created CLI command wrapper functions."""

        def __call__(
            self, *args: t.JsonPayload, **kwargs: t.JsonPayload
        ) -> t.JsonPayload:
            """Execute the wrapper."""
            ...

    @runtime_checkable
    class ResultCommandHandler[TParams: t.BaseModel, TResult: t.JsonPayload](Protocol):
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
        def value(self) -> t.JsonPayload:
            """Expose the successful payload for message formatting."""
            ...

    # mro-j47u (codex): formatter callables have one owner in t.Cli.


__all__: tuple[str, ...] = ("FlextCliProtocolsBase",)
