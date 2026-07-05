"""Higher-level CLI structural contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from pathlib import Path

    from flext_cli import t
    from flext_cli._protocols.base import FlextCliProtocolsBase


class FlextCliProtocolsDomain:
    """CLI domain protocols layered on top of base callable contracts."""

    @runtime_checkable
    class JsonValueProcessor(Protocol):
        """Protocol for JSON-compatible value processors."""

        def __call__(self, value: t.JsonValue) -> t.JsonValue:
            """Transform one JSON-compatible value."""
            ...

    @runtime_checkable
    class ModelCommandHandler[TParams: t.Cli.ModelLike](Protocol):
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
        model_cls: t.Cli.ModelType[t.Cli.ModelLike]
        handler: t.Cli.ResultRouteHandler
        success_message: str | None
        success_formatter: (
            FlextCliProtocolsBase.SuccessMessageFormatter[t.Cli.ResultValue] | None
        )
        success_type: t.Cli.MessageType

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

        @property
        def verb(self) -> str:
            """Verb label for the summary block."""
            ...

        @property
        def total(self) -> int:
            """Total processed items."""
            ...

        @property
        def success(self) -> int:
            """Successful items."""
            ...

        @property
        def failed(self) -> int:
            """Failed items."""
            ...

        @property
        def skipped(self) -> int:
            """Skipped items."""
            ...

        @property
        def elapsed(self) -> float:
            """Elapsed time in seconds."""
            ...

    @runtime_checkable
    class ProjectFailureInfo(Protocol):
        """Per-project failure descriptor for verbose diagnostics."""

        @property
        def project(self) -> str:
            """Project name."""
            ...

        @property
        def elapsed(self) -> float:
            """Elapsed time in seconds."""
            ...

        @property
        def error_count(self) -> int:
            """Total project errors."""
            ...

        @property
        def log_path(self) -> Path:
            """Path to the project log."""
            ...

        @property
        def max_show(self) -> int:
            """Maximum errors to render."""
            ...

        @property
        def errors(self) -> t.SequenceOf[str]:
            """Rendered error excerpt lines."""
            ...


__all__: list[str] = ["FlextCliProtocolsDomain"]
