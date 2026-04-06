"""Pipeline type aliases for DAG engine."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Literal

from flext_core import r

if TYPE_CHECKING:
    from flext_cli import m, p


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal["ok", "skipped", "failed"]
    type PipelineHandler = Callable[
        [p.Cli.PipelineStageContext],
        r[m.Cli.PipelineStageResult],
    ]
    type PipelineSkipPredicate = Callable[[p.Cli.PipelineStageContext], bool]


__all__ = ["FlextCliTypesPipeline"]
