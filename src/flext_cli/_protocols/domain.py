"""Higher-level CLI structural contracts."""

from __future__ import annotations

from collections.abc import (
    Mapping,
)
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import FlextCliProtocolsBase
from flext_core import m

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliProtocolsDomain:
    """CLI domain protocols layered on top of base callable contracts."""

    @runtime_checkable
    class DisplayData(Protocol):
        """Display payload contract backed by a data mapping."""

        @property
        def data(self) -> Mapping[str, t.Container]:
            """Expose the display payload."""
            ...

    @runtime_checkable
    class LoadedConfig(Protocol):
        """Loaded configuration payload contract."""

        @property
        def content(self) -> Mapping[str, t.Container]:
            """Expose loaded configuration content."""
            ...

    @runtime_checkable
    class JsonValueProcessor(Protocol):
        """Protocol for JSON-compatible value processors."""

        def __call__(self, value: t.Cli.JsonValue) -> t.Cli.JsonValue:
            """Transform one JSON-compatible value."""
            ...

    @runtime_checkable
    class ModelCommandHandler[TParams: m.BaseModel](Protocol):
        """Protocol for model-driven CLI command execution."""

        def __call__(self, params: TParams, /) -> t.Cli.RuntimeValue:
            """Execute one model-backed CLI command and return its normalized value."""
            ...

    @runtime_checkable
    class CommandEntry(Protocol):
        """Protocol for command registry entries."""

        name: str
        handler: t.Cli.JsonCommandFn

    @runtime_checkable
    class ResultCommandRoute(Protocol):
        """Protocol for declarative result-route registration."""

        name: str
        help_text: str
        model_cls: type[m.BaseModel]
        handler: t.Cli.ResultRouteHandler
        failure_message: str
        success_message: str | None
        success_formatter: (
            FlextCliProtocolsBase.SuccessMessageFormatter[t.Cli.ResultValue] | None
        )
        success_type: str


__all__: list[str] = ["FlextCliProtocolsDomain"]
