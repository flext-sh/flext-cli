"""Pipeline type aliases for DAG engine.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal

from flext_cli._constants import FlextCliConstantsEnums


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal[
        FlextCliConstantsEnums.PipelineStageStatus.OK,
        FlextCliConstantsEnums.PipelineStageStatus.SKIPPED,
        FlextCliConstantsEnums.PipelineStageStatus.FAILED,
    ]


__all__: list[str] = ["FlextCliTypesPipeline"]
