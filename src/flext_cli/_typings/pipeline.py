"""Pipeline type aliases for DAG engine."""

from __future__ import annotations

from collections.abc import (
    Callable,
)
from typing import TYPE_CHECKING, Literal

from flext_core import FlextProtocols

from flext_cli._constants.enums import FlextCliConstantsEnums

if TYPE_CHECKING:
    from flext_cli._models.pipeline import FlextCliModelsPipeline
    from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal[
        FlextCliConstantsEnums.PipelineStageStatus.OK,
        FlextCliConstantsEnums.PipelineStageStatus.SKIPPED,
        FlextCliConstantsEnums.PipelineStageStatus.FAILED,
    ]
    type PipelineHandler = Callable[
        [FlextCliProtocolsPipeline.PipelineStageContext],
        FlextProtocols.Result[FlextCliModelsPipeline.PipelineStageResult],
    ]
    type PipelineSkipPredicate = Callable[
        [FlextCliProtocolsPipeline.PipelineStageContext],
        bool,
    ]


__all__: list[str] = ["FlextCliTypesPipeline"]
