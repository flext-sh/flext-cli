"""Unit tests for the DAG pipeline engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_cli import cli, r
from flext_tests import tm
from tests import m

if TYPE_CHECKING:
    from pathlib import Path

    from tests import p, t


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

    def test_cycle_detection(self, tmp_path: Path) -> None:
        """Circular dependencies produce a failure result."""
        stages = [
            cli.stage("a", depends_on=frozenset({"b"}), handler=self._ok_handler("a")),
            cli.stage("b", depends_on=frozenset({"a"}), handler=self._ok_handler("b")),
        ]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        tm.fail(result)

    def test_failure_result_runs_stage_once(self, tmp_path: Path) -> None:
        """A failed stage result stops after its first execution."""
        call_count = 0

        def failing(
            _ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            nonlocal call_count
            call_count += 1
            return r[m.Cli.PipelineStageResult].fail("stage failed")

        stages = [cli.stage("failure", handler=failing)]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        tm.fail(result)
        tm.that(call_count, eq=1)

    def test_stage_exception_escapes_first_execution(self, tmp_path: Path) -> None:
        """The first stage exception escapes without normalization or retry."""
        call_count = 0
        error_message = "boom"

        def exploding(
            ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            nonlocal call_count
            _ = ctx
            call_count += 1
            raise ValueError(error_message)

        with pytest.raises(ValueError, match=error_message):
            cli.pipeline(
                [cli.stage("boom", handler=exploding)],
                context=cli.stage_context(tmp_path),
            )
        tm.that(call_count, eq=1)

    def test_empty_pipeline(self, tmp_path: Path) -> None:
        """Empty pipeline returns ok with no stages."""
        result = cli.pipeline([], context=cli.stage_context(tmp_path))
        tm.ok(result)
        tm.that(result.value.success, eq=True)
        tm.that(len(result.value.stages), eq=0)

    def test_total_duration_tracked(self, tmp_path: Path) -> None:
        """Pipeline tracks total duration."""
        stages = [cli.stage("a", handler=self._ok_handler("a"))]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        tm.ok(result)
        tm.that(result.value.total_duration_ms, gte=0.0)

    def test_stage_raise_marks_pipeline_result_failed(self, tmp_path: Path) -> None:
        """A stage handler that raises produces a failed overall pipeline result."""
        error_message = "intentional explosion"

        def exploding(
            _ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            raise ValueError(error_message)

        result = cli.pipeline(
            [cli.stage("boom", handler=exploding)], context=cli.stage_context(tmp_path)
        )

        tm.fail(result)
        tm.that(result.failure, eq=True)
        tm.that(bool(result), eq=False)


__all__: list[str] = ["TestsFlextCliPipeline"]
