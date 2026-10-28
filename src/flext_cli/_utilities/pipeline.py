"""DAG pipeline execution engine backed by ``u.Cli.dag_waves``.

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

import time
from collections.abc import Mapping, MutableMapping, MutableSequence, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import ClassVar

from flext_core import u

from flext_cli import c, m, p, r, settings
from flext_cli._utilities import FlextCliUtilitiesDag


class FlextCliUtilitiesPipeline:
    """Pipeline execution utilities — exposed as u.Cli.execute_pipeline()."""

    _pipeline_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)

    @staticmethod
    def execute_pipeline(
        stages: Sequence[m.Cli.PipelineStageSpec],
        context: m.Cli.PipelineStageContext,
        *,
        logger: p.Logger | None = None,
    ) -> p.Result[m.Cli.PipelineResult]:
        """Execute pipeline stages in topological order.

        Dependencies resolve through ``u.Cli.dag_waves``: a cycle or a
        dependency on an undeclared stage fails the pipeline before any stage
        runs. Stages share state via context.shared mutable mapping.

        Returns:
            The resulting ``p.Result[m.Cli.PipelineResult]``.

        """
        log = logger or FlextCliUtilitiesPipeline._pipeline_logger
        pipeline_start = time.monotonic()
        results: MutableSequence[m.Cli.PipelineStageResult] = []

        if not stages:
            return r[m.Cli.PipelineResult].ok(
                m.Cli.PipelineResult(stages=[], total_duration_ms=0.0),
            )

        stage_map: Mapping[str, m.Cli.PipelineStageSpec] = {
            spec.stage_id: spec for spec in stages
        }
        waves = FlextCliUtilitiesDag.dag_waves({
            spec.stage_id: spec.depends_on for spec in stages
        })
        if waves.failure:
            return r[m.Cli.PipelineResult].fail(
                f"pipeline graph invalid: {waves.error}"
            )

        # Stages inside a wave share no dependency edge by construction, so they
        # run concurrently; a stage still starts only after every dependency
        # completed. A strictly linear pipeline yields waves of width one.
        failed = False
        completed: MutableMapping[str, m.Cli.PipelineStageResult] = {}
        for wave in waves.value:
            if failed:
                FlextCliUtilitiesPipeline._skip_failed_wave(wave, completed)
                continue
            FlextCliUtilitiesPipeline._execute_ready_wave(
                wave,
                stage_map,
                context,
                log,
                completed,
            )
            failed = any(
                completed[stage_id].status == c.Cli.PipelineStageStatus.FAILED
                for stage_id in wave
            )

        # Report in DECLARED stage order: consumers select "the" failure with
        # next(...) over this sequence, so completion order must never leak in.
        results.extend(
            completed[spec.stage_id] for spec in stages if spec.stage_id in completed
        )

        total_ms = (time.monotonic() - pipeline_start) * 1000
        pipeline_result = m.Cli.PipelineResult(
            stages=results,
            total_duration_ms=total_ms,
        )

        log.info(
            "pipeline_complete",
            total_stages=len(results),
            failed=len(pipeline_result.failed_stages),
            skipped=len(pipeline_result.skipped_stages),
            duration_ms=round(total_ms, 2),
        )

        if pipeline_result.failed_stages:
            return r[m.Cli.PipelineResult].fail("one or more pipeline stages failed")
        return r[m.Cli.PipelineResult].ok(pipeline_result)

    @staticmethod
    def _skip_failed_wave(
        wave: Sequence[str],
        completed: MutableMapping[str, m.Cli.PipelineStageResult],
    ) -> None:
        """Record every stage of a wave as skipped after a prior failure."""
        for stage_id in wave:
            completed[stage_id] = m.Cli.PipelineStageResult(
                stage_id=stage_id,
                status=c.Cli.PipelineStageStatus.SKIPPED,
                error="skipped due to prior failure",
            )

    @staticmethod
    def _execute_ready_wave(
        known: Sequence[str],
        stage_map: Mapping[str, m.Cli.PipelineStageSpec],
        context: m.Cli.PipelineStageContext,
        log: p.Logger,
        completed: MutableMapping[str, m.Cli.PipelineStageResult],
    ) -> None:
        """Run ready stages and collect futures in submission order before retiring."""
        if len(known) == 1:
            stage_id = known[0]
            completed[stage_id] = FlextCliUtilitiesPipeline._run_stage(
                stage_map[stage_id],
                context,
                log,
            )
        elif known:
            with ThreadPoolExecutor(
                max_workers=min(settings.cli_pipeline_max_workers, len(known)),
                thread_name_prefix="pipeline_",
            ) as executor:
                futures = {
                    stage_id: executor.submit(
                        FlextCliUtilitiesPipeline._run_stage,
                        stage_map[stage_id],
                        context,
                        log,
                    )
                    for stage_id in known
                }
                for stage_id, future in futures.items():
                    completed[stage_id] = future.result()

    @staticmethod
    def _run_stage(
        spec: m.Cli.PipelineStageSpec,
        context: m.Cli.PipelineStageContext,
        log: p.Logger,
    ) -> m.Cli.PipelineStageResult:
        """Execute a single stage and preserve its first failure.

        Returns:
            The resulting ``m.Cli.PipelineStageResult``.

        """
        if spec.skip_if is not None and spec.skip_if(context):
            log.debug("stage_skipped", stage_id=spec.stage_id, reason="skip_if")
            return m.Cli.PipelineStageResult(
                stage_id=spec.stage_id,
                status=c.Cli.PipelineStageStatus.SKIPPED,
            )

        stage_start = time.monotonic()
        result = spec.handler(context)
        duration_ms = (time.monotonic() - stage_start) * 1000

        if result.success:
            stage_result = result.value
            return stage_result.model_copy(update={"duration_ms": duration_ms})

        error = result.error or f"stage {spec.stage_id} failed"
        log.error("stage_failed", stage_id=spec.stage_id, error=error)
        return m.Cli.PipelineStageResult(
            stage_id=spec.stage_id,
            status=c.Cli.PipelineStageStatus.FAILED,
            error=error,
            duration_ms=duration_ms,
        )


__all__ = ("FlextCliUtilitiesPipeline",)
