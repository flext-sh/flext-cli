"""Pipeline type aliases for DAG engine."""

from __future__ import annotations

from collections.abc import (
    Callable,
)
from typing import TYPE_CHECKING, Literal

from flext_cli._constants.enums import FlextCliConstantsEnums
from flext_core import p, t

if TYPE_CHECKING:
    from flext_cli._models.pipeline import FlextCliModelsPipeline as mp


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal[
        FlextCliConstantsEnums.PipelineStageStatus.OK,
        FlextCliConstantsEnums.PipelineStageStatus.SKIPPED,
        FlextCliConstantsEnums.PipelineStageStatus.FAILED,
    ]
    type PipelineHandler = Callable[
        [mp.PipelineStageContext],
        p.Result[mp.PipelineStageResult],
    ]
    type PipelineSkipPredicate = Callable[
        [mp.PipelineStageContext],
        bool,
    ]
    type PipelineHandlerMap = t.MappingKV[str, PipelineHandler]
    type PipelineRetryMap = t.MappingKV[str, int]
    type PipelineSkipMap = t.MappingKV[str, PipelineSkipPredicate]


__all__: list[str] = ["FlextCliTypesPipeline"]
