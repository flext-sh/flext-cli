"""Pipeline type aliases for DAG engine."""

from __future__ import annotations

from typing import Literal

from .._constants.enums import FlextCliConstantsEnums as ce


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal[
        ce.PipelineStageStatus.OK,
        ce.PipelineStageStatus.SKIPPED,
        ce.PipelineStageStatus.FAILED,
    ]


__all__: list[str] = ["FlextCliTypesPipeline"]
