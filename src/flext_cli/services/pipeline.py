"""Pipeline DSL service exposed through the flext-cli public facade.

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

from collections.abc import Mapping, MutableSequence, Sequence
from pathlib import Path

from flext_cli import c, m, p, r, s, t, u


class FlextCliPipeline(s[p.Cli.RuntimeStatus]):
    """Expose the canonical pipeline DSL through the service layer."""

    @staticmethod
    def stage_context(
        repository_root: Path,
        *,
        shared: t.MutableJsonMapping | None = None,
        settings: t.JsonMapping | None = None,
    ) -> m.Cli.PipelineStageContext:
        """Build one validated stage context from the public DSL.

        Args:
            repository_root: Repository root the stages operate within.
            shared: Optional mutable mapping shared across stages.
            settings: Optional read-only settings mapping for stages.

        Returns:
            The resulting ``m.Cli.PipelineStageContext``.

        """
        return m.Cli.PipelineStageContext.model_validate({
            "repository_root": repository_root,
            "shared": {} if shared is None else shared,
            "settings": {} if settings is None else settings,
        })

    @staticmethod
    def stage(
        stage_id: str,
        *,
        handler: p.Cli.PipelineStage,
        depends_on: Sequence[str] | frozenset[str] = (),
        skip_if: p.Cli.PipelineSkipPredicate | None = None,
    ) -> m.Cli.PipelineStageSpec:
        """Build one declarative stage spec from the public DSL.

        Args:
            stage_id: Unique identifier of the stage.
            handler: Callable that executes the stage.
            depends_on: Identifiers of stages that must complete first.
            skip_if: Optional predicate that skips the stage when it returns
                true.

        Returns:
            The resulting ``m.Cli.PipelineStageSpec``.

        """
        return m.Cli.PipelineStageSpec.model_validate({
            "stage_id": stage_id,
            "depends_on": frozenset(depends_on),
            "handler": handler,
            "skip_if": skip_if,
        })

    @staticmethod
    def stage_result(
        stage_id: str,
        *,
        status: t.Cli.PipelineStageStatus = c.Cli.PipelineStageStatus.OK,
        output: t.JsonMapping | None = None,
        duration_ms: float = 0.0,
        error: str | None = None,
    ) -> m.Cli.PipelineStageResult:
        """Build one typed stage result payload.

        Args:
            stage_id: Identifier of the stage that produced the result.
            status: Stage outcome status; defaults to the OK status.
            output: Optional JSON mapping produced by the stage.
            duration_ms: Stage execution duration in milliseconds.
            error: Optional error message when the stage failed.

        Returns:
            The resulting ``m.Cli.PipelineStageResult``.

        """
        return m.Cli.PipelineStageResult.model_validate({
            "stage_id": stage_id,
            "status": status,
            "output": {} if output is None else output,
            "duration_ms": duration_ms,
            "error": error,
        })

    @classmethod
    def ok_stage(
        cls,
        stage_id: str,
        *,
        output: t.JsonMapping | None = None,
        duration_ms: float = 0.0,
    ) -> p.Result[m.Cli.PipelineStageResult]:
        """Return one successful stage result via the canonical ``r`` API.

        Args:
            stage_id: Identifier of the successful stage.
            output: Optional JSON mapping produced by the stage.
            duration_ms: Stage execution duration in milliseconds.

        Returns:
            One successful stage result via the canonical ``r`` API.

        """
        return r[m.Cli.PipelineStageResult].ok(
            cls.stage_result(
                stage_id,
                status=c.Cli.PipelineStageStatus.OK,
                output=output,
                duration_ms=duration_ms,
            ),
        )

    @classmethod
    def linear_pipeline(
        cls,
        stage_order: Sequence[str],
        handlers: Mapping[str, p.Cli.PipelineStage],
        *,
        skip_by_stage: Mapping[str, p.Cli.PipelineSkipPredicate] | None = None,
    ) -> Sequence[m.Cli.PipelineStageSpec]:
        """Build a linear dependency chain from ordered stage handlers.

        Args:
            stage_order: Ordered stage identifiers forming the chain.
            handlers: Mapping of stage identifier to its handler.
            skip_by_stage: Optional mapping of stage identifier to its skip
                predicate.

        Returns:
            The resulting ``Sequence[m.Cli.PipelineStageSpec]``.

        """
        skips = skip_by_stage or {}
        stage_list: MutableSequence[m.Cli.PipelineStageSpec] = []
        previous_stage_id: str | None = None
        for stage_id in stage_order:
            stage_list.append(
                cls.stage(
                    stage_id,
                    handler=handlers[stage_id],
                    depends_on=()
                    if previous_stage_id is None
                    else (previous_stage_id,),
                    skip_if=skips.get(stage_id),
                ),
            )
            previous_stage_id = stage_id
        return tuple(stage_list)

    def pipeline(
        self,
        stages: Sequence[m.Cli.PipelineStageSpec],
        *,
        context: m.Cli.PipelineStageContext,
        logger: p.Logger | None = None,
    ) -> p.Result[m.Cli.PipelineResult]:
        """Execute a pipeline through the public CLI DSL surface.

        Args:
            stages: Ordered stage specifications to execute.
            context: Validated context shared by the stages.
            logger: Optional logger; the service logger applies when omitted.

        Returns:
            The resulting ``p.Result[m.Cli.PipelineResult]``.

        """
        return u.Cli.execute_pipeline(stages, context, logger=logger or self.logger)


__all__: MutableSequence[str] = ["FlextCliPipeline"]
