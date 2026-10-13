"""Shared pipeline stage handler builders for the split pipeline test parts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import cli

if TYPE_CHECKING:
    from tests import m, p


class TestsFlextCliPipelineHandlers:
    """Single owner of the pipeline stage handler builders."""

    @staticmethod
    def _ok_handler(stage_id: str, output_key: str = "done") -> p.Cli.PipelineStage:
        """Build a handler that succeeds and writes to shared.

        Returns:
            The resulting ``p.Cli.PipelineStage``.

        """

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
