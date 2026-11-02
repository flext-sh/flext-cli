"""Unit tests for the DAG pipeline engine.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import io
from pathlib import Path

from flext_core import FlextSettings

from flext_cli import cli
from tests import m, p, tm, u
from tests.unit.cases.test_pipeline.testsflextclipipeline_part_01 import (
    TestsFlextCliPipelinePart01,
)
from tests.unit.cases.test_pipeline.testsflextclipipeline_part_02 import (
    TestsFlextCliPipelinePart02,
)
from tests.unit.cases.test_pipeline.testsflextclipipeline_part_03 import (
    TestsFlextCliPipelinePart03,
)


class TestsFlextCliPipeline(
    TestsFlextCliPipelinePart01,
    TestsFlextCliPipelinePart02,
    TestsFlextCliPipelinePart03,
):
    """Public facade for TestsFlextCliPipeline."""


class TestsFlextPipelineLoggingContext:
    """Worker stages inherit operation correlation without sharing context state."""

    @staticmethod
    def test_parallel_stages_receive_operation_context(tmp_path: Path) -> None:
        """Each submission receives its own copy of the caller's native context."""
        observed: list[p.LoggingRecord] = []
        logger = u.create_module_logger(
            __name__,
            runtime_settings=FlextSettings(async_logging=False),
            options=m.StructlogOptions(
                observers=(observed.append,),
                handlers=(u.create_logging_handler(stream=io.StringIO()),),
            ),
        )

        def stage(stage_id: str) -> p.Cli.PipelineStage:
            def run(
                context: p.Cli.PipelineStageContext,
            ) -> p.Result[m.Cli.PipelineStageResult]:
                _ = context
                logger.info("stage correlation", stage_id=stage_id)
                return cli.ok_stage(stage_id)

            return run

        stages = [
            cli.stage(stage_id, handler=stage(stage_id))
            for stage_id in ("first", "second")
        ]
        with u.logging_scope("pipeline", run_id="pipeline-operation"):
            tm.ok(
                cli.pipeline(
                    stages,
                    context=cli.stage_context(tmp_path),
                    logger=logger,
                )
            )
        correlated = [
            record.context.get("run_id")
            for record in observed
            if record.message == "stage correlation"
        ]
        tm.that(correlated, eq=["pipeline-operation", "pipeline-operation"])
