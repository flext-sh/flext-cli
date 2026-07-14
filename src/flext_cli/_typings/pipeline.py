"""Pipeline type aliases for DAG engine."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from flext_cli import c
from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline as pp
from flext_core import p, t


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal[
        c.Cli.PipelineStageStatus.OK,
        c.Cli.PipelineStageStatus.SKIPPED,
        c.Cli.PipelineStageStatus.FAILED,
    ]
    type PipelineHandler = Callable[
        [pp.PipelineStageContext], p.Result[pp.PipelineStageResult]
    ]
    type PipelineSkipPredicate = Callable[[pp.PipelineStageContext], bool]
    type PipelineHandlerMap = t.MappingKV[str, PipelineHandler]
    type PipelineRetryMap = t.MappingKV[str, int]
    type PipelineSkipMap = t.MappingKV[str, PipelineSkipPredicate]


__all__: tuple[str, ...] = ("FlextCliTypesPipeline",)
