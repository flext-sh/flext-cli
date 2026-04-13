"""Pipeline Pydantic domain models for DAG execution."""

from __future__ import annotations

from collections.abc import Callable, MutableMapping, Sequence
from pathlib import Path
from typing import Annotated, ClassVar

from pydantic import ConfigDict, Field, computed_field

from flext_cli import c, r, t
from flext_core import m


class FlextCliModelsPipeline:
    """Pipeline models namespace — flat in m.Cli.*."""

    class PipelineStageContext(m.ContractModel):
        """Accumulated state passed between pipeline stages."""

        _flext_enforcement_exempt: ClassVar[bool] = True

        model_config: ClassVar[ConfigDict] = ConfigDict(
            extra="forbid",
            validate_assignment=True,
            arbitrary_types_allowed=True,
        )

        workspace_root: Annotated[
            Path,
            Field(description="Workspace root directory"),
        ]
        shared: Annotated[
            MutableMapping[str, t.RecursiveContainer],
            Field(
                default_factory=dict, description="Mutable shared state between stages"
            ),
        ]
        settings: Annotated[
            t.RecursiveContainerMapping,
            Field(default_factory=dict, description="Immutable pipeline configuration"),
        ]

    class PipelineStageSpec(m.ContractModel):
        """Declarative stage definition with dependency tracking."""

        _flext_enforcement_exempt: ClassVar[bool] = True

        model_config: ClassVar[ConfigDict] = ConfigDict(
            extra="forbid",
            arbitrary_types_allowed=True,
        )

        stage_id: Annotated[
            str,
            Field(description="Unique stage identifier"),
        ]
        depends_on: Annotated[
            frozenset[str],
            Field(
                default_factory=frozenset, description="Stage IDs this stage depends on"
            ),
        ]
        # NOTE: handler/skip_if use inline Callable, not t.Cli.PipelineHandler /
        # t.Cli.PipelineSkipPredicate.  Those are PEP 695 `type` aliases that
        # reference p.Cli.PipelineStageContext under TYPE_CHECKING — Pydantic
        # cannot resolve them at runtime for model field validation.
        handler: Annotated[
            Callable[
                [FlextCliModelsPipeline.PipelineStageContext],
                r[FlextCliModelsPipeline.PipelineStageResult],
            ],
            Field(description="Callable that executes the stage"),
        ]
        skip_if: Annotated[
            Callable[[FlextCliModelsPipeline.PipelineStageContext], bool] | None,
            Field(default=None, description="Predicate — skip stage if returns True"),
        ]
        retry: Annotated[
            int,
            Field(
                default=c.Cli.PIPELINE_DEFAULT_RETRY,
                ge=0,
                le=c.Cli.PIPELINE_MAX_RETRY,
                description="Number of retries on failure",
            ),
        ]

    class PipelineStageResult(m.ContractModel):
        """What a stage produces after execution."""

        _flext_enforcement_exempt: ClassVar[bool] = True

        model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

        stage_id: Annotated[str, Field(description="Stage that produced this result")]
        status: Annotated[
            t.Cli.PipelineStageStatus,
            Field(description="Execution outcome"),
        ]
        output: Annotated[
            t.RecursiveContainerMapping,
            Field(default_factory=dict, description="Stage output payload"),
        ]
        duration_ms: Annotated[
            float,
            Field(default=0.0, description="Execution duration in milliseconds"),
        ]
        error: Annotated[
            str | None,
            Field(default=None, description="Error message if failed"),
        ]

    class PipelineResult(m.ContractModel):
        """Full pipeline execution result — aggregated from all stages."""

        model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

        stages: Annotated[
            Sequence[FlextCliModelsPipeline.PipelineStageResult],
            Field(default_factory=list, description="Results from all executed stages"),
        ]
        total_duration_ms: Annotated[
            float,
            Field(default=0.0, description="Total pipeline execution time"),
        ]

        @computed_field
        @property
        def success(self) -> bool:
            """True if no stage failed."""
            return all(
                s.status != c.Cli.PipelineStageStatus.FAILED for s in self.stages
            )

        @computed_field
        @property
        def failed_stages(self) -> Sequence[FlextCliModelsPipeline.PipelineStageResult]:
            """Return only failed stage results."""
            return [
                s for s in self.stages if s.status == c.Cli.PipelineStageStatus.FAILED
            ]

        @computed_field
        @property
        def skipped_stages(
            self,
        ) -> Sequence[FlextCliModelsPipeline.PipelineStageResult]:
            """Return only skipped stage results."""
            return [
                s for s in self.stages if s.status == c.Cli.PipelineStageStatus.SKIPPED
            ]


__all__: list[str] = ["FlextCliModelsPipeline"]
