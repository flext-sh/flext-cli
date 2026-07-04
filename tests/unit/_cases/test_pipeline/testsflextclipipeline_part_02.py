"""Unit tests for the DAG pipeline engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.constants import c
from tests.models import m

from flext_cli import cli, r

if TYPE_CHECKING:
    from pathlib import Path

    from tests.protocols import p
    from tests.typings import t


class TestsFlextCliPipeline:
    """Implementation part for TestsFlextCliPipeline."""

    @staticmethod
    def _ok_handler(stage_id: str, output_key: str = "done") -> t.Cli.PipelineHandler:
        """Factory for a handler that succeeds and writes to shared."""

        def handler(
            ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            ctx.shared[output_key] = stage_id
            return cli.ok_stage(
                stage_id,
                output={output_key: stage_id},
                duration_ms=1.0,
            )

        return handler

    def test_cycle_detection(self, tmp_path: Path) -> None:
        """Circular dependencies produce a failure result."""
        stages = [
            cli.stage(
                "a",
                depends_on=frozenset({"b"}),
                handler=self._ok_handler("a"),
            ),
            cli.stage(
                "b",
                depends_on=frozenset({"a"}),
                handler=self._ok_handler("b"),
            ),
        ]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        assert result.failure

    def test_retry_on_failure(self, tmp_path: Path) -> None:
        """Stage retries up to retry count before succeeding."""
        call_count = 0

        def flaky(
            ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return r[m.Cli.PipelineStageResult].fail("transient")
            return r[m.Cli.PipelineStageResult].ok(
                cli.stage_result(
                    "flaky",
                    status=c.Cli.PipelineStageStatus.OK,
                ),
            )

        stages = [
            cli.stage(
                "flaky",
                handler=flaky,
                retry=3,
            ),
        ]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        assert result.success
        assert result.value.success
        assert call_count == 3

    def test_retry_on_safe_exception_marks_stage_failed(self, tmp_path: Path) -> None:
        """Safe stage exceptions are retried and end as failed stage results."""
        call_count = 0
        error_message = "boom"

        def exploding(
            ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            nonlocal call_count
            _ = ctx
            call_count += 1
            raise ValueError(error_message)

        result = cli.pipeline(
            [
                cli.stage(
                    "boom",
                    handler=exploding,
                    retry=1,
                ),
            ],
            context=cli.stage_context(tmp_path),
        )

        assert result.success
        assert not result.value.success
        assert call_count == 2
        assert (
            result.value.failed_stages[0].error == f"stage boom raised: {error_message}"
        )

    def test_empty_pipeline(self, tmp_path: Path) -> None:
        """Empty pipeline returns ok with no stages."""
        result = cli.pipeline([], context=cli.stage_context(tmp_path))
        assert result.success
        assert result.value.success
        assert len(result.value.stages) == 0

    def test_total_duration_tracked(self, tmp_path: Path) -> None:
        """Pipeline tracks total duration."""
        stages = [
            cli.stage("a", handler=self._ok_handler("a")),
        ]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        assert result.success
        assert result.value.total_duration_ms >= 0.0


__all__: list[str] = ["TestsFlextCliPipeline"]
