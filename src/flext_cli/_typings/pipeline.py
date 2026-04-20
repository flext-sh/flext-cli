"""Pipeline type aliases for DAG engine."""

from __future__ import annotations

from collections.abc import (
    Callable,
)
from typing import TYPE_CHECKING, Literal

from flext_cli import FlextCliConstantsEnums, p

if TYPE_CHECKING:
    from flext_cli import m


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal[
        FlextCliConstantsEnums.PipelineStageStatus.OK,
        FlextCliConstantsEnums.PipelineStageStatus.SKIPPED,
        FlextCliConstantsEnums.PipelineStageStatus.FAILED,
    ]
    type PipelineHandler = Callable[
        [m.Cli.PipelineStageContext],
        p.Result[m.Cli.PipelineStageResult],
    ]
    type PipelineSkipPredicate = Callable[[m.Cli.PipelineStageContext], bool]


__all__: list[str] = ["FlextCliTypesPipeline"]
