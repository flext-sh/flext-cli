"""Pipeline protocol contracts for DAG-based stage execution.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from flext_core import p

    from flext_cli._typings import FlextCliTypesPipeline


from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols

if TYPE_CHECKING:
    # mro-j47u (codex): p -> m is a reverse facade edge; keep it type-only.

    from flext_cli import t


class FlextCliProtocolsPipeline:
    """Pipeline protocol namespace."""

    @runtime_checkable
    class PipelineStageContext(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def repository_root(self) -> Path:
            """Repository root directory."""
            ...

        @property
        def shared(self) -> t.MutableJsonMapping:
            """Mutable shared state between stages."""
            ...

        @property
        def settings(self) -> t.JsonMapping:
            """Immutable pipeline configuration."""
            ...

    @runtime_checkable
    class PipelineStage(Protocol):
        """Contract for a callable pipeline stage handler."""

        def __call__(
            self,
            ctx: FlextCliProtocolsPipeline.PipelineStageContext,
            /,
        ) -> p.Result[FlextCliProtocolsPipeline.PipelineStageResult]:
            """Execute stage and return typed result."""
            ...

    @runtime_checkable
    class PipelineSkipPredicate(Protocol):
        """Contract for deciding whether one stage is skipped."""

        def __call__(
            self,
            ctx: FlextCliProtocolsPipeline.PipelineStageContext,
            /,
        ) -> bool:
            """Return whether the stage must be skipped."""
            ...

    @runtime_checkable
    class PipelineService(Protocol):
        """Contract for the public pipeline DSL exposed on ``cli``."""

        def stage_context(
            self,
            repository_root: Path,
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
            handler: FlextCliProtocolsPipeline.PipelineStage,
            depends_on: Sequence[str] | frozenset[str] = (),
            skip_if: FlextCliProtocolsPipeline.PipelineSkipPredicate | None = None,
        ) -> FlextCliProtocolsPipeline.PipelineStageSpec:
            """Build one declarative pipeline stage spec."""
            ...

        def stage_result(
            self,
            stage_id: str,
            *,
            status: t.Cli.PipelineStageStatus,
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
            stages: Sequence[FlextCliProtocolsPipeline.PipelineStageSpec],
            *,
            context: FlextCliProtocolsPipeline.PipelineStageContext,
            logger: p.Logger | None = None,
        ) -> p.Result[FlextCliProtocolsPipeline.PipelineResult]:
            """Execute a pipeline from the public service DSL."""
            ...

        def linear_pipeline(
            self,
            stage_order: Sequence[str],
            handlers: Mapping[str, FlextCliProtocolsPipeline.PipelineStage],
            *,
            skip_by_stage: Mapping[
                str,
                FlextCliProtocolsPipeline.PipelineSkipPredicate,
            ]
            | None = None,
        ) -> Sequence[FlextCliProtocolsPipeline.PipelineStageSpec]:
            """Build a linear dependency chain with canonical previous-stage deps."""
            ...

    @runtime_checkable
    class PipelineStageSpec(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def stage_id(self) -> str:
            """Unique stage identifier."""
            ...

        @property
        def depends_on(self) -> frozenset[str]:
            """Stage IDs this stage depends on."""
            ...

        @property
        def handler(
            self,
        ) -> Callable[
            [FlextCliProtocolsPipeline.PipelineStageContext],
            p.Result[FlextCliProtocolsPipeline.PipelineStageResult],
        ]:
            """Callable that executes the stage."""
            ...

        @property
        def skip_if(
            self,
        ) -> Callable[[FlextCliProtocolsPipeline.PipelineStageContext], bool] | None:
            """Predicate — skip stage if returns True."""
            ...

        @property
        def retry(self) -> int:
            """Number of retries on failure."""
            ...

    @runtime_checkable
    class PipelineStageResult(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def stage_id(self) -> str:
            """Stage that produced this result."""
            ...

        @property
        def status(self) -> FlextCliTypesPipeline.PipelineStageStatus:
            """Execution outcome."""
            ...

        @property
        def output(self) -> t.JsonMapping:
            """Stage output payload."""
            ...

        @property
        def duration_ms(self) -> float:
            """Execution duration in milliseconds."""
            ...

        @property
        def error(self) -> str | None:
            """Error message if failed."""
            ...

    @runtime_checkable
    class PipelineResult(FlextProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def stages(self) -> Sequence[FlextCliProtocolsPipeline.PipelineStageResult]:
            """Results from all executed stages."""
            ...

        @property
        def total_duration_ms(self) -> float:
            """Total pipeline execution time."""
            ...

        @property
        def success(self) -> bool:
            """True if no stage failed."""
            ...

        @property
        def failed_stages(
            self,
        ) -> Sequence[FlextCliProtocolsPipeline.PipelineStageResult]:
            """Only the failed stage results."""
            ...

        @property
        def skipped_stages(
            self,
        ) -> Sequence[FlextCliProtocolsPipeline.PipelineStageResult]:
            """Only the skipped stage results."""
            ...


__all__: list[str] = ["FlextCliProtocolsPipeline"]
