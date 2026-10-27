"""Pipeline and dependency-graph type aliases for the DAG engine.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Collection, Mapping
from typing import TYPE_CHECKING, Literal

from flext_cli._constants import FlextCliConstantsEnums

if TYPE_CHECKING:
    import networkx as nx


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal[
        FlextCliConstantsEnums.PipelineStageStatus.OK,
        FlextCliConstantsEnums.PipelineStageStatus.SKIPPED,
        FlextCliConstantsEnums.PipelineStageStatus.FAILED,
    ]
    type DagEdges = Mapping[str, Collection[str]]
    """Every node mapped to the nodes it depends on."""
    type DagGraph = nx.DiGraph[str]
    """NetworkX directed graph whose edges point from a node to a dependency."""


__all__: list[str] = ["FlextCliTypesPipeline"]
