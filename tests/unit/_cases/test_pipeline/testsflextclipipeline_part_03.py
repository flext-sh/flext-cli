"""Unit tests for the DAG pipeline engine."""

from __future__ import annotations

from pathlib import Path

from tests.models import m
from tests.protocols import p
from tests.typings import t

from flext_cli import cli

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
            cli.stage(
                "b",
                depends_on=frozenset({"a"}),
                handler=track("b"),
            ),
            cli.stage(
                "c",
                depends_on=frozenset({"a"}),
                handler=track("c"),
            ),
            cli.stage(
                "d",
                depends_on=frozenset({"b", "c"}),
                handler=track("d"),
            ),
        ]
        result = cli.pipeline(stages, context=cli.stage_context(tmp_path))
        assert result.success
        assert order[0] == "a"
        assert order[-1] == "d"
        assert set(order[1:3]) == {"b", "c"}


__all__: list[str] = ["TestsFlextCliPipeline"]
