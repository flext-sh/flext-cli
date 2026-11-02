"""Pipeline protocol contracts for DAG-based stage execution.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_cli import p


from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Protocol, runtime_checkable

if TYPE_CHECKING:
    # mro-j47u (codex): p -> m is a reverse facade edge; keep it type-only.
    from flext_core import p

    from flext_cli import t


class FlextCliProtocolsPipeline:
    """Pipeline protocol namespace."""

    @runtime_checkable
    class PipelineStageContext(Protocol):
        """Contract for stage execution context — shared state between stages."""

        @property
        def repository_root(self) -> Path:
            """Repository root directory."""
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
    class PipelineStage(Protocol):
        """Contract for a callable pipeline stage handler."""

        def __call__(
            self,
            ctx: FlextCliProtocolsPipeline.PipelineStageContext,
            /,
        ) -> p.Result[p.Cli.PipelineStageResult]:
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
        ) -> p.Cli.PipelineStageContext:
            """Build the canonical pipeline execution context."""
            ...

        def stage(
            self,
            stage_id: str,
            *,
            handler: FlextCliProtocolsPipeline.PipelineStage,
            depends_on: Sequence[str] | frozenset[str] = (),
            skip_if: FlextCliProtocolsPipeline.PipelineSkipPredicate | None = None,
        ) -> p.Cli.PipelineStageSpec:
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
        ) -> p.Cli.PipelineStageResult:
            """Build one typed pipeline stage result payload."""
            ...

        def ok_stage(
            self,
            stage_id: str,
            *,
            output: t.JsonMapping | None = None,
            duration_ms: float = 0.0,
        ) -> p.Result[p.Cli.PipelineStageResult]:
            """Return a successful typed stage result via ``r``."""
            ...

        def pipeline(
            self,
            stages: Sequence[p.Cli.PipelineStageSpec],
            *,
            context: p.Cli.PipelineStageContext,
            logger: p.Logger | None = None,
        ) -> p.Result[p.Cli.PipelineResult]:
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
        ) -> Sequence[p.Cli.PipelineStageSpec]:
            """Build a linear dependency chain with canonical previous-stage deps."""
            ...

    @runtime_checkable
    class PipelineStageSpec(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def stage_id(self) -> str: ...
        @property
        def depends_on(self) -> frozenset[str]: ...
        @property
        def handler(
            self,
        ) -> Callable[
            [p.Cli.PipelineStageContext], p.Result[p.Cli.PipelineStageResult]
        ]: ...
        @property
        def skip_if(self) -> Callable[[p.Cli.PipelineStageContext], bool] | None: ...
        @property
        def retry(self) -> int: ...

    @runtime_checkable
    class PipelineStageResult(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def stage_id(self) -> str: ...
        @property
        def status(self) -> t.Cli.PipelineStageStatus: ...
        @property
        def output(self) -> t.JsonMapping: ...
        @property
        def duration_ms(self) -> float: ...
        @property
        def error(self) -> str | None: ...

    @runtime_checkable
    class PipelineResult(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def stages(self) -> Sequence[p.Cli.PipelineStageResult]: ...
        @property
        def total_duration_ms(self) -> float: ...
        @property
        def success(self) -> bool: ...
        @property
        def failed_stages(self) -> Sequence[p.Cli.PipelineStageResult]: ...
        @property
        def skipped_stages(self) -> Sequence[p.Cli.PipelineStageResult]: ...


__all__: list[str] = ["FlextCliProtocolsPipeline"]
