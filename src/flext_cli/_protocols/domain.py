"""Higher-level CLI structural contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_cli import FlextCliProtocolsBase
from flext_core import m

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from flext_cli import t


class FlextCliProtocolsDomain:
    """CLI domain protocols layered on top of base callable contracts."""

    @runtime_checkable
    class DisplayData(Protocol):
        """Display payload contract backed by a data mapping."""

        @property
        def data(self) -> t.JsonMapping:
            """Expose the display payload."""
            ...

    @runtime_checkable
    class LoadedConfig(Protocol):
        """Loaded configuration payload contract."""

        @property
        def content(self) -> t.JsonMapping:
            """Expose loaded configuration content."""
            ...

    @runtime_checkable
    class JsonValueProcessor(Protocol):
        """Protocol for JSON-compatible value processors."""

        def __call__(self, value: t.JsonValue) -> t.JsonValue:
            """Transform one JSON-compatible value."""
            ...

    @runtime_checkable
    class ModelCommandHandler[TParams: m.BaseModel](Protocol):
        """Protocol for model-driven CLI command execution."""

        def __call__(self, params: TParams, /) -> t.JsonValue:
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
        success_message: str | None
        success_formatter: (
            FlextCliProtocolsBase.SuccessMessageFormatter[t.Cli.ResultValue] | None
        )
        success_type: str

    @runtime_checkable
    class DeclarativeRuleType[TRule](Protocol):
        """Class contract for one settings-backed declarative rule implementation."""

        RULE_MATCHERS: t.Cli.RuleMatchers

        def __call__(self, settings: t.JsonMapping, /) -> TRule:
            """Instantiate one runtime rule from one validated rule definition."""
            ...

    @runtime_checkable
    class DeclarativeFileRuleType[TRule](Protocol):
        """Class contract for one no-arg declarative file-rule implementation."""

        RULE_MATCHERS: t.Cli.RuleMatchers

        def __call__(self) -> TRule:
            """Instantiate one file rule without extra runtime settings."""
            ...

    @runtime_checkable
    class SummaryStats(Protocol):
        """Workspace orchestration summary payload contract."""

        verb: str
        total: int
        success: int
        failed: int
        skipped: int
        elapsed: float

    @runtime_checkable
    class ProjectFailureInfo(Protocol):
        """Per-project failure descriptor for verbose diagnostics."""

        project: str
        elapsed: float
        error_count: int
        log_path: Path
        max_show: int
        errors: Sequence[str]


__all__: list[str] = ["FlextCliProtocolsDomain"]
