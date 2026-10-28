"""Pipeline protocol contracts for DAG-based stage execution.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    # mro-j47u (codex): p -> m is a reverse facade edge; keep it type-only.
    from flext_core import p

    from flext_cli import m, t


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
        ) -> p.Result[m.Cli.PipelineStageResult]:
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
        ) -> m.Cli.PipelineStageContext:
            """Build the canonical pipeline execution context."""
            ...

        def stage(
            self,
            stage_id: str,
            *,
            handler: FlextCliProtocolsPipeline.PipelineStage,
            depends_on: Sequence[str] | frozenset[str] = (),
            skip_if: FlextCliProtocolsPipeline.PipelineSkipPredicate | None = None,
        ) -> m.Cli.PipelineStageSpec:
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
        ) -> m.Cli.PipelineStageResult:
            """Build one typed pipeline stage result payload."""
            ...

        def ok_stage(
            self,
            stage_id: str,
            *,
            output: t.JsonMapping | None = None,
            duration_ms: float = 0.0,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            """Return a successful typed stage result via ``r``."""
            ...

        def pipeline(
            self,
            stages: Sequence[m.Cli.PipelineStageSpec],
            *,
            context: m.Cli.PipelineStageContext,
            logger: p.Logger | None = None,
        ) -> p.Result[m.Cli.PipelineResult]:
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
        ) -> Sequence[m.Cli.PipelineStageSpec]:
            """Build a linear dependency chain with canonical previous-stage deps."""
            ...


__all__: list[str] = ["FlextCliProtocolsPipeline"]
