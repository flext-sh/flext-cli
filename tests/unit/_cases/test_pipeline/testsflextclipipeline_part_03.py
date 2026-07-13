"""Unit tests for the DAG pipeline engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import cli
from flext_tests import tm

if TYPE_CHECKING:
    from pathlib import Path

    from tests import m
    from tests import p
    from tests import t

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


__all__: list[str] = ["TestsFlextCliPipeline"]
