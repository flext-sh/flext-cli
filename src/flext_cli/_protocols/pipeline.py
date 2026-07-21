"""Pipeline protocol contracts for DAG-based stage execution."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from flext_cli._constants.enums import FlextCliConstantsEnums as ce
    from flext_core import p, t


class FlextCliProtocolsPipeline:
    """Pipeline protocol namespace."""

    # mro-wkii.17.26 (codex): pipeline contracts are owned by p so the t
    # facade never imports concrete m models while either facade is composed.
    @runtime_checkable
    class PipelineStageContext(Protocol):
        """Contract for stage execution context — carries shared state between stages."""

        @property
        def workspace_root(self) -> Path:
            """Workspace root directory."""
            ...

        @property
        def shared(self) -> t.MutableJsonMapping:
            """Mutable shared state between stages — stages write outputs here."""
            ...

        @property
        def settings(self) -> t.JsonMapping:
            """Immutable configuration for the pipeline run."""
            ...

    @runtime_checkable
    class PipelineStageResult(Protocol):
        """Observable result of one executed pipeline stage."""

        @property
        def stage_id(self) -> str:
            """Stage identifier."""
            ...

        @property
        def status(self) -> ce.PipelineStageStatus:
            """Stage execution status."""
            ...

        @property
        def output(self) -> t.JsonMapping:
            """Stage output payload."""
            ...

        @property
        def duration_ms(self) -> float:
            """Stage execution duration in milliseconds."""
            ...

        @property
        def error(self) -> str | None:
            """Stage error message."""
            ...

    @runtime_checkable
    class PipelineStageSpec(Protocol):
        """Declarative pipeline stage contract."""

        @property
        def stage_id(self) -> str:
            """Stage identifier."""
            ...

        @property
        def depends_on(self) -> frozenset[str]:
            """Identifiers of prerequisite stages."""
            ...

        @property
        def handler(
            self,
        ) -> Callable[
            [FlextCliProtocolsPipeline.PipelineStageContext],
            p.Result[FlextCliProtocolsPipeline.PipelineStageResult],
        ]:
            """Stage execution handler."""
            ...

        @property
        def skip_if(
            self,
        ) -> Callable[[FlextCliProtocolsPipeline.PipelineStageContext], bool] | None:
            """Optional stage skip predicate."""
            ...

        @property
        def retry(self) -> int:
            """Maximum retry count."""
            ...

    @runtime_checkable
    class PipelineResult(Protocol):
        """Observable aggregate pipeline result."""

        @property
        def stages(self) -> t.SequenceOf[FlextCliProtocolsPipeline.PipelineStageResult]:
            """Results from executed stages."""
            ...

        @property
        def total_duration_ms(self) -> float:
            """Total execution duration in milliseconds."""
            ...

        @property
        def success(self) -> bool:
            """Whether every executed stage succeeded."""
            ...

        @property
        def failed_stages(
            self,
        ) -> t.SequenceOf[FlextCliProtocolsPipeline.PipelineStageResult]:
            """Failed stage results."""
            ...

        @property
        def skipped_stages(
            self,
        ) -> t.SequenceOf[FlextCliProtocolsPipeline.PipelineStageResult]:
            """Skipped stage results."""
            ...

    @runtime_checkable
    class PipelineStage(Protocol):
        """Contract for a callable pipeline stage handler."""

        def __call__(
            self, ctx: FlextCliProtocolsPipeline.PipelineStageContext
        ) -> p.Result[FlextCliProtocolsPipeline.PipelineStageResult]:
            """Execute stage and return typed result."""
            ...

    @runtime_checkable
    class PipelineExecutor(Protocol):
        """Contract for pipeline execution engine."""

        def execute(
            self,
            stages: t.SequenceOf[FlextCliProtocolsPipeline.PipelineStageSpec],
            context: FlextCliProtocolsPipeline.PipelineStageContext,
            *,
            fail_fast: bool = True,
        ) -> p.Result[FlextCliProtocolsPipeline.PipelineResult]:
            """Execute stages in dependency order."""
            ...

    @runtime_checkable
    class PipelineService(Protocol):
        """Contract for the public pipeline DSL exposed on ``cli``."""

        def stage_context(
            self,
            workspace_root: Path,
            *,
            shared: t.MutableJsonMapping | None = None,
            settings: t.JsonMapping | None = None,
        ) -> FlextCliProtocolsPipeline.PipelineStageContext:
            """Build the canonical pipeline execution context."""
            ...

        def stage(
            self,
            stage_id: str,
            *,
            handler: Callable[
                [FlextCliProtocolsPipeline.PipelineStageContext],
                p.Result[FlextCliProtocolsPipeline.PipelineStageResult],
            ],
            depends_on: t.SequenceOf[str] | frozenset[str] = (),
            skip_if: Callable[[FlextCliProtocolsPipeline.PipelineStageContext], bool]
            | None = None,
            retry: int = 0,
        ) -> FlextCliProtocolsPipeline.PipelineStageSpec:
            """Build one declarative pipeline stage spec."""
            ...

        def stage_result(
            self,
            stage_id: str,
            *,
            status: ce.PipelineStageStatus,
            output: t.JsonMapping | None = None,
            duration_ms: float = 0.0,
            error: str | None = None,
        ) -> FlextCliProtocolsPipeline.PipelineStageResult:
            """Build one typed pipeline stage result payload."""
            ...

        def ok_stage(
            self,
            stage_id: str,
            *,
            output: t.JsonMapping | None = None,
            duration_ms: float = 0.0,
        ) -> p.Result[FlextCliProtocolsPipeline.PipelineStageResult]:
            """Return a successful typed stage result via ``r``."""
            ...

        def pipeline(
            self,
            stages: t.SequenceOf[FlextCliProtocolsPipeline.PipelineStageSpec],
            *,
            context: FlextCliProtocolsPipeline.PipelineStageContext,
            fail_fast: bool = True,
            logger: p.Logger | None = None,
        ) -> p.Result[FlextCliProtocolsPipeline.PipelineResult]:
            """Execute a pipeline from the public service DSL."""
            ...

        def linear_pipeline(
            self,
            stage_order: t.StrSequence,
            handlers: t.MappingKV[
                str,
                Callable[
                    [FlextCliProtocolsPipeline.PipelineStageContext],
                    p.Result[FlextCliProtocolsPipeline.PipelineStageResult],
                ],
            ],
            *,
            retry_by_stage: t.MappingKV[str, int] | None = None,
            skip_by_stage: t.MappingKV[
                str, Callable[[FlextCliProtocolsPipeline.PipelineStageContext], bool]
            ]
            | None = None,
        ) -> t.SequenceOf[FlextCliProtocolsPipeline.PipelineStageSpec]:
            """Build a linear dependency chain with canonical previous-stage deps."""
            ...


__all__: tuple[str, ...] = ("FlextCliProtocolsPipeline",)
