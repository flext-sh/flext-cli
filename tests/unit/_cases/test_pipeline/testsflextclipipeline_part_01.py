"""Unit tests for the DAG pipeline engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests import c
from tests import m

from flext_cli import cli, r
from flext_tests import tm

if TYPE_CHECKING:
    from pathlib import Path

    from tests import p
    from tests import t


class TestsFlextCliPipeline:
    """Implementation part for TestsFlextCliPipeline."""

    @staticmethod
    def _ok_handler(stage_id: str, output_key: str = "done") -> t.Cli.PipelineHandler:
        """Build a handler that succeeds and writes to shared."""

        def handler(
            ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            ctx.shared[output_key] = stage_id
            return cli.ok_stage(
                stage_id, output={output_key: stage_id}, duration_ms=1.0
            )

        return handler

    @staticmethod
    def _fail_handler(stage_id: str) -> t.Cli.PipelineHandler:
        """Build a handler that fails."""

        def handler(
            ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            return r[m.Cli.PipelineStageResult].fail(f"{stage_id} failed")

        return handler

    @staticmethod
    def _skip_always(_ctx: p.Cli.PipelineStageContext) -> bool:
        return True

    def test_single_stage_ok(self, tmp_path: Path) -> None:
        """Single stage executes and returns ok."""
        stages = [cli.stage("alpha", handler=self._ok_handler("alpha"))]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        tm.ok(result)
        pipeline = result.value
        tm.that(pipeline.success, eq=True)
        tm.that(len(pipeline.stages), eq=1)
        tm.that(pipeline.stages[0].stage_id, eq="alpha")
        tm.that(pipeline.stages[0].status, eq=c.Cli.PipelineStageStatus.OK)

    def test_dependency_order(self, tmp_path: Path) -> None:
        """Stages execute in topological order — B depends on A."""
        execution_order: list[str] = []

        def tracking_handler(stage_id: str) -> t.Cli.PipelineHandler:
            def handler(
                ctx: p.Cli.PipelineStageContext,
            ) -> p.Result[m.Cli.PipelineStageResult]:
                _ = ctx
                execution_order.append(stage_id)
                return cli.ok_stage(stage_id)

            return handler

        stages = cli.linear_pipeline(
            ("a", "b"), {"a": tracking_handler("a"), "b": tracking_handler("b")}
        )
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        tm.ok(result)
        tm.that(execution_order, eq=["a", "b"])

    def test_shared_state_propagation(self, tmp_path: Path) -> None:
        """Stage B can read what stage A wrote to shared."""
        received: dict[str, t.JsonValue | None] = {}

        def reader(
            ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            received["from_a"] = ctx.shared.get("a_output")
            return cli.ok_stage("b")

        def writer(
            ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            ctx.shared["a_output"] = "hello"
            return cli.ok_stage("a")

        stages = [
            cli.stage("a", handler=writer),
            cli.stage("b", depends_on=frozenset({"a"}), handler=reader),
        ]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        tm.ok(result)
        tm.that(received["from_a"], eq="hello")

    def test_fail_fast_stops_on_failure(self, tmp_path: Path) -> None:
        """With fail_fast=True, pipeline stops after first failure."""
        stages = [
            cli.stage("a", handler=self._fail_handler("a")),
            cli.stage("b", depends_on=frozenset({"a"}), handler=self._ok_handler("b")),
        ]
        result = cli.pipeline(
            stages, context=cli.stage_context(tmp_path), fail_fast=True
        )
        tm.ok(result)
        pipeline = result.value
        tm.that(pipeline.success, eq=False)
        tm.that(len(pipeline.failed_stages), eq=1)
        tm.that(pipeline.failed_stages[0].stage_id, eq="a")

    def test_skip_predicate(self, tmp_path: Path) -> None:
        """Stage with skip_if returning True is skipped."""
        stages = [
            cli.stage(
                "skippable",
                handler=self._ok_handler("skippable"),
                skip_if=self._skip_always,
            )
        ]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        tm.ok(result)
        pipeline = result.value
        tm.that(pipeline.success, eq=True)
        tm.that(pipeline.stages[0].status, eq=c.Cli.PipelineStageStatus.SKIPPED)


__all__: list[str] = ["TestsFlextCliPipeline"]
