"""Higher-level CLI structural contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from pydantic import BaseModel

from flext_cli import FlextCliProtocolsBase

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliProtocolsDomain:
    """CLI domain protocols layered on top of base callable contracts."""

    @runtime_checkable
    class DisplayData(Protocol):
        """Display payload contract backed by a data mapping."""

        @property
        def data(self) -> t.ContainerMapping:
            """Expose the display payload."""
            ...

    @runtime_checkable
    class LoadedConfig(Protocol):
        """Loaded configuration payload contract."""

        @property
        def content(self) -> t.ContainerMapping:
            """Expose loaded configuration content."""
            ...

    @runtime_checkable
    class JsonValueProcessor(Protocol):
        """Protocol for JSON-compatible value processors."""

        def __call__(self, value: t.Cli.JsonValue) -> t.Cli.JsonValue:
            """Transform one JSON-compatible value."""
            ...

    @runtime_checkable
    class ModelCommandHandler[TParams: BaseModel](Protocol):
        """Protocol for model-driven CLI command execution."""

        def __call__(self, params: TParams, /) -> None:
            """Execute one model-backed CLI command."""
            ...

    @runtime_checkable
    class CommandEntry(Protocol):
        """Protocol for command registry entries."""

        name: str
        handler: t.Cli.JsonCommandFn

    @runtime_checkable
    class ResultCommandRoute(Protocol):
        """Protocol for declarative result-route registration."""

        @property
        def name(self) -> str:
            """Return the command name."""
            ...

        @property
        def help_text(self) -> str:
            """Return the user-facing help text."""
            ...

        @property
        def model_cls(self) -> type[BaseModel]:
            """Return the input model class."""
            ...

        @property
        def handler(self) -> t.Cli.CliCommand:
            """Return the route handler."""
            ...

        @property
        def failure_message(self) -> str:
            """Return the fallback failure message."""
            ...

        @property
        def success_message(self) -> str | None:
            """Return the static success message."""
            ...

        @property
        def success_formatter(
            self,
        ) -> FlextCliProtocolsBase.SuccessMessageFormatter[t.Cli.ValueOrModel] | None:
            """Return the dynamic success formatter."""
            ...

        @property
        def success_type(self) -> str:
            """Return the success message style."""
            ...


__all__ = ["FlextCliProtocolsDomain"]
