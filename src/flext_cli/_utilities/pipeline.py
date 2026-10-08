"""DAG pipeline execution engine backed by graphlib.TopologicalSorter.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from graphlib import CycleError, TopologicalSorter
from typing import ClassVar

from flext_cli import c, m, p, r, settings, t
from flext_core import u


class FlextCliUtilitiesPipeline:
    """Pipeline execution utilities — exposed as u.Cli.execute_pipeline()."""

    _pipeline_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)

    @staticmethod
    def execute_pipeline(
        stages: t.SequenceOf[m.Cli.PipelineStageSpec],
        context: m.Cli.PipelineStageContext,
        *,
        logger: p.Logger | None = None,
    ) -> p.Result[m.Cli.PipelineResult]:
        """Execute pipeline stages in topological order.

        Uses graphlib.TopologicalSorter for dependency resolution.
        Stages share state via context.shared mutable mapping.

        Returns:
            The resulting ``p.Result[m.Cli.PipelineResult]``.

        """
        log = logger or FlextCliUtilitiesPipeline._pipeline_logger
        pipeline_start = time.monotonic()
        results: t.MutableSequenceOf[m.Cli.PipelineStageResult] = []

        if not stages:
            return r[m.Cli.PipelineResult].ok(
                m.Cli.PipelineResult(stages=[], total_duration_ms=0.0),
            )

        # Build stage lookup and dependency graph.
        stage_map: dict[str, m.Cli.PipelineStageSpec] = {s.stage_id: s for s in stages}

        # Build TopologicalSorter graph.
        sorter: TopologicalSorter[str] = TopologicalSorter()
        for spec in stages:
            sorter.add(spec.stage_id, *spec.depends_on)

        try:
            sorter.prepare()
        except CycleError as exc:
            return r[m.Cli.PipelineResult].fail(
                f"pipeline cycle detected: {exc}",
                exception=exc,
            )

        # Walk the graph one READY WAVE at a time instead of flattening it to a
        # single serial order. Stages inside a wave share no dependency edge by
        # construction, so they run concurrently; a stage still starts only
        # after every dependency completed. A strictly linear pipeline yields
        # waves of width one and therefore behaves exactly as before.
        failed = False
        completed: dict[str, m.Cli.PipelineStageResult] = {}
        while sorter.is_active():
            wave = tuple(sorter.get_ready())
            if not wave:
                break
            known = FlextCliUtilitiesPipeline._retire_unknown_stages(
                wave,
                stage_map,
                sorter,
            )
            if failed:
                FlextCliUtilitiesPipeline._skip_failed_wave(known, completed, sorter)
                continue
            FlextCliUtilitiesPipeline._execute_ready_wave(
                known,
                stage_map,
                context,
                log,
                completed,
            )
            for stage_id in known:
                sorter.done(stage_id)
            if any(
                completed[stage_id].status == c.Cli.PipelineStageStatus.FAILED
                for stage_id in known
            ):
                failed = True

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
    def _retire_unknown_stages(
        wave: t.VariadicTuple[str],
        stage_map: dict[str, m.Cli.PipelineStageSpec],
        sorter: TopologicalSorter[str],
    ) -> t.VariadicTuple[str]:
        """Retire undeclared dependencies while retaining ready-stage order.

        Returns:
            Declared stage IDs in their ready-wave order.

        """
        known = tuple(stage_id for stage_id in wave if stage_id in stage_map)
        for stage_id in wave:
            if stage_id not in stage_map:
                sorter.done(stage_id)
        return known

    @staticmethod
    def _skip_failed_wave(
        known: t.VariadicTuple[str],
        completed: dict[str, m.Cli.PipelineStageResult],
        sorter: TopologicalSorter[str],
    ) -> None:
        """Record skipped stages and advance the graph after a prior failure."""
        for stage_id in known:
            completed[stage_id] = m.Cli.PipelineStageResult(
                stage_id=stage_id,
                status=c.Cli.PipelineStageStatus.SKIPPED,
                error="skipped due to prior failure",
            )
            sorter.done(stage_id)

    @staticmethod
    def _execute_ready_wave(
        known: t.VariadicTuple[str],
        stage_map: dict[str, m.Cli.PipelineStageSpec],
        context: m.Cli.PipelineStageContext,
        log: p.Logger,
        completed: dict[str, m.Cli.PipelineStageResult],
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
