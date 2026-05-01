"""Pipeline type aliases for DAG engine."""

from __future__ import annotations

from collections.abc import (
    Callable,
)
from typing import TYPE_CHECKING, Literal

from flext_cli._constants.enums import FlextCliConstantsEnums
from flext_core import p

if TYPE_CHECKING:
    from flext_cli import FlextCliModelsPipeline as mp, FlextCliProtocolsPipeline as pp


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal[
        FlextCliConstantsEnums.PipelineStageStatus.OK,
        FlextCliConstantsEnums.PipelineStageStatus.SKIPPED,
        FlextCliConstantsEnums.PipelineStageStatus.FAILED,
    ]
    type PipelineHandler = Callable[
        [pp.PipelineStageContext],
        p.Result[mp.PipelineStageResult],
    ]
    type PipelineSkipPredicate = Callable[
        [pp.PipelineStageContext],
        bool,
    ]


__all__: list[str] = ["FlextCliTypesPipeline"]
