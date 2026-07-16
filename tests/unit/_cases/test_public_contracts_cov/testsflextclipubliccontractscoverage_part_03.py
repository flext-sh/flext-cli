"""Public contract coverage tests for the flext-cli facade and models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests import c
from tests import p

from flext_cli import cli, m, r
from flext_tests import tm

from pathlib import Path



class TestsFlextCliPublicContractsCoverage:
    """Implementation part for TestsFlextCliPublicContractsCoverage."""

    def test_public_pipeline_model_contracts(self, tmp_path: Path) -> None:
        """Exercise the public pipeline models and service contract."""
        context = cli.stage_context(tmp_path, settings={"mode": "test"})

        def stage_handler(
            current: m.Cli.PipelineStageContext,
        ) -> p.Result[p.Cli.PipelineStageResult]:
            return r[p.Cli.PipelineStageResult].ok(
                m.Cli.PipelineStageResult.model_validate({
                    "stage_id": "build",
                    "status": c.Cli.PipelineStageStatus.OK,
                    "output": {"workspace": str(current.workspace_root)},
                })
            )

        spec = cli.stage("build", handler=stage_handler, depends_on=("fetch",), retry=1)
        pipeline = m.Cli.PipelineResult(
            stages=[
                cli.stage_result("ok", status=c.Cli.PipelineStageStatus.OK),
                cli.stage_result(
                    "fail", status=c.Cli.PipelineStageStatus.FAILED, error="boom"
                ),
                cli.stage_result("skip", status=c.Cli.PipelineStageStatus.SKIPPED),
            ],
            total_duration_ms=10.5,
        )
        stage_result = spec.handler(context)
        pipeline_run = cli.pipeline(
            (spec,), context=cli.stage_context(tmp_path, settings={"mode": "test"})
        )

        tm.that(cli, is_=p.Cli.PipelineService)
        tm.that(context.settings, eq={"mode": "test"})
        tm.that(spec.retry, eq=1)
        tm.that(pipeline.success, eq=False)
        tm.that([stage.stage_id for stage in pipeline.failed_stages], eq=["fail"])
        tm.that([stage.stage_id for stage in pipeline.skipped_stages], eq=["skip"])
        tm.ok(stage_result)
        tm.that(stage_result.value.output, eq={"workspace": str(tmp_path)})
        tm.ok(pipeline_run)
        tm.that(pipeline_run.value.success, eq=True)


__all__: list[str] = ["TestsFlextCliPublicContractsCoverage"]
