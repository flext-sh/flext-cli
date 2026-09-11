"""Pipeline type aliases for DAG engine."""

from __future__ import annotations

from typing import Literal

from flext_cli import c


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal[
        c.Cli.PipelineStageStatus.OK,
        c.Cli.PipelineStageStatus.SKIPPED,
        c.Cli.PipelineStageStatus.FAILED,
    ]


__all__: list[str] = ["FlextCliTypesPipeline"]
