"""Framework-neutral contracts for the CLI backend boundary."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable, TYPE_CHECKING

# mro-j47u (codex): consume the earlier local t facade through the package root.
from flext_cli import t

if TYPE_CHECKING:
    from flext_core import p


class FlextCliProtocolsFramework:
    """Structural contracts implemented by the private CLI framework adapter."""

    @runtime_checkable
    class Application(Protocol):
        """Opaque CLI application owned by the private framework adapter."""

        def callback(
            self,
        ) -> Callable[[Callable[..., t.JsonPayload]], Callable[..., t.JsonPayload]]:
            """Return the application callback decorator."""
            ...

        def command[TCommand: Callable[..., t.JsonPayload]](
            self, name: str | None = None, *, help: str | None = None
        ) -> Callable[[TCommand], TCommand]:
            """Return a named command decorator."""
            ...

        # mro-j47u (codex): match the sole adapter and mandatory named-group API.
        def add_typer(
            self, group: FlextCliProtocolsFramework.Application, *, name: str
        ) -> None:
            """Attach a child application under ``name``."""
            ...

    @runtime_checkable
    class ExternalCommand(Protocol):
        """Executable command contract used by framework integrations."""

        def main(
            self,
            # mro-wkii.17.26 (codex): public integrations accept every canonical
            # immutable sequence; the private adapter normalizes at Click ingress.
            args: t.Cli.ExternalArgs | None = None,
            prog_name: str | None = None,
            complete_var: str | None = None,
            *,
            standalone_mode: bool = True,
            windows_expand_args: bool = True,
            **extra: p.AttributeProbe,
        ) -> p.AttributeProbe:
            """Execute one command."""
            ...

    @runtime_checkable
    class InvocationResult(Protocol):
        """Captured output from one real framework invocation."""

        @property
        def exit_code(self) -> int: ...

        @property
        def stdout(self) -> str: ...

        @property
        def stderr(self) -> str: ...


__all__: list[str] = ["FlextCliProtocolsFramework"]
