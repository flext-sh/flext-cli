"""Unit tests for the DAG pipeline engine."""

from __future__ import annotations

from pathlib import Path

from tests import c, m, p, r, t, u

# ── Fixtures ────────────────────────────────────────────────────────


def _ok_handler(stage_id: str, output_key: str = "done") -> t.Cli.PipelineHandler:
    """Factory for a handler that succeeds and writes to shared."""

    def handler(ctx: p.Cli.PipelineStageContext) -> p.Result[m.Cli.PipelineStageResult]:
        ctx.shared[output_key] = stage_id
        return r[m.Cli.PipelineStageResult].ok(
            m.Cli.PipelineStageResult(
                stage_id=stage_id,
                status=c.Cli.PipelineStageStatus.OK,
                output={output_key: stage_id},
                duration_ms=1.0,
            ),
        )

    return handler


def _fail_handler(stage_id: str) -> t.Cli.PipelineHandler:
    """Factory for a handler that fails."""

    def handler(ctx: p.Cli.PipelineStageContext) -> p.Result[m.Cli.PipelineStageResult]:
        return r[m.Cli.PipelineStageResult].fail(f"{stage_id} failed")

    return handler


def _skip_always(_ctx: p.Cli.PipelineStageContext) -> bool:
    return True


def _make_ctx(tmp_path: Path) -> m.Cli.PipelineStageContext:
    return m.Cli.PipelineStageContext(workspace_root=tmp_path)


# ── Tests ───────────────────────────────────────────────────────────


class TestsFlextCliPipeline:
    """Test u.Cli.execute_pipeline()."""

    def test_single_stage_ok(self, tmp_path: Path) -> None:
        """Single stage executes and returns ok."""
        stages = [
            m.Cli.PipelineStageSpec(
                stage_id="alpha",
                handler=_ok_handler("alpha"),
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.success
        pipeline = result.value
        assert pipeline.success
        assert len(pipeline.stages) == 1
        assert pipeline.stages[0].stage_id == "alpha"
        assert pipeline.stages[0].status == c.Cli.PipelineStageStatus.OK

    def test_dependency_order(self, tmp_path: Path) -> None:
        """Stages execute in topological order — B depends on A."""
        execution_order: list[str] = []

        def tracking_handler(stage_id: str) -> t.Cli.PipelineHandler:
            def handler(
                ctx: p.Cli.PipelineStageContext,
            ) -> p.Result[m.Cli.PipelineStageResult]:
                execution_order.append(stage_id)
                return r[m.Cli.PipelineStageResult].ok(
                    m.Cli.PipelineStageResult(
                        stage_id=stage_id, status=c.Cli.PipelineStageStatus.OK
                    ),
                )

            return handler

        stages = [
            m.Cli.PipelineStageSpec(
                stage_id="b",
                depends_on=frozenset({"a"}),
                handler=tracking_handler("b"),
            ),
            m.Cli.PipelineStageSpec(
                stage_id="a",
                handler=tracking_handler("a"),
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.success
        assert execution_order == ["a", "b"]

    def test_shared_state_propagation(self, tmp_path: Path) -> None:
        """Stage B can read what stage A wrote to shared."""
        received: dict[str, t.JsonValue | None] = {}

        def reader(
            ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            received["from_a"] = ctx.shared.get("a_output")
            return r[m.Cli.PipelineStageResult].ok(
                m.Cli.PipelineStageResult(
                    stage_id="b", status=c.Cli.PipelineStageStatus.OK
                ),
            )

        def writer(
            ctx: p.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            ctx.shared["a_output"] = "hello"
            return r[m.Cli.PipelineStageResult].ok(
                m.Cli.PipelineStageResult(
                    stage_id="a", status=c.Cli.PipelineStageStatus.OK
                ),
            )

        stages = [
            m.Cli.PipelineStageSpec(stage_id="a", handler=writer),
            m.Cli.PipelineStageSpec(
                stage_id="b",
                depends_on=frozenset({"a"}),
                handler=reader,
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.success
        assert received["from_a"] == "hello"

    def test_fail_fast_stops_on_failure(self, tmp_path: Path) -> None:
        """With fail_fast=True, pipeline stops after first failure."""
        stages = [
            m.Cli.PipelineStageSpec(stage_id="a", handler=_fail_handler("a")),
            m.Cli.PipelineStageSpec(
                stage_id="b",
                depends_on=frozenset({"a"}),
                handler=_ok_handler("b"),
            ),
        ]
        result = u.Cli.execute_pipeline(
            stages,
            _make_ctx(tmp_path),
            fail_fast=True,
        )
        assert result.success
        pipeline = result.value
        assert not pipeline.success
        assert len(pipeline.failed_stages) == 1
        assert pipeline.failed_stages[0].stage_id == "a"

    def test_skip_predicate(self, tmp_path: Path) -> None:
        """Stage with skip_if returning True is skipped."""
        stages = [
            m.Cli.PipelineStageSpec(
                stage_id="skippable",
                handler=_ok_handler("skippable"),
                skip_if=_skip_always,
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.success
        pipeline = result.value
        assert pipeline.success
        assert pipeline.stages[0].status == c.Cli.PipelineStageStatus.SKIPPED

    def test_cycle_detection(self, tmp_path: Path) -> None:
        """Circular dependencies produce a failure result."""
        stages = [
            m.Cli.PipelineStageSpec(
                stage_id="a",
                depends_on=frozenset({"b"}),
                handler=_ok_handler("a"),
            ),
            m.Cli.PipelineStageSpec(
                stage_id="b",
                depends_on=frozenset({"a"}),
                handler=_ok_handler("b"),
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
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
                m.Cli.PipelineStageResult(
                    stage_id="flaky", status=c.Cli.PipelineStageStatus.OK
                ),
            )

        stages = [
            m.Cli.PipelineStageSpec(
                stage_id="flaky",
                handler=flaky,
                retry=3,
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.success
        assert result.value.success
        assert call_count == 3

    def test_empty_pipeline(self, tmp_path: Path) -> None:
        """Empty pipeline returns ok with no stages."""
        result = u.Cli.execute_pipeline([], _make_ctx(tmp_path))
        assert result.success
        assert result.value.success
        assert len(result.value.stages) == 0

    def test_total_duration_tracked(self, tmp_path: Path) -> None:
        """Pipeline tracks total duration."""
        stages = [
            m.Cli.PipelineStageSpec(stage_id="a", handler=_ok_handler("a")),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.success
        assert result.value.total_duration_ms >= 0.0

    def test_diamond_dependency(self, tmp_path: Path) -> None:
        """Diamond DAG: A -> B, A -> C, B -> D, C -> D."""
        order: list[str] = []

        def track(sid: str) -> t.Cli.PipelineHandler:
            def h(
                ctx: p.Cli.PipelineStageContext,
            ) -> p.Result[m.Cli.PipelineStageResult]:
                order.append(sid)
                return r[m.Cli.PipelineStageResult].ok(
                    m.Cli.PipelineStageResult(
                        stage_id=sid, status=c.Cli.PipelineStageStatus.OK
                    ),
                )

            return h

        stages = [
            m.Cli.PipelineStageSpec(stage_id="a", handler=track("a")),
            m.Cli.PipelineStageSpec(
                stage_id="b",
                depends_on=frozenset({"a"}),
                handler=track("b"),
            ),
            m.Cli.PipelineStageSpec(
                stage_id="c",
                depends_on=frozenset({"a"}),
                handler=track("c"),
            ),
            m.Cli.PipelineStageSpec(
                stage_id="d",
                depends_on=frozenset({"b", "c"}),
                handler=track("d"),
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.success
        assert order[0] == "a"
        assert order[-1] == "d"
        assert set(order[1:3]) == {"b", "c"}
