"""Unit tests for the DAG pipeline engine."""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

from flext_cli import cli
from flext_tests import tm

if TYPE_CHECKING:
    from pathlib import Path

    from tests import m, p, t

# ── Fixtures ────────────────────────────────────────────────────────


class TestsFlextCliPipeline:
    """Implementation part for TestsFlextCliPipeline."""

    def test_diamond_dependency(self, tmp_path: Path) -> None:
        """Diamond DAG: A -> B, A -> C, B -> D, C -> D."""
        order: list[str] = []

        def track(sid: str) -> t.Cli.PipelineHandler:
            def h(
                ctx: p.Cli.PipelineStageContext,
            ) -> p.Result[m.Cli.PipelineStageResult]:
                _ = ctx
                order.append(sid)
                return cli.ok_stage(sid)

            return h

        stages = [
            cli.stage("a", handler=track("a")),
            cli.stage("b", depends_on=frozenset({"a"}), handler=track("b")),
            cli.stage("c", depends_on=frozenset({"a"}), handler=track("c")),
            cli.stage("d", depends_on=frozenset({"b", "c"}), handler=track("d")),
        ]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        tm.ok(result)
        tm.that(order[0], eq="a")
        tm.that(order[-1], eq="d")
        tm.that(set(order[1:3]), eq={"b", "c"})


    def test_independent_stages_run_concurrently(self, tmp_path: Path) -> None:
        """Run stages that share no dependency edge at the same time."""
        # Independent gates are the dominant cost of `check`; running them one
        # after another makes the wall clock the SUM of every gate instead of
        # the slowest one. Each handler blocks on a barrier that releases only
        # once all of them are inside it, so this passes only when the engine
        # actually overlaps them.
        width = 4
        barrier = threading.Barrier(width, timeout=10)

        def blocking(sid: str) -> t.Cli.PipelineHandler:
            def handler(
                ctx: p.Cli.PipelineStageContext,
            ) -> p.Result[m.Cli.PipelineStageResult]:
                _ = ctx
                _ = barrier.wait()
                return cli.ok_stage(sid)

            return handler

        stages = [
            cli.stage(f"gate{index}", handler=blocking(f"gate{index}"))
            for index in range(width)
        ]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        tm.ok(result)
        tm.that(len(result.unwrap().stages), eq=width)

    def test_results_follow_declared_order_not_completion_order(
        self, tmp_path: Path
    ) -> None:
        """Report stages as declared even when they finish out of order."""
        # Consumers pick "the" failure with next(...) over this sequence, so a
        # concurrent engine must not let completion order leak into the report.
        def delayed(sid: str, delay: float) -> t.Cli.PipelineHandler:
            def handler(
                ctx: p.Cli.PipelineStageContext,
            ) -> p.Result[m.Cli.PipelineStageResult]:
                _ = ctx
                time.sleep(delay)
                return cli.ok_stage(sid)

            return handler

        stages = [
            cli.stage("slow", handler=delayed("slow", 0.15)),
            cli.stage("fast", handler=delayed("fast", 0.0)),
        ]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        tm.ok(result)
        tm.that(
            [stage.stage_id for stage in result.unwrap().stages],
            eq=["slow", "fast"],
        )


__all__: list[str] = ["TestsFlextCliPipeline"]
