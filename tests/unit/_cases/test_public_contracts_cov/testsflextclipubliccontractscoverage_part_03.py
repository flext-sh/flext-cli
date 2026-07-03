"""Public contract coverage tests for the flext-cli facade and models."""

from __future__ import annotations

from pathlib import Path

from tests.constants import c
from tests.protocols import p

from flext_cli import cli, m, r


class TestsFlextCliPublicContractsCoverage:
    """Implementation part for TestsFlextCliPublicContractsCoverage."""

    def test_public_pipeline_model_contracts(self, tmp_path: Path) -> None:
        context = cli.stage_context(tmp_path, settings={"mode": "test"})

        def stage_handler(
            current: m.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            return r[m.Cli.PipelineStageResult].ok(
                m.Cli.PipelineStageResult.model_validate({
                    "stage_id": "build",
                    "status": c.Cli.PipelineStageStatus.OK,
                    "output": {"workspace": str(current.workspace_root)},
                })
            )

        spec = cli.stage(
            "build",
            handler=stage_handler,
            depends_on=("fetch",),
            retry=1,
        )
        pipeline = m.Cli.PipelineResult(
            stages=[
                cli.stage_result(
                    "ok",
                    status=c.Cli.PipelineStageStatus.OK,
                ),
                cli.stage_result(
                    "fail",
                    status=c.Cli.PipelineStageStatus.FAILED,
                    error="boom",
                ),
                cli.stage_result(
                    "skip",
                    status=c.Cli.PipelineStageStatus.SKIPPED,
                ),
            ],
            total_duration_ms=10.5,
        )
        stage_result = spec.handler(context)
        pipeline_run = cli.pipeline(
            (spec,),
            context=cli.stage_context(tmp_path, settings={"mode": "test"}),
        )

        assert isinstance(cli, p.Cli.PipelineService)
        assert context.settings == {"mode": "test"}
        assert spec.retry == 1
        assert pipeline.success is False
        assert [stage.stage_id for stage in pipeline.failed_stages] == ["fail"]
        assert [stage.stage_id for stage in pipeline.skipped_stages] == ["skip"]
        assert stage_result.success
        assert stage_result.value.output == {"workspace": str(tmp_path)}
        assert pipeline_run.success
        assert pipeline_run.value.success


__all__: list[str] = ["TestsFlextCliPublicContractsCoverage"]
