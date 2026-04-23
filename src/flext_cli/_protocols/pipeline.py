"""Pipeline protocol contracts for DAG-based stage execution."""

from __future__ import annotations

from collections.abc import (
    Sequence,
)
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import p, t

if TYPE_CHECKING:
    from flext_cli._models.pipeline import FlextCliModelsPipeline


class FlextCliProtocolsPipeline:
    """Pipeline protocol namespace."""

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
    class PipelineStage(Protocol):
        """Contract for a callable pipeline stage handler."""

        def __call__(
            self,
            ctx: FlextCliProtocolsPipeline.PipelineStageContext,
        ) -> p.Result[FlextCliModelsPipeline.PipelineStageResult]:
            """Execute stage and return typed result."""
            ...

    @runtime_checkable
    class PipelineExecutor(Protocol):
        """Contract for pipeline execution engine."""

        def execute(
            self,
            stages: Sequence[FlextCliModelsPipeline.PipelineStageSpec],
            context: FlextCliProtocolsPipeline.PipelineStageContext,
            *,
            fail_fast: bool = True,
        ) -> p.Result[FlextCliModelsPipeline.PipelineResult]:
            """Execute stages in dependency order."""
            ...


__all__: list[str] = ["FlextCliProtocolsPipeline"]
